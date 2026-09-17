# -*- coding: utf-8 -*-
from engine import *

chapter(3, "The architecture at a glance", "Two planes, a shared entry path, and many isolated environments.",
 """Chapter three. The architecture at a glance. Before we follow a single request, I want you to see the whole system from a distance: what's shared, what's dedicated, and how the two connect. Then the next two chapters zoom into the two flows you need to know cold, the request lifecycle and tenant onboarding.""")

D = Diagram("The big picture")
D.box('cp', 640, 30, 640, 130, 'Shared control plane', 'provisioning · lifecycle · deployment config · tenant metadata', kind='cp', step=0, hl='0')
D.label(1310, 60, 'NOT on the request path', kind='cp', step=0, w=380, size='m')
D.zone(560, 300, 580, 470, 'Customer A · isolated', kind='dp', step=1)
D.box('a1', 600, 350, 500, 90, 'Shards + replicas', 'Jira · JSM · Confluence …', kind='dp', step=1, small=True)
D.box('a2', 600, 480, 500, 90, 'Dedicated data stores', 'customer A only', kind='dp', step=1, small=True)
D.box('a3', 600, 610, 500, 90, 'Egress Gateway', 'outbound policy', kind='deny', step=1, small=True)
D.arrow('cp', 'a1', step=1, kind='cp', fs='b', ts='t', fo=0.35, to=0.5, dashed=True, label='provisions & manages', loff=(-120, 0))
D.zone(1250, 300, 580, 470, 'Customer B · isolated', kind='dp', step=2)
D.box('b1', 1290, 350, 500, 90, 'Shards + replicas', '', kind='dp', step=2, small=True)
D.box('b2', 1290, 480, 500, 90, 'Dedicated data stores', 'customer B only', kind='dp', step=2, small=True)
D.box('b3', 1290, 610, 500, 90, 'Egress Gateway', '', kind='deny', step=2, small=True)
D.arrow('cp', 'b1', step=2, kind='cp', fs='b', ts='t', fo=0.75, to=0.5, dashed=True)
D.box('entry', 60, 300, 400, 170, 'Shared entry path', 'Global Edge · Router · Tenant Context Service', kind='shared', step=3, hl='3')
D.box('com', 60, 600, 400, 110, 'Commercial runtime', 'multi-tenant customers', kind='com', step=3, small=True)
D.arrow('entry', 'com', step=3, kind='com', fs='b', ts='t')
D.arrow('entry', 'a1', step=4, kind='shared', fs='r', ts='l', fo=0.5, to=0.5, via=[(530, 385), (530, 395)], name='e-a')
D.label(470, 250, 'requests', kind='shared', step=4, w=120, size='s')
D.label(60, 800, 'Data plane: **dedicated**.   Control plane: **shared**.   Entry path: **shared, and honest about it**.', kind='neutral', step=5, w=1800, size='m', align='center')
sid = D.build()
seg(sid, 0, """At the top is the shared control plane. It onboards tenants, provisions their environments, holds deployment configuration and tenant metadata, and manages each environment's lifecycle. Here's the property that matters most. It is not on the request path. Provisioning can take minutes and can fail. A request can't wait for that. So the control plane does its work, and then it gets out of the way.""")
seg(sid, 1, """Below it are the isolated environments. Customer A has its own shards and replicas for each product, its own dedicated data stores, and its own Egress Gateway for anything leaving. The control plane provisions and manages all of this, which is why that arrow is dashed. It's management, not traffic.""")
seg(sid, 2, """Customer B gets exactly the same thing, completely separate. And so do customer C, D and so on. Notice what's multiplied and what isn't. The environments are multiplied. The control plane is not. That's the whole economic argument of the design.""")
seg(sid, 3, """On the left is the entry path: the Global Edge, the Router, and the Tenant Context Service. It's shared by commercial and isolated tenants. Commercial customers keep flowing to the multi-tenant runtime exactly as before.""")
seg(sid, 4, """And isolated tenants' requests are routed into their own environment. We'll follow that path in detail in the next chapter.""", travel=travel(D.paths['e-a'], 'shared'))
seg(sid, 5, """So here's the summary to say out loud. The data plane is dedicated. The control plane is shared. And the entry path is shared too, and you should be honest about that, because a sharp infra interviewer will point it out. We'll cover exactly how you answer that challenge in the failures chapter.""")

sid = table("Two planes, opposite characteristics", ["", "Control plane", "Customer data plane"], [
 (0, ["Job", "Provisioning and lifecycle", "Serving customer traffic"]),
 (1, ["Shared?", "Shared across customers", "Dedicated per customer"], [None, 'cp', 'dp']),
 (2, ["How often", "Rarely", "Constantly"]),
 (3, ["On the request path?", "**No**", "Yes"], [None, 'deny', 'ok']),
], widths=[24, 38, 38])
seg(sid, 0, """Let's make the two planes precise, because interviewers like to probe the boundary. The control plane's job is provisioning and lifecycle. The data plane's job is serving customer traffic.""")
seg(sid, 1, """The control plane is shared across customers. The data plane is dedicated per customer.""")
seg(sid, 2, """The control plane acts rarely. The data plane works constantly.""")
seg(sid, 3, """And the control plane is not on the request path, while the data plane is. That gives you a great answer to a common question. What happens to isolated customers if the control plane goes down? Live traffic keeps being served. Onboarding, deploys and lifecycle changes wait. The trade-off you're making is simple: you give up the ability to change things during a control plane outage, and in exchange a control plane failure never becomes a customer outage.""")

sid = cards("The components, in one line each", [
 (0, "Global Edge", "Handles the request, forwards to the Router. **Not** placement.", 'shared'),
 (0, "Router", "Commercial or isolated? Cached tenant context.", 'shared'),
 (1, "Tenant Context Service", "Who the tenant is: identity, environment, entitlements.", 'shared'),
 (1, "Shard Manager", "Which shard serves this tenant right now?", 'dp'),
 (2, "Shard", "Logical isolated runtime for one tenant + one product.", 'dp'),
 (2, "Shard configuration repository", "Source of truth for placement. Cache in front.", 'dp'),
 (3, "Shard descriptor", "Per-shard compute, memory, networking, storage, keys, monitoring.", 'cp'),
 (3, "Egress Gateway", "Centralised outbound policy enforcement.", 'deny'),
], cols=2)
seg(sid, 0, """Here's your component vocabulary, one line each. Use these exact words in the interview, consistently. The Global Edge handles the request and forwards it to the Router. It does not decide placement. The Router answers one question: commercial or isolated? It uses cached tenant context.""")
seg(sid, 1, """The Tenant Context Service holds who the tenant is: identity, environment and entitlements. It's relatively static. The Shard Manager answers a different question: which shard serves this tenant right now? That's dynamic.""")
seg(sid, 2, """A shard is a logical isolated runtime for one tenant and one product, and it holds several replicas. The shard configuration repository is the source of truth for placement, with a cache in front purely for speed.""")
seg(sid, 3, """A shard descriptor sets that shard's own compute, memory, networking, storage, keys and monitoring. And the Egress Gateway is where outbound policy is enforced, centrally. If you ever hear yourself saying a shard is an instance, or a cache is the source of truth, stop and correct it. Those are the two mistakes that tell an interviewer you've only heard this architecture described.""")
