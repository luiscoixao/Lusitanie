"""Migration unique : extrait le contenu des anciennes pages vers _articles/<slug>.html"""
import re, json, glob, os, datetime
from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_articles"); os.makedirs(OUT, exist_ok=True)
SKIP = {"index.html","contact.html","mentions-legales.html","confidentialite.html","lusitanie-widget.html"}

# métadonnées des cartes de l'accueil
idx = BeautifulSoup(open(os.path.join(ROOT,"index.html")).read(), "html.parser")
cards = {}
for a in idx.select("a.article-card"):
    cards[a["href"]] = dict(
        rubrique=a.select_one(".card-rubrique").get_text(strip=True),
        cat=a.get("data-cat",""),
        card_title=a.select_one(".card-title").get_text(strip=True),
        excerpt=a.select_one(".card-excerpt").get_text(strip=True),
        image=(a.select_one("img") or {}).get("src",""))
hero = idx.select_one(".hero-feature a.read-link")
feature_slug = hero["href"] if hero else None

BOXES = ["fact-box","heteronyme-box","lieux","pratique","encart","actu-bloc","incontournable","artiste-box"]

def inner(tag):
    return "".join(str(c) for c in tag.contents).strip()

def normalize(soup_frag):
    for c in soup_frag.find_all(string=lambda t: isinstance(t, Comment)): c.extract()
    for t in soup_frag.select(".byline"): t.decompose()
    for t in soup_frag.select(".ornament, .separateur"):
        t.replace_with(BeautifulSoup('<hr>', "html.parser"))
    for t in soup_frag.select(".two-col"):
        for d in t.find_all("div", recursive=False): d.unwrap()
        t.unwrap()
    for cls in BOXES:
        for t in soup_frag.select("."+cls):
            lab = t.select_one("[class$='-label']")
            label = lab.get_text(strip=True).lstrip("✦📋📍🎵 ").strip() if lab else ""
            if lab: lab.decompose()
            txt = t.select_one(".actu-text")
            if txt: txt.name = "p"; del txt["class"]
            new = BeautifulSoup(f'<aside class="encadre">{"<p class=encadre-label>"+label+"</p>" if label else ""}{inner(t)}</aside>', "html.parser")
            t.replace_with(new)
    for t in soup_frag.select(".pull-quote"):
        attr = t.select_one(".pull-quote-attr")
        a = attr.get_text(strip=True).lstrip("— ").strip() if attr else ""
        if attr: attr.decompose()
        body = inner(t)
        if not body.startswith("<p"): body = "<p>"+body+"</p>"
        t.replace_with(BeautifulSoup(f'<blockquote class="citation">{body}{"<cite>"+a+"</cite>" if a else ""}</blockquote>', "html.parser"))
    for t in soup_frag.select(".img-inline"):
        img = t.find("img"); cap = t.select_one(".img-caption")
        c = cap.get_text(strip=True) if cap else ""
        t.replace_with(BeautifulSoup(f'<figure><img src="{img["src"]}" alt="{img.get("alt","")}" loading="lazy">{"<figcaption>"+c+"</figcaption>" if c else ""}</figure>', "html.parser"))
    for t in soup_frag.select(".video-bloc"):
        ifr = t.find("iframe"); cap = t.select_one(".video-caption")
        c = cap.get_text(strip=True) if cap else ""
        t.replace_with(BeautifulSoup(f'<figure class="video"><div class="video-ratio">{ifr}</div>{"<figcaption>"+c+"</figcaption>" if c else ""}</figure>', "html.parser"))
    for t in soup_frag.select(".jour-header"):
        n = t.select_one(".jour-number"); ti = t.select_one(".jour-title")
        t.replace_with(BeautifulSoup(f'<div class="partie"><span>{n.get_text(strip=True)}</span><h2>{inner(ti)}</h2></div>', "html.parser"))
    for t in soup_frag.select(".final, .conclusion"):
        t.name = "div"; t["class"] = "conclusion"
    for t in soup_frag.select(".dedicace"):
        t.name = "p"; t["class"] = "dedicace"
    for t in soup_frag.select(".chiffre-box"): t["class"] = "chiffres"
    for t in soup_frag.select(".chiffre-item-number"): t["class"] = "chiffre"
    for t in soup_frag.select(".chiffre-item-label"): t["class"] = "chiffre-label"
    for t in soup_frag.select("[style]"): del t["style"]
    for img in soup_frag.find_all("img"): img["loading"] = "lazy"
    return soup_frag

def payhip(div):
    lab = div.select_one(".payhip-label"); ti = div.select_one(".payhip-title")
    de = div.select_one(".payhip-desc"); bt = div.select_one(".payhip-btn")
    img = div.find("img")
    return dict(label=lab.get_text(strip=True).lstrip("✦ ").strip() if lab else "",
                title=ti.get_text(strip=True) if ti else "", desc=inner(de) if de else "",
                href=bt["href"] if bt else "", button=bt.get_text(strip=True).rstrip("→ ").strip() if bt else "",
                image=img["src"] if img else "")

for path in sorted(glob.glob(os.path.join(ROOT,"*.html"))):
    fn = os.path.basename(path)
    if fn in SKIP: continue
    raw = open(path).read()
    soup = BeautifulSoup(raw, "html.parser")
    body = soup.body
    m = {}
    m["slug"] = fn[:-5]
    m["description"] = (soup.find("meta", attrs={"name":"description"}) or {}).get("content","")
    m["seo_title"] = soup.title.get_text(strip=True)
    hero = soup.select_one("section.hero") or soup.select_one(".hero-fado")
    h1 = hero.find("h1")
    for br in h1.find_all("br"): br.replace_with(" ")
    m["title_html"] = re.sub(r"\s+"," ",inner(h1))
    m["title"] = re.sub(r"\s+"," ",h1.get_text()).strip()
    if cards.get(fn,{}).get("card_title"): m["title"] = cards[fn]["card_title"].replace("d ubiquite","d'ubiquité")
    k = hero.select_one(".hero-kicker"); m["kicker"] = k.get_text(strip=True) if k else ""
    d = hero.select_one(".hero-deck"); m["deck"] = re.sub(r"\s+"," ",inner(d)) if d else ""
    rub = soup.select_one(".rubrique-label")
    card = cards.get(fn, {})
    m["rubrique"] = card.get("rubrique") or (rub.get_text(strip=True).split("·")[0].strip() if rub else "Culture")
    m["cat"] = card.get("cat","culture")
    m["excerpt"] = card.get("excerpt") or re.sub("<[^>]+>","",m["deck"])
    img = None
    for i in body.find_all("img"):
        if "cloudinary" in i.get("src","") or "youtube" in i.get("src",""):
            img = i; break
    m["image"] = card.get("image") or (img["src"] if img else "")
    m["image_alt"] = img.get("alt","") if img else m["title"]
    if not m["image"] and fn=="o-emigrante.html": m["image"]="https://img.youtube.com/vi/RBi06wdsvXU/maxresdefault.jpg"
    v = re.search(r"/v(\d{10})/", m["image"])
    m["date"] = datetime.date.fromtimestamp(int(v.group(1))).isoformat() if v else "2026-05-15"
    pg = soup.select_one(".pull-giant")
    if pg:
        t = pg.select_one(".pull-giant-text"); a = pg.select_one(".pull-giant-attr")
        m["epigraph"] = dict(text=re.sub(r"\s+"," ",inner(t)), attr=a.get_text(strip=True).lstrip("— ").strip() if a else "")
    m["featured"] = (fn == feature_slug)
    m["source"] = "blog"
    # contenu : tout ce qui suit le hero (ou pull-giant) jusqu'au footer
    start = pg or hero
    parts, asides = [], []
    for sib in start.find_next_siblings():
        if sib.name == "footer": break
        if "payhip-bloc" in (sib.get("class") or []):
            asides.append(payhip(sib)); continue
        if sib.name == "script": continue
        parts.append(sib)
    html = ""
    for p in parts:
        frag = BeautifulSoup(str(p), "html.parser")
        top = frag.find()
        if top and "article-body" in (top.get("class") or []):
            top.unwrap()
        html += str(normalize(frag))
    for p in body.select(".payhip-bloc"):
        if p not in [None] and payhip(p) not in asides: asides.append(payhip(p))
    m["asides"] = asides
    html = re.sub(r"\n\s*\n+", "\n", html).strip()
    html = re.sub(r"(<hr/?>\s*)+$", "", html)
    html = re.sub(r"^(<hr/?>\s*)+", "", html)
    out = "<!--META\n" + json.dumps(m, ensure_ascii=False, indent=1) + "\nMETA-->\n" + html + "\n"
    open(os.path.join(OUT, fn), "w").write(out)
    print(fn, m["date"], m["rubrique"], "|", m["title"][:50], "| asides", len(asides))
