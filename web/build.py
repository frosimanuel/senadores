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
        "Encontrá a tus senadores, mirá la postura de su bloque sobre la Ley de "
        "Tierras y escribiles en un click. Datos oficiales del Senado y del RNTR."
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
        '<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:image" content="{canonical}og-image.png">\n'
        "</head>\n<body>\n" + contenido_body + "\n</body>\n</html>\n"
    )
    OUT_FULL.write_text(full)

    kb_full = len(full.encode()) / 1024
    print(f"OK · artifact.html {len(contenido.encode())/1024:.0f}KB · index.html {kb_full:.0f}KB (budget 200KB)")
    if kb_full > 200:
        sys.exit("ERROR: se pasó del budget de 200KB")


if __name__ == "__main__":
    main()
