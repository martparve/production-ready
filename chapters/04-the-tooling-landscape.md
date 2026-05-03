# Chapter 4: The Tooling Landscape

Nobody builds an AI code factory from scratch. Not because they cannot - Yaniv Aknin[ANDev-033] at Tessl proved you can get a working coding agent in under 100 lines of Python - but because the engineering required to go from "working demo" to "production-grade factory" is enormous. The tools you choose determine how much of that engineering you do yourself versus inherit from someone else.

Aknin's nano-agent is instructive precisely because it works. A 250-byte system prompt ("you're a coding agent, do well"), an execute-command tool, read-file, write-file, and a simple while loop. Asked to build a to-do app, it produces something functional and decent-looking. On Terminal Bench[TerminalBench], a respected coding benchmark, an agent of similar minimalism - the mini SWE agent from Princeton[SWE-agent] - lands in 15th place, within a competitive cohort of much more sophisticated systems. So if a hundred lines gets you 80% of the way there, what do the other thousands of lines in flagship agents actually buy?

The answer, as we will see throughout this chapter, is reliability, safety, team coordination, and the ability to handle the messy edge cases that benchmarks do not test.

This is the fundamental composition decision every team faces. You understood the pipeline stages in Chapter 2. You know how to think about context engineering from Chapter 3. Now you need to pick the machinery. The question is not "which tool is best" - that framing leads to religious wars and regret. The question is: which combination of tools gives your team the most leverage at the least cost in flexibility?

The landscape breaks into four categories. Most organizations end up assembling pieces from all four.

## Full-Pipeline Platforms

Full-pipeline platforms attempt to cover the entire software development lifecycle with an opinionated, integrated experience. They make strong choices about how each stage works so you do not have to.

**Kiro**[Kiro] is the clearest example of spec-driven platform thinking. Built by AWS, Kiro is a forked VS Code editor that structures development around a three-phase specification workflow: requirements in EARS (Easy Approach to Requirements Syntax)[Mavin-EARS] format, design documents generated from codebase analysis, and decomposed implementation task lists. Nikhil Swaminathan[ANDev-016], the product lead, describes the problem it solves: vibe coding produces software where decisions get lost in chat transcripts, like a Slack thread where context is relevant only at the moment it was typed.

The EARS format is not arbitrary. Richard Threlkeld[ANDev-016], an engineer on the Kiro team, traces it back through temporal logic and first-order logic, giving the system formal reasoning power over requirements. When a user writes "when a customer views a product card, the system shall display a heart icon," that sentence structure gives Kiro hooks for verification, contradiction detection, and test generation that a freeform prompt cannot provide.

Kiro also introduces hooks - automated triggers that watch your repository for events (file create, save, delete) and enforce rules. A team can set up a hook that validates single-responsibility principle compliance every time a new React component is created, or one that updates localization strings every time a new feature lands. Combined with steering files (Kiro's equivalent of CLAUDE.md), hooks, and the spec workflow, you get a system where the platform enforces process without requiring the developer to remember to follow it.

The trade-off is clear. You get a coherent, integrated experience where requirements trace all the way through to implementation tasks. You also get AWS's opinions about how software should be built. If those opinions align with your team's practices, Kiro removes enormous amounts of glue engineering. If they do not, you are fighting the platform.

**Tessl** takes a different approach to the same problem. Rather than building another IDE, Tessl positions itself as an agent enablement platform focused on context engineering. It maintains a framework registry and provides tooling for building, testing, and distributing the context that makes agents effective across an organization. Where Kiro owns the editor experience, Tessl is designed to sit behind whatever agent harness you already use.

**Factory**[Factory] and **Devin**[Devin] represent the autonomous end of the spectrum. These platforms aim to handle tasks end-to-end with minimal human involvement - you describe what you want, the system figures out how to build it. The appeal is obvious: maximum leverage per human hour. The risk is equally obvious: when the autonomous system makes a wrong architectural decision early, the blast radius is larger because there were fewer checkpoints where a human could have intervened.

All full-pipeline platforms share a common trade-off profile. They are faster to adopt because you inherit someone else's engineering decisions. They are harder to customize because those decisions are baked into the product. And they carry vendor lock-in risk - your specs, your context, your workflows become entangled with a specific platform's format and assumptions.

## Agent Harnesses

Agent harnesses occupy the middle of the landscape. They handle the core agentic loop - prompting the model, executing tools, managing conversation history - and leave everything else to you. They are the workbenches of the AI code factory, flexible enough to build almost anything, but requiring engineering effort to connect the pipeline stages.

### Claude Code

Claude Code[Claude] is a terminal-based agent harness with a 12KB system prompt, 17 built-in tools, and approximately 41KB of tool descriptions. It uses CLAUDE.md files for persistent context, supports sub-agents for task decomposition, and provides hooks for pre- and post-execution automation.

The tool descriptions are where Claude Code makes its distinctive bet. Where some harnesses give the model a one-line description of each tool and rely on training to fill the gaps, Claude Code provides verbose, detailed instructions: when to use each tool, what to do in edge cases, examples of good and bad usage. The total text devoted to tool descriptions alone dwarfs the entire system prompt of some competitors.

Claude Code also takes a distinctive approach to planning. Its planning tools are not just tokens the model emits into its own context (though that is part of it) - the agentic harness actively manages the plan as a control flow element, reminding the model of upcoming steps and checking whether it has completed the current one. The plan is not decorative. It is enforced.

The sub-agent architecture is particularly flexible. Claude Code pre-warms caches with different model configurations - a smaller, faster model for code exploration, a more capable model for implementation. This allows the system to route different types of work to appropriately sized models within a single session.

### Codex CLI

Codex CLI[Codex], OpenAI's open-source agent, takes an almost philosophically opposite approach. It ships with just 7 tools and 1.1KB of tool descriptions. It does not even have a dedicated read-file tool - if the agent wants to read a file, it executes a `cat` command.

This minimalism is not a limitation. It reflects a different design philosophy. Codex CLI runs on a model (GPT 5.1-codex at the time of writing) that was specifically fine-tuned and further trained to use these particular tools. The tool knowledge is baked into the model's weights, not encoded in verbose descriptions. The harness is lean because the model already knows what to do.

Codex CLI's planning is simpler too. It has an update-plan tool where the model writes out its intended steps, and those steps get added to the conversation history. But there is no harness-level enforcement - the model can deviate from its own plan freely. The plan is tokens in context, not a control flow mechanism.

The trade-off shows up when you add custom tools. Because Claude Code's models learned to use tools generically through detailed descriptions, they tend to adapt well to unfamiliar MCP servers and custom tooling. Codex CLI's model, trained specifically on its built-in tools, can struggle with novel tools it has never seen during training. Aknin's team at Tessl reports "better success making Sonnet make use of arbitrary new tools than we've had with Codex" in their evaluations.[ANDev-033]

### Goose

Goose[Goose] is the open-source, provider-agnostic option. Originally created by Block (the company behind Square and Cash App), it was donated to the Linux Foundation's Agentic AI Foundation[LF-AAIF] alongside MCP[MCP-spec] and AGENTS.md. It is Apache 2.0 licensed, built on a Rust core, and supports over 15 LLM backends through a full bring-your-own-model architecture.

Goose's extensibility model is MCP-only. Every capability beyond the base agentic loop comes through MCP servers. This is both its greatest strength and its primary constraint. You are never locked to a specific model vendor or a specific set of capabilities - you can wire in whatever tools your organization needs. But the quality of your coding agent is directly bounded by the quality of the model you plug in. A Goose instance running a frontier model performs like a frontier agent. A Goose instance running a smaller, cheaper model performs accordingly.

Goose uses a Recipes system as its equivalent of CLAUDE.md - structured context files that define how the agent should behave for specific types of work. Recipes can encode project-specific conventions, preferred patterns, tool configurations, and behavioral guidelines. The mechanism is familiar to anyone who has written a CLAUDE.md or .cursorrules - the difference is that Goose's Recipes are model-agnostic, so the same behavioral context works regardless of which LLM backend is active.

Its pedigree is notable: Stripe's internal Minions system, which generates roughly 1,300 PRs per week, is forked from Goose.[ANDev-052] That lineage validates the architecture even if the out-of-the-box experience requires more assembly than a commercial harness. The fact that one of the world's most demanding engineering organizations chose Goose as the foundation for their internal agent system says something about the soundness of the underlying design.

### Cursor and Aider

**Cursor**[Cursor] represents the IDE-integrated approach. Rather than running in a terminal, it wraps the agent experience inside a VS Code fork with visual diff review, file-by-file change tracking, and a `.cursorrules` configuration system. The advantage is obvious for developers who want to see every change as it happens and interact with the agent through familiar IDE affordances. The disadvantage is equally obvious: you are tethered to an IDE window, which limits the kinds of automation you can build around the agent.

**Aider**[Aider] is a terminal-based, git-native harness. Every change Aider makes is automatically committed to git, giving you a clean rollback point for every agent action. It is the simplest harness in the landscape - opinionated about git integration, flexible about everything else.

The IDE-versus-terminal choice is not cosmetic. A guest on Ep 035 of the AI Native Dev podcast frames it as a spectrum of interactivity and autonomy.[ANDev-035] IDE-based tools like Cursor simplify onboarding - buttons, visual diffs, inline suggestions - and keep the developer firmly in the loop. Terminal-based tools like Claude Code enable background execution, non-interactive pipelines, and the kind of automation you need when scaling to multiple concurrent agents. The progression many teams follow is telling: start with an IDE copilot to build trust, graduate to an IDE-based agent for more autonomous tasks, then move to a terminal agent when you are ready to hand over full context windows and let the agent run unsupervised. Each step is an increase in autonomy that maps to an increase in trust.

### The Harness Internals Matter

All of these harnesses look roughly similar from the outside: you give them a prompt, they call tools, code appears. But the internal differences have profound effects on how you build context for them.

> **Case Study: Reverse-Engineering the Flagship Agents**[ANDev-033]
>
> Yaniv Aknin, a software engineer at Tessl, reverse-engineered the communication between flagship agents and their underlying models using transparent proxying. The research, presented at Ep 033 of the AI Native Dev podcast, revealed surprising divergence between the industry's leading agents.
>
> Claude Code sends approximately 41KB of tool descriptions alongside its 12KB system prompt. Codex CLI sends roughly 1.1KB of tool descriptions alongside its 10.7KB system prompt. That is a 40x difference in how much guidance the harness provides about tool usage.
>
> The system prompts themselves diverge in emphasis. Claude Code devotes substantial space to process management and sub-agent coordination. Codex CLI has almost nothing about process - its system prompt focuses elsewhere. Gemini CLI, with a 14.7KB system prompt and 12 tools, splits the difference.
>
> Aknin's most actionable finding was about compatibility. When you add external context - your CLAUDE.md, your MCP servers, your custom instructions - that context gets "mixed together" with the built-in system prompt and tool descriptions. If your external context contradicts the built-in context, performance degrades. You need what Simon Maple, Aknin's colleague at Tessl, calls "mechanical sympathy" - understanding what is under the covers, the way a Formula One driver understands the gearbox even though their interface is just the gear stick.
>
> The practical implication: before writing context for any agent harness, read its system prompt. Understand what it already tells the model. Then write context that complements rather than contradicts.

This research also suggests why switching models behind a harness is not as simple as changing a configuration value. Codex CLI's minimal tool descriptions work because its model was trained specifically for those tools. Swapping in a different model means that model receives almost no guidance about how to use the tools - a recipe for degraded performance. Claude Code's verbose descriptions, meanwhile, are designed to work with models that learned tool use more generically. The harness and the model are not independent choices. They are coupled.

## Stage-Specific Tools

Not everything needs to be an agent. Some pipeline stages are better served by tools that do one thing well, deterministically, without the overhead and unpredictability of an LLM in the loop.

**CodeRabbit**[CodeRabbit] and **PR-Agent/Qodo**[Qodo] handle AI-powered code review. They analyze pull requests, flag issues, suggest improvements, and can enforce organizational standards. The value proposition is straightforward: a code review bot that runs on every PR, never gets tired, and applies rules consistently is a force multiplier for human reviewers who can then focus on architectural and design questions rather than style violations and obvious bugs.

**GitHub SpecKit**[SpecKit] focuses on the specification stage - helping teams generate and manage the structured requirements documents that feed downstream agents. It occupies the space between a product manager's rough feature description and the formal spec an agent needs to implement correctly.

**OpenRewrite**[OpenRewrite] deserves special mention because it represents an entirely different philosophy. OpenRewrite performs deterministic code transformations - framework migrations, dependency upgrades, code modernization - using pattern-matching rules rather than LLMs. When you need to upgrade 500 files from Spring Boot 2 to Spring Boot 3, you do not want an LLM making creative decisions about each file. You want a tool that applies the same transformation reliably across every file. OpenRewrite does this.

**Guardrails AI**[Guardrails] provides runtime validation for LLM outputs. Rather than hoping the agent produces valid code, you define structural and semantic constraints and the system validates outputs against them before they ship. This is the safety net that makes autonomous operation possible.

The pattern across stage-specific tools is consistent: they trade flexibility for reliability. An agent harness can theoretically handle any stage of the pipeline. A stage-specific tool handles one stage but handles it with guarantees that a general-purpose agent cannot provide.

This is not a small distinction. When you ask an LLM to review a pull request, you get a probabilistic assessment that may or may not catch the critical issue. When you run OpenRewrite's Spring Boot migration recipe, you get a deterministic transformation that either succeeds or fails cleanly. Both are valuable. They are not interchangeable. The AI code factory needs both probabilistic intelligence for novel problems and deterministic tooling for known patterns.

## Infrastructure You Already Have

The fourth category is easy to overlook because it is already in your stack. Your existing engineering infrastructure does not become irrelevant when you adopt AI-native development. It becomes the foundation everything else plugs into.

**Git and GitHub/GitLab** remain the collaboration backbone. Every agent harness produces git commits. Every code review tool reads pull requests. Every CI pipeline triggers on merge. The version control system is not a tool you choose for your AI code factory - it is the substrate the factory runs on.

**Docker and container runtimes** provide the sandboxed execution environments where agents run safely. When an agent wants to execute code, test changes, or validate builds, it needs an isolated environment where a stray `rm -rf` does not destroy anything important. Cian Clarke at NearForm makes this point explicitly: "if it decides to rm -rf /*, that's okay by me because I have everything in git and it's in a container."[ANDev-034]

**Your existing test suites** become dramatically more important, not less. In a traditional workflow, tests validate human-written code. In an AI-native workflow, tests are the primary mechanism through which agents verify their own work and through which humans build trust in agent output. Clarke frames the trust equation directly: "The more that models are able to actually test their outputs and prove that what they claim is working is in fact truth through a completely separate artifact - the more that we can trust that autonomy."[ANDev-034]

**Your CI/CD pipeline** gains a new role. Beyond its traditional function of building, testing, and deploying code, it becomes the enforcement layer for the AI code factory. Hooks that run on every commit, gates that block merges when quality thresholds are not met, automated rollbacks when production metrics deviate - all of this existed before AI agents, but it matters more now because the volume of changes is higher and the human review bandwidth is lower.

The point is not that you need new infrastructure. The point is that your existing infrastructure needs to be excellent. A team with spotty test coverage, a manual deployment process, and a CI pipeline that takes 45 minutes to run will have a miserable time adopting AI-native development. The factory amplifies whatever quality culture you already have - both the good parts and the bad.

## Interactive Tools vs. Headless Infrastructure

Before discussing composition, there is a more fundamental distinction to make. The four categories above mix two fundamentally different types of tooling: tools designed for a developer at the controls, and infrastructure designed to run without one.

**Interactive tools** - Claude Code, Cursor, Aider, Kiro - assume a human is driving the session. The developer starts the agent, provides guidance, reviews output in real time, and course-corrects when the agent drifts. These tools are the learning phase of factory adoption. They build intuition, help teams develop context engineering skills, and handle the complex or novel work where human judgment at every step still matters.

**Headless infrastructure** - GitHub Copilot Coding Agent, Codex (cloud), Devin, Factory, and custom orchestration systems like Stripe's Minions - assumes no human is present during execution. A trigger fires (issue assigned, webhook, scheduled job), the system provisions a sandbox, runs the full pipeline, and produces a merge request. The human's first interaction is reviewing the output. These systems are the operating phase of factory adoption.

The distinction matters because an organization's tooling strategy should reflect where it is headed, not just where it is today. A team that invests heavily in Cursor workflows and local agent skills is optimizing for interactive mode. That is fine as a starting point, but it creates habits and infrastructure that do not transfer to headless operation. Skills shared through git repos, context files maintained per-developer, review workflows centered on IDE diffs - these are all interactive-era patterns.

The headless factory requires different infrastructure: event-driven triggers, cloud sandbox provisioning, centralized context management (not per-developer files), CI-integrated validation, and PR-based review workflows. The context engineering is more demanding because there is no developer to course-correct mid-session. The context must be comprehensive enough for the agent to work autonomously from start to finish.

Teams that plan for headless from the start - even if they begin with interactive tools - make better infrastructure decisions. They write context that is repo-attached rather than developer-attached. They build validation gates that run in CI rather than locally. They structure specs and reviews around PRs rather than IDE sessions. The interactive tools become training wheels that come off when the team is ready, rather than load-bearing infrastructure that has to be replaced.

## The Composition Spectrum

With that distinction in mind, the four tool categories form a spectrum from fully integrated to fully composed.

At one end, a team adopts a full-pipeline platform like Devin or Factory that handles the entire headless flow out of the box - from task intake to PR output. The composition burden is low, but so is the customization ceiling, and the vendor lock-in is significant.

At the other end, a team builds a custom headless pipeline: GitHub Actions or a custom orchestration layer for event-driven triggering, Codespaces or ephemeral containers for sandboxing, Claude Code or Goose as the agent engine (run headlessly in the cloud, not on a developer's machine), CodeRabbit for automated review, and their existing CI/CD for validation and deployment. Every piece is best-in-class for its role, but someone needs to wire it together.

Most organizations start in the middle: interactive tools for daily work, gradually building headless infrastructure for routine tasks. The factory grows from interactive to headless organically as context quality improves and trust builds.

Each subsequent chapter references these categories and notes what changes when the stage runs headless versus interactive.

## The Model Question: Open vs. Proprietary

Underneath every agent harness sits a model. The choice between proprietary frontier models and open-weight alternatives is not just a technical decision - it touches on cost, security, data privacy, vendor dependency, and organizational sovereignty.

Amanda Brock, CEO of Open UK, warns bluntly about what she calls "open-washing" in AI. When Meta labeled Llama as open source, Brock's organization was the only one that supported the launch - but only as "open innovation," not open source. Llama's license includes an acceptable use policy and a commercialization provision requiring a separate license above a certain user threshold. "If you're a Meta and you're saying Llama is open source when it's not, you're misleading people," Brock says. "Open washing takes away the trust. And if you don't have trust, you will not be successful because you don't have the ecosystem around you."[ANDev-049]

The practical distinction matters for teams choosing their model stack. A truly open model on an OSD-compliant license (Apache, MIT, GPL) gives you the right to use it for any purpose, to modify it, to redistribute it. An "open-weight" model gives you the weights but not necessarily the training data or unrestricted usage rights. A proprietary model gives you API access and nothing else.

> **Case Study: From $7,500 an Hour to $20 a Month**[ANDev-035]
>
> A practitioner described on Ep 035 of the AI Native Dev podcast how agentic cost economics have shifted within a single year. In late 2024, running a 10-agent swarm concurrently on API pricing cost approximately $7,500 per hour. A 36-hour test run was conducted mostly to prove it was possible, but the costs were "prohibitively expensive" - substantially cheaper to hire a person.
>
> Then in April 2025, Anthropic launched Claude Code with unlimited-use subscription plans. The same swarm architectures that had cost thousands of dollars per hour could now run for a flat fee starting at $20 per month.
>
> "We saw this interesting inflection of both capability - suddenly we were able to build things dramatically faster and with a lot more capability at an exponentially lower cost, which is an interesting sort of - you don't generally see that happen all at once."
>
> This cost collapse changed the calculus for model selection. When API pricing dominated, teams optimized aggressively for token efficiency, choosing smaller models where possible and rationing frontier model usage for complex tasks. With subscription plans, the optimization target shifted from cost-per-token to capability-per-task. Teams could afford to use frontier models for everything, making the composition decision about quality rather than budget.

The cost picture for self-hosted open models tells a different story. DeepSeek demonstrated that distillation - training a new model using the outputs of existing open models like Qwen and Llama - could reduce model creation costs from roughly $100M to $5M. Brock describes this as "super impactful" for innovation, and it was only possible because Meta had opened Llama's weights.[ANDev-049] The chain from Llama to DeepSeek to the current generation of small language models running on phones would not exist without open model availability.

For teams building AI code factories, the model decision often comes down to three scenarios.

**Cloud-hosted proprietary models** (Claude, GPT, Gemini) offer the highest capability, the simplest operational footprint, and the most vendor lock-in. Your code and context flow through someone else's infrastructure. For many organizations, this is fine. For regulated industries or teams handling sensitive IP, it may not be.

**Cloud-hosted open models** (running Llama, Qwen, or Mistral on your own cloud infrastructure) give you data control and model flexibility at the cost of operational complexity. You need the infrastructure team to host, scale, and maintain the model serving stack.

**Self-hosted open models** (on-premise deployment) maximize control and minimize external dependency. The cost is in hardware and operational expertise. This is the choice for organizations where data sovereignty is non-negotiable.

Goose's architecture is designed explicitly for this spectrum. Because it is provider-agnostic with full BYOM support, a team can start with a proprietary frontier model, evaluate open alternatives, and switch without changing their agent harness or their context engineering. The agent wrapper stays the same. Only the brain changes.

> **Case Study: The MCP Neutrality Play**[ANDev-049]
>
> Amanda Brock, CEO of Open UK, describes a conversation with one of the creators of the Model Context Protocol about why MCP was donated to the Linux Foundation's Agentic AI Foundation (AAIF). The motivation was preserving openness: "It's all about keeping it open and knowing that you've got that security forever of it being open."
>
> This matters for the tooling landscape because MCP has become the de facto standard for extending agent capabilities. Every major harness - Claude Code, Codex CLI, Goose, Cursor - supports MCP servers. Stage-specific tools increasingly expose MCP interfaces. When a protocol this central is controlled by a single company, every tool in the ecosystem carries that company's risk. The Linux Foundation donation was designed to remove that risk.
>
> Goose was donated to the same foundation. So was AGENTS.md. The pattern is deliberate: the building blocks of the agentic ecosystem are being placed in neutral governance structures where no single vendor can change the rules.

## Making the Choice

There is no single correct answer to the tooling question. But there are questions that reliably lead teams to the right answer for their situation.

**How much of the pipeline do you need today?** If you are starting from nothing and need to ship quickly, a full-pipeline platform removes months of integration engineering. If you already have a mature CI/CD pipeline, strong test coverage, and established review practices, an agent harness that plugs into your existing infrastructure may give you more leverage with less disruption.

**How important is model flexibility?** If you want to switch models as the landscape evolves - and it evolves fast - you need a harness or platform that does not hardwire a single provider. Claude Code only runs Claude models. Codex CLI only runs OpenAI models. Goose runs anything. Cursor supports multiple providers. This flexibility matters less today than it will in eighteen months.

**What is your context engineering maturity?** Full-pipeline platforms like Kiro embed context engineering into their workflow - steering files, spec structure, hooks. If your team has not yet built the muscle for writing and maintaining agent context, a platform that provides guardrails helps. If your team already has a sophisticated CLAUDE.md, custom MCP servers, and tested skills, a flexible harness lets you bring that investment forward.

**What is your risk tolerance for vendor lock-in?** This is not just about the model. Your specs, your context files, your workflow automation - all of it can become entangled with a specific vendor's format. Teams that prize portability lean toward open tools (Goose, Aider) and open standards (MCP, AGENTS.md). Teams that prize integration depth lean toward platforms (Kiro, Cursor) where tighter coupling enables tighter feedback loops.

**Are you building toward headless?** This is the most important question and the one most teams skip. If your goal is a factory that processes tasks autonomously - tickets in, PRs out, engineers reviewing - then every tooling decision should be evaluated against that destination. Can this tool run without a human at the keyboard? Can it be triggered by an event? Does it produce output that fits a PR-based review workflow? An interactive tool that requires a developer to start and steer each session is useful for learning, but it is a stepping stone, not a foundation.

**Do you need to go parallel?** Cian Clarke at NearForm identifies the solo-contributor assumption as one of the biggest limitations of current spec-driven tools.[ANDev-034] Most frameworks assume a single developer working through a single backlog. Headless architecture solves this naturally - you can run 20 agent sessions concurrently in the cloud without competing for a single developer's machine or attention. If parallel throughput matters, headless is the path.

The tooling landscape in mid-2026 is moving fast enough that any specific version comparison will be outdated by the time this book reaches your desk. What will not be outdated is the framework: understand the four categories, distinguish interactive from headless, and make choices that let you graduate from one to the other without starting over.

The worst outcome is not picking the wrong tool. It is building so much around interactive workflows - developer-local skills, IDE-centric review, manually triggered agent sessions - that the transition to headless operation requires ripping everything out. Plan for headless from day one, even if you start interactive.

Amanda Brock draws the historical parallel to the early web: "We've ended up with eight companies who control the digital infrastructure. And I don't think anybody wants to see that as the AI future."[ANDev-049] The tooling decisions you make now will determine whether your organization owns its AI code factory or rents it from someone who can change the terms at any time. Choose accordingly.

---
