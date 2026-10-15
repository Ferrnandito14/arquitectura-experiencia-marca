#!/usr/bin/env python3
"""Empareja los partidos de las capturas de la persona usuaria con el inventario de la corrida.

Uso:  resolve_ids.py --run runs/2026-10-15 [--min-score 1.4] [--window-min 150]
Lee runs/<fecha>/ligas/partidos_usuario.json y runs/<fecha>/inventory.json; escribe ligas/ids.json ({"local|visitante": match_id}),
ligas/ids_revision.json (aceptados con su puntuación, para revisión) y ligas/ids_sin_resolver.json.
Criterio: hora de Caracas de la captura dentro de ±window-min de la hora normalizada del inventario, categoría masculina de primer equipo
y similitud de nombres (alias + iniciales) de ambos equipos. Un partido sin candidato suficiente NO se adivina: queda sin resolver.
Las capturas solo definen los PARTIDOS (nunca los mercados)."""
import argparse
import difflib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

ALIAS = {"ny red bulls": "new york red bulls", "borussia dortmund": "dortmund", "fk bodo glimt": "bodo glimt", "saint louis city sc": "st louis city",
         "inter miami cf": "inter miami", "fc toronto": "toronto", "los angeles galaxy": "la galaxy", "nápoles": "napoli", "napoles": "napoli", "génova": "genoa", "genova": "genoa",
         "inter milan": "inter", "bologna fc": "bologna", "sao paulo fc": "sao paulo", "cologne": "koln", "nurnberg": "nurnberg", "psg": "paris saint germain",
         "rcd espanyol": "espanyol", "real betis": "betis", "vfb stuttgart": "stuttgart", "bayern munich": "bayern munchen", "club leon": "leon", "america": "club america",
         "guadalajara chivas": "guadalajara", "tigres uanl": "tigres uanl", "santos laguna": "santos laguna", "deportivo toluca": "toluca", "ham kam": "hamkam",
         "kristiansund": "kristiansund bk", "aalesunds": "aalesund", "amed sportif faaliyetler": "amed", "buyuksehir belediye erzurumspor": "erzurumspor",
         "genclerbirligi sk": "genclerbirligi", "galatasaray sk": "galatasaray", "konyaspor club": "konyaspor", "al qadisiyah": "al qadsiah", "abha": "abha",
         "al khaleej saihat fc": "al khaleej", "al faisaly fc": "al faisaly", "al hazm fc": "al hazm", "al ettifaq fc": "al ettifaq", "neom sc": "neom", "wieczysta krakow": "wieczysta",
         "rakow czestochowa": "rakow", "widzew lodz": "widzew", "wisla krakow": "wisla krakow", "corum fk": "corum", "caykur rizespor": "rizespor", "recoleta": "recoleta",
         "rubio nu": "rubio nu", "atlante fc": "atlante", "xolos de tijuana": "tijuana", "cd leganes": "leganes", "deportivo la coruna": "deportivo la coruna",
         "eintracht frankfurt": "eintracht frankfurt", "holstein kiel": "kiel", "hertha berlin": "hertha", "frosinone calcio": "frosinone", "le mans": "le mans",
         "defensa y justicia": "defensa y justicia", "instituto ac cordoba": "instituto", "internacional": "internacional", "atletico mg": "atletico mineiro",
         "athletico paranaense": "athletico pr", "atletico tucuman": "atletico tucuman", "velez sarsfield": "velez sarsfield", "gimnasia mendoza": "gimnasia mendoza",
         "dep la guaira": "deportivo la guaira", "academia anzoategui fc": "anzoategui", "deportivo tachira": "tachira", "independiente santa fe": "santa fe",
         "jaguares de cordoba": "jaguares", "sporting san jose": "sporting san jose", "deportivo saprissa": "saprissa", "u craiova": "universitatea craiova",
         "nijmegen": "nec nijmegen", "rc celta": "celta vigo", "hapoel beer sheva fc": "hapoel beer sheva", "union saint gilloise": "union saint gilloise",
         "gnk dinamo": "dinamo zagreb", "besiktas jk": "besiktas", "sk sturm graz": "sturm graz", "kairat almaty": "kairat", "heart of midlothian fc": "heart of midlothian",
         "lincoln red imps fc": "lincoln red imps", "fk kauno zalgiris": "zalgiris", "fk borac banja luka": "borac banja luka", "inter club d escaldes": "inter club d escaldes",
         "mjallby": "mjallby", "cska sofia": "cska sofia", "egnatia": "egnatia", "agf aarhus": "aarhus", "kups": "kups", "red star": "crvena zvezda", "ac sparta prague": "sparta prague",
         "lillestrom": "lillestrom", "celje": "celje", "ac omonia nicosia": "omonia", "fc salzburg": "salzburg", "olympique lyonnais": "lyon", "torreense": "torreense",
         "marseille": "marseille", "olympiacos fc": "olympiacos", "levski sofia": "levski sofia", "ofi": "ofi crete", "sl benfica": "benfica", "celtic fc": "celtic"}


def toks(s):
    n = common.norm_name(s)
    n = ALIAS.get(n, n)
    return [t for t in n.split() if t not in ("fc", "sc", "cf", "fk", "sk", "ac", "club")] or n.split()


def sim(a, b):
    ta, tb = " ".join(toks(a)), " ".join(toks(b))
    r = difflib.SequenceMatcher(None, ta, tb).ratio()
    if ta and tb and (ta in tb or tb in ta):
        r = max(r, 0.9)
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--min-score", type=float, default=1.4)
    ap.add_argument("--window-min", type=int, default=150)
    a = ap.parse_args(argv)
    inv = common.read_json(os.path.join(a.run, "inventory.json"))
    cap = common.read_json(os.path.join(a.run, "ligas", "partidos_usuario.json"))
    day = inv["meta"]["date"]
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(inv["meta"].get("tz", "America/Caracas"))
    used, out, review, miss = set(), {}, [], []
    for liga, h, aw, hora, *_ in cap["partidos"]:
        want = datetime.fromisoformat(f"{day}T{hora}:00").replace(tzinfo=tz).astimezone(timezone.utc)
        cands = []
        for m in inv["matches"]:
            if m.get("gender_or_category") != "men" or m["match_id"] in used:
                continue
            try:
                t = datetime.fromisoformat(m["normalized_datetime_utc"].replace("Z", "+00:00"))
            except Exception:
                continue
            if abs((t - want).total_seconds()) / 60 > a.window_min:
                continue
            cands.append((sim(h, m["home_team"]) + sim(aw, m["away_team"]), m))
        cands.sort(key=lambda x: -x[0])
        if cands and cands[0][0] >= a.min_score:
            s, m = cands[0]
            out[f"{h}|{aw}"] = m["match_id"]
            used.add(m["match_id"])
            review.append({"captura": f"{h} – {aw} {hora}", "inventario": f"{m['home_team']} – {m['away_team']}", "competicion": m["competition"], "utc": m["normalized_datetime_utc"],
                           "puntuacion": round(s, 2), "elegible": m.get("analysis_required")})
        else:
            miss.append({"captura": f"{h} – {aw} {hora}", "liga": liga, "mejores": [(round(s, 2), m["home_team"], m["away_team"], m["competition"], m["normalized_datetime_utc"]) for s, m in cands[:3]]})
    d = os.path.join(a.run, "ligas")
    common.write_json_atomic(os.path.join(d, "ids.json"), out)
    common.write_json_atomic(os.path.join(d, "ids_revision.json"), review)
    common.write_json_atomic(os.path.join(d, "ids_sin_resolver.json"), miss)
    print(f"{len(out)} resueltos de {len(cap['partidos'])}; sin resolver: {len(miss)}; con puntuación < 1.7: {sum(1 for r in review if r['puntuacion'] < 1.7)}; no elegibles: {sum(1 for r in review if not r['elegible'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
