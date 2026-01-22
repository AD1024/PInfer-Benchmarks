#!/bin/bash
export PINFER_NUM_CORES=$(nproc)
p infer -t $PINFER_TRACE_DIR/paxos_new/10000 -ce ePaxosConfig -z3
