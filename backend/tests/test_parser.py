
# --------------------------------------------------
# 1. IMPORT THE FUNCTION UNDER TEST
# --------------------------------------------------

# Import verify_analysis from the Agent Service.
# This is the function that performs automated consistency
# and syntax checks on the AI-generated code analysis.
from app.services.agent_service import verify_analysis


# --------------------------------------------------
# 2. TEST VALID IMPROVED PYTHON CODE
# --------------------------------------------------

# Verify that the Agent Service accepts an improved code
# snippet when its Python syntax is valid.
def test_agent_checks_improved_python_syntax():

    # Simulate parser information indicating that
    # the original Python code was parsed successfully.
    parsed = {
        "parse_status": "success"
    }

    # Call verify_analysis() with:
    # - Original source code: x=1
    # - Programming language: Python
    # - A sample AI-generated analysis
    # - A valid improved Python code snippet
    result = verify_analysis(
        "x=1",
        "python",
        {
            "summary": "Assign x.",
            "explanation": "Stores 1.",
            "steps": [],
            "improved_code": "x = 1"
        },
        parsed
    )

    # Assert that the complete verification result passes.
    # If result["passed"] is False, the test fails.
    assert result["passed"]

    # Check that the verification checks contain an
    # improved-code syntax check that passed successfully.
    #
    # any() returns True if at least one item in the
    # generator expression satisfies both conditions:
    # 1. The check name is "Improved-code syntax check".
    # 2. Its passed value is True.
    assert any(
        c["name"] == "Improved-code syntax check"
        and c["passed"]
        for c in result["checks"]
    )


# --------------------------------------------------
# 3. TEST INVALID IMPROVED PYTHON CODE
# --------------------------------------------------

# Verify that the Agent Service identifies a syntax error
# in an AI-generated improved Python code snippet.
def test_agent_flags_invalid_rewrite():

    # Simulate a successful parse of the original Python code.
    # This allows the improved-code syntax check to run.
    parsed = {
        "parse_status": "success"
    }

    # Call verify_analysis() with an invalid improved code snippet.
    # "def broken(:" contains invalid Python function syntax.
    result = verify_analysis(
        "x=1",
        "python",
        {
            "summary": "Assign x.",
            "explanation": "Stores 1.",
            "steps": [],

            # Deliberately invalid Python code for testing
            "improved_code": "def broken(:"
        },
        parsed
    )

    # Assert that the overall verification does not pass.
    # The invalid improved code should cause the
    # improved-code syntax check to fail.
    assert not result["passed"]
