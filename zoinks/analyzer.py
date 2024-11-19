import ast
from colorama import Fore, Style


class ThreadSafetyAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.lock_annotations = {}
        self.variable_guards = {}
        self.shared_variables = set()
        self.current_function = None
        self.parent_stack = []
        self.locked_contexts = set()

    def visit_FunctionDef(self, node):
        """
        Сохраняем аннотации декораторов для функций и переменных.
        """
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):

                    if decorator.func.id == 'requires_lock':
                        lock_name = decorator.args[0].s
                        self.lock_annotations[node.name] = lock_name

                    elif decorator.func.id == 'guards_variable':
                        variable_name = decorator.args[0].s
                        self.variable_guards[node.name] = variable_name

                    elif decorator.func.id == 'shared_variable':
                        variable_name = decorator.args[0].s
                        self.shared_variables.add(variable_name)

        self.generic_visit(node)

    def visit_With(self, node):
        """
        Проверяем вход в блок `with lock`.
        """
        for item in node.items:
            if isinstance(item.context_expr, ast.Name):  # Проверяем выражение внутри `with`
                self.locked_contexts.add(item.context_expr.id)

        self.generic_visit(node)

        for item in node.items:
            if isinstance(item.context_expr, ast.Name):
                self.locked_contexts.discard(item.context_expr.id)

    def visit_Call(self, node):
        """
        Проверяем вызовы функций на соответствие их декораторам @requires_lock.
        """
        if isinstance(node.func, ast.Name):  # Проверяем только обычные вызовы
            func_name = node.func.id
            if func_name in self.lock_annotations:
                required_lock = self.lock_annotations[func_name]
                if required_lock not in self.locked_contexts:
                    self._print_warning(
                        f"Function '{func_name}' requires lock '{required_lock}' but is called without it.",
                        node
                    )

        self.generic_visit(node)

    def visit_Expr(self, node):
        """
        Проверяем вызовы lock.acquire() и lock.release().
        """
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            attr = node.value.func
            if isinstance(attr.value, ast.Name):  # Проверяем, что значение атрибута — имя
                if attr.attr == 'acquire':
                    self.locked_contexts.add(attr.value.id)
                elif attr.attr == 'release':
                    self.locked_contexts.discard(attr.value.id)

        self.generic_visit(node)

    def _print_warning(self, message, node):
        """
        Форматирует и выводит предупреждение с выделением строки.
        """
        line = node.lineno
        col_offset = node.col_offset

        print(
            f"{Fore.YELLOW}Warning:{Style.RESET_ALL} {message} "
            f"{Fore.RESET}(Line: {Fore.YELLOW}{line}, Column: {col_offset}{Fore.RESET})"
        )

    def generic_visit(self, node):
        """
        Обновляем стек родителей.
        """
        self.parent_stack.append(node)
        super().generic_visit(node)
        self.parent_stack.pop()