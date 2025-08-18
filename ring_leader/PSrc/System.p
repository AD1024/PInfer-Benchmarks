type tBallot = int;
event eNominate: (ballot: tBallot, nxt: tBallot);
event eBecomeLeader: (ballot: tBallot);

event eConfig: (nxt: machine, nxtBallot: tBallot);
event eStart;

machine Node {
    var ballot: tBallot;
    var nxt: machine;
    var nxtBallot: tBallot;

    start state Init {
        entry (cfg: (ballot: tBallot)) {
            ballot = cfg.ballot;
        }

        on eConfig do (cfg: (nxt: machine, nxtBallot: tBallot)) {
            nxt = cfg.nxt;
            nxtBallot = cfg.nxtBallot;
            goto Nominating;
        }
        defer eNominate;
    }

    state Nominating {
        entry {
            if ($) {
                send nxt, eNominate, (ballot=ballot, nxt=nxtBallot);
            }
        }

        on eNominate do (n: (ballot: tBallot, nxt: tBallot)) {
            if (n.ballot == ballot) {
                announce eBecomeLeader, (ballot=ballot,);
            } else if (n.ballot < ballot) {
                send nxt, eNominate, (ballot=ballot, nxt=nxtBallot);
            } else {
                send nxt, eNominate, (ballot=n.ballot, nxt=nxtBallot);
            }
        }
    }
}

spec Safety observes eBecomeLeader {
    var ballot: tBallot;

    start state Monitoring {
        entry {
            ballot = -1;
        }

        on eBecomeLeader do (b: (ballot: tBallot)) {
            if (ballot == -1) {
                ballot = b.ballot;
            }
            assert b.ballot == ballot;
        }
    }
}

module RingLeader = { Node };
