#!/usr/bin/env python3
"""Riesgo de ROTACIÓN (auditoría 13-oct): la persona usuaria arma los picks HORAS antes y las alineaciones salen ~1 h antes, así que NO se bloquea el ticket por
falta de once. Se estima un riesgo a priori (descanso, competición europea/copa entre semana, tasa de cambios entre los últimos once) que penaliza unders y patas
de ganador del equipo con riesgo; a T-60 `lineup_check.py` lo reevalúa con el once real. «Ausente del once» NO es baja (puede ser rotación o suplencia habitual)."""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LEVELS = ("bajo", "medio", "alto")


def change_rate(prev_xis):
    """Cambios medios entre once consecutivos (jugadores nuevos por partido, 0–11). prev_xis: lista de conjuntos de ids, del más reciente al más antiguo."""
    xs = [x for x in prev_xis if x]
    if len(xs) < 2:
        return None
    return sum(len(a - b) for a, b in zip(xs, xs[1:])) / (len(xs) - 1)


def overlap_with_habitual(today_xi, prev_xis):
    """Titulares de hoy que estuvieron en al menos la mitad de los once recientes (11 = once habitual completo)."""
    xs = [x for x in prev_xis if x]
    if not today_xi or not xs:
        return None
    need = max(1, len(xs) // 2)
    return sum(1 for p in today_xi if sum(p in x for x in xs) >= need)


def prior_risk(rest_days, euro_or_cup_soon, change_rate_prev, knockout_first_leg=False):
    """Riesgo a priori de rotación: puntos por descanso corto, competición continental/copa próxima, historial de rotación y eliminatoria."""
    pts, why = 0, []
    if rest_days is not None and rest_days <= 3:
        pts += 2
        why.append(f"descanso corto ({rest_days} días)")
    elif rest_days is not None and rest_days <= 4:
        pts += 1
        why.append(f"descanso justo ({rest_days} días)")
    if euro_or_cup_soon:
        pts += 1
        why.append("competición europea/copa en ≤4 días")
    if change_rate_prev is not None and change_rate_prev >= 4:
        pts += 2
        why.append(f"rota mucho (≈{change_rate_prev:.1f} cambios por partido)")
    elif change_rate_prev is not None and change_rate_prev >= 2.5:
        pts += 1
        why.append(f"rotación moderada (≈{change_rate_prev:.1f} cambios)")
    if knockout_first_leg:
        why.append("ida de eliminatoria (cautela)")
    level = "alto" if pts >= 4 else ("medio" if pts >= 2 else "bajo")
    return {"nivel": level, "puntos": pts, "motivos": why}


def real_risk(today_xi, prev_xis):
    """Riesgo con el once real: ≥8 habituales = bajo; 6–7 = medio; ≤5 = alto (el 13-oct Watford 6/11 y Bayern 5/11)."""
    ov = overlap_with_habitual(today_xi, prev_xis)
    if ov is None:
        return {"nivel": None, "habituales": None}
    return {"nivel": "bajo" if ov >= 8 else ("medio" if ov >= 6 else "alto"), "habituales": ov}


def penalty_for_leg(level, direction, is_team_win_leg):
    """Penalización de la pata según el riesgo de rotación: 'veto' (under con riesgo alto), 'rebajar' o None."""
    if level == "alto" and (direction == "under" or is_team_win_leg):
        return "veto"
    if level == "medio" and (direction == "under" or is_team_win_leg):
        return "rebajar"
    return None


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()
