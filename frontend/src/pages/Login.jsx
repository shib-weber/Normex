import React,{useState} from "react";
import {useNavigate} from "react-router-dom";
import {ShieldCheck,LockKeyhole,ArrowRight,Database} from "lucide-react";
import {login} from "../services/api";
import {AmbientField,Reveal} from "../components/chrome";

export default function Login(){
  const nav=useNavigate(),[email,setEmail]=useState("procurement.officer@normex.gov.in"),[password,setPassword]=useState("Normex@2026"),[error,setError]=useState(""),[loading,setLoading]=useState(false);
  async function submit(e){e.preventDefault();setLoading(true);setError("");try{await login(email,password);nav("/dashboard")}catch(err){setError(err.response?.data?.detail||"Unable to authenticate")}finally{setLoading(false)}}
  return <div className="auth-page"><AmbientField variant="auth" showCanvas={false}/>
    <Reveal className="auth-visual" delay={40}>
      <div className="auth-logo"><div className="brandmark">N</div><b>NORMEX</b></div>
      <div>
        <div className="eyebrow">Official access</div>
        <h1>Evidence-led procurement intelligence.</h1>
        <p>Secure workspace for procurement, standards and compliance officials.</p>
        <div className="auth-pills">
          <span><ShieldCheck size={15}/> Role-based access</span>
          <span><Database size={15}/> Synthetic demo knowledge base</span>
        </div>
      </div>
      <small>Prototype environment · All knowledge records shown in demo mode are synthetic.</small>
    </Reveal>

    <Reveal className="auth-card-host" delay={160}>
      <form className="auth-card" onSubmit={submit}>
        <div className="auth-card-head">
          <div className="auth-icon"><LockKeyhole size={22}/></div>
          <div><h2>Official sign in</h2><p>Use an authorized NORMEX demo account.</p></div>
        </div>
        <label htmlFor="email">Official email</label>
        <input id="email" name="email" value={email} onChange={e=>setEmail(e.target.value)} type="email" required autoComplete="username"/>
        <label htmlFor="password">Password</label>
        <input id="password" name="password" value={password} onChange={e=>setPassword(e.target.value)} type="password" required autoComplete="current-password"/>
        {error&&<div className="auth-error" role="alert">{error}</div>}
        <button className="primary wide" disabled={loading}>{loading?"Authenticating…":<>Continue to NORMEX <ArrowRight size={16}/></>}</button>
        <div className="demo-credentials"><b>Demo access</b><span>procurement.officer@normex.gov.in</span><span>Password: Normex@2026</span></div>
      </form>
    </Reveal>
  </div>
}
