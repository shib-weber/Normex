import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Page, Card } from "../components";
import { analyze, api } from "../services/api";

const demo = "We need outdoor LED street lights for municipal roads. The luminaire should have approximately 90W power, IP66 protection, minimum 90 lm/W efficacy, surge protection and suitable outdoor environmental performance.";

export default function NewAnalysis() {
  const [text, setText] = useState(demo);
  const [lang, setLang] = useState("en");
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();

  async function go() {
    setLoading(true);
    try {
      const r = await analyze(text, lang);
      sessionStorage.setItem("normex_result", JSON.stringify(r));
      nav("/analysis/results");
    } finally {
      setLoading(false);
    }
  }

  async function upload(e) {
    const f = e.target.files?.[0];
    if (!f) return;
    const fd = new FormData();
    fd.append("file", f);
    setLoading(true);
    try {
      const r = (await api.post("/documents/upload", fd)).data;
      sessionStorage.setItem("normex_result", JSON.stringify({ ...r.analysis, document: r.filename }));
      nav("/analysis/results");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Page eyebrow="ANALYSIS" title="New procurement analysis" description="Paste a requirement or upload a tender/specification.">
      <div 
        className="analysis-grid" 
        style={{ 
          display: "grid", 
          gridTemplateColumns: "minmax(0, 2fr) minmax(0, 1fr)", 
          gap: "24px", 
          alignItems: "start",
          marginTop: "24px"
        }}
      >
        {/* Left Side: Input Form */}
        <Card style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "20px" }}>
          <div className="row between" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "16px", width: "100%" }}>
            <h2 style={{ margin: 0, fontSize: "1.25rem", fontWeight: "600" }}>Procurement input</h2>
            <select 
              value={lang} 
              onChange={e => setLang(e.target.value)}
              style={{
                padding: "6px 12px",
                borderRadius: "6px",
                border: "1px solid #d1d5db",
                backgroundColor: "#fff",
                fontSize: "0.875rem",
                cursor: "pointer",
                outline: "none"
              }}
            >
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="bn">Bengali</option>
            </select>
          </div>

          <textarea 
            value={text} 
            onChange={e => setText(e.target.value)} 
            placeholder="Describe the procurement requirement..." 
            style={{
              width: "100%",
              minHeight: "180px",
              padding: "12px",
              borderRadius: "8px",
              border: "1px solid #d1d5db",
              fontSize: "0.95rem",
              lineHeight: "1.5",
              resize: "vertical",
              outline: "none",
              fontFamily: "inherit",
              boxSizing: "border-box"
            }}
          />

          <div 
            className="upload" 
            style={{ 
              border: "2px dashed #e5e7eb", 
              borderRadius: "8px", 
              padding: "20px", 
              textAlign: "center",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "8px",
              backgroundColor: "#f9fafb"
            }}
          >
            <input 
              id="file" 
              type="file" 
              accept=".pdf,.docx,.txt" 
              onChange={upload}
              style={{ display: "none" }}
            />
            <label 
              htmlFor="file"
              style={{
                padding: "8px 16px",
                backgroundColor: "#fff",
                border: "1px solid #d1d5db",
                borderRadius: "6px",
                fontWeight: "500",
                fontSize: "0.875rem",
                cursor: "pointer",
                boxShadow: "0 1px 2px rgba(0,0,0,0.05)"
              }}
            >
              Upload PDF / DOCX / TXT
            </label>
            <span style={{ fontSize: "0.75rem", color: "#6b7280", marginTop: "4px" }}>
              Text extraction is performed locally by the prototype backend.
            </span>
          </div>

          <button 
            className="primary wide" 
            disabled={loading || text.length < 5} 
            onClick={go}
            style={{
              width: "100%",
              padding: "12px",
              backgroundColor: loading || text.length < 5 ? "#9ca3af" : "#6366f1",
              color: "#fff",
              border: "none",
              borderRadius: "8px",
              fontWeight: "600",
              fontSize: "0.95rem",
              cursor: loading || text.length < 5 ? "not-allowed" : "pointer"
            }}
          >
            {loading ? "Analyzing…" : "Analyze procurement requirement"}
          </button>
        </Card>

        {/* Right Side: Cleaned & Restructured Checklist */}
        <Card style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "20px" }}>
          <h2 style={{ margin: 0, fontSize: "1.15rem", fontWeight: "600", color: "#111827", letterSpacing: "-0.01em" }}>
            What NORMEX checks
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            {[
              "Technical Entities",
              "Structured Requirements",
              "Standards Retrieval",
              "Knowledge Graphs",
              "Revision Signals",
              "Certification Evidence",
              "Coverage & Gaps",
              "Risk Categories"
            ].map(x => (
              <div 
                className="checkitem" 
                key={x}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  fontSize: "0.9rem",
                  color: "#4b5563",
                  borderBottom: "1px solid #f3f4f6",
                  paddingBottom: "8px"
                }}
              >
                <span style={{ color: "#4f46e5", fontWeight: "bold", fontSize: "0.95rem" }}>✓</span>
                <span style={{ fontWeight: "500", whiteSpace: "nowrap" }}>{x}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </Page>
  );
}
