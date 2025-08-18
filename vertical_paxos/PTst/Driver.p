machine T1P3A1L {
    var o: Orchestrator;
    var rcfg: int;

    start state Init {
        entry {
            o = new Orchestrator((p=1, a=3, l=1));
            rcfg = 3;
            goto Running;
        }
    }

    state Running {
        entry {
            if (rcfg == 0) {
                goto Finished;
            }
            if ($) {
                send o, eReconfig;
                rcfg = rcfg - 1;
            }
            goto Running;
        }
    }

    state Finished {}
}

machine T2P3A1L {
    var o: Orchestrator;
    var rcfg: int;

    start state Init {
        entry {
            o = new Orchestrator((p=2, a=3, l=1));
            rcfg = 3;
            goto Running;
        }
    }

    state Running {
        entry {
            if (rcfg == 0) {
                goto Finished;
            }
            if ($) {
                send o, eReconfig;
                rcfg = rcfg - 1;
            }
            goto Running;
        }
    }

    state Finished {}
}

machine T2P5A1L {
    var o: Orchestrator;
    var rcfg: int;

    start state Init {
        entry {
            o = new Orchestrator((p=2, a=5, l=1));
            rcfg = 2;
            goto Running;
        }
    }

    state Running {
        entry {
            if (rcfg == 0) {
                goto Finished;
            }
            if ($) {
                send o, eReconfig;
                rcfg = rcfg - 1;
            }
            goto Running;
        }
    }

    state Finished {}
}

machine T3P5A1L {
    var o: Orchestrator;
    var rcfg: int;

    start state Init {
        entry {
            o = new Orchestrator((p=3, a=5, l=1));
            rcfg = 3;
            goto Running;
        }
    }

    state Running {
        entry {
            if (rcfg == 0) {
                goto Finished;
            }
            if ($) {
                send o, eReconfig;
                rcfg = rcfg - 1;
            }
            goto Running;
        }
    }

    state Finished {}
}

machine T3P3A3L {
    var o: Orchestrator;
    var rcfg: int;

    start state Init {
        entry {
            o = new Orchestrator((p=3, a=3, l=3));
            rcfg = 3;
            goto Running;
        }
    }

    state Running {
        entry {
            if (rcfg == 0) {
                goto Finished;
            }
            if ($) {
                send o, eReconfig;
                rcfg = rcfg - 1;
            }
            goto Running;
        }
    }

    state Finished {}
}

test t1P3A1L [main = T1P3A1L]:
	assert OneValueDecided in (union VerticalPaxos, { T1P3A1L });

test t2P3A1L [main = T2P3A1L]:
	assert OneValueDecided in (union VerticalPaxos, { T2P3A1L });

test t2P5A1L [main = T2P5A1L]:
	assert OneValueDecided in (union VerticalPaxos, { T2P5A1L });

test t3P3A3L [main = T3P3A3L]:
    assert OneValueDecided in (union VerticalPaxos, { T3P3A3L });

hint P2C(e0: eDecided, e1: eP2A) {}