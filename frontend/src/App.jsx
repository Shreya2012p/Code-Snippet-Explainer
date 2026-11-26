
/* ============================================================
   SECTION 1: IMPORTS AND DEPENDENCIES
   ============================================================ */

// React hooks for managing component state and lifecycle
import { useEffect, useState } from "react";

// Icons used in the user interface
import {
  Sparkles,
  Code2,
  Github,
  Activity,
  Send,
  LoaderCircle,
  Zap
} from "lucide-react";

// Reusable frontend components
import CodeEditor from "./components/CodeEditor";
import AnalysisResult from "./components/AnalysisResult";

// API functions used to communicate with the backend
import { analyzeCode, getHealth } from "./services/api";


/* ============================================================
   SECTION 2: DEFAULT STARTER CODE
   ============================================================ */

// Sample Python code displayed when the application first loads
const starter = `def calculate_total(prices):
    total = 0
    for price in prices:
        total += price
    return total`;


/* ============================================================
   SECTION 3: MAIN APPLICATION COMPONENT
   ============================================================ */

export default function App() {

  /* ----------------------------------------------------------
     SECTION 3.1: REACT STATE MANAGEMENT
     ---------------------------------------------------------- */

  // Stores the source code entered by the user
  const [code, setCode] = useState(starter);

  // Stores the currently selected programming language
  const [language, setLanguage] = useState("python");

  // Stores the analysis response received from the backend
  const [result, setResult] = useState(null);

  // Tracks whether code analysis is currently in progress
  const [loading, setLoading] = useState(false);

  // Controls whether the user wants to send the report to Slack
  const [sendSlack, setSendSlack] = useState(false);

  // Controls the explanation depth: concise, detailed, or deep
  const [detailLevel, setDetailLevel] = useState("detailed");

  // Stores error messages for display in the interface
  const [error, setError] = useState("");

  // Stores the backend health-check response
  const [health, setHealth] = useState(null);


  /* ----------------------------------------------------------
     SECTION 3.2: BACKEND HEALTH CHECK
     ---------------------------------------------------------- */

  // Runs when the component initially loads.
  // Calls the backend health API to check connectivity.
  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: "offline" }));
  }, []);


  /* ----------------------------------------------------------
     SECTION 3.3: MAIN CODE ANALYSIS FUNCTION
     ---------------------------------------------------------- */

  // Executes when the user clicks the Analyze Code button.
  async function handleAnalyze() {

    // Validate that the user has entered source code
    if (!code.trim()) {
      setError("Paste a code snippet before analyzing.");
      return;
    }

    // Start the loading state and clear previous messages
    setLoading(true);
    setError("");
    setResult(null);

    try {

      // Send the source code and user preferences to the backend.
      // Store the returned AI analysis report in the result state.
      setResult(
        await analyzeCode({
          code,
          language,
          send_to_slack: sendSlack,
          detail_level: detailLevel
        })
      );

    } catch (e) {

      // Display an error if the API request fails
      setError(e.message);

    } finally {

      // Stop the loading state whether the request succeeds or fails
      setLoading(false);
    }
  }


  /* ==========================================================
     SECTION 4: USER INTERFACE (JSX)
     ========================================================== */

  return (
    <main className="app-shell">

      {/* ------------------------------------------------------
          SECTION 4.1: HEADER AND BACKEND STATUS
          ------------------------------------------------------ */}

      <header className="topbar">

        {/* Application branding */}
        <a className="brand" href="#">
          <span className="brand-mark">
            <Code2 size={21} />
          </span>

          <span>
            CodeWise
            <span className="brand-ai">AI</span>
          </span>
        </a>

        {/* Workshop label and backend connectivity indicator */}
        <div className="topbar-right">

          <span className="workshop-label">
            WORKSHOP PROJECT
          </span>

          <span
            className={`backend-status ${
              health?.status === "ok" ? "online" : ""
            }`}
          >
            <Activity size={14} />

            {health?.status === "ok"
              ? "Backend connected"
              : "Backend offline"}
          </span>

        </div>
      </header>


      {/* ------------------------------------------------------
          SECTION 4.2: HERO SECTION
          ------------------------------------------------------ */}

      <section className="hero">

        {/* Main application introduction */}
        <div className="hero-copy">

          <div className="hero-kicker">
            <Sparkles size={14} />
            YOUR AI CODE MENTOR
          </div>

          <h1>
            Understand code.
            <br />
            <span>Write it better.</span>
          </h1>

          <p>
            Turn complex snippets into clear explanations,
            actionable improvements, and verified insights
            — powered by AI.
          </p>

          {/* Highlights of application capabilities */}
          <div className="hero-points">
            <span>
              <Zap size={15} />
              Instant breakdowns
            </span>

            <span>
              <ShieldCheckIcon />
              Verified insights
            </span>
          </div>

        </div>

        {/* Decorative AI illustration */}
        <div className="hero-orb">

          <div className="orb-inner">
            <Code2 size={52} />
            <span>AI</span>
          </div>

          <i className="orb-dot dot-one" />
          <i className="orb-dot dot-two" />

        </div>

      </section>


      {/* ------------------------------------------------------
          SECTION 4.3: CODE ANALYZER WORKSPACE
          ------------------------------------------------------ */}

      <div className="workspace">

        {/* Workspace heading and AI technology label */}
        <div className="workspace-title">

          <div>
            <span className="eyebrow">
              CODE ANALYZER
            </span>

            <h2>Start with a snippet</h2>
          </div>

          <span className="powered">
            Powered by Ollama + RAG
          </span>

        </div>


        {/* ----------------------------------------------------
            SECTION 4.4: CODE EDITOR COMPONENT
            ---------------------------------------------------- */}

        {/* Passes code and language state to the reusable editor */}
        <CodeEditor
          code={code}
          setCode={setCode}
          language={language}
          setLanguage={setLanguage}
        />


        {/* ----------------------------------------------------
            SECTION 4.5: ANALYSIS OPTIONS AND USER CONTROLS
            ---------------------------------------------------- */}

        <div className="analyze-row">

          {/* Explanation depth selection */}
          <label className="detail-select">

            Explanation depth

            <select
              value={detailLevel}
              onChange={e => setDetailLevel(e.target.value)}
            >
              <option value="concise">Concise</option>
              <option value="detailed">Detailed</option>
              <option value="deep">Deep dive</option>
            </select>

          </label>


          {/* Optional Slack reporting integration */}
          <label className="slack-toggle">

            <input
              type="checkbox"
              checked={sendSlack}
              onChange={e => setSendSlack(e.target.checked)}
            />

            Send report to Slack via n8n

          </label>


          {/* --------------------------------------------------
              SECTION 4.6: ANALYZE BUTTON
              -------------------------------------------------- */}

          {/* Calls handleAnalyze when clicked.
              Displays loading feedback while processing. */}
          <button
            className="analyze-button"
            disabled={loading || !code.trim()}
            onClick={handleAnalyze}
          >

            {loading ? (
              <>
                <LoaderCircle className="spin" size={17} />
                Analyzing...
              </>
            ) : (
              <>
                <Sparkles size={17} />
                Analyze code
                <Send size={15} />
              </>
            )}

          </button>

        </div>


        {/* ----------------------------------------------------
            SECTION 4.7: ERROR HANDLING
            ---------------------------------------------------- */}

        {/* Displays an error if analysis or API communication fails */}
        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}


        {/* ----------------------------------------------------
            SECTION 4.8: ANALYSIS REPORT HEADING
            ---------------------------------------------------- */}

        <div className="result-heading">

          <div>
            <span className="eyebrow">
              AI INSIGHTS
            </span>

            <h2>Analysis report</h2>
          </div>

          {/* Displays the analyzed programming language */}
          {result && (
            <span className="language-chip">
              {result.language}
            </span>
          )}

        </div>


        {/* ----------------------------------------------------
            SECTION 4.9: ANALYSIS RESULT COMPONENT
            ---------------------------------------------------- */}

        {/* Passes the backend analysis response to the report UI */}
        <AnalysisResult result={result} />

      </div>


      {/* ------------------------------------------------------
          SECTION 4.10: APPLICATION FOOTER
          ------------------------------------------------------ */}

      <footer>

        <span>
          CodeWise AI · Built for learning and better code
        </span>

        <span>
          Prompt Engineering · Python · RAG · Agents · n8n
        </span>

      </footer>

    </main>
  );
}


/* ============================================================
   SECTION 5: SMALL REUSABLE ICON COMPONENT
   ============================================================ */

// Simple checkmark icon used in the hero section
function ShieldCheckIcon() {
  return (
    <span className="tiny-shield">
      ✓
    </span>
  );
}
