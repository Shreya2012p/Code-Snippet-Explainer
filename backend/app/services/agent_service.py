
# Import ast to parse and validate Python source code syntax
import ast

# Import re for regular-expression operations (available for pattern-based checks)
import re


# --------------------------------------------------
# 1. ANALYSIS VERIFICATION FUNCTION
# --------------------------------------------------

# Verifies the AI-generated analysis using automated consistency checks
#
# Parameters:
# code     : Original source code submitted by the user
# language : Programming language of the submitted code
# analysis : AI-generated code analysis report
# parsed   : Results from the code parsing stage
def verify_analysis(code, language, analysis, parsed):

    # Store the results of individual verification checks
    checks = []

    # Identify whether the submitted programming language is Python
    is_python = language.lower() in ("python", "py")

    # Check whether the source code was successfully parsed
    # Python requires successful AST parsing
    # Other languages currently use basic or heuristic parsing
    syntax_valid = (
        parsed.get("parse_status") == "success"
        if is_python
        else parsed.get("parse_status") in ("basic", "heuristic")
    )

    # Add the syntax and parser coverage result to the verification report
    checks.append({
        "name": "Input syntax / parser coverage",
        "passed": syntax_valid,

        # Provide a different explanation depending on the language
        # and whether parsing was successful
        "detail": (
            "Python AST parsed the submitted snippet."
            if is_python and syntax_valid
            else (
                "Python syntax error detected; interpretation is limited."
                if is_python
                else
                "No compiler-grade parser is configured for this language; structural checks are heuristic."
            )
        )
    })


    # --------------------------------------------------
    # 2. VERIFY IMPROVED CODE SYNTAX
    # --------------------------------------------------

    # Retrieve the improved code suggested by the AI model
    improved = analysis.get("improved_code", "")

    # If the language is Python and the original code parsed successfully,
    # validate the syntax of the AI-generated improved code
    if is_python and improved and parsed.get("parse_status") == "success":

        try:
            # Parse the improved Python code using the AST module
            # This checks whether the suggested code is syntactically valid
            ast.parse(improved)

            # Mark the improved code as syntactically valid
            improved_ok = True

            # Store the verification explanation
            detail = "The proposed Python rewrite is syntactically parseable."

        except SyntaxError as e:

            # Mark the improved code as invalid if a syntax error occurs
            improved_ok = False

            # Include the error line number and description
            detail = (
                f"Proposed rewrite has a Python syntax error "
                f"at line {e.lineno}: {e.msg}"
            )

        # Add the improved-code syntax result to the verification checks
        checks.append({
            "name": "Improved-code syntax check",
            "passed": improved_ok,
            "detail": detail
        })

    # For other languages, the improved code is not compiler-validated
    elif improved:

        # Mark the check as None to indicate that it was not performed
        checks.append({
            "name": "Improved-code syntax check",
            "passed": None,
            "detail": (
                "Not checked by a language compiler; "
                "review and run language-specific tests."
            )
        })


    # --------------------------------------------------
    # 3. CHECK FOR FABRICATED EXECUTION CLAIMS
    # --------------------------------------------------

    # Combine the AI-generated summary, explanation and step explanations
    # into one text string for checking
    claims = " ".join(
        [
            str(analysis.get("summary", "")),
            str(analysis.get("explanation", ""))
        ] +
        [
            str(s.get("explanation", ""))
            for s in analysis.get("steps", [])
            if isinstance(s, dict)
        ]
    ).lower()

    # Identify phrases that may incorrectly suggest that the code
    # was actually executed or tested by the application
    unsafe_claim = any(
        x in claims
        for x in [
            "i executed",
            "i ran the code",
            "the test passed",
            "the output is"
        ]
    )

    # Add the execution-claim verification result
    checks.append({
        "name": "No fabricated execution claim",
        "passed": not unsafe_claim,

        # Explain whether suspicious execution claims were detected
        "detail": (
            "No explicit claim of execution or test results was detected."
            if not unsafe_claim
            else
            "The model appears to state execution or test results "
            "that this service did not perform."
        )
    })


    # --------------------------------------------------
    # 4. SOURCE-GROUNDING CHECK
    # --------------------------------------------------

    # Add a reminder that AI-generated explanations should be
    # compared against the actual submitted source code
    checks.append({
        "name": "Source-grounding reminder",
        "passed": True,
        "detail": (
            "AI explanation is advisory; compare references "
            "with the submitted snippet."
        )
    })


    # --------------------------------------------------
    # 5. CALCULATE FINAL VERIFICATION STATUS
    # --------------------------------------------------

    # Consider the verification successful if no check explicitly failed
    # A None value means a check was not applicable or not performed
    passed = all(
        c["passed"] is not False
        for c in checks
    )

    # Return the final verification report
    return {
        # Set status based on the overall verification result
        "status": "verified" if passed else "needs_review",

        # Overall verification result
        "passed": passed,

        # Include all individual verification results
        "checks": checks,

        # Clarify the limitations of automated verification
        "note": (
            "Automated consistency checks only. This is not a formal proof, "
            "full static analysis, security audit, or runtime test."
        )
    }
