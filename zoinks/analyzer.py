import ast
from colorama import Fore, Style

class ThreadSafetyAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.lock_annotations = {}
        self.variable_guards = {}
        self.shared_variables = set()
        self.current_function = None
        self.locked_contexts = set()
        self.current_class = None

    def visit_FunctionDef(self, node):
        """
        Save decorator annotations for functions.
        """
        previous_function = self.current_function
        self.current_function = node.name

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id == 'requires_lock':
                    lock_name = decorator.args[0].s
                    self.lock_annotations[node.name] = lock_name
                elif decorator.func.id == 'guards_variable':
                    variable_name = decorator.args[0].s
                    self.variable_guards[node.name] = variable_name
                    self.shared_variables.add(variable_name)

        self.generic_visit(node)
        self.current_function = previous_function

    def visit_ClassDef(self, node):
        """
        Handle class definitions.
        """
        previous_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = previous_class

    def visit_With(self, node):
        """
        Handle with lock blocks.
        """
        for item in node.items:
            if isinstance(item.context_expr, ast.Name):
                self.locked_contexts.add(item.context_expr.id)

        self.generic_visit(node)

        for item in node.items:
            if isinstance(item.context_expr, ast.Name):
                self.locked_contexts.discard(item.context_expr.id)

    def visit_Call(self, node):
        """
        Check function calls considering @requires_lock decorators.
        """
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Attribute):
                class_name = node.func.value.value.id
                method_name = node.func.attr
                if class_name == self.current_class and method_name in self.lock_annotations:
                    required_lock = self.lock_annotations[method_name]
                    if required_lock not in self.locked_contexts:
                        self._print_warning(
                            f"Method '{method_name}' of class '{class_name}' requires lock '{required_lock}' but is called without it.",
                            node
                        )
            elif isinstance(node.func.value, ast.Name):
                func_name = node.func.attr
                if func_name in self.lock_annotations:
                    required_lock = self.lock_annotations[func_name]
                    if required_lock not in self.locked_contexts:
                        self._print_warning(
                            f"Function '{func_name}' requires lock '{required_lock}' but is called without it.",
                            node
                        )
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.lock_annotations:
                required_lock = self.lock_annotations[func_name]
                if required_lock not in self.locked_contexts:
                    self._print_warning(
                        f"Function '{func_name}' requires lock '{required_lock}' but is called without it.",
                        node
                    )

        self.generic_visit(node)

    def visit_Name(self, node):
        """
        Check access to variables considering @guards_variable decorators.
        """
        if isinstance(node.ctx, ast.Load) and node.id in self.shared_variables:
            if self.current_function in self.variable_guards:
                guarded_by = self.lock_annotations.get(self.current_function)
                if guarded_by not in self.locked_contexts:
                    if self.current_class:
                        self._print_warning(
                            f"Access to shared variable '{node.id}' in method '{self.current_function}' "
                            f"of class '{self.current_class}' is not protected by lock '{guarded_by}'.",
                            node
                        )
                    else:
                        self._print_warning(
                            f"Access to shared variable '{node.id}' in function '{self.current_function}' "
                            f"is not protected by lock '{guarded_by}'.",
                            node
                        )

    def visit_Expr(self, node):
        """
        Handle lock.acquire() and lock.release() calls.
        """
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            attr = node.value.func
            if isinstance(attr.value, ast.Name):
                if attr.attr == 'acquire':
                    self.locked_contexts.add(attr.value.id)
                elif attr.attr == 'release':
                    self.locked_contexts.discard(attr.value.id)

        self.generic_visit(node)

    def _print_warning(self, message, node):
        """
        Format and print warnings.
        """
        line = node.lineno
        col_offset = node.col_offset

        print(
            f"{Fore.YELLOW}Warning:{Style.RESET_ALL} {message} "
            f"{Fore.RESET}(Line: {Fore.YELLOW}{line}, Column: {col_offset}{Fore.RESET})"
        )

    def generic_visit(self, node):
        """
        General processing of nodes while tracking parent contexts.
        """
        super().generic_visit(node)