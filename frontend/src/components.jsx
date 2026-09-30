import React from "react";
import {Link} from "react-router-dom";
import {useReveal} from "./lib/motion";
import {CountUp} from "./components/chrome";

/**
 * Standard page frame.
 * The heading block reveals on mount; `children` are untouched so callers keep
 * full control of their own layout and data.
 */
export function Page({eyebrow,title,description,actions,children}){
  const head=useReveal();
  return <section className="page">
    <div className="pagehead" ref={head}>
      <div>
        {eyebrow&&<div className="eyebrow">{eyebrow}</div>}
        <h1>{title}</h1>
        {description&&<p>{description}</p>}
      </div>
      {actions&&<div className="actions">{actions}</div>}
    </div>
    {children}
  </section>
}

/**
 * Glass surface. `className`, `style` and any other props are forwarded, so
 * callers can compose variants (`.stat`, `.tender-card`, …) unchanged.
 */
export function Card({children,className="",...rest}){
  return <div className={"card pointer-glow "+className} {...rest}>{children}</div>;
}

export function Stat({label,value,sub}){
  return <Card className="stat"><span>{label}</span><strong><CountUp value={value}/></strong>{sub&&<small>{sub}</small>}</Card>;
}

export function Badge({children,tone=""}){
  return <span className={"badge "+tone}>{children}</span>;
}

export function StandardCard({item,onAdd}){
  return <Card className="standard">
    <div className="row between">
      <div>
        <Badge>{item.category||"STANDARD"}</Badge>
        <h3>{item.standard_number}</h3>
        <p className="title">{item.title}</p>
      </div>
      <strong className="relevance">{item.relevance}%</strong>
    </div>
    <p>{item.scope}</p>
    <div className="row between">
      <span className="muted">{item.source_type}</span>
      <Link className="textlink" to={`/standards/${item.id}`}>View details →</Link>
    </div>
    {onAdd&&<button className="secondary" onClick={()=>onAdd(item.id)}>Add to basket</button>}
  </Card>
}
