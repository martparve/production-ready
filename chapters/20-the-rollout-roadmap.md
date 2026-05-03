# Chapter 20: The Rollout Roadmap: From First Agent to Full Factory

You have the blueprint. Eighteen chapters of architecture, validation, context engineering, security, governance, and cost management. You know what the factory looks like when it runs.

Now you need to build it. And the order in which you build it matters as much as what you build. Organizations that try to stand up the full headless pipeline in a single quarter learn an expensive lesson: the factory is not a product you install. It is a capability you grow. The interactive phase - engineers working alongside agents in IDEs and CLI tools - is not a detour on the way to headless operation. It is the training ground where your teams develop the judgment, the context, and the process discipline that headless operation demands.

This chapter traces the full path from "we have no factory" to "headless factory running autonomously with humans as overseers." It covers the prerequisites that must be in place before you start, the team structures that sustain the effort, the build sequence for technical capabilities, the adoption phases for rolling it across the org, the evolution of the human role, and the enablement work that makes all of it stick.

## Maturity Prerequisites: Fix the Foundation Before You Accelerate

The most dangerous assumption in AI-native development is that AI will fix your broken process. It will not. It will make it worse, faster.

The 2025 DORA report[DORA-2025] quantified what many practitioners already suspected. Daniel Jones, speaking on the AI Native Dev podcast (Ep 045), put it plainly: "Teams with high levels of development maturity went faster when they introduced agentic coding. Teams with low levels of maturity went slower."[ANDev-045] He framed this through the theory of constraints: speed up one part of a system without addressing the bottlenecks on either side, and you create pile-ups. If agents can churn out commits every few minutes but your lead time to production is three days, you end up with a mountain of merge conflicts and a branch that has diverged so far from main that CI becomes meaningless.

This is not a minor inconvenience. It is a structural failure mode. Every weakness in your engineering practice - poor test coverage, manual deployment gates, undocumented conventions, inconsistent code review - becomes a multiplier of dysfunction when agents enter the picture.

> **Case Study: AI Amplifies Indiscriminately**
>
> Bhageetha from ThoughtWorks, speaking on the AI Native Dev podcast's 100th episode retrospective (Ep 050), captured the dynamic in a single sentence: "AI amplifies indiscriminately. So if you have a bad setup, you might just amplify that bad setup. And if you have a good one, everything might go well." She pointed to the infrastructure gap that most organizations underestimate: "Can you actually, in your organization, with your pipelines, with your processes, support an increase in throughput? I think a lot of organizations are still underestimating this foundation that you need."[ANDev-050]
>
> Guy Podjarny reinforced the point: "If the agents just replicate the code base, well, a lot of the things that you've done before in your code base, you don't actually want to repeat." The takeaway is that agent adoption is not just a tooling change - it is a stress test for your entire engineering practice. Organizations with clean foundations get amplified benefits. Organizations with sloppy foundations get amplified pain.

Before you touch agent tooling, audit four fundamentals.

**Automated testing.** Not aspirational coverage targets - actually passing tests that run on every commit. If your test suite is flaky, fix the flakes first. If your coverage is below 50%, raise it. Agents need a feedback signal to know whether their output works. Tests are that signal. Without them, the agent loops endlessly or ships broken code that nobody catches until production.

**Clean CI pipeline.** Every commit must run through a pipeline that builds, tests, lints, and reports results within minutes. If your CI takes 45 minutes, agents will stack up waiting for feedback. If your pipeline has manual approval gates before staging, those gates become the new bottleneck. Strip your pipeline to the essentials and make it fast.

**Version control discipline.** Trunk-based development or short-lived branches. If your team runs long-lived feature branches that diverge for weeks, agent-generated code will conflict with everything. The factory model assumes frequent integration. If your branching strategy does not support that, change the strategy before introducing agents.

**Documented conventions.** This does not mean a 200-page wiki that nobody reads. It means the minimum viable set of decisions that an agent needs to produce code consistent with your codebase: which framework version, which patterns, which API conventions, where things go in the directory structure. If these live only in senior engineers' heads, they need to be written down - not for the humans, but for the instruction files that will guide every agent session.

Jones listed what "good" looks like in concrete terms: test coverage, alignment on coding standards, small batch sizes in stories, and a short path to production.[ANDev-045] All of these are just good engineering from the last two decades of software development. The factory does not require exotic prerequisites. It requires that you have actually done the basics.

### The Skills Gap Is the Bigger Prerequisite

Even with a solid engineering foundation, you face a second challenge: your engineers do not yet know how to work with agents.

The numbers here are sobering. An MIT study reported a 95% failure rate for agentic projects.[Agentix-95pct] The Agentix Foundation's analysis (Ep 035) dug into why: "The reason for that failure is likely 99% of engineers, programmers, developers, project managers don't know how to actually build agentic systems. And it's a byproduct of a new emerging space."[ANDev-035]

This is not a reflection of engineering talent. It is a reflection of the fact that nobody was trained for this. The comparison to the early internet is instructive: in the late 1990s, corporations attempted web projects with teams that knew desktop software but had never built a web application. The failure rate was astronomical - not because the technology was bad, but because the skills had not been developed.

The same dynamic applies here. Your engineers need to learn context engineering, spec writing, agent debugging, and validation pipeline design. These are not skills that transfer automatically from traditional development. Enablement is not optional - it is a prerequisite on par with clean CI and automated testing. We will return to enablement in detail in Section 19.6.

## Team Topologies for Operating the Factory

The factory is infrastructure. Like CI/CD pipelines, like cloud platforms, like observability stacks - someone has to build it, someone has to run it, and someone has to use it. The organizational question is how you divide those responsibilities.

Three models emerge from organizations that have deployed AI code factories at scale. Each reflects a different trade-off between consistency and autonomy.

### Model A: Platform Team Builds, Everyone Uses

A dedicated team of 3-5 engineers builds and maintains all factory infrastructure: the agent harness configuration, the sandbox environment, the validation pipeline, the MCP integration layer, the instruction file hierarchy, and the governance gates. Product teams are consumers. They write their domain-specific context (instruction files for their repos, spec templates for their features) but they do not modify the factory itself.

**Strengths.** Speed of initial build-out. Single point of accountability for reliability. Consistency across all teams from day one. No duplication of effort.

**Weaknesses.** The platform team becomes a bottleneck for feature requests. Product teams have no ownership of the tooling and treat it as "someone else's problem." If the platform team gets priorities wrong, every team suffers.

**Best for.** Early-stage rollouts (first 3-6 months). Organizations with an existing platform engineering function. Small-to-medium orgs where one team can cover all teams' needs.

### Model B: Platform Builds Foundation, Teams Extend and Contribute

The platform team builds and owns the core: the pipeline, the sandbox infrastructure, the validation framework, the MCP gateway, the governance enforcement layer. Product teams own their domain-specific configuration - instruction files, spec templates, custom validation rules, domain MCP servers. An inner-source model lets teams contribute improvements back to the core platform.

**Strengths.** Teams own their context engineering, which they should because they know their domain best. The platform team focuses on what it does best: shared infrastructure. Broader capability development across the org.

**Weaknesses.** Requires clear boundaries between "platform responsibility" and "team responsibility." Without those boundaries, you get finger-pointing when something breaks. Needs a contribution model (PR review, compatibility testing) that adds overhead.

**Best for.** Mid-stage rollouts (months 4-12). Organizations with strong engineering culture and teams capable of self-service. Orgs that want distributed ownership.

### Model C: Distributed with Community of Practice

No dedicated platform team. Every team builds and maintains its own factory configuration. A community of practice (guild) meets regularly to share patterns, discuss what works, and converge on standards.

**Strengths.** Maximum experimentation velocity. Each team can optimize for its specific domain. No bottleneck from a central team.

**Weaknesses.** Fragmentation. Duplicate effort across teams solving the same problems. Governance is the hardest to enforce - each team can cut corners in its own config. Knowledge stays siloed unless the guild is unusually effective.

**Best for.** Small organizations (under 30 engineers). Exploratory phases where nobody knows what works yet. Research-oriented teams.

### Which Model When

The progression for most organizations is A then B. Start with Model A: a dedicated team builds the initial factory infrastructure while one or two pilot teams validate it. After the pilot proves the model, transition to Model B: the platform team opens the contribution model, product teams take ownership of their context engineering, and the platform team shifts to maintaining the core and building the next layer.

Model C is rarely the right starting point. The governance overhead - ensuring every team maintains consistent security gates, coverage floors, and API standards - makes distributed ownership impractical without a platform foundation already in place.

### Platform Team Composition

The factory platform team is not a traditional DevOps team, though it overlaps. The core competencies are:

**Context engineering.** Someone who understands instruction file design, prompt architecture, and how context flows through the agent's decision-making. This is the most novel skill and the hardest to hire for. In practice, you develop it internally by putting your best engineers through the pilot.

**Pipeline and CI.** Someone who can build and maintain the validation pipeline, the sandbox provisioning, the branch automation, and the merge infrastructure. This is the most traditional skill on the team.

**Security.** Someone who understands the trust model from Chapter 15 - sandboxing, secret management, MCP permission control, and the attack surface that agent access creates.

**Product sensibility.** Someone who bridges factory capabilities and what product teams actually need. Without this, the platform team builds technically excellent infrastructure that nobody uses.

Start with 3-5 people. At maturity, expect 5-8, depending on the number of teams served and the complexity of your factory configuration. This is comparable to the size of platform engineering teams that manage CI/CD and cloud infrastructure in organizations of similar scale.

## The Capability Build Sequence

Order matters. Each layer depends on the one below it, and building out of sequence creates capabilities you cannot use because their prerequisites are missing. The layers below represent a recommended sequence, not a rigid prescription. Adjust the timing to your organization's pace, but do not skip layers.

### Layer 0: Minimal Viable Factory (Weeks 1-2)

This is learning to drive before building the highway.

Pick a harness. Claude Code, Codex CLI, Cursor with agent mode - it does not matter which. What matters is that one or two engineers start using it on real (small) tasks. Write a basic instruction file for your repo. Try the agent on a bug fix, a test addition, a small feature. See what it gets right and what it gets wrong. Document what you learn.

Sean Roberts of Netlify (Ep 031) calls this the Crawl phase: "Audit what people are doing. Figure out what's going on. If they're using spec-driven development, that might be a little different looking of an agent experience than if they're using some other tool."[ANDev-031] The goal is not productivity. The goal is literacy. Your engineers need to experience what agents can and cannot do, what context they need, and how they fail.

#### Tooling Choices

The harness you pick here shapes what is possible at Layer 4 and beyond. Prioritize tools that run headless - if the agent requires an IDE window, it cannot run in a cloud pipeline.

| Option | Pros | Cons | Headless path |
|---|---|---|---|
| **Claude Code (CLI)** | Runs in terminal, SDK available for programmatic use, direct path to headless via `--headless` flag and Claude Code SDK. Strong context file support (CLAUDE.md hierarchy). | Anthropic-only models. Requires API key management. | Direct - same tool scales from interactive to headless |
| **Codex CLI** | Open-source, runs in terminal, OpenAI models. Simple sandbox model with network-disabled execution. | Smaller ecosystem. Fewer MCP integrations. Less mature instruction file model. | Moderate - CLI-native but fewer orchestration primitives |
| **Cursor / Windsurf** | Familiar IDE experience, lower learning curve for engineers reluctant to use terminal. Multi-model support. | IDE-dependent - no headless mode. Builds habits (visual diff review, inline chat) that do not transfer to headless operation. | Dead end - requires retraining when you move to headless |
| **Aider** | Open-source, terminal-based, multi-model. Git-aware with automatic commits. | Thinner context engineering support. No native SDK for headless orchestration. | Partial - terminal-native but limited orchestration |

**Recommendation for fastest path to headless:** Start with Claude Code CLI. Engineers learn the terminal-based workflow from day one, the instruction file hierarchy (CLAUDE.md) transfers directly to headless operation, and the SDK provides programmatic control when you reach Layer 4. If your organization has an existing OpenAI contract, Codex CLI is a reasonable alternative, but expect more custom work at the orchestration layer.

The output of Layer 0 is not infrastructure. It is understanding. Two or three engineers who have actually used agents on real work and can articulate what needs to be built to make agents effective. Everything that follows builds on that understanding.

### Layer 1: Agent + Context + Sandbox (Weeks 3-6)

Now you build the first real infrastructure.

**Branch sandboxing.** Every agent run operates in an isolated branch with a disposable environment. The agent cannot touch main, cannot access production secrets, cannot interfere with other engineers' work. This is the foundational safety mechanism from Chapter 9.

**Instruction file hierarchy.** Org-level instructions (coding standards, security rules), repo-level instructions (framework conventions, directory structure), and module-level instructions (specific patterns for this service or component). The hierarchy from Chapter 8 does not need to be perfect. It needs to exist, with the right inheritance model, so that every agent session receives baseline context.

**Basic validation gates.** At minimum: build passes and tests pass. These two gates catch the majority of agent errors. More sophisticated validation (security scanning, coverage enforcement, API compliance) comes later. Do not over-build the validation pipeline before you have enough agent volume to justify the investment.

#### Tooling Choices

**Sandboxing and environment isolation.** The agent needs a disposable workspace where it cannot damage production or interfere with other work.

| Option | Pros | Cons | Headless path |
|---|---|---|---|
| **Docker containers + Nix/Flox** | Fully reproducible environments. Nix ensures identical toolchains across local and CI. Flox wraps Nix with simpler UX. Containers provide hard process isolation. | Nix has a steep learning curve. Container builds add seconds to every agent run. | Excellent - same container definition runs locally and in cloud CI |
| **GitHub Codespaces** | Zero-config cloud environments. Per-branch isolation built in. Familiar to GitHub-native teams. | Cost scales linearly with usage. 30-60 second spin-up time. Vendor lock to GitHub. | Good - already cloud-native, but expensive at scale |
| **Gitpod / Devcontainers** | Open standard (devcontainer.json). Works across GitHub, GitLab, self-hosted. Faster startup than Codespaces. | Requires self-hosting for air-gapped environments. Less polished than Codespaces. | Good - portable across cloud providers |
| **Branch isolation only (no container)** | Simplest setup. Agent runs in CI runner with branch checkout. No environment management overhead. | No process isolation - agent can access host filesystem. Environment drift between runs. | Adequate for early stages, replace by Layer 3 |

**Recommendation:** Docker containers with Flox for environment management. Flox gives you Nix's reproducibility without Nix's learning curve, and the container definition becomes your headless execution environment at Layer 4 with zero rework. If your team already uses GitHub Codespaces, use those for Layers 0-1 and plan the migration to containers when cost becomes a factor.

**Instruction file hierarchy.** Native formats depend on your harness choice:

- Claude Code: `CLAUDE.md` at repo root, `CLAUDE.md` in subdirectories, plus `.claude/` for settings
- Codex CLI: `AGENTS.md` (Codex) or `codex.md` at repo root
- Cursor: `.cursor/rules/` directory with `.mdc` rule files

Start with a single repo-level file containing: framework version, directory structure, testing conventions, coding standards, and common pitfalls. Expand to subdirectory-level files as you learn which modules need specialized guidance.

**Basic CI.** GitHub Actions is the default for GitHub-hosted repos. GitLab CI for GitLab shops. The specifics matter less than the principle: every agent-produced branch triggers build + test automatically. A minimal workflow file that runs on branch push is sufficient for Layer 1.

The output of Layer 1 is a working loop: an agent picks up a task, operates in a sandbox, produces code, and the validation gates check whether the output works. It is clunky, it probably requires manual triggering, and the agent still needs heavy guidance. That is fine. You now have the skeleton that every subsequent layer will extend.

### Layer 2: Spec Pipeline + Review (Weeks 7-12)

This is the inflection point. Before Layer 2, agents are sophisticated code-completion tools. After Layer 2, they are factory workers that receive formal work orders and produce traceable output.

**Spec formalization.** Implement the spec structure from Chapter 6 - inputs, outputs, edge cases, constraints, acceptance criteria. Not every task needs a full spec. Start with new features and significant changes. Bug fixes and minor updates can run with lighter specifications.

**Spec review workflow.** A human reviews and approves the spec before the agent begins implementation. This is the single most impactful quality gate in the entire pipeline. A bad spec produces bad code that passes all your automated checks, because the checks are verifying the spec and the spec is wrong. Human judgment at the spec level is irreplaceable for now.

**Spec-to-implementation tracing.** Every PR should link back to its spec. Every acceptance criterion in the spec should map to a test in the implementation. This traceability is what makes quality auditable - not "does this PR look right?" but "does this PR satisfy the approved spec, and can I prove it?"

#### Tooling Choices

**Spec authoring and management.** The spec pipeline needs a format, a storage location, and a review workflow.

| Option | Pros | Cons | Headless path |
|---|---|---|---|
| **Kiro (spec-driven IDE)** | Purpose-built for spec-driven development. Structured spec format with requirements, design, and tasks. Built-in spec-to-implementation flow. | IDE-dependent (VS Code extension). Spec format is proprietary. Still early-stage product. | Partial - specs are reusable but the IDE workflow is not |
| **BMAD framework** | Open-source, comprehensive methodology covering personas (analyst, architect, developer). Markdown-based specs with clear structure. | Heavy process overhead - multiple "personas" and documents for each feature. Can feel ceremonial for small tasks. | Good - markdown specs feed directly into any headless agent |
| **Custom markdown templates + GitHub** | Full control over spec format. Specs live as markdown in the repo. Review via standard PR workflow. No new tooling to learn. | No guardrails - nothing enforces completeness. Template discipline depends entirely on team culture. | Excellent - simplest path, specs are just files in the repo |
| **GitHub SpecKit** | GitHub-native spec management. Integrates with issues and PRs. Structured format with built-in review flow. | GitHub-only. Still emerging. Less flexible than custom templates. | Good - GitHub Actions integration is straightforward |

**Recommendation for fastest path to headless:** Custom markdown templates stored in the repo, reviewed via PR. This is the least tooling to adopt, works with every agent harness, and the specs become input files for headless agent runs at Layer 4 without any format translation. Use EARS syntax (Chapter 6) for requirements within your templates to get structured precision without proprietary formats. Kiro is worth evaluating if your team struggles with spec discipline, but the IDE dependency is a liability for headless operation.

**Spec review workflow.** Keep it simple: spec is a markdown file, author opens a PR, reviewer approves before implementation begins. The agent reads the approved spec file as input. No special tooling needed - your existing PR review process works. Add a GitHub Actions check or CI step that verifies the spec file exists and contains required sections (inputs, outputs, acceptance criteria) before the implementation agent can run.

Why Layer 2 is the inflection point: it is where the factory begins producing output that is measurably different from ad-hoc agent usage. Teams with spec pipelines report lower rework rates, fewer "what was this supposed to do?" conversations in code review, and higher confidence in agent output. The spec is the forcing function that turns ambiguous intent into precise instructions, and precision is what agents need to produce correct code on the first pass.

### Layer 3: Validation Depth + Governance (Weeks 13-18)

With the spec pipeline producing consistent output, you can now invest in catching the failures that basic build-and-test gates miss.

**Validation layers 3-4.** Static analysis (security scanning, lint rules beyond basic formatting), integration testing, coverage enforcement with hard floors, and domain-specific validators. Chapter 11 covers these in detail. The key principle: add validation layers based on the failure modes you actually observe, not the ones you theoretically fear.

**AI-assisted code review.** An AI reviewer that checks for spec compliance, identifies potential issues, and flags patterns that deviate from conventions. This is not a replacement for human review - it is triage. The AI reviewer handles the mechanical checks (naming conventions, error handling patterns, test coverage gaps) so the human reviewer can focus on design decisions and architectural judgment.

**Org-wide quality governance.** The governance model from Chapter 18: org-level gates that no team can override, team-level gates that extend the org floor, and a clear inheritance hierarchy. This is when governance transitions from "each team does its own thing" to "the organization has consistent quality floors."

**MCP integrations.** Connect the factory to your external systems - issue trackers, documentation, monitoring, deployment pipelines. Each MCP server extends the agent's ability to gather context and take action without human intervention. Start with read-only integrations (pull context from Jira, read monitoring data) before adding write capabilities (create PRs, deploy to staging).

#### Tooling Choices

**AI-assisted code review.** An AI reviewer that runs on every agent-produced PR to catch issues before human review.

| Option | Pros | Cons |
|---|---|---|
| **CodeRabbit** | Mature product. Automatic PR reviews with line-level comments. Learns from review feedback over time. Supports spec compliance checking. | SaaS-only - code leaves your environment. Per-seat pricing adds up at scale. |
| **Qodo (formerly CodiumAI) / PR-Agent** | Open-source core (PR-Agent). Self-hostable. Generates tests alongside review. Covers security, style, and correctness. | Self-hosting requires infrastructure. Less polished than CodeRabbit for pure review. |
| **Graphite** | Fast PR workflow with stacked PRs. AI reviewer built into the PR tool. Designed for high-throughput teams. | Adds a PR workflow layer on top of GitHub. Review AI is secondary to the workflow tool. |
| **Custom (agent-as-reviewer)** | Use your chosen agent harness (Claude Code, Codex) as a reviewer with a review-specific instruction file. Full control over review criteria. | You build and maintain it. No feedback learning loop unless you build one. |

**Recommendation:** CodeRabbit for immediate value with minimal setup. If code cannot leave your environment, self-host Qodo/PR-Agent. The custom approach (agent-as-reviewer) becomes the right choice at Layer 4 when your factory is mature enough to run review agents headlessly - but it requires more infrastructure than the other options.

**Security scanning.** Add static analysis that runs before human review.

| Option | Pros | Cons |
|---|---|---|
| **Snyk** | Broad coverage: dependencies, code, containers, IaC. Good IDE integration for interactive use. Large vulnerability database. | Commercial pricing. Can be noisy with false positives on AI-generated code. |
| **Semgrep** | Open-source core. Custom rule authoring is straightforward. Fast - runs in seconds even on large codebases. | Community rules vary in quality. Enterprise features (supply chain, secrets) require paid tier. |
| **GitHub Advanced Security** | Native GitHub integration. CodeQL for deep semantic analysis. Secret scanning built in. | GitHub-only. CodeQL scans are slow on large repos. Limited to GitHub-hosted repos. |

**Recommendation:** Semgrep with custom rules tuned to your codebase patterns. Its speed matters for factory operation - a security scan that adds 10 minutes to every agent cycle is a bottleneck. Add Snyk for dependency scanning if your stack has a large third-party surface area. Both integrate cleanly into CI pipelines.

**First MCP servers to deploy.** Not all integrations are equally valuable. Prioritize by impact on headless operation:

1. **Git/GitHub MCP** - the agent reads PRs, issues, and commit history without manual copy-paste
2. **Sentry or error tracking MCP** - production errors flow directly into agent context for bug fixes
3. **Documentation MCP** - internal docs, API references, runbooks become searchable context
4. **Issue tracker MCP** (Jira, Linear) - the agent reads task descriptions and acceptance criteria from the source of truth

### Layer 4: Feedback Loops + Autonomy (Weeks 19-26)

The factory can now produce and validate code. Layer 4 makes it learn and self-correct.

**Monitoring-as-context via MCP.** Production metrics, error rates, and deployment outcomes flow back into the agent's context for future tasks. When an agent writes a feature and it causes a spike in error rates after deployment, that signal should inform the next task in the same domain. This is the feedback loop from Chapter 13 made operational.

**Progressive gate reduction.** For task categories where agents consistently produce correct output, begin reducing the gates. If agents have produced 50 consecutive PRs for API endpoint additions that pass all validation and require zero human review changes, consider allowing those PRs to auto-merge after validation. Gate reduction is earned, not assumed. Track the data.

**Validation layers 5-6.** Performance testing, accessibility verification, production simulation. These expensive validation layers are justified only when you have enough agent volume to amortize their cost and enough confidence in the earlier layers to know that the code reaching layers 5-6 is structurally sound.

**Evals framework.** Systematic evaluation of agent performance across task categories. How often does the agent produce correct output on the first pass? What types of tasks require the most human intervention? Where does context engineering need improvement? These evaluations inform both the platform team (what infrastructure to improve) and product teams (what context to add).

**Cost optimization.** With enough volume data, you can now route tasks to appropriate models - cheaper models for routine changes, expensive reasoning models for complex architectural work. Chapter 16 covers the economics. The optimization is ongoing, not one-time, because model pricing and capabilities change quarterly.

#### Tooling Choices

This is the layer where interactive development transitions to headless operation. The tooling choices here determine how fast you reach cloud-hosted autonomous execution.

**Headless agent triggers.** The agent needs to start without a human typing a command.

| Option | Pros | Cons |
|---|---|---|
| **GitHub Actions + Claude Code SDK** | Native CI/CD integration. Agent runs as a job step triggered by issue creation, PR event, or schedule. Claude Code SDK provides programmatic control. Same CLAUDE.md files from interactive use. | GitHub-only. Action runner costs at scale. Cold start for large repos. |
| **GitHub Actions + Codex CLI** | Same trigger model as above. OpenAI models. Simpler sandbox model (network-disabled by default). | Less mature orchestration. Fewer context engineering primitives than Claude Code. |
| **Custom orchestration (event-driven)** | Any event source (webhooks, message queues, cron). Any cloud provider. Full control over retry logic, parallelism, and routing. | You build and maintain the orchestration layer. Significant engineering investment. |
| **Goose (Block)** | Open-source agent framework. Extensible with custom tools. Provider-agnostic (any LLM). | No built-in orchestration - you still need triggers. Less opinionated about context engineering. |

**Recommendation for fastest path to headless:** GitHub Actions triggering Claude Code in headless mode (`claude --headless`). This is the shortest path from "engineer runs agent in terminal" to "agent runs in cloud on event trigger" because the instruction files, context hierarchy, and validation pipeline are identical. The transition is mechanical, not architectural. A GitHub Action that runs `claude --headless --spec path/to/spec.md` on issue label change gets you to headless operation in a single workflow file.

**Monitoring and observability.** Production feedback must flow back to the agent for the feedback loop to close.

| Option | Pros | Cons |
|---|---|---|
| **Sentry + Sentry MCP** | Error tracking with direct MCP integration. Agent reads stack traces, error context, and affected code paths. Mature product with broad language support. | SaaS pricing scales with event volume. MCP server is still early. |
| **Dash0** | Built for AI-native observability. OpenTelemetry-native. Designed to feed signals to agents, not just dashboards. | Newer product with smaller community. |
| **Datadog LLM Observability** | Comprehensive platform. Tracks LLM calls, token usage, latency, and errors. Strong alerting and dashboarding. | Expensive. Complex setup. The LLM observability features are an add-on to an already large platform. |
| **Custom (OpenTelemetry + MCP)** | OpenTelemetry is vendor-neutral. Build an MCP server that reads your OTEL data and exposes it to agents. | You build the MCP server. Requires understanding both OTEL and MCP. |

**Recommendation:** Sentry with the Sentry MCP server for immediate feedback loop closure. Sentry's MCP integration lets the agent read production errors directly, which is the single most valuable feedback signal for headless bug-fix operation. Add Dash0 or a custom OpenTelemetry MCP for broader operational metrics once the error-driven loop is working.

**Evals.** Measure agent performance systematically, not anecdotally.

Start simple: track first-pass success rate (did the agent's output pass all validation gates without human intervention?), rework rate (how many PRs required changes after human review?), and cycle time (how long from spec approval to merged PR?). Store these as structured data - a simple database table or even a spreadsheet. Sophisticated eval frameworks can come later. The data matters more than the tooling that collects it.

### Layer 5: Mature Headless Factory (Month 7+)

Routine work flows through the pipeline without human intervention. Bug fixes, test additions, documentation updates, straightforward feature implementations, API endpoint additions, dependency upgrades - these follow the spec-implement-validate-merge path with human oversight only at the spec review stage (and for some task categories, not even there).

Humans manage the factory itself: updating instruction files, refining validation gates, adjusting governance rules, handling architectural decisions, and debugging the cases where the factory produces incorrect output. Context engineering - the design of instruction hierarchies, spec templates, and validation rules - is the primary engineering discipline.

#### Tooling Choices

At Layer 5, the question is no longer which agent to use interactively. It is which execution platform runs your headless factory in the cloud.

**Headless execution platforms.** The agent runs as a service, triggered by events, producing PRs.

| Option | Pros | Cons |
|---|---|---|
| **Claude Code headless + GitHub Actions** | Continuation of the Layer 4 setup. Proven path. Same context files. SDK for orchestration. Anthropic maintains the runtime. | Single-vendor model dependency. GitHub Actions runners have resource limits for long-running agent sessions. |
| **Devin** | Purpose-built headless agent. Web interface for task assignment and monitoring. Handles multi-step tasks autonomously. | Fully managed SaaS - limited control over execution. Expensive. Opaque decision-making. Your context engineering (CLAUDE.md, specs) may not transfer. |
| **Factory (factory.ai)** | Designed for enterprise headless code production. Security and compliance features. Structured workflow management. | Commercial product with enterprise pricing. Less flexibility than building your own orchestration. |
| **Custom orchestration (Claude Code SDK / Goose / SWE-agent)** | Full control. Any model, any cloud, any trigger. Open-source options (Goose, Princeton SWE-agent) provide starting points. Optimize cost, latency, and routing per task type. | Significant engineering investment to build and maintain. You own reliability, scaling, and on-call. |

**Recommendation for production headless factory:** Claude Code headless on cloud compute (your own runners or a container platform) orchestrated via GitHub Actions for event triggers. This path has the lowest migration cost from interactive use - every CLAUDE.md file, every spec template, every validation gate works unchanged. For organizations with the platform engineering capacity, the custom orchestration path using Claude Code SDK as the agent runtime gives the most flexibility: route high-complexity tasks to reasoning models, routine tasks to fast models, and run multiple agent sessions in parallel on a Kubernetes cluster or serverless containers.

Devin and Factory are viable if you want to buy rather than build the orchestration layer, but evaluate carefully whether your existing context engineering (instruction files, spec templates, MCP integrations) transfers to their platform. Migrating a mature factory to a new platform is expensive. Building on a foundation that lets you own the runtime avoids that risk.

**The full headless stack at maturity:**

1. **Event source** - GitHub issue labeled, schedule trigger, Slack message, monitoring alert
2. **Orchestrator** - GitHub Actions workflow or custom service that receives the event, selects the right spec template, and provisions an agent session
3. **Agent runtime** - Claude Code headless (or equivalent) running in a container with the repo checked out, instruction files loaded, MCP servers connected
4. **Validation pipeline** - automated gates (build, test, lint, security scan, AI review) that run on the agent's output branch
5. **Merge policy** - auto-merge for low-risk tasks that pass all gates, human review queue for high-risk tasks
6. **Feedback loop** - production monitoring (Sentry MCP) feeding results back into the next agent session

This is not full automation. The factory never reaches a state where humans can walk away entirely. It reaches a state where human attention goes to work that requires human judgment, and everything else runs on infrastructure.

## Adoption Phases

The capability build sequence describes what to build. The adoption phases describe how to roll it across the organization. Building capabilities for one team is straightforward. Getting fifteen teams to adopt them is a different challenge entirely.

### Phase 0: Foundation (Weeks 1-6)

Build Layers 0 and 1. All teams start the Crawl phase: pick a harness, try it on small tasks, build initial literacy. The platform team (Model A) builds the sandbox infrastructure and validation pipeline.

During this phase, identify the pilot team. Selection criteria matter more than you think.

**The right pilot team has:** A willing tech lead (not just compliant). Moderate codebase complexity. Good test coverage (above 60%). A representative technology stack shared by at least 3-4 other teams, so what you learn transfers. And critically, not mission-critical - if the experiment slows the team for a few weeks, the business should not suffer.

**The wrong pilot team is:** The team with the most enthusiastic junior engineer but a skeptical lead. The team on the revenue-critical system with board-level visibility. The team whose codebase is so unusual that nothing they learn will transfer.

### Phase 1: Pilot (Weeks 7-12)

The pilot team runs the full pipeline: spec formalization, spec review, agent implementation, validation, code review. The platform team builds Layer 2 alongside the pilot team, using their feedback to shape the spec pipeline and review workflow.

This phase ends with a go/no-go decision based on measurable criteria:

- Does the factory produce output that passes code review with fewer than 2 change requests on average?
- Is the rework rate (changes after merge) comparable to or lower than human-written code for the same task types?
- Can engineers articulate how to write effective specs and debug agent output?
- Is the validation pipeline catching the errors it should catch, and is it fast enough (under 10 minutes) to support the factory's cycle time?

If the answer to any of these is no, extend Phase 1 and fix the gaps. Do not expand to more teams while the pilot is struggling. Every problem you skip in Phase 1 will be multiplied by the number of teams in Phase 2.

Expect a productivity dip before gains materialize. GitHub's enterprise study with Accenture - covering deployment across roughly 90% of the Fortune 100 - found that it takes 11 weeks for developers to fully realize productivity gains from AI-assisted workflows. During that ramp-up, teams experience slower throughput as they learn new patterns, build context files, and develop judgment about when to trust agent output. The study also measured concrete outcomes after the ramp-up: PR cycle time dropped from 9.6 days to 2.4 days - a 75% reduction - with 80% active license usage across the organization.[GH-Copilot-enterprise] These numbers set a useful benchmark for your pilot's go/no-go criteria. If your pilot team has not reached the 11-week mark, you are measuring the dip, not the steady state. The patience to wait for the full ramp-up curve is one of the hardest parts of the rollout.

One critical caveat on measurement: individual productivity metrics are misleading. The DORA 2024 report found that while individual developer productivity increased with AI tools, overall delivery throughput dropped 1.5% and stability declined 7.2%. The report also found that 39% of developers report little trust in AI-generated code.[DORA-2024] This means your go/no-go criteria must measure at the system level - lead time to production, deployment frequency, change failure rate - not just at the individual level. A pilot where every engineer reports feeling faster but the team's delivery throughput is flat or declining has a systems problem, not a perception problem. The factory accelerates code production, but if review queues, merge conflicts, or flaky tests absorb the gains, the organization sees no benefit.

### Phase 2: Expansion (Weeks 13-20)

Three to five teams join the factory. The platform team builds Layers 2-3 for the broader organization while the pilot team's configuration serves as the template. Each new team adapts the template to its domain: different instruction files, different spec templates, same pipeline and governance infrastructure.

This is when Model A transitions to Model B. The pilot team has developed enough expertise to contribute back to the platform. New teams take ownership of their context engineering while the platform team maintains the core. Establish the inner-source contribution model: how teams propose changes to shared configs, how those changes are reviewed, how they are rolled out.

The expansion phase is where most organizations hit their first serious cultural friction. The pilot team volunteered and was selected for willingness. The expansion teams may include skeptics, engineers who feel the factory is imposed rather than chosen. Section 19.6 addresses this directly.

### Phase 3: Org-Wide (Weeks 21-30+)

All teams operate through the factory for eligible task categories. The platform team builds Layer 4: feedback loops, progressive automation, evals, cost optimization. Governance is fully operational. The factory is infrastructure.

This phase has no end date. Like CI/CD and cloud infrastructure, the factory is maintained and improved continuously. New model capabilities require instruction file updates. New security threats require validation gate additions. Steady-state is not static; it is a slower rate of change, focused on optimization rather than construction.

## The Journey to Humans as Overseers

The adoption phases describe the organizational timeline. But within each engineer's daily work, a parallel evolution is happening: the gradual transfer of execution from humans to machines. This evolution has five stages, and understanding where your team is on the spectrum helps you calibrate expectations, measure progress, and avoid pushing teams past what their infrastructure can support.

### Stage 1: Humans Write Code, AI Assists

This is the pre-factory state that most organizations occupied in 2024-2025. Engineers write code in their IDE. AI provides completions, suggestions, and inline help. The human is the primary author. The AI is a sophisticated autocomplete.

The human role: implement, test, debug, review, deploy. The AI role: suggest, accelerate individual keystrokes, generate boilerplate on demand.

This stage delivers real productivity gains - the DORA 2025 study showed documentation improvements and modest velocity increases.[DORA-2025] But it does not change the fundamental model. The human is still the bottleneck. Every feature still flows through a human's fingers.

### Stage 2: AI Writes Code, Humans Review Everything

This is the early factory state, corresponding to Layers 0-2 of the capability build. The agent produces the implementation. Every output is reviewed by a human. Both the spec review gate and the code review gate are mandatory. Nothing merges without human approval.

The human role: write specs, review specs, review code, approve merges, debug failures. The AI role: implement specs, write tests, produce documentation, fix validation failures.

This stage feels slower than Stage 1 for some tasks, because the overhead of writing a spec and reviewing agent output can exceed the time to just write the code yourself. That is expected and correct. The investment is not in individual task speed - it is in building the judgment, the infrastructure, and the validation that make later stages possible.

### Stage 3: AI Writes Code, Humans Review Selectively

This is the maturing factory state, corresponding to Layers 3-4. The organization has enough data to implement risk-tiered review. Low-risk tasks (bug fixes, test additions, documentation, routine API changes) flow through validation gates and merge with minimal or no human code review. High-risk tasks (new features, architectural changes, security-sensitive code) still require full human review.

The human role: write and review specs, review high-risk code, manage factory configuration, handle exceptions. The AI role: implement, test, validate, auto-merge low-risk changes, flag high-risk changes for review.

The key enabler for Stage 3 is data. You cannot tier risk without knowing which task categories the agent handles reliably and which it does not. The evals framework from Layer 4 provides this data. Without it, risk-tiering is guesswork, and guesswork at Stage 3 leads to bugs in production.

### Stage 4: AI Writes and Reviews, Humans Set Direction and Handle Exceptions

This is the mature factory state, corresponding to Layer 5. AI agents handle both implementation and first-pass code review. Humans operate at the spec level and the architectural level. Day-to-day code production is factory output - humans see it only when exceptions are flagged.

The human role: define product direction, make architectural decisions, write and review complex specs, handle flagged exceptions, maintain factory infrastructure. The AI role: implement, test, validate, review, merge, monitor, flag exceptions.

This stage requires confidence in validation depth, governance enforcement, and feedback loops. It also requires organizational trust - leadership, product management, and engineering management all need to believe that the factory's output meets quality standards without human review of every line. That trust is earned through months of data at Stage 3.

### Stage 5: Humans as Overseers

This is the destination - the factory running as infrastructure with human oversight focused on strategy, architecture, and exception handling. Routine software development is an automated process, like payroll processing or inventory management. Humans design the system, set the constraints, and handle the edge cases that the system cannot.

Stage 5 is an asymptote that organizations approach but may never fully reach, because "routine" is a moving target - as the factory handles more task categories, the remaining ones are by definition the harder ones that require human judgment.

### Timeline Expectations

Stage 1 to Stage 4 is achievable in 6-9 months for an organization that starts with solid engineering fundamentals and invests in enablement. Stage 4 for routine work categories (not all work - routine work) is achievable by the end of 2026 for organizations that start now.

Stage 5 is a multi-year trajectory. The factory will continue to expand the set of tasks it handles autonomously, but the asymptote means the last 10-20% of tasks - the novel, the ambiguous, the cross-cutting - will require human involvement for years to come.

Do not set the expectation that your engineering team will be "fully autonomous" by Q4. Set the expectation that routine implementation work will be handled by the factory, and human attention will be freed for higher-value work. The former is achievable. The latter is the actual business value.

> **Case Study: Crawl, Walk, Run**
>
> Sean Roberts, VP of Applied AI at Netlify (Ep 031), structured his rollout advice around three phases that map directly to the stages above. The Crawl phase: "Audit what people are using. Ask them what's working, what's not. Figure out what's going on."[ANDev-031] Build an internal community - get engineers together to share what they are learning, pair-program with agents, and discover how different people approach the same problem differently.
>
> The Walk phase: invest in context files, document your key dependencies, and make implicit knowledge explicit. "So many code bases you see like, okay, to run a test suite, it's this magical command. That's not obvious. If you have those, make sure that they're in your context."
>
> The Run phase: shared sub-agents, centralized distribution of instruction files across repos, and evals to measure agent performance. "Centralizing these outside of a single agent is incredibly important. Because if you did this audit in step one, unless they all said, I only use Claude Code - picking one agent is a recipe for disaster."
>
> Roberts' framing reinforces a critical point: each phase builds on the learning from the previous one. You cannot centralize instruction files before you know what should be in them, and you cannot know what should be in them before you have used agents on real work.

## Enablement and Adoption Dynamics

You can build the best factory in the world and it will sit idle if your engineers do not know how to use it, do not want to use it, or do not believe it produces good output. Technical infrastructure is necessary but not sufficient. The human side of the rollout is where most organizations underinvest - and where the rollout succeeds or fails.

### The Adoption Paradox

Before discussing enablement tactics, it is worth understanding the broader adoption landscape your rollout enters. Stack Overflow's Developer Surveys show AI tool usage climbing from 76% in 2024 to 84% in 2025 - adoption is approaching universality. Yet trust is moving in the opposite direction: developer confidence in AI-generated code hit an all-time low in the same period.[SO-survey] This is a paradox your rollout strategy must account for. Engineers are using AI tools because they feel they have to - peer pressure, management expectation, competitive anxiety - not because they trust the output. The implication for rollout is that high adoption numbers in your organization do not signal success. Adoption without trust produces a specific failure mode: engineers use the tools superficially, accept low-quality output to save time on tasks they consider unimportant, and quietly rewrite agent output for anything that matters. Your enablement investment must target trust, not just usage.

The DX/Atlassian State of Developer Experience report reinforces this with harder numbers: 62% of developers say AI tools have little or no measurable impact on their productivity, even as management surveys report the opposite. Meanwhile, 97% of developers report losing an entire day or more per week to inefficiencies in their development workflow - inefficiencies that AI tools were supposed to address but largely have not.[DX-2024] Dismissing this skepticism as resistance to change is a mistake. The 62% who report no impact are telling you something about how the tools are being deployed, configured, and supported. Enablement is the bridge between adoption and impact.

### Enablement Is the Number One Factor

Justin Reock, Deputy CTO at DX (Ep 014), studied organizations that reported positive outcomes from AI tooling and compared them to organizations that did not. His conclusion was unambiguous: "The one word that I can use to sum all that up is enablement. That's really being missed by a lot of organizations."[ANDev-014]

The difference between successful and struggling organizations was not the tools, the models, or the budget. It was whether engineers were taught how to use the tools effectively. Reock identified specific gaps: understanding meta-prompting and multi-shot prompting, knowing how to manipulate system prompts and instruction files, understanding how context affects model output, and knowing which use cases deliver the highest value.[ANDev-014]

The highest-value use case his study identified was not code generation - it was stack trace analysis.[ANDev-014] Engineers who learned to feed stack traces to AI tools saved more time than engineers who used AI for code completion. The lesson: enablement is not "here is how you use Cursor." Enablement is "here are the ten workflows that save you the most time, here is how to do each one, and here is when to use which."

### What to Learn, What to Unlearn

Engineers adopting the factory need to develop three new competencies.

**Spec writing and review.** The ability to express intent precisely enough that an agent produces correct output. This is harder than it sounds. Engineers are trained to translate fuzzy requirements into code through iterative refinement - they write a bit, test it, adjust. Spec writing demands that the refinement happen upfront, in natural language, before any code is produced. It is a different cognitive skill.

**Context engineering.** Understanding how instruction files, knowledge bases, and MCP integrations shape agent behavior. An engineer who can diagnose "the agent used the wrong database pattern" as a context problem (missing instruction about the preferred ORM) rather than a model problem (the model is dumb) will be dramatically more effective than one who cannot.

**Agent debugging.** When the agent produces wrong output, where did the chain break? Was the spec ambiguous? Was context missing? Did the validation gates fail to catch the issue? Was the model simply wrong? Agent debugging is a new skill that combines traditional debugging intuition with prompt engineering and systems thinking.

Engineers also need to unlearn two habits.

**Writing code for every task.** The reflexive response to "this needs doing" should not be "let me open my editor." It should be "let me write a spec." This transition is genuinely uncomfortable for engineers who identify with the craft of coding. The discomfort is real and should be acknowledged, not dismissed.

**Reviewing style over correctness.** In human code review, experienced engineers develop strong opinions about naming, structure, idioms, and style. Agent-produced code will not match any individual engineer's style preferences. Reviewing agent code for correctness, security, and spec compliance is productive. Reviewing it for whether the variable names match what you would have chosen is not.

### The Junior Developer Pipeline

> **Case Study: How Do Juniors Learn?**
>
> Cian Clarke, engineering leader at NearForm (Ep 034), raised a concern that many leaders are thinking about: "One really unfortunate artifact we've seen of this AI native era is probably the reduction in hiring pipelines and also what the future looks like for junior developers."[ANDev-034] NearForm's engineering team averages eight years of experience per person. Senior engineers can steer agents effectively because they have deep knowledge of what good looks like. But how do juniors acquire that knowledge if they never write code from scratch?
>
> Clarke's take was cautiously optimistic: "We're still going to need junior developers that we grow into senior talent. Maybe that more progressive mindset of somebody who hasn't been doing this for as long is more open to the change that AI native brings. And actually it ends up being an advantage."
>
> The practical implication for factory rollouts: design an entry path for junior engineers that builds expertise through the factory, not around it. Junior engineers can start with spec review - reading agent-produced specs and identifying gaps, ambiguities, and missing edge cases. They can move to context engineering - writing and refining instruction files, debugging why the agent produces incorrect output for specific task types. They can progress to agent debugging - investigating factory failures and determining root causes.
>
> This path builds the same fundamental skills (understanding requirements, recognizing patterns, diagnosing failures) that traditional coding develops, but through a different medium. The junior who spends six months reviewing specs and debugging agent output develops judgment about software quality that is directly applicable in an AI-native workflow.

The hiring data makes this pipeline redesign urgent, not optional. Stack Overflow's analysis found that 70% of hiring managers believe AI can perform the tasks traditionally assigned to interns and junior developers. Entry-level developer hiring has already decreased 25% year over year.[SO-survey] A separate Stack Overflow investigation reported that 37% of employers now prefer "hiring" AI over recent graduates, that entry-level job postings dropped 60% between 2022 and 2024, and that software developer employment for ages 22-25 declined 20% from its 2022 peak.[SO-GenZ] These are not projections. They are observed market shifts that are already reshaping who enters the profession.

The question, then, is not whether juniors will still be hired - fewer will be - but whether those who are hired will actually develop engineering judgment through AI-mediated work. Anthropic's research provides the most rigorous answer available. A randomized controlled trial with 52 junior engineers found that the AI-assisted group scored 17% lower on code comprehension assessments than the control group (50% versus 67%). But the study's most important finding was not the average - it was the variance. Engineers who used AI primarily for code generation (delegation) scored below 40% on comprehension. Engineers who used AI primarily for conceptual inquiry - asking the model to explain patterns, clarify tradeoffs, and reason about design choices - scored above 65%.[Anthropic-skills] The gap between those two usage patterns is larger than the gap between using AI and not using it at all. This transforms the junior pipeline discussion from "will juniors learn?" to a design problem: structure the learning path so junior engineers use AI for inquiry and understanding, not for delegation and avoidance. Spec review, context engineering, and agent debugging - the entry path described above - are exactly the kind of inquiry-oriented tasks that the Anthropic study found preserve and develop comprehension skills.

### Resistance Patterns

Every rollout encounters resistance. The patterns are predictable, and having prepared responses matters more than having perfect arguments.

**"I'm faster without this."** Probably true in week 2. Measure again at week 6, after the engineer has developed context engineering skills and the instruction files have been refined. The initial productivity dip is real - it is the cost of learning a new workflow. If the dip persists past week 6, investigate: is the tooling actually wrong for this engineer's task profile, or is the engineer not engaging with the enablement?

**"I don't trust the output."** Valid concern. The response is not "trust it" - it is "verify it." Start with low-risk features where incorrect output has minimal consequences. Let the engineer review every line. Over time, as they see the validation gates catching errors and the output improving with better context, trust develops organically. Trust cannot be mandated. It must be earned through observed reliability.

**"This is taking my job."** The most emotionally charged concern and the one that deserves the most honest response. The factory does not eliminate the need for engineers. It changes what engineers do. The reframe: you are being upgraded from implementation to architecture, from writing code to designing systems, from producing output to ensuring quality. This is a genuine career upgrade for engineers who embrace it - and it requires acknowledging that the transition is uncomfortable.

**"My codebase is too complex for this."** Every codebase feels special. Most are not. The factory works on codebases with poor documentation, inconsistent patterns, and legacy architecture - it just requires more context engineering to make it work. Start with the simple parts of the codebase (there are always simple parts) and expand as the context matures.

### The Escape Valve

Critical design principle: teams can always drop back to manual development. The factory is a tool, not a mandate. If a team determines that the factory is not effective for their domain, they should be free to stop using it without organizational penalty.

This escape valve serves two purposes. First, it protects teams from being forced into a workflow that genuinely does not fit. Some codebases - highly specialized embedded systems, performance-critical inner loops, novel research code - may not benefit from factory-style development. Second, and more importantly, the escape valve reduces resistance. Engineers who know they can opt out are more willing to opt in. The teams that choose to use the factory are more effective than teams that are forced to use it.

In practice, very few teams exercise the escape valve permanently. Most teams that initially resist find, after 4-6 weeks of genuine engagement, that the factory works for enough of their tasks to justify the investment. The tasks where it does not work become the exceptions that humans handle directly, which is exactly how the factory is supposed to operate.

## Decision Matrix: Starting Your Rollout

| Decision | Recommendation | Key Factor |
|---|---|---|
| When to start | After CI is green, tests exist, branches are short-lived | Foundation maturity |
| First harness | Whatever your engineers are already using | Familiarity reduces friction |
| Team model | Model A initially, transition to Model B | Org size and existing platform function |
| Pilot team size | 1 team, 4-6 engineers | Small enough to iterate, large enough to be representative |
| Pilot duration | 6 weeks (Layers 0-1), then 6 weeks of spec pipeline | Enough time to build literacy and infrastructure |
| First task types | Bug fixes, test additions, documentation updates | Low risk, high volume, clear success criteria |
| Go/no-go criteria | Rework rate, review change requests, engineer confidence | Measurable outcomes, not vibes |
| When to expand | After pilot meets go/no-go criteria | Data, not calendar |
| When to reduce human review | After 50+ consistent successes per task category | Earned trust through observed reliability |
| Stage 4 target | 6-9 months for routine work categories | Realistic, not aspirational |

The factory does not arrive in a single deployment. It grows through layers of capability, each one expanding what agents can do and contracting what humans must do. The organizations that succeed are the ones that treat it as infrastructure, invest in enablement as seriously as they invest in tooling, and measure outcomes rather than activity. Start with the foundation, build the pilot, expand with data, and let the factory earn its autonomy one validated PR at a time.
