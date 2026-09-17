# -*- coding: utf-8 -*-
from engine import *

chapter(4, "The request lifecycle", "Follow one request from the client to the right isolated runtime, and see exactly where it can never go.",
 """Chapter four is the request lifecycle. This is the diagram an interviewer expects you to be able to draw from memory, so we're going to build it one component at a time. For every box, I want you to know three things. What question it answers. Why it's a separate component. And what happens when it fails.""")

D = Diagram("One request, end to end")
D.box('client', 60, 70, 210, 110, 'Client', 'browser or app', kind='neutral', step=0)
D.box('edge', 340, 70, 240, 110, 'Global Edge', 'initial handling', kind='shared', step=0, hl='0')
D.arrow('client', 'edge', step=0, kind='neutral', name='c-e')
D.box('router', 650, 70, 270, 110, 'Router', 'commercial or isolated?', kind='shared', step=1, hl='1,2,11')
D.arrow('edge', 'router', step=1, kind='shared', name='e-r')
D.label(330, 214, 'in-memory tenant context cache\nmiss → fetch, then populate', kind='shared', step=2, w=300, size='s', align='right')
D.box('tcs', 650, 330, 270, 110, 'Tenant Context Service', 'identity · environment · entitlements', kind='shared', step=2, hl='2', small=True)
D.arrow('router', 'tcs', step=2, kind='shared', fs='b', ts='t', fo=0.3, to=0.3, dashed=True)
D.arrow('tcs', 'router', step=2, kind='shared', fs='t', ts='b', fo=0.55, to=0.55, dashed=True)
D.box('com', 1000, 72, 250, 106, 'Commercial runtime', 'multi-tenant', kind='com', step=3, hl='3,10', small=True)
D.arrow('router', 'com', step=3, kind='com', fs='r', ts='l', fo=0.5, to=0.5)
D.label(930, 28, 'commercial', kind='com', step=3, w=120, size='s')
D.label(1000, 186, '✕ never for an\nisolated tenant', kind='deny', step=10, w=260, size='m', hl='10')
D.box('sm', 1000, 250, 250, 110, 'Shard Manager', 'which shard, right now?', kind='dp', step=4, hl='4,5,11')
D.arrow('router', 'sm', step=4, kind='dp', fs='b', ts='l', fo=0.9, via=[(893, 305)], name='r-sm')
D.label(905, 196, 'isolated', kind='dp', step=4, w=100, size='s')
D.box('repo', 1000, 470, 250, 120, 'Shard configuration repository', 'source of truth + cache', kind='dp', step=5, hl='5', small=True)
D.arrow('sm', 'repo', step=5, kind='dp', fs='b', ts='t', fo=0.4, to=0.4, dashed=True, label='lookup', loff=(-50, 6))
D.zone(1320, 40, 560, 750, 'Isolated environment', kind='dp', step=6)
D.box('shard', 1370, 90, 460, 110, 'Isolated shard', 'Tenant A · Jira · Shard-123', kind='dp', step=6, hl='6')
D.arrow('sm', 'shard', step=6, kind='dp', fs='r', ts='l', via=[(1300, 305), (1300, 145)], name='sm-sh')
for k, x in enumerate((1370, 1530, 1690)):
    D.box('r%d' % k, x, 260, 140, 90, 'Replica %d' % (k + 1), '', kind='dp', step=7, hl='7', small=True)
D.arrow('shard', 'r1', step=7, kind='dp', fs='b', ts='t', name='sh-r')
D.label(1374, 360, 'AWS Auto Scaling', kind='dp', step=7, w=200, size='s', align='left')
D.box('data', 1370, 430, 460, 100, 'Dedicated data stores', 'this tenant only', kind='dp', step=8, hl='8')
D.arrow('r1', 'data', step=8, kind='dp', fs='b', ts='t', name='r-d')
D.box('egress', 1370, 600, 460, 100, 'Egress Gateway', 'policy checked on the way out', kind='deny', step=9, hl='9')
D.arrow('data', 'egress', step=9, kind='deny', fs='b', ts='t', name='d-eg')
D.box('ext', 1000, 640, 240, 96, 'External systems', 'only if policy allows', kind='neutral', step=9, small=True)
D.arrow('egress', 'ext', step=9, kind='deny', fs='l', ts='r', name='eg-x')
D.label(90, 540, '**Fail closed**\nNo healthy shard → error, retry\nNo tenant context → reject\nNever → commercial', kind='deny', step=10, w=520, size='m', hide=11)
D.label(90, 540, '**Two questions, two owners**\nRouter: who is this tenant?\nShard Manager: where does it run now?', kind='ok', step=11, w=560, size='m')
sid = D.build()
P = D.paths

seg(sid, 0, """A request starts at the client and arrives at the Global Edge. The edge does the initial handling and forwards the request on. Here's the first thing people get wrong in interviews. They say the edge decides where the tenant lives. It doesn't. Placement is two components further down. If you give the edge that job, the interviewer will immediately ask how the edge knows about shard replacements, and you won't have a good answer.""",
    travel=travel(P['c-e'], 'shared'))
seg(sid, 1, """Next is the Router. The Router answers exactly one question. Is this tenant commercial, or isolated? That's it. The important point here is how narrow that job is. The Router sits on every single request, commercial and isolated, so whatever it does has to be cheap and it has to be stable.""",
    travel=travel(P['e-r'], 'shared'))
seg(sid, 2, """To answer that question quickly, the Router keeps tenant context in an in-memory cache. Tenant context is relatively static information. Who the tenant is, which environment they belong to, and their entitlements. On a cache hit, the Router answers immediately. On a miss, it calls the Tenant Context Service and populates its cache. Why is caching safe here? Because tenant context changes rarely. It only changes when a tenant moves environment or entitlement, for example when they migrate from commercial to isolated. And those events are exactly where invalidation happens. Hold on to that, because it comes back when we talk about failures.""")
seg(sid, 3, """If the tenant is commercial, the request goes to the commercial, multi-tenant runtime, exactly like it always did. Nothing about isolated cloud changes the commercial path.""")
seg(sid, 4, """If the tenant is isolated, the request goes to the Shard Manager. And the Shard Manager answers a different question. Which shard serves this tenant, right now? Notice the words right now. Placement moves. A shard can be replaced because of a failure, maintenance, a deployment, a migration, or a capacity change. That's the core reason the Shard Manager is its own component, and we'll spend a whole chapter on why.""",
    travel=travel(P['r-sm'], 'dp'))
seg(sid, 5, """The Shard Manager looks up placement in the shard configuration repository. The repository is the source of truth. There's a cache in front of it for speed, but the cache is never authoritative. If an interviewer asks what happens when that cache is lost, the answer is simple and strong. You pay latency while it refills. You don't lose correctness. If you ever describe a cache as the place placement lives, you have no answer to that question.""")
seg(sid, 6, """Now the request enters the isolated environment and reaches the shard. Be precise about what a shard is. A shard is a logical isolated deployment for one tenant and one product. Here, tenant A's Jira, shard one two three. It is not a machine. And it's not a data partition. People hear the word shard and think of splitting data for scale. Say early that it isn't that, or your whole explanation drifts.""",
    travel=travel(P['sm-sh'], 'dp'))
seg(sid, 7, """Inside the shard there are several replicas. When traffic rises, replicas scale with AWS Auto Scaling. The shard itself doesn't change, and neither does its placement. If one replica fails, the shard absorbs it. The tenant to shard mapping stays exactly the same. That distinction, replica failure versus shard replacement, is one of the most probed points in this whole design.""",
    travel=travel(P['sh-r'], 'dp'))
seg(sid, 8, """The replica reads and writes the tenant's dedicated data stores. This tenant only. Nothing about this customer's data sits in a shared store.""",
    travel=travel(P['r-d'], 'dp'))
seg(sid, 9, """And if anything needs to leave, it goes through the Egress Gateway. Outbound data goes through one place, where policy is checked, and it only reaches an external system if the policy allows it. Why one place? Because outbound data control is a compliance concern that applies to every product. If a hundred and seventy-eight teams each wrote their own policy, the guarantee would only be as strong as the weakest one. And don't name a policy engine unless you're certain. Say policy-driven enforcement.""",
    travel=travel(P['d-eg'] + P['eg-x'][1:], 'deny'))
seg(sid, 10, """Now the failure view, and this is where you earn the Staff signal. An isolated tenant's request never falls back to commercial. Not when a shard is down. Not when tenant context is unavailable. If no healthy shard is found, the request errors and is retried. If the Router can't get tenant context, the request is rejected. Why be that strict? Because an outage is a reliability problem, but serving an isolated customer from shared infrastructure is a compliance failure. The interviewer may push back and say some service is better than none. Your answer is a clear no. You buy availability with replicas inside the shard, not with an escape route to shared infrastructure.""")
seg(sid, 11, """So here's the whole lifecycle in one sentence you can say out loud. The edge receives it, the Router decides commercial or isolated from cached tenant context, the Shard Manager decides which shard serves that tenant right now, the shard's replicas do the work against dedicated data, and anything leaving goes through the Egress Gateway. Two questions, two owners. Who is this tenant, and where does it run right now. If you can draw this and say that sentence, you've got the backbone of the interview.""")

question("An isolated tenant's shard is unhealthy. Why not send the request to the commercial runtime instead?", 8,
 "Because that would serve an isolated customer from shared infrastructure, which is exactly what they pay to prevent. The request errors and retries instead. Availability comes from replicas inside the shard, not from an escape route.",
 "It names the trade explicitly: reliability problem versus compliance failure, and says where availability comes from instead.",
 "Whether you'll weaken a hard guarantee under availability pressure, and whether you can hold the line with a reason.",
 ["What stops a bug from sending it to commercial anyway?", "How often did failing closed cause errors?", "What's your availability target for a shard?"],
 narr=dict(
  short="""Here's the thirty-second answer. Because that would serve an isolated customer from shared infrastructure, and that's exactly what they're paying to prevent. So the request errors and is retried. We get availability from replicas inside the shard, not from an escape route to commercial.""",
  strong="""Why is that strong? Because it doesn't hedge. It names the trade out loud. An outage is a reliability problem. Serving from shared infrastructure is a compliance failure. And then it says where availability actually comes from. That last part matters, because it shows you didn't just refuse, you designed an alternative.""",
  testing="""What's the interviewer really testing? Whether you'll quietly weaken a hard guarantee when someone mentions availability. A Senior answer often says, well, it depends. The Staff answer says no, here's why, and here's how we stayed available anyway.""",
  follow="""Expect the follow-ups. First, what stops a bug from sending it to commercial anyway? The answer is three independent locks: the Router fails closed, the commercial side refuses tenants locked as migrated, and after the rollback window there's no data there to serve. Second, how often did failing closed cause errors? Don't invent a number you can't defend. And third, the availability target, which we cover in the operations chapter."""))
