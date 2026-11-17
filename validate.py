"""Validate local links and content constraints without third-party packages."""

import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from build import FEATURES, GROUPS, ORGANISATIONS, PHOTOS, SITE_URL, asset_url, esc, page_url

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.links = []
        self.ids = set()
        self.headings = 0
        self.main = 0
        self.title = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate ID: {self.path.name}#{attrs['id']}"
            self.ids.add(attrs["id"])
        self.headings += tag == "h1"
        self.main += tag == "main"
        self.title += tag == "title"
        if tag == "img":
            assert "alt" in attrs, f"Missing image alt: {self.path.name}"
        for attr in ("href", "src"):
            if attrs.get(attr):
                self.links.append(attrs[attr])


def main():
    pages = {}
    for path in SITE.glob("*.html"):
        page = Page(path)
        content = path.read_text(encoding="utf-8")
        page.feed(content)
        assert page.headings == page.main == page.title == 1, f"Invalid landmarks: {path.name}"
        assert not re.search(r"[\u2013\u2014]", content), f"Forbidden dash in {path.name}"
        assert "eng.njugunas@gmail.com" not in content and "njuguna@asdaria.com" not in content
        assert 'href="mailto:asdaria.ltd@gmail.com"' in content
        assert "email to be confirmed" not in content.lower()
        assert "logo-" not in content
        assert '<html lang="en-KE" data-theme="light">' in content
        root = "/" if path.name == "404.html" else ""
        assert f'<link rel="stylesheet" href="{root}{asset_url("assets/style.css")}"><script src="{root}{asset_url("assets/main.js")}" defer></script>' in content, f"Stale asset versions in {path.name}: run build.py after editing site\\assets"
        assert '<meta name="color-scheme" content="light">' in content
        assert "prefers-color-scheme" not in content and "scoutTheme" not in content
        assert content.count('class="brand-mark"') == 1
        assert content.count(f'src="{root}assets/asdaria-logo.png"') == 1
        assert content.count('<span class="brand-name">ASDARIA</span>') == 1
        assert content.count('<span class="brand-descriptor">Agribzenergy Systems</span>') == 1
        assert "footer-nav" not in content and "footer-brand" not in content, f"Footer repeats the header: {path.name}"
        icon_links = 0 if path.name == "contact.html" else 2
        assert content.count('class="icon-link"') == icon_links, f"Footer contact icons: {path.name}"
        if icon_links:
            assert 'aria-label="Call +254733954103"' in content and 'aria-label="Email asdaria.ltd@gmail.com"' in content
        assert "P.O. Box 3736, 01002 Thika, Kenya" in content
        assert "200+" not in content or path.name == "projects.html"
        assert "hero-provenance" not in content and "Not an ASDARIA contract." not in content
        if path.name == "404.html":
            assert '<meta name="robots" content="noindex">' in content and 'rel="canonical"' not in content
        else:
            canonical = page_url(path.stem)
            assert content.count('rel="canonical"') == 1 and f'<link rel="canonical" href="{canonical}"><meta property="og:url" content="{canonical}">' in content, f"Canonical URL in {path.name}"
        assert f'<meta property="og:image" content="{SITE_URL}/assets/share.jpg">' in content
        pages[path.resolve()] = page
    assert len(pages) == 8
    assert (SITE / "assets" / "share.jpg").is_file()
    indexable = {page_url(path.stem) for path in pages if path.name != "404.html"}
    assert sorted(re.findall(r"<loc>([^<]+)</loc>", (SITE / "sitemap.xml").read_text(encoding="utf-8"))) == sorted(indexable), "sitemap.xml must list exactly the indexable pages"
    assert f"Sitemap: {SITE_URL}/sitemap.xml" in (SITE / "robots.txt").read_text(encoding="utf-8").splitlines(), "robots.txt must point to the sitemap"
    checked = 0
    for path, page in pages.items():
        for link in page.links:
            parsed = urlsplit(link)
            if parsed.scheme:
                if link.startswith(f"{SITE_URL}/"):
                    assert link == page_url(path.stem), f"Only the canonical link may use the absolute site address: {path.name}: {link}"
                    continue
                assert link in ("tel:+254733954103", "mailto:asdaria.ltd@gmail.com"), f"Unexpected external link: {link}"
                continue
            if parsed.path:
                # 404.html is served at any missing address, so it alone uses root paths, and uses them throughout.
                assert parsed.path.startswith("/") == (path.name == "404.html"), f"{'Folder-relative' if path.name == '404.html' else 'Root'} path in {path.name}: {link}"
                target = (SITE / unquote(parsed.path[1:]) if parsed.path.startswith("/") else path.parent / unquote(parsed.path)).resolve()
            else:
                target = path
            assert target.is_relative_to(SITE.resolve()), f"Link escapes public root: {link}"
            assert target.exists(), f"Broken link: {path.name}: {link}"
            if parsed.fragment:
                assert target in pages and unquote(parsed.fragment) in pages[target].ids, f"Missing fragment: {link}"
            checked += 1
    data = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
    assert len(data["projects"]) == 56
    assert all(p["track"] in ("company", "partner", "research") for p in data["projects"])
    assert sum(p["track"] == "company" for p in data["projects"]) == 1
    service_ids = {service["id"] for service in data["services"]}
    project_by_id = {project["id"]: project for project in data["projects"]}
    assert len(project_by_id) == len(data["projects"]), "Project anchors must be unique"
    for project in data["projects"]:
        assert project["services"] and set(project["services"]) <= service_ids
    for service in data["services"]:
        assert service["examples"], f"Missing related experience: {service['id']}"
        for project_id in service["examples"]:
            assert project_id in project_by_id, f"Unknown related assignment: {project_id}"
            assert service["id"] in project_by_id[project_id]["services"], f"Inconsistent service association: {project_id}"
    projects = (SITE / "projects.html").read_text(encoding="utf-8")
    assert projects.count('<article class="xp-feature') == len(FEATURES)
    for feature in FEATURES:
        assert re.search(rf'<article class="xp-feature[^"]*" id="{feature}">', projects), f"Missing feature: {feature}"
    for project in data["projects"]:
        if project["id"] in FEATURES:
            continue
        level = 3 if project["track"] == "research" else 4
        row = f'<li id="{project["id"]}"><h{level}>{esc(project["title"])}</h{level}><p>{esc(project["description"])}</p></li>'
        assert row in projects, f"Experience entry incomplete: {project['id']}"
    assert projects.count('<li id="') == len(data["projects"]) - len(FEATURES)
    assert projects.count('<ul class="xp-ledger" role="list">') == 7
    partner = [project for project in data["projects"] if project["track"] == "partner"]
    categories = list(dict.fromkeys(project["category"] for project in partner))
    tabs = re.findall(r'<button type="button" role="tab" id="tab-([a-z-]+)" aria-controls="([a-z-]+)" aria-selected="(true|false)" tabindex="(-?\d)">([^<]+) <span class="xp-tab-count">(\d+)<span class="visually-hidden"> assignments</span></span></button>', projects)
    assert [(tab[0], tab[1], tab[4], int(tab[5])) for tab in tabs] == [(GROUPS[c][0], GROUPS[c][0], GROUPS[c][1], sum(p["category"] == c for p in partner)) for c in categories], "Practice tabs do not match the data"
    assert [tab[2] for tab in tabs] == ["true"] + ["false"] * 5 and [tab[3] for tab in tabs] == ["0"] + ["-1"] * 5
    for category in categories:
        group_id = GROUPS[category][0]
        assert f'<section class="xp-panel" id="{group_id}" aria-labelledby="{group_id}-title">' in projects, f"Missing practice panel: {group_id}"
    assert projects.count('role="tablist"') == 1 and '<div class="xp-tabs-bar" hidden>' in projects
    assert '<p class="container xp-tabs-label" id="xp-tabs-label" hidden>Choose a practice area</p>' in projects and 'role="tablist" aria-labelledby="xp-tabs-label"' in projects
    next_links = re.findall(r'<a class="xp-next" href="#([a-z-]+)"><span class="xp-next-label">Next practice</span>\s*<span class="xp-next-title">([^<]+)</span><span class="xp-next-count">(\d+) assignments</span>', projects)
    assert [(link[0], html.unescape(link[1]), int(link[2])) for link in next_links] == [(GROUPS[c][0], c, sum(p["category"] == c for p in partner)) for c in categories[1:]], "Each practice except the last must link to the next one"
    assert projects.count('class="xp-count"') == 6
    experience_main = projects.split("<main", 1)[1].split("</main>", 1)[0]
    assert re.findall(r'<img src="assets/img/([a-z-]+)\.webp"', experience_main) == ["coffee-assessment", "food-hub"], "Experience shows only the coffee and Kalobeyei feature photographs"
    for removed in ("project-tools", "project-search", "service-filter", "data-filter", "technical-figure", "Illustrative scope diagram", "register", "expand-all", "<details", "entry", "<dialog", "xp-nav", "xp-grid", "xp-card", "xp-photo", "data-services"):
        assert removed not in projects, f"Removed experience UI remains: {removed}"
    services = (SITE / "services.html").read_text(encoding="utf-8")
    assert services.count('class="chain-photo"') == 4
    assert services.count('<nav class="service-index"') == 1 and len(re.findall(r'<li><a href="#[a-z]+"><span class="index">', services)) == len(data["services"])
    assert 'aria-labelledby="chain-heading"' in services
    assert "?service=" not in services
    assert 'id="afpq"' in projects
    home = (SITE / "index.html").read_text(encoding="utf-8")
    partner = [project for project in data["projects"] if project["track"] == "partner"]
    expected_counts = [sum(project["category"] == category for project in partner) for category in GROUPS]
    assert [int(n) for n in re.findall(r'<span class="index-count">(\d+)</span>', home)] == expected_counts and sum(expected_counts) == 48
    assert home.count('<article class="case') == 3 and home.count('<li class="pillar') == 3 and home.count('<li class="reason') == 3
    for project in data["projects"]:
        assert not re.search(r"\b(?:19|20)\d{2}\b", project["title"] + project["description"]), "Calendar year in project"
    contact = (SITE / "contact.html").read_text(encoding="utf-8")
    assert "does not send messages" in contact
    assert contact.count('href="mailto:asdaria.ltd@gmail.com"') == 1 and contact.count('href="tel:+254733954103"') == 1
    expected_images = {f"{name}.webp" for name in PHOTOS}
    expected_images |= {f"{name}-small.webp" for name, photo in PHOTOS.items() if photo[0] > 960}
    assert {p.name for p in (SITE / "assets" / "img").iterdir()} == expected_images
    gallery = (SITE / "gallery.html").read_text(encoding="utf-8")
    about = (SITE / "about.html").read_text(encoding="utf-8")
    for name in PHOTOS:
        if name.startswith("director-"):
            assert f'src="assets/img/{name}.webp"' in about
        else:
            assert f'id="photo-{name}"' in gallery
    assert gallery.count('class="gallery-open"') == 7 and gallery.count('<figure class="gallery-item') == 7
    assert gallery.count("is-portrait") == 2 and gallery.count("is-wide") == 1
    for control in ('aria-label="Close"', 'aria-label="Previous photograph"', 'aria-label="Next photograph"'):
        assert control in gallery
    assert "Open photograph" not in gallery and ">Close <" not in gallery
    assert 'id="organisations"' in about
    assert about.count('src="assets/organisations/') == len(ORGANISATIONS)
    assert about.count('<ul class="org-wall">') == 1 and "intro-media" not in about
    assert about.count('class="info-card"') == 6, "Expected four sector cards and two growth cards"
    assert sum(relationship == "company" for _, _, _, relationship in ORGANISATIONS) == 1
    assert {p.stem for p in (SITE / "assets" / "organisations").glob("*.webp")} == {slug for slug, _, _, _ in ORGANISATIONS}
    for image in (SITE / "assets" / "img").glob("*.webp"):
        raw = image.read_bytes()
        assert raw[:4] == b"RIFF" and raw[8:12] == b"WEBP"
    for name in ("asdaria-logo.png", "favicon.png"):
        assert (SITE / "assets" / name).read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    css = (SITE / "assets" / "style.css").read_text(encoding="utf-8")
    assert "color-scheme: dark" not in css and 'data-theme="dark"' not in css
    assert css.count("--cp-accent:") == 1
    blocks = {}
    for line in (SITE / "_headers").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line[0].isspace():
            rule = blocks.setdefault(line.strip(), [])
        elif line.strip():
            assert blocks and line.startswith("  "), f"Malformed _headers line: {line}"
            rule.append(tuple(part.strip() for part in line.split(":", 1)))
    share_rules = [rule for rule in blocks if rule != "/*"]
    assert list(blocks)[0] == "/*" and len(share_rules) == 1 and re.fullmatch(r"https://asdaria\.(pages\.dev|[a-z0-9-]+\.workers\.dev)/\*", share_rules[0]), "_headers holds the site-wide rule and one rule for the free Cloudflare share address"
    assert blocks[share_rules[0]] == [("X-Robots-Tag", "noindex")], "The share link must stay out of search results"
    expected_headers = blocks["/*"]
    assert all(key != "X-Robots-Tag" for key, _ in expected_headers), "The custom domain must stay indexable"
    firebase = json.loads((ROOT / "firebase.json").read_text(encoding="utf-8"))["hosting"]
    assert firebase["public"] == "site" and "_headers" in firebase["ignore"]
    assert [(h["key"], h["value"]) for h in firebase["headers"][0]["headers"]] == expected_headers and firebase["headers"][0]["source"] == "**", "firebase.json headers must match site/_headers"
    assert all(h["key"] != "X-Robots-Tag" for rule in firebase["headers"] for h in rule["headers"]), "Firebase serves the canonical address, so it must stay indexable"
    print(f"PASS: {len(pages)} pages, {checked} local references, 56 attributed assignments, contact and image constraints.")


if __name__ == "__main__":
    main()
