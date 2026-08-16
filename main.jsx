import React,{useEffect,useState}from"react";
import{createRoot}from"react-dom/client";
import{Users,Ticket,Clock,CheckCircle,Play,Pause,SkipForward,Bell,Settings,User,LogOut,LayoutDashboard,ShieldCheck}from"lucide-react";
import"./style.css";

const API="http://127.0.0.1:8000";

async function api(path,options={}){
  const res=await fetch(API+path,options);
  const data=await res.json().catch(()=>({}));
  if(!res.ok)throw new Error(data.detail||`Request failed (${res.status})`);
  return data;
}

function Login({ok}){
  let[id,setId]=useState(""),[pw,setPw]=useState(""),[error,setError]=useState(""),[loading,setLoading]=useState(false);
  async function login(){
    setError("");
    if(!id.trim()||!pw.trim()){setError("Enter Staff ID and password");return}
    setLoading(true);
    try{
      const staff=await api("/staff");
      const found=staff.find(x=>String(x.staff_id).toLowerCase()===id.trim().toLowerCase()||String(x.id)===id.trim());
      if(!found)throw new Error("Staff not found");
      ok(found);
    }catch(e){setError(e.message)}
    finally{setLoading(false)}
  }
  return <div className="login"><div className="loginbox"><div className="logo"><ShieldCheck/></div><h1>Staff Portal</h1><p>Login to manage your assigned queue.</p><input placeholder="Staff ID" value={id} onChange={e=>setId(e.target.value)}/><input type="password" placeholder="Password" value={pw} onChange={e=>setPw(e.target.value)}/><button className="primary" onClick={login} disabled={loading}>{loading?"Connecting...":"Login"}</button>{error&&<small className="error">{error}</small>}<small>Hackathon mode: password is not validated by the current backend.</small></div></div>
}

function App(){
  let[staff,setStaff]=useState(null),[page,setPage]=useState("dashboard"),[list,setList]=useState([]),[current,setCurrent]=useState(null),[active,setActive]=useState(false),[dark,setDark]=useState(false),[note,setNote]=useState(true),[loading,setLoading]=useState(false),[error,setError]=useState("");

  async function loadData(s=staff){
    if(!s)return;
    try{
      const [queue,staffData]=await Promise.all([api("/queue"),api("/staff/"+s.id)]);
      setList(queue);
      setStaff(staffData);
      setActive(Boolean(staffData.active));
      const mine=queue.find(x=>x.staff_id===staffData.id&&(x.status==="CALLED"||x.status==="SERVING"));
      setCurrent(mine||null);
      setError("");
    }catch(e){setError(e.message)}
  }

  async function login(s){
    setStaff(s);
    setActive(Boolean(s.active));
    await loadData(s);
  }

  useEffect(()=>{if(!staff)return;loadData();const t=setInterval(()=>loadData(),5000);return()=>clearInterval(t)},[staff?.id]);

  async function toggleActive(){
    try{
      const next=!active;
      const updated=await api(`/staff/${staff.id}/status?active=${next}`,{method:"PATCH"});
      setStaff(updated);setActive(updated.active);
    }catch(e){setError(e.message)}
  }

  async function next(){
    if(!active)return alert("Activate counter first");
    if(current)return alert("Complete current customer first");
    setLoading(true);setError("");
    try{
      const counter=staff.assigned_counter||1;
      const q=await api(`/queue/call-next/${staff.id}/${counter}`,{method:"POST"});
      setCurrent(q);await loadData({...staff});
    }catch(e){setError(e.message)}
    finally{setLoading(false)}
  }

  async function action(name){
    if(!current)return;
    setLoading(true);setError("");
    try{
      const q=await api(`/queue/${current.id}/${name}`,{method:"POST"});
      if(q.status==="CALLED"||q.status==="SERVING")setCurrent(q);else setCurrent(null);
      await loadData();
    }catch(e){setError(e.message)}
    finally{setLoading(false)}
  }

  if(!staff)return <Login ok={login}/>;
  const waiting=list.filter(x=>x.status==="WAITING");
  const served=staff.served_today??0;
  const counter=staff.assigned_counter??1;
  const service=current?.service||waiting[0]?.service||"General Service";

  return <div className={dark?"app dark":"app"}>
    <aside>
      <div className="brand"><div className="logo"><ShieldCheck/></div><b>SQMS<small>Staff Portal</small></b></div>
      <div className="staff"><b>{staff.name}</b><small>{staff.staff_id} · Counter {counter}</small></div>
      {[["dashboard","Dashboard",LayoutDashboard],["customers","Customer List",Users],["serve","Serve Customer",Ticket],["notifications","Notifications",Bell],["profile","Staff Profile",User],["settings","Settings",Settings]].map(([p,t,I])=><button key={p} className={page===p?"nav on":"nav"} onClick={()=>setPage(p)}><I size={18}/>{t}</button>)}
      <button className="logout" onClick={()=>setStaff(null)}><LogOut/> Logout</button>
    </aside>
    <main>
      <header><div><small>Staff Portal / {page}</small><h1>{page==="dashboard"?"Staff Dashboard":page}</h1><p>Counter {counter} · {service}</p></div><button className={active?"active":"inactive"} onClick={toggleActive}>● {active?"Active":"Not Active"}</button></header>
      {error&&<div className="card error">{error}</div>}
      {page==="dashboard"&&<Dashboard waiting={waiting.length}served={served}current={current}next={next}start={()=>action("start")}done={()=>action("complete")}hold={()=>action("hold")}skip={()=>action("skip")}list={list}loading={loading}/>}
      {page==="customers"&&<CustomerList list={list}/>}
      {page==="serve"&&<section className="page"><h2>Serve Customer</h2><Serve current={current}next={next}start={()=>action("start")}done={()=>action("complete")}hold={()=>action("hold")}skip={()=>action("skip")}loading={loading}/></section>}
      {page==="notifications"&&<section className="page"><h2>Notifications</h2><Card t="Live Queue" d={`${waiting.length} customer(s) currently waiting.`}/><Card t="System" d="Staff queue is connected to the FastAPI backend."/><Card t="Counter" d={`You are assigned to Counter ${counter}.`}/></section>}
      {page==="profile"&&<section className="page"><h2>Staff Profile</h2><Card t={staff.name} d={`Staff ID: ${staff.staff_id} · Database ID: ${staff.id} · Assigned Counter: ${counter} · Served Today: ${served}`}/></section>}
      {page==="settings"&&<section className="page"><h2>Settings</h2><div className="card row"><span>Dark Theme</span><button onClick={()=>setDark(x=>!x)}>{dark?"ON":"OFF"}</button></div><div className="card row"><span>Notifications</span><button onClick={()=>setNote(x=>!x)}>{note?"ON":"OFF"}</button></div><div className="card row"><span>Refresh</span><button onClick={()=>loadData()}>Refresh</button></div><div className="card row"><span>Logout</span><button onClick={()=>setStaff(null)}>Logout</button></div></section>}
    </main>
  </div>
}

function Dashboard({waiting,served,current,next,start,done,hold,skip,list,loading}){
  return <section className="page"><h2>Good morning 👋</h2><div className="kpis"><K label="Waiting Customers" v={waiting} I={Users}/><K label="Current Token" v={current?.token||"—"} I={Ticket}/><K label="Served Today" v={served} I={CheckCircle}/><K label="Queue Status" v={waiting>5?"Busy":"Normal"} I={Clock}/></div><div className="grid"><div className="card"><h3>Current Customer</h3>{current?<Serve current={current} next={next} start={start} done={done} hold={hold} skip={skip} loading={loading}/>:<div className="empty">No customer at your counter<button className="primary" onClick={next} disabled={loading}>{loading?"Calling...":"Call Next"}</button></div>}</div><div className="card"><h3>Next in Queue</h3>{list.filter(x=>x.status==="WAITING").slice(0,5).map(x=><div className="q" key={x.id}><b>{x.queue_position??"—"}</b><strong>{x.token}</strong><span>{x.waiting_time} min</span></div>)}{waiting.length===0&&<div className="empty">Queue is empty</div>}<button className="primary full" onClick={next} disabled={loading}>Call Next Customer</button></div></div></section>
}

function Serve({current,next,start,done,hold,skip,loading}){
  if(!current)return <div className="empty">Ready for next customer<button className="primary" onClick={next} disabled={loading}>{loading?"Calling...":"Call Next"}</button></div>;
  return <div className="serve"><small>TOKEN</small><strong>{current.token}</strong><span className={"status "+current.status}>{current.status}</span><p>{current.service}</p><div className="actions">{current.status==="CALLED"&&<button className="primary" onClick={start} disabled={loading}><Play/> Start Service</button>}{current.status==="SERVING"&&<button className="success" onClick={done} disabled={loading}><CheckCircle/> Complete</button>}<button className="warn" onClick={hold} disabled={loading}><Pause/> Hold</button><button className="danger" onClick={skip} disabled={loading}><SkipForward/> Skip</button></div></div>
}

function CustomerList({list}){return <section className="page"><h2>Customer List</h2><div className="card table"><table><thead><tr><th>Token</th><th>Service</th><th>Status</th><th>Waiting</th><th>Position</th></tr></thead><tbody>{list.map(x=><tr key={x.id}><td>{x.token}</td><td>{x.service}</td><td><span className={"status "+x.status}>{x.status}</span></td><td>{x.waiting_time} min</td><td>{x.queue_position||"—"}</td></tr>)}</tbody></table></div></section>}

function K({label,v,I}){return <div className="card kpi"><I/><strong>{v}</strong><small>{label}</small></div>}
function Card({t,d}){return <div className="card notice"><b>{t}</b><p>{d}</p></div>}

createRoot(document.getElementById("root")).render(<App/>);
