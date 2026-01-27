#!/bin/bash
python3 cleanup.py
python3 run_pinfer_sequential.py
cd rq2  
eval $(opam env) && python3 run_pinfer_examples.py