import React from "react";
import {Link} from "react-router-dom";
export function Page({eyebrow,title,description,actions,children}){return <section className="page"><div className="pagehead"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div><div className="actions">{actions}</div></div>{children}</section>}
export function Card({children,className=""}){return <div className={"card "+className}>{children}</div>}
export function Stat({label,value,sub}){return <Card className="stat"><span>{label}</span><strong>{value}</strong>{sub&&<small>{sub}</small>}</Card>}
export function Badge({children,tone=""}){return <span className={"badge "+tone}>{children}</span>}
export function StandardCard({item,onAdd}){return <Card className="standard"><div className="row between"><div><Badge>{item.category||"STANDARD"}</Badge><h3>{item.standard_number}</h3><p className="title">{item.title}</p></div><strong className="relevance">{item.relevance}%</strong></div><p>{item.scope}</p><div className="row between"><span className="muted">{item.source_type}</span><Link className="textlink" to={`/standards/${item.id}`}>View details →</Link></div>{onAdd&&<button className="secondary" onClick={()=>onAdd(item.id)}>Add to basket</button>}</Card>}
