# El Senado y la Tierra

**72 senadores deciden quién puede comprar la Argentina.** Sitio ciudadano independiente sobre la votación del proyecto de "Inviolabilidad de la Propiedad Privada" (capítulo tierras), que deroga los topes de la Ley de Tierras 26.737.

🔗 **Sitio:** https://0xdwb.is-a.dev/senadores/

## Qué hace

- Perfil de cada uno de los 72 senadores, con su foto oficial: provincia, bloque, postura del bloque frente al proyecto, contacto oficial y redes.
- Datos de extranjerización de tierras por provincia (RNTR, vía Chequeado).
- Botón para escribirle a cada senador por Gmail con un mail prellenado y editable.
- Modo campaña (`#/campania`): escribile a un grupo entero — tus senadores, los votos en juego o los 72 — con progreso guardado en tu navegador.
- Botones para compartir por WhatsApp y X.

## Metodología y fuentes

- **Datos de senadores** (nombre, provincia, bloque, mail, teléfono, redes, mandato): [Datos Abiertos del Senado de la Nación](https://www.senado.gob.ar/micrositios/DatosAbiertos/) — los mails son datos públicos oficiales.
- **Extranjerización de tierras**: Registro Nacional de Tierras Rurales (RNTR), citado vía Chequeado.
- **Posturas**: se informan por **bloque** (dictámenes firmados y posición pública del bloque), no como voto individual. Cuando exista votación nominal oficial, se reemplazará por el voto efectivo de cada senador.
- Tono: informativo y citable. Todos los números llevan fuente.

## Estructura

```
data/    senadores-full.json (crudo oficial) · senadores-web.json (normalizado) · estado-votacion.json (banner)
web/     template.html + build.py → index.html (Pages) y artifact.html
fotos/   fotos oficiales de los senadores (datos abiertos del Senado), una por slug
mailer/  herramienta local de mail-merge con Gmail
docs/    plan y decisiones
```

## Build

```bash
python3 web/build.py   # genera web/index.html y web/artifact.html
cp web/index.html web/og-image.png .   # el root es lo que sirve GitHub Pages
```

Sin dependencias: un solo archivo HTML, sin frameworks, sin requests externos, sin analytics ni cookies.

## Actualizar el estado de la votación

Editar `data/estado-votacion.json` (`estado`: `en_curso` | `aprobada` | `rechazada` | `sin_quorum`), rebuildear y copiar al root.

---

Proyecto ciudadano independiente, sin afiliación partidaria. Las correcciones son bienvenidas: abrí un issue.
