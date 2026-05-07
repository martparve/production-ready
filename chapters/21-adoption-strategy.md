# Chapter 21: Adoption Strategy - Top-Down, Bottom-Up, or Both?

Every organization building an AI code factory faces the same structural question before it writes a single skill or deploys a single agent: how should the capability to build and operate the factory be distributed across the engineering organization?

There are three broad strategies. The first treats AI-native development as a centralized competency - an extension of CI/CD, built and maintained by a dedicated platform team. The second distributes the exploration across the entire engineering organization - everyone experiments, the best approaches spread organically. The third starts with the second and evolves into the first: broad experimentation to discover what works, then platform consolidation to scale it.

The destination is the same regardless of path. Every organization that succeeds ends up with an AI-powered development pipeline maintained by a platform team. What differs is how that team learns what to build.

Chapter 22 covers the tactical rollout: what to build, in what order, how to staff it. This chapter addresses the organizational architecture and design layer that precedes it: how to organize the people who figure out the factory's shape.

## Strategy 1: Centralized - AI as CI/CD Extension

The centralized approach treats AI-native development as infrastructure. A dedicated team builds the end-to-end pipeline - from business intent through specs, code generation, review, and deployment - as an extension of the existing CI/CD system. Product teams consume it as a service, the same way they consume build pipelines and deployment infrastructure today.

The team does ten thousand reps on specific problems. Is the better solution for context and hallucination management an agent architecture or progressive disclosure through MCP? Which Playwright skill definitions produce the best frontend tests? How should SonarQube findings be fed back into agent context? The team evaluates options, picks one, develops it fully, and ships the result as tooling. Product teams consume the output. If they find improvements, they PR back to the skills repo. The platform team moves to the next problem.

### Who does this

Shopify's engineering team built an LLM proxy for managed API access, 24+ MCP servers connecting internal systems, and standardized tool configurations - infrastructure that individual product teams could not have built in isolation.[PE-07] Google's internal AI coding guidance was authored by engineers who had accumulated deep experience with their own tools, giving it technical credibility that a management directive would not have carried.[Google-AI-guidance] Stripe's Leverage team built the Minions platform that handles agent orchestration, safety, and code review - infrastructure that enables 1,300+ agent PRs per week.[Stripe-Minions-1]

### Tradeoffs

**Fast convergence, but premature lock-in.** A focused team ships shared infrastructure fast - Shopify had its LLM proxy and MCP servers running before most teams finished experimenting individually. But in a tooling environment that changes every six months (Chapter 23's six-month rule[ANDev-011]), architectural bets made in Q1 may be obsolete by Q3. Switching costs accumulate. The platform team becomes invested in defending its choices rather than abandoning them.

**No duplicate effort, but narrow solution space.** Ten product teams do not independently solve the same problems. But however talented, a small team has a limited range of perspectives. Agur Jõgi, CTO of Pipedrive, responded to this model directly: "I fully understand it. And I say it is fundamentally wrong." His objection: "We lock the discovery of the best possibilities from this new technology into a small group's domain."[Jogi-Pipedrive] What is the basis for believing the best talent for building something that has never existed before happens to be in the platform team? The ten-thousand-reps argument assumes the team doing the reps has the right starting intuitions. In a paradigm shift, that assumption may not hold.

**Clear ownership, but infrastructure outruns skills.** One team owns the pipeline's reliability and evolution. Product teams keep shipping without splitting attention. But engineers consuming pre-built infrastructure need 11 weeks to develop the mental models to use it effectively.[GH-Copilot-enterprise] Infrastructure that arrives before the skills to use it creates what DORA documented in 2024: individual perceived productivity rises, but system-level delivery throughput drops 1.5% and stability declines 7.2%.[DORA-2024]

## Strategy 2: Distributed Experimentation

The distributed approach inverts the centralized model. Instead of one team figuring it out and serving it to everyone else, every engineer experiments. The best approaches emerge organically - spread through peer recommendation, Slack channels, internal demos - and a platform team consolidates the winners into shared infrastructure after the fact.

The core argument is about probability. Capability is talent times practice. A dedicated team has high practice but a limited talent pool. Distributed experimentation has a broader talent pool but fewer reps per person. More engineers experimenting means more combinations of problems, perspectives, and approaches being tried simultaneously. The innovations that survive organic peer adoption have been validated by real usage, not by the judgment of a small team.

Think of it as evolution. Mutations happen when organisms face environmental pressure - not in a lab. Real teams working on real problems encounter a wider range of unexpected challenges and can test solutions immediately in context. A platform team solves the problems it can imagine. A hundred engineers embedded in production work encounter the problems nobody imagined.

Distributed experimentation does not happen by removing mandates and hoping for the best. Beyond leadership driving the mindset shift, it benefits from an organization where initiative and collaboration are in the DNA. Pipedrive's investment predated AI by years:

- **Communication.** Pipedrive has deliberately invested in getting even the nerdiest of engineers to talk to each other. Lightning Talks where public speaking can be practiced in a low-stakes environment. Deliberate team rotation. Slack channels for sharing experiments. Innovation in one person's head is worthless.
- **Psychological safety.** "No manual coding" month is a good example. Engineers were instructed to start every task with a prompt, burning as many tokens as they wanted. Tiger Teams for experimentation without delivery pressure.

Pipedrive has also benefited enormously from disposable infrastructure. Cloud-based devboxes were set up before AI coding became a thing, which means every experiment gets its own environment. No risk of breaking shared state.[Jogi-Pipedrive]

### Who does this

Pipedrive deliberately chose the distributed approach. CTO Agur Jõgi invested smart engineers' time across product teams to figure out what works, rather than concentrating experimentation in a platform team.[Jogi-Pipedrive]

The most striking result was an AI agent called Scooby, built over a single weekend by a mid-level engineer. It integrated codebase knowledge, monitoring data, and customer feedback into an internal agent. No management directive followed. The tool spread through Slack as engineers recommended it to each other. Other engineers contributed plugins and extensions.

> **Case Study: The Scooby Effect**
>
> Agur Jõgi, CTO of Pipedrive, describes a mid-level engineer who built an AI agent called Scooby over a single weekend. Scooby integrated codebase knowledge, monitoring metrics, and customer feedback into an internal agent. No directive from management followed. The tool spread through Slack as engineers recommended it to each other, and contributors added plugins and extensions. Jõgi's takeaway: "I believe that engineers make their own work more efficient and automated by nature."[Jogi-Pipedrive]

Meta Reality Labs followed a similar path. Ian Thomas described how adoption started with "a few people that were really keen and experimenting" who had found value from AI tools outside of work. Senior engineers were skeptical. The early adopters built a community of practice - sharing workflows, pairing with skeptics, demonstrating concrete results on real projects. Adoption reached 80%+ measured as four-days-out-of-seven engagement. Thomas captured the dynamic: "If it's bottoms up, it's more like, okay, we can make this work." Engineers who chose the tools through peer influence developed genuine skill, rather than going through the motions of compliance.[ANDev-036]

BBVA provides the large-enterprise proof point: 11,000 employees adopted AI tools and teams built 4,800 custom AI-powered tools internally. The adoption was driven by team-level experimentation and internal sharing, not by a centralized tooling team. Harvard Business Review cites BBVA as evidence that distributed approaches can scale even in heavily regulated industries, provided the organization invests in enablement infrastructure and internal tool-sharing platforms.[HBR-BBVA]

### Tradeoffs

**Wider solution space, but fragmentation.** Von Hippel's research shows breakthroughs come from "lead users" who experience needs ahead of the market.[VonHippel-1988] Scooby was built by exactly the kind of engineer a platform team would never have assigned to the problem. But without coordination, you get duplicate effort, ungovernable tooling sprawl, and knowledge siloed in individual heads (Chapter 22's Model C failure modes).

**Battle-tested solutions, but slow to converge.** Innovations that survive organic adoption have been validated by real usage, not committee judgment. But many experiments and no scalable solutions is what March called "over-exploration."[March-1991] McKinsey finds only 6% of organizations reach "high performer" AI status - most stall between experimentation and consolidation.[McKinsey-AI-2024]

**Deep capability, but split attention.** Engineers who discover approaches through experimentation understand them at a depth that consumers of pre-built infrastructure never reach. The METR trial found AI tools made experienced developers 19% slower while they perceived a 20% speedup[METR-2025] - comfort is not capability. Experimentation builds capability. But it also means engineers split time between feature work and tooling research.

## Strategy 3: Broad Experimentation, Then Platform Consolidation

The evidence from the strongest performers in 2025-2026 points to a third strategy that is neither purely centralized nor purely distributed. Let many engineers experiment. Then consolidate what works into platform infrastructure. The second strategy leading to the first.

Jõgi captured the logic: "When you want to innovate something like AI-based development, it is useful to go broad and bottom-up. When competencies emerge that can be consolidated, you focus there and start building the platform. But if you said 'you, you, and you - you be the innovation team,' maybe they are not the right people."[Jogi-Pipedrive]

This does not reject the centralized vision. The end-to-end AI pipeline - from business intent through specs, code generation, review, and deployment - is the destination regardless. The disagreement is about the discovery path. The centralized approach puts a dedicated team on the path from day one. The hybrid lets broad experimentation discover what the path should look like, then builds the platform team around proven approaches. The end state is the same. What differs is how the platform team learns what to build.

### Who does this

**Shopify.** Despite the CEO memo that drew public attention, Shopify actually followed this pattern. The memo came after R&D was already leaning in. VP Engineering Farhan Thawar explained: "R&D was already leaning in... the memo changed things more outside of R&D."[PE-07] The LLM proxy and MCP servers were built bottom-up by engineering teams solving their own problems, then standardized. The memo gave permission. The infrastructure gave capability.

**Meta Reality Labs.** Started with grassroots champions, built a community of practice, then added organizational push. By the time the push came, 80%+ of engineers were already using tools daily. The push formalized what was already happening.[ANDev-036]

**Stripe.** The most mature example. The Leverage team built the Minions platform - centralized infrastructure - but designed it to be triggered by any engineer via a Slack emoji. The platform team did not dictate which tasks to automate. Engineers chose based on their domain knowledge. The platform ensured that whatever engineers chose to automate would be safe, reviewed, and well-tested.

> **Case Study: Stripe's Minions - Infrastructure That Engineers Choose to Use**
>
> Stripe's Leverage team built the Minions platform: agent orchestration infrastructure handling code generation, safety checks, and automated review. The key structural decision was that the platform team built the rails, but individual engineers decided what to run on them. Any engineer can trigger a Minions run via a Slack emoji on a ticket. The platform team does not dictate which tasks to automate - engineers choose based on their domain knowledge. Result: 1,300+ agent-generated PRs merged per week.[Stripe-Minions-1]

### The phases

The hybrid unfolds in a predictable sequence.

**Months 1-3: Broad experimentation.** Provide tools and budget. Track what teams discover. Do not mandate approaches. Daniel Jones of Tessl observed the pattern across the industry: "2025 was more organic trialing. 2026 is the shift to structured rollout."[ANDev-045]

**Months 3-6: Pattern recognition.** Which experiments produced reusable approaches? Where are the Scooby-style innovations worth scaling? Indeed's cohort-based experimental approach - running controlled groups to compare AI-assisted versus traditional workflows - provides a template for rigorous pattern identification.

**Months 6-9: Platform consolidation.** The platform team takes winning experiments and builds them into shared infrastructure. Standardize what works. The platform team itself is evolving: Jones describes it becoming the "software factory team."[ANDev-045]

**Month 9+: Managed evolution.** Platform provides the foundation. Teams extend it for their domains. This is Chapter 22's Model B.

BCG research quantifies the investment pattern behind successful hybrids: 10% of the effort goes to the algorithm or model, 20% to technology and infrastructure, and 70% to people and process changes. Organizations that invert this ratio consistently underperform.[BCG-10-20-70]

### Tradeoffs

**The platform builds the right thing, but executives must wait.** The team consolidates proven approaches rather than betting on its own judgment - eliminating Strategy 1's premature lock-in risk. But "let people experiment for three months before we know what to build" sounds like "we don't have a plan." Patience is scarce when competitors are moving fast.

**Engineers arrive skilled, but the early phases produce nothing standardized.** By the time the platform ships tooling, engineers already have the mental models to use it - closing Strategy 1's infrastructure-outruns-skills gap. But leaders must resist the urge to pick a direction prematurely. The ambiguity is the feature, not a bug.

**Best of both strategies, but both sets of prerequisites.** Broad exploration early, concentrated expertise later. The experimentation phase still carries Strategy 2's cultural requirements. And McKinsey's 6% "high performer" rate shows that most organizations stall between experimentation and consolidation.[McKinsey-AI-2024] Building the consolidation phase into the plan from the start is the difference between a strategy and an aspiration.

## Choosing Your Strategy

Most organizations do not choose - they default. Process-heavy organizations default to the centralized model because that is how they adopt everything. Engineering-empowered organizations default to distributed experimentation because that matches their culture. The strategic question is whether your default is right for AI-native development specifically, given that the technology changes faster than any previous adoption challenge.

The worst outcome is not picking the wrong strategy. It is not making a deliberate choice at all, and discovering six months in that your default did not serve you.


