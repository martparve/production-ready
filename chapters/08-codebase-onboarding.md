# Chapter 8: Codebase Onboarding: Teaching the Machine Your System

A spec tells the agent what to build. Context tells it how to build it here.

Without codebase context, an agent with a perfect spec will produce code that is functionally correct and structurally alien. It will use the wrong logging library. It will create a new REST endpoint in a codebase that routes everything through GraphQL. It will write tests with Jest in a repo that uses Vitest. It will implement attention from scratch instead of calling `torch.nn.functional.scaled_dot_product_attention`. Every one of these mistakes is locally rational: the agent picked patterns it has seen before. They are globally wrong because the agent did not know where it was working.

In interactive mode, a developer catches these mistakes and corrects them. The correction costs a few minutes and a couple of follow-up prompts. In headless mode - where the factory runs in the cloud, event-triggered, with no developer present - that correction never comes. The agent commits the wrong pattern, the pipeline validates it against tests that pass (because the behavior is correct even if the approach is wrong), and the code lands in the repository. Now every future agent run sees this alien pattern and treats it as precedent. One uncorrected mistake becomes a convention.

This chapter is about building the context package that prevents that drift. Not the spec (covered in Chapters 5-7), but the operating manual for the codebase itself: architecture, conventions, dependency contracts, test patterns, deployment constraints, and the pitfalls that only a developer who has lived in the repo would know.

Anthropic's own engineering team arrived at the same conclusion from the model-provider side. Their guide on effective context engineering opens with a statement that should be pinned above every factory operator's desk: "The single most important skill for working effectively with AI is not prompt engineering - it is context engineering."[Anthropic-context] Intelligence is not the bottleneck. The model is smart enough. What limits agent performance is the quality and structure of the context it receives. This chapter is the engineering discipline that follows from that insight.

## What the Agent Needs to Know

A developer joining a new team picks up context from dozens of sources: onboarding docs, architecture decision records, code review comments, hallway conversations, the tech lead explaining why that one module uses a different pattern. Some of this context is documented. Most of it is not. It lives in people's heads, and the team functions because enough people carry overlapping fragments of it.

Agents have none of this ambient knowledge. They start from zero on every task - or more precisely, they start from their training data, which is a mix of the entire internet's coding patterns and may or may not resemble your codebase. The context package must make explicit everything a competent team member would need to contribute effectively.

This breaks down into seven categories:

**Architecture overview.** How is the system structured? What are the major components and how do they communicate? Is this a monolith, a set of microservices, a modular monolith? Where does business logic live versus infrastructure concerns? An agent that does not know the system topology will create cross-cutting changes that violate module boundaries.

**Conventions.** What does good code look like in this repo? Naming patterns, file organization, error handling style, logging conventions. These are the norms that make code from different contributors feel like it belongs to the same system. An agent that writes `fetchUserData()` in a codebase where every function uses `getUserData()` creates cognitive friction for every human reviewer.

**Dependency map.** Which libraries does the project use, and for what purposes? If the project uses Pydantic for validation, the agent should not roll its own validator. If the project pins SQLAlchemy to version 1.4, the agent should not use 2.0 syntax. This includes internal dependencies: which services does this component call, and through what interfaces?

**API contracts.** What are the interfaces between this component and its neighbors? Request/response formats, authentication mechanisms, error codes. An agent working on one service needs to understand the contracts it must honor with adjacent services.

**Test patterns.** How does this project test code? What framework, what style (unit vs. integration vs. end-to-end), what level of mocking is acceptable? Where do test fixtures live? What is the expected coverage convention?

**Deployment constraints.** What environment does this code run in? What are the resource limits? Are there cold-start considerations, database migration requirements, feature flag systems? A headless agent that generates code incompatible with the deployment environment creates work that has to be thrown away.

**Known pitfalls.** The tribal knowledge that prevents teams from repeating past mistakes. Do not use the `any` type in this TypeScript codebase. Do not call the payments API synchronously. The legacy `UserProfile` table has a column named `email` that actually stores usernames in some rows. This category is the hardest to document because it consists of things people know but have never written down.

## The Instruction File Hierarchy

Context needs to be scoped. Organization-wide security policies apply to every repo. Team-specific conventions apply to a team's repos. Repo-level patterns apply to a single codebase. Module-level notes apply to a single directory. Mixing all of these into a single instruction file creates a document too long to be useful and too generic to be precise.

The practical hierarchy has four levels:

**Organization-level context.** Shared across all teams and all repositories. Security policies, compliance requirements, universal coding standards, brand guidelines. These are the non-negotiable rules that every piece of code must follow regardless of where it lives. Voice and tone for documentation, mandated dependency scanning, prohibited patterns. This layer changes infrequently and should be versioned independently of any single repo.

**Team-level context.** Stack-specific conventions and team workflow patterns. A frontend team might specify React component patterns, state management conventions, and accessibility requirements. A platform team might specify infrastructure-as-code patterns, monitoring conventions, and incident response procedures. This layer captures the shared understanding within a team that distinguishes its code from other teams' code.

**Repo-level context.** The `CLAUDE.md`, `.cursorrules`, or `agents.md` file that lives in the repository root. This is the primary instruction file for most agent interactions. It describes the specific architecture, patterns, dependencies, and conventions of this codebase. For most teams, this is where the bulk of the useful context lives.

**Module-level context.** Per-directory instruction files for large repositories. A monorepo with a frontend app, a backend API, and a shared library has different conventions in each directory. The frontend directory might specify component patterns and styling conventions. The backend directory might specify API design patterns and database access conventions. Module-level context prevents the repo-level file from becoming an unmanageable wall of text.

The hierarchy works through inheritance and override. Module-level context inherits from repo-level, which inherits from team-level, which inherits from organization-level. A module can override a team convention if there is a good reason, but the default is to follow the broader scope.

For headless mode, this hierarchy must be machine-resolvable. The factory needs to assemble the complete context package for a given task by merging the relevant layers automatically. This means the context cannot live in a wiki or a Confluence page that requires human navigation. It must be repo-attached (in the repo itself) or registry-attached (in a central registry that the factory can query), versioned alongside the code it describes.

Daniel Jones, a consultant working on AI-native transformations across Nordic enterprises, puts it clearly on the AI Native Dev podcast: "Having things as global as possible and consistent is going to lead to better results. Wikis are often where documentation goes to die. If you want stale and out-of-date information, that's a good place to put it. So probably in the repository would be the main place to do that."[ANDev-045]

## Built-in vs. Added Context

Before adding context, you need to understand what the agent already knows. Every major coding agent ships with substantial built-in context in the form of system prompts and tool descriptions.

Yaniv Aknin, a software engineer at Tessl who has done detailed analysis of the internals of major coding agents, documented the scale of this built-in context on the AI Native Dev podcast. Claude Code ships with approximately 12KB of system prompt plus 41KB of tool descriptions - roughly 53KB of context before a single user instruction is added. Codex has about 10KB of system prompt but only 1.1KB of tool descriptions, relying instead on model fine-tuning for tool behavior. Gemini CLI lands somewhere in the middle with 14KB of system prompt and 11KB of tool descriptions.[ANDev-033]

These are not trivial amounts. The system prompt alone is roughly 12 pages of text that the model reads on every invocation. It includes instructions about process management, test writing, code style, safety constraints, and how to use sub-agents. The tool descriptions tell the model when and how to use each capability: reading files, executing commands, searching code, delegating to sub-agents.

The practical implication is that context you add must work with - not against - the built-in context. Simon Maple[Simon], co-host of the AI Native Dev podcast, frames this as "mechanical sympathy" - the same concept from high-performance computing where understanding what happens under the hood lets you use the system more effectively. If the built-in system prompt already instructs the agent to run tests after making changes, your added context does not need to repeat that instruction. If the built-in prompt tells the agent to prefer small, focused changes, your context should not instruct it to make sweeping refactors in a single pass.

Adding context that contradicts built-in prompts does not just waste tokens. It degrades performance. The model receives conflicting instructions and must resolve the conflict, which introduces unpredictability. In Aknin's analysis, each agent takes a distinct philosophical approach to tool use and planning: Claude Code uses rich tool descriptions and active plan management with harness-level reminders, while Codex uses minimal descriptions and relies on model training.[ANDev-033] Context that assumes one philosophy while running on an agent built around the other will underperform.

This has a corollary that is less obvious but equally important: context that matches default behavior is not just redundant - it is actively wasteful. Analysis of agent execution logs at Tessl revealed a clear pattern: agents ignore instructions that describe things they would do anyway, and instructions that need to override defaults must be phrased with unusual specificity to actually take effect.[ANDev-037] If the agent defaults to using git, telling it to use git wastes tokens. If you need it to use `gh` as the CLI tool instead, you need to say it in a very specific way that counters the agent's intuitive default. The practical rule is: only include context that overrides what the agent would do without it. Everything else is noise that dilutes attention from the instructions that actually matter.

The model-specificity problem compounds this. The same instruction text produces different behaviors across model tiers - Opus may decide it knows better and override an instruction that Haiku follows obediently.[ANDev-040] Context is not write-once-run-anywhere. When switching models or providers, re-evaluate whether your instructions still produce the intended behavior.

The minimum viable action: read your agent's system prompt (many are extractable or documented), understand its built-in behaviors, and write your context as a complement rather than an override. Then test. Run the agent without your context on a representative task, observe what it does by default, and write context only for the behaviors you need to change.

## Third-Party Library Context

One of the most persistent failure modes in agent-generated code is misuse of external dependencies. Agents hallucinate APIs, confuse library versions, and bypass high-level abstractions in favor of implementing functionality from scratch. This is not accidental - LLMs have a structural bias toward re-implementation over reuse.[ANDev-042] The model has seen thousands of implementations of common functionality and will happily write another one rather than call the library that already handles it. You lose upgradeability, introduce new bugs, and duplicate code that the team already solved - all because the agent did not know which library to call or how.

Maria Gorinova[ANDev-032], a member of the AI engineering team at Tessl, led research measuring this problem rigorously. Her team created an evaluation framework that generates coding tasks requiring correct use of specific libraries, then measures "abstraction adherence" - whether the agent uses the library's intended abstractions or reimplements the functionality.

The results are striking. When agents were given curated library context (what Tessl calls "tiles" - structured documentation about a library's API and intended usage patterns), they showed 35% higher abstraction adherence compared to baseline. For libraries released in the last three years, the improvement jumped to 50%. In a deep-dive case study on LangGraph, focusing specifically on features introduced after the model's training cutoff, agents with curated context performed 90% better.[ANDev-032]

> **Case Study: The PyTorch Attention Problem**[ANDev-032]
>
> Gorinova uses a telling example from PyTorch to illustrate why library context matters. PyTorch 2.0 introduced a one-liner implementation of scaled dot-product attention that is heavily optimized and significantly faster than a manual implementation. An agent trained before this version will implement attention from scratch - writing the matrix multiplications, the softmax, the scaling - because that is what exists in its training data. The generated code is functionally correct. It will produce the right outputs. But it is slower, harder to maintain, and misses optimizations that the PyTorch team spent months developing. With library context that describes the `scaled_dot_product_attention` function and when to use it, the agent calls the one-liner instead. The performance difference is substantial, the code is cleaner, and the agent produces output that a human PyTorch developer would recognize as idiomatic.

The version problem is particularly acute. Gorinova's research found that agent baseline performance follows a curve: worst for very old and very new library versions, best for versions from the period most heavily represented in training data.[ANDev-032] Pydantic v1 and v2 have substantially different APIs, and agents routinely confuse them. A React codebase pinned to version 17 will get React 18 patterns if the agent is not told which version to use.

The source code fallback is a tempting alternative: just give the agent the library's source code and let it figure out the API. Gorinova's research tested this scenario and found that while it does improve results, it is significantly slower and more expensive. The agent takes more "turns" (agentic steps) as it reads through source files, searches for relevant functions, and builds understanding from raw code. Curated context - structured documentation that describes the library's API surface, intended usage patterns, and version-specific changes - gets to the same or better results in a fraction of the time.[ANDev-032]

For headless mode, this means the factory needs a mechanism to resolve the correct library context for each task. A manifest of dependencies with pinned versions, mapped to curated documentation, becomes part of the codebase onboarding package.

## The Context-Attention Tradeoff Applied to Onboarding

Chapter 3 introduced the context-attention tradeoff: every piece of context you add genuinely helps the agent with the thing it describes, but simultaneously dilutes the attention the agent pays to everything else in its window. Codebase onboarding is where this tension bites hardest. The previous sections argue that agents need comprehensive context - architecture maps, library versions, coding conventions, module boundaries - to produce code that belongs in your codebase. The research says that loading all of it at once degrades the agent's ability to use any of it well. NoLiMa measured a 15% reasoning drop above 30,000 tokens.[Hsieh-2502] A follow-up from the University of Zurich found degradation between 30,000 and 60,000 tokens for current-generation models.[ANDev-038] Jones found that poorly structured instructions reduce outcome quality by about 20% compared to having no instructions at all.[ANDev-045]

The range of outcomes is dramatic. Tessl's systematic testing of context quality measured the full spectrum: a well-crafted Agent Browser skill took agent success rate from 28% to 71% - a 2.5x improvement from a single piece of focused context. But a meta-skill codifying a respected practitioner's general best practices had a minimally negative effect (-3%), because it over-complicated simple tasks the agent already handled well. Even Anthropic's own canvas design skill scored 27% on content conciseness in evaluation - "extremely verbose with extensive repetition" and "monolithic wall of text with no references to external files for detailed guidance."[ANDev-040] Good context is a force multiplier. Mediocre context is dead weight. Bad context makes the agent worse than having no context at all.

For codebase onboarding, this means you cannot simply concatenate your architecture docs, conventions, and module context into a single prompt and expect good results. The resolution is progressive disclosure applied specifically to codebase context: assemble a different context package for each task, loading only the layers relevant to the work at hand.

> **Case Study: OpenAI's Just-in-Time Context Injection**[ANDev-052]
>
> Ryan LaPopolo, a member of technical staff at OpenAI, described his team's approach on the AI Native Dev podcast. His team has banned IDE usage in favor of fully agent-driven development, and they have converged on a minimal-context philosophy. "Instead of front-loading all the context into AGENTS.md, I want to just-in-time inject how to remediate a linter failure at the time it happens," LaPopolo explains. His team maintains only five or six centralized skills across the entire codebase. Each skill is a focused prompt that gets injected into context only when the agent encounters a specific situation.
>
> The key insight is that everything entering the agent's context is a prompt: skills are prompts, error messages from tests are prompts, review feedback is prompts. LaPopolo's team treats context engineering as the discipline of "figuring out creative ways to inject prompts into context" and "getting them just in time." This approach allows agents to operate over very long time horizons - LaPopolo describes agents running for 6, 12, even 30 hours - because the context stays lean enough for the model to maintain attention.

The tradeoff also has a spatial dimension. Liu et al. demonstrated that LLMs follow a U-shaped performance curve: they reliably use information at the very beginning and the very end of the context window, but degrade sharply for information buried in the middle.[Liu-2307] For codebase onboarding, this has a direct structural implication: the order in which context is assembled matters as much as its content. Put the most critical architectural constraints and conventions at the top. Put the specific module context relevant to the current task at the bottom, closest to the agent's working memory. Let supporting reference material - dependency lists, historical patterns, secondary conventions - fill the middle, where partial loss is least damaging. Naive context assembly that simply concatenates files in alphabetical order is leaving performance on the table.

Four strategies implement progressive disclosure for codebase context:

**Task-scoped context assembly.** Instead of a single onboarding document, maintain modular context pieces that can be composed per-task. The BMAD (Build More Architect Dream) framework[BMAD] takes this approach, organizing specifications and context into composable documents selected based on the current task. A database migration task loads schema context and migration conventions. A frontend task loads component patterns and design tokens. The total available context is large; the loaded context stays focused.

**Sub-agents as context firewalls.** Sean Roberts[ANDev-031] from Netlify advocates shared sub-agents: instead of putting five specializations into a single instruction file, create separate sub-agent definitions for design, copywriting, data migrations, and other domains. The main agent delegates to the specialized sub-agent, which carries only its own focused context. When the sub-agent completes, only its result - not its full context - returns to the main agent. This prevents context accumulation across tasks and gives each sub-agent a fresh attention budget.

**Layered summaries with drill-down.** Load a summary of the codebase context by default - architecture overview, key conventions, module map. When the agent encounters a specific module or pattern, inject the detailed context for that area. The summary consumes a fraction of the token budget while giving the agent enough orientation to know what it does not know and where to look.

**RAG for knowledge retrieval.** For very large codebases, treat the context as a searchable knowledge base rather than a document to be loaded in full. The agent queries for relevant context based on the current task, retrieves only the pertinent sections, and operates with a focused context window. The caveat from Chapter 3 applies: naive similarity search retrieves fragments that are individually relevant but mutually incoherent. Structured retrieval - knowledge graphs, dependency-aware search - produces better results.

## Knowledge Graphs for Large Codebases

For codebases with hundreds of thousands of lines, flat documentation hits its limits. The relationships between components - which services call which, which modules share data models, which configuration changes cascade through the system - are as important as the components themselves.

Sean Roberts highlights knowledge graphs as a solution for this scale. "If you have a really large code base and you're asking it to do things, every time that you try to ask it to do something, it's got to kind of figure it out on its own. And the larger the code base, the longer that takes, the more expensive it is, the more likely it is it's going to miss parts or get confused."[ANDev-031] Tools like Cognition's DeepWiki and Codemaps generate these pre-computed understanding maps, creating a queryable representation of the codebase's structure and relationships.

Michael Hunger, VP of Product Innovation at Neo4j, makes the case for graph-enhanced RAG from the database perspective. In traditional vector-search RAG, you get back text fragments that match the query, but you lose the context of how those fragments relate to each other and to the broader system. In a graph-enhanced approach, the agent can traverse relationships: starting from a function, walking to the services that call it, the data models it touches, the configuration it depends on, and the tests that cover it. "You get a much richer answer back from the database, which you then pass to the LLM for the final answer," Hunger explains.[ANDev-010]

For a code factory operating in headless mode, knowledge graphs serve a specific purpose: they let the factory determine the blast radius of a proposed change. Before an agent starts implementing a feature, the factory can query the graph to understand which components will be affected, what interfaces must be honored, and what tests should be run. This scoping step reduces the chance of the agent making changes that break distant parts of the system.

Building the graph can itself be AI-assisted. Hunger notes that LLMs are effective at extracting entities and relationships from unstructured data: "You can provide them a schema and instructions and the text. And it will actually extract entities and relationships and attributes from the text."[ANDev-010] For codebases that lack structured documentation, an LLM can generate the initial graph from source code analysis, which human engineers then validate and correct.

## Beyond Flat Retrieval: Structured Codebase Representations

Knowledge graphs are one approach to structured understanding. Recent research points to an even broader principle: any representation that captures the structure of a codebase - not just its text - dramatically improves agent comprehension.

Gao et al. developed CodeMap, a system that extracts codebase information, decomposes it into structured layers (architecture, module dependencies, API surfaces, data flows), and visualizes these layers for both human and AI consumption.[Gao-2504] The key finding is that human-AI co-understanding - where the agent works from a structured map rather than raw files - produces measurably better outcomes than either humans or AI working alone from unstructured code. The agent stops treating the codebase as a bag of files and starts reasoning about it as an interconnected system. This is the difference between giving a new hire a stack of printed source files versus giving them an architecture whiteboard session.

The challenge intensifies when agents need to work across files. Phan et al. investigated RAG (retrieval-augmented generation) applied to entire repositories and identified three problems that basic similarity search cannot solve.[Phan] First, long-range dependencies: a function in one file may depend on a type defined three directories away, and vector similarity between the query and that type definition may be low. Second, global consistency: the agent retrieves snippets that are individually correct but mutually contradictory because they come from different branches of an if-else in the architecture. Third, cross-file reasoning: understanding how a change in module A affects module B requires traversing the dependency graph, not just finding similar code. These findings reinforce the case for knowledge graphs and structured context over naive RAG. Dumping relevant-looking code snippets into the context window is not codebase understanding - it is a keyword search wearing a trench coat.

## Simplicity as Force Multiplier

There is a pattern that runs through every successful codebase onboarding story: the simpler the codebase, the better the agent performs. This is not a platitude. It is a measurable effect with a clear mechanism.

David Cramer, co-founder of Sentry, articulates this from eight weeks of agent-only development. He found that agents excel when working with simple, consistent patterns and collapse when facing unusual architectures. "The simpler the sort of technology stack that they're working with, the better it is for humans, the easier for us, the right code, the easier it is going to be for them to debug, to build all this stuff," Cramer says.[ANDev-015] When he used ORPC - a JavaScript API binding layer with an intentionally simple interface - he was able to co-generate entire API migrations including tests, because the patterns were uniform enough for the agent to extrapolate reliably.

But when Cramer built embedded agents inside MCP tools (an MCP tool calling an agent, calling other tools), the agent "gets so lost in words" that no amount of context steering could keep it on track.[ANDev-015] The pattern was too uncommon for the model to match against its training data.

This has a direct implication for codebase onboarding: if your codebase is complex, your context burden is higher. A codebase with three ways to make an API call needs context that explains when to use each one. A codebase with one way needs a single sentence. Teams that invest in simplifying their codebase are simultaneously reducing the amount of context their agents need and increasing the probability that agents will use the remaining patterns correctly.

The agent performance equation is roughly: outcome quality = model capability x context relevance x codebase simplicity. You can improve the first factor by choosing better models. You can improve the second by writing better context. But improving the third - making the codebase itself more regular and predictable - amplifies both of the others.

> **Case Study: ServiceTitan's Context-First Migration**[ANDev-036]
>
> David Stein, Principal AI Engineer at ServiceTitan, led a project to migrate 247 legacy metrics from C#/SQL to DBT/Snowflake using coding agents. The first 20-30 metrics took nearly two months - not because the agent could not write the code, but because the team was tuning the context package. Each iteration revealed gaps: the agent needed standardized tools for context acquisition (CLI commands to inspect database schemas, view example data, confirm destination platform state), it needed a migration-goals.txt that described the target patterns precisely, and it needed the system prompt to explain the validation loop.
>
> Once the context and tooling were right, the remaining 217 metrics were migrated in a few weeks. The estimated human timeline for the same work: multiple quarters. "The agent doesn't need to be that smart," Stein observes. "As long as you have that kind of self-healing loop where you're able to empower the agent to check its work and then try to make corrections." The investment curve is front-loaded: expensive to calibrate, then cheap to execute at scale.

Chad Fowler, former CTO of Wunderlist, pushes simplicity to its logical extreme with what he calls Phoenix Architecture: treat code as a disposable build artifact generated from specifications, not a durable asset requiring onboarding.[ANDev-047] At Wunderlist, constraining every service to fit on one page of an editor with consistent calling conventions meant that 70% of the codebase was replaced with implementations in Clojure, Go, and Rust over three months. When a Haskell service's build system rotted after an acquisition (the team could no longer compile it), someone rewrote it in Go in an afternoon because the component was small enough to understand completely from its interface alone.

The implication for onboarding is radical: if code is cheap enough to replace, you do not need to teach the agent the existing implementation. You need to teach it the system's interfaces, invariants, and constraints - then let it generate fresh implementations that honor those contracts. "Evaluations are the real codebase," Fowler argues.[ANDev-047] What persists across regenerations is not code but the definition of correct behavior. For most teams this is an aspirational architecture, not today's reality. But even partial movement toward smaller, more bounded components with consistent interfaces reduces the onboarding burden proportionally.

Forsgren, Humble, and Kim documented the same principle from the human side in their Accelerate research.[Forsgren-Accelerate] Teams practicing trunk-based development with short-lived branches consistently outperformed teams with long-lived feature branches and complex merge strategies. The mechanism is relevant here: long-lived branches create ambiguity about what "the current state of the code" actually means. When an agent onboards to a codebase with six active feature branches, each containing weeks of divergent changes, its understanding of the system is necessarily incomplete. It cannot know which patterns are current and which are mid-migration. Trunk-based development, with its emphasis on small, frequent integrations, gives the agent a single source of truth. The codebase the agent sees on the main branch is the codebase. There is no second version of reality hiding in a branch that has not been merged yet.

## Legacy Codebase Onboarding

The hardest onboarding challenge is a codebase where the original developers are gone, documentation is absent, and possibly even the source code is lost. This is not hypothetical. Birgitta Boeckeler, a Distinguished Engineer at ThoughtWorks, describes working with a client who lost access to their backend source code after a vendor relationship ended - "apparently not that uncommon," she notes.[ANDev-018]

> **Case Study: Forensic Reverse Engineering at ThoughtWorks**[ANDev-018]
>
> Boeckeler's team developed what amounts to a forensic approach to codebase onboarding. Without source code, they assembled understanding from every available signal. Database triggers captured change data - every insert and update logged to an audit table so they could observe the running application's behavior. An AI agent browsed the web application using a Playwright MCP server, systematically clicking through every path and describing what it observed. After each interaction, the agent queried the audit table: "What changed in the database since I clicked that button?"
>
> The team decompiled the application binary and fed the assembly code to an LLM, which converted it to pseudocode that humans could reason about. Two colleagues "paired with AI to try and reason about the assembly code and come up with hypotheses and theories." They discovered signs of mainframe calls that no one had documented - connections to backend systems that would need to be replicated in any replacement.
>
> The output of this forensic phase was not code but a comprehensive description: a specification of what the application does, reconstructed from observation rather than documentation. This specification then became the input for forward engineering - the basis for building a replacement. Boeckeler emphasizes that this two-phase approach (reverse engineer to description, then forward engineer from description) is standard practice in legacy migrations, but AI dramatically accelerates both phases. What previously required weeks of manual analysis by senior engineers can now be accomplished in days.
>
> Critically, the generated descriptions were validated by running the same prompts multiple times and comparing outputs for consistency. "If we get basically the same result every time, then we were relatively confident that it was okay," Boeckeler explains. This statistical validation, combined with human sanity checks from subject matter experts who remembered the original system, built confidence that the forensic reconstruction was accurate.

For teams onboarding agents to existing (but accessible) legacy codebases, the forensic approach is overkill. But the underlying principle transfers: use the agent itself to help generate the context it needs. Point the agent at the codebase and ask it to document the architecture, identify patterns, map dependencies, and flag inconsistencies. Then have experienced engineers review and correct that generated documentation. This is faster than writing context from scratch and often more comprehensive, because the agent will identify patterns that humans take for granted and therefore forget to document.

## Process-Aware Understanding: Learning from How Code Was Written

The approaches discussed so far treat the codebase as a static artifact: here is the code, here is its structure, here are its conventions. But a codebase is also the product of a process - thousands of commits, build failures, code review discussions, and design decisions that shaped it over time. Google's DIDACT project demonstrated that training models on the process of development, not just the finished code, produces dramatically better codebase understanding.[Google-AI-SWE]

DIDACT trains on edit histories, build error logs, and code review comments - the artifacts that capture how developers actually work, not just what they produce. The insight is that a build error message paired with the commit that fixed it teaches the model something that neither the error nor the fix teaches alone: it teaches the model the causal relationship between symptom and solution in this specific codebase. Three tools built on this approach were deployed to thousands of Google developers, handling tasks from code completion to build repair to review comment resolution.

For factory operators, DIDACT points to a frontier that most codebase onboarding packages ignore entirely. The typical CLAUDE.md describes what conventions to follow. It does not describe why those conventions exist, what mistakes led to their adoption, or what the codebase looked like before them. A process-aware context package would include not just "use Pydantic v2 BaseModel, not v1" but the migration history that explains the breaking changes, the common errors developers hit during the transition, and the patterns that look correct but fail at runtime. This is harder to assemble than static documentation, but it is precisely the kind of context that separates a competent contributor from someone who merely follows the style guide.

## The Context Development Lifecycle

Context that was accurate when written and wrong when read is worse than no context at all. It actively misleads the agent, causing it to follow obsolete patterns with high confidence. Just like software rots, context rots.[ANDev-042] The difference is that rotten software produces visible errors; rotten context produces invisible drift - the agent confidently generates code following patterns the team abandoned months ago.

An empirical study of 401 open-source repositories found that cursor rules files average only 5.68 commits over their entire lifetime.[Jiang-2512] Nearly 29% of content is duplicated. Teams write the initial context with good intentions, then rarely return to maintain it. This is not a character flaw - it is a systems problem. Without feedback mechanisms that surface when context has drifted, maintenance competes with feature work and loses.

The solution is to treat context as a managed artifact with a lifecycle: define, evaluate, distribute, observe - then repeat.[ANDev-042] This is the same DevOps loop applied to a different artifact. Context development is becoming the developer's new job as agents handle more of the software development lifecycle.[ANDev-047]

The freshness problem has three dimensions:

**Drift from code.** The codebase evolves through daily commits. The context file stays static. Over weeks, they diverge. The context says the project uses REST endpoints; someone added a GraphQL layer last month. The context says tests go in `__tests__` directories; the team adopted co-located test files three sprints ago.

**Drift from dependencies.** Library versions change. The context describes the Pydantic v1 API; the project upgraded to v2. The context recommends a specific testing pattern; the test framework released a new version with a simpler API.

**Drift from conventions.** Teams evolve their practices. The context says to use class components; the team adopted functional components. The context recommends a specific state management pattern; the team found a better approach.

Automated freshness checks can catch some of these problems. A CI step that validates context claims against the actual codebase - checking that referenced files exist, that described patterns match what grep finds in the source, that listed dependencies match the lock file - catches the most obvious drift. More sophisticated checks use an LLM to compare the context document against a sample of recent commits and flag potential contradictions.

But detection is only half the problem. Someone has to update the context when it drifts. In interactive mode, this happens organically: a developer notices the agent using an outdated pattern, corrects it, and updates the context file. In headless mode, this feedback loop must be automated or scheduled. A weekly job that compares the context against the current codebase and generates a diff for human review is one approach. Another is to instrument the factory itself: when a headless agent's output is rejected in code review, capture the reason and check whether a context update would have prevented the issue.

Sean Roberts describes a feedback practice he calls "agent therapy" - when an agent goes off the rails, he has it reflect on what went wrong and suggest updates to the context files. "If the agent's really going off the rails here, I have it look back and say, what could we have done better here? And specifically update the context files to make sure that happens."[ANDev-031] This creates a self-improving context loop, though the updates still require human review before being committed.

**The evaluation-first approach.** Rather than writing context based on intuition about what agents need, start with measurement. Extract representative commits or pull requests from the repository's history, turn them into evaluation scenarios, and run agents against them.[ANDev-042] Where agents fail - wrong library usage, violated conventions, broken architectural boundaries - create targeted context to address that specific gap. Where agents succeed without context, leave well enough alone. This inverts the typical approach: instead of writing comprehensive context and hoping agents use it, identify concrete failures and write the minimum context to prevent them.

**The forgetting step.** Richmond Alake, Director of AI Developer Experience at Oracle, argues that the "memory" framing makes something natural that the "context" framing obscures: the need to forget.[ANDev-044] Without active suppression of stale information, retrieval systems surface outdated patterns alongside current ones, creating confusion. Park et al.'s "Generative Agents" research demonstrated weighted decay mechanisms for memory units - a scoring system that reduces the relevance of older, unaccessed information over time.[Stanford-GenAgents] Applied to codebase context, this means scheduling periodic reviews where each context rule is either validated against current practice or removed.

The one-way ratchet is a real risk. Roberts flags what he calls Mobs' Law applied to context: "Laws and regulations, once they're enacted, monotonically just grow, they never contract."[ANDev-031] Context files accumulate rules over time - every mistake generates a new instruction. Without periodic pruning, the context file grows past the saturation ceiling and starts degrading the agent's performance. Evals against the codebase help here: if removing a context rule does not change the agent's output quality (measured by running the same tasks with and without the rule), the rule is safe to remove.

**Observability as the feedback loop.** Detection alone does not close the loop - someone has to notice when context fails in production. Mining agent execution logs for patterns of manual correction, skill non-activation, and repeated failures provides the signal.[ANDev-040] When an agent consistently ignores a context rule or a developer repeatedly overrides agent output in the same way, that is evidence either that the context is poorly written (the agent does not understand it) or that the context contradicts the agent's training (it needs stronger phrasing to override defaults). Either way, the logs tell you where to invest maintenance effort.

## When Is Onboarding Done?

The natural instinct is to declare onboarding complete when the instruction file is written. But writing context is not the same as validating context. A CLAUDE.md exists - does it work? The only honest answer comes from measurement: run agents against representative tasks with and without the context, compare outcomes, and define done as the point where the delta justifies the investment.

Augment Code tested this rigorously with their AuggieBench eval suite, A/B testing tasks with and without AGENTS.md files. The results should alarm anyone who equates comprehensiveness with quality: LLM-generated context files hurt performance in five of eight tested settings. Agents took 2.5-4 additional steps per task, and inference costs rose 20-23%. In one case, an AGENTS.md containing a full service topology caused the agent to load roughly 80,000 tokens of irrelevant context for a two-line configuration change - completeness dropped 25%.[Augment-AgentsMD] The definition of done is not "documented everything." It is "the minimum context that measurably improves outcomes on the tasks that matter."

Five definitions of done coexist. Teams at different maturity levels will find different ones useful:

**Task eval delta.** The minimum viable definition. Run agents on representative scenarios with your context and without it. If the delta is negligible, the context is not helping. If the delta is negative, the context is actively harmful. Tessl's framework formalizes this: generate coding tasks from real library APIs, measure abstraction adherence with and without curated context, compute the improvement.[ANDev-032] A context file that does not produce at least a 20% improvement on its target task class is a candidate for rewriting or removal.

**Human intervention rate.** The operational definition. Track how often humans reject, modify, or override agent output. Stripe's Minions system merges 70% of PRs without any human modification - that number is their production benchmark for context and tooling quality.[Stripe-Minions-1] Anthropic frames the same signal as: "can you fully delegate this task class without the human stepping back in?" When humans stop correcting, your context is working.

**Eval saturation.** The capability ceiling. When your eval suite approaches 100% pass rate, you have saturated the current measurement - the evals are catching regressions but cannot show improvement.[Anthropic-evals] The response is not to declare victory but to add boundary evals that test harder tasks. Saturation means your context handles the current scope. It does not mean your context handles everything.

**Minimality threshold.** The counterintuitive definition. Context is done when adding more makes things worse. A/B test each section: if removing a paragraph or rule does not degrade eval scores, it was dead weight diluting attention from the rules that matter. This is the hardest definition to accept because it feels like deleting work. But the Augment data is unambiguous: more context correlates with worse outcomes past a saturation point.

**Activation coverage.** The instrumentation definition. Context that exists but never activates is indistinguishable from absent context. Review agent logs and compute: how often should this skill or rule have been activated, versus how often was it actually activated?[ANDev-045] Low activation indicates poor naming, poor descriptions, or triggering conditions that do not match real task patterns. Fix the activation mechanism before blaming the content.

One calibration matters more than any single threshold: the pilot-to-production gap. Research on AI program deployments found that programs achieving 80% accuracy in controlled pilots lose 12-19 percentage points on broader launch, because production surfaces task variants that pilots never tested. An eval suite showing 85% pass rate should be expected to deliver 66-73% in production. Teams should set their eval target significantly above their desired production floor - approximately 10-15 points higher to absorb this decay.

Non-determinism compounds the calibration problem. Daniel Jones, a consultant working on AI-native transformations, puts it directly: agentic coding is "a breeding ground for superstition" because a single successful run proves nothing about the next run.[ANDev-045] Without controlled experiments over a population of tasks, teams develop false beliefs about what context helps. "I added that paragraph and the agent started working better" may be coincidence across a sample of one. The fix is straightforward if labor-intensive: same task population, same model, context present versus absent, measured over enough runs to achieve statistical significance. Anthropic recommends pass@k (probability of at least one success in k attempts) as the metric rather than single-shot pass/fail.[Anthropic-evals]

The practical starting point for teams that have not yet built eval infrastructure: extract five recent commits from your repo's history that represent typical work. Run the agent on each with your current context. Score the output manually against three criteria: does it build, does it follow the conventions described in your context, and would a reviewer merge it without modification? That gives you a baseline. After any context change, rerun the same five scenarios and compare. This is crude, but it is infinitely better than the alternative - which is guessing.

## Tooling Landscape and Decision Matrix

The tools for codebase onboarding range from zero-infrastructure approaches to sophisticated platforms. Which to choose depends on the size of the codebase, the number of agents operating on it, and whether you are running in interactive or headless mode.

**Instruction files (CLAUDE.md, .cursorrules, agents.md).** Zero infrastructure. A markdown file in the repo root. Works immediately with any agent that supports it. Best for small to medium codebases with a single team. Limitation: scales poorly beyond a few thousand words, no composition mechanism across repos, no version resolution for library context. Start here.

**Registry-based context (Tessl Registry, Context7, Ref).** Curated library documentation delivered via MCP or CLI. Solves the third-party library problem by providing version-specific, agent-optimized documentation for thousands of open-source packages. Useful when the primary failure mode is library misuse or version confusion. Limitation: covers public libraries well but requires custom work for internal libraries and proprietary systems.

**Knowledge graphs (DeepWiki, Codemaps, Neo4j-based).** Pre-computed structural understanding of the codebase. Best for large codebases (100K+ lines) where the relationships between components are as important as the components themselves. Enables blast-radius analysis and dependency-aware task scoping. Limitation: requires setup and maintenance, graph must be kept in sync with the codebase.

**Skills and progressive disclosure.** Agent-specific mechanisms (Claude Code skills, Cursor rules) that inject context on demand rather than front-loading it. Best when operating near the context saturation ceiling or running long-duration agent sessions. Late 2025 saw rapid convergence: Anthropic published a skills standard, and within a month Cursor, Codex, and Gemini announced support - with Cursor planning to phase out its proprietary rules format entirely.[ANDev-040] The key architectural distinction is between rules (forced into context every time), skills (breadcrumbed - a short description stays in context, full content loaded on demand), and docs (zero context cost at rest, found only when the agent searches). A thousand rules would cripple your agent; a thousand docs are fine as long as the agent can find the right one.[ANDev-040] Limitation: requires careful authoring to ensure activation - the agent must recognize when to load a skill, and poorly written skill descriptions cause missed activations.

The fragmentation problem is real. Teams that use multiple agents (Claude Code for backend, Cursor for frontend) end up copying the same context into `.claude/skills/`, `.cursor/rules/`, and `.github/copilot/` - with no synchronization mechanism. When one copy gets updated, the others drift silently.[ANDev-040] Tools like Vercel's skills.sh solve distribution by copying from a GitHub repo, but provide no update path - once installed, the skill is frozen at the version it was copied at. The registry approach (Tessl, Context7) solves this by treating skills like package dependencies: a manifest file in the repo references versioned skills resolved from a central registry, with install and update commands analogous to npm.[ANDev-040]

**Custom MCP servers.** Purpose-built tools that expose codebase-specific knowledge through the Model Context Protocol. Boeckeler's team created throwaway MCP servers during legacy forensics[ANDev-018]; Cramer built search and documentation tools into Sentry's MCP server[ANDev-015]. Best when the knowledge the agent needs is dynamic (database state, CI results, live documentation) rather than static. Limitation: requires engineering investment to build and maintain.

| Factor | Instruction Files | Registry | Knowledge Graph | Skills | Custom MCP |
|--------|------------------|----------|-----------------|--------|------------|
| Setup cost | Minutes | Hours | Days | Hours | Days |
| Codebase size sweet spot | Small-medium | Any | Large | Medium-large | Any |
| Library context | Manual | Automated | N/A | Manual | Custom |
| Structural understanding | Flat | Flat | Rich | Flat | Custom |
| Headless readiness | Basic | Good | Good | Good | Best |
| Freshness maintenance | Manual | Automated | Semi-automated | Manual | Automated |

For most teams starting out, the right answer is a well-written repo-level instruction file supplemented by registry-based library context. As the codebase grows or the team moves toward headless operation, add knowledge graphs for structural understanding and custom MCP servers for dynamic context. Skills and progressive disclosure become important when context volume starts hitting the saturation ceiling.

## Practical Onboarding Checklist

For teams building their first codebase onboarding package, work through these items in order. Each builds on the previous.

1. **Establish a baseline first.** Before writing any context, run the agent on a representative task from your repo's recent history with no instruction file at all. Record what it gets right and what it gets wrong. This baseline tells you what the agent already knows from training and what context actually needs to add. Writing context for things the agent handles correctly by default wastes tokens and attention.

2. **Read your agent's built-in context.** Understand the system prompt and tool descriptions. Note behaviors the agent already has so you do not duplicate or contradict them.

3. **Write the repo-level instruction file.** Start with architecture overview, key conventions, and the three most common mistakes the baseline run revealed. Keep it under 2,000 words. You can always expand later; you cannot easily contract.

4. **Document dependency versions and intended usage.** For each major dependency, note the pinned version and any patterns specific to how your project uses it. Connect to registry-based context if available.

5. **Add module-level context for distinct areas.** If your repo has clearly separated concerns (frontend/backend, different services in a monorepo), add per-directory context files.

6. **Set up evaluation scenarios.** Extract 5-10 representative commits from your repo's history and turn them into repeatable eval scenarios. Run these after every context change to confirm the change actually improved outcomes - or at minimum did not regress them.[ANDev-042]

7. **Set up a freshness check.** At minimum, add a CI step that flags when the instruction file has not been updated in 30 days. Better: validate specific claims against the codebase.

8. **Test on a different model.** If your team uses multiple models or might switch providers, run the same eval scenarios on at least one alternative model. Context that works perfectly on Claude may behave differently on Gemini or GPT. Catch model-specificity early.

9. **Prune ruthlessly.** After a month of accumulating context rules, remove any that the agent follows correctly without the rule. Test this with evals, not intuition. If removing a rule does not change the eval score, the rule was dead weight.

## The Destination

The endgame is a codebase that an agent can operate on autonomously with the same judgment a senior engineer would bring. Not the same creativity or insight - those remain human contributions channeled through specs and architecture decisions. But the same practical knowledge of how things work here, what patterns to follow, which libraries to use, and which pitfalls to avoid.

We are not there yet. The saturation ceiling limits how much context an agent can effectively use. Activation mechanisms for skills and progressive disclosure are unreliable. Knowledge graphs require manual maintenance. Library context covers thousands of public packages but not internal frameworks. Every team that has pushed hard on headless operation reports the same finding: the context package requires continuous investment, just like the codebase it describes.

Goldratt's Theory of Constraints offers a useful corrective here.[Goldratt] Optimizing one part of a system does not improve overall throughput unless that part is the actual bottleneck. A team that invests weeks perfecting its CLAUDE.md while the underlying codebase has tangled dependencies, missing test coverage, and three competing patterns for the same operation is optimizing the wrong constraint. The agent's context package can only be as good as the codebase it describes. If the codebase is a mess, the most accurate context file is one that says "this is a mess" - and the right investment is in the codebase itself, not in better documentation of the mess.

But the direction is clear. Every improvement in model context handling - longer effective windows, better instruction following, more reliable tool activation - reduces the gap between what the agent needs and what we can practically deliver. The teams that build the context infrastructure now will be the ones ready to exploit those improvements when they arrive. The teams that wait will find themselves writing the same instruction files in a year, just with more urgency and less time.

One final distinction that this chapter has deliberately sidestepped until now: context is informational, not enforcement. A context file that says "never modify the payments table directly" informs the agent of a constraint, but it does not enforce it. Research and production incidents have shown that agents can see an instruction, appear to understand it, and still violate it - through attention decay over long sessions, through positional bias that buries the instruction in the middle of the window, or through the model deciding it knows better. Safety-critical constraints need mechanical enforcement: sandboxes that prevent filesystem access, database permissions that block writes to production tables, pre-commit hooks that reject prohibited patterns. The context package is the informational layer that guides the agent toward correct behavior. The enforcement layer (covered in Chapters 9 and 15) is what prevents catastrophic behavior when guidance fails.

The context package is not documentation. Documentation is written for humans who can fill in gaps with common sense and ask clarifying questions. The context package is an operating manual for a machine that will follow instructions literally, fill gaps with plausible hallucinations, and never ask for help. Write it with that reader in mind.

---
