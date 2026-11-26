#!/bin/bash
# usage: q.sh spec1 spec2 ... (waits for running make_reel first)
while pgrep -f make_reel.py >/dev/null; do sleep 5; done
for s in "$@"; do python3 -I /home/user/Mun/.claude/skills/ajans-edit/scripts/make_reel.py $s >> q.log 2>&1; echo "DONE $s $?" >> q.log; done
