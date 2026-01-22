#!/bin/bash
export PINFER_NUM_CORES=$(nproc)
p infer -t $PINFER_TRACE_DIR/consensus/10000 -ce eConfig -z3
