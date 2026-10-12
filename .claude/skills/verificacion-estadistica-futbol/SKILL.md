---
name: verificacion-estadistica-futbol
description: Reglas para validar estadísticas de fútbol por mercado (goles, BTTS, córners, tarjetas, 1X2/hándicap) - muestra, local/visitante, línea exacta, calidad del rival, detección de datos defectuosos y reglas de liquidación. Úsala al verificar o interpretar cualquier estadística antes de aceptarla como evidencia.
---

# Verificación estadística por mercado

Para cualquier cifra: fuente, fecha de consulta, competición, temporada, n real, y si es total/local/visitante.

## Reglas generales
- Reportar siempre `k/n` (p. ej. 7/10), no solo porcentajes ni medias. n<8 = muestra débil; mezclar competiciones/temporadas = declararlo.
- Frecuencia observada ≠ probabilidad. No convertir medias en probabilidad de superar una línea.
- Ponderar por calidad de rival y localía; no tratar todos los partidos como equivalentes. Excluir/segregar partidos con roja temprana, rotaciones o partidos amistosos.
- Cifras defectuosas: ceros sospechosos, promedios incompatibles con los partidos listados, partidos faltantes. Contrastar con otra fuente o descartar la cifra.
- Fuentes derivadas del mismo proveedor de datos no son evidencias independientes.

## Córners
Necesario: a favor y en contra, local/visitante separados, últimos 5–10, n, distribución de córners totales, frecuencia de superar la **línea exacta** (ojo línea .5 vs entera/asiática), calidad de rivales. Comprobar si el mercado cuenta córners del partido completo o de una mitad. Con ≥2 fuentes: comparar partido a partido.

## Tarjetas
Distinguir amarillas, rojas, totales y puntos (amarilla=1, roja=2 o 3 según casa). Verificar la regla de liquidación de la casa (¿doble amarilla cuenta?, ¿banquillo/técnicos?). Árbitro: designación confirmada en fuente fiable, n de partidos en **esa competición**, no extrapolar entre ligas. La media del árbitro no es probabilidad del mercado; cruzar con equipos, rivalidad, contexto y faltas.

## Goles / BTTS
Goles a favor/en contra local-visitante; xG/xGA solo si la liga está cubierta y es fiable; BTTS y Over por equipo con n; tendencia ofensiva con bajas de delanteros/porteros.

## 1X2 / doble oportunidad / hándicap
Forma ajustada por rival, localía, motivación, bajas, descanso/viajes; H2H solo si es reciente y los plantillas/entrenadores son comparables.

## Lesiones/alineaciones
Estado: baja confirmada / duda / regreso probable / convocado / alineación probable / once confirmado. Fecha de la noticia. Explicar el efecto plausible sobre el mercado sin cifras inventadas.

## Salida
Cada dato verificado entra como: `dato | fuente | fecha | n | estado (Confirmado / Una sola fuente / Discrepante / No verificable)`.
