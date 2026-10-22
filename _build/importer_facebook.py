"""Convertit des textes de publications Facebook en articles du blog.

Usage : python3 _build/importer_facebook.py <dossier_textes> <meta.py>
Chaque texte : 1re ligne = titre, 2e ligne = chapô, puis le corps.
  « ## Intertitre »  -> intertitre
  « – élément »      -> liste
  « @legende texte » -> légende de la photo
  « @payhip label|titre|description|lien » -> encart en fin d'article
"""
import os, re, sys, json, html, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FB = "https://www.facebook.com/lusitanie"


def charger_meta(chemin):
    spec = importlib.util.spec_from_file_location("meta", chemin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.M, mod.P


def esc(s):
    return html.escape(s, quote=False)


def premiere_phrase(texte):
    m = re.match(r"(.+?[.!?])\s+(.*)", texte, re.S)
    return (m.group(1), m.group(2)) if m else (texte, "")


def convertir(texte):
    lignes = [l.strip() for l in texte.strip().split("\n") if l.strip()]
    titre, chapo, reste = lignes[0], lignes[1], lignes[2:]
    corps_debut = []
    if len(chapo) > 320:  # chapô trop long : on garde la 1re phrase, le reste ouvre le corps
        chapo, suite = premiere_phrase(chapo)
        if suite:
            corps_debut.append(suite)
    legende, asides, blocs, liste = "", [], [], []

    def fermer_liste():
        if liste:
            blocs.append("<ul>" + "".join(f"<li>{esc(x)}</li>" for x in liste) + "</ul>")
            liste.clear()

    for l in corps_debut + reste:
        if l.startswith("@legende "):
            legende = l[9:].strip()
        elif l.startswith("@payhip "):
            lab, ti, de, href = [x.strip() for x in l[8:].split("|")]
            asides.append(dict(label=lab, title=ti, desc=esc(de), href=href, button="Écouter", image=""))
        elif l.startswith("## "):
            fermer_liste(); blocs.append(f"<h2>{esc(l[3:])}</h2>")
        elif re.match(r"^[–-]\s", l):
            liste.append(l[2:].strip())
        else:
            fermer_liste(); blocs.append(f"<p>{esc(l)}</p>")
    fermer_liste()
    return titre, chapo, "\n".join(blocs), legende, asides


def main(dossier, meta_path):
    M, P = charger_meta(meta_path)
    for ident, (slug, rubrique, date, pfbid) in M.items():
        texte = open(os.path.join(dossier, f"{ident}.txt"), encoding="utf-8").read()
        titre, chapo, corps, legende, asides = convertir(texte)
        extrait = chapo if len(chapo) <= 200 else chapo[:197].rsplit(" ", 1)[0] + "…"
        meta = dict(
            slug=slug, title=titre, kicker="", deck=esc(chapo), rubrique=rubrique, cat="",
            excerpt=extrait, description=extrait,
            image=f"images/{slug}.jpg", image_alt=titre,
            legende=legende, date=date, source="facebook",
            facebook_url=(P + pfbid) if pfbid else FB, asides=asides, featured=False,
        )
        out = "<!--META\n" + json.dumps(meta, ensure_ascii=False, indent=1) + "\nMETA-->\n" + corps + "\n"
        open(os.path.join(ROOT, "_articles", f"{slug}.html"), "w", encoding="utf-8").write(out)
        print(f"{slug}: {titre[:60]}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
