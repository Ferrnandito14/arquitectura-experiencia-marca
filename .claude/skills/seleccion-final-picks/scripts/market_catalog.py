#!/usr/bin/env python3
"""Catálogo DECLARATIVO de mercados de fútbol que deben investigarse por partido (Fase 1 de la reforma de arquitectura).

Qué es: la lista de qué se investiga, independiente de cualquier casa de apuestas, de una captura o de lo que publique una API concreta.
Qué NO es: una lista de precios. Los precios llegan por proveedores opcionales (`price_sources.py`); un mercado sin precio sigue en el catálogo.

Cada entrada declara:
  id              identificador estable (familia.mercado.alcance.línea.dirección)
  family          resultado | goles | corners | tarjetas | tiros | otros
  scope           match | home | away
  label           plantilla de la etiqueta (usa {home}/{away}); coincide con las etiquetas de `tickets.atoms` cuando `stats` es «atoms»
  line, direction línea numérica (o None) y dirección (over/under/win/draw/yes/no…)
  data_requirements campos de las filas de historial que hacen falta para examinar el mercado (gf, ga, ht_goals, corners, cards_pts, sot, shots, offsides): la
                  investigación de datos deportivos se resuelve comprobando si esos campos EXISTEN en las filas, con independencia de que haya estimador
  stats           «atoms» (ya calculado por tickets.atoms), «extended» (atoms con extended=True) o None (sin extractor de estadística implementado)
  model           clave de capacidad de `leg_model.py` (None = sin modelo)
  price_key/idx   clave del agregador (`adapters._ODDS_PAIRS`) y posición en la lista de cuotas, si la API publica ese mercado
  price_via_api   True si la API de cuotas CONOCIDA lo entrega (aunque el adaptador no lo mapee todavía); False si no lo publica
  settlement      «implementada» | «no_implementada» (si `seguimiento.py` sabe liquidarla)

Las líneas de córners/tarjetas/remates viven AQUÍ (`STAT_MARKETS`): `tickets.py` las importa, no las duplica.
"""


def drange(lo, hi, step=1.0):
    n = int(round((hi - lo) / step)) + 1
    return [round(lo + i * step, 1) for i in range(n)]


# (clave de fila, mercado, nombre en la etiqueta, líneas del total, líneas por equipo). Tarjetas = PUNTOS (amarilla 1, roja 2, máx. 3 por jugador).
STAT_MARKETS = [
    ("corners", "córners", "córners", drange(6.5, 14.5), drange(2.5, 8.5)),
    ("cards_pts", "tarjetas", "tarjetas (A=1, R=2)", drange(1.5, 9.5), drange(0.5, 5.5)),
    ("sot", "remates a puerta", "remates a puerta", drange(3.5, 14.5), drange(1.5, 9.5)),
    ("shots", "remates", "remates totales", drange(14.5, 32.5), drange(6.5, 18.5)),
]
GOAL_TOTAL_LINES = (0.5, 1.5, 2.5, 3.5, 4.5, 5.5)
GOAL_TOTAL_WHOLE_LINES = (1, 2, 3, 4, 5)                       # totales enteros (devolución si el total es exacto): la API los publica
TEAM_GOAL_LINES = (0.5, 1.5, 2.5)
FIRST_HALF_TOTAL_LINES = (0.5, 1.5, 2.5)
HANDICAP_HALF_LINES = (-2.5, -1.5, -0.5, 0.5, 1.5, 2.5)       # asiático de media línea (sin devolución)
HANDICAP_WHOLE_LINES = (-2, -1, 0, 1, 2)                       # asiático entero (con devolución): la API lo entrega, el adaptador aún no lo mapea
EUROPEAN_HANDICAP_LINES = (-2, -1, 1, 2)                       # europeo de 3 resultados

FAMILIES = ("resultado", "goles", "corners", "tarjetas", "tiros", "otros")


# Campos de historial requeridos por mercado (clave = nombre del mercado en el catálogo).
DATA_REQUIREMENTS = {"córners": ["corners"], "tarjetas": ["cards_pts"], "remates a puerta": ["sot"], "remates": ["shots"], "fueras de juego": ["offsides"],
                     "1.ª parte resultado": ["ht_goals"], "1.ª parte goles": ["ht_goals"]}


def _e(eid, family, market, scope, label, line=None, direction=None, stats=None, model=None, price_key=None, price_idx=None, price_via_api=False, settlement="no_implementada"):
    return {"data_requirements": DATA_REQUIREMENTS.get(market, ["gf", "ga"]), "id": eid, "family": family, "market": market, "scope": scope, "label": label, "line": line, "direction": direction, "stats": stats, "model": model,
            "price_key": price_key, "price_idx": price_idx, "price_via_api": price_via_api, "settlement": settlement}


def _fmt(x):
    return f"{x:+.1f}" if abs(x - round(x)) > 1e-9 else f"{int(x):+d}"


def build_catalog():
    C = []
    # ── Resultado ──
    for i, (side, lab) in enumerate((("home", "Local gana (1)"), ("draw", "Empate (X)"), ("away", "Visitante gana (2)"))):
        C.append(_e(f"resultado.1x2.{side}", "resultado", "resultado", "match", lab, direction=side, stats="atoms", model="1x2", price_key="resultado.1x2", price_idx=i, price_via_api=True,
                    settlement="implementada" if side != "draw" else "no_implementada"))
    for i, (side, lab) in enumerate((("1x", "Local o empate (1X)"), ("12", "Gana alguno, sin empate (12)"), ("x2", "Empate o visitante (X2)"))):
        C.append(_e(f"resultado.dc.{side}", "resultado", "doble oportunidad", "match", lab, direction=side, stats="atoms", model="dc", price_key="resultado.doble_oportunidad", price_idx=i,
                    price_via_api=True, settlement="implementada"))
    for side in ("home", "away"):
        C.append(_e(f"resultado.dnb.{side}", "resultado", "empate no válido", "match", f"Empate no válido: {'local' if side == 'home' else 'visitante'}", direction=side))
    for L in HANDICAP_HALF_LINES:
        tag = f"{L:+.1f}"
        C.append(_e(f"resultado.ah.home.{tag}", "resultado", "hándicap", "home", f"Hándicap local {tag}", line=L, direction="home", stats="atoms", model="handicap",
                    price_key=f"resultado.handicap{tag}", price_idx=0, price_via_api=True, settlement="implementada"))
        C.append(_e(f"resultado.ah.away.{-L:+.1f}", "resultado", "hándicap", "away", f"Hándicap visitante {-L:+.1f}", line=-L, direction="away", stats="atoms", model="handicap",
                    price_key=f"resultado.handicap{tag}", price_idx=1, price_via_api=True, settlement="implementada"))
    for L in HANDICAP_WHOLE_LINES:
        for side, ln in (("home", L), ("away", -L)):
            C.append(_e(f"resultado.ah_entero.{side}.{_fmt(ln)}", "resultado", "hándicap asiático entero", side, f"Hándicap asiático entero {'local' if side == 'home' else 'visitante'} {_fmt(ln)}",
                        line=ln, direction=side, price_key=f"resultado.handicap{_fmt(L) if L else '0'}", price_idx=0 if side == "home" else 1, price_via_api=True))
    for L in EUROPEAN_HANDICAP_LINES:
        for k, nm in (("home", "local"), ("draw", "empate"), ("away", "visitante")):
            C.append(_e(f"resultado.eh.{k}.{_fmt(L)}", "resultado", "hándicap europeo", "match", f"Hándicap europeo ({_fmt(L)} al local): {nm}", line=L, direction=k))
    for k, lab, nm in (("home", "1.ª parte: local gana", "local"), ("draw", "1.ª parte: empate", "empate"), ("away", "1.ª parte: visitante gana", "visitante")):
        C.append(_e(f"primera_parte.1x2.{k}", "resultado", "1.ª parte resultado", "match", lab, direction=k, stats="extended"))
    # ── Goles ──
    for L in GOAL_TOTAL_LINES:
        key = "goles.over_" + str(L).replace(".", "_")
        C.append(_e(f"goles.total.over.{L}", "goles", "goles", "match", f"Más de {L} goles", line=L, direction="over", stats="atoms", model="goals_total", price_key=key, price_idx=0, price_via_api=True, settlement="implementada"))
        C.append(_e(f"goles.total.under.{L}", "goles", "goles", "match", f"Menos de {L} goles", line=L, direction="under", stats="atoms", model="goals_total", price_key=key, price_idx=1, price_via_api=True, settlement="implementada"))
    for L in GOAL_TOTAL_WHOLE_LINES:
        key = f"goles.over_{L}"
        C.append(_e(f"goles.total_entero.over.{L}", "goles", "goles total entero", "match", f"Más de {L} goles", line=L, direction="over", price_key=key, price_idx=0, price_via_api=True))
        C.append(_e(f"goles.total_entero.under.{L}", "goles", "goles total entero", "match", f"Menos de {L} goles", line=L, direction="under", price_key=key, price_idx=1, price_via_api=True))
    C.append(_e("goles.btts.yes", "goles", "goles", "match", "Ambos anotan: sí", direction="yes", stats="atoms", model="btts", price_key="goles.btts", price_idx=0, price_via_api=True, settlement="implementada"))
    C.append(_e("goles.btts.no", "goles", "goles", "match", "Ambos anotan: no", direction="no", stats="atoms", model="btts", price_key="goles.btts", price_idx=1, price_via_api=True, settlement="implementada"))
    for scope in ("home", "away"):
        for L in TEAM_GOAL_LINES:
            C.append(_e(f"goles.equipo.{scope}.over.{L}", "goles", "goles por equipo", scope, "{" + scope + "}: más de " + f"{L} goles", line=L, direction="over", stats="extended"))
            C.append(_e(f"goles.equipo.{scope}.under.{L}", "goles", "goles por equipo", scope, "{" + scope + "}: menos de " + f"{L} goles", line=L, direction="under", stats="extended"))
    for L in FIRST_HALF_TOTAL_LINES:
        C.append(_e(f"primera_parte.total.over.{L}", "goles", "1.ª parte goles", "match", f"1.ª parte: más de {L} goles", line=L, direction="over", stats="extended"))
        C.append(_e(f"primera_parte.total.under.{L}", "goles", "1.ª parte goles", "match", f"1.ª parte: menos de {L} goles", line=L, direction="under", stats="extended"))
    # ── Córners, tarjetas, remates (mismas líneas que usa tickets.py) ──
    fam = {"corners": "corners", "cards_pts": "tarjetas", "sot": "tiros", "shots": "tiros"}
    for key, market, nm, tot_lines, team_lines in STAT_MARKETS:
        for L in tot_lines:
            C.append(_e(f"{key}.total.over.{L}", fam[key], market, "match", f"Más de {L} {nm}", line=L, direction="over", stats="atoms", settlement="implementada" if key in ("cards_pts",) else "no_implementada"))
            C.append(_e(f"{key}.total.under.{L}", fam[key], market, "match", f"Menos de {L} {nm}", line=L, direction="under", stats="atoms", settlement="implementada" if key in ("cards_pts",) else "no_implementada"))
        for scope in ("home", "away"):
            for L in team_lines:
                C.append(_e(f"{key}.equipo.{scope}.over.{L}", fam[key], market, scope, "{" + scope + "}: más de " + f"{L} {nm}", line=L, direction="over", stats="atoms"))
                C.append(_e(f"{key}.equipo.{scope}.under.{L}", fam[key], market, scope, "{" + scope + "}: menos de " + f"{L} {nm}", line=L, direction="under", stats="atoms"))
    C.append(_e("otros.fueras_de_juego.total", "otros", "fueras de juego", "match", "Fueras de juego totales"))
    for e in C:                                                    # capacidad de los modelos propios (leg_model.py / count_model.py); None = sin estimador
        i = e["id"]
        if i.startswith("resultado.dnb."):
            e["model"] = "dnb"
        elif i.startswith("goles.equipo."):
            e["model"] = "team_goals"
        elif i.startswith("primera_parte.1x2."):
            e["model"] = "half_1x2"
        elif i.startswith("primera_parte.total."):
            e["model"] = "half_total"
        elif i.startswith("corners."):
            e["model"] = "count:corners"
        elif i.startswith("cards_pts."):
            e["model"] = "count:cards"
    return C


CATALOG = build_catalog()
BY_ID = {e["id"]: e for e in CATALOG}
assert len(BY_ID) == len(CATALOG), "ids duplicados en el catálogo"


def entry_label(entry, home, away):
    return entry["label"].replace("{home}", home).replace("{away}", away)


def entries(family=None):
    return [e for e in CATALOG if family is None or e["family"] == family]


def summary():
    out = {}
    for e in CATALOG:
        out.setdefault(e["family"], {}).setdefault(e["market"], 0)
        out[e["family"]][e["market"]] += 1
    return out


if __name__ == "__main__":
    import json
    print(json.dumps({"entradas": len(CATALOG), "por_familia": summary()}, ensure_ascii=False, indent=1))
