import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Page, Card } from "../components";
import { analyze, api } from "../services/api";
import { Check, Sparkles } from "lucide-react";

const demo = "We need outdoor LED street lights for municipal roads. The luminaire should have approximately 90W power, IP66 protection, minimum 90 lm/W efficacy, surge protection and suitable outdoor environmental performance.";

const CHECKS = [
  "Technical Entities",
  "Structured Requirements",
  "Standards Retrieval",
  "Knowledge Graphs",
  "Revision Signals",
  "Certification Evidence",
  "Coverage & Gaps",
  "Risk Categories",
];

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
      <div className="analysis-grid analysis-grid--split">
        {/* Left Side: Input Form */}
        <Card className="stack-lg">
          <div className="card-title-row">
            <h2 className="mb-0">Procurement input</h2>
            <label className="sr-only" htmlFor="lang">Input language</label>
            <select
              id="lang"
              className="lang-select"
              value={lang}
              onChange={e => setLang(e.target.value)}
            >
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="bn">Bengali</option>
            </select>
          </div>

          <label className="sr-only" htmlFor="req">Procurement requirement</label>
          <textarea
            id="req"
            className="analysis-textarea"
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="Describe the procurement requirement..."
          />

          <div className="upload">
            <input
              id="file"
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={upload}
            />
            <label htmlFor="file">Upload PDF / DOCX / TXT</label>
            <span>Text extraction is performed locally by the prototype backend.</span>
          </div>

          <button
            className="primary wide"
            disabled={loading || text.length < 5}
            onClick={go}
          >
            <Sparkles size={15} />
            {loading ? "Analyzing…" : "Analyze procurement requirement"}
          </button>
        </Card>

        {/* Right Side: Cleaned & Restructured Checklist */}
        <Card className="stack-lg">
          <h2 className="mb-0">What NORMEX checks</h2>
          <div className="checklist">
            {CHECKS.map(x => (
              <div className="checkitem checkitem--tick" key={x}>
                <span><Check size={12} /></span>
                <b>{x}</b>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </Page>
  );
}
