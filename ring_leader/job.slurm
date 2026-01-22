#!/bin/bash
export PINFER_NUM_CORES=$(nproc)
p infer -t $PINFER_TRACE_DIR/ring_leader/10000 -z3
