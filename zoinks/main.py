import ast
import sys
from zoinks.analyzer import ThreadSafetyAnalyzer


def main():
    if len(sys.argv) != 2:
        print("Usage: zoinks <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    analyzer = ThreadSafetyAnalyzer()

    try:
        with open(filename, "r") as source:
            tree = ast.parse(source.read())
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except SyntaxError as e:
        print(f"Error: Syntax error in file '{filename}': {e}")
        sys.exit(1)

    analyzer.visit(tree)
    return 0


if __name__ == "__main__":
    sys.exit(main())
