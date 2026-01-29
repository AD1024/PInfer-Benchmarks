import os

num_traces = [
    10000 #, 20000, 30000, 40000, 50000
]

# public benchmarks
benchmarks = ['ring_leader', 'consensus', '2PC', 'sharded_kv', 'firewall', 'paxos_hint', 'distributed_lock', 'Raft', 'Raft_hint', 
              'vertical_paxos', 'ChainReplication', 'lockserver', 'ClockBound']

# benchmarks = ['ring_leader', 'consensus', '2PC', 'sharded_kv', 'firewall', 'paxos_hint', 'distributed_lock', 'Raft_hint', 
#               'vertical_paxos', 'ChainReplication', 'lockserver', 'ClockBound', 'JournalLeaderElection', 'Kermit2PC']

config_events = {
    'paxos': 'ePaxosConfig',
    '2PC': 'eMonitor_AtomicityInitialize'
}

#export PINFER_TRACE_DIR=
trace_dir = os.environ['PINFER_TRACE_DIR']

configurations = {
    '2PC': ['tcC2P3T3', 'tcC3P4T3', 'tcC3P5T3', 'tcSingleClientNoFailure'],
    'ClockBound': ['tcC1R3', 'tcC2R3', 'tcC3R3', 'tcC4R3', 'tcC3R5'],
    'consensus': ['tcOneNode', 'tcTwoNodes', 'tcThreeNodes', 'tcFiveNodes', 'tcFourNodes'],
    'paxos': ['testBasicPaxos1on1', 'testBasicPaxos3on5', 'testBasicPaxos3on3', 'testBasicPaxos3on1', 'testBasicPaxos2on3', 'testBasicPaxos2on2'],
    'paxos_hint': ['testBasicPaxos1on1', 'testBasicPaxos3on5', 'testBasicPaxos3on3', 'testBasicPaxos3on1', 'testBasicPaxos2on3', 'testBasicPaxos2on2'],
    'Raft': ['oneClientFiveServersReliable', 'oneClientFiveServersUnreliable', 'twoClientsThreeServersReliable', 'twoClientsThreeServersUnreliable'],
    'Raft_hint': ['oneClientFiveServersReliable', 'oneClientFiveServersUnreliable', 'twoClientsThreeServersReliable', 'twoClientsThreeServersUnreliable'],
    'ring_leader': ['tcOneNode', 'tcTwoNodes', 'tcThreeNodes', 'tcFiveNodes'],
    'lockserver': ['tcOneNode', 'tcThreeNodes', 'tcFourNodes', 'tcFiveNodes'],
    'distributed_lock': ['tcThreeNodes', 'tcFourNodes', 'tcFiveNodes', 'tcSixNodes'],
    'sharded_kv': ['tcTwoNodes', 'tcThreeNodes', 'tcFourNodes', 'tcFiveNodes'],
    'vertical_paxos': ['t1P3A1L', 't2P3A1L', 't2P5A1L', 't3P3A3L'],
    'ChainReplication': ['tc1C1K', 'tc1C3K', 'tc3C1K', 'tc3C3K'],
    'firewall': ['tcI3E1', 'tcI1E3', 'I3E3', 'I4E5'],
    '3FS_DataStorage': ['tcOneClientWriteNoFailure', 'tcTwoClientsWriteNoFailure', 'tcThreeClientsWriteNoFailure', 'tcOneClientWriteUnreliableDetector', 'tcTwoClientsWriteUnreliableDetector'],
    '3FS_RDMASocket': ['tcPingPong', 'tcOneWay', 'tcTwoWay'],
    'MarianaStorage': ['tcSingleProducerConsumer', 'tcMultipleProducerConsumer', 'tcSingleProducerConsumerMultiRequest', 'tcMultipleProducerConsumerMultiRequest'],
    'PhysaliaBlessingMigrator': ['tcSinglePrimaryKey', 'tcSinglePrimaryKeyWithFailures', 'tcSinglePrimaryKeyWithFailuresAndDCSweeper',
                                 'tcMultiplePrimaryKeys', 'tcMultiplePrimaryKeysWithFailures', 'tcMultiplePrimaryKeysWithFailuresAndDCSweeper'],
    'IndexBrickManager': ['tcSingleClient_Get_WithSplitsMerges_OnRandomPerkle',
                          'tcMultipleClient_Get_WithSplitsMerges_OnRandomPerkle',
                          'tcSingleClient_Put_WithSplitsMerges_OnRandomPerkle',
                          'tcMultipleClient_Put_WithSplitsMerges_OnRandomPerkle',
                          'tcSingleClient_GetPut_WithSplitsMerges_OnRandomPerkle',
                          'tcMultipleClient_GetPut_WithSplitsMerges_OnRandomPerkle'],
    'JournalLeaderElection': ['tcOneNodeNoFailures', 'tcTwoSequentialNodes', 'tcThreeNodes', 'tcTwoNodesNoFailures'],
    'Kermit2PC': ['tcSingleClientSingleRouterNoFailures', 'tcMultipleClientsSingleRouterNoFailures',
                  'tcMultipleClientsMultipleRoutersNoFailures', 'tcSingleClientSingleRouterWithFailures',
                  'tcMultipleClientsMultipleRoutersWithFailures']
}

event_combs = {
    'Raft': [
        ('eEntryApplied', 'eBecomeLeader', 'eRaftConfig'),
        ('eBecomeLeader', 'eRequestVoteReply', 'eRaftConfig'),
    ],
    'Raft_hint': [
        ('eNotifyLog', 'eRaftConfig'),
        ("eRaftConfig", "eBecomeLeader", "eEntryApplied"),
    ],
    'vertical_paxos': [
        ('eP1A', 'eP1B', 'eP2A', 'eP2B', 'eDecided', 'ePaxosConfig')
    ],
    '2PC': [
        ('ePrepareReq', 'ePrepareSuccess', 'ePrepareFailure', 'eWriteTransSuccess',
         'eWriteTransTimeout', 'eWriteTransFailure', 'eCommitTrans', 'eAbortTrans', 'eMonitor_AtomicityInitialize')
    ],
    'ring_leader': [
        ('eNominate', 'eBecomeLeader')
    ],
    'ChainReplication': [
        ('eWriteRequest', 'eWriteResponse', 'eReadSuccess', 'eReadFail', 'eNotifyLog')
    ],
    '3FS_DataStorage': [
        ('eWriteReq', 'eWriteResp', 'eWriteWork', 'eSystemConfig', 'eWriteOpFinishResult', 'eCommitOpResult',
         'eReadWorkDone', 'eWriteWorkDone', 'eCommitWorkDone', 'eNewRoutingInfo',
         'eNewRoutingInfo', 'eSyncStartReq', 'eSyncDoneResp', 'eStopMonitorTargetStates')
    ],
    '3FS_RDMASocket': [
        ('eSendBytes', 'eRecvBytes', 'eRecvBytesResp', 'ePostSend',
         'ePostRecv', 'ePollSendCQReturn', 'ePollRecvCQReturn', 'eConfig',)
    ],
    'MarianaStorage': [
        ('eProduceRequest', 'eProduceResponse', 'eFetchRequest', 'eFetchResponse', 'eElectLeaderRequest',
         'ePutSegmentsRequest', 'ePutSegmentsResponse', 'eGetSlicedSegmentsRequest', 'eGetSlicedSegmentsResponse')
    ],
    'IndexBrickManager': [
        ('eBrickGetResp', 'eBrickGetReq', 'eBrickPutResp', 'eBrickPutReq')
    ],
    'JournalLeaderElection': [
        ('eSpec_ECRead', 'eSpec_DataRecordCommittedOnLeader', 'eSpec_CRead', 'eSpec_LeadershipLeaderCReads'
         , 'eSpec_AcquireLeadership', 'eSpec_DataRecordCommittedToJournal', 'eSpec_RelinquishLeadership')
    ],
    'Kermit2PC': [
        ('eCommitRead', 'eCommitWrite',
         'eLeadShardCommitRsp', 'eCommitTxnRsp',
         'eShardAbortTxn', 'eShardCommitTxn')
    ]
}

module_names = {
    'lockserver': 'LockServerMod',
    '2PC': 'TwoPhaseCommit, TwoPCClient, FailureInjector',
    'ChainReplication': 'Client, ChainRepEnv, FailureInjector',
    'ClockBound': 'ClockBound',
    'consensus': 'ConsensusEPR',
    'distributed_lock': 'DistributedLockMod',
    'firewall': 'FirewallMod',
    'paxos': 'Paxos',
    'paxos_hint': 'Paxos',
    'Raft': 'Server, Timer, Client, View',
    'Raft_hint': 'Server, Timer, Client, View',
    'ring_leader': 'RingLeader',
    'sharded_kv': 'ShardedKV',
    'vertical_paxos': 'VerticalPaxos', 
    'JournalLeaderElection': 'Node',
    'Kermit2PC': 'Kermit2PC, ClockBound'
}

test_interface_names = {
    'lockserver': ['OneNode', 'ThreeNodes', 'FourNodes', 'FiveNodes', 'TenNodes'],
    '2PC': ['C2P3T3', 'C3P4T3', 'C3P5T3', 'SingleClientNoFailure', 'C4P5T4'],
    'ChainReplication': ['SingleClientTest', 'SingleClientMultipleKeys', 'MultipleClientSingleKey', 'MultipleClientMultipleKeys', 'PruningTestcase'],
    'ClockBound': ['C1R3', 'C2R3', 'C3R3', 'C4R3', 'C3R5', 'C5R5'],
    'consensus': ['OneNode', 'TwoNodes', 'ThreeNodes', 'FiveNodes', 'FourNodes', 'TenNodes'],
    'distributed_lock': ['ThreeNodes', 'FourNodes', 'FiveNodes', 'SixNodes', 'TenNodes'],
    'firewall': ['I3E1', 'I1E3', 'I3E3', 'I4E5', 'I5E6'],
    'paxos': ['BasicPaxos1on1', 'BasicPaxos3on5', 'BasicPaxos3on3', 'BasicPaxos3on1', 'BasicPaxos2on3', 'BasicPaxos2on2', 'BasicPaxos4on4'],
    'paxos_hint': ['BasicPaxos1on1', 'BasicPaxos3on5', 'BasicPaxos3on3', 'BasicPaxos3on1', 'BasicPaxos2on3', 'BasicPaxos2on2', 'BasicPaxos4on4'],
    'Raft': ['OneClientFiveServersReliable', 'OneClientFiveServersUnreliable', 'TwoClientsThreeServersReliable', 'TwoClientsThreeServersUnreliable', 'ThreeClientsOneServerReliable'],
    'ring_leader': ['OneNode', 'TwoNodes', 'ThreeNodes', 'FiveNodes'],
    'sharded_kv': ['TwoNodes', 'ThreeNodes', 'FourNodes', 'FiveNodes', 'SevenNodes'],
    'vertical_paxos': ['T1P3A1L', 'T2P3A1L', 'T2P5A1L', 'T3P5A1L'],
    'JournalLeaderElection': ['OneNodeNoFailures', 'OneNode', 'TwoSequentialNodes',
                              'TwoNodesNoFailures', 'TwoNodesNoData', 'TwoNodes', 
                              'ThreeNodesNoData', 'ThreeNodes'],
    'Kermit2PC': ['SingleClientSingleRouterNoFailures', 'MultipleClientsSingleRouterNoFailures',
                  'MultipleClientsMultipleRoutersNoFailures', 'SingleClientSingleRouterWithFailures',
                  'MultipleClientsSingleRouterWithFailures', 'MultipleClientsMultipleRoutersWithFailures']
}