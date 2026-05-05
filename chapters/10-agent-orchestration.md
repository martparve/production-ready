# Chapter 10: Agent Orchestration: Running the Machine

The sandbox is ready, the spec is approved, the branch is provisioned. This chapter is about the machine that turns that approved spec into a working pull request without a developer sitting at the controls. Orchestration is the decision layer: which agent runs, in what order, with what context, using what execution pattern, and what happens when it fails. Get this right and the factory hums along producing merge requests overnight. Get it wrong and you have a very expensive token bill and a repository full of half-finished branches.

Orchestration in headless mode is fully autonomous. An approved spec enters the pipeline, triggers an agent run, and the orchestrator manages every downstream decision: decomposing the work, dispatching agents, feeding back build results, detecting when an agent is stuck, and escalating when recovery is impossible. No developer is involved until the pull request appears for review.

## Single Agent vs. Multi-Agent Architectures

The simplest orchestration pattern is no orchestration at all: one agent, one spec, one run. The agent receives the full spec, writes all the code, runs the build, executes the tests, and opens a merge request. This is how most teams start, and it works better than most people expect.

Single-agent execution has real advantages. There is no coordination overhead. The agent holds the full context of the spec in its window. There are no handoff points where information can be lost. Debugging is straightforward because there is one conversation to inspect. For specs that describe a contained feature touching a handful of files, a single agent with a capable model (Claude Opus 4 or equivalent) will outperform a multi-agent setup because the coordination cost of multi-agent systems is never zero.

The limitation is context window pressure. A spec that requires understanding three services, modifying database migrations, updating API contracts, writing frontend components, and adding integration tests can overwhelm even a large context window. As Jonathan Schneider of Moderne puts it: there is an "inverse relationship between context window and the attention mechanism that's fundamental to LLMs."[ANDev-012] Throw too much at the model and it loses focus, producing code that satisfies the last requirement it read while forgetting the first three. This is not a theoretical concern. It shows up in practice as agents that implement the happy path correctly but miss error handling, or that write the backend endpoint but forget to wire up the frontend component that calls it.

Multi-agent architectures address this by splitting work across multiple context windows. A 2024 survey of emerging agent architectures by Masterman et al. catalogues the design space systematically, identifying single-agent reasoning loops, multi-agent collaboration topologies, and hybrid patterns that combine both.[Masterman-2404] Two primary patterns dominate in practice.

**Supervisor-worker decomposition.** A supervisor agent reads the spec and breaks it into subtasks. Each subtask is dispatched to a worker agent with its own fresh context window. The supervisor collects results, checks for consistency, and handles integration. This is the pattern that BMAD[BMAD] and similar spec-driven frameworks use when they generate a task list from requirements and design documents. Cian Clarke of NearForm describes BMAD's approach: the framework shards lengthy documents like PRDs and architecture specs so that only subsets are included in the context window when interacting with the model.[ANDev-034] The supervisor holds the big picture; workers focus on individual stories.

**Role-based specialization.** Instead of splitting by task, you split by role. One agent writes implementation code. Another writes tests. A third does code review. Each agent has a narrow job and a context window loaded with the relevant subset of project knowledge: the test agent gets the testing conventions and the spec's acceptance criteria; the code agent gets the architecture document and the API contracts; the review agent gets the style guide and the linter configuration. Guo et al.'s survey of LLM-based multi-agent systems documents how role specialization, structured communication protocols, and coordination mechanisms improve task completion compared to monolithic single-agent approaches.[Guo-2402]

In practice, most factories blend these patterns. A supervisor decomposes the spec into tasks, and within each task, specialized sub-agents handle distinct phases of the work (implement, test, review). The key design decision is granularity: how small should each unit of work be? Too coarse and you lose the benefits of decomposition. Too fine and you spend more tokens on coordination than on actual code generation.

## Routing Work to the Right Engine

Not every change should go through an LLM - getting this wrong wastes tokens on work that a deterministic tool could handle faster and more reliably.

Jonathan Schneider's experience at Moderne with OpenRewrite[OpenRewrite] illustrates the principle. OpenRewrite is a deterministic refactoring engine: you define a recipe (a program that makes a specific code change), and it applies that recipe identically across thousands of repositories. For something like migrating Spring Boot 3 to 4, there are nearly 3,400 recipes in the catalog.[ANDev-012] Each one produces the same output every time. No hallucinations. No attention drift. No probabilistic variation.

> **Case Study: Deterministic Recipes for Cross-Cutting Changes**[ANDev-012]
>
> Jonathan Schneider (Moderne/OpenRewrite, Ep 012) draws a clear line between what LLMs should and should not do at scale. When a banking executive described needing to migrate applications from file-based logging to stdout for container deployment, Schneider transcribed the requirement into a paragraph and had Claude Code plan and write the OpenRewrite recipes. Within 20 minutes, the first six functional recipes were ready. They deployed those recipes to the bank's tenant and ran them across nearly 10,000 repositories.
>
> The critical insight: the LLM wrote the recipes, but a deterministic engine executed them. "If you need to apply the same change across thousands or tens of thousands of repositories, you really don't want to scale the human review of those changes to the number of changes that are being made," Schneider explains. "What you really want is the actor to be deterministic." The LLM is valuable for authoring the recipe because the cost of writing new custom recipes "is approaching zero." But the LLM should not be the actor that stamps out the change ten thousand times, because probabilistic systems produce probabilistic variations.

The routing decision for your orchestrator follows a simple heuristic. Structural changes - dependency upgrades, API migrations, framework version bumps, cross-cutting refactors that follow a known pattern - route to deterministic tools. Behavioral changes - new features, bug fixes that require understanding intent, anything where the "what" is novel - route to LLMs. When in doubt, ask: would I want this change to be exactly the same in every file it touches, or does each instance require judgment? Sameness means deterministic. Judgment means LLM.

A well-designed orchestrator maintains a registry of available engines (LLM agents, OpenRewrite recipes, code generators, linters, formatters) and routes each task to the appropriate one based on the task type encoded in the spec. This routing logic does not need to be sophisticated. A simple decision tree based on task labels works for most factories.

## Task Decomposition

The orchestrator's first job after receiving an approved spec is to break it into implementable chunks. Decompose too aggressively and you create a coordination nightmare where every chunk depends on three others; too conservatively and each chunk is too large for a single agent to handle cleanly.

BMAD's approach to this problem, as Cian Clarke describes it, is document sharding: the framework splits requirements by epic and architecture documents by component (frontend, backend), then feeds only the relevant shards into each agent's context window.[ANDev-034] This keeps each agent focused on a manageable subset of the problem while preserving the broader context through the spec hierarchy.

The practical decomposition for most features follows a natural layering:

1. **Data model changes.** Database migrations, schema updates, model definitions. These come first because everything else depends on them.
2. **API/service layer.** Endpoints, service methods, business logic. Depends on the data model being in place.
3. **Frontend components.** UI elements that consume the API. Depends on the API contract being defined.
4. **Integration and tests.** End-to-end validation that the layers work together.

Each layer can be a separate agent task with its own context window. The orchestrator sequences them, passing the output of each layer as context to the next. This is where the task list from the spec formalization phase (Chapter 6) pays off: a well-structured task list maps directly to agent dispatch instructions.

The decomposition should produce tasks that are as atomic as possible. Wes Rice of ThoughtWorks, describing his team's RIPER-5 framework, emphasizes keeping tasks discrete enough to be individual commits: "They're not leaking across different tasks. There are a couple of reasons for that. They do have that atomicity. We might split tasks up - you might do one, I might do another. We might parallelize some of the work."[ANDev-036]

## Agent Execution Patterns

Once tasks are decomposed, the orchestrator must decide how each task is executed. Anthropic's "Building Effective Agents" guide identifies five workflow patterns that map well to factory orchestration: prompt chaining, routing, parallelization, orchestrator-workers, and evaluator-optimizer.[Anthropic-agents] Their core advice - start with the simplest pattern that works and add complexity only when measurement proves it necessary - applies directly to factory design. There are four dominant execution patterns in practice, each with distinct tradeoffs.

**Implement-then-test.** The agent writes the implementation first, then generates tests. This is how most developers work and how most agents default to behaving. The risk is well-known: tests written after implementation tend to test what the code does rather than what the spec says it should do. David Cramer of Sentry reports finding tests that "it was not testing what I wanted it to test at all"[ANDev-015] because the agent had generated tests that confirmed its own implementation rather than validating the spec's requirements.

**TDD-first.** Generate tests from the spec's acceptance criteria, then implement code until the tests pass. This sounds ideal on paper but has friction in practice. The Kiro[Kiro] team at AWS tried making every spec go through a TDD flow as the default. Nikhil Swaminathan, Kiro's product lead, describes the outcome: "From our early tests, we found that that generally worked pretty well. But then when actually putting that in front of users and customers, it was not typically how they were working. TDD is great. People follow it, but a lot of users, a lot of customers were just not doing that."[ANDev-016] The lesson: forced TDD as a default creates friction. Offered TDD as a steering option works better. In Kiro, teams can add a TDD steering file that augments the workflow for their specific project.

**RIPER-5.** Wes Rice's team at ThoughtWorks uses a structured five-phase execution model: Research, Innovate, Plan, Execute, Review. The critical innovation is phase discipline: in Research mode, the agent asks questions and analyzes the codebase but does not write code; in Plan mode, it breaks down tasks but does not execute them; in Execute mode, it follows the plan without replanning. "What you cannot do in each of the stages" matters as much as what you can do, Rice explains.[ANDev-036] This prevents the common failure mode where an agent rushes from reading the spec to writing code without understanding the codebase or considering implementation alternatives.

> **Case Study: RIPER-5 in Practice at ThoughtWorks**[ANDev-036]
>
> Wes Rice (ThoughtWorks, Ep 036) describes deploying RIPER-5 on a project building a knowledge graph for a US state agency. The team had 10 developers, limited domain knowledge, and a traditional client. Rather than letting each developer interact with LLMs ad hoc, Rice standardized the workflow: every spec goes through Research (understand the code and requirements), Innovate (explore implementation options), Plan (break into atomic tasks), Execute (write code following the plan), and Review (verify the output matches the spec).
>
> The Review phase acts as drift detection. "What it does is it looks at the plan, looks at the code that was created, and shows you drift," Rice explains. "Did it do what you asked it to do?" The developer decides whether the drift is acceptable or needs remediation. Notably, some drift is desirable: "The reason why LLMs are so powerful is because they're non-deterministic. Sometimes it will give you something that you're like, oh, I like that." When drift is accepted, the team updates the spec to reflect reality, keeping spec and code in sync.

**Parallel implementation.** For specs with independent subtasks, the orchestrator dispatches multiple agents simultaneously. Two agents writing code for different modules on separate branches, each unaware of the other. This maximizes throughput but requires the conflict management strategies described in Chapter 9. Parallel execution works best when module boundaries are clean and task decomposition has minimized cross-module dependencies.

## Deterministic Test Compilation

A radical alternative to having the LLM write tests: compile them deterministically from the spec and never let the LLM touch them.

Baruch Sadogursky[ANDev-009] describes this as the "intent integrity chain." The core argument: LLMs are non-deterministic by nature. You cannot trust them to faithfully translate spec requirements into tests because they will introduce subtle variations, hallucinate edge cases, or miss critical assertions. Since you are also not going to manually review every test (because nobody does), the gap between intent and validation becomes invisible.

The solution is to use a structured spec format (Gherkin, EARS syntax, or a purpose-built spec language) and compile it into tests with a deterministic algorithm. The same spec produces the same tests every time. No model involved. The tests become inviolable guardrails. Then you let the LLM write implementation code and iterate until those tests pass.

> **Case Study: Never Trust a Monkey to Write Shakespeare**[ANDev-009]
>
> Baruch Sadogursky (Ep 009) lays out the chain: prompt to spec (reviewed by humans and LLM-as-judge), spec to tests (compiled deterministically via Cucumber/Gherkin), tests to code (LLM iterates until tests pass). "We don't need a monkey," he says of the spec-to-test step. "We take an algorithm and compile the specs into tests deterministically, every time. If you run it 10 times you'll get the same thing 10 times." The tests must be protected from the LLM: "Make the files read only, put them in a Docker container - do whatever to protect the tests. And then let the monkeys loose."
>
> The practical limitation is that Gherkin-style behavioral specs cannot express everything. Security constraints, performance requirements, and non-functional concerns are awkward to encode in given-when-then format. Sadogursky acknowledges this: "There are concepts that are impossible to describe in given-when-then. Especially stuff like other non-functional requirements like security." The intent integrity chain works best as a partial coverage strategy rather than total specification.

For factory orchestration, the implication is clear: where your spec includes formal acceptance criteria in a compilable format, generate deterministic tests and make them immutable. Where the spec describes behavior that cannot be formalized, let the agent write tests but flag them for human review. The orchestrator should know the difference and route accordingly.

## Agent Memory During Execution

A single agent task might run for minutes. A complex feature decomposed into sequential subtasks might run for hours. The longest agent runs reported in practice stretch far beyond that: Ryan LaPopolo of OpenAI describes Codex runs lasting "6, 12, 30 hours," with a laptop "buckled into the backseat of my car, burning tokens."[ANDev-052]

At these timescales, memory management becomes an orchestration concern. The agent must retain relevant context across a long execution while discarding noise. Richmond Alake[ANDev-044], Director of AI Developer Experience at Oracle, breaks agent memory into three categories drawn from neuroscience.

**Entity memory** stores facts about the project: what the codebase does, what services it talks to, what the team's conventions are. This is the equivalent of a developer's institutional knowledge. In factory orchestration, entity memory is loaded from the codebase onboarding artifacts (Chapter 8) and the spec's architecture documentation.

**Procedural memory** stores how to do things: build commands, testing procedures, deployment steps, linting configurations. This maps directly to the skills and SOPs that Alake describes: "Skills are SOPs for agents. It's just a way of telling an agent, there is a task and I'm going to give an arbitrary name to the task. Then I'm going to describe the task in a certain length. Then I'm going to give you step by step instructions."[ANDev-044] In the factory, procedural memory is codified as skills files that are injected into the agent's context just-in-time.

**Episodic memory** stores what has happened during this run: which files were modified, which tests failed, what the error messages said, what approaches were tried and abandoned. This is the memory that degrades most during long runs as the context window fills up and older interactions get compacted. The orchestrator can help by checkpointing episodic memory at task boundaries: after each subtask completes, summarize what was accomplished and inject that summary into the next subtask's context rather than carrying the full conversation history forward.

LaPopolo's approach to this at OpenAI is aggressive: minimize upfront context, inject knowledge just-in-time, and let the agent cook over long horizons. "Instead of front-loading all the context into AGENTS.md, I want to just-in-time inject how to remediate a linter failure at the time it happens," he explains. "This allows us to have much wider periods of black box behavior where the agent is reasoning and cooking and writing code and resolving its own failures."[ANDev-052]

## The Feedback Loop

The core loop of agent execution is: write code, run the build, run the tests, read the output, adjust. The orchestrator's job is to manage this loop, detecting when the agent is making progress and when it is stuck.

A healthy feedback loop looks like a converging spiral. The agent writes code. The build fails with three errors. The agent fixes two of them. The build fails with one error. The agent fixes the last one. Tests pass. Done. Each iteration brings the agent closer to a working solution. David Stein of ServiceTitan describes building exactly this loop for a legacy reporting migration: "As long as you have that kind of self-healing loop where you're able to empower the agent to check its work and then try to make corrections if it didn't pass validation, that's the key."[ANDev-036] His team migrated 247 metrics from a legacy C# ORM stack to a data lake architecture. The first 20-30 metrics took one to two months as they tuned the agent's context and validation tools. Once the flywheel was running, the remaining metrics took just a few weeks. Work that would have taken quarters of engineer time was compressed into weeks.

An unhealthy feedback loop looks like oscillation. The agent fixes error A but introduces error B. It fixes error B but reintroduces error A. It tries a different approach but now there are errors C and D. Token usage climbs while test pass rate stays flat. Stein encountered this too: agents would get stuck when they lacked sufficient test data to confirm their rewrites. "Which is a similar problem that a human engineer could have," he notes.[ANDev-036] The fix was improving the validation tooling, not improving the agent.

David Cramer of Sentry quantifies the problem from his eight-week experiment of agent-only development: "Sub 10% of the time was I able to get like a one-shot fix in, without like serious refinement. And even sub 10% where like one or two prompts got it correct. It was usually like 20 prompts to get something even remotely good." His insight about when agents struggle is not about task size: "It's not about the size of the task. It's about the complexity in the task based on the commonality of the task."[ANDev-015] If the agent is doing something that matches common patterns in its training data, it works well. If the task requires novel combinations, it flounders. Cramer calls this the complexity cliff: the agent does not degrade gracefully. It works well up to some threshold of novelty, then falls off abruptly into confused loops.

The quality of the feedback matters as much as its existence. A raw compiler error dump is less useful than a curated error message with the relevant source context attached. A test failure that says "assertion failed" is less useful than one that says "expected endpoint /api/users to return 200, got 404, because the route was not registered in server.ts." The orchestrator should transform build output into agent-digestible prompts, stripping noise and highlighting the information the agent needs to make progress.

The orchestrator needs diminishing returns detection: a mechanism that notices when an agent is in an unproductive loop and intervenes. Simple heuristics work surprisingly well:

- **Iteration count ceiling.** If the agent has attempted more than N build-fix cycles (a reasonable default is 5-8), pause and escalate.
- **Test pass rate plateau.** If the number of passing tests has not increased in the last three iterations, the agent is likely stuck.
- **Token budget exhaustion.** Set a token budget per task. When 80% of the budget is consumed, warn. When 100% is consumed, stop.
- **Repeated error patterns.** If the same error message appears in three consecutive build outputs, the agent is cycling.

When any of these triggers fire, the orchestrator has three options: retry with a different model (sometimes switching from Sonnet to Opus or vice versa unlocks progress), retry with additional context (inject a hint, an example, or a relevant code snippet), or escalate to a human. The headless factory should never spin indefinitely burning tokens on an unsolvable problem.

## Handling Failures

Beyond stuck loops, agents fail in several characteristic ways that the orchestrator must handle.

**Hallucinated APIs.** The agent calls a function or imports a module that does not exist. This is especially common when the agent's training data includes an older version of a library. The fix is to ensure the agent has access to current API documentation, either through documentation MCP servers or by including relevant type definitions in its context. The orchestrator should detect import errors in build output and inject the correct API surface before the next retry.

**Architectural drift.** The agent implements a feature in a way that works but violates the project's architectural conventions. It uses a different state management pattern, introduces a new dependency where an existing one would suffice, or puts business logic in the wrong layer. This is hard to detect automatically because the code compiles and tests pass. Linters and architecture-specific rules (ArchUnit for Java, ESLint rules for JavaScript import boundaries) catch some of these. For the rest, the review phase is the last line of defense.

**The refactoring gap.** Agents do not spontaneously refactor. Maor Shlomo, founder of Base44, observes the limitation directly: "AI is not really good at stuff and saying, oh, you know what, there's actually common concepts here that I could combine to this infrastructure or package that I can later use in other features. And, oh, I'm writing the same code again and again. Let's stop. And before I do the task that you gave me, let's refactor the code."[ANDev-017] The agent will dutifully implement every task as instructed, duplicating code and creating increasingly tangled dependencies along the way. Base44 addresses this with behind-the-scenes refactoring triggers: when a code file exceeds a length threshold, the system tells the LLM to refactor before proceeding. A factory orchestrator should do the same, running periodic code quality checks between tasks and injecting refactoring tasks into the queue when metrics cross a threshold.

**Context window overflow.** For long-running tasks, the agent's context window fills up with conversation history, and earlier instructions get pushed out. The agent "forgets" constraints that were stated at the beginning. This manifests as the agent reverting to default behaviors: using `any` types in TypeScript despite explicit instructions not to (Cramer's observation), ignoring project-specific conventions, or abandoning the spec's approach in favor of whatever is most common in training data. Cramer describes the futility of trying to control this through prompting alone: "I have it in the Claude code at the top of it in the prompts, like critical, don't use this. And if you send that in every prompt, it's probably okay, but you don't, that's not how you work."[ANDev-015] The mitigation is context compaction at regular intervals, preserving critical instructions (the spec, the architecture constraints, the do-not-do list) while summarizing the conversation history. Some teams use a "golden rules" file that gets re-injected after every compaction, ensuring that non-negotiable constraints are never pushed out of the context window regardless of how long the conversation runs.

## The Decision Matrix

Choosing the right orchestration pattern depends on the nature of the work. Here is a practical decision matrix.

| Factor | Single Agent | Supervisor-Worker | Role-Specialized |
|--------|-------------|-------------------|-----------------|
| Spec scope | Single feature, <10 files | Multi-component feature | Full-stack feature with distinct layers |
| Context window pressure | Low-medium | Medium-high (workers get focused context) | Medium (each role gets relevant subset) |
| Coordination overhead | None | Medium (supervisor manages handoffs) | High (roles must agree on interfaces) |
| Failure isolation | Poor (one failure blocks all) | Good (worker failure does not block other workers) | Good (role failure is contained) |
| Best for | Bug fixes, small features, contained changes | Epics with decomposable subtasks | Projects with clear layer boundaries |

For most factories in 2026, the practical recommendation is to start with single-agent execution and add multi-agent patterns only when you hit context window limits. A single capable model with good context engineering (well-structured specs, relevant code in context, just-in-time skill injection) will handle a surprising range of tasks. Multi-agent orchestration is powerful but introduces failure modes that do not exist in single-agent runs: agents contradicting each other, integration failures at handoff points, and the classic distributed systems problem of partial failure.

## Tooling for Orchestration

The orchestrator is a piece of software that needs to be built or assembled. As of mid-2026, there is no dominant open-source orchestration framework for AI code factories. Teams are building custom orchestrators from general-purpose components. The three most widely used agent frameworks each reflect a different philosophy: CrewAI organizes agents into role-based crews with delegated tasks; LangGraph models workflows as directed graphs with state checkpointing; and AutoGen (now merging with Semantic Kernel into Microsoft's unified Agent Framework) uses event-driven group chats for multi-agent coordination.[DataCamp-agents] None of these were designed specifically for code factories, but their primitives - task routing, agent lifecycle, state persistence - map onto factory orchestration needs.

The minimum viable orchestrator needs:

- **A task queue.** Something that holds approved specs and dispatches them to agents. This can be as simple as a GitHub Actions workflow triggered by a label, or as sophisticated as a dedicated job scheduler.
- **Agent runtime management.** The ability to spin up agent processes, connect them to sandboxes, and tear them down when done. Container orchestration (Kubernetes, ECS) handles the infrastructure; the orchestrator adds the agent-specific lifecycle management.
- **Context assembly.** The logic that determines which documents, code snippets, skills, and instructions go into each agent's context window. This is where most of the intelligence lives.
- **Feedback routing.** Capturing build output, test results, and linter warnings and feeding them back to the agent in a useful format.
- **Escalation logic.** The diminishing returns detection and intervention mechanisms described above.
- **Observability.** Logging, tracing, and metrics for every agent run. You cannot improve what you cannot measure. Track token usage per task, build-fix iteration counts, time to merge request, and human intervention rate. These metrics tell you where the factory is efficient and where it is burning tokens unproductively.

Stripe's internal system, as described by engineer Steve Kuliski, illustrates what a mature orchestrator looks like: "I can click a single emoji in Slack. It'll spin up an entire replica of Stripe and run an agent loop off of that prompt. And then it will use all of our internal docs and tools and CI to try to resolve that prompt." They produce 1,300 pull requests per week without human assistance beyond code review. The key to their success: pattern matching on the type of change to inject appropriate context. "Maybe 80% of coding at Stripe follows some blessed paths. And because we can pattern match to one of those pathways, we can make sure we're introducing the appropriate context."[ANDev-052]

That is the orchestrator's ultimate job. Not running agents - that is just process management. The real work is knowing what each agent needs to succeed and making sure it has exactly that: the right context, the right tools, the right constraints, and the right escape hatch when things go wrong.

---
