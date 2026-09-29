import axios from "axios";
export const api=axios.create({baseURL:import.meta.env.VITE_API_BASE_URL||"http://localhost:8000/api/v1"||""});
api.interceptors.request.use(config=>{const token=localStorage.getItem("normex_token");if(token)config.headers.Authorization=`Bearer ${token}`;return config});
api.interceptors.response.use(r=>r,err=>{if(err.response?.status===401&&location.pathname!=="/login"){localStorage.removeItem("normex_token");localStorage.removeItem("normex_user");location.href="/login"}return Promise.reject(err)});
export async function login(email,password){const r=(await api.post("/auth/login",{email,password})).data;localStorage.setItem("normex_token",r.access_token);localStorage.setItem("normex_user",JSON.stringify(r.user));return r.user}
export function logout(){localStorage.removeItem("normex_token");localStorage.removeItem("normex_user");location.href="/"}
export function currentUser(){try{return JSON.parse(localStorage.getItem("normex_user")||"null")}catch{return null}}
export async function analyze(text,language){return (await api.post("/analysis",{text,language})).data}
export async function tenderAnalyze(text){return (await api.post("/tender/analyze",{text})).data}
export async function standards(q=""){return (await api.get("/standards/search",{params:{q}})).data}
export async function standard(id){return (await api.get(`/standards/${id}`)).data}
export async function history(){return (await api.get("/analysis")).data}
export async function graph(id){return (await api.get(`/graph/standard/${id}`)).data}
export async function addBasket(id){return (await api.post("/standards-basket",{standard_id:id})).data}
export async function demoOverview(){return (await api.get("/demo/overview")).data}
export async function evidence(){return (await api.get("/demo/evidence")).data}
export async function scenarios(){return (await api.get("/demo/scenarios")).data}
export async function procurementOverview(){return (await api.get("/procurement/overview")).data}
export async function createTender(payload){return (await api.post("/procurement/tenders",payload)).data}
export async function complianceReview(id,payload){return (await api.post(`/procurement/tenders/${id}/compliance-review`,payload)).data}
export async function publishTender(id){return (await api.post(`/procurement/tenders/${id}/publish`)).data}
export async function submitBid(id,payload){return (await api.post(`/procurement/tenders/${id}/submit`,payload)).data}
export async function closeBidding(id){return (await api.post(`/procurement/tenders/${id}/close-bidding`)).data}
export async function evaluateSubmission(id,payload){return (await api.post(`/procurement/submissions/${id}/evaluate`,payload)).data}
export async function awardTender(tenderId,submissionId){return (await api.post(`/procurement/tenders/${tenderId}/award/${submissionId}`)).data}
export async function procurementAudit(){return (await api.get("/procurement/audit")).data}
