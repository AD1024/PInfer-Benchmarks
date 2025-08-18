hint Linear(e0: eReadSuccess, e1: eWriteResponse) {}
enum Bool { Yes, No }
hint Hist(e0: eNotifyLog, e1: eNotifyLog) {
    @prop(refl, antisym, trans)
    fun prefixOf(xs: (epoch: tEpoch, position: tPos, log: seq[tRid], sent: seq[tRid]), ys: (epoch: tEpoch, position: tPos, log: seq[tRid], sent: seq[tRid])): Bool {
        var i: int;
        var e1: int;
        var e2: int;
        var x: seq[tRid];
        var y: seq[tRid];
        x = xs.log;
        y = ys.log;
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
    include_guards = e0.position <= e1.position;
    term_depth = 1;
}

hint Inprocess(e0: eNotifyLog, e1: eNotifyLog) {
    @prop(refl)
    fun UnionEq(xs: (epoch: tEpoch, position: tPos, log: seq[tRid], sent: seq[tRid]), ys: (epoch: tEpoch, position: tPos, log: seq[tRid], sent: seq[tRid])): Bool {
        var i: tRid;
        foreach (i in xs.log) {
            if (!contains(ys.log, i) && !contains(ys.sent, i)) {
                return No;
            }
        }
        return Yes;
    }
    include_guards = e0.position <= e1.position;
    term_depth = 1;
}