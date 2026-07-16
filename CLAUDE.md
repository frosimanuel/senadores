# Proyecto Senadores — "El Senado y la Tierra"

Web pública de perfiles de los 72 senadores argentinos, centrada en la votación del proyecto de "Inviolabilidad de la Propiedad Privada" (capítulo tierras). Objetivo: que cualquier persona encuentre a sus senadores, entienda su postura sobre la ley de tierras y pueda escribirles en un click.

## Contexto político (verificado al 16/07/2026)

- El proyecto deroga los topes de la Ley de Tierras 26.737 (15% nacional/provincial/departamental, 30% por nacionalidad, 1.000 ha zona núcleo) y crea silencio administrativo positivo de 180 días en zonas de frontera. Las provincias reciben facultad de autorizar/regular/vetar.
- Ingresó por el **Senado** (cámara de origen). Si se aprueba → media sanción → Diputados.
- Sesión del 16/07/2026: hubo quórum y se aprobaron pliegos judiciales, pero al llegar al proyecto Bullrich pidió **cuarto intermedio hasta el 06/08/2026** — el oficialismo no tenía los votos para el capítulo de tierras (llegó a circular una "versión 15" del texto horas antes). Fuentes: Ámbito n6300262, Infobae en-vivo 16/07. Banner actualizado (estado `postergada`). Próximo hito: sesión del 6 de agosto.
- Datos clave (RNTR vía Chequeado, citables): extranjerización nacional 5,02% (12,5M ha), PERO 36 departamentos >15% y 4 >50% (Lácar/Neuquén, Gral. Lamadrid/La Rioja, Molinos y San Carlos/Salta). ~2M ha en paraísos fiscales, 2,2M ha de nacionalidad desconocida.

## Estructura

- `data/senadores-full.json` — crudo del endpoint oficial: https://www.senado.gob.ar/micrositios/DatosAbiertos/ExportarListadoSenadores/json (`table.rows`)
- `data/senadores-web.json` — normalizado: slug, género (para saludo), postura de bloque (impulsa/dictamen/juego/rechaza), datos RNTR por provincia, contacto y redes
- `data/senadores.csv` — versión simple (nombre, provincia, bloque, email)
- `mailer/` — herramienta local de mail-merge (mailer-senadores.html) + template de mail + listas BCC
- `web/` — el sitio público (single-file `index.html`, se publica como Artifact de claude.ai)
- `docs/PLAN.md` — plan revisado con pipeline gstack /autoplan

## Decisiones tomadas (no re-litigar)

1. **Single-file HTML con hash-routing** (`#/senador/<slug>`) — se publica como Artifact; CSP bloquea todo request externo → **nada de CDNs, webfonts remotas, ni fotos del Senado**; medallones con iniciales en su lugar.
2. **Postura por BLOQUE, no por senador** — no inventamos votos individuales; etiquetas: "Impulsa el proyecto" (LLA), "Firmó dictamen de mayoría" (UCR/PRO), "Dictamen de minoría"/"Rechaza" (CF/PJ), "Voto en juego" (provinciales). Cuando haya votación nominal real, reemplazar por voto efectivo.
3. **Tono sobrio y citable, no partidario** — todos los números con fuente (RNTR/Chequeado, prensa). El sitio informa y facilita contacto; no insulta ni milita.
4. **Estética patriótica**: celeste #74ACDF · tinta #14212E · fondo #FAFBFC · dorado sol de mayo #C99C33 (único acento fuerte) · verde/rojizo apagados solo para semáforo de postura. Display serif Didot/Bodoni stack, cuerpo sans humanista, `tabular-nums` en datos.
5. **Saludo por género** en mails (dataset trae `genero` F/M inferido del nombre de pila — los 72 son inequívocos).
6. Los mails de senadores son datos públicos oficiales (datos abiertos del Senado) — publicarlos es legítimo.

## Convenciones

- Español rioplatense, ortografía completa.
- No commitear sin pedido explícito.
- Al terminar trabajo sustantivo, actualizar la sección "Estado" de abajo para las otras sesiones.

## Estado (actualizar al cerrar cada sesión)

- [16/07 ~19:45] Proyecto migrado desde sesión principal. Dataset normalizado listo. Mailer funcional en `mailer/`.
- [16/07 ~20:40] Sitio construido y publicado como Artifact (privado): https://claude.ai/code/artifact/0edd6df9-62b1-41f8-9c1f-377be36bbaf3 — build con `python3 web/build.py` (genera index.html para Pages y artifact.html para Artifact). Plan revisado con /autoplan en docs/PLAN.md (audit trail + checklist de salida).
- [16/07 ~20:50] v2 share-ready publicada (misma URL): botones compartir WhatsApp/X/copiar-link en footer y en cada perfil, OG meta tags en index.html, banner afinado ('resultado aún no confirmado'). CONFIRMADO: el '40-22' que circula en búsquedas es la votación de holdouts de JUNIO, no tierras — no publicarlo como resultado.
- [16/07 ~21:00] Repo público creado: github.com/frosimanuel/senadores · GitHub Pages activo → https://frosimanuel.github.io/senadores/ (301 → dominio custom del user: https://0xdwb.is-a.dev/senadores/, ese es el canónico). Root index.html es copia de web/index.html — al rebuildear, re-copiar y pushear.
- [16/07, día de sesión] Share-ready final pusheado y verificado en vivo: `<head>` completo (title, meta description, canonical, favicon sol de mayo inline), og:image 1200×630 generada con Pillow (web/og-image.png + copia en root; regenerar con scratchpad si cambia el copy), twitter:card summary_large_image, README.md público con metodología. build.py ahora strippea el title/meta del template en index.html (quedan solo para que el Artifact se nombre). OJO TIMEZONE: la máquina está en UTC+7; Argentina es UTC-3 (10h menos). La sesión del Senado (12hs ART) arranca ~22hs hora local de la máquina. Banner corregido a pre-sesión. Cron one-shot en esta sesión chequea el resultado a las 02:07 local (16:07 ART).
- [16/07, mediodía ART] v3 PUBLICADA (Pages + Artifact): fix overflow 375px (select provincia era 393px intrínsecos → max-width), footer sin párrafo EN, fotos oficiales de los 72 en `fotos/<slug>.jpg` (fsenaG 110×110 del Senado, medallón con fallback a iniciales si no cargan — en Artifact la CSP las bloquea y quedan iniciales), y modo campaña en `#/campania` (grupos: en juego / en juego+dictamen / mi provincia / los 72; progreso por senador en localStorage `campania-enviados`). Tests con puppeteer-core (scratchpad) contra server local: overflow 375 OK, fotos OK, persistencia OK.
- [17/07 local] Auditoría /fanout (4 ángulos) + Día 1 completo aplicado: countdown al 6/08 (hero kicker + banner), mail/asunto/shares con el deadline, remitente (nombre/ciudad) y provincia persistentes en localStorage, share post-envío, navigator.share, botón "Abriendo…", contacto primero en perfil mobile, link a campaña desde perfil/footer, contraste dictamen AA (#3E6690), **72 páginas prerender s/<slug>.html con tarjeta OG personalizada og/<slug>.jpg** (los shares de perfil apuntan ahí — card de WhatsApp con cara y nombre), sitemap.xml, robots.txt, 404.html, .nojekyll, HTTPS enforced. Tarjetas OG se regeneran con scratchpad/og_senadores.py (Pillow). PROYECTOS pendientes de la auditoría: camp-rapido embebido en el hero al elegir provincia (ítem 15) y asset vertical 1080×1920 para stories (ítem 21).
- PENDIENTE: (1) resultado de la votación → actualizar `data/estado-votacion.json` + rebuild + cp al root + push + re-publicar Artifact (favicon 🇦🇷, misma URL); recordar: el "40-22" indexado es holdouts de JUNIO, no publicarlo; (2) contacto del proyecto en footer — NO publicar datos personales sin su OK; (3) checklist de salida de docs/PLAN.md a mano en navegador real (deep-links en iframe, teclado, 375px).
