
import React,{useState} from "react";
import {useNavigate} from "react-router-dom";
import {ShieldCheck,LockKeyhole,ArrowRight,Database} from "lucide-react";
import {login} from "../services/api";
export default function Login(){
 const nav=useNavigate(),[email,setEmail]=useState("procurement.officer@normex.gov.in"),[password,setPassword]=useState("Normex@2026"),[error,setError]=useState(""),[loading,setLoading]=useState(false);
 async function submit(e){e.preventDefault();setLoading(true);setError("");try{await login(email,password);nav("/dashboard")}catch(err){setError(err.response?.data?.detail||"Unable to authenticate")}finally{setLoading(false)}}
 return <div className="auth-page"><div className="auth-visual"><div className="auth-logo"><div className="brandmark">N</div><b>NORMEX</b></div><div><div className="eyebrow">OFFICIAL ACCESS</div><h1>Evidence-led procurement intelligence.</h1><p>Secure workspace for procurement, standards and compliance officials.</p><div className="auth-pills"><span><ShieldCheck size={15}/> Role-based access</span><span><Database size={15}/> Synthetic demo knowledge base</span></div></div><small>Prototype environment · All knowledge records shown in demo mode are synthetic.</small></div>
 <form className="auth-card" onSubmit={submit}><div className="auth-card-head"><div className="auth-icon"><LockKeyhole size={22}/></div><div><h2>Official sign in</h2><p>Use an authorized NORMEX demo account.</p></div></div><label>Official email<input value={email} onChange={e=>setEmail(e.target.value)} type="email" required/></label><label>Password<input value={password} onChange={e=>setPassword(e.target.value)} type="password" required/></label>{error&&<div className="auth-error">{error}</div>}<button className="primary wide" disabled={loading}>{loading?"Authenticating…":<>Continue to NORMEX <ArrowRight size={16}/></>}</button><div className="demo-credentials"><b>Demo access</b><span>procurement.officer@normex.gov.in</span><span>Password: Normex@2026</span></div></form></div>
}
