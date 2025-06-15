#!/bin/bash
for file in /home/normchell/Документы/Programs/antipuzzle_pusher/*.pgn; do
    python "generator.py" "$file" nogen
done
