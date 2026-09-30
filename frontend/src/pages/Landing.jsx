import React from "react"; import {Link} from "react-router-dom"; import {ArrowRight,Network,ShieldCheck,GitBranch,SearchCheck,FileWarning,Languages} from "lucide-react";
import BackgroundVideo from "../components/BackgroundVideo";
import {AmbientField,ScrollProgress,Reveal,RevealGroup} from "../components/chrome";
import {useTilt,useScrollState} from "../lib/motion";
const features=[["Hybrid retrieval","Keyword + semantic retrieval + metadata filtering + graph expansion.",SearchCheck],["Standards graph","Trace normative, test, safety, installation and allied relationships.",Network],["Version intelligence","Surface potential outdated references without silently replacing them.",GitBranch],["Tender Linter","Detect ambiguity, missing tests, gaps, conflicts and version alerts.",FileWarning],["Compliance evidence","Keep certification claims evidence-backed and reviewable.",ShieldCheck],["Multilingual search","English, Hindi and Bengali procurement input.",Languages]];
const pipeline=["Understand input","Extract requirements","Retrieve BIS standards","Expand graph","Check versions","Assess coverage","Explain & generate"];
export default function Landing(){
  const panelRef=useTilt({max:7,scale:1.02});
  const {scrolled}=useScrollState();
  return <div className="landing"><AmbientField variant="hero"/><ScrollProgress/>
  <nav className={"landnav"+(scrolled?" is-scrolled":"")}><div className="brand"><div className="brandmark">N</div><b>NORMEX</b></div><div><Link to="/dashboard" className="secondary">Open platform</Link></div></nav>

  <section className="hero">
    <BackgroundVideo src="/normex-bg.mp4" poster="/normex-poster.jpg">
      <div className="hero-video-scrim"/>
      <div className="hero-video-tint"/>
    </BackgroundVideo>

    <Reveal className="hero-copy">
      <div className="eyebrow">Indian Standards &amp; Procurement Intelligence</div>
      <h1>Turn procurement requirements into <em>traceable standards intelligence.</em></h1>
      <p>NORMEX analyzes technical requirements, discovers relevant standards and connected evidence, checks versions and procurement gaps, and produces an auditable recommendation trail.</p>
      <div className="hero-actions">
        <Link to="/analysis/new" className="primary">Start an analysis <ArrowRight size={18}/></Link>
        <Link to="/tender-linter" className="secondary">Run Tender Linter</Link>
      </div>
    </Reveal>

    <Reveal delay={140} className="tilt-wrap">
      <div ref={panelRef} className="hero-panel tilt">
        <span className="tilt-glare"/>
        <div className="panel-top"><span>LIVE PROTOTYPE</span><span>TRACEABLE</span></div>
        <div className="pipeline">{pipeline.map((x,i)=><div key={x}><span>{String(i+1).padStart(2,"0")}</span>{x}</div>)}</div>
      </div>
    </Reveal>
  </section>

  <section className="section">
    <Reveal className="section-title">
      <div className="eyebrow">Why NORMEX</div>
      <h2>Built as procurement intelligence, not a chatbot.</h2>
    </Reveal>
    <RevealGroup className="feature-grid" stagger={80}>
      {features.map(([t,d,I])=><div className="feature" key={t}><I size={22}/><h3>{t}</h3><p>{d}</p></div>)}
    </RevealGroup>
  </section>

  <footer>NORMEX is a prototype decision-support system. Verify recommendations against authoritative standards, notifications and applicable regulations.</footer>
  </div>
}
