// ================================================================
//  RideShare v2 — app.js
//  FastAPI backend at localhost:8000
// ================================================================

const API = "http://localhost:8000";

// Current modal context
let modalCtx = { type: null, id: null };

// ================================================================
//  UTILITIES
// ================================================================
function toast(msg, type = "success") {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = `toast ${type} show`;
  setTimeout(() => t.classList.remove("show"), 3200);
}

function initials(name) {
  return name.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();
}

function fmtDate(dt) {
  if (!dt) return "—";
  const d = new Date(dt.replace(" ", "T"));
  return d.toLocaleDateString("en-IN", { day:"2-digit", month:"short" }) +
         " · " + d.toLocaleTimeString("en-IN", { hour:"2-digit", minute:"2-digit" });
}

function setBadge(id, count) {
  const el = document.getElementById(id);
  if (el) el.textContent = count;
}

async function checkHealth() {
  try {
    const res = await fetch(`${API}/`);
    const ok  = res.ok;
    document.querySelector(".stat-dot").className = `stat-dot ${ok ? "dot-green" : "dot-red"}`;
    document.getElementById("api-status-text").textContent = ok ? "API online" : "API offline";
  } catch {
    document.querySelector(".stat-dot").className = "stat-dot dot-red";
    document.getElementById("api-status-text").textContent = "API offline";
  }
}

// ================================================================
//  TAB SWITCHING
// ================================================================
function showTab(name) {
  document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  document.getElementById(`tab-${name}`).classList.add("active");
  document.getElementById(`nav-${name}`).classList.add("active");
  if (name === "rides")   { populateSelects(); loadRides(); }
  if (name === "drivers") loadDrivers();
  if (name === "riders")  loadRiders();
}

// ================================================================
//  RIDES
// ================================================================
async function loadRides() {
  const grid = document.getElementById("rides-grid");
  grid.innerHTML = `<div class="loading-state"><div class="spinner"></div><span>Loading rides…</span></div>`;
  try {
    const res  = await fetch(`${API}/rides`);
    const data = await res.json();
    setBadge("rides-count", data.length);
    updateRideStats(data);
    if (!data.length) {
      grid.innerHTML = `<div class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none"><path d="M5 17H3a2 2 0 01-2-2V7a2 2 0 012-2h11l5 5v5a2 2 0 01-2 2h-2" stroke="currentColor" stroke-width="1.5"/><circle cx="7.5" cy="17.5" r="2.5" stroke="currentColor" stroke-width="1.5"/><circle cx="17.5" cy="17.5" r="2.5" stroke="currentColor" stroke-width="1.5"/></svg>
        <p>No rides posted yet. Click "Post a Ride" to get started.</p></div>`;
      return;
    }
    grid.innerHTML = data.map((r, i) => rideCard(r, i)).join("");
  } catch {
    grid.innerHTML = `<div class="empty-state"><p>Could not connect to API. Is the server running?</p></div>`;
  }
}

function updateRideStats(rides) {
  const counts = { available: 0, full: 0, completed: 0, cancelled: 0 };
  rides.forEach(r => { if (counts[r.status] !== undefined) counts[r.status]++; });
  document.getElementById("stat-available").textContent  = counts.available;
  document.getElementById("stat-full").textContent       = counts.full;
  document.getElementById("stat-completed").textContent  = counts.completed;
  document.getElementById("stat-cancelled").textContent  = counts.cancelled;
}

function rideCard(r, i) {
  const delay = Math.min(i * 0.05, 0.4);
  const riderStr = r.rider_name
    ? `<div class="meta-chip"><svg width="13" height="13" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.8"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="currentColor" stroke-width="1.8"/></svg>${r.rider_name}</div>`
    : `<div class="meta-chip" style="opacity:.5"><svg width="13" height="13" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.8"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="currentColor" stroke-width="1.8"/></svg>No rider</div>`;

  // Encode ride data safely for onclick
  const safe = encodeURIComponent(JSON.stringify(r));

  return `
  <div class="ride-card" style="animation-delay:${delay}s">
    <div class="ride-card-header">
      <div class="driver-info">
        <div class="driver-avatar">${initials(r.driver_name)}</div>
        <div>
          <div class="driver-name">${r.driver_name}</div>
          <div class="driver-vehicle">${r.vehicle || "—"}</div>
        </div>
      </div>
      <span class="status-badge badge-${r.status}">${r.status}</span>
    </div>

    <div class="ride-route">
      <div class="route-point">
        <div class="route-dot dot-pickup"></div>
        <div>
          <div class="route-label">Pickup</div>
          <div class="route-text">${r.pickup_point}</div>
        </div>
      </div>
      <div class="route-line-sep" style="margin-left:4.5px"></div>
      <div class="route-point">
        <div class="route-dot dot-dropoff"></div>
        <div>
          <div class="route-label">Drop-off</div>
          <div class="route-text">${r.dropoff_point}</div>
        </div>
      </div>
    </div>

    <div class="ride-meta">
      <div class="meta-chip chip-fare">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
        ₹${r.fare_per_seat}
      </div>
      <div class="meta-chip chip-seats">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8z" stroke="currentColor" stroke-width="1.8"/></svg>
        ${r.seats_available}/${r.total_seats} seats
      </div>
      <div class="meta-chip">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8"/><path d="M12 6v6l4 2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
        ${fmtDate(r.departure_time)}
      </div>
      ${riderStr}
    </div>

    <div class="ride-actions">
      <button class="btn-edit-card" onclick="editRideModal(decodeURIComponent('${safe}'))">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="1.8"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="1.8"/></svg>
        Edit Ride
      </button>
      <button class="btn-del-card" onclick="deleteRide(${r.id})">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" stroke="currentColor" stroke-width="1.8"/></svg>
        Delete
      </button>
    </div>
  </div>`;
}

async function deleteRide(id) {
  if (!confirm("Delete this ride?")) return;
  try {
    const res = await fetch(`${API}/rides/${id}`, { method: "DELETE" });
    const d = await res.json();
    if (!res.ok) throw new Error(d.detail);
    toast("✓ Ride deleted");
    loadRides();
  } catch (e) { toast(`✗ ${e.message}`, "error"); }
}

// ================================================================
//  DRIVERS
// ================================================================
async function loadDrivers() {
  const grid = document.getElementById("drivers-grid");
  grid.innerHTML = `<div class="loading-state"><div class="spinner"></div><span>Loading…</span></div>`;
  try {
    const res  = await fetch(`${API}/drivers`);
    const data = await res.json();
    setBadge("drivers-count", data.length);
    if (!data.length) {
      grid.innerHTML = `<div class="empty-state"><p>No drivers yet. Add one!</p></div>`; return;
    }
    grid.innerHTML = data.map((d, i) => driverCard(d, i)).join("");
  } catch { grid.innerHTML = `<div class="empty-state"><p>Failed to load.</p></div>`; }
}

function driverCard(d, i) {
  const delay = Math.min(i * 0.05, 0.4);
  const safe = encodeURIComponent(JSON.stringify(d));
  return `
  <div class="person-card" style="animation-delay:${delay}s">
    <div class="person-header">
      <div class="person-avatar avatar-driver">${initials(d.name)}</div>
      <div>
        <div class="person-name">${d.name}</div>
        <div class="person-sub">${d.license_no}</div>
      </div>
    </div>
    <div class="person-details">
      <div class="detail-row">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M5 17H3a2 2 0 01-2-2V7a2 2 0 012-2h11l5 5v5a2 2 0 01-2 2h-2" stroke="currentColor" stroke-width="1.8"/><circle cx="7.5" cy="17.5" r="2.5" stroke="currentColor" stroke-width="1.8"/><circle cx="17.5" cy="17.5" r="2.5" stroke="currentColor" stroke-width="1.8"/></svg>
        ${d.vehicle}
      </div>
      <div class="detail-row">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 8.63 19.79 19.79 0 01.01 2.02 2 2 0 012 0h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.09 7.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z" stroke="currentColor" stroke-width="1.8"/></svg>
        ${d.phone}
      </div>
      <div class="detail-row">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke="currentColor" stroke-width="1.8"/><polyline points="22,6 12,13 2,6" stroke="currentColor" stroke-width="1.8"/></svg>
        ${d.email}
      </div>
    </div>
    <div class="person-actions">
      <button class="btn-edit-card" style="flex:1" onclick="editDriverModal(decodeURIComponent('${safe}'))">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="1.8"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="1.8"/></svg>
        Edit
      </button>
      <button class="btn-del-card" onclick="deletePerson('drivers', ${d.id})">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" stroke="currentColor" stroke-width="1.8"/></svg>
      </button>
    </div>
  </div>`;
}

// ================================================================
//  RIDERS
// ================================================================
async function loadRiders() {
  const grid = document.getElementById("riders-grid");
  grid.innerHTML = `<div class="loading-state"><div class="spinner"></div><span>Loading…</span></div>`;
  try {
    const res  = await fetch(`${API}/riders`);
    const data = await res.json();
    setBadge("riders-count", data.length);
    if (!data.length) {
      grid.innerHTML = `<div class="empty-state"><p>No riders yet. Add one!</p></div>`; return;
    }
    grid.innerHTML = data.map((r, i) => riderCard(r, i)).join("");
  } catch { grid.innerHTML = `<div class="empty-state"><p>Failed to load.</p></div>`; }
}

function riderCard(r, i) {
  const delay = Math.min(i * 0.05, 0.4);
  const safe = encodeURIComponent(JSON.stringify(r));
  return `
  <div class="person-card" style="animation-delay:${delay}s">
    <div class="person-header">
      <div class="person-avatar avatar-rider">${initials(r.name)}</div>
      <div>
        <div class="person-name">${r.name}</div>
        <div class="person-sub">Rider</div>
      </div>
    </div>
    <div class="person-details">
      <div class="detail-row">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 8.63 19.79 19.79 0 01.01 2.02 2 2 0 012 0h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.09 7.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z" stroke="currentColor" stroke-width="1.8"/></svg>
        ${r.phone}
      </div>
      <div class="detail-row">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke="currentColor" stroke-width="1.8"/><polyline points="22,6 12,13 2,6" stroke="currentColor" stroke-width="1.8"/></svg>
        ${r.email}
      </div>
    </div>
    <div class="person-actions">
      <button class="btn-edit-card" style="flex:1" onclick="editRiderModal(decodeURIComponent('${safe}'))">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="1.8"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="1.8"/></svg>
        Edit
      </button>
      <button class="btn-del-card" onclick="deletePerson('riders', ${r.id})">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" stroke="currentColor" stroke-width="1.8"/></svg>
      </button>
    </div>
  </div>`;
}

async function deletePerson(type, id) {
  if (!confirm(`Delete this ${type === 'drivers' ? 'driver' : 'rider'}?`)) return;
  try {
    const res = await fetch(`${API}/${type}/${id}`, { method: "DELETE" });
    const d = await res.json();
    if (!res.ok) throw new Error(d.detail);
    toast(`✓ ${type === 'drivers' ? 'Driver' : 'Rider'} deleted`);
    type === 'drivers' ? loadDrivers() : loadRiders();
  } catch (e) { toast(`✗ ${e.message}`, "error"); }
}

// ================================================================
//  MODAL SYSTEM
// ================================================================
let driversList = [];
let ridersList  = [];

async function populateSelects() {
  const [dr, ri] = await Promise.all([
    fetch(`${API}/drivers`).then(r => r.json()).catch(() => []),
    fetch(`${API}/riders`).then(r => r.json()).catch(() => []),
  ]);
  driversList = dr; ridersList = ri;
}

function openModal(type) {
  modalCtx = { type, id: null };
  const titles = { ride: "Post a Ride", driver: "Add Driver", rider: "Add Rider" };
  document.getElementById("modal-title").textContent = titles[type];
  document.getElementById("modal-sub").textContent   = "Fill in the details below";
  document.getElementById("modal-submit").textContent = type === "ride" ? "Post Ride" : `Add ${type.charAt(0).toUpperCase()+type.slice(1)}`;
  document.getElementById("modal-msg").className = "msg-box";
  document.getElementById("modal-body").innerHTML = formHTML(type);
  document.getElementById("modal-overlay").classList.add("open");
  document.body.style.overflow = "hidden";
}

function closeModal() {
  document.getElementById("modal-overlay").classList.remove("open");
  document.body.style.overflow = "";
  modalCtx = { type: null, id: null };
}

function formHTML(type, data = {}) {
  if (type === "ride") {
    const drOpts = driversList.map(d => `<option value="${d.id}" ${data.driver_id == d.id ? "selected" : ""}>${d.name} — ${d.vehicle}</option>`).join("");
    const riOpts = `<option value="">None</option>` + ridersList.map(r => `<option value="${r.id}" ${data.rider_id == r.id ? "selected" : ""}>${r.name}</option>`).join("");
    const dt = data.departure_time ? data.departure_time.replace(" ", "T").slice(0,16) : "";
    return `
      <div class="section-label">Route</div>
      <div class="field"><label>Pickup Point</label><input type="text" id="f-pickup" placeholder="Koramangala, Bangalore" value="${data.pickup_point||""}" required/></div>
      <div class="field"><label>Drop-off Point</label><input type="text" id="f-dropoff" placeholder="Electronic City, Bangalore" value="${data.dropoff_point||""}" required/></div>
      <div class="section-label" style="margin-top:8px">Schedule & Pricing</div>
      <div class="field-row">
        <div class="field"><label>Departure Time</label><input type="datetime-local" id="f-time" value="${dt}" required/></div>
        <div class="field"><label>Fare per Seat (₹)</label><input type="number" id="f-fare" placeholder="80" value="${data.fare_per_seat||""}" min="0" step="0.5" required/></div>
      </div>
      <div class="field-row">
        <div class="field"><label>Total Seats</label><input type="number" id="f-total" min="1" max="8" value="${data.total_seats||3}" required/></div>
        <div class="field"><label>Seats Available</label><input type="number" id="f-avail" min="0" max="8" value="${data.seats_available||3}" required/></div>
      </div>
      <div class="section-label" style="margin-top:8px">People & Status</div>
      <div class="field-row">
        <div class="field"><label>Driver</label><select id="f-driver" required><option value="">Select driver…</option>${drOpts}</select></div>
        <div class="field"><label>Rider (optional)</label><select id="f-rider">${riOpts}</select></div>
      </div>
      <div class="field"><label>Status</label>
        <select id="f-status">
          <option value="available" ${(data.status||"available")==="available"?"selected":""}>🟢 Available</option>
          <option value="full"      ${data.status==="full"?"selected":""}>🟡 Full</option>
          <option value="completed" ${data.status==="completed"?"selected":""}>🔵 Completed</option>
          <option value="cancelled" ${data.status==="cancelled"?"selected":""}>🔴 Cancelled</option>
        </select>
      </div>`;
  }
  if (type === "driver") return `
      <div class="field"><label>Full Name</label><input type="text" id="f-name" placeholder="Arjun Mehta" value="${data.name||""}" required/></div>
      <div class="field-row">
        <div class="field"><label>Phone</label><input type="tel" id="f-phone" placeholder="9876543210" value="${data.phone||""}" required/></div>
        <div class="field"><label>Email</label><input type="email" id="f-email" placeholder="arjun@mail.com" value="${data.email||""}" required/></div>
      </div>
      <div class="field"><label>Vehicle</label><input type="text" id="f-vehicle" placeholder="Honda City - Silver" value="${data.vehicle||""}" required/></div>
      <div class="field"><label>License Number</label><input type="text" id="f-license" placeholder="KA01AB1234" value="${data.license_no||""}" required/></div>`;
  if (type === "rider") return `
      <div class="field"><label>Full Name</label><input type="text" id="f-name" placeholder="Divya Nair" value="${data.name||""}" required/></div>
      <div class="field-row">
        <div class="field"><label>Phone</label><input type="tel" id="f-phone" placeholder="9871234560" value="${data.phone||""}" required/></div>
        <div class="field"><label>Email</label><input type="email" id="f-email" placeholder="divya@mail.com" value="${data.email||""}" required/></div>
      </div>`;
}

// Pre-fill modal for editing
function editRideModal(raw) {
  const r = JSON.parse(raw);
  modalCtx = { type: "ride", id: r.id };
  document.getElementById("modal-title").textContent  = "Update Ride";
  document.getElementById("modal-sub").textContent    = `Editing ride #${r.id}`;
  document.getElementById("modal-submit").textContent = "Update Ride";
  document.getElementById("modal-msg").className = "msg-box";
  document.getElementById("modal-body").innerHTML = formHTML("ride", r);
  document.getElementById("modal-overlay").classList.add("open");
  document.body.style.overflow = "hidden";
}
function editDriverModal(raw) {
  const d = JSON.parse(raw);
  modalCtx = { type: "driver", id: d.id };
  document.getElementById("modal-title").textContent  = "Update Driver";
  document.getElementById("modal-sub").textContent    = `Editing ${d.name}`;
  document.getElementById("modal-submit").textContent = "Update Driver";
  document.getElementById("modal-msg").className = "msg-box";
  document.getElementById("modal-body").innerHTML = formHTML("driver", d);
  document.getElementById("modal-overlay").classList.add("open");
  document.body.style.overflow = "hidden";
}
function editRiderModal(raw) {
  const r = JSON.parse(raw);
  modalCtx = { type: "rider", id: r.id };
  document.getElementById("modal-title").textContent  = "Update Rider";
  document.getElementById("modal-sub").textContent    = `Editing ${r.name}`;
  document.getElementById("modal-submit").textContent = "Update Rider";
  document.getElementById("modal-msg").className = "msg-box";
  document.getElementById("modal-body").innerHTML = formHTML("rider", r);
  document.getElementById("modal-overlay").classList.add("open");
  document.body.style.overflow = "hidden";
}

// ================================================================
//  MODAL SUBMIT — routes to correct CRUD
// ================================================================
async function handleModalSubmit() {
  const { type, id } = modalCtx;
  const msgEl = document.getElementById("modal-msg");
  msgEl.className = "msg-box";

  let payload = {}; let url; let method;

  if (type === "ride") {
    const riderVal = document.getElementById("f-rider")?.value;
    payload = {
      driver_id:       parseInt(document.getElementById("f-driver").value),
      rider_id:        riderVal ? parseInt(riderVal) : null,
      pickup_point:    document.getElementById("f-pickup").value,
      dropoff_point:   document.getElementById("f-dropoff").value,
      departure_time:  document.getElementById("f-time").value,
      total_seats:     parseInt(document.getElementById("f-total").value),
      seats_available: parseInt(document.getElementById("f-avail").value),
      fare_per_seat:   parseFloat(document.getElementById("f-fare").value),
      status:          document.getElementById("f-status").value,
    };
    url    = id ? `${API}/rides/${id}` : `${API}/rides`;
    method = id ? "PUT" : "POST";
  } else if (type === "driver") {
    payload = {
      name:       document.getElementById("f-name").value,
      phone:      document.getElementById("f-phone").value,
      email:      document.getElementById("f-email").value,
      vehicle:    document.getElementById("f-vehicle").value,
      license_no: document.getElementById("f-license").value,
    };
    url    = id ? `${API}/drivers/${id}` : `${API}/drivers`;
    method = id ? "PUT" : "POST";
  } else if (type === "rider") {
    payload = {
      name:  document.getElementById("f-name").value,
      phone: document.getElementById("f-phone").value,
      email: document.getElementById("f-email").value,
    };
    url    = id ? `${API}/riders/${id}` : `${API}/riders`;
    method = id ? "PUT" : "POST";
  }

  try {
    const res  = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error");
    const label = id ? "updated" : "created";
    toast(`✓ ${type.charAt(0).toUpperCase()+type.slice(1)} ${label}!`);
    closeModal();
    if (type === "ride")   { populateSelects(); loadRides(); }
    if (type === "driver") { loadDrivers(); populateSelects(); }
    if (type === "rider")  { loadRiders();  populateSelects(); }
  } catch (err) {
    msgEl.textContent = `✗ ${err.message}`;
    msgEl.className = "msg-box error";
  }
}

// ================================================================
//  INIT
// ================================================================
window.addEventListener("DOMContentLoaded", async () => {
  checkHealth();
  await populateSelects();
  loadRides();
});
