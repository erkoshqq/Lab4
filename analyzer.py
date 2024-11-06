import ast
import builtins
import sys
from typing import Set
from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Footer, ListView, ListItem
from textual.containers import Container

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
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    if node.id.isupper():
                        self.constants.add(node.id)
                    else:
                        self.variables.add(node.id)
            elif isinstance(node, ast.FunctionDef):
                returns_value = any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(node))
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

class AnalyzerApp(App):
    CSS_PATH = "analyzer.css"  # Можно настроить внешний вид через CSS

    def __init__(self, analyzer: PythonCodeAnalyzer):
        super().__init__()
        self.analyzer = analyzer

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("=== Отчет по анализу Python кода ==="),
            Static(f"Переменные: {len(self.analyzer.variables)}"),
            ListView(*[ListItem(Static(item)) for item in sorted(self.analyzer.variables)]),
            Static(f"Константы: {len(self.analyzer.constants)}"),
            ListView(*[ListItem(Static(item)) for item in sorted(self.analyzer.constants)]),
            Static(f"Системные процедуры: {len(self.analyzer.system_procedures)}"),
            ListView(*[ListItem(Static(item)) for item in sorted(self.analyzer.system_procedures)]),
            Static(f"Системные функции: {len(self.analyzer.system_functions)}"),
            ListView(*[ListItem(Static(item)) for item in sorted(self.analyzer.system_functions)]),
            Static(f"Пользовательские процедуры: {len(self.analyzer.user_procedures)}"), 
            ListView(*[ListItem(Static(item)) for item in sorted(self.analyzer.user_procedures)]),
            Static(f"Пользовательские функции: {len(self.analyzer.user_functions)}"),
            ListView(*[ListItem(Static(item)) for item in sorted(self.analyzer.user_functions)]),
        )
        yield Footer()

def main():
    if len(sys.argv) != 2:
        print("Использование: python analyzer.py <входной_файл>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    analyzer = PythonCodeAnalyzer()
    analyzer.analyze_file(input_file)
    
    app = AnalyzerApp(analyzer)
    app.run()

if __name__ == "__main__":
    main()

