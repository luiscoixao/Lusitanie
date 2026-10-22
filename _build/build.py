"""Génère le site lusitanie.blog à partir de _articles/ et _pages/.

Usage : python3 _build/build.py
Chaque article est un fichier _articles/<slug>.html : un bloc <!--META {json} META-->
suivi du corps HTML. Le script réécrit les pages .html à la racine, l'accueil,
les pages rubriques et le sitemap.
"""
import os, re, json, html, datetime, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://lusitanie.blog"

RUBRIQUES = [  # (slug, libellé)
    ("culture", "Culture"), ("histoire", "Histoire"), ("musique", "Musique"),
    ("voyage", "Voyage"), ("diaspora", "Diaspora"),
]
SECTION_DE = {  # rubrique affichée -> section de navigation
    "culture": "culture", "cinéma": "culture", "langue": "culture", "langue portugaise": "culture", "architecture": "culture", "bande dessinée": "culture", "philosophie": "culture", "littérature": "culture",
    "histoire": "histoire", "patrimoine": "histoire",
    "musique": "musique", "fado": "musique",
    "voyage": "voyage", "carnet de voyage": "voyage",
    "diaspora": "diaspora", "société": "diaspora",
    "football": "football", "sport": "football",
}
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]

HEAD_TRACKING = """<!-- Google Analytics GA4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-0E4SEHN0TT"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag("js", new Date());
  gtag("config", "G-0E4SEHN0TT");
</script>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({"gtm.start":
new Date().getTime(),event:"gtm.js"});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!="dataLayer"?"&l="+l:"";j.async=true;j.src=
"https://www.googletagmanager.com/gtm.js?id="+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,"script","dataLayer","GTM-KBSPNMDP");</script>
<!-- Google AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6217390274263347" crossorigin="anonymous"></script>"""
BODY_TRACKING = """<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-KBSPNMDP" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>"""

LIENS = [("Facebook", "https://facebook.com/lusitanie"),
         ("Instagram", "https://instagram.com/lusitanie.insta"),
         ("Boutique", "https://payhip.com/Lusitanie")]


def esc(s):
    return html.escape(s or "", quote=True)


def date_fr(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day}{'er' if d.day == 1 else ''} {MOIS[d.month - 1]} {d.year}"


def section(a):
    return SECTION_DE.get(a["rubrique"].lower(), a.get("cat") or "culture")


def lecture(corps):
    mots = len(re.sub(r"<[^>]+>", " ", corps).split())
    return max(1, math.ceil(mots / 230))


# Boutique Payhip affichée en bas de chaque page : (id produit, titre, type, prix, couverture)
BOUTIQUE = [
    ("ubEdI", "Les oubliés de la Lys — Le Portugal dans la Grande Guerre", "Récit audio", "2,00", "ubEdI"),
    ("tFoJq", "L'épopée maritime portugaise", "Livre audio", "3,99", "tFoJq"),
    ("lDFO7", "Les Bidonvilles portugais", "Livre audio", "3,99", "lDFO7"),
    ("b4rSg", "L'Immigration portugaise en France", "Récit audio", "1,99", "b4rSg"),
    ("YPtSq", "As Mães Corajosas da Imigração Portuguesa", "Récit audio", "2,00", "YPtSq"),
    ("VQ5P1", "Les mères courage de l'immigration portugaise", "Livre audio", "2,00", "VQ5P1"),
    ("pkMNA", "L'Écusson de l'équipe du Portugal", "Récit audio", "2,00", "pkMNA"),
    ("HVo5F", "Les Pères de l'immigration portugaise", "Récit audio", "2,00", "HVo5F"),
    ("B38YI", "La Saudade", "Chanson", "1,00", "B38YI"),
    ("JHYld", "Le Fado", "Chanson", "1,00", "JHYld"),
    ("LQEXG", "Nos parents, ces héros", "Chanson", "1,00", "LQEXG"),
    ("w6Ouy", "Fado", "Chanson", "1,00", "w6Ouy"),
    ("70RZb", "L'immigration portugaise : mémoire d'exils, transmission d'un héritage et saudade", "Récit audio", "2,00", "70RZb"),
    ("EDZFs", "La Gare", "Récit audio", "2,00", "EDZFs"),
    ("pmnuA", "Portugal — Là où finit la terre, là où commence l'horizon", "Livre audio", "10,00", "pmnuA"),
    ("pR94y", "Saudade", "Récit audio", "2,00", "pR94y"),
    ("3Vsu9", "De Lisbonne à Paris", "Chanson", "1,00", "3Vsu9"),
    ("iZdLM", "25 Avril", "Chanson", "1,00", "iZdLM"),
    ("6YWyV", "Portugal — Là où finit la terre, là où commence l'horizon", "Ebook", "7,00", "6YWyV"),
    ("s6gvM", "Portugal — Là où finit la terre, là où commence l'horizon", "Récit audio", "2,00", "pmnuA"),
]


def boutique():
    cartes = "".join(
        f'<li><a href="https://payhip.com/b/{i}" target="_blank" rel="noopener">'
        f'<img src="images/boutique/{c}.jpg" alt="" loading="lazy" width="500" height="833">'
        f'<span class="b-type">{esc(t)}</span><span class="b-titre">{esc(n)}</span>'
        f'<span class="b-prix">{p} €</span></a></li>'
        for i, n, t, p, c in BOUTIQUE)
    return f"""<section class="boutique" aria-labelledby="boutique-titre"><div class="wrap">
  <div class="boutique-tete"><h2 class="titre-section" id="boutique-titre">La boutique Lusitanie</h2>
  <a class="boutique-tout" href="https://payhip.com/Lusitanie" target="_blank" rel="noopener">Tout le catalogue →</a></div>
  <p class="boutique-intro">Livres audio, récits et chansons, à télécharger.</p>
  <ul class="boutique-bande">{cartes}</ul>
</div></section>"""


CSS_VERSION = __import__("hashlib").md5(open(os.path.join(ROOT, "assets", "lusitanie.css"), "rb").read()).hexdigest()[:8]


def ld_json(donnees):
    """Bloc de données structurées schema.org (JSON-LD)."""
    if not donnees:
        return ""
    txt = json.dumps(donnees, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return f'\n<script type="application/ld+json">\n{txt}\n</script>'


EDITEUR = {"@type": "Organization", "name": "Lusitanie", "url": f"{SITE}/",
           "sameAs": ["https://www.facebook.com/lusitanie", "https://www.instagram.com/lusitanie.insta"]}


def ld_article(a, url):
    img = a.get("image") or ""
    if img and not img.startswith("http"):
        img = f"{SITE}/{img}"
    sec = section(a)
    libelle = dict(RUBRIQUES).get(sec, a["rubrique"])
    article = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": a["title"][:110],
        "description": a.get("description") or a["excerpt"],
        "datePublished": a["date"], "dateModified": a.get("maj") or a["date"],
        "inLanguage": "fr", "articleSection": a["rubrique"],
        "mainEntityOfPage": url, "url": url,
        "author": EDITEUR, "publisher": EDITEUR,
    }
    if img:
        article["image"] = [img]
    fil = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": libelle, "item": f"{SITE}/rubrique-{sec}.html"},
        {"@type": "ListItem", "position": 3, "name": a["title"], "item": url}]}
    return [article, fil]


def page(titre, description, contenu, *, canonical, image=None, courant=None, type_og="website", donnees=None):
    if image and not image.startswith("http"):
        image = f"{SITE}/{image}"
    og_img = f'\n<meta property="og:image" content="{esc(image)}">' if image else ""
    nav = "".join(
        f'<li><a href="rubrique-{s}.html"{" aria-current=\"page\"" if s == courant else ""}>{l}</a></li>'
        for s, l in RUBRIQUES)
    liens = "".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in LIENS)
    aujourd_hui = date_fr(datetime.date.today().isoformat())
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
{HEAD_TRACKING}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titre)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(titre)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="{type_og}">
<meta property="og:site_name" content="Lusitanie">
<meta property="og:url" content="{canonical}">{og_img}
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,400..800;1,14..32,400..600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/lusitanie.css?v={CSS_VERSION}">{ld_json(donnees)}
</head>
<body>
{BODY_TRACKING}
<div class="barre"><div class="wrap"><span class="date">{aujourd_hui}</span><nav>{liens}</nav></div></div>
<header class="entete">
  <a class="logo" href="index.html">LUSITANIE</a>
  <p class="devise">Culture portugaise et lusophone</p>
  <nav class="rubriques" aria-label="Rubriques"><ul>{nav}</ul></nav>
</header>
<main>
{contenu}
</main>
{boutique()}
<footer class="pied"><div class="wrap">
  <div><a class="logo" href="index.html">LUSITANIE</a><p>Culture portugaise et lusophone.</p></div>
  <nav>{liens}<a href="a-propos.html">À propos</a><a href="contact.html">Contact</a><a href="mentions-legales.html">Mentions légales</a><a href="confidentialite.html">Confidentialité</a></nav>
</div></footer>
</body>
</html>
"""


def charger():
    arts = []
    d = os.path.join(ROOT, "_articles")
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".html"):
            continue
        raw = open(os.path.join(d, fn), encoding="utf-8").read()
        m = re.match(r"<!--META\n(.*?)\nMETA-->\n(.*)", raw, re.S)
        meta = json.loads(m.group(1))
        meta["corps"] = m.group(2)
        if meta.get("brouillon"):
            continue
        meta["section"] = section(meta)
        meta["libelle"] = dict(RUBRIQUES).get(meta["section"], meta["rubrique"])  # étiquette affichée = rubrique de navigation
        meta["minutes"] = lecture(meta["corps"])
        arts.append(meta)
    arts.sort(key=lambda a: a["date"], reverse=True)
    return arts


def vignette(img, w):
    """Image Cloudinary redimensionnée pour les cartes."""
    if "res.cloudinary.com" in img and "/upload/" in img:
        return img.replace("/upload/q_auto/f_auto/", "/upload/").replace("/upload/", f"/upload/c_fill,w_{w},ar_3:2,q_auto,f_auto/", 1)
    return img


def carte(a):
    entiere = " entiere" if a.get("image_entiere") else ""
    return f"""<a class="carte" href="{a['slug']}.html">
  <div class="carte-image{entiere}"><img src="{esc(vignette(a['image'], 720))}" alt="{esc(a.get('image_alt') or a['title'])}" loading="lazy"></div>
  <span class="surtitre">{esc(a['libelle'])}</span>
  <h3>{esc(a['title'])}</h3>
  <p>{esc(a['excerpt'])}</p>
  <div class="meta"><span>{date_fr(a['date'])}</span><span>{a['minutes']} min</span></div>
</a>"""


def ligne(a):
    return f"""<a href="{a['slug']}.html"><img class="{'entiere' if a.get('image_entiere') else ''}" src="{esc(vignette(a['image'], 300))}" alt="" loading="lazy"><div><span class="surtitre">{esc(a['libelle'])}</span><h3>{esc(a['title'])}</h3></div></a>"""


def titre_h1(a):
    th = a.get("title_html")
    if th and re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", th)).strip() == a["title"]:
        return th
    return esc(a["title"])


def article(a, tous):
    ep = a.get("epigraph")
    exergue = ""
    if ep and ep.get("text"):
        cite = f"<cite>{esc(ep['attr'])}</cite>" if ep.get("attr") else ""
        exergue = f'<blockquote class="exergue"><p>{ep["text"]}</p>{cite}</blockquote>'
    legende = f"<figcaption>{esc(a['legende'])}</figcaption>" if a.get("legende") else ""
    visuel = f'<figure class="article-visuel"><img src="{esc(a["image"])}" alt="{esc(a.get("image_alt") or a["title"])}">{legende}</figure>' if a.get("image") else ""
    encarts = ""
    for x in a.get("asides", []):
        externe = ' target="_blank" rel="noopener"' if x["href"].startswith("http") else ""
        encarts += f"""<aside class="encart-produit"><div><div><span class="surtitre">{esc(x['label'])}</span><h3>{esc(x['title'])}</h3><p>{x['desc']}</p></div><a class="bouton" href="{esc(x['href'])}"{externe}>{esc(x['button'] or 'Découvrir')}</a></div></aside>"""
    source = ""
    voisins = [b for b in tous if b["slug"] != a["slug"] and b["section"] == a["section"]]
    voisins += [b for b in tous if b["slug"] != a["slug"] and b not in voisins]
    suite = "".join(carte(b) for b in voisins[:3])
    contenu = f"""<article>
<header class="article-entete">
  <a class="surtitre" href="rubrique-{a['section']}.html">{esc(a['libelle'])}</a>
  <h1>{titre_h1(a)}</h1>
  <p class="chapo">{a['deck']}</p>
  <div class="meta"><span>La rédaction</span><span><time datetime="{a['date']}">{date_fr(a['date'])}</time></span><span>{a['minutes']} min de lecture</span></div>
</header>
{visuel}
{exergue}
<div class="corps">
{a['corps']}
</div>
{source}
{encarts}
</article>
<div class="wrap"><h2 class="titre-section">À lire aussi</h2><div class="grille">{suite}</div></div>"""
    titre = f"{a['title']} — Lusitanie"
    return page(titre, a.get("description") or a["excerpt"], contenu,
                canonical=f"{SITE}/{a['slug']}.html", image=a.get("image"),
                courant=a["section"], type_og="article",
                donnees=ld_article(a, f"{SITE}/{a['slug']}.html"))


def accueil(arts):
    une = next((a for a in arts if a.get("featured")), arts[0])
    reste = [a for a in arts if a is not une]
    contenu = f"""<div class="wrap">
<a class="une" href="{une['slug']}.html">
  <div class="une-image{' entiere' if une.get('image_entiere') else ''}"><img src="{esc(vignette(une['image'], 1200))}" alt="{esc(une.get('image_alt') or une['title'])}"></div>
  <div>
    <span class="surtitre">{esc(une['libelle'])}</span>
    <h2>{esc(une['title'])}</h2>
    <p>{esc(une['excerpt'])}</p>
    <div class="meta"><span>{date_fr(une['date'])}</span><span>{une['minutes']} min de lecture</span></div>
  </div>
</a>
<h2 class="titre-section">Derniers articles</h2>
<div class="grille">{''.join(carte(a) for a in reste[:9])}</div>
"""
    if len(reste) > 9:
        contenu += f"""<h2 class="titre-section">Toutes nos lectures</h2>
<div class="liste-compacte">{''.join(ligne(a) for a in reste[9:])}</div>
"""
    contenu += "</div>"
    return page("Lusitanie — Culture portugaise et lusophone",
                "Lusitanie : la culture portugaise et lusophone. Fado, littérature, histoire, voyage, diaspora, football.",
                contenu, canonical=f"{SITE}/", image=une.get("image"),
                donnees=[{"@context": "https://schema.org", "@type": "WebSite", "name": "Lusitanie",
                          "url": f"{SITE}/", "inLanguage": "fr"},
                         dict(EDITEUR, **{"@context": "https://schema.org"})])


def rubrique(slug, libelle, arts):
    liste = [a for a in arts if a["section"] == slug]
    corps = "".join(carte(a) for a in liste) or "<p>Aucun article pour le moment.</p>"
    contenu = f"""<div class="wrap">
<header class="intro-rubrique"><h1>{libelle}</h1></header>
<h2 class="titre-section">{len(liste)} article{'s' if len(liste) > 1 else ''}</h2>
<div class="grille">{corps}</div>
</div>"""
    return page(f"{libelle} — Lusitanie", f"Tous les articles {libelle.lower()} de Lusitanie.", contenu,
                canonical=f"{SITE}/rubrique-{slug}.html", courant=slug)


def pages_simples():
    d = os.path.join(ROOT, "_pages")
    for fn in sorted(os.listdir(d)):
        raw = open(os.path.join(d, fn), encoding="utf-8").read()
        m = re.match(r"<!--TITLE (.*?) -->\n(.*)", raw, re.S)
        titre, corps = m.group(1), m.group(2)
        yield fn, page(titre, titre, f'<div class="page">{corps}</div>', canonical=f"{SITE}/{fn}")


def sitemap(arts):
    urls = [(f"{SITE}/", datetime.date.today().isoformat(), "1.0")]
    urls += [(f"{SITE}/rubrique-{s}.html", datetime.date.today().isoformat(), "0.6") for s, _ in RUBRIQUES]
    urls += [(f"{SITE}/{a['slug']}.html", a.get("maj") or a["date"], "0.9") for a in arts]
    lignes = "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod><priority>{p}</priority></url>\n" for u, d, p in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{lignes}</urlset>\n'


def ecrire(nom, contenu):
    with open(os.path.join(ROOT, nom), "w", encoding="utf-8") as f:
        f.write(contenu)


def main():
    arts = charger()
    for a in arts:
        ecrire(f"{a['slug']}.html", article(a, arts))
    ecrire("index.html", accueil(arts))
    for s, l in RUBRIQUES:
        ecrire(f"rubrique-{s}.html", rubrique(s, l, arts))
    for fn, contenu in pages_simples():
        ecrire(fn, contenu)
    ecrire("sitemap.xml", sitemap(arts))
    print(f"{len(arts)} articles générés.")
    for s, l in RUBRIQUES:
        print(f"  {l}: {sum(1 for a in arts if a['section'] == s)}")


if __name__ == "__main__":
    main()
