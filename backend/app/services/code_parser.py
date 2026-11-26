
# Import ast to parse Python source code into an Abstract Syntax Tree (AST)
import ast

# Import Any to support flexible data types in dictionaries and lists
from typing import Any


# --------------------------------------------------
# 1. MAIN CODE PARSER FUNCTION
# --------------------------------------------------

# Analyzes the submitted source code and extracts its structural details
#
# Parameters:
# code     : Source code submitted by the user
# language : Programming language of the submitted code
#
# Returns:
# A dictionary containing code structure, syntax information
# and extracted programming constructs
def parse_code(code: str, language: str) -> dict[str, Any]:

    # Normalize the programming language name
    # Convert it to lowercase and remove unnecessary spaces
    lang = language.lower().strip()

    # Initialize the result dictionary with default values
    # These fields store the information extracted from the source code
    result = {
        "language": lang,

        # Count the total number of lines in the submitted code
        "line_count": len(code.splitlines()),

        # Count the total number of characters in the code
        "character_count": len(code),

        # Store discovered functions, classes and imported modules
        "functions": [],
        "classes": [],
        "imports": [],

        # Store control structures and programming constructs
        "constructs": [],

        # Store variable declarations and assignments
        "variables": [],

        # Store documentation strings associated with functions and classes
        "docstrings": [],

        # Default parser status before language-specific parsing
        "parse_status": "basic",

        # Stores syntax error details if parsing fails
        "syntax_error": None,

        # Counters for important programming statements
        "returns": 0,
        "raises": 0,
        "awaits": 0
    }


    # --------------------------------------------------
    # 2. PYTHON AST-BASED PARSING
    # --------------------------------------------------

    # Check whether the submitted language is Python
    if lang in ("python", "py"):

        try:
            # Convert Python source code into an Abstract Syntax Tree
            # This validates Python syntax and exposes its code structure
            tree = ast.parse(code)

            # Mark parsing as successful
            result["parse_status"] = "success"

            # Traverse all nodes in the Abstract Syntax Tree
            # Each node represents a programming element in the source code
            for node in ast.walk(tree):

                # ------------------------------------------
                # 2A. FUNCTION EXTRACTION
                # ------------------------------------------

                # Identify normal and asynchronous function definitions
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

                    # Extract function name, line numbers, arguments
                    # and return type annotation
                    result["functions"].append({
                        "name": node.name,
                        "line": node.lineno,

                        # Retrieve the ending line number when available
                        "end_line": getattr(
                            node,
                            "end_lineno",
                            node.lineno
                        ),

                        # Extract positional-only, regular and keyword-only arguments
                        "arguments": [
                            a.arg
                            for a in (
                                node.args.posonlyargs
                                + node.args.args
                                + node.args.kwonlyargs
                            )
                        ],

                        # Identify whether the function is asynchronous
                        "async": isinstance(node, ast.AsyncFunctionDef),

                        # Extract the return type annotation if present
                        "returns_annotation": (
                            ast.unparse(node.returns)
                            if node.returns
                            else None
                        )
                    })

                    # Retrieve the function's documentation string
                    doc = ast.get_docstring(node)

                    # Store the docstring if one exists
                    if doc:
                        result["docstrings"].append({
                            "name": node.name,
                            "text": doc
                        })


                # ------------------------------------------
                # 2B. CLASS EXTRACTION
                # ------------------------------------------

                # Identify class definitions in the Python code
                elif isinstance(node, ast.ClassDef):

                    # Store the class name, starting line and its methods
                    result["classes"].append({
                        "name": node.name,
                        "line": node.lineno,

                        # Extract methods defined directly inside the class
                        "methods": [
                            n.name
                            for n in node.body
                            if isinstance(
                                n,
                                (ast.FunctionDef, ast.AsyncFunctionDef)
                            )
                        ]
                    })


                # ------------------------------------------
                # 2C. IMPORT EXTRACTION
                # ------------------------------------------

                # Identify import statements
                # This includes both import and from-import syntax
                elif isinstance(node, (ast.Import, ast.ImportFrom)):

                    # Convert the import node back into readable Python code
                    result["imports"].append(ast.unparse(node))


                # ------------------------------------------
                # 2D. PROGRAMMING CONSTRUCT EXTRACTION
                # ------------------------------------------

                # Identify important programming constructs such as:
                # loops, conditions, exception handling, context managers,
                # pattern matching, comprehensions and lambda expressions
                elif isinstance(
                    node,
                    (
                        ast.For,
                        ast.AsyncFor,
                        ast.While,
                        ast.If,
                        ast.Try,
                        ast.With,
                        ast.AsyncWith,
                        ast.Match,
                        ast.ListComp,
                        ast.DictComp,
                        ast.SetComp,
                        ast.Lambda
                    )
                ):

                    # Store the construct type and its source line number
                    result["constructs"].append({
                        "type": type(node).__name__,
                        "line": getattr(node, "lineno", None)
                    })


                # ------------------------------------------
                # 2E. VARIABLE EXTRACTION
                # ------------------------------------------

                # Identify regular assignments, annotated assignments
                # and assignment expressions
                elif isinstance(
                    node,
                    (ast.Assign, ast.AnnAssign, ast.NamedExpr)
                ):

                    # Regular assignments can contain multiple targets
                    # Other assignment types have a single target
                    targets = (
                        node.targets
                        if isinstance(node, ast.Assign)
                        else [node.target]
                    )

                    # Extract variable names from simple name targets
                    for target in targets:

                        if isinstance(target, ast.Name):

                            result["variables"].append({
                                "name": target.id,
                                "line": node.lineno
                            })


                # ------------------------------------------
                # 2F. STATEMENT COUNTERS
                # ------------------------------------------

                # Count return statements
                elif isinstance(node, ast.Return):
                    result["returns"] += 1

                # Count exception-raising statements
                elif isinstance(node, ast.Raise):
                    result["raises"] += 1

                # Count await expressions used in asynchronous code
                elif isinstance(node, ast.Await):
                    result["awaits"] += 1


        # Handle invalid Python syntax
        except SyntaxError as exc:

            # Mark the parser status as a syntax error
            result["parse_status"] = "syntax_error"

            # Store the error message and its location
            result["syntax_error"] = {
                "message": exc.msg,
                "line": exc.lineno,
                "offset": exc.offset
            }


    # --------------------------------------------------
    # 3. HEURISTIC PARSING FOR OTHER LANGUAGES
    # --------------------------------------------------

    # For JavaScript, TypeScript, Java, C, C++ and C#,
    # use regular expressions to identify selected code patterns
    elif lang in (
        "javascript",
        "js",
        "typescript",
        "ts",
        "java",
        "c",
        "cpp",
        "c++",
        "csharp",
        "c#"
    ):

        # Import regular expressions for pattern-based code extraction
        import re

        # Define regular-expression patterns for selected constructs
        # These patterns provide basic structural identification
        patterns = [
            ("function", r"\bfunction\s+([A-Za-z_$][\w$]*)"),
            ("class", r"\bclass\s+([A-Za-z_$][\w$]*)"),
            ("arrow_function", r"=>"),
            ("if", r"\bif\s*\("),
            ("loop", r"\b(for|while)\s*\(")
        ]

        # Check the submitted code against each defined pattern
        for kind, pat in patterns:

            # Find every occurrence of the current pattern
            for m in re.finditer(pat, code):

                # Store the construct type and its source line number
                # Add the matched name when the pattern captures one
                result["constructs"].append({
                    "type": kind,

                    # Calculate the line number from the match position
                    "line": code.count("\n", 0, m.start()) + 1,

                    # Include the captured name when available
                    **(
                        {"name": m.group(1)}
                        if m.lastindex
                        else {}
                    )
                })

        # Mark the result as heuristic because regular expressions
        # do not provide full compiler-level syntax validation
        result["parse_status"] = "heuristic"


    # --------------------------------------------------
    # 4. RETURN PARSING RESULTS
    # --------------------------------------------------

    # Return the complete dictionary containing extracted
    # code structure, parser status and syntax information
    return result
