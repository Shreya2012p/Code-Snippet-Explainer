
# Import JSON to convert Python data into JSON format
import json

# Import urllib modules to send HTTP requests and handle network errors
import urllib.request
import urllib.error

# Import FastAPI to create the backend API
# HTTPException is used to return proper HTTP error responses
from fastapi import FastAPI, HTTPException

# Import CORS middleware to allow communication between frontend and backend
from fastapi.middleware.cors import CORSMiddleware

# Import application configuration settings
from app.config import (
    APP_NAME,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    N8N_WEBHOOK_URL
)

# Import the request model used to validate incoming analysis requests
from app.models import AnalyzeRequest

# Import the main code analysis function
from app.services.analysis_service import analyze


# --------------------------------------------------
# 1. INITIALIZE FASTAPI APPLICATION
# --------------------------------------------------

# Create the FastAPI application with its name, version and description
app = FastAPI(
    title=APP_NAME,
    version="2.0.0",
    description="Structured code intelligence using Python analysis, RAG, Ollama, verification and n8n."
)


# --------------------------------------------------
# 2. CONFIGURE CORS
# --------------------------------------------------

# Enable Cross-Origin Resource Sharing (CORS)
# This allows the React frontend running on port 5173
# to communicate with the FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# 3. HEALTH CHECK API
# --------------------------------------------------

# GET endpoint to check whether the backend and AI model are available
@app.get("/api/health")
def health():

    # Initialize connection status variables
    ollama_ok = False
    model_available = False

    try:
        # Create a request to retrieve the list of installed Ollama models
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL.rstrip('/')}/api/tags"
        )

        # Send the request and read the response
        with urllib.request.urlopen(req, timeout=4) as r:
            tags = json.loads(r.read().decode())

        # Mark Ollama as reachable if the request succeeds
        ollama_ok = True

        # Check whether the configured AI model is installed
        model_available = any(
            m.get("name", "").split(":")[0] == OLLAMA_MODEL.split(":")[0]
            for m in tags.get("models", [])
        )

    except Exception:
        # Keep the status flags False if Ollama cannot be reached
        pass

    # Return backend health and integration information
    return {
        "status": "ok",
        "ollama_reachable": ollama_ok,
        "model_available": model_available,
        "model": OLLAMA_MODEL,
        "retrieval": "ChromaDB with keyword fallback",
        "n8n_configured": bool(N8N_WEBHOOK_URL)
    }


# --------------------------------------------------
# 4. CODE ANALYSIS API
# --------------------------------------------------

# POST endpoint that receives code and starts the analysis process
@app.post("/api/analyze")
def analyze_code(request: AnalyzeRequest):

    try:
        # Pass the submitted code, programming language and detail level
        # to the analysis service
        result = analyze(
            request.code,
            request.language,
            request.detail_level
        )

        # Send the generated report to the n8n workflow when requested
        # Otherwise, mark Slack delivery as False
        result["slack_sent"] = (
            send_to_n8n(result, request.code)
            if request.send_to_slack
            else False
        )

        # Return the complete analysis result to the frontend
        return result

    # Handle AI service or processing errors
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
        )

    # Handle invalid or incorrectly formatted AI responses
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Invalid model response: {exc}"
        )

    # Handle any other unexpected analysis errors
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {exc}"
        )


# --------------------------------------------------
# 5. SHARE REPORT API
# --------------------------------------------------

# POST endpoint to manually forward an existing report to n8n
@app.post("/api/share")
def share_report(payload: dict):

    # Send the supplied report and its code to the n8n workflow
    sent = send_to_n8n(
        payload,
        payload.get("code", "")
    )

    # Return an error if the webhook is unavailable or not configured
    if not sent:
        raise HTTPException(
            status_code=503,
            detail="n8n webhook is not configured or unavailable."
        )

    # Return confirmation when the report is successfully forwarded
    return {
        "sent": True,
        "message": "Report forwarded to n8n."
    }


# --------------------------------------------------
# 6. N8N WEBHOOK INTEGRATION
# --------------------------------------------------

# Helper function to forward the analysis report to n8n
def send_to_n8n(result, code):

    # Check whether an n8n webhook URL has been configured
    if not N8N_WEBHOOK_URL:
        return False

    # Prepare the report payload containing the event, source code
    # and complete AI analysis result
    data = json.dumps({
        "event": "code_analysis_completed",
        "code": code,
        "analysis": result
    }).encode()

    # Create an HTTP POST request with JSON content
    req = urllib.request.Request(
        N8N_WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        # Send the report to n8n and wait for its response
        with urllib.request.urlopen(req, timeout=15) as response:

            # Return True if n8n responds with a successful HTTP status
            return 200 <= response.status < 300

    # Handle network errors and request timeouts
    except (urllib.error.URLError, TimeoutError):
        return False
