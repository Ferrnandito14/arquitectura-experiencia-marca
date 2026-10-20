#!/bin/bash
cd /home/user/football-picks-system
export PYTHONDONTWRITEBYTECODE=1 APIFOOTBALL_KEY_FILE=/tmp/claude-0/-home-user/d56b1dd2-9e37-5240-9a83-4b470c476a77/scratchpad/probe/key.txt
for i in $(seq 1 60); do
  python3 .claude/skills/seleccion-final-picks/scripts/vivo.py --run runs/2026-10-18 --every 90
  rc=$?
  [ $rc -eq 0 ] && break
  sleep 5
done
