# Chapter 13: Merge, Deploy, and Monitor: Closing the Loop

The PR is approved. Validation passed. The reviewer signed off. Now the code needs to get into the mainline, ship to production, and prove it works under real traffic. In a conventional workflow, a developer clicks the merge button, watches the deploy, and checks the dashboard. In a headless factory, none of those steps should require a human. Most teams lose their nerve here: they built the spec automation, configured the agents, stood up the validation layers, implemented risk-tiered review - and then merge by hand, deploy by hand, and monitor by staring at Grafana. All the upstream automation collapses into a manual last mile that cancels half the throughput gains.

The headless factory closes the loop. Merge is triggered by approval. Deploy runs through existing CI/CD. Monitoring feeds back as new events that re-enter the pipeline. The factory is not a line - it is a circle.

## Merge Strategies

Two merge strategies dominate, and they make different tradeoffs in a headless factory. The choice matters more than most teams realize. Research spanning 23,000+ professionals across thousands of organizations, published in *Accelerate* by Nicole Forsgren, Jez Humble, and Gene Kim, found that trunk-based development with short-lived branches (less than one day) is a statistically significant predictor of high software delivery performance.[Forsgren-Accelerate] Elite performers in that study deploy multiple times per day with lead times under one hour and recover from failures in under one hour. The merge strategy you choose either enables or blocks that cadence.

**Squash-and-merge** compresses all commits in a PR into a single commit on the mainline. The history is clean. Every commit on main corresponds to one spec, one PR, one unit of work. This is the default at most organizations and it works well when you care about readable history and simple reverts. If a change causes trouble in production, `git revert <commit>` undoes the entire unit of work in one step.

The downside is that you lose the agent's implementation trace. The intermediate commits that show how the agent built the feature - the false starts, the refactors, the test additions - are compressed into a single blob. If you need to understand why the agent made a particular choice, the commit history will not help you. The decision log in the PR description (Chapter 12) becomes the only record.

**Merge commits** preserve the full branch history. Every intermediate commit the agent made is visible on the mainline. You can trace the agent's reasoning, see where it struggled, and understand the sequence of changes. The tradeoff is a noisier history. When you run `git log --oneline` on main, you see dozens of commits per feature instead of one, and many of them are noise: "fix lint error," "add missing import," "update test assertion."

For headless factories, merge commits have a less obvious benefit: traceability to the agent session. If your commit messages include the session ID, the spec ID, or both, you can walk from any line of production code back to the spec that motivated it and the agent run that produced it. This forensic trail matters when a production incident requires understanding not just what changed but why it was changed that way.

The pragmatic middle ground: squash-and-merge for routine work, merge commits for high-risk or complex changes where the implementation trace has diagnostic value. Encode this in your branch protection rules by risk tier, the same way you stratified review (Chapter 12).

Both strategies benefit from trunk-based development with short-lived branches. The empirical evidence from trunkbaseddevelopment.com and the *Accelerate* research is consistent: branches that live longer than a day correlate with lower throughput and higher failure rates.[TBD] In a headless factory, this is naturally achievable. An agent does not take a three-day vacation mid-feature. It implements, validates, and submits within hours. The branch lifetime is bounded by the pipeline execution time, not by human attention spans. Factories that enforce a maximum branch age of one business day - automatically closing or rebasing stale branches - align with the practices that predict elite performance.

**Automated merge on approval.** In a headless factory, the merge should happen when the last required reviewer approves - not when someone remembers to click the button. GitHub's auto-merge feature, Graphite's merge queue, and GitLab's merge when pipeline succeeds all support this. The configuration is trivial. The cultural shift is not. Many teams resist removing the manual merge button because it feels like giving up the last point of human control. But that control is an illusion. If you already approved the PR, what additional information does clicking the merge button give you? None. It is a ritual, not a gate.

Once a human (or an AI reviewer for low-risk tiers) approves the PR and all validation checks are green, the merge should be automatic. Any delay between approval and merge is time during which the mainline drifts further from the branch, increasing the probability of merge conflicts.

**Merge queues** become essential at agent scale. When multiple agents are producing PRs against the same mainline, merge conflicts are inevitable. A merge queue serializes the merges, rebasing each PR against the latest mainline before merging. If the rebase introduces test failures, the PR is ejected from the queue and sent back for remediation - either to the original agent or to a conflict-resolution agent.

Without a merge queue, the alternative is a manual rebase-and-retry cycle that defeats the purpose of automation. Stripe's 1,300 agent-generated PRs per week[ANDev-052] would be impossible without merge queue infrastructure.

## CI/CD at Agent Scale

The DORA 2024 State of DevOps report delivered a finding that reframes the entire CI/CD discussion for agent-driven teams. Across their global dataset, AI adoption increased individual developer productivity - but resulted in a 1.5% decrease in delivery throughput and a 7.2% reduction in deployment stability.[DORA-2024] The report's authors captured it precisely: the bottleneck is not writing code, it is putting good code into production. Agents accelerate the writing. If the merge, build, test, and deploy infrastructure cannot absorb the increased volume, the productivity gains evaporate into longer queues, more merge conflicts, and flakier pipelines. This chapter addresses the bottleneck that the DORA data identified.

The CI/CD infrastructure you have today was built for humans. Humans submit two, maybe three diffs a week. Build times of 15 minutes are acceptable when you run 10 builds a day. Test suites that take 30 minutes are tolerable when a developer can context-switch to another task while waiting.

Agents change every assumption:

> **Case Study: Madison Fortner on Why CI/CD Is Dead**
>
> Madison Fortner, Partner at NEA and former AI researcher at Meta, delivered a sharp assessment at AI Engineer London (Ep 052): "When you think about how engineers are using traditional CI/CD tools, those were built for humans pre-cloud. And you get this massive volume stack in PRs that we never saw with humans. Humans were submitting two, maybe three diffs a week. Now it's thousands, maybe tens of thousands. You start to get to a place where your code base is just impossible to manage."[ANDev-052]
>
> Fortner's thesis is not that CI/CD is unnecessary - it is that the current implementations cannot scale to agent-native workloads. "I do think over time this will likely replace GitHub and other CI/CD tools that are just not built for this infra." Her investment in Namespace, a company that accelerates GitHub Actions builds, reflects the conviction that build infrastructure is the next bottleneck to break.

The numbers make the problem concrete. Suppose your test suite takes 20 minutes. With 10 agent-generated PRs per day, that is 200 minutes of CI time - manageable. At 100 PRs per day, it is 2,000 minutes. At Stripe's 1,300 per week[ANDev-052], it is roughly 4,300 minutes per week of test execution alone. And that assumes each PR only runs once, which never happens - retries, rebases, and post-merge verification multiply the total.

Four strategies address this.

**Parallel test execution.** Most test suites are embarrassingly parallel but run serially by default. Splitting the suite across 10 workers turns a 20-minute run into a 2-minute run. The tooling exists: Jest sharding, pytest-xdist, Go's native parallelism, Nx-style affected-test partitioning. The investment is in configuring it and maintaining the sharding strategy as the test suite grows.

**Incremental builds.** Do not rebuild the entire project when only three files changed. Build systems like Turborepo, Nx, Bazel, and Buck compute the dependency graph and rebuild only what is affected. This matters more at agent scale because agents typically touch a small surface area per PR - they are implementing one spec, not refactoring the whole project. An incremental build that takes 30 seconds instead of 5 minutes at 100 PRs per day saves 7 hours of build time daily.

**Smart test selection.** Run only the tests that are affected by the change. This requires a dependency graph between source files and test files, which is what tools like Launchable, Jest's `--changedSince`, and Nx's affected commands provide. The tradeoff is confidence: if your dependency graph is incomplete, you skip tests that should have run. Mitigate this with periodic full-suite runs on the mainline.

**Merge queue optimization.** Instead of running the full CI pipeline for each PR in the merge queue individually, batch-merge compatible PRs and run CI once on the combined result. If the batch fails, bisect to find the offending PR. This is speculative merging - it trades occasional bisection overhead for dramatically reduced total CI time. Bors-ng and GitHub's native merge queue support variants of this pattern.

The deeper point is that CI/CD at agent scale is not a scaling problem you solve once. It is an ongoing optimization challenge that requires the same attention you give to production infrastructure. Build times, test parallelization, merge conflict resolution, and queue management all need continuous tuning as agent volume grows.

Jez Humble and David Farley formalized this as the deployment pipeline pattern in *Continuous Delivery* (2010): software should always be in a deployable state, and automated testing at every stage creates fast feedback that prevents defects from propagating downstream.[Humble-CD] The headless factory is, in structural terms, a deployment pipeline. Agent-generated code flows through build, test, security scan, and integration stages before reaching production. The difference is throughput. Humble and Farley designed the pattern for human-paced commits. At agent scale, the pipeline must absorb ten to a hundred times the volume without sacrificing the core guarantee - that every artifact reaching production has passed every gate. The four strategies above (parallel execution, incremental builds, smart test selection, merge queue optimization) are implementations of Humble and Farley's insight adapted for machine-generated throughput.

## Deployment: Shipping Machine-Generated Changes

The code is merged. Now it needs to reach production. The deployment strategy for machine-generated code does not differ from the strategy for human-generated code, but two practices become non-negotiable at agent scale: feature flags and canary deployments.

**Feature flags for every agent-generated feature.** When a human writes a feature, they have mental context about its blast radius - which customers will be affected, which edge cases they handled, which they deferred. An agent has no such intuition. It implemented a spec. Whether that spec was complete, whether the validation caught every gap, whether the behavior is correct for all customer segments - those are open questions until real traffic answers them.

Feature flags let you decouple deployment from release. The code ships to production behind a flag. You enable the flag for 1% of traffic. You watch the error rates, latency distributions, and business metrics. If nothing breaks, you ramp to 10%, then 50%, then 100%. If something breaks at 1%, you kill the flag. No rollback. No hotfix. No incident. Just a config change.

Martin Fowler's taxonomy of feature toggles clarifies the design space.[Fowler-toggles] He identifies four categories: release toggles (ship incomplete code as latent paths), experiment toggles (A/B tests), ops toggles (runtime kill switches for performance-sensitive features), and permission toggles (feature access by user segment). For the headless factory, release toggles are the most important. They enable trunk-based development by allowing agents to merge incomplete features without exposing them to users. An agent implementing a multi-step feature can merge the data layer behind a release toggle on day one and the UI layer on day two. Each merge is independently safe. The toggle ensures that partial work never reaches users. This aligns directly with the short-lived branch discipline: you do not need a long-lived feature branch if the code ships dark.

This advice becomes mandatory when the volume of changes increases by an order of magnitude and the author has no intuition about impact.

**Progressive delivery as the deployment model.** James Governor coined the term "progressive delivery" in 2018 to describe the broader practice that encompasses canary releases, dark launches, blue-green deployments, and A/B testing under a single operational philosophy: deploy to a small audience, observe, and expand incrementally.[Governor-PD] For factory-generated code, progressive delivery is the natural model. Every agent-produced change is, from the factory's perspective, an experiment. The factory implemented a spec. Whether the implementation is correct under all production conditions is an empirical question that progressive delivery answers with data rather than assumptions. The cadence is: dark launch to internal users, canary to 1% of traffic, observe for a defined window, expand to 10%, observe again, and promote to general availability. Each stage has automated gates. The factory does not need to get it right on the first try - it needs the infrastructure to detect when it got it wrong before most users are affected.

**Canary deployments with automated rollback triggers.** A canary deployment sends the new version to a small subset of production instances while the rest of the fleet runs the old version. Traffic splits between them. Automated monitors compare the canary's error rate, latency, and key business metrics against the baseline.

At human scale, a developer watches the canary dashboard and decides whether to proceed or roll back. At agent scale, that developer is reviewing the next ten PRs in their queue. The canary needs to make its own decision. If the error rate exceeds a threshold - say, a 2x increase over the baseline - the deployment rolls back automatically without human intervention.

Define rollback triggers precisely. Vague triggers ("if things look bad") do not automate. Precise triggers do:

- Error rate exceeds 2x the trailing 7-day average for more than 5 minutes
- P99 latency exceeds 3x the baseline for more than 3 minutes
- Key business metric (conversion rate, payment success rate) drops by more than 1% for more than 10 minutes

These thresholds are organization-specific. The point is not the exact numbers - it is that they are numbers, not feelings. Automated rollback runs on numbers.

**Staged rollouts by risk tier.** Not all changes need the same deployment ceremony. A copy change in a tooltip can go straight to production. A change to the payment processing pipeline needs a multi-stage rollout with extended monitoring at each stage. Use the same risk tiers from your review process (Chapter 12) to determine deployment strategy.

## Agent-Friendly Monitoring

Production monitoring was built for humans. Dashboards with charts, alert pages with colored dots, PagerDuty notifications that wake someone at 3 AM. All of this assumes a human will look at the data, interpret it, and decide what to do.

In a headless factory, the first responder to a production issue should be an agent, not a human. That requires monitoring tools that agents can query, interpret, and act on programmatically.

> **Case Study: Dash0's Agent-First Design**
>
> Mirko Novakovic, CEO of Dash0 and former founder of Instana (acquired by IBM), described a fundamental rethinking of observability on the AI Native Dev podcast (Ep 041): "The way we now design our product is really that we think of everything first in the perspective of an AI agent. And also what an AI agent could probably do with that information and how we can make life easier for the user then."[ANDev-041]
>
> Novakovic's insight cuts to the core of why traditional monitoring fails in agentic workflows: "Charts are good for users, not good for agents. We created charts because we as humans, we are really good at looking at a chart and seeing a spike. Where the agent will actually look at the underlying data and do a deep analysis of the data. But we cannot look at 5,000 data points and then see this. An agent doesn't need charts anymore."
>
> The practical implication: Dash0 replaced chart-centric dashboards with textual service summaries as the primary interface. "Today the primary information we give you on a service is a textual description of the status of the service. It would tell you your service is operating fine, it is in the range of the performance of the last 30 days, but we found two errors which came up recently that we haven't seen before which are suspicious." An agent can consume that. A chart, it cannot.

Charity Majors, co-founder of Honeycomb, takes this further with what she calls the deploy-and-observe loop.[Majors-ODD] Her principle: the person who writes the code should deploy it and watch it, with a maximum deploy time of 15 minutes. Feature flags plus observability provide the confidence to ship fast. In the headless factory, the "person" who writes the code is the factory itself, which means the factory needs the observability infrastructure to watch its own output. This is the monitoring-as-context loop: production metrics flow back into the factory not as alerts for humans but as structured data that agents consume, evaluate, and act on. Majors' insight maps directly - the factory is both the author and the first responder, collapsing the feedback loop from hours (developer deploys, goes to lunch, checks dashboard after lunch) to minutes (factory deploys, factory observes, factory reacts).

The *Accelerate* research provides the measurement framework for this loop. Forsgren, Humble, and Kim identified four key metrics that predict software delivery performance: deployment frequency, lead time for changes, mean time to recovery (MTTR), and change failure rate.[Forsgren] These four metrics should be the factory's primary health indicators. Not lines of code generated, not PRs created, not specs completed - those are activity metrics. The DORA four are outcome metrics. A factory that generates 200 PRs per day but has a 15% change failure rate and a 4-hour MTTR is performing worse than one that generates 50 PRs per day with a 2% failure rate and 15-minute recovery. Instrument your factory against the DORA four from the start.

The Sentry MCP server, built by David Cramer (Ep 015), demonstrates the same pattern from the error-tracking side. Cramer described the integration: "In Claude or Cursor, I can say, 'what was the total token consumption of X service yesterday?' And it can answer that through Sentry's MCP call."[ANDev-015] This is not just API access - the MCP server embeds agents that translate natural language queries into API calls, aggregate results, and return structured answers.

Three capabilities make a monitoring system agent-friendly.

**Queryable via MCP or structured API.** The monitoring system must expose its data through an interface that agents can call - MCP servers, REST APIs with well-documented schemas, or GraphQL endpoints. Agents cannot read dashboards. They cannot interpret screenshots. They need structured data they can process programmatically.

**Anomaly detection as structured output.** Instead of showing a human a chart and relying on their pattern recognition, the monitoring system should detect anomalies and emit them as structured events: which metric, what baseline, how far the deviation, when it started, what changed around that time. These events are consumable by agents that can then correlate them with recent deployments, recent merges, and spec changes.

**Traceability from alert to deployment to PR to spec.** When a production alert fires, the agent investigating it needs to answer a chain of questions: What changed? When was it deployed? Which PR introduced it? What spec was that PR implementing? If your deployment metadata includes PR references, and your PRs include spec references, this chain is traversable programmatically. If any link is missing, the agent hits a dead end and a human has to investigate manually.

## The Feedback Loop Back to the Factory

Here is where the factory becomes a loop.

A production incident fires. The monitoring system detects an error rate spike on the checkout service. An agent queries the monitoring MCP server, correlates the spike with a deployment that happened 45 minutes ago, traces that deployment to PR #4721, and traces PR #4721 to spec FEAT-892.

Now the factory has something it did not have before: a signal from production that traces back to a specific spec. The incident is not just a bug to fix. It is information about the factory's output quality that should influence the factory's behavior.

Three types of feedback matter.

**Spec gaps.** The spec said "handle payment failures." It did not specify what happens when the payment gateway returns a timeout versus an explicit rejection. The agent implemented both as generic failures. The production incident reveals that timeouts need retry logic and rejections do not. The feedback: the spec formalization step (Chapter 6) needs to prompt for timeout-vs-rejection distinction whenever payment integrations are involved.

**Validation gaps.** The test suite passed, but it did not include a test for the specific failure mode that caused the incident. The feedback: the validation layer (Chapter 11) needs a new test pattern, or the test generation prompt needs to be updated to cover gateway-specific error codes.

**Onboarding gaps.** The agent used a retry library that the team deprecated three months ago. The production incident occurred because the deprecated library has a known bug under high concurrency. The feedback: the codebase onboarding context (Chapter 8) needs to include the deprecation notice and the approved alternative.

Each of these feedback loops closes at a different point in the pipeline. The factory does not just produce code - it produces data about its own failures that improves its future output. This is the CDLC (Chapter 3) in action. Context is not a static artifact you write once. It is a living system that evolves with every production signal.

The most mature headless factories automate parts of this feedback loop. A production incident triggers an agent that investigates the root cause, identifies which pipeline stage failed, and proposes a context update - a new rule in CLAUDE.md, a new test pattern, a new onboarding warning. A human reviews and approves the context change. The factory gets smarter.

## Post-Deployment Spec Closure

A spec is not done when the code merges. It is done when the feature works in production.

Post-deployment closure has three steps, and they are embarrassingly easy to skip in the excitement of shipping.

**Mark the spec as implemented.** Whatever tracking system holds your specs - Jira, Linear, Notion, a custom system - the spec status should update automatically when the deployment completes and the monitoring confirms stable behavior. If the canary rolls back, the spec reverts to in-progress. This is not a manual status update. It is an event-driven state machine.

**Update the codebase onboarding context.** The new feature changed the system. Maybe it added a new API endpoint, introduced a new database table, or established a new integration pattern. The onboarding context (Chapter 8) that future agents will consume needs to reflect these changes. If it does not, the next agent that works on a related feature will not know about the new endpoint and may duplicate functionality or introduce conflicts.

**Archive the decision log.** The PR description, the agent's decision log, the review comments, the validation report - these artifacts tell the story of how this feature was built. They are invaluable when a future engineer (or agent) needs to understand why the implementation looks the way it does. Mirko Novakovic referenced the practice from his IBM days: "Whenever you did a decision, you had to document it and explain why. Because whenever you had a new team member join the team, they ask you, why did you use this framework? And you can pinpoint them to the document because there was actually a reason for it."[ANDev-041]

The CDLC ensures this closure happens. It is not an optional post-mortem exercise. It is a pipeline stage, just like validation or review. If the spec is not closed, the factory's records are incomplete, and future runs operate on stale context.

## Maintenance and Bug Fixes

In a headless factory, bugs do not get hand-patched. This is one of the hardest cultural shifts for teams adopting agentic development.

A developer sees a bug in production. Their instinct is to open the editor, fix the three lines, push the commit, and move on. They have the context, they understand the problem, the fix takes ten minutes. Going through the full pipeline - capturing intent, formalizing a spec, running the agent, validating, reviewing - takes an hour. Why would anyone do that?

Because the fix is not the point - the pipeline is the point.

When a developer hand-patches a bug, they fix the symptom. When the same bug enters the pipeline as new intent - "this behavior is wrong, the correct behavior is X" - the factory produces a fix and also updates its context. The spec captures the correct behavior, the test suite gains a regression test, the onboarding context records the pitfall. The next time an agent works on related code, it knows about this edge case.

Hand-patching is a leak in the feedback loop: a fix that exists only in the code, with no spec, no test, no context update. The factory cannot see it, so the factory will make the same mistake again.

The discipline is simple: every change enters through the pipeline. Bug reports become intent. Intent becomes spec. Spec becomes implementation. The loop closes.

This does not mean the process must be slow. A low-risk bug fix - a typo, a wrong constant, a missing null check - can fly through the pipeline in minutes if your risk tiers are calibrated correctly. The pipeline has a fast lane. What it does not have is a bypass.

## Tooling

The tooling landscape for the merge-deploy-monitor stage is more mature than for earlier pipeline stages because much of it predates the agentic era. The challenge is not finding tools - it is configuring them for agent-scale throughput.

**Merge automation and queues.** GitHub auto-merge, Graphite merge queue, GitLab merge-when-pipeline-succeeds, Mergify, Bors-ng. These tools serialize merges, handle rebasing, and eject failing PRs from the queue. At agent scale, the merge queue is infrastructure, not a convenience feature.

**CI/CD acceleration.** Namespace (GitHub Actions acceleration), Turborepo and Nx (incremental builds), Bazel (hermetic builds), Launchable (smart test selection), BuildPulse (flaky test detection). The goal is to reduce the per-PR CI time from minutes to seconds, because at hundreds of PRs per day, every minute of build time costs hours of aggregate throughput.

**Feature flag platforms.** LaunchDarkly, Statsig, Flagsmith, Unleash, Eppo. These provide the runtime infrastructure for staged rollouts, A/B testing, and kill switches. The key requirement for headless factories is API-driven flag management - agents need to create and configure flags as part of the implementation, not as a manual post-deployment step.

**Monitoring and observability with agent interfaces.** Sentry MCP server[Sentry-MCP] (error tracking), Dash0[Dash0] (OpenTelemetry-native observability with Agent Zero), Datadog (API-rich monitoring), PagerDuty (incident management with API automation). The critical requirement is that these tools expose their data through MCP servers or structured APIs that agents can consume. A monitoring tool that only works through a human-operated dashboard is a bottleneck in a headless factory.

**Deployment automation.** ArgoCD, Flux, Spinnaker, AWS CodeDeploy, Vercel, Railway. These handle the mechanics of getting code from the mainline to production instances. The key feature for headless factories is automated canary analysis with rollback triggers - the deployment system must be able to decide on its own whether to proceed or roll back.

## Decision Matrix

The following matrix maps decisions across the merge-deploy-monitor stage to the appropriate level of automation based on the maturity of your factory and the risk tier of the change.

**Merge triggering.** Low-risk changes: auto-merge on approval. Medium-risk: auto-merge on approval with merge queue serialization. High-risk: auto-merge on approval with merge queue plus mandatory staging deployment before production.

**Deployment strategy.** Low-risk: direct deploy, no canary. Medium-risk: canary deployment with automated rollback on error rate spike. High-risk: multi-stage canary with extended monitoring windows (hours, not minutes) and manual promotion between stages.

**Incident response.** Low-severity: agent investigates, proposes fix, fix enters pipeline. Medium-severity: agent investigates, human reviews root cause analysis before fix enters pipeline. High-severity: human-led investigation with agent assistance, post-incident review updates factory context.

**Feedback loop.** All severities: production incidents trace back to originating spec. Context updates (rules, skills, onboarding docs) are proposed by agent, reviewed by human, and merged into the context repository.

## The Circle Completes

The ten stages of the pipeline from Chapter 2 are not a waterfall - they are a cycle.

Intent enters the factory. It is formalized into a spec, reviewed by a human, handed to an agent with full codebase context, implemented in an isolated sandbox, validated by six layers of automated checks, reviewed by humans and AI, merged into the mainline, deployed behind feature flags, monitored by agent-queryable observability tools, and - when something goes wrong - the production signal re-enters the factory as new intent.

The factory learns. Every production incident that traces back to a spec gap improves the spec template. Every validation failure that escapes to production improves the test generation prompts. Every onboarding miss that causes an agent to use a deprecated library improves the codebase context. The CDLC is the mechanism that captures these learnings and distributes them to every future agent run.

This is the destination: not a tool, not a framework, but a way of organizing software production where the human job is designing and maintaining the factory - its context, its quality gates, its feedback loops - while the factory runs.

Steve Kuliski at Stripe described the end state simply: an engineer sees a Jira ticket, clicks a single emoji in Slack, and an agent spins up an entire replica of Stripe, implements the change, runs CI, generates a PR, and waits for review.[ANDev-052] 1,300 PRs per week, with human intervention only at the review gate. But behind that simplicity is the entire pipeline: the context that teaches the agent how to build Stripe, the validation that catches failures before humans see them, the merge queue that serializes a thousand weekly PRs, the monitoring that feeds production signals back into the factory.

The factory is not magic - it is engineering. It has stages, feedback loops, quality gates, and failure modes. You build it one stage at a time, instrument it, tune it, and gradually shift from manually operating each stage to designing the stages and letting the machines run. The machine writes the code. You build the machine.

---
