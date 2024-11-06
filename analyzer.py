import ast
import builtins
import sys
from typing import Dict, List, Set
from pathlib import Path

class PythonCodeAnalyzer:
    def __init__(self):
        self.variables: Set[str] = set()
        self.constants: Set[str] = set()
        self.labels: Set[str] = set()
        self.system_functions: Set[str] = set()
        self.system_procedures: Set[str] = set()
        self.user_functions: Set[str] = set()
        self.user_procedures: Set[str] = set()
        self.builtin_functions = set(dir(builtins))

    def analyze_file(self, file_path: str) -> None:
        """Анализирует файл Python и собирает информацию о его компонентах."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source = file.read()
            
            tree = ast.parse(source)
            self._analyze_ast(tree)
            
        except Exception as e:
            print(f"Ошибка при анализе файла: {e}")
            sys.exit(1)

    def _analyze_ast(self, tree: ast.AST) -> None:
        """Анализирует AST дерево для извлечения компонентов."""
        for node in ast.walk(tree):
            # Анализ переменных и констант
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    if node.id.isupper():
                        self.constants.add(node.id)
                    else:
                        self.variables.add(node.id)
            
            # Анализ функций и процедур
            elif isinstance(node, ast.FunctionDef):
                # Проверяем, возвращает ли функция значение
                returns_value = False
                for n in ast.walk(node):
                    if isinstance(n, ast.Return) and n.value is not None:
                        returns_value = True
                        break
                
                if node.name in self.builtin_functions:
                    if returns_value:
                        self.system_functions.add(node.name)
                    else:
                        self.system_procedures.add(node.name)
                else:
                    if returns_value:
                        self.user_functions.add(node.name)
                    else:
                        self.user_procedures.add(node.name)

    def save_report(self, output_file: str) -> None:
        """Сохраняет отчет в файл."""
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write("=== Отчет по анализу Python кода ===\n\n")
            
            file.write("Переменные (по алфавиту):\n")
            for var in sorted(self.variables):
                file.write(f"- {var}\n")
            
            file.write("\nКонстанты (по алфавиту):\n")
            for const in sorted(self.constants):
                file.write(f"- {const}\n")
            
            file.write("\nМетки (по алфавиту):\n")
            for label in sorted(self.labels):
                file.write(f"- {label}\n")
            
            file.write("\nСистемные процедуры:\n")
            for proc in sorted(self.system_procedures):
                file.write(f"- {proc}\n")
            
            file.write("\nСистемные функции:\n")
            for func in sorted(self.system_functions):
                file.write(f"- {func}\n")
            
            file.write("\nПользовательские процедуры:\n")
            for proc in sorted(self.user_procedures):
                file.write(f"- {proc}\n")
            
            file.write("\nПользовательские функции:\n")
            for func in sorted(self.user_functions):
                file.write(f"- {func}\n")

def main():
    if len(sys.argv) != 3:
        print("Использование: python analyzer.py <входной_файл> <выходной_файл>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    analyzer = PythonCodeAnalyzer()
    analyzer.analyze_file(input_file)
    analyzer.save_report(output_file)
    print(f"Анализ завершен. Результаты сохранены в {output_file}")

if __name__ == "__main__":
    main()