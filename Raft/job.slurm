#!/bin/bash
export PINFER_NUM_CORES=$(nproc)
p infer -t $PINFER_TRACE_DIR/Raft/10000 -ce eRaftConfig -z3
