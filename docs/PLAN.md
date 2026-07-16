# Plan — "El Senado y la Tierra" (web pública)

## Qué construimos

Single-file HTML (`web/index.html`) publicado como Artifact de claude.ai, con:

1. **Home**: hero con sol de mayo (canvas) y tesis ("72 personas deciden quién puede comprar la Argentina"), tira de contexto con los 4 números RNTR citables, tablero de situación (21 impulsan / 13 dictamen / 14 en juego / 24 rechazan), filtros (búsqueda, provincia, bloque, postura) y grilla de 72 tarjetas.
2. **Perfil por senador** (hash-routing `#/senador/<slug>`): medallón escarapela con iniciales, nombre, provincia, bloque, partido, mandato, postura del bloque con explicación, dato de extranjerización de su provincia (si hay), contacto (email con botón copiar + abrir en Gmail prellenado, teléfono conmutador) y redes (X/FB/IG).
3. **Sección "Qué se vota"**: explicación sobria del proyecto (qué elimina, qué mantiene, el silencio administrativo de 180 días, el promedio vs. los departamentos) con fuentes linkeadas.
4. **Footer metodológico**: fuentes (datos abiertos Senado, RNTR/Chequeado, prensa), fecha de corte, aclaración de que la postura es de bloque, no predicción de voto individual.

## Datos

`data/senadores-web.json` embebido en el HTML en build (script `web/build.py` — inyecta JSON en template). Estado de votación en `data/estado-votacion.json` (pendiente/aprobada/rechazada/sin quórum) también embebido; el banner del sitio cambia según estado.

## Diseño

Paleta y tipografía según CLAUDE.md (celeste/tinta/dorado, Didot display + sans humanista). Mobile-first (375px). Accesibilidad: contraste AA, focus visible, navegación por teclado en la grilla, `prefers-reduced-motion`.

## Restricciones duras

- CSP de Artifacts: cero requests externos (sin webfonts CDN, sin fotos remotas, sin analytics). Links salientes (Gmail, redes, fuentes) sí funcionan.
- Tono no partidario, todo número con fuente.
- Sin datos personales no oficiales de los senadores.

## No-scope (deferido)

- Backend / actualización automática de datos (es un snapshot con fecha de corte visible).
- Votación nominal en vivo (se agrega cuando exista el dato, re-publicando el artifact).
- Multi-idioma (el pedido "para el mundo" se cubre con un párrafo introductorio en inglés en el footer, no con i18n completo).
- Fotos reales de senadores (CSP; evaluar embeber data-URIs en iteración futura si el peso lo permite).

---

# GSTACK REVIEW REPORT (/autoplan, 16/07/2026)

Adaptación declarada: sin voces Codex (velocidad, votación en curso); voz dual = Claude subagente independiente (Sonnet) + análisis orquestador. Fases CEO→Design→Eng secuenciales; DX no aplica (no es producto developer-facing).

## Consenso de voces

| Dimensión | Orquestador | Subagente | Consenso |
|---|---|---|---|
| Artifact como canal público final | Débil | Crítico: no indexa, sin og:tags, URL sospechosa en WhatsApp | DISAGREE parcial → GATE (challenge) |
| Framing pre-voto vs post-voto | Banner por estado | Crítico: decidir antes de codear; copy cambia | CONFIRMADO → máquina de estados |
| Dorado como texto | Solo decorativo | Falla AA (2,45:1 medido) | CONFIRMADO |
| Mobile: grilla plana de 72 | Filtro prominente | Provincia-first / acordeones; 6000px+ de scroll si no | CONFIRMADO |
| Riesgo kitsch | Sobrio, line-art | Sol line-art fino, medallones flat sin glow/gradiente | CONFIRMADO |
| Postura de bloque "en juego" | Etiqueta honesta | Disclaimer EN el perfil, no solo footer | CONFIRMADO |
| Hash deep-links en Artifact | Asumido OK | No verificado en iframe — experimento de 10 min o Pages | CONFIRMADO (riesgo real) |
| tel interno 1045/1046 | — | No clickeable sin troncal verificado | CONFIRMADO |
| XSS | Escapar | `</script` escape + textContent estricto + assertion en build.py | CONFIRMADO |

## Decision Audit Trail

| # | Fase | Decisión | Clase | Principio | Racional |
|---|---|---|---|---|---|
| 1 | Eng | JSON en `<script type="application/json">` con `</script` escapado; render 100% textContent; assertion anti-`</script` en build.py | Mecánica | P1 | Elimina XSS por diseño |
| 2 | Design | Dorado NUNCA como texto sobre claro; decorativo/bordes/fills con texto tinta | Mecánica | P1 | AA 2,45:1 falla |
| 3 | Design | Selector de provincia arriba del pliegue + grilla agrupada por provincia (acordeones en mobile) | Mecánica | P5 | Tarea principal: encontrar a TUS 3 senadores |
| 4 | Design | Estados: empty de filtro, 404 de slug, 4 banners de votación (pendiente/aprobada/rechazada/sin quórum) diseñados | Mecánica | P1 | Completeness |
| 5 | Design | Semáforo de postura: ícono+texto además de color; paleta apagada | Mecánica | P1 | WCAG 1.4.1 |
| 6 | CEO | Disclaimer "postura de bloque ≠ voto individual" en cada tarjeta/perfil "en juego" | Mecánica | P1 | Riesgo reputacional |
| 7 | Eng | Teléfono como texto "Conmutador del Senado — interno X", no clickeable | Mecánica | P5 | Interno no discable |
| 8 | Eng | Budget <200KB sin comprimir; checklist de salida (abajo) antes de publicar | Mecánica | P1 | Gama baja / 3G |
| 9 | CEO | Copy como máquina de estados: mismo sitio sirve pre-voto (mobilizador) y post-voto (rendición de cuentas + Diputados) | Mecánica | P1+P6 | La votación es esta noche |
| 10 | CEO | Canal de publicación | USER CHALLENGE | — | → GATE |
| 11 | Design | Tesis del hero (editorial vs neutra) | TASTE | — | → GATE |
| 12 | CEO | Autoría/accountability en footer | TASTE | — | → GATE |

## Checklist de salida (test plan)

Deep-link con hash en pestaña incógnita · atrás/adelante · `#/senador/inexistente` → 404 · assertion `</script` en build · inyección de prueba `<img onerror>` renderiza literal · axe/contraste sin dorado-texto · recorrido solo-teclado completo · 375px real · Gmail prellenado con acentos (encodeURIComponent) · clipboard en iframe con fallback · los 4 banners probados · verificación de acceso al link público sin cuenta.

## NOT in scope
Backend, votación nominal en vivo (re-publish manual), i18n completo, fotos (CSP/peso).

## Qué ya existe
Dataset normalizado (data/senadores-web.json), template de mail probado, targeting por bloque, kit mailer local (no duplicar: el perfil abre Gmail con UN mail).
