import React,{useState,useEffect,Suspense,lazy} from "react";
import {Routes,Route,Navigate,Link,useLocation} from "react-router-dom";
import {LayoutDashboard,Search,FileCheck2,Network,GitCompare,Archive,ShieldCheck,FileText,History,BarChart3,Settings,Menu,Plus,Database,LogOut,ChevronDown,Workflow,BriefcaseBusiness,Users,ClipboardCheck} from "lucide-react";
import Landing from "./pages/Landing"; import Login from "./pages/Login";
import {ScrollProgress,AmbientField} from "./components/chrome";
import {useScrollState,useSmoothScroll,initPointerGlow} from "./lib/motion";
import {currentUser,logout} from "./services/api";

/* Fixed-height skeleton shown while a route chunk downloads. Sized to match
   the page header so the swap does not shift layout. */
function RouteFallback(){
  return <div className="route-loading" role="status" aria-live="polite">
    <span className="sr-only">Loading view…</span>
    <div className="sk sk-title"/><div className="sk sk-line"/>
    <div className="sk-grid"><div className="sk sk-card"/><div className="sk sk-card"/><div className="sk sk-card"/><div className="sk sk-card"/></div>
  </div>;
}

/* Landing and Login stay in the initial chunk because they are the entry
   points. Everything else is split so the heavy graph/chart vendors never
   block first paint. */
const Dashboard=lazy(()=>import("./pages/Dashboard"));
const NewAnalysis=lazy(()=>import("./pages/NewAnalysis"));
const Processing=lazy(()=>import("./pages/Processing"));
const Results=lazy(()=>import("./pages/Results"));
const Standards=lazy(()=>import("./pages/Standards"));
const StandardDetails=lazy(()=>import("./pages/StandardDetails"));
const KnowledgeGraph=lazy(()=>import("./pages/KnowledgeGraph"));
const TenderLinter=lazy(()=>import("./pages/TenderLinter"));
const Compare=lazy(()=>import("./pages/Compare"));
const SpecificationDiff=lazy(()=>import("./pages/SpecificationDiff"));
const Basket=lazy(()=>import("./pages/Basket"));
const Compliance=lazy(()=>import("./pages/Compliance"));
const Reports=lazy(()=>import("./pages/Reports"));
const HistoryPage=lazy(()=>import("./pages/History"));
const Evaluation=lazy(()=>import("./pages/Evaluation"));
const Evidence=lazy(()=>import("./pages/Evidence"));
const Scenarios=lazy(()=>import("./pages/Scenarios"));
const Procurement=lazy(()=>import("./pages/Procurement"));

const COMMON=[
  ["/dashboard","Dashboard",LayoutDashboard],
  ["/procurement","Procurement Hub",Workflow],
];
const ROLE_NAV={
  ORGANIZATION_ADMIN:[...COMMON,["/analysis/new","New Analysis",Plus],["/tender-linter","Tender Linter",FileCheck2],["/standards","Standards",Search],["/compliance","Compliance",ShieldCheck],["/reports","Reports",FileText],["/history","History",History]],
  PROCUREMENT_OFFICER:[...COMMON,["/analysis/new","New Analysis",Plus],["/tender-linter","Tender Linter",FileCheck2],["/standards","Standards",Search],["/evidence","Evidence Center",Database],["/compliance","Compliance",ShieldCheck],["/evaluation","Evaluation",BarChart3],["/reports","Reports",FileText],["/history","History",History]],
  GOVERNMENT_REVIEWER:[...COMMON,["/evidence","Evidence Center",Database],["/standards","Standards",Search],["/evaluation","Evaluation",BarChart3],["/reports","Reports",FileText],["/history","History",History]],
  STANDARDS_OFFICER:[...COMMON,["/standards","Standards Library",Search],["/evidence","Evidence Center",Database],["/graph","Knowledge Graph",Network],["/compare","Compare",GitCompare],["/basket","Standards Basket",Archive],["/reports","Reports",FileText]],
  COMPLIANCE_OFFICER:[...COMMON,["/standards","Standards",Search],["/evidence","Evidence Center",Database],["/tender-linter","Tender Linter",FileCheck2],["/compliance","Compliance",ShieldCheck],["/reports","Reports",FileText],["/history","History",History]],
  VENDOR:[...COMMON,["/reports","My Reports",FileText]],
  AUDITOR:[...COMMON,["/evidence","Evidence Center",Database],["/reports","Reports",FileText],["/history","History",History]],
  ADMIN:[...COMMON,["/analysis/new","New Analysis",Plus],["/standards","Standards",Search],["/evidence","Evidence Center",Database],["/graph","Knowledge Graph",Network],["/compare","Compare",GitCompare],["/basket","Standards Basket",Archive],["/compliance","Compliance",ShieldCheck],["/evaluation","Evaluation",BarChart3],["/reports","Reports",FileText],["/history","History",History],["/scenarios","Demo Scenarios",Database]],
};

function Protected({children}){return localStorage.getItem("normex_token")?<>{children}</>:<Navigate to="/login" replace/>}
function Shell({children}){
  const [open,setOpen]=useState(true),[mobileOpen,setMobileOpen]=useState(false),[menu,setMenu]=useState(false),loc=useLocation(),user=currentUser();
  const nav=ROLE_NAV[user?.role]||COMMON;
  const {scrolled}=useScrollState();

  // Close the mobile drawer and dismiss the user menu whenever the route changes.
  useEffect(()=>{setMobileOpen(false);setMenu(false)},[loc.pathname]);

  // Escape closes the drawer / menu.
  useEffect(()=>{
    const onKey=(e)=>{if(e.key!=="Escape")return;setMobileOpen(false);setMenu(false)};
    window.addEventListener("keydown",onKey);
    return()=>window.removeEventListener("keydown",onKey);
  },[]);

  return <div className="app"><AmbientField variant="app"/>
    <ScrollProgress/>
    <aside className={`${open?"sidebar":"sidebar collapsed"} ${mobileOpen?"mobile-open":""}`}>
      <div className="brand"><div className="brandmark">N</div>{open&&<div><b>NORMEX</b><small>Procurement Intelligence</small></div>}</div>
      <nav>{nav.map(([to,label,Icon])=><Link key={to} className={loc.pathname===to?"nav active":"nav"} to={to} title={open?undefined:label}><Icon size={18}/>{open&&label}</Link>)}</nav>
      <div className="side-bottom"><Link className="nav" to="/settings" title={open?undefined:"Settings"}><Settings size={18}/>{open&&"Settings"}</Link></div>
    </aside>
    {mobileOpen&&<button className="drawer-backdrop" aria-label="Close menu" onClick={()=>setMobileOpen(false)}/>}
    <main className="main">
      <header className={scrolled?"is-scrolled":""}>
        <button className="iconbtn mobile-menu-btn" aria-label="Open navigation menu" aria-expanded={mobileOpen} onClick={()=>setMobileOpen(!mobileOpen)}><Menu size={20}/></button>
        <button className="iconbtn desktop-menu-btn" aria-label={open?"Collapse sidebar":"Expand sidebar"} aria-expanded={open} onClick={()=>setOpen(!open)}><Menu size={20}/></button>
        <div className="crumb"><span className="live-dot"/> {user?.role?.replaceAll("_"," ")||"Secure official workspace"} <span>•</span> Synthetic knowledge base</div>
        <div className="user-area">
          <button className="user-btn" aria-haspopup="menu" aria-expanded={menu} onClick={()=>setMenu(!menu)}>
            <span className="avatar">{user?.name?.[0]||user?.full_name?.[0]||"O"}</span>
            <span className="user-text"><b>{user?.name||user?.full_name||"Official"}</b><small>{user?.role?.replaceAll("_"," ")}</small></span>
            <ChevronDown size={15}/>
          </button>
          {menu&&<div className="user-menu" role="menu"><div className="menu-meta">{user?.organization}</div><button role="menuitem" onClick={logout}><LogOut size={15}/> Sign out</button></div>}
        </div>
      </header>
      {children}
    </main>
  </div>
}

export default function App(){
  useSmoothScroll();
  useEffect(()=>{initPointerGlow()},[]);
  return <Routes>
    <Route path="/" element={<Landing/>}/>
    <Route path="/login" element={<Login/>}/>
    <Route path="*" element={<Protected><Shell><Suspense fallback={<RouteFallback/>}><Routes>
      <Route path="/dashboard" element={<Dashboard/>}/>
      <Route path="/procurement" element={<Procurement/>}/>
      <Route path="/analysis/new" element={<NewAnalysis/>}/>
      <Route path="/analysis/processing" element={<Processing/>}/>
      <Route path="/analysis/results" element={<Results/>}/>
      <Route path="/standards" element={<Standards/>}/>
      <Route path="/standards/:id" element={<StandardDetails/>}/>
      <Route path="/evidence" element={<Evidence/>}/>
      <Route path="/graph" element={<KnowledgeGraph/>}/>
      <Route path="/tender-linter" element={<TenderLinter/>}/>
      <Route path="/compare" element={<Compare/>}/>
      <Route path="/specification-diff" element={<SpecificationDiff/>}/>
      <Route path="/basket" element={<Basket/>}/>
      <Route path="/compliance" element={<Compliance/>}/>
      <Route path="/reports" element={<Reports/>}/>
      <Route path="/history" element={<HistoryPage/>}/>
      <Route path="/scenarios" element={<Scenarios/>}/>
      <Route path="/evaluation" element={<Evaluation/>}/>
      <Route path="/settings" element={<Dashboard/>}/>
      <Route path="*" element={<Navigate to="/dashboard"/>}/>
    </Routes></Suspense></Shell></Protected>}/>
  </Routes>
}
