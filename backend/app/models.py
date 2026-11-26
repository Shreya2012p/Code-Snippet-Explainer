
# Import BaseModel to define structured data models
# Import Field to apply validation rules and default values
from pydantic import BaseModel, Field

# Import Any to allow flexible data types in dictionaries and lists
from typing import Any


# --------------------------------------------------
# 1. ANALYSIS REQUEST MODEL
# --------------------------------------------------

# Defines the structure and validation rules for incoming
# code analysis requests received by the FastAPI backend
class AnalyzeRequest(BaseModel):

    # Source code submitted by the user
    # Must contain at least 1 character and cannot exceed 30,000 characters
    code: str = Field(min_length=1, max_length=30000)

    # Programming language of the submitted code
    # Defaults to Python if the user does not specify a language
    # Must contain between 1 and 40 characters
    language: str = Field(
        default="python",
        min_length=1,
        max_length=40
    )

    # Controls whether the generated analysis report
    # should be forwarded to the n8n workflow for Slack delivery
    # Disabled by default
    send_to_slack: bool = False

    # Controls the level of detail in the AI-generated analysis
    # Only three values are accepted: concise, detailed or deep
    # Defaults to detailed analysis
    detail_level: str = Field(
        default="detailed",
        pattern="^(concise|detailed|deep)$"
    )


# --------------------------------------------------
# 2. ANALYSIS RESPONSE MODEL
# --------------------------------------------------

# Defines the expected structure of the code analysis response
# returned by the application
class AnalyzeResponse(BaseModel):

    # Identifies the programming language analyzed
    language: str

    # Provides a high-level summary of the submitted code
    summary: str

    # Explains how the code works in understandable language
    explanation: str

    # Contains step-by-step explanations of the code execution
    steps: list[dict[str, Any]]

    # Describes the organization and components of the code
    # such as classes, functions and variables
    code_structure: dict[str, Any]

    # Lists the programming concepts identified in the code
    concepts: list[dict[str, Any]]

    # Describes how data moves through the program
    data_flow: list[str]

    # Contains information about the program's inputs and outputs
    inputs_outputs: dict[str, Any]

    # Provides complexity-related analysis
    # such as time and space complexity, when applicable
    complexity: dict[str, Any]

    # Contains detected coding issues, bugs or potential risks
    issues: list[dict[str, Any]]

    # Lists design patterns or coding patterns identified in the code
    patterns_used: list[str]

    # Provides suggestions for improving the submitted code
    improvement: str

    # Contains the improved version of the submitted source code
    improved_code: str

    # Explains the reasons behind the suggested code improvements
    improvement_rationale: str

    # Contains suggested test cases for checking program behavior
    test_cases: list[dict[str, Any]]

    # Contains verification information about the analysis
    verification: dict[str, Any]

    # Stores any warnings generated during the analysis
    # Defaults to an empty list
    warnings: list[str] = []

    # Indicates whether the report was successfully forwarded
    # to the n8n webhook for further delivery
    # Defaults to False
    slack_sent: bool = False
