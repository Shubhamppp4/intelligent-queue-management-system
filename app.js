const API_BASE = "http://127.0.0.1:8000";

const $ = id => document.getElementById(id);
let currentCustomer = null;
let currentQueue = null;

function generateCustomerId(){
  $("uniqueId").value = "CUST-" + Math.floor(100000 + Math.random()*900000);
}
function generateToken(){
  $("token").value = "T" + Math.floor(1000 + Math.random()*9000);
}
$("generateId").onclick = generateCustomerId;
$("generateToken").onclick = generateToken;

$("tokenForm").addEventListener("submit", async e => {
  e.preventDefault();
  $("error").textContent = "";
  const payload = {
    name: $("name").value.trim(),
    unique_id: $("uniqueId").value.trim(),
    service: $("service").value,
    token: $("token").value.trim()
  };
  try{
    const res = await fetch(`${API_BASE}/customers`, {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(payload)
    });
    const data = await res.json();
    if(!res.ok) throw new Error(data.detail || "Unable to create customer");
    currentCustomer = data;

    const queuePayload = {
      customer_id: data.id,
      staff_id: null,
      counter_number: null,
      token: data.token,
      service: data.service
    };
    const qres = await fetch(`${API_BASE}/queue`,{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(queuePayload)
    });
    const qdata = await qres.json();
    if(!qres.ok) throw new Error(qdata.detail || "Customer created but queue entry failed");
    currentQueue = qdata;
    showTicket();
  }catch(err){
    $("error").textContent = "Failed to connect: " + err.message;
  }
});

function showTicket(){
  $("homeScreen").classList.add("hidden");
  $("ticketScreen").classList.remove("hidden");
  $("ticketToken").textContent = currentCustomer.token;
  $("ticketName").textContent = currentCustomer.name;
  $("ticketId").textContent = currentCustomer.unique_id;
  $("ticketService").textContent = currentCustomer.service;
  updateTicket(currentQueue);
}

function updateTicket(q){
  if(!q) return;
  $("position").textContent = q.queue_position ?? "—";
  $("wait").textContent = q.waiting_time ?? 0;
  $("statusBadge").textContent = q.status;
  const messages = {
    WAITING:"Please wait. Your turn will be called soon.",
    CALLED:"Your token has been called. Please proceed to the counter.",
    SERVING:"Your service is currently in progress.",
    COMPLETED:"Your service has been completed.",
    HOLD:"Your token is on hold.",
    SKIPPED:"Your token was skipped."
  };
  $("statusText").textContent = messages[q.status] || "Queue status updated.";
}

async function refreshStatus(){
  $("ticketError").textContent = "";
  if(!currentQueue) return;
  try{
    const res = await fetch(`${API_BASE}/queue/${currentQueue.id}`);
    const data = await res.json();
    if(!res.ok) throw new Error(data.detail || "Could not refresh");
    currentQueue = data;
    updateTicket(data);
  }catch(err){
    $("ticketError").textContent = "Refresh failed: " + err.message;
  }
}
$("refresh").onclick = refreshStatus;
setInterval(() => { if(currentQueue) refreshStatus(); }, 10000);

$("newToken").onclick = () => {
  currentCustomer = null; currentQueue = null;
  $("ticketScreen").classList.add("hidden");
  $("homeScreen").classList.remove("hidden");
  $("tokenForm").reset();
  generateCustomerId();
  generateToken();
};

generateCustomerId();
generateToken();
