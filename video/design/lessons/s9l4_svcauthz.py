# -*- coding: utf-8 -*-
"""Chapter 9, Lesson 4 — service-to-service permissions."""
from lib import *

lesson_header('9.4', 'Design service-to-service permissions',
              'Workload identity &middot; policy distribution &middot; evaluate locally &middot; revocation',
              dict(reports='InterviewTV list only', latest='2026', level='Staff, Infrastructure',
                   conf='MEDIUM &mdash; single source', sources='InterviewTV.io'), 16,
              """Chapter nine, lesson four, and the last design in the course. LinkedIn has many """
              """services that call one another, and you need to decide which service may call which. """
              """This question has a trap at the very start: almost everyone begins with the policy """
              """language, and the policy is the easy part. The hard part is <i>identity</i> &mdash; """
              """proving that the caller is who it claims to be &mdash; and if you get that wrong, """
              """your beautiful policy engine is authorising a liar.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff, Infrastructure',
  'Named: <b>identity, authentication, authorization, policy storage, policy evaluation, caching, '
  'policy propagation, revocation, audit, zero trust, failure behaviour</b>'),
], """Single source, so medium confidence. But look at the order of the named topics: identity and """
     """authentication come before authorization, which is the correct order and is also the order """
     """most candidates reverse.""",
 ["""And three of the eleven &mdash; propagation, revocation, failure behaviour &mdash; are the """
  """distribution problem from lesson four point four. This is the denylist question wearing a """
  """security hat, and recognising that saves you half the design."""],
 caveat='Single source. The identity-plus-policy-distribution pattern underlies every service mesh and '
        'zero-trust system, so it transfers.',
 narration_caveat="""Single source. The identity plus policy distribution pattern underlies every """
                  """service mesh and zero-trust system, so the preparation transfers.""")

sid = beat('Why this is interesting', 'Authorization is easy. <b>Identity</b> is the whole problem.',
           '<div style="font-size:28px;line-height:1.72">'
           '<b>Authorization</b> is a lookup: may service A call service B? That is a set membership '
           'test. <span style="color:#a8e6a3">It is not hard.</span><br><br>'
           '<b>Authentication</b> is the hard part: <i>is the caller really service A?</i><br><br>'
           '<span style="color:#ff9a9a">If identity rests on something forgeable &mdash; an IP '
           'address, a hostname, a header saying <code>X-Service-Name: payments</code> &mdash; then '
           'any service that can reach the network can claim to be any other service, and your policy '
           'engine will cheerfully authorise it.</span><br><br>'
           '<b>That is what &ldquo;zero trust&rdquo; actually means:</b> being on the network is not '
           'evidence of anything. Identity must be <b>cryptographically provable</b> on every call.'
           '<br><br>'
           '<b>And there is a second trap:</b> this check is on <i>every internal call</i>. '
           '<span style="color:#ffd483">Millions per second, with a latency budget near zero. A '
           'network call to an auth service per request is unaffordable &mdash; so evaluation must be '
           'local.</span><br><br>'
           '<span style="color:#a8e6a3">Which makes this: identity (crypto) + policy distribution '
           '(lesson 4.4) + local evaluation.</span></div>',
           """Why is this interesting? Because authorization is easy and identity is the whole """
           """problem.""", step=0)
seg(sid, 1, """Authorization is a lookup: may service A call service B? That is a set membership test, """
            """and it is genuinely not hard.""")
seg(sid, 2, """Authentication is the hard part &mdash; is the caller really service A? If identity rests """
            """on something forgeable, like an I-P address, a hostname, or a header saying """
            """&ldquo;X-Service-Name: payments&rdquo;, then any service that can reach the network can """
            """claim to be any other service. And your policy engine will cheerfully authorise it, """
            """because the policy was never the weak link.""")
seg(sid, 3, """That is what zero trust actually means, stripped of the marketing: being on the network is """
            """not evidence of anything. Identity has to be cryptographically provable on every single """
            """call.""")
seg(sid, 4, """And there is a second trap. This check happens on every internal call &mdash; millions a """
            """second across a large fleet, with a latency budget near zero. A network call to a """
            """central authorisation service per request is completely unaffordable, so evaluation has """
            """to happen locally.""")
seg(sid, 5, """Which makes this question three things: identity, which is cryptography; policy """
            """distribution, which is lesson four point four again; and local evaluation. If you """
            """recognise the middle one, you have already designed a third of this.""")

think('Service A calls service B with a header saying "I am service A". What stops service C &mdash; '
      'which is compromised and sitting on the same network &mdash; from sending exactly the same '
      'header?',
      20,
      """Pause. Service A calls service B with a header saying &ldquo;I am service A&rdquo;. What stops """
      """service C, which has been compromised and sits on the same network, from sending exactly the """
      """same header? Say it out loud.""",
      """Hold that. If the answer is &ldquo;nothing&rdquo;, then every policy you write afterwards is """
      """decoration.""")

clarify('What I would clarify first', [
 ('What is the unit of identity &mdash; service, instance, or version?',
  '<b>Service is usually right.</b> Per-instance identity gives finer revocation but far more '
  'certificates to manage. Per-version lets you authorise a canary differently.'),
 ('Is this allow-listing calls, or full RBAC on operations?',
  '&ldquo;A may call B&rdquo; is a graph. &ldquo;A may call B.deleteUser but not B.deleteAccount&rdquo; '
  'is <b>much</b> richer, and the policy store and evaluation both change.'),
 ('Does identity need to propagate &mdash; A calls B which calls C <i>on behalf of a user</i>?',
  '<b>The hardest part of real systems.</b> B must be able to prove it is acting for the original '
  'caller, or C cannot make a correct decision.'),
 ('What is the latency budget for the check?',
  'Sub-millisecond means <b>local evaluation, no exceptions</b>. That one answer removes a whole class '
  'of design.'),
 ('Fail open or fail closed when policy is unavailable?',
  '<b>Ask explicitly.</b> Fail closed takes the site down on a policy outage. Fail open means an '
  'outage becomes a security hole. Neither is obviously right.'),
 ('How fast must a revocation take effect?',
  'Minutes is cheap. Seconds forces short-lived credentials or an active revocation channel &mdash; '
  'a much more expensive system.'),
], [
 """What is the unit of identity &mdash; the service, the instance, or the version? Service is usually """
 """right. Per-instance identity gives finer-grained revocation and far more certificates to manage. """
 """Per-version is genuinely useful, because it lets you authorise a canary differently from the stable """
 """release.""",
 """Is this allow-listing calls, or full role-based access control on operations? &ldquo;A may call """
 """B&rdquo; is a graph. &ldquo;A may call B's delete-user endpoint but not its delete-account """
 """endpoint&rdquo; is much richer, and both the policy store and the evaluation change """
 """substantially.""",
 """Does identity need to propagate? A calls B, which calls C, on behalf of a user. That is the hardest """
 """part of real systems &mdash; B has to be able to prove it is acting for the original caller, or C """
 """cannot make a correct decision. Ask, because it changes the token design.""",
 """What is the latency budget? Sub-millisecond means local evaluation with no exceptions, and that one """
 """answer removes an entire class of designs from consideration.""",
 """Fail open or fail closed when policy is unavailable? Ask explicitly rather than assuming. Fail """
 """closed takes the whole site down during a policy outage. Fail open turns an outage into a security """
 """hole. Neither is obviously right and it is the interviewer's call, not yours.""",
 """And how fast must a revocation take effect? Minutes is cheap. Seconds forces short-lived """
 """credentials or an active revocation channel, which is a materially more expensive system.""",
])

capacity('Capacity', [
 ('~1,000 services, ~100k instances', 'typical large fleet', '100k identities',
  'Small. <b>Identity issuance is not a scale problem</b>'),
 ('Internal calls', '~10M calls / s across the fleet', '10M authz checks / s',
  '<b>This is the number that decides everything</b>'),
 ('If each check were a network call', '10M/s &times; 1 ms RTT', '<b>impossible</b>',
  'A central authz service would need to be the largest system you own. <b>Rules it out</b>'),
 ('Local evaluation', 'in-process check against cached policy', '&asymp; 1&ndash;10 &micro;s',
  '<b>Free.</b> The check is a map lookup plus a signature verification'),
 ('Policy size: 1,000 services &times; ~50 rules', '50,000 rules &times; ~200 B', '&asymp; 10 MB',
  '<b>Replicate it everywhere.</b> It fits in every process &mdash; no partitioning needed'),
 ('Certificate issuance / rotation', '100k instances, 24 h certs', '&asymp; 1.2 issues / s',
  'Trivial. <b>Short-lived certs are affordable</b>, and they are also the revocation mechanism'),
], [
 """Numbers. About a thousand services across a hundred thousand instances, so a hundred thousand """
 """identities. Small &mdash; identity issuance is not a scale problem.""",
 """Internal calls, though: roughly ten million a second across a large fleet, so ten million """
 """authorisation checks a second. That is the number that decides everything.""",
 """If each check were a network call to a central service, ten million a second with a millisecond """
 """round trip is simply impossible &mdash; your authorisation service would have to be the largest """
 """system you own, and it would be on the critical path of every other system. That rules it out, and """
 """it rules it out with arithmetic rather than taste.""",
 """Local evaluation &mdash; an in-process check against cached policy &mdash; is one to ten """
 """microseconds. Effectively free. The check is a map lookup plus a signature verification.""",
 """Policy size: a thousand services with about fifty rules each is fifty thousand rules, around ten """
 """megabytes. Which means you replicate it everywhere. It fits in every process, so there is no """
 """partitioning problem &mdash; the third time in this course that the right answer to partitioning """
 """is &ldquo;you do not need to&rdquo;.""",
 """And certificate issuance with twenty-four hour lifetimes across a hundred thousand instances is """
 """about one a second. Trivial &mdash; which means short-lived certificates are affordable, and that """
 """matters because short lifetimes are also your revocation mechanism.""",
])

A = Arch('Identity, policy distribution, local evaluation', kicker='Architecture', height=800)

A.zone(60, 440, 700, 300, 'DATA PLANE — every call, locally')

A.box('ca',   540, 140, 230, 125, 'Identity authority', 'short-lived certs, SPIFFE', kind='ok', step=0, focus=[0, 1])
A.box('ctrl',  250, 150, 215, 110, 'Policy store', 'who may call whom', kind='ok', step=2, focus=[2, 3])

A.box('a',     95, 500, 170, 100, 'Service A', 'has identity', kind='info', step=1, focus=[1, 4], small=True)
A.box('sca',   95, 630, 170, 85, 'Sidecar/lib', 'holds cert', kind='shared', step=1, focus=1, small=True)
A.arrow('ca', 'sca', step=1, focus=1, dashed=True)

A.box('b',    560, 500, 170, 100, 'Service B', '', kind='info', step=4, focus=[4, 5], small=True)
A.box('scb',  560, 630, 170, 85, 'Sidecar/lib', 'verifies + evaluates', kind='ok', step=4, focus=[4, 5], small=True)
A.arrow('ca', 'scb', step=1, focus=1, dashed=True)
A.arrow('ctrl', 'scb', step=3, focus=3, dashed=True)
A.arrow('ctrl', 'sca', step=3, focus=3, dashed=True)

A.arrow('a', 'b', step=4, label='mTLS call', focus=4)

A.box('aud',  880, 500, 200, 110, 'Audit log', 'every decision', kind='dp', step=6, focus=6, small=True)
A.arrow('scb', 'aud', step=6, focus=6, dashed=True)

A.box('rev',  880, 150, 200, 110, 'Revocation', 'short TTL +<br>push for urgent', kind='shared',
      step=5, focus=5, small=True)
A.arrow('rev', 'ca', step=5, focus=5, dashed=True)

A.note(880, 320, 'Policy is ~10 MB. It fits in every process — replicate it, never query it per call.',
       step=3, kind='info', w=440)

A.narrate(0, """At the top, two control-plane components. An identity authority that issues short-lived """
             """certificates &mdash; S-P-I-F-F-E is the usual standard &mdash; and a policy store """
             """holding who may call whom.""")
A.narrate(1, """Every workload gets a cryptographic identity: a certificate naming the service, """
             """issued at startup and rotated every twenty-four hours. The private key never leaves """
             """the workload. That is what makes identity unforgeable &mdash; service C cannot claim to """
             """be A, because it does not have A's key.""",
          A.flow([(647, 260), (647, 400), (180, 630)]))
A.narrate(2, """The policy store holds the rules: which service may call which, and on which """
             """operations.""")
A.narrate(3, """And the policy is distributed as a signed bundle to every workload &mdash; about ten """
             """megabytes, so every process holds the whole thing. This is exactly the versioned push """
             """with a pull fallback from lesson four point four, which I would say out loud rather """
             """than re-deriving.""",
          A.flow([(465, 205), (645, 630)]))
A.narrate(4, """Now the actual call. Service A calls B over mutual T-L-S. Both sides present """
             """certificates, so B cryptographically knows who A is &mdash; not because A said so, but """
             """because A proved it.""",
          A.flow([(265, 550), (560, 550)]))
A.narrate(5, """B's sidecar verifies the certificate and evaluates the policy locally, in process. One """
             """to ten microseconds, no network call. And revocation works primarily through short """
             """certificate lifetimes &mdash; a revoked identity simply stops being renewed &mdash; """
             """with a push channel for the urgent cases.""")
A.narrate(6, """And every decision is written to an audit log. That is not optional in a security """
             """system: if you cannot answer &ldquo;who called what, and was it allowed&rdquo; six """
             """months later, you do not really have access control, you have a feeling about it.""",
          A.flow([(730, 672), (880, 555)]))
A.build()

sid = beat('Deep dive 1', 'Identity &mdash; mTLS, SPIFFE, and the bootstrap problem',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>What will not work:</b> IP allow-lists (IPs are reassigned and spoofable), hostnames '
           '(DNS is not authentication), shared secrets in config (<span style="color:#ff9a9a">one leak '
           'compromises everything, and rotation is a fleet-wide outage waiting to happen</span>).'
           '<br><br>'
           '<b>What works: a certificate per workload.</b><br>'
           '&bull; Each workload gets an X.509 cert with a <b>SPIFFE ID</b> &mdash; '
           '<code>spiffe://linkedin/ns/prod/sa/payments</code><br>'
           '&bull; Calls use <b>mutual TLS</b>: both sides present and verify certs<br>'
           '&bull; The callee learns the caller&rsquo;s identity from the <b>certificate</b>, not from '
           'a header<br>'
           '&bull; Short lifetime (hours) so <span style="color:#a8e6a3">rotation is routine and '
           'revocation is mostly just &ldquo;stop renewing&rdquo;</span><br><br>'
           '<b>And the question that separates answers &mdash; the bootstrap problem:</b><br>'
           '<i>How does a brand-new workload prove who it is in order to get its first certificate?</i>'
           '<br>'
           '&bull; You cannot use a certificate &mdash; it has none yet<br>'
           '&bull; <span style="color:#ffd483">You must root trust in the platform</span>: the '
           'orchestrator or cloud provider attests &ldquo;this workload is payments&rdquo; &mdash; a '
           'Kubernetes service-account token, or cloud instance identity<br>'
           '&bull; <b>Trust ultimately rests on whoever schedules the workload.</b> Say that out loud: '
           'there is no turtles-all-the-way-down answer</div>',
           """Deep dive one: identity, and the answer to what I asked you to pause on. First, what will """
           """not work.""", step=0)
seg(sid, 1, """I-P allow-lists fail because I-Ps get reassigned constantly in a dynamic fleet and can be """
            """spoofed. Hostnames fail because D-N-S is not authentication &mdash; it is a lookup, not """
            """a proof. And shared secrets in configuration fail because one leak compromises """
            """everything, and rotating them is a fleet-wide coordinated change that nobody wants to """
            """do, so in practice they never rotate.""")
seg(sid, 2, """What works is a certificate per workload. Each one gets an X five-oh-nine certificate """
            """carrying a S-P-I-F-F-E identity &mdash; a structured name like spiffe, LinkedIn, """
            """namespace prod, service account payments.""")
seg(sid, 3, """Calls use mutual T-L-S, so both sides present and verify certificates. And the crucial """
            """part: the callee learns the caller's identity from the certificate, not from a header. """
            """A header is a claim; a certificate is a proof.""")
seg(sid, 4, """Lifetimes are short &mdash; hours &mdash; which makes rotation routine rather than an """
            """event, and means revocation is mostly just &ldquo;stop renewing&rdquo;.""")
seg(sid, 5, """And now the question that separates good answers from great ones: the bootstrap problem. """
            """How does a brand new workload prove who it is in order to get its first certificate? You """
            """cannot use a certificate, because it does not have one yet.""")
seg(sid, 6, """You have to root trust in the platform. The orchestrator or the cloud provider attests """
            """that this workload is payments &mdash; a Kubernetes service account token, or a cloud """
            """instance identity document. Which means trust ultimately rests on whoever schedules the """
            """workload. I would say that explicitly, because there is no turtles-all-the-way-down """
            """answer, and pretending otherwise is worse than naming where the chain terminates.""")

sid = beat('Deep dive 2', 'Policy distribution and revocation &mdash; the same problem as 4.4',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Evaluation must be local</b> &mdash; 10M checks/s makes a network call per request '
           'impossible. So policy has to be <i>at</i> every workload.<br><br>'
           '<b>And that is exactly the denylist problem from lesson 4.4:</b><br>'
           '&bull; <b>Push</b> a signed, versioned policy bundle to every workload<br>'
           '&bull; Each workload tracks its bundle <b>version</b>; a gap triggers a pull<br>'
           '&bull; Workloads <b>export the age of their policy</b>, and you alert on age &mdash; not on '
           'whether the push job succeeded<br>'
           '&bull; <span style="color:#a8e6a3">Sign the bundle, so a compromised distribution channel '
           'cannot inject policy</span><br><br>'
           '<b>Revocation is the asymmetric case &mdash; same as removals in 4.4:</b><br>'
           '&bull; <b>Granting</b> access late is mildly annoying<br>'
           '&bull; <b>Revoking</b> late means a compromised service keeps its access. '
           '<span style="color:#ff9a9a">That is the one that matters.</span><br>'
           '&bull; Primary mechanism: <b>short certificate lifetimes</b> &mdash; revocation is '
           '&ldquo;stop renewing&rdquo;, bounded by the TTL<br>'
           '&bull; For urgent cases: a push to the identity authority plus a deny-list of revoked '
           'IDs &mdash; <span style="color:#ffd483">and now you are literally running lesson '
           '4.4 again</span></div>',
           """Deep dive two: policy distribution and revocation. Evaluation has to be local, because ten """
           """million checks a second makes a network call per request impossible. So the policy has to """
           """be physically present at every workload.""", step=0)
seg(sid, 1, """And that is exactly the denylist problem from lesson four point four. Push a signed, """
            """versioned policy bundle to every workload. Each one tracks its bundle version, and a gap """
            """triggers a pull to catch up.""")
seg(sid, 2, """Workloads export the age of the policy they are running, and you alert on age rather than """
            """on whether the push job succeeded &mdash; because the job can succeed while a thousand """
            """workloads sit on a stale bundle.""")
seg(sid, 3, """And sign the bundle, so that a compromised distribution channel cannot inject policy. """
            """That is the one addition over the denylist case, and it matters because here the payload """
            """is the security control itself.""")
seg(sid, 4, """Revocation is the asymmetric case, exactly like removals in four point four. Granting """
            """access late is mildly annoying. Revoking access late means a compromised service keeps """
            """its access. That is the one that matters, and the asymmetry should drive the design.""")
seg(sid, 5, """The primary mechanism is short certificate lifetimes: revocation becomes &ldquo;stop """
            """renewing&rdquo;, bounded by the T-T-L. For urgent cases you add a push to the identity """
            """authority plus a deny-list of revoked identities &mdash; at which point you are """
            """literally running lesson four point four again. I would name that out loud, because """
            """reusing a pattern you have already justified is faster and more convincing than """
            """deriving it twice.""")

tradeoff('Where the authorization decision is made', [
 ('Central authorization service, called per request', 'info',
  ['One place for policy &mdash; always consistent', 'Easy to audit centrally',
   'Policy changes take effect instantly'],
  ['<b>10M calls/s to one service</b> &mdash; it becomes the biggest system you own',
   'It is on the critical path of <i>everything</i>', 'Its outage is a total outage']),
 ('Local evaluation against a distributed bundle', 'ok',
  ['<b>1&ndash;10 &micro;s, no network call</b>', 'Survives control-plane outages',
   'Scales with the fleet automatically'],
  ['Policy is eventually consistent &mdash; bounded staleness',
   'Revocation is bounded by the propagation interval', 'Every workload needs the agent/library']),
 ('Local evaluation + central check for sensitive operations', 'shared',
  ['Fast common path', 'Strong consistency where it genuinely matters (e.g. money movement)'],
  ['Two paths to maintain and reason about',
   'Someone must classify which operations are sensitive &mdash; and that list will rot']),
], 'Local evaluation against a signed, versioned bundle. The arithmetic rules out anything else as the '
   'default path.',
 'For a small number of genuinely dangerous operations &mdash; issuing refunds, deleting customer data '
 '&mdash; I would add a synchronous central check and accept the latency, because there the cost of a '
 'stale allow is unbounded.',
 [
 """Trade-off: where is the authorization decision made? A central service called per request gives you """
 """one place for policy, always consistent, easy to audit, and changes take effect instantly. It also """
 """means ten million calls a second to one service, which makes it the largest system you own, puts """
 """it on the critical path of everything, and means its outage is a total outage.""",
 """Local evaluation against a distributed bundle is one to ten microseconds with no network call, """
 """survives control-plane outages, and scales with the fleet automatically. The costs are that policy """
 """is eventually consistent with bounded staleness, revocation is bounded by the propagation interval, """
 """and every workload needs the agent or library.""",
 """A hybrid &mdash; local evaluation plus a central check for sensitive operations &mdash; gives a """
 """fast common path with strong consistency where it genuinely matters.""",
 """I would take local evaluation against a signed versioned bundle as the default, because the """
 """arithmetic rules out anything else.""",
 """And what would flip it, for a subset: for a small number of genuinely dangerous operations """
 """&mdash; issuing refunds, deleting customer data &mdash; I would add a synchronous central check and """
 """accept the latency. There the cost of a stale allow is unbounded, so the trade reverses. And I """
 """would be honest that someone has to maintain the list of which operations are sensitive, and that """
 """list will rot unless it has an owner.""",
])

failures('What happens when each piece dies', [
 ('Policy store is unavailable', 'Nothing immediately &mdash; workloads have their bundle',
  '<b>This is the whole point of local evaluation.</b> Staleness grows silently, so alert on policy '
  '<b>age</b> at the workload, not on control-plane health'),
 ('Identity authority is down', 'Existing certs keep working until they expire',
  '<b>Then everything fails at once</b>, clustered by issuance time. Stagger certificate lifetimes, '
  'and make renewal start well before expiry'),
 ('A workload cannot renew its certificate', 'It loses access when the cert expires',
  'Renew at <b>50% of lifetime</b>, not at 90%. A 24 h cert should be renewing after 12 h, giving '
  '12 h of headroom to fix a problem'),
 ('Policy push fails to a subset of workloads', 'Inconsistent enforcement across the fleet',
  'Version the bundle, have workloads report their version, <b>alert on divergence</b>. Never let a '
  'workload run policy of unknown age'),
 ('A service is compromised', 'It can do exactly what its policy allows',
  '<b>Least privilege is the only containment.</b> This is the argument for per-operation policy '
  'rather than per-service: the blast radius <i>is</i> the policy'),
 ('Fail open vs fail closed on policy failure', 'Either a security hole or an outage',
  '<b>Fail closed by default</b>, with a documented, audited break-glass path. For a security control, '
  'an outage is recoverable and an undetected breach is not'),
], [
 """Failures. Policy store unavailable: nothing happens immediately, because workloads already have """
 """their bundle. That is the entire point of local evaluation. Staleness grows silently, so alert on """
 """policy age at the workload rather than on control-plane health.""",
 """Identity authority down means existing certificates keep working until they expire &mdash; and then """
 """everything fails at once, clustered by issuance time. So stagger certificate lifetimes and start """
 """renewal well before expiry. A synchronised expiry across a fleet is a self-inflicted outage waiting """
 """for a bad afternoon.""",
 """A workload that cannot renew loses access when its certificate expires. Renew at fifty percent of """
 """lifetime, not ninety. A twenty-four hour certificate should start renewing after twelve hours, """
 """which gives you twelve hours of headroom to notice and fix the problem.""",
 """Policy push failing to a subset gives inconsistent enforcement. Version the bundle, have workloads """
 """report their version, and alert on divergence &mdash; the same discipline as the denylist, and the """
 """same reason.""",
 """A service being compromised means the attacker can do exactly what that service's policy allows. """
 """Least privilege is the only containment, and that is the real argument for per-operation policy """
 """rather than per-service: the blast radius is literally the policy you wrote. That reframing is """
 """worth saying, because it turns a granularity decision into a security one.""",
 """And fail open versus fail closed. I would fail closed by default, with a documented and audited """
 """break-glass path. For a security control, an outage is recoverable and an undetected breach is not """
 """&mdash; but I would state that as my recommendation and let the interviewer disagree, because it is """
 """genuinely their risk decision.""",
])

say('What I should actually say in the room', [
 'I want to separate two things, because I think one of them is the real question. Authorization '
 '&mdash; may A call B &mdash; is a lookup. Authentication &mdash; is the caller really A &mdash; is '
 'the hard part.',
 'If identity rests on an IP, a hostname, or a header, then anything on the network can impersonate '
 'anything else, and the policy engine will authorise it. That is what zero trust actually means: '
 'being on the network proves nothing.',
 'So every workload gets a short-lived certificate with a structured identity &mdash; SPIFFE-style '
 '&mdash; and calls go over mutual TLS. The callee reads the identity from the certificate, not from a '
 'header.',
 'The bootstrap question is worth naming: a new workload has no certificate yet, so trust has to be '
 'rooted in the platform &mdash; a Kubernetes service-account token or cloud instance identity. '
 'Ultimately trust rests on whoever schedules the workload, and there is no deeper answer.',
 'At roughly 10 million internal calls a second, a network call per check is impossible, so evaluation '
 'has to be local. The policy is about 10 MB, so I replicate the whole thing to every workload rather '
 'than partitioning it.',
 'Distribution is a signed, versioned bundle, pushed with a pull fallback on version gap &mdash; which '
 'is the same mechanism as the IP denylist question, so I would reuse it rather than reinvent it.',
 'Revocation is asymmetric: granting late is annoying, revoking late is dangerous. So short cert '
 'lifetimes are the primary mechanism, with a push channel for urgent cases.',
], [
 """The sentences. Open by separating authentication from authorization, because that distinction is """
 """the question and most candidates collapse it.""",
 """Then why forgeable identity breaks everything, then m-T-L-S with certificate-not-header. Then the """
 """bootstrap problem, which is the detail that shows real depth.""",
 """Then the arithmetic forcing local evaluation, the distribution mechanism named as a reuse of """
 """lesson four point four, and the revocation asymmetry. Seven sentences covering all eleven named """
 """follow-ups.""",
])

followups([
 'How do services prove their identity?',
 'How do you authenticate and authorise?',
 'Where is policy stored?',
 'How is policy evaluated?',
 'How do you cache decisions?',
 'How does policy propagate?',
 'How do you revoke access?',
 'How do you audit?',
 'What does zero trust mean here?',
 'What happens on failure?',
], [
 'A calls B on behalf of a user. How does B know, and how does C know?',
 'How do you roll out a policy change safely to 100,000 workloads?',
 'How would you find every caller of an endpoint you want to delete?',
 'A service is compromised. Walk me through containment.',
 'Who writes these policies, and how do you stop them all becoming &ldquo;allow&rdquo;?',
],
 """The reported follow-ups are the lesson. On caching decisions: you do not cache decisions, you """
 """cache the policy &mdash; because caching decisions means you have to invalidate them, and caching """
 """the policy means evaluation is already local and free. That distinction is worth making crisply. """
 """Audit means logging every decision with caller, callee, operation and outcome, and that log is the """
 """thing that makes the whole system reviewable.""",
 """The staff-level follow-ups go deeper. On-behalf-of is token propagation &mdash; B presents both its """
 """own identity and a delegated token for the user, so C can make a decision about both, and getting """
 """this wrong is how confused-deputy vulnerabilities happen. Rolling out a policy change safely means """
 """shadow mode first: evaluate the new policy, log what <i>would</i> have been denied, change nothing """
 """&mdash; and only enforce once that log is empty. Finding every caller of an endpoint is the audit """
 """log earning its keep, and it is the single most useful thing this system gives you day to day. """
 """Containment is revoke the identity, which is stop renewing plus an urgent push. And the last """
 """question is the real one: who writes these policies, and how do you stop them all becoming allow? """
 """The honest answer is that policy must be owned by the callee team, reviewed in code, and audited """
 """for over-broad grants &mdash; because a permission system that everyone routes around is worse than """
 """none, since it provides false assurance.""")

cheatsheet('Service permissions &mdash; the one-page card', [
 ('Requirements', 'Decide which service may call which, on every call, without adding latency'),
 ('Scale', '~1,000 services, ~100k instances, <b>~10M authz checks/s</b>. Policy ~10 MB total'),
 ('Core architecture', 'Identity authority issues short-lived certs &rarr; mTLS between workloads '
                       '&rarr; <b>local</b> policy evaluation against a signed, versioned bundle'),
 ('Data store', 'Policy store (small, central, source of truth); replicated bundles at every workload; '
                'append-only audit log'),
 ('Partition key', '<b>None.</b> Policy is ~10 MB &mdash; replicate it whole to every process'),
 ('Cache', 'The bundle <i>is</i> the cache. <b>Cache the policy, not the decisions</b> &mdash; '
           'decisions would need invalidating'),
 ('Queue', 'Policy distribution channel; audit log stream'),
 ('Consistency', 'Eventual, with an explicit staleness budget. <b>Revocation propagates faster than '
                 'granting</b>'),
 ('Failure handling', '<b>Fail closed</b> with an audited break-glass; alert on policy <b>age</b> and '
                      'version divergence; renew certs at 50% of lifetime'),
 ('Key deep dives', 'Identity and the bootstrap problem &middot; distribution and revocation '
                    '(= lesson 4.4)'),
 ('Biggest trade-off', 'Central consistency vs local speed &mdash; and at 10M checks/s, '
                       '<b>local wins and the staleness is the price</b>'),
], [
 """The card. The scale row has the number that decides the architecture: ten million checks a """
 """second.""",
 """Architecture in one line. Note the partition key row says none &mdash; policy is ten megabytes, so """
 """replicate it whole. And the cache row carries a distinction worth remembering: cache the policy, """
 """not the decisions, because decisions would need invalidating and policy does not.""",
 """Consistency is eventual with revocation propagating faster than granting. Failure handling is fail """
 """closed with break-glass, and renew certificates at half their lifetime. And the biggest trade-off """
 """is central consistency against local speed, where at this volume local wins and staleness is the """
 """price you pay.""",
])

say('The 60-second answer', [
 'I want to separate two things, because one of them is the actual question. Authorization &mdash; may '
 'A call B &mdash; is a lookup and is not hard. Authentication &mdash; is the caller genuinely A '
 '&mdash; is the whole problem.',
 'If identity rests on an IP address, a hostname, or a header, then anything that can reach the network '
 'can impersonate anything else, and the policy engine will happily authorise it. That is what zero '
 'trust means in practice: presence on the network proves nothing.',
 'So every workload gets a short-lived X.509 certificate carrying a structured identity, SPIFFE-style, '
 'and calls go over mutual TLS &mdash; the callee reads the caller&rsquo;s identity from the '
 'certificate rather than from a header it could have made up.',
 'The bootstrap question is worth naming: a brand-new workload has no certificate, so trust has to be '
 'rooted in the platform, via a Kubernetes service-account token or a cloud instance identity. Trust '
 'ultimately rests on whoever schedules the workload, and there is no deeper answer than that.',
 'At around 10 million internal calls a second a network call per check is impossible, so evaluation is '
 'local. The whole policy is about 10 MB, so I replicate it to every workload rather than partitioning '
 'it, distributed as a signed versioned bundle with a pull on version gap &mdash; the same mechanism as '
 'the IP denylist question.',
 'And revocation is asymmetric: granting late is annoying, revoking late is dangerous. So short '
 'certificate lifetimes are the primary mechanism &mdash; revocation becomes &ldquo;stop '
 'renewing&rdquo; &mdash; with a push channel for the urgent cases, and I would fail closed with an '
 'audited break-glass path.',
], [
 """The sixty-second answer, and the last one in the course. The opening split between authentication """
 """and authorization is the single most important move, because it reframes a question most people """
 """answer backwards.""",
 """And the bootstrap sentence is the one that signals real depth &mdash; naming where the chain of """
 """trust terminates, rather than pretending it does not. Practise both until they are automatic.""",
], kicker='60-second interview answer')
