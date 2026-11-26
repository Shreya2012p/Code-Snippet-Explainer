import { Code2, Trash2 } from "lucide-react";

export default function CodeEditor({ code, setCode, language, setLanguage }) {
  return <section className="panel editor-panel">
    <div className="panel-heading">
      <div><span className="eyebrow">INPUT</span><h2><Code2 size={18}/> Your code</h2></div>
      <div className="editor-actions">
        <select value={language} onChange={e => setLanguage(e.target.value)}>
          {["python","javascript","typescript","java","c","cpp","csharp","go","sql"].map(x =>
            <option key={x} value={x}>{x}</option>)}
        </select>
        <button className="icon-button" title="Clear code" onClick={() => setCode("")}><Trash2 size={16}/></button>
      </div>
    </div>
    <textarea className="code-input" spellCheck="false" value={code}
      onChange={e => setCode(e.target.value)} placeholder="Paste your code snippet here..." />
    <div className="editor-footer"><span>{code.split("\n").length} lines</span><span>{code.length} characters</span></div>
  </section>;
}
