import ast
import sysconfig
import os
import sys
from itertools import combinations
from colorama import Fore, Style
import functools


def check_gil():
    return bool(sysconfig.get_config_var('Py_GIL_DISABLED') == 1)


class ThreadSafetyAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.lock_annotations = {}
        self.variable_guards = {}
        self.shared_variables = set()
        self.current_function = None
        self.locked_contexts = set()
        self.current_class = None
        self.warnings = []
        self.lock_acquisition_sequences = {}
        self.current_lock_sequence = []
        self.locked_multiple_times = {}
        self.lock_acquire_counts = {}
        self.lock_release_counts = {}

    def visit_FunctionDef(self, node):
        previous_function = self.current_function
        self.current_function = node.name
        self.current_lock_sequence = []

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id == 'requires_lock':
                    required_lock = decorator.args[0].s
                    self.lock_annotations[node.name] = required_lock
                elif decorator.func.id == 'guards_variable':
                    variable_name = decorator.args[0].s
                    self.variable_guards[node.name] = {
                        "var": variable_name,
                        "lock": self.lock_annotations.get(node.name)
                    }
                    self.shared_variables.add(variable_name)

        self.generic_visit(node)

        self.lock_acquisition_sequences[self.current_function] = list(self.current_lock_sequence)

        for lock in set(self.lock_acquire_counts.keys()) | set(self.lock_release_counts.keys()):
            acquired = self.lock_acquire_counts.get(lock, 0)
            released = self.lock_release_counts.get(lock, 0)

            if acquired != released:
                self._add_warning(
                    f"Mismatch between .acquire() and .release() calls for '{lock}': "
                    f"{acquired} acquires but {released} releases in function '{node.name}'.",
                    node
                )

        self.lock_acquire_counts.clear()
        self.lock_release_counts.clear()

        self.current_function = previous_function

        self.current_function = previous_function

    def visit_ClassDef(self, node):
        previous_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = previous_class

    def visit_With(self, node):
        for item in node.items:
            if isinstance(item.context_expr, ast.Name):
                lock_name = item.context_expr.id
                self.locked_contexts.add(lock_name)
                self.current_lock_sequence.append(lock_name)

        self.generic_visit(node)

        for item in node.items:
            if isinstance(item.context_expr, ast.Name):
                lock_name = item.context_expr.id
                self.locked_contexts.discard(lock_name)

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
                lock_name = attr.value.id

                if attr.attr == 'acquire':
                    self.lock_acquire_counts[lock_name] = self.lock_acquire_counts.get(lock_name, 0) + 1
                    if lock_name in self.locked_contexts:
                        self._add_warning(
                            f"Potential self-deadlock: '{lock_name}' is a regular Lock and is already held by the same thread.",
                            node
                        )
                    self.locked_contexts.add(lock_name)
                    self.current_lock_sequence.append(lock_name)

                elif attr.attr == 'release':
                    self.lock_release_counts[lock_name] = self.lock_release_counts.get(lock_name, 0) + 1
                    if lock_name in self.locked_contexts:
                        self.locked_contexts.remove(lock_name)

        self.generic_visit(node)

    def detect_deadlocks(self):
        sequences = self.lock_acquisition_sequences

        for (func1, seq1), (func2, seq2) in combinations(sequences.items(), 2):
            if not seq1 or not seq2:
                continue

            pos1 = {lock: idx for idx, lock in enumerate(seq1)}
            pos2 = {lock: idx for idx, lock in enumerate(seq2)}

            for lock_a in set(seq1) & set(seq2):
                for lock_b in set(seq1) & set(seq2):
                    if lock_a == lock_b:
                        continue
                    if lock_a in pos1 and lock_b in pos1 and lock_a in pos2 and lock_b in pos2:
                        if (pos1[lock_a] < pos1[lock_b]) and (pos2[lock_a] > pos2[lock_b]):
                            self._add_warning(
                                f"Potential deadlock detected: inconsistent lock acquisition order "
                                f"for '{lock_a}' and '{lock_b}' between functions '{func1}' and '{func2}'.",
                                None
                            )
                            break

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
        analyzer.detect_deadlocks()

        warnings_found = bool(analyzer.warnings)
        print(f"\n{Fore.RED if warnings_found else Fore.GREEN}=== Analyzing: {filename} ==={Style.RESET_ALL}")

        if warnings_found:
            for warning, line, col in analyzer.warnings:
                print(f"{Fore.RED}Warning:{Style.RESET_ALL} {warning} "
                      f"{Fore.RESET}(Line: {Fore.YELLOW}{line}, Column: {col}{Fore.RESET})")
        else:
            print(f"{Fore.GREEN}Warnings not found{Style.RESET_ALL}")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except SyntaxError as e:
        print(f"Error: Syntax error in file '{filename}': {e}")