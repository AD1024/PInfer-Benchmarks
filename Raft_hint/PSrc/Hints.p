enum EqEnum {
    YES, NO
}
type LogIndexPair = (log: seq[tServerLog], idx: LogIndex);

hint LogMatching (e0: eNotifyLog, e1: eNotifyLog) {
    @prop(refl, antisym, sym)
    // LogMatching property of Raft
    fun logMatching(e0: (timestamp: tTS, server: Server, log: seq[tServerLog]), e1: (timestamp: tTS, server: Server, log: seq[tServerLog])): EqEnum {
        var n: LogIndex;
        var i: LogIndex;
        if (sizeof(e0.log) < sizeof(e1.log)) {
            n = sizeof(e0.log);
        } else {
            n = sizeof(e1.log);
        }
        i = n - 1;
        while (i >= 0 && e0.log[i] != e1.log[i]) {
            i = i - 1;
        }
        while (i >= 0) {
            if (e0.log[i] != e1.log[i]) {
                return NO;
            }
            i = i - 1;
        }
        return YES;
    }
}

hint LeaderComplete(e0: eBecomeLeader, e1: eBecomeLeader) {
    @prop(refl, antisym)
    // LeaderComplete property of Raft
    fun logContains(p1: tBecomeLeader, p2: tBecomeLeader): EqEnum {
        var i: LogIndex;
        var j: LogIndex;
        var found: bool;
        i = 0;
        while (i < p1.commitIndex) {
            j = 0;
            found = false;
            while (j < sizeof(p2.log)) {
                if (p1.log[i] == p2.log[j]) {
                    found = true;
                    break;
                }
                j = j + 1;
            }
            if (!found) return NO;
            i = i + 1;
        }
        return YES;
    }
}
