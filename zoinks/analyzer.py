import ast
import sysconfig
from colorama import Fore, Style


def check_gil():
    return bool(sysconfig.get_config_var('Py_GIL_DISABLED')==1)


class ThreadSafetyAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.lock_annotations = {}
        self.variable_guards = {}
        self.shared_variables = set()
        self.current_function = None
        self.locked_contexts = set()
        self.current_class = None
        self.warnings = []

    def visit_FunctionDef(self, node):
        previous_function = self.current_function
        self.current_function = node.name

        required_lock = None

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id == 'requires_lock':
                    required_lock = decorator.args[0].s
                    self.lock_annotations[node.name] = required_lock
                elif decorator.func.id == 'guards_variable':
                    variable_name = decorator.args[0].s
                    self.variable_guards[node.name] = {
                        "var": variable_name,
                        "lock": required_lock
                    }
                    self.shared_variables.add(variable_name)

        self.generic_visit(node)
        self.current_function = previous_function

    def visit_ClassDef(self, node):
        previous_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = previous_class

    def visit_With(self, node):
        for item in node.items:
            if isinstance(item.context_expr, ast.Name):
                self.locked_contexts.add(item.context_expr.id)

        self.generic_visit(node)

        for item in node.items:
            if isinstance(item.context_expr, ast.Name):
                self.locked_contexts.discard(item.context_expr.id)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Attribute):
                class_name = node.func.value.value.id
                method_name = node.func.attr
                if class_name == self.current_class and method_name in self.lock_annotations:
                    required_lock = self.lock_annotations[method_name]
                    if required_lock not in self.locked_contexts:
                        self._add_warning(
                            f"Method '{method_name}' of class '{class_name}' requires lock '{required_lock}' but is called without it.",
                            node
                        )
            elif isinstance(node.func.value, ast.Name):
                func_name = node.func.attr
                if func_name in self.lock_annotations:
                    required_lock = self.lock_annotations[func_name]
                    if required_lock not in self.locked_contexts:
                        self._add_warning(
                            f"Function '{func_name}' requires lock '{required_lock}' but is called without it.",
                            node
                        )
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.lock_annotations:
                required_lock = self.lock_annotations[func_name]
                if required_lock not in self.locked_contexts:
                    self._add_warning(
                        f"Function '{func_name}' requires lock '{required_lock}' but is called without it.",
                        node
                    )

        self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.ctx, (ast.Load, ast.Store)) and isinstance(node.value, ast.Name):
            if node.attr in self.shared_variables:
                if self.current_function in self.variable_guards:
                    guard_info = self.variable_guards[self.current_function]
                    guarded_var = guard_info["var"]
                    lock_name = guard_info["lock"]

                    if node.attr == guarded_var and lock_name not in self.locked_contexts:
                        if self.current_class:
                            self._add_warning(
                                f"Access to guarded variable '{node.attr}' in method '{self.current_function}' of class '{self.current_class}' "
                                f"is not protected by lock '{lock_name}'.",
                                node
                            )
                        else:
                            self._add_warning(
                                f"Access to guarded variable '{node.attr}' in function '{self.current_function}' "
                                f"is not protected by lock '{lock_name}'.",
                                node
                            )
        self.generic_visit(node)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            attr = node.value.func
            if isinstance(attr.value, ast.Name):
                if attr.attr == 'acquire':
                    self.locked_contexts.add(attr.value.id)
                elif attr.attr == 'release':
                    self.locked_contexts.discard(attr.value.id)

        self.generic_visit(node)

    def _add_warning(self, message, node):
        line = node.lineno if node else "Unknown"
        col_offset = node.col_offset if node else "Unknown"
        self.warnings.append((message, line, col_offset))

    def generic_visit(self, node):
        super().generic_visit(node)


def analyze_file(filename):
    analyzer = ThreadSafetyAnalyzer()

    try:
        with open(filename, "r") as source:
            tree = ast.parse(source.read(), filename=filename)
        analyzer.visit(tree)

        warnings_found = bool(analyzer.warnings)
        print(f"\n{Fore.RED if warnings_found else Fore.GREEN}=== Analyzing: {filename} ==={Style.RESET_ALL}")

        if warnings_found:
            for warning, line, col in analyzer.warnings:
                print(f"{Fore.RED}Warning:{Style.RESET_ALL} {warning} "
                      f"{Fore.RESET}(Line: {Fore.YELLOW}{line}, Column: {col}{Fore.RESET})")
        else:
            print(f"{Fore.GREEN}Warnings not found")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except SyntaxError as e:
        print(f"Error: Syntax error in file '{filename}': {e}")
