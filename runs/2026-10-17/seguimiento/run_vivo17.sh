#!/bin/bash
cd /home/user/football-picks-system
export PYTHONDONTWRITEBYTECODE=1 APIFOOTBALL_KEY_FILE=/tmp/claude-0/-home-user/d56b1dd2-9e37-5240-9a83-4b470c476a77/scratchpad/probe/key.txt
# no consulta nada hasta 5 min antes del primer partido (11:30 UTC = 07:30 Caracas)
t0=$(date -u -d '2026-10-17 11:25:00' +%s)
while [ $(date -u +%s) -lt $t0 ]; do sleep 60; done
for i in $(seq 1 40); do
  python3 .claude/skills/seleccion-final-picks/scripts/vivo.py --run runs/2026-10-17 --every 60
  rc=$?
  [ $rc -eq 0 ] && break
  sleep 5
done
