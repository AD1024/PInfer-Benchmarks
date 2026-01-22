#!/bin/bash
export PINFER_NUM_CORES=$(nproc)
p infer -t $PINFER_TRACE_DIR/2PC/10000 -ce eMonitor_AtomicityInitialize -z3
