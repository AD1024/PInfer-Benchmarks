test tcOneNode [main = OneNode]:
  assert Safety in union RingLeader, { OneNode };

test tcTwoNodes [main = TwoNodes]:
  assert Safety in union RingLeader, { TwoNodes };

test tcThreeNodes [main = ThreeNodes]:
  assert Safety in union RingLeader, { ThreeNodes };

test tcFiveNodes [main = FiveNodes]:
  assert Safety in union RingLeader, { FiveNodes };

test tcTenNodes [main = TenNodes]:
  assert Safety in union RingLeader, { TenNodes };
