spec UpdatePropAndInprocess observes eNotifyLog {
    var posToLog: map[tEpoch, map[int, seq[tRid]]];
    var posToSent: map[tEpoch, map[int, seq[tRid]]];

    start state Monitoring {
        entry {
            posToLog = default(map[tEpoch, map[int, seq[tRid]]]);
            posToSent = default(map[tEpoch, map[int, seq[tRid]]]);
        }

        on eNotifyLog do (input: (epoch: tEpoch, position: tPos, log: seq[tRid], sent: seq[tRid])) {
            var i: tPos;
            if (!(input.epoch in keys(posToLog))) {
                posToLog[input.epoch] = default(map[int, seq[tRid]]);
                posToSent[input.epoch] = default(map[int, seq[tRid]]);
            }
            posToLog[input.epoch][input.position] = input.log;
            posToSent[input.epoch][input.position] = input.sent;
            foreach (i in keys(posToLog[input.epoch])) {
                if (i <= input.position) {
                    // UpdatePropagation
                    assert isPrefixOf(posToLog[input.epoch][i], input.log) == Yes;
                    // Inprocess request
                    assert posToLog[input.epoch][i] == merge(input.log, posToSent[input.epoch][i]);
                }
            }
        }
    }

    fun isPrefixOf(x: seq[tRid], y: seq[tRid]): Bool {
        var i: int;
        var e1: tRid;
        var e2: tRid;
        if (sizeof(x) > sizeof(y)) {
            return No;
        }
        i = 0;
        while (i < sizeof(x)) {
            e1 = x[i];
            e2 = y[i];
            if (!(e1 == e2)) {
                return No;
            }
            i = i + 1;
        }
        return Yes;
    }
}

fun contains(xs: seq[tRid], x: tRid): bool {
    var i: int;
    i = 0;
    while (i < sizeof(xs)) {
        if (xs[i] == x) {
            return true;
        }
        i = i + 1;
    }
    return false;
}

fun merge(x: seq[tRid], y: seq[tRid]): seq[tRid] {
    var i: int;
    var memo: set[tRid];
    var res: seq[tRid];
    res = default(seq[tRid]);
    memo = default(set[tRid]);
    i = 0;
    res = x;
    while (i < sizeof(x)) {
        memo += (x[i]);
        res += (sizeof(res), x[i]);
        i = i + 1;
    }
    while (i < sizeof(y)) {
        if (!(y[i] in memo)) {
            res += (sizeof(res), y[i]);
        }
        i = i + 1;
    }
    i = 0;
    return res;
}