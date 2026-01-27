#!/bin/bash
mkdir -p tables
python3 draw_tables.py --tables 4
python3 draw_tables.py --tables 5 --no-rerun
python3 draw_tables.py --tables 6 --no-rerun
mv table_4.txt table_5.txt table_6.txt tables/
mv rq2/pv_times.txt tables/table_6_verifier_time.txt