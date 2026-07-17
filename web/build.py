#!/usr/bin/env python3
"""Build de "El Senado y la Tierra".

Inyecta los datasets en el template y genera:
  - web/index.html    (documento completo, para GitHub Pages / hosting propio)
  - web/artifact.html (solo contenido, para publicar como Artifact de claude.ai)

Assertions de seguridad: ninguna secuencia `</script` puede quedar viva dentro
de los payloads JSON inyectados.
"""
import json
import pathlib
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = BASE / "web" / "template.html"
OUT_FULL = BASE / "web" / "index.html"
OUT_ARTIFACT = BASE / "web" / "artifact.html"


def payload(path: pathlib.Path) -> str:
    data = json.loads(path.read_text())
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def main() -> None:
    template = TEMPLATE.read_text()
    senadores = payload(BASE / "data" / "senadores-web.json")
    estado = payload(BASE / "data" / "estado-votacion.json")

    if "__DATA__" not in template or "__ESTADO__" not in template:
        sys.exit("ERROR: faltan placeholders __DATA__/__ESTADO__ en el template")

    contenido = template.replace("__DATA__", senadores).replace("__ESTADO__", estado)

    # El title/meta del tope del template son para el Artifact (le dan nombre).
    # En el documento completo van en <head>, así que acá los sacamos del body.
    contenido_body = "\n".join(
        linea
        for linea in contenido.splitlines()
        if not linea.startswith("<title>") and not linea.startswith('<meta name="description"')
    )

    for nombre, blob in (("senadores", senadores), ("estado", estado)):
        if "</script" in blob.lower():
            sys.exit(f"ERROR: '</script' sin escapar en payload {nombre}")

    OUT_ARTIFACT.write_text(contenido)

    og_desc = (
        "No se votó el 16/7 — vuelve al Senado el 6 de agosto. Encontrá a tus "
        "senadores, mirá la postura de su bloque y escribiles en un click: el "
        "mail sale pre-armado."
    )
    canonical = "https://0xdwb.is-a.dev/senadores/"
    favicon = (
        "data:image/svg+xml,"
        "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
        "%3Crect width='32' height='32' fill='%2314212E'/%3E"
        "%3Ccircle cx='16' cy='16' r='6' fill='none' stroke='%23C99C33' stroke-width='2'/%3E"
        "%3Cg stroke='%23C99C33' stroke-width='1.6'%3E"
        "%3Cpath d='M16 2v6M16 24v6M2 16h6M24 16h6M6 6l4 4M22 22l4 4M26 6l-4 4M10 22l-4 4'/%3E"
        "%3C/g%3E%3C/svg%3E"
    )
    # Config opcional (no versionada como requisito): claves para SEO/analytics.
    #   data/config.json → {"google_verification": "...", "goatcounter": "codigo-sitio"}
    config_path = BASE / "data" / "config.json"
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    extra_head = ""
    if config.get("google_verification"):
        extra_head += f'<meta name="google-site-verification" content="{config["google_verification"]}">\n'
    if config.get("goatcounter"):
        extra_head += (
            f'<script data-goatcounter="https://{config["goatcounter"]}.goatcounter.com/count" '
            'async src="https://gc.zgo.at/count.js"></script>\n'
        )
    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "El Senado y la Tierra",
        "url": canonical,
        "inLanguage": "es-AR",
        "description": og_desc,
    }, ensure_ascii=False)
    extra_head += f'<script type="application/ld+json">{json_ld}</script>\n'

    full = (
        '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>El Senado y la Tierra — 72 senadores, una votación</title>\n"
        f'<meta name="description" content="{og_desc}">\n'
        f'<link rel="canonical" href="{canonical}">\n'
        f'<link rel="icon" href="{favicon}">\n'
        '<meta name="theme-color" content="#14212E">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:title" content="El Senado y la Tierra — 72 senadores, una votación">\n'
        f'<meta property="og:description" content="{og_desc}">\n'
        f'<meta property="og:url" content="{canonical}">\n'
        f'<meta property="og:image" content="{canonical}og-image.png">\n'
        '<meta property="og:image:width" content="1200">\n'
        '<meta property="og:image:height" content="630">\n'
        '<meta property="og:locale" content="es_AR">\n'
        '<meta property="og:site_name" content="El Senado y la Tierra">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:image" content="{canonical}og-image.png">\n'
        + extra_head +
        "</head>\n<body>\n" + contenido_body + "\n</body>\n</html>\n"
    )
    OUT_FULL.write_text(full)

    prerender_perfiles(json.loads((BASE / "data" / "senadores-web.json").read_text()))

    kb_full = len(full.encode()) / 1024
    print(f"OK · artifact.html {len(contenido.encode())/1024:.0f}KB · index.html {kb_full:.0f}KB (budget 200KB)")
    if kb_full > 200:
        sys.exit("ERROR: se pasó del budget de 200KB")


CANONICAL = "https://0xdwb.is-a.dev/senadores/"


def prerender_perfiles(senadores: list) -> None:
    """72 mini-páginas s/<slug>.html con OG propia (nombre + tarjeta con foto).

    Los crawlers de WhatsApp/X nunca ven el fragment #/senador/x, así que las
    URLs que se comparten desde un perfil apuntan acá; la página redirige a la
    SPA al instante. También genera sitemap.xml y robots.txt.
    """
    import html

    s_dir = BASE / "s"
    s_dir.mkdir(exist_ok=True)
    urls = [CANONICAL]
    for s in senadores:
        slug = s["slug"]
        cargo = "Senadora nacional" if s["genero"] == "F" else "Senador nacional"
        titulo = html.escape(f"{s['apellido']}, {s['nombre']} — {cargo} por {s['provincia']}")
        desc = html.escape(
            f"{s['posturaLabel']} frente a la Ley de Tierras, que vuelve al Senado "
            "el 6 de agosto. Escribile en un click: el mail sale pre-armado."
        )
        hash_url = f"{CANONICAL}#/senador/{slug}"
        persona = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": f"{s['nombre']} {s['apellido']}",
            "jobTitle": cargo,
            "worksFor": {"@type": "Organization", "name": "Honorable Senado de la Nación Argentina"},
            "workLocation": {"@type": "Place", "name": s["provincia"] + ", Argentina"},
            "image": f"{CANONICAL}fotos/{slug}.jpg",
            "url": hash_url,
        }
        redes = [s.get(r) for r in ("tw", "ig", "fb") if s.get(r)]
        if redes:
            persona["sameAs"] = redes
        persona_ld = json.dumps(persona, ensure_ascii=False).replace("</", "<\\/")
        pagina = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{titulo}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta property="og:type" content="profile">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{CANONICAL}s/{slug}.html">
<meta property="og:image" content="{CANONICAL}og/{slug}.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="es_AR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{CANONICAL}og/{slug}.jpg">
<link rel="canonical" href="{hash_url}">
<script type="application/ld+json">{persona_ld}</script>
<meta http-equiv="refresh" content="0; url=../#/senador/{slug}">
<script>location.replace("../#/senador/{slug}");</script>
</head>
<body>
<p>Abriendo el perfil… <a href="../#/senador/{slug}">Ver el perfil de {titulo}</a></p>
</body>
</html>
"""
        (s_dir / f"{slug}.html").write_text(pagina)
        urls.append(f"{CANONICAL}s/{slug}.html")

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f"<url><loc>{u}</loc></url>" for u in urls]
    sitemap.append("</urlset>")
    (BASE / "sitemap.xml").write_text("\n".join(sitemap) + "\n")
    (BASE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {CANONICAL}sitemap.xml\n")
    print(f"prerender: {len(senadores)} perfiles en s/ · sitemap.xml · robots.txt")


if __name__ == "__main__":
    main()
