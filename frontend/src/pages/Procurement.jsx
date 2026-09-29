import React,{useEffect,useMemo,useState} from "react";
import {Page,Card,Badge} from "../components";
import {procurementOverview,createTender,complianceReview,publishTender,submitBid,closeBidding,evaluateSubmission,awardTender,currentUser,procurementAudit} from "../services/api";
import {Workflow,Plus,Send,ClipboardCheck,Building2,ShieldCheck,History,ChevronRight,LockKeyhole,SearchCheck,Flag,CheckCircle2} from "lucide-react";

const ROLE_COPY={
 ORGANIZATION_ADMIN:"Own your organisation's procurement pipeline, review approved tenders and publish them to the supplier marketplace.",
 PROCUREMENT_OFFICER:"Create tenders, inspect NORMEX analysis, coordinate compliance review, close bidding and evaluate suppliers.",
 GOVERNMENT_REVIEWER:"Review supplier submissions, inspect procurement evidence and participate in technical/compliance evaluation.",
 STANDARDS_OFFICER:"Validate standards references and identify standards-related issues before a tender reaches publication.",
 COMPLIANCE_OFFICER:"Control the publication gate. Approve compliant tenders or return them to the author for correction.",
 VENDOR:"Discover published opportunities, read requirements and submit one bid per organisation.",
 AUDITOR:"Inspect the end-to-end synthetic audit trail across tender creation, review, publication, bidding and award.",
 ADMIN:"Platform-wide procurement visibility and administration."
};

const canCreate=r=>["ORGANIZATION_ADMIN","PROCUREMENT_OFFICER"].includes(r);
const canEvaluate=r=>["PROCUREMENT_OFFICER","GOVERNMENT_REVIEWER"].includes(r);
const canReview=r=>r==="COMPLIANCE_OFFICER";
const canPublish=r=>["ORGANIZATION_ADMIN","PROCUREMENT_OFFICER","COMPLIANCE_OFFICER"].includes(r);

function statusTone(status){
 if(["PUBLISHED","AWARDED","READY_TO_PUBLISH"].includes(status)) return "good";
 if(["DRAFT","COMPLIANCE_REVIEW","EVALUATION"].includes(status)) return "warn";
 return "";
}

export default function Procurement(){
 const user=currentUser();
 const [data,setData]=useState(null),[error,setError]=useState(""),[busy,setBusy]=useState(false),[bid,setBid]=useState({}),[review,setReview]=useState({});
 const [form,setForm]=useState({title:"",description:"",category:"Lighting",budget:"",deadline:""});

 async function load(){try{setError("");setData(await procurementOverview())}catch(e){setError(e.response?.data?.detail||"Unable to load procurement workspace")}}
 useEffect(()=>{load()},[]);

 async function run(action,successReset=false){setBusy(true);setError("");try{await action();if(successReset)setForm({title:"",description:"",category:"Lighting",budget:"",deadline:""});await load()}catch(e){setError(e.response?.data?.detail||"Action could not be completed")}finally{setBusy(false)}}
 async function create(){await run(()=>createTender({...form,budget:Number(form.budget)}),true)}
 async function reviewTender(id,decision){await run(()=>complianceReview(id,{decision,notes:review[id]||""}));setReview({...review,[id]:""})}
 async function publish(id){await run(()=>publishTender(id))}
 async function close(id){await run(()=>closeBidding(id))}
 async function bidSubmit(id){const amount=Number(bid[id]||0);if(!amount){setError("Enter a bid amount before submitting");return}await run(()=>submitBid(id,{bid_amount:amount,proposal:{delivery:"14 weeks",warranty:"5 years",commercial_note:"Synthetic vendor proposal"}}));setBid({...bid,[id]:""})}
 async function evaluate(s){await run(()=>evaluateSubmission(s.id,{technical_score:88,compliance_score:90,commercial_score:84,notes:"Synthetic panel review: evidence and commercial response checked.",decision:"SHORTLISTED"}))}
 async function award(tenderId,submissionId){await run(()=>awardTender(tenderId,submissionId))}

 const counts=data?.counts||{};
 const visibleTenders=useMemo(()=>data?.tenders||[],[data]);
 return <Page eyebrow="END-TO-END PROCUREMENT" title="Procurement Hub" description={ROLE_COPY[user?.role]||"Controlled procurement workflow with standards intelligence, compliance gates and auditability."}>
   <div className="workflow-strip">{(data?.workflow||[]).map((x,i)=><div key={x}><span>{String(i+1).padStart(2,"0")}</span>{x}{i<data.workflow.length-1&&<ChevronRight size={13}/>}</div>)}</div>
   <div className="statgrid" style={{marginTop:18}}>
    <MiniStat label="Drafts" value={counts.draft||0}/><MiniStat label="In review" value={counts.review||0}/><MiniStat label="Published" value={counts.published||0}/><MiniStat label="Bids" value={counts.bids||0}/>
   </div>
   {error&&<div className="auth-error" style={{marginTop:18}}>{error}</div>}

   {canCreate(user?.role)&&<div className="two-col" style={{marginTop:18}}>
    <Card><div className="row between"><div><Badge tone="good">AUTHORING</Badge><h2>Create a new tender</h2><p className="muted-text">The organisation creates the requirement. NORMEX analyses it immediately and places it into the controlled review workflow.</p></div><Building2 size={24}/></div>
      <div className="formgrid">
       <label>Tender title<input value={form.title} onChange={e=>setForm({...form,title:e.target.value})} placeholder="Municipal LED street-light modernisation"/></label>
       <label>Category<select value={form.category} onChange={e=>setForm({...form,category:e.target.value})}><option>Lighting</option><option>Solar</option><option>IT</option><option>Construction</option><option>Medical</option><option>Water</option></select></label>
       <label>Budget (INR)<input type="number" min="1" value={form.budget} onChange={e=>setForm({...form,budget:e.target.value})} placeholder="8500000"/></label>
       <label>Bid deadline<input type="date" value={form.deadline} onChange={e=>setForm({...form,deadline:e.target.value})}/></label>
      </div>
      <textarea value={form.description} onChange={e=>setForm({...form,description:e.target.value})} placeholder="Describe measurable specifications, quantities, testing, installation, acceptance criteria, warranty and required certifications..."/>
      <button className="primary wide" disabled={busy||form.title.trim().length<5||form.description.trim().length<20||!form.budget||!form.deadline} onClick={create}><Plus size={15}/>{busy?"Creating and analysing…":"Create + analyse tender"}</button>
      <small className="muted-text">After creation: DRAFT → NORMEX analysis → compliance review → approved → publish.</small>
    </Card>
    <Card><h2>Who acts next?</h2><Gate n="01" title="Organisation / Procurement Officer" text="Creates the tender and checks NORMEX's extracted requirements."/><Gate n="02" title="Compliance Officer" text="Approves or returns the tender before publication."/><Gate n="03" title="Vendor / Supplier" text="Sees only PUBLISHED tenders and submits a bid."/><Gate n="04" title="Government / Procurement" text="Closes bidding, evaluates submissions and awards the tender."/></Card>
   </div>}

   <div className="section-mini" style={{marginTop:30}}><div><div className="eyebrow">LIVE PROCUREMENT CASES</div><h2 style={{margin:0}}>{user?.role==="VENDOR"?"Open tenders":"Tender pipeline"}</h2></div><Badge>{visibleTenders.length} cases</Badge></div>
   {!visibleTenders.length&&<Card style={{marginTop:14}}><div className="empty">No cases are available for this role yet.</div></Card>}
   <div className="tender-grid">
    {visibleTenders.map(t=><TenderCard key={t.id} t={t} user={user} bid={bid} setBid={setBid} review={review} setReview={setReview} busy={busy} onReview={reviewTender} onPublish={publish} onClose={close} onBid={bidSubmit} onEvaluate={evaluate} onAward={award} canReview={canReview(user?.role)} canPublish={canPublish(user?.role)} canEvaluate={canEvaluate(user?.role)}/>) }
   </div>
   {(user?.role==="AUDITOR"||user?.role==="ADMIN")&&<Audit/>}
 </Page>
}

function TenderCard({t,user,bid,setBid,review,setReview,busy,onReview,onPublish,onClose,onBid,onEvaluate,onAward,canReview,canPublish,canEvaluate}){
 return <Card className="tender-card">
   <div className="row between"><Badge tone={statusTone(t.status)}>{t.status.replaceAll("_"," ")}</Badge><span className="evidence-code">{t.tender_number}</span></div>
   <h2>{t.title}</h2><p>{t.description}</p>
   <div className="tender-meta"><span>🏢 {t.organization}</span><span>₹{Number(t.budget).toLocaleString("en-IN")}</span><span>Deadline {t.deadline}</span><span>{t.submission_count} bids</span></div>
   <div className="tender-analysis"><b><SearchCheck size={14}/> NORMEX analysis</b><span>{t.analysis?.coverage?.ratio??0}% requirement coverage</span><span>{(t.compliance_status||"PENDING").replaceAll("_"," ")}</span></div>

   {canReview&&["DRAFT","COMPLIANCE_REVIEW"].includes(t.status)&&<div className="action-box"><div className="action-title"><ShieldCheck size={15}/> Compliance gate</div><textarea value={review[t.id]||""} onChange={e=>setReview({...review,[t.id]:e.target.value})} placeholder="Review notes / evidence comments"/><div className="row"><button className="primary" disabled={busy} onClick={()=>onReview(t.id,"APPROVE")}><CheckCircle2 size={14}/> Approve</button><button className="secondary" disabled={busy} onClick={()=>onReview(t.id,"RETURN")}>Return for correction</button></div></div>}

   {canPublish&&t.status==="READY_TO_PUBLISH"&&<button className="primary wide" disabled={busy} onClick={()=>onPublish(t.id)}><Flag size={14}/> Publish tender</button>}

   {user?.role==="VENDOR"&&t.status==="PUBLISHED"&&<div className="bidbox"><input type="number" min="1" placeholder="Bid amount (INR)" value={bid[t.id]||""} onChange={e=>setBid({...bid,[t.id]:e.target.value})}/><button className="primary" disabled={busy} onClick={()=>onBid(t.id)}><Send size={14}/> Submit bid</button></div>}

   {(["ORGANIZATION_ADMIN","PROCUREMENT_OFFICER"].includes(user?.role))&&t.status==="PUBLISHED"&&<button className="secondary wide" disabled={busy} onClick={()=>onClose(t.id)}><LockKeyhole size={14}/> Close bidding & start evaluation</button>}

   {canEvaluate&&t.submissions?.length>0&&<div className="submission-list"><h3><ClipboardCheck size={15}/> Supplier evaluation</h3>{t.submissions.map(s=><div className="submission" key={s.id}><div><b>{s.vendor}</b><small>₹{Number(s.bid_amount).toLocaleString("en-IN")} · {s.status} · final {Number(s.final_score||0).toFixed(2)}</small></div><div className="row">{s.status==="SUBMITTED"&&<button className="secondary" disabled={busy} onClick={()=>onEvaluate(s)}>Evaluate</button>}{["SHORTLISTED","RECOMMENDED"].includes(s.status)&&t.status==="EVALUATION"&&<button className="primary" disabled={busy} onClick={()=>onAward(t.id,s.id)}>Award</button>}</div></div>)}</div>}
 </Card>
}

function MiniStat({label,value}){return <Card className="stat"><span>{label}</span><strong>{value}</strong></Card>}
function Gate({n,title,text}){return <div className="checkitem"><span>{n}</span><div><b>{title}</b><small>{text}</small></div></div>}
function Audit(){const [rows,setRows]=useState([]);useEffect(()=>{procurementAudit().then(setRows).catch(()=>{})},[]);return <Card style={{marginTop:18}}><div className="row between"><h2><History size={17}/> Audit trail</h2><Badge>{rows.length} events</Badge></div>{rows.slice(0,15).map(r=><div className="listrow" key={r.id}><div><b>{r.action.replaceAll("_"," ")}</b><small>{r.entity_type} #{r.entity_id} · {new Date(r.created_at).toLocaleString()}</small></div><span className="evidence-code">{JSON.stringify(r.details)}</span></div>)}</Card>}
