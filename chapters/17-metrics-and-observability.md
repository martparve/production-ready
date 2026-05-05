# Chapter 17: Metrics and Observability

A factory without sensors is a factory you cannot trust. It produces output. You ship the output. You hope the output is good. When something breaks, you trace backwards through logs and guesswork, trying to reconstruct what happened inside a system you never bothered to instrument. This is not engineering. This is gambling.

The headless code factory described in the preceding chapters is opaque by design. No human watches the agent write code. No human observes the context selection, the retry loops, the validation passes. The system ingests a spec and emits a pull request. Between those two events, dozens of decisions are made by machines, and without observability, all of those decisions are invisible. The factory is a black box. Metrics are how you turn it into a glass box.

This chapter covers what to measure, why each metric matters, what to avoid measuring, and how to organize the resulting data into dashboards that drive decisions rather than decorating walls.

Factory observability is harder than traditional software observability in a way worth naming directly. Charity Majors and the team at Honeycomb put it plainly: "You can't have great AI observability unless you start with great software observability."[Majors-AI] Traditional monitoring assumes that failures manifest as crashes, exceptions, or latency spikes - signals that existing tools are built to catch. Agent workflows break this assumption. An agent does not crash when it misunderstands a spec. It does not throw an exception when it writes code that passes tests but violates an architectural convention. It does not spike latency when it produces a technically correct but subtly wrong implementation. The failure mode is not "the system is down" but "the system produced output that looks right and is wrong." Error rates, response times, and throughput - the three pillars of traditional monitoring - tell you nothing about whether the agent understood what you asked it to do. Factory observability requires measuring semantic correctness, not just operational health. This is why the metrics in this chapter focus on spec coverage, architectural drift, and review rejection rates rather than uptime and p99 latency.

The tooling landscape for this kind of observability is maturing rapidly. The OpenTelemetry project - already the industry standard for distributed tracing and metrics - released Generative AI Semantic Conventions in 2024, with contributions from Amazon, Elastic, Google, IBM, and Microsoft.[OTel-GenAI] These conventions define a standard schema for tracking prompts, responses, token usage, and tool calls across LLM-powered systems. In 2025, the project extended these conventions specifically to agent workflows, establishing common patterns for tracing across agent frameworks with three signal types: traces that follow an agent run from invocation through tool calls to completion, metrics that capture token consumption and latency per step, and events that record decision points within the agent's execution.[OTel-agents] For factory operators, the practical significance is that you do not need to build custom telemetry from scratch. The emerging OTel standard means your agent traces can integrate with the same observability stack you already use for your application - Jaeger, Grafana, Datadog, or whatever your team runs today. A single trace can follow a spec from intake through context loading, agent implementation, validation, and merge, giving you the end-to-end visibility that the factory's black-box nature would otherwise deny you.

## Factory-Level Metrics

Six metrics define whether your factory is working, ordered by importance rather than ease of collection.

**Spec-to-deploy cycle time.** This is your end-to-end measure: the elapsed time from when a spec enters the system to when the resulting code is running in production. It includes context assembly, agent execution, validation, human review, merge, deployment, and any post-deploy verification. In a well-running factory, a straightforward feature spec should move from intake to production in hours, not days. If your cycle time is consistently above 24 hours for simple specs, something in the pipeline is stuck, and this metric tells you to go find out what.

Cycle time is not the same as agent execution time. An agent might generate code in four minutes, but the pull request sits in a review queue for two days. If you only measure agent speed, you will optimize the fast part and ignore the bottleneck. Eli Goldratt's lesson from The Goal applies directly[Goldratt]: improving a non-constraint is waste.

**First-pass validation rate.** Of all agent runs, what percentage pass every validation gate - build, test, spec compliance, security, architecture - on the first attempt, without retries? This is the single most informative metric for agent quality. A first-pass rate of 70% means three out of ten runs need at least one retry cycle. Each retry burns compute, consumes context window, and adds latency.

Track this metric per validation layer. If your first-pass rate is 95% at the build layer but 40% at the spec-compliance layer, you know exactly where the problem is: the agent understands the language but misunderstands the requirements. That points to spec quality, not model capability.

**Human intervention rate.** How often does the system escalate to a human before producing a reviewable pull request? This includes agent failures that exhaust retry budgets, ambiguous specs that the system cannot resolve, and validation failures that require human judgment. A healthy factory should have a human intervention rate below 15% of all specs. Above 30%, you do not have a factory - you have a suggestion engine with extra steps.

**Rejection rate at code review.** Of the pull requests the factory produces and presents to human reviewers, what percentage are rejected or require substantial rework? This metric sits downstream of validation, so it measures the gap between what your automated gates catch and what a human reviewer considers acceptable. If your validation is comprehensive, rejection rates should be below 10%. If they are above 25%, your validation layers have blind spots.

**Production incident rate.** Track production incidents separately for factory-generated code and human-written code. This is the metric that answers the question every skeptic asks: "Is the machine's code as reliable as ours?" You need clean attribution, which requires tagging deployments by source. In the early months, expect factory code to produce incidents at roughly the same rate as human code. If factory code produces significantly more incidents, your validation pipeline is insufficient. If it produces significantly fewer, your validation pipeline might be too conservative, letting through only trivial changes while rejecting anything interesting.

**Cost per deployed feature.** The total cost of producing a deployed feature: LLM API tokens, compute for sandboxing and validation, human review time (valued at engineer hourly rate), and any retry overhead. This is the metric that justifies the factory's existence. If a feature costs $12 in API tokens and 20 minutes of human review time versus eight hours of manual development, the economics are clear. If a feature costs $200 in tokens because the agent retried 15 times and still needed four hours of human rework, the economics are also clear - just in the other direction.

## Quality Metrics

Throughput without quality is a factory that produces defects at speed. These metrics track whether the output is actually good.

**Spec coverage.** What percentage of your behavioral contracts have corresponding tests? Not just tests that the agent wrote alongside its code - those are claims, as discussed in Chapter 11 - but tests derived from spec acceptance criteria. If your spec has twelve acceptance criteria and the deployed code has tests covering eight of them, your spec coverage is 67%. Tracking this over time tells you whether the factory is becoming more or less rigorous about verifying its own output.

**Architectural drift.** Does the factory's code follow the patterns established in the codebase, or is it gradually introducing its own idioms? Measure this through static analysis: dependency direction violations, unauthorized cross-module imports, pattern deviations from documented architecture rules. A slow upward trend in architectural violations is a leading indicator that your context is stale or insufficient. The agent is not maliciously ignoring your architecture. It never understood it properly.

**Tech debt accumulation rate.** Every codebase accumulates technical debt. The question is whether the factory accumulates it faster than human development does. Measure complexity metrics (cyclomatic complexity, cognitive complexity), duplication rates, and dependency counts over time, segmented by source. If factory-generated code averages a cyclomatic complexity of 14 while human code averages 8, the factory is producing code that will be expensive to maintain regardless of whether it works today.

**Shadow spec detection.** A shadow spec is an undocumented behavior that the agent introduced - something the code does that no spec requested. Chapter 6 discussed why specs need to be explicit. Shadow specs are the failure mode when they are not. Detect them through coverage analysis: code paths that no spec-derived test exercises are candidates for shadow behavior. Some of these are legitimate (error handling the agent added proactively). Others are the agent "helping" by adding features nobody asked for. Track the count and review the trend.

## Developer Impact Metrics

The factory does not exist in isolation. It exists inside an engineering organization staffed by humans. Measuring only the machine's output while ignoring the humans who operate and review that output gives you half the picture.

Justin Reock[ANDev-014], Deputy CTO at DX, articulates the framework for measuring developer impact around AI tools. DX built their AI measurement framework on three dimensions - utilization, impact, and cost - drawing on validated research from the DORA metrics[DORA-2025], the SPACE framework, and the DevEx framework:

> **Case Study: When System Metrics Lie**
>
> Justin Reock (DX, AI Native Dev Ep 014) describes a core principle of DX's measurement philosophy: "If you see some conflict, if a system metric coming in seems to conflict with what you're seeing from the survey metrics, you should trust the survey metrics and figure out why the system metrics aren't aligning. There's probably something wrong in the way you're scraping the data or something stale about the data."[ANDev-014]
>
> The example he gives is telling. Copilot's most popular telemetry metric - suggested lines versus accepted lines - breaks down because engineers do not always click the accept button. They see the suggestion, absorb the idea, and keep typing. The system records zero acceptance. The engineer saved thirty seconds. The metric says the tool is unused. The survey says it is invaluable.
>
> This is not an edge case. It is the default failure mode for any system-only measurement approach. Reock's prescription: blend quantitative telemetry with qualitative self-reported data, and when they disagree, investigate the system metric first.

Reock's framework maps cleanly to the headless factory. Here is how the three dimensions apply:

**Utilization.** Who is using the factory, and how? This includes raw adoption - what percentage of your engineering team submits specs to the factory versus writing code manually. But it also includes depth of use. An engineer who submits trivial one-line specs is using the factory differently from one who submits complex multi-file feature specs. Track both breadth (percentage of engineers) and depth (complexity distribution of submitted specs).

**Impact.** Are engineers more productive with the factory than without it? Measure PR throughput, rate of delivery, and developer satisfaction. Reock emphasizes that satisfaction is not a soft metric - it directly predicts retention, quality, and long-term productivity.[ANDev-014] An engineer who hates the factory will find ways to route around it, and you will never know from system metrics alone.

Impact measurement carries a specific trap that Microsoft Research documented in their 2024 study on "Ironies of Generative AI."[MS-Ironies] Their analysis identified four mechanisms by which AI tools can reduce productivity even when naive metrics suggest improvement: engineers shift time from production to evaluation (reading and verifying AI output instead of writing code), workflows restructure around the tool in ways that add friction, AI-generated suggestions interrupt the engineer's own reasoning, and - most critically - AI makes easy tasks easier while making hard tasks harder. That last finding is particularly dangerous for factory metrics. If you measure average cycle time across all features and see improvement, you may be seeing the factory accelerate trivial work while slowing down or degrading the quality of complex work. Segment your impact metrics by task complexity. A factory that cuts cycle time by 60% on simple features but increases rework rates by 30% on complex features is not delivering the productivity gain that the blended average suggests.

One finding from DX's research deserves special attention. When they surveyed engineers to stack-rank their most time-saving AI use cases, the number one response was stack trace analysis[ANDev-014] - not code generation, not autocomplete, but using AI to interpret error output. This is not even a generative use case. It is a comprehension aid. The implication for factory operators: do not assume the factory's value comes only from writing code. Measure the time savings across the entire workflow, including debugging, review preparation, and documentation.

**Cost.** What is the total spend on the factory, and what return does it generate? This includes API costs, compute costs, and the opportunity cost of human time spent on review and intervention. Reock notes the parallel to cloud cost management: "It's amazing. You still see brand new companies starting up that will help you measure your cloud costs. And we're how long into the cloud at this point."[ANDev-014] AI cost measurement will follow the same trajectory. Start tracking it now, before the bill surprises you.

**Team-level metrics.** Beyond the three dimensions, track metrics specific to how the team operates around the factory:

- *Time on spec versus time on code review.* As the factory matures, engineers should spend more time writing precise specs and less time reviewing generated code. If the ratio is not shifting over time, the factory is not reducing review burden, and you should investigate why.
- *Engineer satisfaction scores.* Survey quarterly. Ask specifically about the factory experience: trust in output quality, frustration with false positives in validation, clarity of escalation paths when the factory fails.
- *Enablement effectiveness.* Reock's research found that the single biggest differentiator between organizations seeing positive returns from AI tools and those seeing flat or negative returns was enablement[ANDev-014] - whether engineers were trained on prompting best practices, context management, and high-value use cases. Track completion rates for internal training and correlate them with per-engineer factory success rates.

## Evals as Factory Confidence

Metrics tell you how the factory performed yesterday. Evals tell you how it will perform tomorrow. Where metrics are lagging indicators derived from production data, evals are proactive experiments that measure whether the factory can handle the types of work you need it to handle - before you assign that work.

The distinction between validation (Chapter 11), metrics (this chapter), and evals matters. Validation checks individual outputs. Metrics track aggregate trends. Evals are controlled experiments against representative tasks that answer "can this configuration handle this class of work?" Chapter 18 covers eval design in depth: what to measure, how to score, how to build and maintain a test corpus, and how to sustain the practice as the factory evolves.

## Dashboards and Alerting

Data without presentation is noise. Organize your metrics into three cadences.

**Daily dashboard.** Throughput (specs processed, PRs produced), failure rate by validation layer, retry rate, cost. This is the factory floor view. The operator glances at it each morning to confirm the machine is running. Alerts trigger when the first-pass validation rate drops below its seven-day rolling average by more than 10 percentage points, or when cost per feature exceeds twice the trailing average.

**Weekly review.** Quality trends (spec coverage, architectural drift, tech debt accumulation), review rejection rates, human intervention patterns. This is the engineering manager's view. It answers: "Is the factory getting better or worse?" Weekly granularity smooths out daily noise while catching trends before they become crises.

**Monthly report.** Adoption rates, satisfaction scores, cost trends, capability eval results. This is the leadership view. It answers: "Is this investment paying off?" Monthly granularity is appropriate for metrics that change slowly and need organizational context to interpret.

One rule applies to all three: every metric on a dashboard must have an owner and an action. If a metric turns red and nobody knows whose job it is to investigate, the metric is decoration. If a metric turns red and there is no playbook for what to do next, the alert is a distraction. Justin Reock's colleague Max Kanat-Alexander, who ran developer experience at Google, taught a principle that applies directly: "The audience is more important than the data. If you can't comfortably say who's going to be upset if this data is not available, then you may as well not even capture the data in the first place."[ANDev-014]

## Leading Indicators of Degradation

The metrics above tell you how the factory is performing. These leading indicators tell you how it is about to perform.

**Rising retry rates.** If the average number of retries per agent run is climbing, the factory is struggling. This might mean the model is degrading on your codebase (possible after a provider-side model update), your context is becoming stale, or your specs are becoming more ambiguous. Investigate before the retry rate translates into higher costs and longer cycle times.

**Growing context sizes.** If the average context window usage per agent run is trending upward, you are accumulating context without pruning. Eventually you hit the window limit, and the agent starts dropping information. This is Roberts' one-way ratchet in action.[ANDev-031] Use your eval suite to identify context that can be safely removed.

**Review rejection climbing.** If human reviewers are rejecting more factory PRs than they were a month ago, something has changed. Either the reviewers have become more demanding (possible, and worth investigating through surveys), or the factory's output quality has dropped. Cross-reference with first-pass validation rates: if validation still looks fine but reviewers are unhappy, your validation gates have blind spots.

**Shadow spec accumulation.** If the count of undocumented code paths is growing, the factory is improvising. Some improvisation is benign - sensible error handling, reasonable defaults. But unchecked shadow spec growth means the codebase is diverging from the documented system design. The code does things nobody asked for, and eventually those things will interact with each other in ways nobody predicted.

**Context window saturation.** Track the percentage of available context window consumed by mandatory context (architecture docs, rules, dependency information) before the agent even reads the spec. If mandatory context consumes 60% of the window, the agent has only 40% left for the actual task. This ratio should be monitored and kept below 50%.

## Anti-Metrics

Not everything that can be measured should be measured. Some metrics are actively harmful because they create perverse incentives or provide false confidence.

**Lines of code generated.** This metric is meaningless in any context, and doubly so for agent-generated code. An agent can produce a thousand lines of verbose, repetitive code or fifty lines of clean, well-abstracted code. The thousand-line version scores higher on this metric and is objectively worse. Do not track it. Do not report it. Do not let anyone in your organization use it to justify the factory's value.

**Agent uptime.** The percentage of time the agent infrastructure is available. This is an infrastructure metric, not a factory metric. It tells you whether the servers are running, not whether the factory is producing valuable output. A factory with 99.99% uptime that produces garbage code is worse than a factory with 95% uptime that produces excellent code. Track uptime for SRE purposes, but do not put it on the factory dashboard.

**Feature count without quality gate.** The raw number of features deployed per week, without any quality filter. This is Goodhart's Law in its purest form. Reock describes the classic failure mode: "The textbook one with PR throughput has always been like, 'Oh, I have to get 10 PRs a week. Great. I'll update the readme file 10 times on Monday and I'm done.' But I haven't actually contributed anything of value."[ANDev-014] If you incentivize feature count, the factory will learn to decompose trivial changes into many small PRs. Every metric you track must be paired with a quality counterweight.

**Acceptance rate on autocomplete.** This is a metric from the code-assistant era that does not translate to the factory context. In a headless factory, there is no human accepting or rejecting individual line completions. The unit of work is a spec, not a keystroke.

**Token efficiency.** Tokens consumed per line of code produced. This sounds like a cost metric but behaves like a quality-destroying incentive. The cheapest code to produce is also the most obvious and least valuable. Difficult problems require more reasoning, more exploration, more context - and therefore more tokens. A factory optimized for token efficiency will gravitate toward simple tasks and avoid hard ones. Measure cost per deployed feature instead, which captures the full picture.

## The Decision Matrix

Every metric in this chapter serves a specific decision. If a metric does not connect to a decision, remove it. Here is the mapping:

| Metric | Who Uses It | What Decision It Drives |
|--------|-------------|------------------------|
| Spec-to-deploy cycle time | Engineering manager | Where are the bottlenecks? Should we invest in faster validation or faster review? |
| First-pass validation rate | Factory operator | Is the agent capable enough? Do we need better context or a different model? |
| Human intervention rate | Team lead | Is the factory reducing workload or creating new workload? |
| Review rejection rate | Quality lead | Are our automated gates sufficient, or do humans keep catching things the machine misses? |
| Production incident rate | Engineering director | Is factory code safe to ship at our current velocity? |
| Cost per deployed feature | Finance/leadership | Is this investment generating returns? Should we scale up or scale back? |
| Spec coverage | Quality lead | Are we testing what the spec describes, or are we testing what the agent decided to build? |
| Architectural drift | Architect | Is the codebase staying coherent, or is the factory fragmenting it? |
| Developer satisfaction | Engineering manager | Do engineers trust the factory? Are they routing around it? |
| Capability eval pass rate | Factory operator | Can we assign this type of work to the factory, or does it need human handling? |
| Retry rate trend | Factory operator | Is performance degrading? Do we need to update context or investigate model changes? |
| Context window usage | Factory operator | Are we approaching the limits of what the agent can hold? Time to prune? |

## Closing: The Instrument Panel

A factory without observability is an act of faith. You are trusting that the probabilistic system producing your code is doing so correctly, efficiently, and sustainably - without any evidence that this is true.

The metrics in this chapter are not optional additions to a working factory. They are the factory. Without them, you have a script that calls an LLM and commits the output. With them, you have a system you can reason about, debug, improve, and trust.

Start with five metrics: cycle time, first-pass validation rate, human intervention rate, cost per feature, and developer satisfaction. Get those on a dashboard within the first week of factory operation. Add the rest as the system matures and as specific questions arise that need data to answer.

Measure what matters. Ignore what flatters. Act on what the data tells you - especially when it tells you something you do not want to hear.

---
