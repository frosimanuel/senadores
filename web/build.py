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

    for nombre, blob in (("senadores", senadores), ("estado", estado)):
        if "</script" in blob.lower():
            sys.exit(f"ERROR: '</script' sin escapar en payload {nombre}")

    OUT_ARTIFACT.write_text(contenido)

    og_desc = (
        "Encontrá a tus senadores, mirá la postura de su bloque sobre la Ley de "
        "Tierras y escribiles en un click. Datos oficiales del Senado y del RNTR."
    )
    full = (
        '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="theme-color" content="#14212E">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:title" content="El Senado y la Tierra — 72 senadores, una votación">\n'
        f'<meta property="og:description" content="{og_desc}">\n'
        '<meta property="og:locale" content="es_AR">\n'
        '<meta name="twitter:card" content="summary">\n'
        "</head>\n<body>\n" + contenido + "\n</body>\n</html>\n"
    )
    OUT_FULL.write_text(full)

    kb_full = len(full.encode()) / 1024
    print(f"OK · artifact.html {len(contenido.encode())/1024:.0f}KB · index.html {kb_full:.0f}KB (budget 200KB)")
    if kb_full > 200:
        sys.exit("ERROR: se pasó del budget de 200KB")


if __name__ == "__main__":
    main()
