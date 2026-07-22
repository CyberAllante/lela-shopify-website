/**
 * Inventory Manager (admin.html) — edits a working copy of window.INVENTORY
 * entirely in the browser, autosaves to localStorage, and exports a fresh
 * data/inventory.js. No server, no accounts: the downloaded file IS the
 * database. Photos dropped here are resized to ~900px JPEG and embedded.
 */
(function () {
  "use strict";

  var LS_KEY = "msl-inventory-draft";
  var $ = function (s) { return document.querySelector(s); };

  // Working copy: prefer an unsaved draft from a previous session.
  var data = JSON.parse(JSON.stringify(window.INVENTORY || { vehicles: [], dealership: {} }));
  try {
    var draft = localStorage.getItem(LS_KEY);
    if (draft) {
      var parsed = JSON.parse(draft);
      if (parsed && parsed.vehicles) {
        data = parsed;
        setState("Restored unsaved draft from this browser — download to make it permanent.");
      }
    }
  } catch (e) { /* corrupted draft — ignore */ }

  var editingId = null;   // null = adding new
  var photos = [];        // working photo list for the open editor

  function setState(msg) {
    var el = $("#save-state");
    if (el) el.textContent = msg;
  }

  function persist() {
    try { localStorage.setItem(LS_KEY, JSON.stringify(data)); } catch (e) {
      setState("Draft too large for browser autosave — download inventory.js now to keep your work.");
    }
  }

  function money(n) { return "$" + Number(n || 0).toLocaleString("en-US"); }

  function title(v) {
    return v.year + " " + v.make + " " + v.model + (v.trim ? " " + v.trim : "");
  }

  /* ---------- list ---------- */

  function renderList() {
    var list = $("#list");
    $("#count").textContent = data.vehicles.length;
    if (!data.vehicles.length) {
      list.innerHTML = '<div class="empty-state"><strong>No cars yet.</strong>Click "+ Add a Car" to start.</div>';
      return;
    }
    list.innerHTML = data.vehicles.map(function (v) {
      var img = (v.images && v.images[0]) || "assets/placeholder-sedan.svg";
      return (
        '<div class="admin-row">' +
          '<img src="' + img + '" alt="" onerror="this.onerror=null;this.src=\'assets/placeholder-sedan.svg\'">' +
          '<div class="meta"><strong>' + title(v) + (v.sold ? '<span class="badge-sold">SOLD</span>' : "") + "</strong>" +
          "<span>" + money(v.price) + " · " + Number(v.mileage || 0).toLocaleString() + " mi · " + (v.stock ? "Stock " + v.stock : "no stock #") + "</span></div>" +
          '<div class="ops">' +
            '<button class="op' + (v.featured ? " on" : "") + '" data-op="feature" data-id="' + v.id + '">★ Featured</button>' +
            '<button class="op' + (v.sold ? " on" : "") + '" data-op="sold" data-id="' + v.id + '">Sold</button>' +
            '<button class="op" data-op="edit" data-id="' + v.id + '">Edit</button>' +
            '<button class="op warn" data-op="delete" data-id="' + v.id + '">Delete</button>' +
          "</div>" +
        "</div>"
      );
    }).join("");
  }

  $("#list").addEventListener("click", function (e) {
    var btn = e.target.closest("button[data-op]");
    if (!btn) return;
    var v = data.vehicles.filter(function (x) { return x.id === btn.getAttribute("data-id"); })[0];
    if (!v) return;
    var op = btn.getAttribute("data-op");
    if (op === "feature") { v.featured = !v.featured; }
    if (op === "sold") { v.sold = !v.sold; }
    if (op === "delete") {
      if (!confirm("Delete the " + title(v) + "? This can't be undone after you download.")) return;
      data.vehicles = data.vehicles.filter(function (x) { return x.id !== v.id; });
      if (editingId === v.id) closeEditor();
    }
    if (op === "edit") { openEditor(v); return; }
    persist(); renderList();
    setState("Change saved to draft — download inventory.js when you're done.");
  });

  /* ---------- editor ---------- */

  var form = $("#car-form");

  function openEditor(v) {
    editingId = v ? v.id : null;
    $("#editor").hidden = false;
    $("#editor-title").textContent = v ? "Edit: " + title(v) : "Add a Car";
    form.reset();
    photos = v && v.images ? v.images.slice() : [];
    if (v) {
      ["year","make","model","trim","price","mileage","bodyStyle","drivetrain","transmission",
       "engine","exteriorColor","interiorColor","mpgCity","mpgHwy","vin","stock","description"]
        .forEach(function (k) { if (form[k]) form[k].value = v[k] != null ? v[k] : ""; });
      form.features.value = (v.features || []).join(", ");
      form.featured.checked = !!v.featured;
      form.sold.checked = !!v.sold;
    }
    renderPhotos();
    $("#editor").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function closeEditor() {
    editingId = null;
    $("#editor").hidden = true;
  }

  $("#btn-new").addEventListener("click", function () { openEditor(null); });
  $("#btn-cancel").addEventListener("click", closeEditor);

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var slug = (form.year.value + "-" + form.make.value + "-" + form.model.value + "-" + (form.stock.value || Date.now()))
      .toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
    var v = editingId
      ? data.vehicles.filter(function (x) { return x.id === editingId; })[0]
      : { id: slug };
    if (!editingId) data.vehicles.unshift(v);

    v.year = Number(form.year.value);
    v.make = form.make.value.trim();
    v.model = form.model.value.trim();
    v.trim = form.trim.value.trim();
    v.price = Number(String(form.price.value).replace(/[^0-9]/g, "")) || 0;
    v.mileage = Number(String(form.mileage.value).replace(/[^0-9]/g, "")) || 0;
    v.bodyStyle = form.bodyStyle.value;
    v.drivetrain = form.drivetrain.value;
    v.transmission = form.transmission.value;
    v.engine = form.engine.value.trim();
    v.exteriorColor = form.exteriorColor.value.trim();
    v.interiorColor = form.interiorColor.value.trim();
    v.mpgCity = Number(form.mpgCity.value) || 0;
    v.mpgHwy = Number(form.mpgHwy.value) || 0;
    v.vin = form.vin.value.trim().toUpperCase();
    v.stock = form.stock.value.trim();
    v.fuel = v.fuel || "Gasoline";
    v.description = form.description.value.trim();
    v.features = form.features.value.split(",").map(function (s) { return s.trim(); }).filter(Boolean);
    v.images = photos.slice();
    v.featured = form.featured.checked;
    v.sold = form.sold.checked;

    persist(); renderList(); closeEditor();
    setState("Saved to draft — download inventory.js to publish.");
  });

  /* ---------- photos ---------- */

  function renderPhotos() {
    $("#photo-thumbs").innerHTML = photos.map(function (src, i) {
      return '<div class="pt"><img src="' + src + '" alt=""><button type="button" data-i="' + i + '">×</button></div>';
    }).join("");
  }

  $("#photo-thumbs").addEventListener("click", function (e) {
    if (e.target.tagName !== "BUTTON") return;
    photos.splice(Number(e.target.getAttribute("data-i")), 1);
    renderPhotos();
  });

  var zone = $("#drop-zone");
  var fileInput = $("#file-input");
  zone.addEventListener("click", function () { fileInput.click(); });
  fileInput.addEventListener("change", function () { addFiles(fileInput.files); fileInput.value = ""; });
  ["dragenter", "dragover"].forEach(function (ev) {
    zone.addEventListener(ev, function (e) { e.preventDefault(); zone.classList.add("hot"); });
  });
  ["dragleave", "drop"].forEach(function (ev) {
    zone.addEventListener(ev, function (e) { e.preventDefault(); zone.classList.remove("hot"); });
  });
  zone.addEventListener("drop", function (e) { addFiles(e.dataTransfer.files); });

  function addFiles(files) {
    Array.prototype.forEach.call(files, function (file) {
      if (!/^image\//.test(file.type)) return;
      var img = new Image();
      img.onload = function () {
        // Resize to max 900px wide, JPEG — keeps the data file manageable.
        var scale = Math.min(1, 900 / img.width);
        var c = document.createElement("canvas");
        c.width = Math.round(img.width * scale);
        c.height = Math.round(img.height * scale);
        c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
        photos.push(c.toDataURL("image/jpeg", 0.78));
        renderPhotos();
        URL.revokeObjectURL(img.src);
      };
      img.src = URL.createObjectURL(file);
    });
  }

  /* ---------- export ---------- */

  $("#btn-download").addEventListener("click", function () {
    data.updated = new Date().toISOString().slice(0, 10);
    var text =
      "/** Inventory for Matthew's Stop and Look Auto Sales.\n" +
      " * Generated by admin.html on " + data.updated + ".\n" +
      " * Replace data/inventory.js with this file and re-deploy to publish. */\n" +
      "window.INVENTORY = " + JSON.stringify(data, null, 2) + ";\n";
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([text], { type: "text/javascript" }));
    a.download = "inventory.js";
    a.click();
    URL.revokeObjectURL(a.href);
    try { localStorage.removeItem(LS_KEY); } catch (e) {}
    setState("Downloaded! Replace data/inventory.js in the site folder and re-deploy.");
  });

  /* ---------- credit apps inbox ---------- */

  // Set this to your backend's list endpoint once your automations exist —
  // it must return JSON: [{id, received, status, fields:{...}}, ...] matching
  // what creditapp.html POSTs to CREDIT_APP_ENDPOINT (see README).
  var CREDIT_APPS_FEED = "";

  var DEMO_APPS = [
    { id: "demo-1", received: "Today 10:42 AM", fields: { "First Name": "Marcus", "Last Name": "T.", "Mobile Phone": "313-555-0148", "Monthly Income": "$3,200", "Employer": "Detroit Medical Center", "Vehicle To Finance": "2019 Chevrolet Malibu LT — $13,995", "Down Payment": "$500 – $1,000" } },
    { id: "demo-2", received: "Today 9:15 AM", fields: { "First Name": "Keisha", "Last Name": "W.", "Mobile Phone": "313-555-0192", "Monthly Income": "$2,600", "Employer": "Self-Employed / 1099", "Vehicle To Finance": "2018 Ford Escape SE — $12,495", "Trade-In": "2009 Impala, running" } },
    { id: "demo-3", received: "Yesterday 4:58 PM", fields: { "First Name": "Andre", "Last Name": "B.", "Mobile Phone": "313-555-0113", "Monthly Income": "$4,100", "Employer": "Stellantis", "Vehicle To Finance": "2015 Ford F-150 XLT SuperCrew — $17,995" } }
  ];

  function appStatuses() {
    try { return JSON.parse(localStorage.getItem("msl-app-status") || "{}"); } catch (e) { return {}; }
  }

  function renderApps(apps) {
    var st = appStatuses();
    $("#apps-count").textContent = apps.length;
    $("#apps-badge").textContent = apps.filter(function (a) { return !st[a.id]; }).length;
    $("#apps-list").innerHTML = apps.map(function (a) {
      var f = a.fields || {};
      var contacted = !!st[a.id];
      var detail = Object.keys(f).map(function (k) {
        return "<span style='display:inline-block;margin:2px 10px 2px 0'><b>" + k + ":</b> " + f[k] + "</span>";
      }).join("");
      return (
        '<div class="admin-row" style="align-items:flex-start">' +
          '<div class="meta">' +
            "<strong>" + (f["First Name"] || "?") + " " + (f["Last Name"] || "") +
            (contacted ? '<span class="badge-sold" style="background:var(--green-600)">CONTACTED</span>' : '<span class="badge-sold" style="background:var(--brand-600)">NEW</span>') +
            "</strong>" +
            '<span>' + (a.received || "") + " · " + (f["Vehicle To Finance"] || "no vehicle picked") + "</span>" +
            '<div style="font-size:12.5px;color:var(--ink-soft);margin-top:6px">' + detail + "</div>" +
          "</div>" +
          '<div class="ops">' +
            (f["Mobile Phone"] ? '<a class="op" href="tel:' + f["Mobile Phone"].replace(/[^0-9+]/g, "") + '">Call</a>' +
             '<a class="op" href="sms:' + f["Mobile Phone"].replace(/[^0-9+]/g, "") + '">Text</a>' : "") +
            '<button class="op' + (contacted ? " on" : "") + '" data-app="' + a.id + '">✓ Contacted</button>' +
          "</div>" +
        "</div>"
      );
    }).join("") || '<div class="empty-state"><strong>No applications yet.</strong>They\'ll show up here as they come in.</div>';
  }

  $("#apps-list").addEventListener("click", function (e) {
    var btn = e.target.closest("button[data-app]");
    if (!btn) return;
    var st = appStatuses();
    var id = btn.getAttribute("data-app");
    st[id] = !st[id];
    try { localStorage.setItem("msl-app-status", JSON.stringify(st)); } catch (err) {}
    loadApps();
  });

  function loadApps() {
    if (CREDIT_APPS_FEED) {
      $("#apps-config-note").style.display = "none";
      fetch(CREDIT_APPS_FEED).then(function (r) { return r.json(); }).then(renderApps)
        .catch(function () {
          $("#apps-list").innerHTML = '<div class="empty-state"><strong>Couldn\'t reach the applications feed.</strong>Check CREDIT_APPS_FEED in js/admin.js.</div>';
        });
    } else {
      renderApps(DEMO_APPS);
    }
  }

  /* ---------- tabs ---------- */

  function showTab(which) {
    $("#view-inventory").hidden = which !== "inventory";
    $("#view-apps").hidden = which !== "apps";
    $("#tab-inventory").className = "btn btn-sm " + (which === "inventory" ? "btn-primary" : "btn-ghost");
    $("#tab-apps").className = "btn btn-sm " + (which === "apps" ? "btn-primary" : "btn-ghost");
  }
  $("#tab-inventory").addEventListener("click", function () { showTab("inventory"); });
  $("#tab-apps").addEventListener("click", function () { showTab("apps"); loadApps(); });

  renderList();
  loadApps();
  showTab("inventory");
})();
