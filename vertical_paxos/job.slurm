#!/bin/bash
export PINFER_NUM_CORES=$(nproc)
p infer -t $PINFER_TRACE_DIR/vertical_paxos/10000 -ce ePaxosConfig -z3
