#!/bin/bash
mkdir -p tables
echo "==========Table 4=========="
python3 draw_tables.py --tables 4
echo "==========================="
echo "==========Table 5=========="
python3 draw_tables.py --tables 5 --no-rerun
echo "==========================="
echo "==========Table 6=========="
python3 draw_tables.py --tables 6 --no-rerun
echo "==========================="

cd rq2  
eval $(opam env) && python3 run_pinfer_examples.py
echo "==========Table 6 -- Verification Time=========="
cat pv_times.txt
echo "==============================================="
cd ..

mv table_4.txt table_5.txt table_6.txt tables/
mv rq2/pv_times.txt tables/table_6_verifier_time.txt