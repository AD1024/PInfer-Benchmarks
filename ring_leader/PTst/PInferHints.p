hint SelfPendingMax (e0: eNominate, e1: eNominate) {
    @iff(pld.ballot == pld.nxt)
    fun vote_eq_nxt(pld: (ballot: tBallot, nxt: tBallot)): bool {
        return pld.ballot == pld.nxt;
    }
}