
# Import the code parser to extract the structure and syntax information
# from the submitted source code
from app.services.code_parser import parse_code

# Import the RAG retriever to fetch relevant programming knowledge
# and contextual information from the knowledge base
from app.services.rag_service import retriever

# Import the AI analysis function that generates the code analysis report
from app.services.llm_service import generate_analysis

# Import the verification function to validate the AI-generated analysis
from app.services.agent_service import verify_analysis


# --------------------------------------------------
# 1. SAFE RESPONSE STRUCTURE
# --------------------------------------------------

# Ensures that the AI-generated result contains all expected fields
# and that each field has the correct basic data type
def _safe_shape(result):

    # Define default values for all expected analysis fields
    # These defaults prevent missing or incorrectly typed fields
    # from breaking the application
    defaults = {
        "summary": "Analysis generated.",
        "explanation": "",
        "steps": [],
        "code_structure": {},
        "concepts": [],
        "data_flow": [],
        "inputs_outputs": {
            "inputs": [],
            "outputs": [],
            "side_effects": []
        },
        "complexity": {
            "time": "not determined",
            "space": "not determined",
            "assumptions": "Insufficient information."
        },
        "issues": [],
        "patterns_used": [],
        "improvement": "Review the identified findings.",
        "improved_code": "",
        "improvement_rationale": "",
        "test_cases": []
    }

    # Check every expected field in the AI-generated result
    for key, value in defaults.items():

        # Replace missing fields or fields with incorrect data types
        # with their corresponding default values
        if not isinstance(result.get(key), type(value)):
            result[key] = value

    # Perform an additional check to ensure these fields are lists
    # This helps maintain a consistent response structure
    for key in (
        "steps",
        "concepts",
        "issues",
        "data_flow",
        "test_cases",
        "patterns_used"
    ):
        if not isinstance(result.get(key), list):
            result[key] = []

    # Return the normalized analysis result
    return result


# --------------------------------------------------
# 2. MAIN CODE ANALYSIS FUNCTION
# --------------------------------------------------

# Coordinates the complete code analysis pipeline
#
# Parameters:
# code        : Source code submitted by the user
# language    : Programming language of the submitted code
# detail_level: Controls the depth of the AI-generated explanation
#
# Default analysis level is "detailed"
def analyze(code, language, detail_level="detailed"):

    # STEP 1: Parse the submitted source code
    # Extract syntax information, functions, classes and other
    # structural details using the code parser
    parsed = parse_code(code, language)

    # STEP 2: Retrieve relevant programming knowledge using RAG
    # Search the knowledge base for information related to the
    # submitted code and its programming language
    patterns = retriever.retrieve(code, language)

    # STEP 3: Generate AI-powered code analysis
    # Send the source code, language, parser information,
    # retrieved knowledge and requested detail level to the AI model
    #
    # _safe_shape() ensures the generated response follows
    # the expected output structure
    result = _safe_shape(
        generate_analysis(
            code,
            language,
            parsed,
            patterns,
            detail_level
        )
    )

    # STEP 4: Enrich the code structure with parser information
    # Preserve the AI-generated code structure and add
    # factual information extracted by the parser
    result["code_structure"] = {
        **result.get("code_structure", {}),
        "parser_facts": parsed
    }

    # STEP 5: Verify the AI-generated analysis
    # Check syntax information, improved-code syntax and
    # possible unsupported execution claims
    result["verification"] = verify_analysis(
        code,
        language,
        result,
        parsed
    )

    # STEP 6: Populate identified programming patterns
    # Use the AI-generated patterns if available
    # Otherwise, use the titles of knowledge items retrieved through RAG
    result["patterns_used"] = (
        result.get("patterns_used")
        or [p["title"] for p in patterns]
    )

    # STEP 7: Add information about the RAG retrieval process
    # Include the retrieval mode, number of retrieved items
    # and titles of the sources used for contextual analysis
    result["retrieval"] = {
        "mode": retriever.mode,
        "items_retrieved": len(patterns),
        "sources": [p["title"] for p in patterns]
    }

    # STEP 8: Initialize a list to store analysis warnings
    warnings = []

    # Check whether the Python parser detected a syntax error
    if parsed.get("parse_status") == "syntax_error":

        # Add a warning explaining that normal execution
        # cannot be assumed when syntax errors are present
        warnings.append(
            f"Python syntax error: {parsed.get('syntax_error')}. "
            "Normal execution cannot be assumed."
        )

    # Check whether heuristic parsing was used
    elif parsed.get("parse_status") in ("basic", "heuristic"):

        # Inform the user that a full compiler-grade parser
        # is not configured for this programming language
        warnings.append(
            "This language currently uses heuristic structure "
            "extraction, not a full compiler/parser."
        )

    # Check whether the verification process identified concerns
    if not result["verification"]["passed"]:

        # Add a warning asking the user to review the findings
        warnings.append(
            "Verification flagged one or more concerns; "
            "review before relying on this result."
        )

    # STEP 9: Attach all collected warnings to the final report
    result["warnings"] = warnings

    # STEP 10: Add the programming language to the final result
    result["language"] = language

    # Return the complete structured analysis report
    return result
