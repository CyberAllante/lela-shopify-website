/**
 * Shared site logic. Which page-specific init runs is decided by
 * <body data-page="..."> — home | inventory | vehicle | financing | about.
 * All vehicle data comes from window.INVENTORY (data/inventory.js).
 */
(function () {
  "use strict";

  var DATA = window.INVENTORY || { vehicles: [], dealership: {} };
  var VEHICLES = DATA.vehicles.filter(function (v) { return !v.sold; });

  /* ---------- helpers ---------- */

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function money(n) {
    return "$" + Number(n).toLocaleString("en-US");
  }

  function miles(n) {
    return Number(n).toLocaleString("en-US") + " mi";
  }

  function title(v) {
    return v.year + " " + v.make + " " + v.model + (v.trim ? " " + v.trim : "");
  }

  // Rough monthly payment used on cards/VDP: 10% down, 60 months, 14.9% APR.
  // Purely an estimate — real terms come from the dealership's lenders.
  function estMonthly(price, down, apr, months) {
    down = down == null ? price * 0.1 : down;
    apr = apr == null ? 14.9 : apr;
    months = months || 60;
    var principal = Math.max(price - down, 0);
    var r = apr / 100 / 12;
    if (principal <= 0) return 0;
    if (r === 0) return principal / months;
    return (principal * r) / (1 - Math.pow(1 + r, -months));
  }

  function cardHTML(v) {
    var img = (v.images && v.images[0]) || "assets/placeholder-sedan.svg";
    var tag = v.featured ? '<span class="tag">Featured</span>' : "";
    if (v.sold) tag = '<span class="tag sold">Sold</span>';
    return (
      '<a class="vehicle-card" href="vehicle.html?id=' + encodeURIComponent(v.id) + '">' +
        '<div class="vehicle-photo">' + tag +
          '<img src="' + img + '" alt="' + title(v) + '" loading="lazy">' +
        "</div>" +
        '<div class="vehicle-body">' +
          '<div class="vehicle-title">' + title(v) + "</div>" +
          '<div class="vehicle-sub">' + v.bodyStyle + " · " + v.exteriorColor + "</div>" +
          '<div class="vehicle-meta">' +
            '<span class="chip">' + miles(v.mileage) + "</span>" +
            '<span class="chip">' + v.transmission + "</span>" +
            '<span class="chip">' + v.drivetrain + "</span>" +
          "</div>" +
          '<div class="vehicle-foot">' +
            '<div class="price">' + money(v.price) +
              "<small>est. " + money(Math.round(estMonthly(v.price))) + "/mo*</small>" +
            "</div>" +
            '<span class="btn btn-ghost btn-sm">Details</span>' +
          "</div>" +
        "</div>" +
      "</a>"
    );
  }

  function renderCards(el, list) {
    if (!el) return;
    if (!list.length) {
      el.innerHTML =
        '<div class="empty-state" style="grid-column:1/-1">' +
        "<strong>No vehicles match those filters.</strong>" +
        "Try widening your price range, or call us — new cars arrive every week." +
        "</div>";
      return;
    }
    el.innerHTML = list.map(cardHTML).join("");
  }

  function uniqueSorted(field) {
    var seen = {};
    VEHICLES.forEach(function (v) { seen[v[field]] = true; });
    return Object.keys(seen).sort();
  }

  function fillSelect(el, values, labelAll) {
    if (!el) return;
    el.innerHTML =
      '<option value="">' + labelAll + "</option>" +
      values.map(function (x) { return '<option value="' + x + '">' + x + "</option>"; }).join("");
  }

  /* ---------- shared chrome ---------- */

  function initChrome() {
    var toggle = $(".nav-toggle");
    var nav = $(".main-nav");
    if (toggle && nav) {
      toggle.addEventListener("click", function () {
        nav.classList.toggle("open");
      });
    }
    var yearEl = $("#footer-year");
    if (yearEl) yearEl.textContent = String(new Date().getFullYear());

    // Mark current page in the nav.
    var page = document.body.getAttribute("data-page");
    $all(".main-nav a").forEach(function (a) {
      if (a.getAttribute("data-nav") === page) a.classList.add("active");
    });
  }

  /* ---------- home ---------- */

  function initHome() {
    var featured = VEHICLES.filter(function (v) { return v.featured; });
    if (featured.length < 3) featured = VEHICLES.slice(0, 6);
    renderCards($("#featured-grid"), featured.slice(0, 6));

    fillSelect($("#qs-make"), uniqueSorted("make"), "Any Make");
    fillSelect($("#qs-body"), uniqueSorted("bodyStyle"), "Any Type");

    var form = $("#quick-search-form");
    if (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var params = new URLSearchParams();
        var make = $("#qs-make").value;
        var body = $("#qs-body").value;
        var price = $("#qs-price").value;
        if (make) params.set("make", make);
        if (body) params.set("body", body);
        if (price) params.set("maxPrice", price);
        window.location.href = "inventory.html" + (params.toString() ? "?" + params : "");
      });
    }
  }

  /* ---------- inventory ---------- */

  function initInventory() {
    var grid = $("#inventory-grid");
    var countEl = $("#result-count");
    var makeSel = $("#f-make");
    var bodySel = $("#f-body");
    var priceSel = $("#f-price");
    var milesSel = $("#f-miles");
    var searchInput = $("#f-search");
    var sortSel = $("#f-sort");

    fillSelect(makeSel, uniqueSorted("make"), "All Makes");
    fillSelect(bodySel, uniqueSorted("bodyStyle"), "All Types");

    // Seed filters from URL (?make=Ford&body=SUV&maxPrice=15000)
    var params = new URLSearchParams(window.location.search);
    if (params.get("make")) makeSel.value = params.get("make");
    if (params.get("body")) bodySel.value = params.get("body");
    if (params.get("maxPrice")) priceSel.value = params.get("maxPrice");
    if (params.get("q")) searchInput.value = params.get("q");

    function apply() {
      var make = makeSel.value;
      var body = bodySel.value;
      var maxPrice = Number(priceSel.value) || Infinity;
      var maxMiles = Number(milesSel.value) || Infinity;
      var q = (searchInput.value || "").trim().toLowerCase();

      var list = VEHICLES.filter(function (v) {
        if (make && v.make !== make) return false;
        if (body && v.bodyStyle !== body) return false;
        if (v.price > maxPrice) return false;
        if (v.mileage > maxMiles) return false;
        if (q && (title(v) + " " + (v.description || "")).toLowerCase().indexOf(q) === -1) return false;
        return true;
      });

      var sort = sortSel.value;
      list.sort(function (a, b) {
        if (sort === "price-asc") return a.price - b.price;
        if (sort === "price-desc") return b.price - a.price;
        if (sort === "year-desc") return b.year - a.year;
        if (sort === "miles-asc") return a.mileage - b.mileage;
        return (b.featured === true) - (a.featured === true);
      });

      renderCards(grid, list);
      if (countEl) {
        countEl.textContent = list.length + " vehicle" + (list.length === 1 ? "" : "s") + " available";
      }
    }

    [makeSel, bodySel, priceSel, milesSel, sortSel].forEach(function (el) {
      if (el) el.addEventListener("change", apply);
    });
    if (searchInput) searchInput.addEventListener("input", apply);

    apply();
  }

  /* ---------- vehicle detail ---------- */

  function initVehicle() {
    var id = new URLSearchParams(window.location.search).get("id");
    var v = DATA.vehicles.filter(function (x) { return x.id === id; })[0];
    var root = $("#vdp-root");
    if (!v) {
      root.innerHTML =
        '<div class="empty-state" style="margin:40px 0">' +
        "<strong>Vehicle not found.</strong>" +
        'It may have just sold. <a href="inventory.html" style="color:var(--dark-800);font-weight:700;text-decoration:underline">Browse the rest of our inventory →</a>' +
        "</div>";
      return;
    }

    document.title = title(v) + " | Matthew's Stop and Look Auto Sales";

    var imgs = v.images && v.images.length ? v.images : ["assets/placeholder-sedan.svg"];
    var phone = DATA.dealership.phone || "313-891-8000";
    var phoneHref = DATA.dealership.phoneHref || "tel:+13138918000";

    root.innerHTML =
      '<div class="vdp-layout">' +
        "<div>" +
          '<div class="gallery-main"><img id="gallery-main-img" src="' + imgs[0] + '" alt="' + title(v) + '"></div>' +
          (imgs.length > 1
            ? '<div class="gallery-thumbs">' +
              imgs.map(function (src, i) {
                return '<button data-i="' + i + '"' + (i === 0 ? ' class="active"' : "") + '><img src="' + src + '" alt="Photo ' + (i + 1) + '" loading="lazy"></button>';
              }).join("") +
              "</div>"
            : "") +
          '<div class="vdp-desc">' +
            "<h2>About this " + v.model + "</h2>" +
            "<p>" + (v.description || "Call us for full details on this vehicle.") + "</p>" +
            (v.features && v.features.length
              ? '<ul class="feature-list">' + v.features.map(function (f) { return "<li>" + f + "</li>"; }).join("") + "</ul>"
              : "") +
          "</div>" +
        "</div>" +
        "<div>" +
          '<div class="vdp-panel">' +
            "<h1>" + title(v) + "</h1>" +
            '<div class="vdp-sub">Stock #' + (v.stock || "—") + (v.vin ? " · VIN " + v.vin : "") + "</div>" +
            '<div class="vdp-price">' + money(v.price) + "</div>" +
            '<div class="vdp-payment">est. ' + money(Math.round(estMonthly(v.price))) + "/mo* with 10% down</div>" +
            '<div class="vdp-actions">' +
              '<a class="btn btn-primary btn-block" href="financing.html?vehicle=' + encodeURIComponent(title(v)) + '">Get Pre-Approved</a>' +
              '<a class="btn btn-dark btn-block" href="' + phoneHref + '">Call ' + phone + "</a>" +
              '<a class="btn btn-ghost btn-block" href="financing.html?vehicle=' + encodeURIComponent(title(v)) + "#trade" + '">Value My Trade-In</a>' +
            "</div>" +
            '<table class="spec-table">' +
              "<tr><td>Mileage</td><td>" + miles(v.mileage) + "</td></tr>" +
              "<tr><td>Body Style</td><td>" + v.bodyStyle + "</td></tr>" +
              "<tr><td>Engine</td><td>" + (v.engine || "—") + "</td></tr>" +
              "<tr><td>Transmission</td><td>" + (v.transmission || "—") + "</td></tr>" +
              "<tr><td>Drivetrain</td><td>" + (v.drivetrain || "—") + "</td></tr>" +
              "<tr><td>Exterior</td><td>" + (v.exteriorColor || "—") + "</td></tr>" +
              "<tr><td>Interior</td><td>" + (v.interiorColor || "—") + "</td></tr>" +
              (v.mpgCity ? "<tr><td>MPG (city/hwy)</td><td>" + v.mpgCity + " / " + v.mpgHwy + "</td></tr>" : "") +
            "</table>" +
            '<div class="calc">' +
              "<h3>Estimate Your Payment</h3>" +
              '<div class="calc-grid">' +
                '<div><label>Down Payment</label><input id="calc-down" type="number" value="' + Math.round(v.price * 0.1) + '" min="0" step="100"></div>' +
                '<div><label>APR %</label><input id="calc-apr" type="number" value="14.9" min="0" step="0.1"></div>' +
                '<div class="full" style="grid-column:1/-1"><label>Term</label>' +
                  '<select id="calc-term"><option value="36">36 months</option><option value="48">48 months</option><option value="60" selected>60 months</option><option value="72">72 months</option></select>' +
                "</div>" +
              "</div>" +
              '<div class="calc-result">Estimated payment: <strong id="calc-out"></strong>/mo</div>' +
              '<div class="calc-note">*Estimate only. Not a financing offer — your rate and terms depend on credit approval.</div>' +
            "</div>" +
          "</div>" +
        "</div>" +
      "</div>";

    // Gallery thumbs
    $all(".gallery-thumbs button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        $all(".gallery-thumbs button").forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        $("#gallery-main-img").src = imgs[Number(btn.getAttribute("data-i"))];
      });
    });

    // Payment calculator
    function recalc() {
      var down = Number($("#calc-down").value) || 0;
      var apr = Number($("#calc-apr").value) || 0;
      var term = Number($("#calc-term").value) || 60;
      $("#calc-out").textContent = money(Math.round(estMonthly(v.price, down, apr, term)));
    }
    ["calc-down", "calc-apr", "calc-term"].forEach(function (fid) {
      $("#" + fid).addEventListener("input", recalc);
      $("#" + fid).addEventListener("change", recalc);
    });
    recalc();

    // SEO: schema.org Vehicle markup
    var ld = {
      "@context": "https://schema.org",
      "@type": "Car",
      name: title(v),
      brand: v.make,
      model: v.model,
      vehicleModelDate: String(v.year),
      mileageFromOdometer: { "@type": "QuantitativeValue", value: v.mileage, unitCode: "SMI" },
      color: v.exteriorColor,
      offers: { "@type": "Offer", price: v.price, priceCurrency: "USD", availability: "https://schema.org/InStock" }
    };
    var s = document.createElement("script");
    s.type = "application/ld+json";
    s.textContent = JSON.stringify(ld);
    document.head.appendChild(s);
  }

  /* ---------- financing ---------- */

  function initFinancing() {
    // Pre-fill "vehicle of interest" from ?vehicle=
    var vehicle = new URLSearchParams(window.location.search).get("vehicle");
    var vehicleInput = $("#fin-vehicle");
    if (vehicle && vehicleInput) vehicleInput.value = vehicle;

    var form = $("#finance-form");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      // No backend wired up yet: open the visitor's email client with the
      // details pre-filled, addressed to the dealership. Swap this for a
      // Formspree/Basin endpoint (see README) for a smoother experience.
      var fields = $all("input, select, textarea", form);
      var lines = fields
        .filter(function (f) { return f.name && f.value; })
        .map(function (f) { return f.name + ": " + f.value; });
      var mail =
        "mailto:sales@313carloans.com" +
        "?subject=" + encodeURIComponent("Pre-Approval Request from Website") +
        "&body=" + encodeURIComponent(lines.join("\n"));
      window.location.href = mail;
      var ok = $("#form-success");
      if (ok) ok.style.display = "block";
    });
  }

  /* ---------- boot ---------- */

  document.addEventListener("DOMContentLoaded", function () {
    initChrome();
    var page = document.body.getAttribute("data-page");
    if (page === "home") initHome();
    if (page === "inventory") initInventory();
    if (page === "vehicle") initVehicle();
    if (page === "financing") initFinancing();
  });
})();
