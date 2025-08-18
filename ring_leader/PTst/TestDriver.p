fun getBallot(now: seq[tBallot]): tBallot {
    var b: tBallot;
    b = choose(100);
    while (b in now) {
        b = choose(100);
    }
    return b;
}

fun SetupSystem(n: int) {
    var nodes: seq[machine];
    var ballots: seq[tBallot];
    var i: int;
    var node: machine;
    nodes = default(seq[machine]);
    ballots = default(seq[tBallot]);
    i = 0;
    while (i < n) {
        ballots += (sizeof(ballots), getBallot(ballots));
        nodes += (sizeof(nodes), new Node((ballot=ballots[i],)));
        i = i + 1;
    }
    i = 0;
    while (i < n) {
        send nodes[i], eConfig, (nxt=nodes[(i + 1) % n], nxtBallot=ballots[(i + 1) % n]);
        i = i + 1;
    }
    // i = 0;
    // while (i < n) {
    //     if ($) {
    //         send nodes[i], eStart;
    //     }
    //     i = i + 1;
    // }
}

machine OneNode {
    start state Start {
        entry {
            SetupSystem(1);
        }
    }
}

machine TwoNodes {
    start state Start {
        entry {
            SetupSystem(2);
        }
    }
}

machine ThreeNodes {
    start state Start {
        entry {
            SetupSystem(3);
        }
    }
}

machine FiveNodes {
    start state Start {
        entry {
            SetupSystem(5);
        }
    }
}

machine TenNodes {
    start state Start {
        entry {
            SetupSystem(10);
        }
    }
}

machine TwentyNodes {
    start state Start {
        entry {
            SetupSystem(20);
        }
    }
}
