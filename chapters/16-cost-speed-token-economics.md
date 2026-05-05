# Chapter 16: Cost, Speed, and Token Economics

Running AI agents at scale costs real money. Not theoretical money, not "well, it depends on the model" money - real line items on a budget that someone has to approve. The AI code factory is a production system, and like every production system, it has operating costs that must be understood, modeled, and optimized. The economics are different from anything software teams have budgeted for before: not headcount, not cloud infrastructure, not SaaS licenses, but token consumption that varies by task complexity, context size, and how many times the agent gets stuck in a retry loop before it produces working code.

This chapter covers what the factory costs to run, what it costs not to run, where the money goes, and how to make the numbers work. It also covers speed, because in a headless factory, cost and speed are the same conversation. Tokens burned per feature, time from intent to deploy, throughput per week - these are the operating metrics of your factory, and they deserve the same rigor you apply to your cloud infrastructure monitoring.

## The Cost Structure of a Headless Factory

The economics of a headless factory differ from interactive AI-assisted development in a structural way. When a developer uses Cursor or Claude Code at their desk, the cost equation is: developer salary + tool subscription + tokens consumed. The developer's time dominates. Whether the model costs $0.50 or $5.00 per conversation, the developer sitting there for an hour costs $75-150 in loaded salary. The token cost is a rounding error.

In headless mode, the developer is gone during execution. The cost equation flips: cloud compute + tokens consumed + review time. No one is sitting at a terminal watching the agent work. The human cost is limited to writing the spec (minutes), reviewing the output (minutes to an hour), and handling any escalations. For routine features that the factory handles well, human involvement might total 30 minutes of senior engineer time for a feature that would have taken a full day to build by hand.

This is why headless mode is cheaper per feature for routine work, even when token costs are higher. You are replacing hours of a developer's focused implementation time with minutes of review time, plus whatever the agents consume in tokens and compute.

Token consumption distributes unevenly across the pipeline stages.

**Spec formalization** is moderate. The model reads a natural language intent, generates structured output, and maybe does one or two refinement passes. A few thousand tokens in, a few thousand out. This stage rarely exceeds $0.10 even on frontier models.

**Codebase onboarding and context loading** is expensive and easy to underestimate. Before the agent writes a single line, it needs to understand your codebase: architecture documents, coding conventions, relevant existing code, dependency maps, test patterns. This context payload can easily hit 50,000-100,000 tokens. And it gets loaded for every agent session. If you run five agents in parallel on decomposed subtasks, you pay for onboarding five times unless you are caching aggressively.

**Agent implementation sessions** are the biggest cost driver by far. This is where the agent iterates: write code, run tests, read errors, fix code, run tests again. A clean implementation that passes on the first try might consume 20,000-30,000 tokens. But that almost never happens. A typical session involves three to five iteration cycles, and a difficult one can spiral into twenty or more rounds of generate-test-fix before the agent produces passing code. Each cycle multiplies the token count. A single feature implementation can consume anywhere from 50,000 tokens (happy path) to 500,000 tokens (complex, unfamiliar pattern with multiple test failures).

**Validation re-runs** are variable. If the CI pipeline passes on first submission, the cost is just the compute to run the pipeline. If it fails, the agent needs to read the failure, reason about the cause, generate a fix, and resubmit. Each re-run adds another full interaction cycle.

**Review agents** are moderate. Automated code review reads the diff, checks against style guides and architectural rules, and produces comments. This is a single-pass operation - typically 10,000-30,000 tokens depending on diff size.

## The Price Collapse

The economics of agentic development have shifted faster than any other input cost in the history of software engineering. The shift did not happen gradually. It happened in a single quarter.

The historical data confirms just how unprecedented this deflation is. Martin Casado at Andreessen Horowitz tracked what he calls "LLMflation" - the decline in LLM inference costs for equivalent performance. The numbers are staggering: from roughly $60 per million tokens in 2021 to $0.06 per million tokens by mid-2025, a thousandfold reduction in four years.[Casado-LLMflation] This rate of decline - approximately 10x per year for equivalent capability - is faster than the drop in PC compute costs during the 1990s and faster than the bandwidth cost collapse during the dotcom era. No prior technology input has deflated this aggressively. For factory operators, the practical implication is direct: a workload that costs $100 per day in agent runs today will cost roughly $10 per day in twelve months, assuming you hold capability constant.

But the decline is not uniform, and this matters for how you architect your model routing. Epoch AI's analysis of inference price trends found that the rate of decline varies enormously depending on which performance milestone you measure.[Epoch-prices] For a GPT-4-equivalent level of capability, pricing dropped from approximately $20 per million tokens in late 2022 to around $0.40 per million tokens by early 2025 - a roughly 50x reduction. For less demanding tasks, the decline has been even steeper. However, frontier reasoning models - the ones you need for hard implementation tasks where the agent must plan across multiple files and reason about edge cases - have not followed the same curve. Their pricing has remained relatively stable because each generation pushes into harder capabilities rather than making existing capabilities cheaper. This is a critical nuance for the model routing discussion later in this chapter: the cheap models are getting cheaper fast, but the models you need for the factory's hardest work are not deflating at the same rate.

> **Case Study: From $7,500 Per Hour to $20 Per Month**[ANDev-035]
>
> On the AI Native Dev podcast (Ep 035), a guest from the Agentix Foundation described the cost trajectory of running agent swarms. In late 2024, his team built recursive agent systems that could operate for hours or days autonomously. A 36-hour test run was technically successful but economically absurd: running a 10-agent swarm concurrently cost $7,500 per hour. "It's just substantially cheaper to hire a person at that point to do that work."
>
> Then in April 2025, Anthropic launched flat-rate subscription plans for Claude Code. The same team re-implemented their swarm protocol under the new pricing. "We were able to spawn these swarms that could run for hours on end and cost a flat fee, often starting at $20 for an entire month. Thousands of dollars an hour to $20 a month." Capability went up and cost dropped by several orders of magnitude in the same release cycle - an inflection that, as he noted, "you don't generally see happen all at once."

This price collapse reshapes the entire cost model. Under per-token pricing, every retry loop, every context reload, every exploratory branch the agent takes has a direct dollar cost. Teams had to be disciplined about prompt engineering, context window management, and early termination of unproductive sessions because the meter was running. A bad agent run on a complex task could cost $50-100 in tokens and produce nothing usable.

Under subscription pricing, the marginal cost of an additional agent session approaches zero. The constraint shifts from "how much does this cost" to "how many concurrent sessions can I run within rate limits." This changes the optimization calculus entirely. Under per-token pricing, you optimize for token efficiency: shorter prompts, compressed context, fewer retries. Under subscription pricing, you optimize for throughput: maximize the number of features the factory processes per unit of time.

Both models will coexist. Subscription plans work for teams with consistent, high-volume usage. Per-token API pricing works for teams with spiky or low-volume usage, or those running custom orchestration pipelines. The smart money is on modeling both and choosing based on your actual usage pattern, not on whichever pricing page you saw first.

There is a counterintuitive trap in this cost deflation that factory operators must understand: cheaper tokens do not mean lower total bills. Andreessen Horowitz's analysis of data from OpenRouter found that by mid-2025, the AI ecosystem was processing over 100 trillion tokens per year, a volume that would have been unthinkable at 2023 prices.[a16z-AI] This is Jevons Paradox playing out in real time - when an input becomes cheaper, consumption expands to more than offset the savings. Hyperscalers are projected to spend over $600 billion on AI infrastructure in 2026 alone, despite per-token costs falling by orders of magnitude. For your factory, this means that as token costs drop, the rational move is to run more agents, on more tasks, with more retries, with richer context - and your total spend may stay flat or even increase while your per-feature cost drops. Budget planning that assumes "costs will decrease because tokens are getting cheaper" without modeling usage expansion will produce forecasts that are wrong in a predictable direction.

## Cost Modeling: When the Factory Pays for Itself

The ROI calculation for a headless factory is not "tokens saved versus tokens spent." It is human hours reclaimed versus total factory operating cost.

Consider a concrete example. A mid-size team ships 20 features per sprint. Each feature takes a developer roughly 6 hours of focused implementation work: reading the requirements, understanding the relevant code, writing the implementation, writing tests, handling code review feedback, making fixes. At a loaded cost of $100/hour for a mid-senior engineer, that is $600 per feature, or $12,000 per sprint in implementation labor alone.

Now route 12 of those 20 features through the headless factory - the routine ones with clear specs and well-established patterns. Each feature requires 15 minutes of spec writing, 30 minutes of review, and maybe 15 minutes of follow-up. Call it one hour of human time per feature at $100/hour. Add $5-15 in token costs per feature (on per-token pricing) or amortize the subscription cost. The factory cost per feature is roughly $105-115, compared to $600 for manual implementation. That is $5,820-$5,940 saved per sprint on 12 features.

But the real savings are not in the direct cost comparison. They are in what those developers do with the reclaimed hours. If they spend the freed time on the 8 complex features that the factory cannot handle - the novel architectures, the performance-critical paths, the gnarly integrations - the team's effective throughput increases without adding headcount.

This math only works if the factory's output quality is high enough that review time stays low. If every factory-produced PR requires an hour of back-and-forth to get to merge-ready, the savings evaporate. The quality of your specs, your test suite, and your validation pipeline directly determines whether the factory is a cost center or a force multiplier.

Justin Reock[ANDev-014] of DX brings the measurement discipline this requires.

> **Case Study: Measuring What the Factory Actually Delivers**[ANDev-014]
>
> Justin Reock, Deputy CTO of DX (AI Native Dev Ep 014), cautions against accepting headline productivity claims. "The hype around these like 10x, 100x improvements are just that. The data is not bearing that out." DX's measurement framework, validated across hundreds of companies, shows realistic gains of 20-30% increases in velocity. Their customer Intercom achieved a 41% increase in AI-driven developer time savings - impressive, but a long way from the 10x claims on social media.
>
> Reock emphasizes measuring both velocity and quality: "We do have to be very careful that these velocity gains that we're clearly making now aren't just trading technical debt down the road." DX tracks PR throughput alongside change fail percentage and code maintainability scores. Speed without quality is not savings; it is deferred cost.

The 20-30% velocity figure is important because it sets realistic expectations for factory ROI modeling. Do not build your business case on 10x. Build it on 25% improvement, and let anything above that be upside.

## Speed Metrics: Measuring the Factory's Clock

Cost tells you what the factory consumes. Speed tells you what it produces. For a headless factory, the key speed metrics are:

**End-to-end cycle time** is the interval from approved spec to merge-ready pull request. This is the factory's clock speed. It includes spec formalization, context loading, agent implementation, validation, and automated review. A well-tuned factory on a routine feature should produce a merge-ready PR in 15-45 minutes. Complex features take longer, sometimes hours, especially if the agent needs multiple validation cycles.

**Throughput** is the number of features completed per unit of time. This is the factory's bandwidth. With parallel agent execution, throughput scales with the number of concurrent agents you can run, up to the point where rate limits, compute capacity, or merge conflicts become the bottleneck.

**First-pass success rate** is the percentage of agent runs that produce a merge-ready PR without human intervention beyond the standard review. This is the factory's quality signal. A first-pass rate below 60% means the factory is generating more rework than value.

**Retry cost ratio** measures how much of your total token spend goes to retries versus productive first-attempt generation. A high retry ratio (above 40%) indicates that the factory is burning tokens on tasks it is not well-suited for - either the specs are underspecified, the patterns are too unfamiliar, or the validation feedback is not actionable enough for the agent to self-correct.

Daniel Jones[ANDev-045], speaking from his consulting work with enterprise teams adopting agentic development, frames the speed question through the theory of constraints.

The 2025 DORA report[DORA-2025] found that teams with high development maturity went faster when they introduced agentic coding, while teams with low maturity went slower. Jones explains this through the lens of the theory of constraints: "If you take one part of a system, speed it up massively, then you're going to create bottlenecks on either side."[ANDev-045] If agents can produce commits minute after minute but it takes three days to get anything into production, you get merge conflicts, stale branches, and wasted work.

The factory's speed is only useful if the surrounding system can absorb it. This means fast CI pipelines, responsive review processes, and a product team that can keep the spec backlog full. Jones has seen this play out directly: "You speed up the software development part, and that puts pressure on product almost immediately. They're like, blimey, we haven't got enough stuff figured out, we can't keep the agents well fed."[ANDev-045]

Bottleneck identification follows the classic Theory of Constraints approach. Measure cycle time at each stage. The stage with the longest wait time is your constraint. Common constraints in factory pipelines:

- **Spec backlog starvation.** The factory is idle because product cannot write specs fast enough.
- **Review queue buildup.** PRs pile up waiting for human review. The factory produces faster than humans can evaluate.
- **CI pipeline congestion.** Multiple agent-produced branches compete for shared CI resources.
- **Rate limit throttling.** The model provider's rate limits cap concurrent agent execution.

Your bottleneck is never permanently fixed. As you relieve one constraint, another emerges downstream. This is Goldratt's Five Focusing Steps applied to the code factory: identify, exploit, subordinate, elevate, repeat.

## Optimization Levers

Once you understand where the cost and time go, you can pull specific levers to improve the economics.

**Prompt caching** is the highest-impact optimization for per-token pricing. Codebase onboarding context - architecture docs, coding conventions, API schemas - is identical across multiple agent sessions. If your model provider supports prompt caching (Anthropic does with a 5-minute TTL), structuring your prompts so that onboarding content occupies a stable prefix means you pay full price once and cache-price for subsequent sessions within the TTL window. The savings are substantial: cached input tokens typically cost 90% less than uncached ones. For a factory running multiple agents against the same codebase, prompt caching can cut context-loading costs by 80% or more.

**Context compression** reduces both cost and quality degradation. Not everything the agent might need should be loaded upfront. Three strategies:

- *Summarization*: Replace full file contents with architectural summaries unless the agent is modifying that specific file. The agent does not need to read every line of your 2,000-line service class to understand its interface.
- *Selective inclusion*: Load only the files and documentation relevant to the current task. A good orchestrator uses the task decomposition to determine which context each agent needs.
- *Just-in-time loading*: Give the agent tools to fetch additional context on demand rather than pre-loading everything. This keeps the initial context window lean and lets the agent pull in specifics as needed.

Research suggests that reasoning quality drops 15% or more above 30,000 tokens of context.[Hsieh-2502] Every token you can trim from the context window without losing essential information improves the agent's output quality and reduces cost simultaneously.

**Model selection by task** is straightforward but underused. Not every pipeline stage needs a frontier model. Linting checks, formatting validation, and simple code review can run on smaller, faster, cheaper models. Save the expensive frontier models for the implementation phase where reasoning quality directly determines output quality. A tiered model strategy might use a small model for spec formatting and validation, a mid-tier model for test generation and code review, and a frontier model only for implementation of novel logic.

**Open versus proprietary model selection** adds another dimension. Open-weight models (Llama, Mistral, DeepSeek) running on your own infrastructure have zero per-token cost after the initial hardware investment. They are slower and less capable than frontier proprietary models for complex reasoning, but they are perfectly adequate for many factory stages. A hybrid approach - open models for boilerplate stages, proprietary frontier models for complex implementation - can cut token costs by 50% or more while maintaining output quality where it matters.

**Warm sandbox pools** reduce cycle time by eliminating cold-start overhead. If every agent run must provision a fresh container, clone the repo, install dependencies, and build the project, that setup time adds 2-10 minutes per run. Pre-warming a pool of sandboxes with the repo already cloned and dependencies installed means agents can start writing code within seconds of dispatch.

**Parallel agent execution** is the primary throughput multiplier. A factory running one agent at a time has a theoretical maximum throughput of maybe 3-4 features per day. Running 5-10 agents in parallel pushes that to 15-40 features per day. The limit is rate limits, compute, and - crucially - merge conflict resolution when multiple agents modify overlapping files.

**Retry budget management** prevents runaway costs on difficult tasks. Set a maximum number of iteration cycles per agent run. If the agent has not produced passing code after N attempts (5-10 is a reasonable starting range), terminate the run and escalate to a human. Without a retry budget, a single difficult task can consume as many tokens as ten routine features combined, with no guarantee of success.

## Capacity Planning

Running the factory at production scale requires the same capacity planning discipline you apply to any other infrastructure.

**Concurrent agent limits** depend on your model provider's rate limits, your compute budget, and your sandbox pool size. Start by mapping your provider's rate limits: tokens per minute, requests per minute, concurrent sessions. Then size your sandbox pool to match. There is no value in having 20 agent slots if your rate limit only supports 5 concurrent sessions.

**Queueing** becomes necessary when demand exceeds capacity. A queue of approved specs waiting for agent slots is normal and healthy. A queue that grows faster than the factory can drain it means you need to either increase capacity or route fewer features through the factory.

**Burst capacity** matters for sprint starts and deadline weeks when the spec backlog suddenly fills up. Consider auto-scaling your sandbox pool within a defined budget ceiling. Define a "normal" concurrency level for steady-state operation and a "burst" level for peak periods. Set hard budget limits on burst usage so that a bad week does not blow the quarterly budget.

**Token budget allocation** across pipeline stages helps prevent any single stage from consuming disproportionate resources. If implementation agents have unlimited retry budgets but your review agents have a fixed token allocation, you will produce PRs faster than you can review them, creating a quality bottleneck.

## When NOT to Use the Factory

The factory is an optimization for routine work. It is not a universal replacement for human engineering. Knowing when to bypass the factory is as important as knowing how to run it.

David Cramer's experience at Sentry draws a sharp line. "It's not about the size of the task or any of this. It's about the complexity in the task based on the commonality of the task."[ANDev-015] The factory excels when the work follows patterns well-represented in training data. It fails when the work requires novel combinations that the model cannot pattern-match its way through.

Cramer reports that for his core product work, agentic-only development "will slow you down a lot of times." On a side project built entirely through agents, he found that "sub 10% of the time was I able to get a one-shot fix in without serious refinement. It's usually like 20 prompts to get something even remotely good."[ANDev-015] That 20-prompt spiral is exactly the kind of token-burning failure mode that kills factory economics.

The factory should not handle:

**Exploratory prototyping.** When you do not know what you are building yet, you need a human thinking through the design space. The factory needs a clear spec. If you cannot write one, the work is not ready for the factory.

**Novel architecture.** First-time implementations of patterns the codebase has never used before. The agent has no local examples to pattern-match against, and training data for niche architectures is thin. This is where Cramer's complexity cliff hits: "If you're doing something that can't easily find common patterns, it just doesn't actually know what to do. So it's going to reach for another common pattern that looks like that."[ANDev-015]

**Crisis hotfixes.** Production is down. You need a human who understands the system making judgment calls under pressure, not an agent burning through retry cycles while customers wait. The factory's cycle time - even at its fastest - adds latency that a skilled engineer with direct access does not have.

**Uncommon patterns and integrations.** Third-party APIs with poor documentation, legacy systems with undocumented behavior, novel algorithms, anything where the correct implementation requires reasoning from first principles rather than matching against known patterns.

**Cross-cutting architectural changes.** Refactors that touch every layer of the system simultaneously, where the agent would need to hold the entire codebase in its head to make consistent changes. Deterministic refactoring tools (like OpenRewrite, covered in Chapter 10) are better suited for this.

The factory should be an escape valve, not a mandate. If a feature is assigned to the factory and the agent fails after three attempts, it should be routed to a human without guilt or process overhead. The worst outcome is an engineer spending two hours trying to coerce the factory into handling a task that a developer could have finished in forty-five minutes.

## The Decision Matrix

Route work through the factory or to a human based on three factors:

| Factor | Route to Factory | Route to Human |
|---|---|---|
| **Pattern commonality** | CRUD endpoints, standard UI components, boilerplate services, test generation | Novel algorithms, unfamiliar integrations, first-of-its-kind patterns |
| **Spec clarity** | Clear acceptance criteria, well-defined inputs and outputs, existing examples in codebase | Ambiguous requirements, undefined edge cases, "figure out the right approach" |
| **Risk tolerance** | Internal tools, non-critical features, behind feature flags | Payment processing, auth systems, data migration, anything touching PII |

When two of three factors point to factory, route to factory. When two of three point to human, route to human. When all three are mixed, start with the factory but set a tight retry budget and escalate fast.

## The Real Math

A headless factory does not save money by replacing developers. It saves money by reallocating developer time from routine implementation to work that actually requires human judgment. The factory handles the commodity code - the CRUD endpoints, the standard integrations, the boilerplate that developers can write but do not enjoy writing. The developers handle the hard stuff: system design, performance optimization, debugging novel failures, and the architectural decisions that determine whether the codebase will still be maintainable in two years.

The cost trajectory points in one direction. Models get cheaper. Context windows get larger. Caching gets more effective. Subscription plans get more generous. The factory's operating cost per feature will continue to drop. Meanwhile, developer salaries show no signs of decreasing. The gap between "cost of a human doing routine work" and "cost of the factory doing routine work" widens every quarter.

The teams that figure out the routing - which work goes to the factory, which stays with humans, and how to make that decision quickly and accurately - will outperform teams that either ignore the factory or try to force everything through it. The economics are clear. The execution is where it gets difficult.
