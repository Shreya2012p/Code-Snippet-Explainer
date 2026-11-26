
# --------------------------------------------------
# 1. IMPORT REQUIRED LIBRARIES
# --------------------------------------------------

# Import json to read and process the programming knowledge base
import json

# Import re to identify keywords from source code and knowledge records
import re

# Import Path to construct and manage file system paths
import os
from pathlib import Path


# --------------------------------------------------
# 2. DEFINE THE KNOWLEDGE BASE FILE LOCATION
# --------------------------------------------------

# Locate the code_patterns.json file inside the project's data directory
#
# __file__ represents the current Python file.
# resolve() converts its location into an absolute path.
# parent.parent moves two directory levels upward.
# Then the data folder and JSON file path are appended.
DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "code_patterns.json"
)


# --------------------------------------------------
# 3. DEFINE THE PATTERN RETRIEVER CLASS
# --------------------------------------------------

# This class manages the programming knowledge base.
# It loads, normalizes and retrieves relevant coding patterns.
class PatternRetriever:


    # --------------------------------------------------
    # 3A. INITIALIZE THE RETRIEVER
    # --------------------------------------------------

    # Constructor method called automatically when an object is created
    def __init__(self):

        # Set the retrieval approach to keyword matching
        self.mode = "keyword"

        # Load the programming patterns from the JSON knowledge base
        self.patterns = self._load()


    # --------------------------------------------------
    # 3B. LOAD THE KNOWLEDGE BASE
    # --------------------------------------------------

    # Reads the JSON file and converts its records
    # into a consistent internal format
    def _load(self):

        # Check whether the knowledge base file exists
        if not DATA_FILE.exists():

            # Raise an error if the file is missing
            raise FileNotFoundError(
                f"Knowledge base not found: {DATA_FILE}"
            )

        # Open the JSON file in read mode using UTF-8 encoding
        with open(DATA_FILE, "r", encoding="utf-8") as file:

            # Parse the JSON content into a Python object
            data = json.load(file)


        # Check whether the JSON root is a dictionary
        if isinstance(data, dict):

            # If it is a dictionary, retrieve the records
            # stored under the "patterns" key
            records = data.get("patterns", [])

        # Check whether the JSON root is directly a list
        elif isinstance(data, list):

            # Use the list itself as the collection of records
            records = data

        else:

            # Reject unsupported JSON root structures
            raise ValueError("Invalid code patterns JSON format")


        # Ensure the extracted pattern records are stored in a list
        if not isinstance(records, list):

            # Raise an error if the patterns field is not a list
            raise ValueError("'patterns' must contain a list")


        # Create a new list to store cleaned and standardized records
        normalized = []


        # Process every record in the knowledge base
        # enumerate() also provides the record's index
        for index, record in enumerate(records):

            # Ignore entries that are not dictionaries
            if not isinstance(record, dict):
                continue


            # Extract the pattern title
            # Use "title" first, then "name", and finally a default name
            title = (
                record.get("title")
                or record.get("name")
                or f"Pattern {index + 1}"
            )

            # Extract the category or use General as the default
            category = record.get("category") or "General"


            # Retrieve the main content of the pattern
            content = record.get("content")


            # If content is missing or empty, construct it
            # using the description and best-practice fields
            if not content:

                # Extract the description
                description = record.get("description", "")

                # Extract the recommended best practice
                best_practice = record.get("best_practice", "")

                # Combine both fields into one readable content string
                content = (
                    f"{description} "
                    f"Best practice: {best_practice}"
                ).strip()


            # Store the record in a standardized dictionary format
            normalized.append({

                # Convert the record ID into a string
                "id": str(record.get("id", index + 1)),

                # Store the normalized title
                "title": str(title),

                # Store the normalized category
                "category": str(category),

                # Store the normalized content
                "content": str(content)
            })


        # Return all cleaned and standardized knowledge records
        return normalized


    # --------------------------------------------------
    # 3C. RETRIEVE RELEVANT PROGRAMMING PATTERNS
    # --------------------------------------------------

    # Searches the knowledge base for patterns related to the
    # submitted source code and programming language
    #
    # Parameters:
    # code     : Source code submitted by the user
    # language : Programming language of the source code
    # top_k    : Maximum number of matching patterns to return
    #
    # Returns:
    # A list of the most relevant programming patterns
    def retrieve(self, code: str, language: str, top_k: int = 5):

        # Return an empty list if the knowledge base has no patterns
        if not self.patterns:
            return []


        # --------------------------------------------------
        # 3C-1. EXTRACT KEYWORDS FROM THE SOURCE CODE
        # --------------------------------------------------

        # Identify words that start with a letter or underscore
        # and may contain letters, numbers or underscores
        #
        # Convert the language and source code to lowercase
        # so keyword matching is case-insensitive
        tokens = set(
            re.findall(
                r"[A-Za-z_][A-Za-z0-9_]*",
                f"{language} {code}".lower()
            )
        )


        # Create a list to store matching records and their scores
        scored = []


        # --------------------------------------------------
        # 3C-2. COMPARE SOURCE CODE WITH KNOWLEDGE RECORDS
        # --------------------------------------------------

        # Examine every programming pattern in the knowledge base
        for record in self.patterns:

            # Combine the title, category and content into one
            # searchable text string and convert it to lowercase
            searchable_text = (
                record["title"] + " " +
                record["category"] + " " +
                record["content"]
            ).lower()


            # Extract keywords from the knowledge record
            # Store them in a set to avoid duplicate words
            keywords = set(
                re.findall(
                    r"[A-Za-z_][A-Za-z0-9_]*",
                    searchable_text
                )
            )


            # Calculate the relevance score
            # Each shared keyword contributes one point
            score = len(tokens.intersection(keywords))


            # Keep only records with at least one matching keyword
            if score > 0:

                # Store the relevance score together with its record
                scored.append((score, record))


        # --------------------------------------------------
        # 3C-3. RANK MATCHING PATTERNS
        # --------------------------------------------------

        # Sort records by relevance score in descending order
        # Patterns with more matching keywords appear first
        scored.sort(
            key=lambda item: item[0],
            reverse=True
        )


        # --------------------------------------------------
        # 3C-4. HANDLE CASES WITH NO KEYWORD MATCHES
        # --------------------------------------------------

        # If no records match the submitted code,
        # return the first top_k default knowledge patterns
        if not scored:
            return self.patterns[:top_k]


        # --------------------------------------------------
        # 3C-5. RETURN THE TOP MATCHING PATTERNS
        # --------------------------------------------------

        # Extract only the records from the scored results
        # Return at most the requested number of patterns
        return [
            record
            for score, record in scored[:top_k]
        ]


# --------------------------------------------------
# 4. CREATE A SHARED RETRIEVER INSTANCE
# --------------------------------------------------

# Create one PatternRetriever object when this module is imported.
# This loads the knowledge base and makes the retriever available
# to other modules, such as analysis_service.py.
retriever = PatternRetriever()
