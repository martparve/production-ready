# Chapter 3: The Context Development Lifecycle

Most agent failures are not intelligence failures - they are context failures. The model was smart enough; it just did not know what you needed it to know. It picked the wrong theme because nobody told it which design system to use. It hallucinated API endpoints because its training data predated the library version you are running. It wrote perfectly functional code that violated three of your team's architectural constraints - constraints that lived in a senior engineer's head and nowhere else.

This chapter is the foundation everything else in the book rests on. Before the pipeline processes a single feature, before agents write a single line of code, the factory needs its operating system: the context that tells agents how to behave.

Guy Podjarny, CEO of Tessl, has spent two years studying this shift. His conclusion is sharp: "Agents should operate the SDLC and the human should live in the context development lifecycle."[ANDev-037] The CDLC is not a supporting discipline. It IS the human job. Anthropic's engineering team arrived at the same conclusion independently: "Intelligence is not the bottleneck - context is."[Anthropic-context] Simon Willison coined the term "context engineering" to describe this emerging discipline - the art of providing models with the right information, in the right format, at the right time.[Willison-context]

In the factory model, agents run the production line. Humans design the factory floor. The context development lifecycle is how you design, test, distribute, and maintain the instructions that make the factory produce what you actually want.

## From Speccing the Program to Speccing the Programmer

In Podjarny's early episodes of the AI Native Dev podcast, he predicted a shift from code-centric to spec-centric development. He was close. But looking back from mid-2026, he corrects himself: "We've moved from speccing the program to speccing the programmer."[ANDev-037]

When you hire a senior engineer, you do not hand them a feature spec and walk away. You onboard them. You explain your team's conventions. You show them which libraries you use and which you have banned. You explain your deployment cadence, your testing philosophy, how you handle database migrations. You share tribal knowledge about the three systems that break every time someone touches the payments module.

You do all of that because a brilliant engineer without organizational context is a liability. They will make confident, well-reasoned decisions that are completely wrong for your environment.

Agents are no different. Except they join your team fresh on every task, with no memory of what happened yesterday and no instinct for what your organization values. Every session, you are onboarding a new hire. The context you provide determines whether that hire performs like a senior engineer who has been on the team for two years or like a confident junior on their first day.

This is why Podjarny's correction matters. The spec for your feature is important, yes. But it is a fraction of what agents need. They need the full onboarding package - how to build, how to test, how to collaborate, how to troubleshoot, how to balance speed and quality, how to use your existing infrastructure. All of that is context.

## The Three Categories of Context

Not all context is equal, and not all context belongs in the same place. The industry has converged on three categories, each with different delivery mechanisms, different costs, and different management challenges.

### Rules: Always-On Behavioral Steering

Rules are the instructions that go into every agent session, whether the agent needs them or not. They live in files like CLAUDE.md, .cursorrules, or system prompts. They are short, directive, and unconditional.

Examples:
- "Never use deprecated APIs. Always use the v3 endpoint."
- "All database queries must go through the data access layer. No raw SQL in controllers."
- "Test files go in `__tests__/` adjacent to the module, not in a top-level test directory."

Rules compete for a scarce resource: the context window. Every rule you add dilutes the attention the model pays to every other rule. This is not a theoretical concern - it is a measured effect with hard numbers behind it (more on this shortly).

Think of rules as standing orders for a military unit. They should be few, clear, and non-negotiable. If you find yourself writing a rule that only applies to one type of task, it probably should not be a rule.

### Skills: Reusable Task Patterns

Skills are structured instructions for how agents do specific types of work. Task decomposition templates, review checklists, implementation patterns, deployment procedures. They are invoked on demand - either explicitly by the user or implicitly when the agent recognizes a matching situation.

The key difference from rules: skills are not always loaded. They carry a small breadcrumb in the context window (a name and brief description) so the agent knows they exist. When the agent encounters a relevant situation, it loads the full skill. This progressive disclosure pattern keeps the base context window lean. Anthropic's guide to building effective agents identifies five workflow patterns - prompt chaining, routing, parallelization, orchestrator-workers, and evaluator-optimizer - each of which depends on loading the right skill context at the right stage rather than front-loading everything.[Anthropic-agents]

Richmond Alake, Director of AI Developer Experience at Oracle, frames skills through a neuroscience lens: "Skills are a form of procedural memory. Humans have procedural memory in our brain - the cerebellum stores routines and tasks. Skills are procedural knowledge for your agents."[ANDev-044]

The human equivalent is an SOP - a standard operating procedure. Your organization already has these. The challenge is translating them into a format agents can follow reliably.

One critical nuance: the same skill text does not produce the same behavior across different models. Podjarny is direct about this: "We have repeating data to show that the same words would not trigger Haiku and Sonnet and Opus to the same action. Opus is much more of a smartass and can choose to say, no, I know better and won't do it. Haiku might need more detailed instructions."[ANDev-037] Skills are not a write-once artifact. They need to be tested against the models your team actually uses.

### Knowledge: Information on Demand

Knowledge is the broad corpus of information agents reach for when needed. Architecture docs, API contracts, data models, library documentation, prior decisions. It is retrieved via search, RAG, MCP servers, or file system traversal - never stuffed wholesale into the prompt. A recent survey of RAG-for-code techniques confirms that providing relevant in-context code and API documentation yields consistent gains, but blindly retrieving similar-looking examples can actually hurt performance by consuming context budget without adding useful signal.[A-2510]

Maria Gorinova, a researcher on Tessl's AI engineering team, draws the distinction clearly: "Documentation is more about knowledge, more about facts. It's something the agent can reach for when it doesn't know something. Rules are more behavioral. The agent doesn't really know how to reach for behavioral instructions."[ANDev-032]

The cost model is different for each category. You can have thousands of knowledge documents with no performance penalty - the only question is whether the agent can find the right one at the right time. You can have dozens of skills with modest overhead. But you can have only a handful of rules before you start degrading performance.

## The Context-Attention Tradeoff

There is a fundamental tension at the heart of context engineering, and every architectural decision in this book runs into it eventually.

Context helps. Every rule you add genuinely improves agent behavior for the thing it describes. Tell the agent to use your team's logging library and it stops importing random alternatives. Describe your API conventions and it produces endpoints that match the existing codebase. Add a security policy and it stops writing SQL with string concatenation. Each individual instruction makes the agent more capable, more aligned with your codebase, more likely to produce code a reviewer will accept. The case for more context is real and measurable.

But attention is finite. Every token of context competes with every other token for the model's limited attention. Add a rule about logging, and the model pays slightly less attention to your rule about error handling. Add enough rules and the model follows none of them reliably. This is a measured effect with hard numbers behind it, not a metaphor.

Gorinova puts it bluntly: "The longer the steering context is, the more you try to ask the agent to behave certain ways, the less it's going to follow any of those suggestions."[ANDev-038]

The data is stark. The NoLiMa paper[Hsieh-2502] from 2024 measured a 15% drop in reasoning ability above 30,000 tokens of context. Liu et al.'s "Lost in the Middle" study showed the effect is not just about volume but placement: LLMs exhibit a U-shaped performance curve, degrading sharply when key information is buried in the middle of the context window rather than placed at the beginning or end.[Liu-2307] Daniel Jones[ANDev-045], founder of the AI-native consultancy Resync, reports on subsequent replication studies: "For GPT 4.1 era models, I've found between 30,000 and 60,000 tokens, again, reasoning capability drops off. That's not very much."[ANDev-038]

And it gets worse. A study out of Zurich showed that adding instructions to your agents.md file reduces the quality of outcomes by about 20% compared to having no instructions at all[ANDev-038] - the act of adding guidance, if done poorly, makes the agent worse than giving it nothing.

Jones puts this into practical terms: "I have certainly, there have been points where I've opened up Claude Code, no MCP servers installed, no Claude MD, and it's already using like 40,000 tokens just for its system prompt. So it doesn't take much to tip your model into the point where it's going to get confused."[ANDev-038]

This is not a problem you solve once. It is a tradeoff you navigate continuously. You are always choosing a position on a curve where the x-axis is context volume and the y-axis is attention fidelity per instruction. Move right (more context) and each individual instruction gets less attention. Move left (less context) and the agent lacks knowledge it genuinely needs. There is no position on this curve where both problems vanish. Every context decision is a bet about which failure mode costs more for a given task.

### Progressive Disclosure of Context

The resolution is not "less context" or "more context" but the right context at the right time - a pattern borrowed from interface design called progressive disclosure.

In UI design, progressive disclosure means showing users only the controls and information relevant to their current task, revealing complexity on demand rather than all at once. Applied to context engineering, it means the same thing: start the agent with the minimum viable context for its task, and inject additional context only when the agent reaches a point where it needs it.

This transforms the tradeoff from a static position on a fixed curve to a dynamic strategy that adapts per task. An agent working on a database migration gets database conventions, schema context, and migration-specific skills - not your frontend naming rules or your deployment checklist. An agent fixing a UI bug gets component patterns and design system context - not your database indexing policy. Each agent session occupies a different position on the context-attention curve, optimized for its specific task rather than carrying the full weight of every instruction the organization has ever written.

The three-category model - rules, skills, knowledge - is the mechanism for implementing progressive disclosure. Rules (always loaded) represent the absolute minimum: the handful of non-negotiable constraints that apply to every task. Skills (loaded on demand) represent task-specific procedures that activate when the agent recognizes a matching situation. Knowledge (retrieved when needed) represents the deep reference material that the agent pulls only when it encounters a specific question. This is not just an organizational taxonomy. It is an attention budget allocation strategy, and every decision about which category to place a piece of context into is a decision about when and how hard the model should pay attention to it.

> **Case Study: The Overloaded CLAUDE.md**[ANDev-045]
>
> A mid-size fintech company started their agentic coding journey the way many teams do - enthusiastically. Every time an agent made a mistake, someone added a rule. After three months, their CLAUDE.md file had grown to 4,200 words: coding standards, security policies, test requirements, deployment procedures, naming conventions, error handling patterns, and a section called "Things Claude Gets Wrong" that alone ran 800 words.
>
> Agent performance had been steadily declining, but the team attributed it to "model quality" and waited for the next release. When they finally measured, they found the agents were following their rules less than 40% of the time - worse than when they had started with a minimal configuration.
>
> They brought in a consultant (Jones, as it happens) who helped them ruthlessly prune the file to 600 words of genuine rules, migrate task-specific guidance into skills, and move reference documentation into retrievable knowledge files. Agent adherence to the remaining rules jumped to over 80%. The team shipped more features in the following two weeks than they had in the prior month.
>
> This is progressive disclosure in action. The team did not lose any of their accumulated knowledge - they redistributed it across the three categories so each piece loaded only when relevant. The total context available to the agent actually increased. The context loaded at any given moment decreased. Attention per instruction went up.

The context-attention tradeoff recurs throughout this book. When Chapter 8 discusses codebase onboarding, the question is how much repository context to inject and when. When Chapter 10 covers agent orchestration, the question is whether a single agent with full context outperforms multiple sub-agents with focused context. When Chapter 14 examines MCP integration, the question is how many tools to register before tool descriptions themselves consume the attention budget. When Chapter 20 analyzes Stripe's Minions system, their Toolshed - which curates ~500 available tools down to ~15 per task - is a direct implementation of progressive disclosure applied to tool context. Every architectural choice in the factory involves picking a position on the context-attention curve. Recognizing this tradeoff explicitly is what separates thoughtful context engineering from ad hoc prompt accumulation.

## Context Artifact Types and Their Lifecycles

Not every piece of context serves the same purpose or ages at the same rate. Understanding the types and their natural lifecycles helps you manage the portfolio.

**Specs.** Per-feature behavioral contracts. They describe what you want built, the acceptance criteria, the constraints. Specs have a short active lifecycle - they matter intensely during implementation and review, then become historical reference. They should be loaded for the task at hand and archived after.

**Codebase instructions.** CLAUDE.md files, system prompts, always-on rules. These are the standing orders. They should be the smallest, most stable set of non-negotiable behaviors. They change infrequently and every change should be tested (more on this below).

**Architecture context.** System maps, dependency graphs, API contracts, data models. This is knowledge the agent needs to make sound architectural decisions. It changes when your system architecture changes, which should be infrequent but is often poorly tracked. Stale architecture docs are among the most dangerous forms of context - they lead to agents confidently building against systems that no longer exist.

**Skills and templates.** Reusable prompt patterns for how your team does specific types of work. These evolve as your team learns, as models improve, and as your infrastructure changes. They require active maintenance - the part most teams skip.

**Guardrails.** Constraints, forbidden patterns, security rules. The things that should never happen regardless of what the agent is building. These are the highest-priority rules and should consume the least context possible. "Never expose customer PII in logs" does not need a paragraph of explanation.

## Skills as Software: The Distribution Problem

Here is where most teams go off the rails with skills. Someone writes a skill. It works. They share it by copying the markdown file into a Slack channel. Three people copy it into their repos. One person modifies their copy. The original author updates the source version. Now there are four divergent copies of the same skill, three of which are stale, and nobody knows which is which.

This is the dependency management problem, and we solved it decades ago for code. JavaScript had npm. Python had pip. Java had Maven. Every mature language has a package manager because copy-pasting source files between projects is a recipe for chaos.

Skills need the same infrastructure. Podjarny is blunt: "People are copying skills all over. They're designed to be reusable, and yet we kind of copy and duplicate them everywhere. We've seen that movie and we know where that ends."[ANDev-020]

What a mature skill distribution system requires:

- **Versioning.** Every skill has an identifier and a version number. You know exactly which version you are running.
- **A manifest file.** Your project declares which skills it depends on, at which versions. New team members install the same set automatically.
- **Update mechanisms.** When the source skill is updated, consumers can pull the new version deliberately - not silently, not automatically, but with awareness that something changed.
- **Cross-agent compatibility.** A skill should work in Claude Code, Cursor, Codex, and whatever ships next quarter. The format is standardized (Anthropic's agent skills spec has become the de facto standard, with Cursor, Codex, and others adopting it). But remember: same words, different behavior across models.

Roberts sees this pressure intensifying in enterprise contexts: "As soon as you have more than one repo, you run into how do I distribute these things? Your voice and tone for your brand - that's a global thing. Your brand style guides - global. How you might do reviews - global. But how do you share that across your developer base, which might be dozens or potentially thousands of people?"[ANDev-031]

If you are a team of five, copying files might be tolerable. If you are an organization of 500 engineers across 50 repos, it is a governance failure waiting to happen. The CTOs Jones talks to in his consulting work are already asking: "How the hell do you manage all of these skills? It's just scripts floating around moving between people's machines. We need this to be auditable. We need it to be versioned."[ANDev-045]

Treat skills as software artifacts. Give them the same lifecycle tooling you give your production code: version control, automated testing, package management, and deprecation processes.

## The One-Way Ratchet Problem

Sean Roberts, VP of Applied AI at Netlify, identifies a pattern that should alarm anyone managing context at scale. He calls it the one-way ratchet problem, referencing Mobs' Law of Bureaucracy: "Laws and regulations, once they're enacted, monotonically just grow, they never contract and they never substantially get repealed or reduced. And we are seeing that happening with context rules and context as well."[ANDev-031]

The dynamic is predictable. Agent breaks something. Engineer adds a rule. Agent breaks a different thing. Engineer adds another rule. Nobody removes the first rule because nobody knows if it is still needed. Six months later, the context file is bloated, contradictory, and actively harming performance.

This is the default trajectory for every team that manages context reactively.

Roberts' solution: evals. You need a systematic way to measure the impact of each context artifact. If you can run the same tasks with and without a specific rule and show that the rule improves outcomes, keep it. If you cannot demonstrate improvement, cut it.

"But how do you safely feel confident in peeling back some of those requirements?" Roberts asks. "And how do you fix this issue, but you cause other issues? How do you feel confident about not doing that? I think evals for the agent experience is going to be incredibly important."[ANDev-031]

The discipline here is the same one that distinguishes good software teams from mediocre ones: if it is not tested, it does not work. Your context rules are software. Treat them accordingly.

## Agent Memory vs. Static Context

The three categories above - rules, skills, knowledge - are all forms of static context. You write them, you store them, agents consume them. But there is a parallel track that is rapidly maturing: agent memory.

Alake[ANDev-044] breaks this into three types that mirror how human cognition works:

**Entity memory.** The agent's understanding of who you are, what you prefer, how you work. "We can front-load this information," Alake explains, "or we can have back-and-forth interaction and begin to formulate an understanding. Or we have both - start with some information and build on top of that."[ANDev-044]

**Procedural memory.** How to do things - the skills and SOPs we discussed above. This is the agent's learned workflow for specific task types.

**Episodic memory.** What happened before. Prior sessions, past failures, previous decisions. This is the memory type most conspicuously absent from today's agent architectures. Each session starts fresh, and every lesson learned is lost. Google's DIDACT research program points toward a solution: instead of training only on finished code, DIDACT trains on the process of development - edit histories, build errors, code review comments - capturing the episodic trail that developers leave behind.[Google-AI-SWE]

The lifecycle of memory is different from static context. Alake emphasizes a capability most teams overlook: the ability to forget. "If you work with context, forgetting or suppressing information doesn't come naturally. But when I speak to developers and I say, if you think about things from the perspective of memory, you immediately start to see that you need to implement a way of forgetting information."[ANDev-044]

Memory that never decays becomes noise. Just as the one-way ratchet bloats static context, uncurated memory accumulates stale associations, outdated preferences, and resolved issues. A robust memory system needs ingestion, encoding, storage, retrieval, and forgetting.

Where does this leave us practically? For mid-2026, most teams will manage primarily with static context (rules, skills, knowledge) and limited session-level memory. But the teams that build the infrastructure for persistent, curated agent memory now will have a compounding advantage. The agent that remembers that last Tuesday's database migration broke the payments module - and knows to check for that pattern in future migrations - is vastly more valuable than one that starts from zero every session.

The bridge between static context and dynamic memory is already emerging. Alake describes a pattern where agents that are omnipresent across tools - Slack, code editors, CI systems - can observe successful workflows and automatically generate new skills. "Agents today are omnipresent. They can go through different systems and understand different systems. Therefore, we actually don't have the problem of loss of knowledge. If you do this properly, you start to have like a scribe that is following you around, always writing down things you're doing successfully."[ANDev-044]

This is the vision: agent memory feeds the context development lifecycle automatically. The agent observes that a senior engineer always checks the cache invalidation layer after modifying the user service. It proposes a skill codifying that pattern. A human reviews and approves it. The skill is distributed to all agents via the registry. Now every agent on the team checks cache invalidation after user service changes, not just the ones paired with that particular senior engineer.

Static context is human-to-agent knowledge transfer. Agent memory is agent-to-context knowledge extraction. The CDLC needs both.

## Context Quality Testing

If your context is software, it needs tests.

Gorinova's team at Tessl has been running systematic evaluations on context quality.[ANDev-032] Their approach is straightforward: create coding scenarios, run agents with and without a specific piece of context, and measure the difference.

The results are revealing. For their documentation tiles (context packages describing library APIs), they measured 35% higher abstraction adherence on average when agents had access to the documentation. For newer libraries - those released in the last three years - the improvement jumped to 50%. For a deep dive on LangGraph features released after the model's training cutoff, context improved performance by 90%.[ANDev-032]

But the inverse is equally important. Not every piece of context helps. The Tessl team found that a skill codifying Andrej Karpathy's prompting best practices had a minimally negative effect on agent performance. It over-complicated simple tasks. Another skill, Browser Use, actually reduced performance by about 3% because the model already knew how to do what the skill was teaching.[ANDev-032]

> **Case Study: The Skill That Hurt More Than It Helped**[ANDev-032]
>
> Tessl's evaluation team ran task evals on two browser-related agent skills. Agent Browser, from Vercel, took agent success rates from 28% to 71% - a dramatic improvement. The skill was clearly filling a knowledge gap the model could not bridge on its own.
>
> A conceptually similar skill called Browser Use, however, told a different story. The baseline success rate without the skill was already 85%. Adding the skill dropped performance to about 82%. The skill was re-teaching the model things it already knew, and the added context consumed attention that would have been better spent on the actual task.
>
> The lesson is not that skills are unreliable. The lesson is that unmeasured skills are unreliable. Without evals, you have no idea whether your carefully crafted context is the difference between 28% and 71% success or an active drag on performance. The only way to know is to test.

There is a deeper lesson here about what evals reveal. Gorinova's team also found that agents performed worse on niche libraries (fewer GitHub forks) and on very old or very new library versions. The performance curve formed a bell shape - models did best on libraries that were popular during their training period and worst on everything else. But with context tiles, niche and popular libraries performed at roughly the same level. Context was an equalizer: it closed the gap that training data left open.[ANDev-032]

This has direct implications for enterprise teams working with internal libraries, proprietary frameworks, or industry-specific tools that will never appear in public training data. For these teams, context is not a nice-to-have. It is the difference between agents that can use your stack and agents that hallucinate your APIs.

The practical takeaway: every piece of context in your system should be able to answer the question "what measurably improves when this is present?" If it cannot, it is a candidate for pruning.

## Agent Therapy: The Feedback Loop

Roberts describes a practice he calls "agent therapy." When an agent goes off the rails, instead of immediately correcting the output, he has the agent analyze what went wrong.

"I have this MCP where if the agent's really going off the rails, I have it look back and say, what could we have done better here? It's like an agent therapy session. What should we do better to make sure that you're going to get this right next time? And specifically update the context files to make sure that happens."[ANDev-031]

The pattern is simple:

1. Agent fails at a task.
2. Ask the agent to analyze what context was missing or misleading.
3. The agent proposes updates to context files.
4. Human reviews and approves the updates.
5. Agent retries the task with updated context.

This creates a closed feedback loop from failure to improvement. Every agent failure becomes an investment in future performance. The context files get better with each failure - but only if you have the discipline to route failures through this loop instead of just fixing the output and moving on.

There is a related practice worth adopting alongside agent therapy: having AI review tools not just flag what is wrong in a pull request, but suggest when patterns were missing from context files that would have prevented the issue. Roberts advocates for this: "Not only having your AI review tool figuring out what's wrong with a thing, but also suggesting when there are patterns that were missing from your context files that would have prevented this from happening in the future."[ANDev-031] This closes the loop between code review and context improvement - every review becomes an opportunity to strengthen the factory's operating system.

The broader principle is that context should be a living system, not a static artifact. It should improve over time through structured feedback, measured through evals, and pruned when it stops delivering value. Teams that treat their CLAUDE.md as a write-once configuration file are leaving enormous performance on the table.

## The Decision Matrix: How to Manage Context at Scale

As you scale from one developer to a team to an organization, context management decisions become architectural. Here are the three dimensions where you need to make deliberate choices.

### Centralized vs. Federated Context Management

**Centralized:** A platform team or AI DevX team owns the canonical set of rules, skills, and knowledge. Teams consume from the central registry. Changes go through a review process.

- Pros: Consistency, auditability, reduced drift, easier to evaluate.
- Cons: Bottleneck risk, slower response to team-specific needs, one-size-fits-all pressure.

**Federated:** Each team manages its own context, with shared conventions but local autonomy.

- Pros: Teams can adapt quickly, context matches team-specific needs.
- Cons: Drift between teams, duplication, harder to audit, no shared learning.

The right answer for most organizations at scale is a hybrid: centralized global context (security rules, architectural principles, coding standards) with federated team-level context (project-specific skills, local conventions). Jones sees this emerging in his enterprise consulting: "Rolling out a consistent, sensible, auditable, regulatory-safe set of agentic coding practices - that's going to need coordination and that's going to need to come from somewhere central."[ANDev-045]

### Automated vs. Manual Context Generation

**Manual:** Humans write and maintain all context artifacts. High quality per artifact, does not scale.

**Automated:** Agents analyze code, logs, and outcomes to generate and update context. Scales well, but requires robust eval to catch drift and errors.

**Hybrid (recommended):** Automated generation with human review. Use agents to draft context updates from failure analysis (agent therapy), from code review patterns, from production incidents. Have humans approve and refine before promotion.

### Front-Loaded vs. Just-in-Time Injection

Front-loaded versus just-in-time injection is one of the most consequential architectural decisions in context engineering.

**Front-loaded:** Pack everything the agent might need into the initial context. Simple to implement. Runs headlong into the saturation problem.

**Just-in-time:** Give the agent minimal context to start, inject additional context only when specific situations arise. More complex to implement. Dramatically more efficient with the context budget.

Ryan LaPopolo, a member of technical staff at OpenAI, is the most vocal advocate for just-in-time injection. His team at OpenAI has banned themselves from opening their IDEs and runs agents for 6, 12, even 30-hour sessions.[OpenAI-harness] The key to making this work: "Instead of front-loading all the context into AGENTS.md, I want to just-in-time inject how to remediate a linter failure at the time it happens. This allows us to have much wider periods of black box behavior where the agent is reasoning and cooking and writing code and resolving its own failures."[ANDev-052]

LaPopolo's team keeps just five or six skills - a deliberately small number. "In order to maximize attention and limit context, we want the code, the process, the test to be the same as much as possible. And we want the agents to largely cook with the minimum amount of instructions, giving it context just in time."[ANDev-052]

This is the direction the industry is heading. The constraint is not how much context you can create but how precisely you can deliver the right context at the right moment.

> **Case Study: Stripe's 1,300 PRs Per Week**[ANDev-052]
>
> Stripe's internal coding agent, Minions, generates about 1,300 pull requests per week without human assistance beyond standard code review. Steve Kuliski, a Stripe engineer, explains how they manage context for a 10-year-old codebase with vast amounts of institutional knowledge: "Maybe 80% of coding at Stripe follows some blessed paths - making an API change, a change to documentation, introducing a new currency. Because we can pattern match to one of those pathways, we can make sure we're introducing the appropriate context to nail that."
>
> Stripe does not dump everything into a single context file. They recognize the type of change being made and load the context that matches. "The context you need to make a docs change looks a lot different than the context you need to make a cross-border money transfer kind of thing. Understanding the type of products we're building and the type of changes we're making lets us thoughtfully put in context in advance, instead of just saying, here's the entire thing, good luck."
>
> This is just-in-time injection at organizational scale. The agent does not need to know about payment compliance rules when it is fixing a typo in the docs. Pattern-matching the task type to the relevant context keeps each session lean and focused.

## The CDLC as a Continuous Loop

The context development lifecycle is not a one-time setup. It is a continuous loop with five phases:

**1. Define.** Figure out what correct behavior looks like. This is harder than it sounds. As Podjarny notes, "knowing what you want is actually hard."[ANDev-037] Start with your most painful failure modes: what are agents getting wrong most often? Those failures point to missing context.

**2. Encode.** Translate that knowledge into the right artifact type. Rules for non-negotiable behaviors. Skills for repeatable procedures. Knowledge for reference information. Be ruthless about which bucket each piece belongs in.

**3. Evaluate.** Test the context. Run the same tasks with and without it. Measure the difference. If a rule does not improve outcomes, it is noise. If a skill makes agents slower without making them more accurate, cut it.

**4. Distribute.** Get the right context to the right agent at the right time. This is the package management problem - versioning, manifests, installation, updates. Do not copy markdown files between repos. Use a registry with version tracking.

**5. Observe and Learn.** Watch how agents perform in production. Extract insights from agent logs. Identify cases where the agent deviated from expected behavior. Feed those observations back into step 1.

This loop never stops. Models change. Your codebase evolves. Your team learns new things. Business requirements shift. The context that was perfect three months ago may be stale, redundant, or actively harmful today.

## Why This Is the Human Job

There is a common objection to investing heavily in context engineering: "Won't the models just get better and make this unnecessary?"

The models will get better - they are already dramatically better than they were a year ago - and context engineering will only become more important, not less. Better models can do more with less context, true. But better models also enable more ambitious tasks. As you move from asking agents to write a function to asking them to build a feature to asking them to operate an entire development pipeline, the amount of organizational context they need increases, not decreases. A model smart enough to architect a microservice is a model that needs to understand your service mesh, your team's API conventions, your deployment topology, your data residency requirements, and your on-call rotation.

Intelligence without knowledge is dangerous. The smarter the model, the more confidently it will make decisions based on incomplete information. The more capable the model, the more critical it is that the information it operates on is correct, current, and complete.

This is why Podjarny frames the CDLC as the human job. The agents will write the code, run the tests, perform the reviews, deploy the changes. Humans will define what correct looks like, encode that definition into context, test whether the encoding works, and update it when reality changes.

As Bhageetha from ThoughtWorks put it on the podcast: "AI amplifies indiscriminately. If you have a bad setup, you might just amplify that bad setup."[ANDev-018] The context development lifecycle is how you make sure you are amplifying the right things.

## Practical Starting Points

If you are reading this chapter and feeling overwhelmed, here is where to start.

**Week 1: Audit.** What context do your agents currently have? Read your CLAUDE.md or equivalent. Count the words. Check whether it has grown monotonically since it was created. Ask your team: what are the three things agents get wrong most often?

**Week 2: Prune and categorize.** Take your existing context file and sort every instruction into one of three buckets: rule (always needed), skill (needed for specific task types), or knowledge (reference information). Cut anything that does not clearly fit in one bucket. Your rules file should get much shorter.

**Week 3: Measure.** Pick the three most common agent tasks your team performs. Run each task five times with your current context, five times with your pruned context. Compare success rates. You will likely find that less is more.

**Week 4: Build the loop.** Establish the agent therapy pattern. When agents fail, route through the analysis step. Collect the proposed context updates. Review and promote the ones that survive scrutiny.

That gives you a basic CDLC in a month. The rest of this book will build on this foundation - showing how context flows through each pipeline stage, how it scales across teams, and how it evolves as your factory matures.

The context development lifecycle is the quality system for the inputs that determine output quality. Get it right, and the factory hums. Get it wrong, and you are amplifying chaos at machine speed.

---
