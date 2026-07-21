# 313 Car Loans — New Website

A modern, fast, conversion-focused website for **Matthew's Stop and Look Auto Sales**
(McQueen Auto, Inc.) — 8146 E 8 Mile Rd, Detroit, MI 48234 · 313-891-8000 —
currently at [313carloans.com](https://313carloans.com).

---

## What their current site runs on

The existing site is built by **[Dealer Car Search](https://www.dealercarsearch.com)** —
a website + back-office vendor for independent used-car dealers. You can tell from the
template URL structure (`/newandusedcars`, `/vdp/…` vehicle pages, `/bdp/…` blog pages,
`/creditapp`, `/locatorservice`, `/meetourstaff`), which is Dealer Car Search's standard
site skeleton.

That's also the "software that handles a whole bunch of their backend stuff":
Dealer Car Search isn't just the website — it's their **inventory manager and lead
system**. Dealers log in, add a car with photos once, and it feeds the website *and*
syndicates listings out to Facebook Marketplace, Craigslist, CarGurus, etc., and
collects leads/credit apps back in. Keep that in mind before fully replacing it:
the smart play is usually to **replace the front-end website** (this project) while
they keep using their existing back office for inventory + syndication — or move to
any other DMS later, since this site just reads a data file and can be fed by anything.

## What this project is

A **zero-dependency static website** — plain HTML/CSS/JS, no framework, no build
step, hostable anywhere for free (GitHub Pages, Netlify, Cloudflare Pages). All
vehicle data lives in one file: **`data/inventory.js`**. Change that file, and the
whole site updates.

```
313-car-loans/
├── index.html          Homepage — hero, quick search, featured cars, financing CTA
├── inventory.html      Full inventory with live filters (make/body/price/miles) + sort
├── vehicle.html        Vehicle detail page (?id=…) — gallery, specs, payment calculator
├── financing.html      Pre-approval + trade-in form (soft inquiry, no SSN collected)
├── about.html          About, hours, map, directions
├── css/styles.css      All styling (design tokens at the top for easy re-theming)
├── js/site.js          All behavior (rendering, filters, calculator)
├── data/inventory.js   ⭐ THE data file — every car on the site lives here
├── assets/             Placeholder images (+ downloaded photos after scraping)
└── scraper/scrape_inventory.py   Pulls real inventory from 313carloans.com
```

## Quick start

Just open `index.html` in a browser — it works from disk. For a proper local server:

```bash
cd 313-car-loans
python3 -m http.server 8080
# → http://localhost:8080
```

## Pulling their real inventory

The scraper reads the live site's sitemap, visits every vehicle page, and rewrites
`data/inventory.js` with real cars, prices, mileage, VINs and photo URLs.
Run it from any normal machine with internet access:

```bash
cd 313-car-loans/scraper
pip install requests beautifulsoup4
python3 scrape_inventory.py --limit 3      # test on 3 cars first
python3 scrape_inventory.py                # full inventory, hotlinks their photo CDN
python3 scrape_inventory.py --download-images   # also saves photos into assets/photos/
```

Use `--download-images` for the real launch so the site doesn't depend on
Dealer Car Search's CDN staying up. Re-run whenever the lot changes, then push /
re-deploy. (It's the dealership scraping its own data — still, the script is
polite and rate-limited.)

**Ongoing updates without scraping:** `data/inventory.js` is human-editable.
Adding a car is copy-pasting a block and changing the fields. Down the road you
can generate it from any DMS export (Frazer, DealerCenter, Wayne Reaves and
Dealer Car Search can all export CSV inventory feeds).

## Deploying free on GitHub Pages

1. Push this folder to a GitHub repo.
2. Repo → Settings → Pages → deploy from branch, folder `/313-car-loans` (or move
   these files to the repo root / a `docs/` folder).
3. Point the `313carloans.com` domain (or a new one) at GitHub Pages when ready.

Netlify / Cloudflare Pages: drag-and-drop the folder — done.

## Wiring up the lead form

`financing.html` currently opens the visitor's email app (mailto) with the form
contents. For a smoother experience, create a free form endpoint at
[Formspree](https://formspree.io) (or Basin/Web3Forms) and swap the mailto block in
`js/site.js` (`initFinancing`) for a `fetch()` POST to that endpoint — it's marked
with a comment. Leads then arrive by email/dashboard without the visitor's email
app opening.

**Important:** the form deliberately collects **no SSN or date of birth**. A full
credit application with SSN requires a secure, compliant backend (SSL + encryption
+ GLBA safeguards). Options: keep linking to their existing secure credit app, or
use a dealer-finance form service (700Credit QuickQualify, etc.). Don't collect
SSNs through a static-site form.

## Things to verify with the owner before launch

- [ ] Hero photo — currently an AI-generated stand-in of "the lot" (Higgsfield), hotlinked in
      `css/styles.css`. Replace with a real photo of the shop: save it as `assets/hero-lot.jpg`
      and point the `url()` in the `.hero` rule at it (Google Business Profile photos work great)
- [ ] Business hours (currently placeholders: M–F 10–6, Sat 10–4, Sun closed)
- [ ] Address — listings show both "8146 E 8 Mile Rd" and "8146 W 8 Mile Rd / M-102"; confirm which is right
- [ ] Real customer reviews to replace the sample ones on the homepage
- [ ] Lead email address (form currently targets `sales@313carloans.com` — likely wrong)
- [ ] Logo / brand colors if they have them (edit CSS variables at the top of `styles.css`)
- [ ] Whether they're keeping Dealer Car Search for back-office (recommended at first)

## Re-theming in 30 seconds

All colors are CSS variables at the top of `css/styles.css`:

```css
--dark-800: #1a1c21;    /* header / dark sections */
--brand-600: #c1121f;   /* stop-sign red — CTAs + accents */
```

Change those two and the whole site follows. The logo lives in `assets/logo.svg`
(used in the header, hero, footer, and favicon).
