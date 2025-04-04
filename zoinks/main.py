import os
import sys
import ast
from zoinks.analyzer import ThreadSafetyAnalyzer, analyze_file
from colorama import Fore, Style


def main():
    if len(sys.argv) < 2:
        print("Usage: zoinks <file_or_directory1> <file_or_directory2> ...")
        sys.exit(1)

    targets = sys.argv[1:]

    for target in targets:
        if os.path.isdir(target):
            for root, _, files in os.walk(target):
                for file in files:
                    if file.endswith(".py"):
                        analyze_file(os.path.join(root, file))
        elif os.path.isfile(target) and target.endswith(".py"):
            analyze_file(target)
        else:
            print(f"Error: '{target}' is not a valid Python file or directory.")
            sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
