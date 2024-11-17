import ast


class ThreadSafetyAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.lock_annotations = {}
        self.variable_guards = {}
        self.shared_variables = set()
        self.current_function = None
        self.parent_stack = []

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        requires_lock = None
        guarded_vars = set()

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if decorator.func.id == 'requires_lock':
                    requires_lock = decorator.args[0].s
                    self.lock_annotations[node.name] = requires_lock
                elif decorator.func.id == 'guards_variable':
                    var_name = decorator.args[0].s
                    guarded_vars.add(var_name)
                    if node.name not in self.variable_guards:
                        self.variable_guards[node.name] = set()
                    self.variable_guards[node.name].add(var_name)
                elif decorator.func.id == 'shared_variable':
                    var_name = decorator.args[0].s
                    self.shared_variables.add(var_name)

        if requires_lock and not self._uses_lock(node, requires_lock):
            print(f"Warning: Function '{node.name}' requires lock '{requires_lock}' but does not use it.")

        for var in guarded_vars:
            if not self._guards_variable(node, var):
                print(
                    f"Warning: Function '{node.name}' is supposed to guard variable '{var}' but lacks necessary protection.")

        self.generic_visit(node)
        self.current_function = None

    def _uses_lock(self, node, lock_name):
        """
        Проверяет, используется ли заданная блокировка внутри `with lock_name`.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.With):
                for item in child.items:
                    if isinstance(item.context_expr, ast.Name) and item.context_expr.id == lock_name:
                        return True
        return False

    def _guards_variable(self, node, var_name):
        """
        Проверяет, что переменная `var_name` защищена внутри функции.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name) and target.id == var_name:
                        if not self._uses_lock(node, self.lock_annotations.get(node.name, None)):
                            return False
        return True

    def visit_Assign(self, node):
        """
        Проверка использования @shared_variable
        """
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                if var_name in self.shared_variables:
                    if self._is_locked():
                        print(f"Warning: Shared variable '{var_name}' should not be used with a lock.")
        self.generic_visit(node)

    def _is_locked(self):
        """
        Проверяет, находится ли текущий узел внутри `with` блока.
        """
        return any(isinstance(parent, ast.With) for parent in self.parent_stack)

    def generic_visit(self, node):
        """
        Переопределяем generic_visit для отслеживания родительских узлов
        """
        self.parent_stack.append(node)
        super().generic_visit(node)
        self.parent_stack.pop()
