cd /home/user/football-picks-system
export APIFOOTBALL_KEY_FILE=/tmp/claude-0/-home-user/d56b1dd2-9e37-5240-9a83-4b470c476a77/scratchpad/probe/key.txt PYTHONDONTWRITEBYTECODE=1
S=.claude/skills/seleccion-final-picks/scripts
R=runs/2026-10-26
python3 $S/level1.py --run $R --ids $R/ligas/ids.json > $R/level1.log 2>&1
LEAGUES=$(python3 - <<'PY'
import sys,json
sys.path.insert(0,'.claude/skills/seleccion-final-picks/scripts')
import market_coverage as cov
R='runs/2026-10-26'
ids=json.load(open(R+'/ligas/ids.json'))
inv=json.load(open(R+'/inventory.json'))['matches']
by={m['match_id']:m for m in inv}
s=set()
for mid in ids.values():
    l=cov.league_of(by[mid],inv)
    if l: s.add(str(l))
print(' '.join(sorted(s)))
PY
)
echo "$LEAGUES" > $R/league_ids.txt
for L in $LEAGUES; do python3 $S/league_sample.py --run $R --league-id $L --to 2026-10-25 2>&1 | tail -1; done > $R/league_samples.log
MS=$(python3 -c "import json;print(','.join(json.load(open('$R/ligas/ids.json')).values()))")
for i in 1 2 3; do python3 $S/rotation_prior.py --run $R --matches $MS 2>&1 | tail -1; done > $R/rotation_log.txt
python3 $S/tsa_fetch.py --run $R --ids $R/ligas/ids.json --key-file /tmp/claude-0/-home-user/d56b1dd2-9e37-5240-9a83-4b470c476a77/scratchpad/probe/thestatsapi_key.txt > $R/tsa.log 2>&1
echo done > $R/prep.done
