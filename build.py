"""Build the asdaria static site with the Python standard library."""

import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
DATA = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
PHONE = "+254733954103"
EMAIL = "asdaria.ltd@gmail.com"
# The public address search engines and link previews use; change it when a custom domain goes live.
SITE_URL = "https://asdaria.web.app"
NAV = [("about", "About"), ("services", "Services"), ("projects", "Experience"), ("gallery", "Gallery")]
ATTRIBUTION = {"company": "ASDARIA", "partner": "Directors' experience", "research": "Directors' research"}
GROUPS = {
    "Engineering design, project and construction management": ("engineering-experience", "Engineering", "Engineering", "engineering"),
    "Baseline studies, sector analysis and project feasibility": ("studies-experience", "Studies", "Studies and baselines", "feasibility"),
    "Monitoring and evaluation": ("evaluation-experience", "Evaluation", "Monitoring and evaluation", "evaluation"),
    "Capacity needs assessment and capacity building": ("capacity-experience", "Capacity", "Capacity building", "capacity"),
    "Business feasibility studies and business development services": ("business-experience", "Business", "Business development", "bds"),
    "Policy development and review": ("policy-experience", "Policy", "Policy", "policy"),
}
FEATURES = {"coffee": "coffee-assessment", "kalobeyei": "food-hub", "afpq": None}
PHOTOS = {
    "coffee-assessment": (1600, 1200, "Coffee infrastructure assessment", "A site assessment beside coffee-processing water channels and a small pump building."),
    "climate-assessment": (1200, 1600, "Climate adaptation field visit", "A project site visit beside a reservoir and earthworks."),
    "food-hub": (1600, 1200, "Food hub exterior", "The courtyard and buildings of a food-processing hub."),
    "bakery": (1600, 1200, "Bakery interior", "Bakery equipment, racks and stainless-steel work surfaces."),
    "poultry-layout": (1200, 1600, "Poultry-house layout", "A team setting out a poultry-house layout on site."),
    "greenhouse-dryer": (680, 510, "Greenhouse dryer", "A greenhouse drying structure with a visitor standing beside the entrance."),
    "capacity-building": (1280, 720, "Capacity-building preparation", "A training room being prepared with tables, materials and presentation equipment."),
    "director-samuel": (385, 385, "Eng. Samuel Njuguna Ndirangu", "Portrait of Eng. Samuel Njuguna Ndirangu."),
    "director-grace": (236, 236, "Grace Muthoni Mwangi", "Portrait of Grace Muthoni Mwangi."),
}
CAPTIONS = {
    "coffee-assessment": "Assessment of coffee infrastructure to redesign and improve water re-circulation.",
    "climate-assessment": "A project site visit to assess the impact of a climate change adaptation project.",
    "food-hub": "A near-complete food hub following design and construction oversight.",
    "bakery": "A mini bakery supported through design, construction supervision, equipment selection and installation support.",
    "poultry-layout": "Setting out the layout of a poultry house.",
    "greenhouse-dryer": "A greenhouse dryer for red pepper, documented during construction.",
    "capacity-building": "Preparing a venue for capacity building.",
}
ORGANISATIONS = [
    ("celim", "CELIM, Centro Laici Italiani per le Missioni", 6, "company"),
    ("jkuat", "Jomo Kenyatta University of Agriculture and Technology", 7, "director"),
    ("agriculture-ministry", "Ministry of Agriculture and Livestock Development, Kenya", 8, "director"),
    ("cold-chain", "World Food Logistics Organization / Global Cold Chain Foundation", 9, "director"),
    ("agra", "AGRA", 10, "director"),
    ("fao", "Food and Agriculture Organization of the United Nations", 11, "director"),
    ("usaid", "USAID / Development Alternatives Incorporated", 12, "director"),
    ("solidaridad", "Solidaridad Network", 13, "director"),
    ("gain", "Global Alliance for Improved Nutrition", 14, "director"),
    ("snv", "SNV Netherlands Development Organisation", 15, "director"),
    ("aatf", "African Agricultural Technology Foundation", 16, "director"),
    ("wfp", "United Nations World Food Programme", 17, "director"),
    ("rti", "RTI International", 18, "director"),
    ("fairtrade", "Fairtrade Africa", 19, "director"),
    ("nema", "National Environment Management Authority, Kenya", 20, "director"),
    ("kcic", "Kenya Climate Innovation Center", 21, "director"),
    ("world-bank", "World Bank", 22, "director"),
    ("kcsap", "Kenya Climate Smart Agriculture Project", 23, "director"),
    ("narigp", "National Agricultural and Rural Inclusive Growth Project", 24, "director"),
    ("childfund", "ChildFund International", 25, "director"),
    ("mespt", "Micro Enterprises Support Programme Trust", 26, "director"),
    ("welthungerhilfe", "Welthungerhilfe", 27, "director"),
    ("kenya-markets-trust", "Kenya Markets Trust", 28, "director"),
    ("pwc", "PwC", 29, "director"),
    ("act", "Act! Change Transform", 30, "director"),
    ("cdtf", "Community Development Trust Fund", 31, "director"),
    ("eu", "European Union", 32, "director"),
    ("jica", "Japan International Cooperation Agency", 33, "director"),
]
HOME_ORGANISATIONS = ["fao", "world-bank", "wfp", "agra", "snv", "gain", "jica"]
LOGO_SCALE = {"welthungerhilfe": 0.82, "eu": 0.9, "snv": 0.85, "fairtrade": 1.1, "kcsap": 1.1, "kenya-markets-trust": 1.1}


def esc(value):
    return html.escape(str(value), quote=True)


def arrow():
    return '<span aria-hidden="true">&rarr;</span>'


def icon(name):
    paths = {
        "feasibility": '<path d="M5 4h11l3 3v17H5zM9 10h6M9 14h6M9 19l3-3 3 2 4-5"/>',
        "engineering": '<path d="M3 24 14 4l11 20zM9 24l5-9 5 9M9 14h10"/>',
        "postharvest": '<path d="M4 13 14 5l10 8v11H4zM10 24v-8h8v8M14 5V2M5 10V5h4"/>',
        "research": '<path d="M10 3h8M12 3v9L5 23q-1 2 2 2h14q3 0 2-2l-7-11V3M9 18h10M12 21h1M16 15h1"/>',
        "technology": '<path d="M3 7h15v12H3zM6 19v5M15 19v5M18 11h6v13M3 13h15M7 10h3M7 16h3"/>',
        "capacity": '<path d="m3 9 11-5 11 5-11 5zM7 11v7q7 6 14 0v-7M25 9v11"/>',
        "bds": '<path d="M4 24h20M7 20v-6M13 20V9M19 20V4M4 10l7-5 5 2 7-5"/>',
        "policy": '<path d="M7 3h14v22H7zM11 8h6M11 12h6M11 17l2 2 5-4"/>',
        "evaluation": '<circle cx="12" cy="12" r="8"/><path d="m18 18 7 7M8.5 12l2.5 2.5 4.5-5"/>',
        "agriculture": '<path d="M14 25V13M14 13C14 8 10.5 5 5 5c0 5 3.5 8 9 8zM14 17c0-5 3.5-8 9-8 0 5-3.5 8-9 8zM8 25h12"/>',
        "water": '<path d="M14 3C10.5 8.5 6 12.5 6 17.5a8 8 0 0 0 16 0C22 12.5 17.5 8.5 14 3zM10 18a4 4 0 0 0 4 4"/>',
        "environment": '<path d="M14 25v-8M14 20l-3.5-3.5M14 18.5l3-3M14 3a7 7 0 0 0-6.6 9.4A5 5 0 0 0 9 22h10a5 5 0 0 0 1.6-9.6A7 7 0 0 0 14 3z"/>',
        "energy": '<circle cx="14" cy="14" r="5"/><path d="M14 3v3M14 22v3M3 14h3M22 14h3M6.2 6.2l2.1 2.1M19.7 19.7l2.1 2.1M6.2 21.8l2.1-2.1M19.7 8.3l2.1-2.1"/>',
        "region": '<path d="M14 25s-8-7.4-8-13a8 8 0 0 1 16 0c0 5.6-8 13-8 13z"/><circle cx="14" cy="12" r="3"/>',
        "phone": '<path d="m8 3-4 2c-2 9 10 21 19 19l2-4-6-4-3 3c-4-2-6-4-8-8l3-3z"/>',
        "email": '<rect x="3" y="6" width="22" height="16" rx="1"/><path d="m3 7 11 8L25 7"/>',
    }
    return f'<svg class="practice-icon" viewBox="0 0 28 28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{paths[name]}</svg>'


def control_icon(path):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="{path}"/></svg>'


def brand():
    return '''<img class="brand-mark" src="assets/asdaria-logo.png" width="800" height="787" alt="">
      <span class="brand-copy"><span class="brand-name">ASDARIA</span><span class="brand-descriptor">Agribzenergy Systems</span></span>'''


def contact_link(kind):
    href, value = (f"tel:{PHONE}", PHONE) if kind == "phone" else (f"mailto:{EMAIL}", EMAIL)
    return f'<a class="contact-link" href="{href}">{icon(kind)}<span class="contact-value">{value}</span></a>'


def picture(name, alt=None, eager=False, sizes="(max-width: 760px) calc(100vw - 40px), 50vw"):
    width, height, _, default_alt = PHOTOS[name]
    loading = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    responsive = ""
    if width > 960:
        responsive = f' srcset="assets/img/{name}-small.webp 640w, assets/img/{name}.webp {width}w" sizes="{sizes}"'
    return f'<img src="assets/img/{name}.webp"{responsive} width="{width}" height="{height}" alt="{esc(default_alt if alt is None else alt)}" {loading}>'


def webp_size(path):
    header = path.read_bytes()[:30]
    chunk = header[12:16]
    if chunk == b"VP8L":
        bits = int.from_bytes(header[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b"VP8X":
        return int.from_bytes(header[24:27], "little") + 1, int.from_bytes(header[27:30], "little") + 1
    if chunk == b"VP8 ":
        return int.from_bytes(header[26:28], "little") & 0x3FFF, int.from_bytes(header[28:30], "little") & 0x3FFF
    raise ValueError(f"Unsupported WebP file: {path}")


def organisation_logo(slug):
    name = next(name for key, name, _, _ in ORGANISATIONS if key == slug)
    width, height = webp_size(SITE / "assets" / "organisations" / f"{slug}.webp")
    # Equalise visual weight across wide wordmarks and compact emblems.
    scale = (4300 / (width * height)) ** 0.5 * LOGO_SCALE.get(slug, 1)
    scale = min(scale, 150 / width, 66 / height)
    return f'<li><img src="assets/organisations/{slug}.webp" width="{round(width * scale)}" height="{round(height * scale)}" alt="{esc(name)}" loading="lazy" decoding="async"></li>'


def section_head(eyebrow, title, intro="", heading_id=None):
    identifier = f' id="{heading_id}"' if heading_id else ""
    return f'<div class="section-head"><div><p class="eyebrow">{eyebrow}</p><h2{identifier}>{title}</h2></div>{intro}</div>'


def page_hero(label, title, lead, aside="", modifier=""):
    copy = f'<p class="eyebrow">{esc(label)}</p><h1>{title}</h1><p class="lead">{lead}</p>'
    if aside:
        copy = f'<div class="page-hero-copy">{copy}</div>{aside}'
    return f'''<section class="page-hero{modifier}"><div class="container{" has-aside" if aside else ""}">
      {copy}</div></section>'''


def icon_link(kind):
    href, label = (f"tel:{PHONE}", f"Call {PHONE}") if kind == "phone" else (f"mailto:{EMAIL}", f"Email {EMAIL}")
    return f'<a class="icon-link" href="{href}" aria-label="{label}" title="{label}">{icon(kind)}</a>'


def footer_cta():
    return f'''<div class="footer-cta"><h2>Let's talk about your project.</h2>
      <div class="footer-cta-links">{icon_link("phone")}{icon_link("email")}</div></div>'''


def asset_url(path):
    # The content hash changes the URL whenever the file changes, so browsers never pair new pages with cached old assets.
    return f"{path}?v={hashlib.sha256((SITE / path).read_bytes()).hexdigest()[:10]}"


def page_url(slug):
    return f"{SITE_URL}/" if slug == "index" else f"{SITE_URL}/{slug}.html"


def render(slug, title, description, body):
    def current(key):
        return ' aria-current="page"' if key == slug else ""

    nav = "".join(f'<a href="{key}.html"{current(key)}>{name}</a>' for key, name in NAV)
    nav += f'<a class="nav-cta" href="contact.html"{current("contact")}>Contact us</a>'
    indexing = '<meta name="robots" content="noindex">' if slug == "404" else f'<link rel="canonical" href="{page_url(slug)}"><meta property="og:url" content="{page_url(slug)}">'
    page = f'''<!doctype html>
<html lang="en-KE" data-theme="light"><head><meta charset="utf-8">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#faf9f4">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | ASDARIA</title><meta name="description" content="{esc(description)}">
<meta property="og:title" content="{esc(title)} | ASDARIA">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="ASDARIA">
<meta property="og:locale" content="en_KE">
<meta property="og:image" content="{SITE_URL}/assets/share.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(PHOTOS["bakery"][3])}"><meta name="twitter:card" content="summary_large_image">
{indexing}
<link rel="icon" href="assets/favicon.png" type="image/png">
<link rel="stylesheet" href="{asset_url("assets/style.css")}"><script src="{asset_url("assets/main.js")}" defer></script>
</head><body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="container header-inner">
<a class="brand" href="index.html" aria-label="ASDARIA home">{brand()}</a>
<button class="menu-toggle" type="button" aria-controls="primary-nav" aria-expanded="false" hidden><span class="menu-icon" aria-hidden="true"></span>Menu</button>
<nav id="primary-nav" aria-label="Primary">{nav}</nav>
</div></header>
<main id="main" tabindex="-1">{body}</main>
<footer class="site-footer"><div class="container">{"" if slug == "contact" else footer_cta()}
<div class="footer-bottom"><p>&copy; ASDARIA Ltd</p><address>P.O. Box 3736, 01002 Thika, Kenya</address><a href="privacy.html">Privacy</a></div>
</div></footer></body></html>'''
    if slug == "404":
        # Hosts serve this page at any missing address, so its URLs must resolve from the site root.
        page = re.sub(r'\b(href|src)="(?![a-z]+:|#|/)', r'\1="/', page)
    (SITE / f"{slug}.html").write_text(page, encoding="utf-8")


def project(project_id):
    return next(p for p in DATA["projects"] if p["id"] == project_id)


def highlights(item):
    return '<ul class="highlights">' + "".join(f"<li>{esc(point)}</li>" for point in item.get("highlights", [])) + "</ul>"


def home():
    service_titles = {service["id"]: service["title"] for service in DATA["services"]}
    pillars = [
        ("feasibility", "Feasibility & business advisory", "Feasibility studies, business development support, financial analysis and business planning for agricultural investments.", ["feasibility", "bds"]),
        ("engineering", "Engineering design & technology", "Design and installation of production, processing and energy systems, with technology support, tender documents and construction supervision.", ["engineering", "technology"]),
        ("research", "Studies, evaluation & capacity", "Value chain and post-harvest studies, baselines, monitoring and evaluation, capacity strengthening and policy review.", ["postharvest", "research", "capacity", "policy"]),
    ]
    pillar_items = "".join(f'''<li class="pillar reveal"><div class="pillar-head"><span class="pillar-index">0{i}</span>{icon(key)}</div><h3>{title}</h3><p>{text}</p>
      <ul class="pillar-links">{"".join(f'<li><a href="services.html#{sid}">{esc(service_titles[sid])}<span aria-hidden="true">&rarr;</span></a></li>' for sid in services)}</ul></li>''' for i, (key, title, text, services) in enumerate(pillars, 1))
    company_logo = organisation_logo("celim")
    director_logos = "".join(organisation_logo(slug) for slug in HOME_ORGANISATIONS)
    case_sizes = "(max-width: 900px) calc(100vw - 40px), 440px"
    cases = [
        (project("coffee"), "Coffee processing and water re-circulation", picture("coffee-assessment", sizes=case_sizes)),
        (project("kalobeyei"), "Kalobeyei food-processing hub", picture("food-hub", sizes=case_sizes)),
        (project("afpq"), "Alliance for Product Quality in Africa", f'<span class="case-mark" aria-hidden="true">{icon("bds")}<span>AFPQ</span></span>'),
    ]
    case_items = "".join(f'''<article class="case reveal{" is-company" if item["track"] == "company" else ""}"><div class="case-media">{media}</div><div class="case-body">
      <p class="case-label">{"Through ASDARIA" if item["track"] == "company" else ATTRIBUTION[item["track"]]}</p><h3><a href="projects.html#{item["id"]}">{title}</a></h3><p>{esc(item["summary"])}</p></div></article>''' for item, title, media in cases)
    partner = [p for p in DATA["projects"] if p["track"] == "partner"]
    index_items = "".join(f'<li><a href="projects.html#{group_id}"><span class="index-count">{sum(p["category"] == category for p in partner)}</span><span class="index-label">{icon(icon_name)}{label}</span></a></li>' for category, (group_id, _, label, icon_name) in GROUPS.items())
    reasons = [
        ("bds", "Business case first", "Technical layouts and equipment choices connected to a viable business case."),
        ("research", "Connected to research", "The directors' research with universities and research institutions spans solar drying, renewable energy and value chain upgrading."),
        ("region", "Field experience across the region", "The directors' assignments span Kenyan counties and countries across sub-Saharan Africa, from post-harvest baselines to processing facilities."),
    ]
    reason_items = "".join(f'<li class="reason reveal"><span class="card-icon">{icon(key)}</span><h3>{title}</h3><p>{text}</p></li>' for key, title, text in reasons)
    leaders = f'''<div class="leaders"><div class="leader-faces">{picture("director-samuel", alt="")}{picture("director-grace", alt="")}</div>
      <p>Led by <strong>Eng. Samuel Njuguna Ndirangu</strong>, Executive Director, and <strong>Grace Muthoni Mwangi</strong>, Non-Executive Director.</p>
      <a class="text-link" href="about.html#leadership-title">Meet the directors {arrow()}</a></div>'''
    body = f'''<section class="home-hero" aria-labelledby="hero-title"><div class="home-hero-grid">
      <div class="hero-copy"><p class="eyebrow">Engineering &amp; agribusiness consultancy, Kenya</p>
      <h1 id="hero-title">Agricultural<br>engineering.<br><span>Agribusiness<br>insight.</span></h1>
      <p class="hero-lead">Technical design, commercial analysis and applied research for agricultural, food-processing, water and energy systems.</p>
      <div class="hero-actions"><a class="button light" href="services.html">Explore our services {arrow()}</a><a class="button outline-light" href="projects.html">See our experience</a></div></div>
      <figure class="hero-media">{picture("bakery", eager=True, sizes="(max-width: 900px) 100vw, 50vw")}<figcaption>{CAPTIONS["bakery"]}</figcaption></figure>
      </div></section>
      <section class="org-band" aria-labelledby="org-band-title"><div class="container">
      <div class="org-band-head"><h2 id="org-band-title">Organisations we have worked with</h2><a class="text-link" href="about.html#organisations">All organisations {arrow()}</a></div>
      <div class="org-band-groups"><div class="org-band-group org-band-company"><p>Through ASDARIA</p><ul class="org-row">{company_logo}</ul></div>
      <div class="org-band-group"><p>Directors' experience</p><ul class="org-row">{director_logos}</ul></div></div>
      </div></section>
      <section class="section practice" aria-labelledby="practice-title"><div class="container">
      {section_head("What we do", "Technical decisions.<br>Commercial context.", "<p>ASDARIA brings engineering and business thinking together, from the first investment question to the systems and skills needed to operate.</p>", "practice-title")}
      <ol class="pillars reveal-group">{pillar_items}</ol></div></section>
      <section class="section soft featured" aria-labelledby="featured-title"><div class="container">
      {section_head("Selected experience", "From design<br>to delivery.", f'<a class="text-link" href="projects.html">All experience {arrow()}</a>', "featured-title")}
      <div class="cases reveal-group">{case_items}</div>
      <div class="practice-index reveal"><h3>Directors' assignments by practice area</h3><ul>{index_items}</ul></div>
      </div></section>
      <section class="section why" aria-labelledby="why-title"><div class="container">
      {section_head("Why ASDARIA", "What we bring<br>to each assignment.", leaders, "why-title")}
      <ul class="reasons reveal-group">{reason_items}</ul>
      </div></section>'''
    render("index", "Agricultural engineering and agribusiness consultancy", "ASDARIA combines agricultural engineering and agribusiness advisory for agriculture, food processing, post-harvest systems, water and energy in Kenya and Africa.", body)


def organisations():
    company = "".join(organisation_logo(slug) for slug, _, _, relationship in ORGANISATIONS if relationship == "company")
    directors = "".join(organisation_logo(slug) for slug, _, _, relationship in ORGANISATIONS if relationship == "director")
    return f'''<section class="section organisations" id="organisations" aria-labelledby="organisations-heading"><div class="container">
      {section_head("Professional connections", "Organisations we<br>have worked with.", "<p>Company engagements and the directors' wider professional experience, shown separately.</p>", "organisations-heading")}
      <div class="org-company"><h3>Through ASDARIA</h3><ul class="org-logo">{company}</ul><p>CELIM, Centro Laici Italiani per le Missioni</p></div>
      <div class="org-directors"><div class="org-directors-head"><h3>Directors' experience</h3><p>Organisations the directors have worked with directly, not through the company.</p></div>
      <ul class="org-wall">{directors}</ul></div>
      </div></section>'''


def about():
    steps = [
        ("Understand", "Assess the site, the market, the constraints and the investment question."),
        ("Design", "Connect technical layouts and equipment choices with a viable business case."),
        ("Implement", "Prepare tender documents and bills of quantities, then supervise construction and installation."),
        ("Strengthen", "Build the skills, operating practices and organisation needed to sustain the system."),
    ]
    step_items = "".join(f'<li><span class="step-index">0{i}</span><h3>{title}</h3><p>{text}</p></li>' for i, (title, text) in enumerate(steps, 1))
    people = [
        ("director-samuel", "Executive Director", "Eng. Samuel Njuguna Ndirangu", "Strategy and day-to-day running of the company: planning, operations, and project implementation and management.", ["BSc Agricultural Engineering", "MA Economic Policy and Management", "PhD candidate"]),
        ("director-grace", "Non-Executive Director", "Grace Muthoni Mwangi", "Oversight, governance, administration, finance and capacity building.", ["BSc Agricultural and Home Economics", "Postgraduate Diploma in Education"]),
    ]
    people_html = "".join(f'<article class="person">{picture(photo)}<div class="person-copy"><p class="person-role">{role}</p><h3>{name}</h3><p>{text}</p><ul class="credentials">{"".join(f"<li>{c}</li>" for c in credentials)}</ul></div></article>' for photo, role, name, text, credentials in people)
    sectors = [
        ("agriculture", "Agriculture", "Animal and crop production, agro-processing and value addition."),
        ("water", "Water", "Water, irrigation, hygiene and sanitation."),
        ("environment", "Environment", "Climate change mitigation and adaptation, and waste management systems."),
        ("energy", "Energy", "Renewable energy technologies, including solar energy systems, coolers and cold rooms."),
    ]
    sector_items = "".join(f'<li class="info-card"><span class="card-icon">{icon(key)}</span><h4>{title}</h4><p>{text}</p></li>' for key, title, text in sectors)
    growth = [
        ("research", "Collaborative, integrated research", "Research in cold chain, post-harvest management, renewable energy and climate change, developed with partners and connected across disciplines."),
        ("postharvest", "Food processing in untapped areas", "Developing starter food-processing businesses in untapped areas."),
    ]
    growth_items = "".join(f'<li class="info-card"><span class="card-icon">{icon(key)}</span><h3>{title}</h3><p>{text}</p></li>' for key, title, text in growth)
    body = page_hero("About ASDARIA", "Engineering and advisory<br>for agri-food systems.", "An agricultural engineering and agribusiness consultancy connecting the systems we design with the enterprises that operate them.")
    body += f'''<section class="section" aria-labelledby="intro-title"><div class="container split intro">
      <div class="intro-copy"><p class="eyebrow">Who we are</p><h2 id="intro-title">Built around<br>practical questions.</h2>
      <p class="large-copy">Agribzenergy Systems Development and Research in Africa (ASDARIA Ltd) is a private company registered in Kenya.</p>
      <p>We work in engineering design, promotion, installation, capacity building and management of agri-systems. Assignments can combine feasibility studies, design, equipment selection, construction supervision, research and training, shaped by the investment and the people who will operate it.</p></div>
      <div class="intro-sectors"><h3 class="sectors-label">Sectors we work in</h3><ul class="card-grid sectors">{sector_items}</ul></div>
      </div></section>
      <section class="section" aria-labelledby="leadership-title"><div class="container">
      {section_head("Leadership", "Complementary perspectives.", "", "leadership-title")}
      <div class="people">{people_html}</div></div></section>
      <section class="section soft" aria-labelledby="approach-title"><div class="container">
      {section_head("How we work", "Clarity at every stage.", "<p>A connected approach to technical, commercial and operational decisions.</p>", "approach-title")}
      <ol class="steps">{step_items}</ol></div></section>'''
    body += organisations()
    body += f'''<section class="section soft growth" aria-labelledby="growth-title"><div class="container">
      {section_head("Future direction", "Connecting research<br>and enterprise.", "", "growth-title")}
      <ul class="card-grid growth-list">{growth_items}</ul></div></section>'''
    render("about", "About us", "Meet ASDARIA, a Kenyan agricultural engineering and agribusiness consultancy: its directors, approach, professional connections and future direction.", body)


def services():
    project_by_id = {p["id"]: p for p in DATA["projects"]}
    stages = [
        ("Production infrastructure", "Animal and on-farm structures, and marketing infrastructure such as collection centres.", "poultry-layout"),
        ("Processing & value addition", "Food and agro-processing plants, food hubs, communal kitchens and bakeries.", "bakery"),
        ("Post-harvest technology", "Drying, cold chain, handling, milling and extraction equipment.", "greenhouse-dryer"),
        ("Enterprise & capacity", "Business planning, financial analysis, advisory services and capacity building.", "capacity-building"),
    ]
    stage_items = "".join(f'<li><div class="chain-photo">{picture(photo, sizes="(max-width: 760px) calc(100vw - 40px), (max-width: 900px) 50vw, 25vw")}</div><h3><span class="index">0{i}</span>{title}</h3><p>{text}</p></li>' for i, (title, text, photo) in enumerate(stages, 1))
    rows = []
    for i, service in enumerate(DATA["services"], 1):
        items = "".join(f"<li>{esc(item)}</li>" for item in service["items"])
        related = "".join(f'<li><a href="projects.html#{esc(pid)}">{esc(project_by_id[pid]["title"])}</a><span class="attribution">{ATTRIBUTION[project_by_id[pid]["track"]]}</span></li>' for pid in service["examples"])
        rows.append(f'''<article class="service-row" id="{service["id"]}"><div class="service-row-head">{icon(service["id"])}<span class="index">0{i}</span><h3>{esc(service["title"])}</h3></div>
      <div class="service-row-body"><p class="service-summary">{esc(service["description"])}</p><ul class="service-items">{items}</ul></div>
      <div class="service-related"><h4>Related experience</h4><ul>{related}</ul></div></article>''')
    service_index = "".join(f'<li><a href="#{service["id"]}"><span class="index">0{i}</span>{esc(service["title"])}<span class="jump-arrow" aria-hidden="true">&darr;</span></a></li>' for i, service in enumerate(DATA["services"], 1))
    body = page_hero("Our services", "Expertise across the<br>agricultural value chain.", "Technical, commercial and institutional support for agricultural, food-processing, water and energy investments.",
                     aside=f'<nav class="service-index" aria-label="Services on this page"><ol>{service_index}</ol></nav>')
    body += f'''<section class="section soft value-chain" aria-labelledby="chain-heading"><div class="container">
      {section_head("Along the value chain", "From production<br>to market.", "<p>Where our engineering and business advisory work fits, from the farm to the enterprise.</p>", "chain-heading")}
      <ol class="chain-stages">{stage_items}</ol></div></section>
      <section class="section" aria-labelledby="services-title"><div class="container">
      {section_head("Our services", "Find the support<br>you need.", "<p>An assignment can combine several services. We can discuss the scope and any specialist partners needed.</p>", "services-title")}
      <div class="service-list">{"".join(rows)}</div>
      <p class="section-more"><a class="text-link" href="projects.html">Explore all experience {arrow()}</a></p></div></section>'''
    render("services", "Services", "Feasibility studies, engineering design and installation, value chain and post-harvest studies, monitoring and evaluation, technology support, capacity strengthening, business development and policy review.", body)


def xp_feature(item, level):
    photo = FEATURES[item["id"]]
    media = f'<div class="xp-feature-media">{picture(photo, sizes="(max-width: 760px) calc(100vw - 40px), (max-width: 1100px) 50vw, 680px")}</div>' if photo else ""
    return f'''<article class="xp-feature{"" if photo else " no-media"}" id="{esc(item["id"])}">{media}<div class="xp-feature-body">
      <h{level}>{esc(item["title"])}</h{level}><p>{esc(item["description"])}</p>{highlights(item)}</div></article>'''


def xp_ledger(items, level):
    rows = "".join(f'<li id="{esc(item["id"])}"><h{level}>{esc(item["title"])}</h{level}><p>{esc(item["description"])}</p></li>' for item in items if item["id"] not in FEATURES)
    return f'<ul class="xp-ledger" role="list">{rows}</ul>' if rows else ""


def xp_panel(category, items, following=None):
    group_id, _, _, icon_name = GROUPS[category]
    count = f'{len(items)} assignment{"" if len(items) == 1 else "s"}'
    features = "".join(xp_feature(item, 4) for item in items if item["id"] in FEATURES)
    next_link = ""
    if following:
        next_category, next_count = following
        next_link = f'''<a class="xp-next" href="#{GROUPS[next_category][0]}"><span class="xp-next-label">Next practice</span>
      <span class="xp-next-title">{esc(next_category)}</span><span class="xp-next-count">{next_count} assignments</span>{arrow()}</a>'''
    return f'''<section class="xp-panel" id="{group_id}" aria-labelledby="{group_id}-title">
      <div class="xp-head"><span class="card-icon">{icon(icon_name)}</span><h3 id="{group_id}-title">{esc(category)}</h3><span class="xp-count">{count}</span></div>
      {features}{xp_ledger(items, 4)}{next_link}</section>'''


def projects():
    by_track = {track: [p for p in DATA["projects"] if p["track"] == track] for track in ATTRIBUTION}
    categories = list(dict.fromkeys(p["category"] for p in by_track["partner"]))
    groups = {category: [p for p in by_track["partner"] if p["category"] == category] for category in categories}
    tabs = "".join(f'''<button type="button" role="tab" id="tab-{GROUPS[c][0]}" aria-controls="{GROUPS[c][0]}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}">{GROUPS[c][1]} <span class="xp-tab-count">{len(groups[c])}<span class="visually-hidden"> assignments</span></span></button>''' for i, c in enumerate(categories))
    company = "".join(xp_feature(item, 3) for item in by_track["company"])
    panels = "".join(xp_panel(c, groups[c], (categories[i + 1], len(groups[categories[i + 1]])) if i + 1 < len(categories) else None) for i, c in enumerate(categories))
    body = page_hero("Experience", "Engineering in practice.<br>Enterprise in focus.", "Assignments undertaken through ASDARIA, and the directors' experience through other organisations and research institutions.")
    body += f'''<section class="section xp-part xp-company" id="company-assignments" aria-labelledby="company-title"><div class="container">
      {section_head("Through ASDARIA", "Company assignments", "<p>Undertaken directly through ASDARIA Ltd.</p>", "company-title")}{company}</div></section>
      <section class="section xp-part xp-directors" id="directors-assignments" aria-labelledby="directors-title"><div class="container">
      {section_head("Directors' experience", "Directors' assignments", "<p>Undertaken by the directors outside the company, through other firms and organisations.</p>", "directors-title")}</div>
      <p class="container xp-tabs-label" id="xp-tabs-label" hidden>Choose a practice area</p>
      <div class="xp-tabs-bar" hidden><div class="container xp-tabs" role="tablist" aria-labelledby="xp-tabs-label">{tabs}</div></div>
      <div class="container xp-panels">{panels}</div></section>
      <section class="section soft xp-part" id="directors-research" aria-labelledby="research-title"><div class="container">
      {section_head("Not through the company", "Directors' research", "<p>Research activities the directors have been involved in.</p>", "research-title")}{xp_ledger(by_track["research"], 3)}</div></section>'''
    render("projects", "Experience", "ASDARIA company assignments, and separately attributed assignments and research by its directors outside the company.", body)


def gallery():
    order = ["coffee-assessment", "climate-assessment", "food-hub", "bakery", "poultry-layout", "greenhouse-dryer", "capacity-building"]
    figures = []
    for name in order:
        width, height, label, _ = PHOTOS[name]
        shape = " is-portrait" if height > width else " is-wide" if width / height > 1.5 else ""
        sizes = "(max-width: 760px) calc(100vw - 40px), (max-width: 1100px) " + ("100vw" if shape == " is-wide" else "50vw") + ", 33vw"
        figures.append(f'<figure class="gallery-item{shape}" id="photo-{name}"><a class="gallery-open" href="assets/img/{name}.webp" data-caption="{esc(CAPTIONS[name])}" aria-label="Enlarge photograph: {esc(label)}">{picture(name, sizes=sizes)}</a><figcaption>{CAPTIONS[name]}</figcaption></figure>')
    body = page_hero("Gallery", "People, projects<br>and practical engineering.", "Photographs from work undertaken through ASDARIA or individually by its directors.")
    body += f'''<section class="section"><div class="container"><div class="gallery-grid">{"".join(figures)}</div></div></section>
      <dialog class="image-dialog" aria-label="Enlarged photograph"><div class="dialog-bar"><p class="dialog-count"></p><button type="button" class="dialog-close" aria-label="Close">{control_icon("M6 6l12 12M18 6 6 18")}</button></div>
      <img alt=""><div class="dialog-foot"><p class="dialog-caption" aria-live="polite"></p><div class="dialog-nav"><button type="button" class="dialog-prev" aria-label="Previous photograph">{control_icon("m15 5-7 7 7 7")}</button><button type="button" class="dialog-next" aria-label="Next photograph">{control_icon("m9 5 7 7-7 7")}</button></div></div></dialog>'''
    render("gallery", "Gallery", "Field photographs of agricultural engineering, coffee infrastructure, food processing, drying technology and capacity building.", body)


def contact():
    options = [service["title"] for service in DATA["services"]] + ["Research collaboration", "Other"]
    interest_options = "".join(f"<option>{esc(option)}</option>" for option in options)
    body = page_hero("Contact", "Talk to us about<br>your project.", "A feasibility question, an engineering design, a processing investment or a research collaboration. Tell us what you have in mind.", modifier=" compact")
    body += f'''<section class="section contact-section"><div class="container contact-grid">
      <div class="contact-details"><h2>Speak to us directly.</h2>
      <dl class="contact-list"><div><dt>Phone</dt><dd>{contact_link("phone")}</dd></div><div><dt>Email</dt><dd>{contact_link("email")}</dd></div><div><dt>Postal address</dt><dd>P.O. Box 3736, 01002<br>Thika, Kenya</dd></div></dl></div>
      <div class="brief-card"><h2>Send a project brief.</h2>
      <p>Share the location, the question you need answered and the support you are looking for. This form does not send messages: it opens a draft in your email app for you to review and send.</p>
      <form id="brief-form" hidden><div class="field-row"><div class="field"><label for="name">Your name *</label><input id="name" name="name" autocomplete="name" maxlength="160" required></div>
      <div class="field"><label for="organisation">Organisation</label><input id="organisation" name="organisation" autocomplete="organization" maxlength="200"></div></div>
      <div class="field"><label for="interest">Area of interest</label><select id="interest" name="interest">{interest_options}</select></div>
      <div class="field"><label for="message">Your project *</label><textarea id="message" name="message" rows="6" minlength="20" maxlength="1500" placeholder="Location, the question you need answered, the support you need and your timeline." aria-describedby="message-hint" required></textarea><small id="message-hint">At least 20 characters. Avoid confidential information.</small></div>
      <button class="button primary" type="submit">Open email draft {arrow()}</button>
      <p class="fineprint">* Required. <a href="privacy.html">How the form handles your details</a>.</p></form>
      <noscript><p>Enable JavaScript to prepare an email draft, or call or email ASDARIA directly.</p></noscript>
      <div class="brief-result" hidden><h3>Your draft</h3><p>If your email app did not open, <a id="draft-link">try again</a> or copy this text into an email to {EMAIL}.</p><pre id="brief-output" tabindex="0"></pre><button type="button" id="copy-brief" class="button secondary">Copy text</button></div>
      <p id="brief-status" role="status" aria-live="polite"></p></div></div></section>'''
    render("contact", "Contact", f"Call ASDARIA on {PHONE} or email {EMAIL} to discuss feasibility, engineering design, studies or business advisory.", body)


def privacy():
    body = page_hero("Privacy", "A simple site.<br>A clear data policy.", "No advertising, analytics or online enquiry service is included in this website.")
    body += f'''<section class="section"><div class="container prose">
      <h2>Project brief form</h2><p>The form on the contact page does not send or store your details. When you choose Open email draft, your browser passes them to your email app as a draft addressed to {EMAIL}. You decide whether to send it. Your browser may remember form entries through its own autofill features.</p>
      <h2>Calls and email</h2><p>Telephone links open your device's calling app. Email you send to ASDARIA is handled by your email provider and by Gmail.</p>
      <h2>Site delivery</h2><p>This website does not use cookies, analytics, advertising, third-party fonts, tracking scripts or embedded external content. The hosting service may keep technical access logs, such as IP addresses and browser details, to deliver and secure the site.</p>
      <h2>Questions</h2><p>Call <a href="tel:{PHONE}">{PHONE}</a> or email <a href="mailto:{EMAIL}">{EMAIL}</a> with any questions about this site.</p></div></section>'''
    render("privacy", "Privacy", "How the ASDARIA website handles the project brief form, calls, email and site delivery.", body)


def not_found():
    body = page_hero("404 / Page not found", "Let's get you<br>back on track.", "The page may have moved, or the address may be incomplete.")
    body += f'<section class="section"><div class="container actions"><a class="button primary" href="index.html">Back to home {arrow()}</a><a class="text-link" href="services.html">Explore our services {arrow()}</a></div></section>'
    render("404", "Page not found", "This page could not be found. Return to ASDARIA's homepage or explore our services.", body)


def discovery_files():
    slugs = sorted((path.stem for path in SITE.glob("*.html") if path.stem != "404"), key=lambda slug: (slug != "index", slug))
    urls = "".join(f"  <url><loc>{page_url(slug)}</loc></url>\n" for slug in slugs)
    (SITE / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")


def main():
    SITE.mkdir(exist_ok=True)
    home()
    about()
    services()
    projects()
    gallery()
    contact()
    privacy()
    not_found()
    discovery_files()
    print(f"Built 8 pages, sitemap.xml and robots.txt in {SITE}")


if __name__ == "__main__":
    main()
