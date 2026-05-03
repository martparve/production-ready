# Chapter 5: Intent Capture: From Business Language to Structured Input

A product manager types "Users should be able to favorite items" into a Jira ticket. A Slack message says "checkout is too slow, customers are dropping." A CTO records a voice memo on her commute about an audit trail for compliance. A customer support lead pastes a screenshot of an angry email thread and writes "fix this."

These are all intents. They are the raw material entering the factory. And none of them, in their current form, are ready for a machine to act on.

Intent capture is the first stage of the pipeline, the point where a human thought crosses the boundary into a system that will eventually produce working software. Every error here propagates. Every ambiguity compounds. Every missing detail becomes either a wrong assumption the machine makes confidently or a clarifying question that interrupts someone's afternoon. The goal of this stage is not perfection. It is sufficiency: enough signal for the downstream stages to do their jobs without inventing things.

This chapter covers what intent capture means when machines formalize the specifications, how to build intake systems that produce useful signal, and why the semantic gap between business language and technical reality is the hardest problem at this stage.

## What Happens at This Stage

Intent capture takes unstructured human language and packages it for machine consumption. The input is whatever the human provides: a sentence, a paragraph, a document, a recording. The output is a structured intake artifact with enough information to feed into spec formalization (Chapter 6) or, at minimum, enough information for the machine to generate intelligent clarifying questions.

In a traditional development workflow, the quality of a feature request mattered, but a skilled developer could compensate for ambiguity. They had organizational context, relationship access ("I'll just ask Sarah what she meant"), and enough domain knowledge to fill the gaps themselves. The spec lived partly in the ticket and partly in the developer's head. That worked because the developer was the spec.

Agents do not have organizational context. They do not know Sarah. They do not know that "revenue" means net revenue excluding refunds in your company, or that "the billing page" actually refers to three separate micro-frontends maintained by two different teams. When an agent encounters ambiguity, it does one of two things: it guesses confidently, or it asks a question. The quality of your intent capture determines which one happens.

The bar for intent capture has shifted. It is not "write a document comprehensive enough that a developer can build the feature." It is "provide enough signal that a machine can ask the right clarifying questions." This is a lower bar in terms of initial effort and a higher bar in terms of precision. You do not need to write a perfect spec. You do need to be clear about what you want, what systems are affected, and what success looks like.

There is a cost to this precision. Research on formal methods in requirements engineering shows that formalizing requirements can increase development cycle time by roughly 30%.[Lorch-formal] That is real overhead, and teams should not pretend otherwise. But the payback comes in clarity, correctness, and verifiability - properties that matter more, not less, when agents are the downstream consumers. A human developer encountering an ambiguous requirement will pause and ask a colleague. An agent encountering the same ambiguity will pick an interpretation and build confidently on top of it. The 30% upfront cost of formalization prevents the 300% rework cost of an agent that spent a day implementing the wrong interpretation at machine speed.

## How It Works Technically

Intent enters the pipeline through one of four channels: ticketing systems, messaging platforms, dedicated intake forms, or direct prompt input. Each channel has different trade-offs in structure, metadata richness, and adoption friction.

### Ticketing System Integration

Jira, Linear, and GitHub Issues remain the most common entry points for teams with established workflows. The advantage is that these systems already capture some metadata: priority, assignee, project, labels, linked issues. The disadvantage is that the free-text body of a ticket is exactly as ambiguous as the person who wrote it.

Integration works through webhooks or polling. When a ticket reaches a designated status (typically "Ready for AI" or equivalent), the factory ingests the ticket body and metadata, runs it through an intake processor, and either promotes it to spec formalization or generates a structured set of clarifying questions posted back as a comment on the ticket.

Linear deserves a mention for its API quality and its native support for project-level context. A Linear issue carries its project description, team configuration, and label taxonomy as queryable metadata, which gives the intake processor more signal to work with than a bare Jira issue. GitHub Issues, meanwhile, have the advantage of living alongside the code, making it trivial to link intent to the repository it affects.

The practical pattern most teams converge on: a bot monitors a specific label or status transition, ingests the ticket, and enriches it with metadata from adjacent systems (the repository structure, recent changes, related tickets). The enriched artifact flows into spec formalization.

### Messaging Platform Integration

Slack and Teams messages are the worst possible format for intent capture and the most common way features actually get requested. A message is contextual, conversational, and ephemeral. It references a shared understanding that exists nowhere except in the heads of the participants.

That said, pretending people will stop requesting features in Slack is a losing bet. The practical approach is a Slack bot that allows a user to promote a message (or thread) into a formal intake artifact. The bot extracts the message content, identifies mentioned users and channels, captures any linked documents or screenshots, and opens a short interactive form to collect the minimum required metadata: affected system, priority, and a one-sentence description of the desired outcome.

This is a translation layer, not a replacement for the ticketing system. The bot creates the ticket in Jira or Linear and links back to the original Slack thread for context. The thread becomes a reference, not the source of truth.

### Dedicated Intake Forms

Custom intake forms sit at the high-structure end of the spectrum. They enforce specific fields: description, affected systems, success criteria, constraints, related documentation. They can include dropdowns for known domains, auto-complete for system components, and links to the business glossary.

The advantage is obvious: structured input produces structured output. The disadvantage is equally obvious: adoption. Every additional required field is friction. Forms that take fifteen minutes to fill out get abandoned or gamed (every priority becomes "Critical," every timeline becomes "ASAP").

The teams that make forms work keep them short - five to seven fields maximum - and make clear that the form is the starting point, not the finished specification. The machine will ask follow-up questions. The form's job is to provide enough context that the follow-up questions are targeted rather than generic.

### Event-Driven Triggers (Headless Mode)

In the headless factory, intent capture is not a human action at all - it is an event. An issue is assigned to the factory's service account. A Slack emoji reaction promotes a message. A monitoring alert fires. A scheduled job detects a dependency with a known CVE. The factory ingests the event, enriches it with metadata from adjacent systems, and promotes it into the pipeline without any human opening an IDE or starting an agent session.

This is the target architecture. Everything above - ticketing integration, messaging integration, intake forms - should be designed as event sources that the headless factory consumes, not as workflows that require a developer to manually forward a ticket to their local agent.

### Direct Prompt Input (Interactive Mode)

The simplest entry point: a developer opens their agent and types what they want. This is vibe coding's natural mode, and it is the mode where intent capture most often fails. It also keeps the developer as an operator rather than an overseer - fine for learning and exploration, but not how the factory runs at scale.

When a developer types "add favorites" into Claude Code, the intent exists only in that session's context. There is no ticket to trace back to. There is no metadata. There is no way for a second person to understand what was built or why. Nikhil Swaminathan at Kiro[Kiro] describes the problem precisely: vibe coding produces work where the decision log is captured in a conversational thread rather than a document, relevant only at the moment it was typed.[ANDev-016]

Direct prompt input is fine for solo exploration and prototyping. It is inadequate for any work that will be reviewed, maintained, or extended by someone who was not present when the prompt was written. The factory needs a record. If your developers start features by prompting agents directly, the minimum viable discipline is to have the agent write the intake artifact before it writes any code. Kiro enforces this structurally with its spec mode.[ANDev-016] Other harnesses can approximate it through rules in CLAUDE.md or equivalent configuration files.

## The Semantic Layer Problem

Jason Ganz, Head of Developer Experience at dbt Labs, captures the hardest problem in intent capture with a single observation about how organizations define business terms: five people will have multiple definitions, and the LLM will invent another one.[ANDev-008]

This is not a theoretical concern. It is the single most common failure mode for data-referencing intents, and it increasingly matters for any intent that touches business logic.

When a stakeholder writes "show me revenue by region," the word "revenue" could mean gross revenue, net revenue, revenue excluding refunds, revenue including pending charges, ARR, MRR, or some internal metric that maps to none of the standard definitions. The database has columns for several of these. The LLM, being eager to help and lacking the institutional knowledge to know which definition applies, will pick one and produce a confident, reasonable, and possibly wrong answer.

> **Case Study: Five Definitions of Revenue**
>
> Jason Ganz at dbt Labs describes a pattern he sees across organizations of every size: "Every organization defines revenue differently. And in fact, every organization probably has five or nine different definitions of revenue that ultimately some poor soul has to go and reconcile." When an LLM encounters an intent that references "revenue," it generates SQL that looks reasonable and produces a number. The problem is that the number might not match any of the organization's recognized definitions. "LLMs are like a very smart, eager [person], but they don't know anything about your business. You tell it to go calculate revenue. It's going to come up with one of nine, or it's going to make a tenth, an eleventh, a twelfth."[ANDev-008]
>
> dbt's solution is the semantic layer: a formal mapping between business concepts and their technical definitions. When an intent references "revenue," the system resolves it against the semantic layer rather than letting the LLM infer a definition from column names. Ganz reports that benchmarking shows "much, much more accurate" results when LLMs operate on semantic concepts rather than raw structured data. The semantic layer does not just improve accuracy - it improves consistency, ensuring that "revenue" means the same thing regardless of who asks or which agent answers.

The semantic layer pattern generalizes beyond data engineering. Any organization with domain-specific terminology - which is every organization - has a vocabulary gap between business language and technical reality. "The billing page" might refer to three micro-frontends. "Enterprise customers" might mean customers on the Enterprise plan, or customers with over 500 seats, or customers assigned to the enterprise sales team. "Latency" might mean p50, p95, or p99 depending on who is talking.

Intent capture should link business terms to their canonical definitions. This can be a formal business glossary, a semantic layer like dbt's, or even a curated section of your agent's context (a terminology file in CLAUDE.md or equivalent). The mechanism matters less than the discipline: when the factory encounters a business term in an intent, it should resolve it against an authoritative source rather than letting the agent guess.

For teams just starting, the minimum viable approach is a markdown glossary of the twenty most commonly misunderstood terms in your domain, included in the agent's context. This is not elegant. It is effective. As Ganz notes, the abstractions built to solve these problems for humans are the same abstractions needed for AI systems - just with a more rigorous enforcement layer.[ANDev-008]

## The Human Role

The human's job at the intent capture stage is deceptively simple: express what you want clearly enough that a machine can ask you good questions.

This is not the same as writing a complete specification. The complete specification is the output of stage 2 (spec formalization), not stage 1. The human at stage 1 is responsible for four things:

**Declaring the outcome.** What should be true after this work is done that is not true now? "Users can favorite items and see their favorites list" is useful. "Improve the product experience" is not.

**Identifying affected systems.** Which parts of the codebase, which services, which databases are involved? Even an approximate answer ("the frontend product pages and probably the user profile service") saves the machine significant exploration time.

**Stating success criteria.** How will you know this is done? A metric ("checkout p95 latency below 400ms"), a behavior ("clicking the heart icon toggles favorite state and persists across sessions"), or a business outcome ("compliance team can generate audit reports for any permission change in the last 90 days").

**Naming constraints.** What must not happen? What systems must not be modified? What timelines apply? Constraints are often more important than requirements because they define the boundaries the machine must respect.

Everything else - edge cases, technical design, test strategies, implementation order - is the machine's job to surface and the human's job to approve. The clarification loop between intake and spec formalization is where most of the value of AI-assisted development materializes. A good intake processor reads "add favorites" and comes back with: "Should favorites persist across sessions or reset on logout? Should there be a maximum number of favorites? What happens to a favorited item if the product is discontinued? Is this user-specific or account-level?" These are questions a senior developer would ask in a backlog grooming session. The machine asks them before anyone writes a line of code.

## Tooling

Intent capture tooling falls into three categories: native platform support, agent harness extensions, and purpose-built intake tools.

**Native platform support.** Kiro handles intent capture natively through its spec workflow. A developer enters an idea - "add the ability to favorite items" - and Kiro generates structured requirements in EARS format[Mavin-EARS], with user stories and acceptance criteria. The entire flow from raw intent to structured requirements happens inside the IDE, with the developer reviewing and editing at each step. Nikhil Swaminathan's team at Kiro reports that users who skip straight to coding (vibe mode) frequently lose track of what they built and why, while users who start with specs have a traceable record of every decision.[ANDev-016]

**Agent harness extensions.** Claude Code, Codex CLI, and Goose do not have built-in intent capture workflows, but they can be extended through MCP servers and context configuration. A Jira MCP server can read tickets and make them available as agent context. A Slack MCP server can ingest promoted messages. The pattern is consistent: the harness provides the agent loop, and MCP provides the integration with your intake systems.

**Purpose-built intake tools.** Backlog.md[BacklogMD], created by Alex Gavrilescu[ANDev-024], represents a class of tools designed specifically for the AI-native workflow. These tools treat task management as a problem that agents and humans need to share, with formats optimized for both audiences.

> **Case Study: Backlog.md and AI-First Project Management**
>
> Alex Gavrilescu, a lead engineer in Vienna, built Backlog.md after hitting the limits of vibe coding at scale. His problem: every new Claude Code session required re-explaining the same context, re-encountering the same pitfalls, and re-issuing the same instructions. "The problems were single task problems that would repeat themselves on every single task," he explains. "Every time you have a new session with your agent and you try to build as much as possible within your context window. And this doesn't scale."[ANDev-024]
>
> His solution was to extract project management into markdown files stored in the Git repository. Each task is a markdown file with metadata, dependencies, acceptance criteria, and (after implementation) notes about what was done. The key design decision: Backlog.md is a CLI tool that agents operate alongside humans, rather than an AI-powered system that replaces human judgment. A developer tells Claude "break this feature down using Backlog.md" and the agent creates atomic tasks, each scoped to fit within a single productive context window.
>
> Gavrilescu's insight about task sizing is particularly useful: he found that telling Claude to "break down this feature into smaller tasks that each can fit in a good PR" produced consistently well-scoped tasks. The model's training on millions of GitHub pull requests gave it an intuitive sense of what constitutes a reviewable unit of change. The acceptance criteria in each task become the contract between the human (who reviews) and the agent (who implements).
>
> The tool also addresses Gavrilescu's observation about agent context: "They start reading the files that they have to modify when they start working on the task. And by the time they are done, that's the moment where they really know almost everything about how the task should be done. But the task is already finished at this point." His pragmatic response is a two-pass pattern: let the agent build a rough prototype to learn the codebase, throw it away, and build again with the full context it accumulated on the first pass.

**Ticketing system integrations.** Jira, Linear, and GitHub Issues all have robust APIs and existing MCP servers. The integration pattern is straightforward: an event (status change, label application, or webhook) triggers ingestion, the intent is enriched with metadata from adjacent systems, and the artifact flows into the pipeline. Most teams start with a simple bot that reads a ticket body and posts clarifying questions back as comments. This is crude and effective.

**Slack bots.** Several open-source Slack bots exist for promoting messages to tickets. The best ones let a user react with an emoji to trigger intake, which is zero friction for the requester. The bot handles the structured extraction and ticket creation.

## Decision Matrix: How Structured Should Intake Be?

The central decision at this stage is how much structure to impose on incoming intents. There are three viable positions, and the right choice depends on your team's adoption readiness and the cost of rework in your domain.

### Option 1: Lightweight Templates

A short intake template with three to five fields: title, description, affected systems, success criteria, and priority. Can be implemented as a Jira issue template, a Linear template, or a markdown file.

**Pros:** Low friction. Easy adoption. Works with existing ticketing workflows. Does not require new tooling.

**Cons:** Variable quality. A template with optional fields gets fields left blank. The description field carries the same ambiguity problem as unstructured input. Requires a strong clarification loop downstream to compensate for sparse input.

**Best for:** Teams early in their AI-native adoption, where the priority is getting people to use the pipeline at all rather than optimizing input quality.

### Option 2: Rigid Forms with Required Fields

A detailed intake form with required fields for affected systems (selected from a predefined list), success criteria (validated against a format), constraints, related documentation, and semantic term resolution (mapping business terms to glossary entries).

**Pros:** High-quality, consistent input. Reduces the clarification loop. Makes spec formalization faster and more accurate. Easier to measure intake quality across the organization.

**Cons:** Adoption friction. People avoid forms they find tedious. Gaming (every field gets a perfunctory answer). Maintenance burden on the form itself: the predefined lists of systems and terms need to stay current. Teams with high request volumes find the per-request cost prohibitive.

**Best for:** Teams with regulated domains (finance, healthcare, compliance) where the cost of a wrong implementation is high enough to justify the intake overhead. Also suitable for platform teams that process requests from many internal customers and need consistent quality.

### Option 3: Free-Form Input with AI Pre-Processing

Accept any format of input - a sentence, a paragraph, a document, a voice recording. Run it through an AI intake processor that extracts structured fields, identifies ambiguities, resolves terms against the glossary, and generates targeted clarifying questions. The human reviews the AI-extracted structure and answers the clarifying questions.

**Pros:** Lowest friction for the requester. The AI does the structuring work. Scales to diverse input formats. The clarification loop is targeted rather than generic.

**Cons:** Requires a good AI intake processor (which is itself a non-trivial system to build and maintain). The quality of the extracted structure depends on the model's access to organizational context. Without a semantic layer or glossary, the AI will guess at business term definitions. Adds a processing step and latency before work begins.

**Best for:** Teams with diverse intake sources (Slack messages, customer support tickets, executive voice memos) where imposing a single format is impractical. Also suitable for organizations that have already invested in context engineering (rich CLAUDE.md or equivalent) and can provide the intake processor with strong organizational context.

### Should You Enforce Semantic Resolution?

For intents that reference business metrics, domain-specific terms, or data definitions: yes. The cost of letting an agent guess at what "revenue" or "active user" or "enterprise customer" means is a wrong implementation discovered late.

For intents that are purely technical ("upgrade the React version," "fix the broken test in checkout-service"): no. Semantic resolution adds overhead without value when the intent is already in technical language that maps directly to code.

The practical rule: if the intent uses words that mean different things to different departments, resolve them before the intent leaves this stage. A glossary check is cheap. A wrong implementation is not.

### Recommendation

Start with Option 1 (lightweight templates) and invest in Option 3 (AI pre-processing) as your pipeline matures. Option 2 (rigid forms) is justified only in regulated domains or high-cost-of-failure environments.

The reason is adoption. A pipeline that nobody uses is worth less than an imperfect pipeline that everyone uses. Lightweight templates get people into the system. AI pre-processing improves quality without increasing friction. The clarification loop between intake and spec formalization compensates for sparse initial input - that is what it is for.

Regardless of which option you choose, invest in defining contracts before implementation begins. Microsoft's ISE team documented their experience with API design-first development using TypeSpec: defining the API contract before writing any code unblocked all roles simultaneously - frontend, backend, testing, documentation - because everyone could work against the agreed interface.[MS-TypeSpec] The same principle applies to intent capture. When the intake artifact clearly defines what success looks like, the spec formalization stage, the test generation stage, and the implementation stage can all proceed with a shared target. The contract is not the code. It is the agreement about what the code must do, and that agreement needs to exist before anyone - human or agent - starts building.

If you have a data-heavy domain, invest in semantic resolution early. Build the glossary. Link it to your intake process. This is cheap to do and expensive to skip. Ganz's observation[ANDev-008] is not an edge case: the semantic gap between business language and technical definitions is the default state of every organization, and agents are worse at navigating it than the humans they replace.

## Anti-Patterns

Three patterns reliably produce bad intents. Avoid them.

**The prompt-as-intent.** A developer opens Claude Code and types "make the checkout faster." There is no ticket, no record, no metadata. When the developer's session ends, the intent is gone. Even if the implementation is perfect, nobody else knows what was built or why. Discipline: if it matters enough to build, it matters enough to record. GitClear's 2025 analysis of AI-assisted code quality makes the cost of this anti-pattern measurable: code written with AI assistance shows significantly higher churn rates - it gets revised and rewritten more often than human-authored code, and the proportion of moved and refactored code (indicators of thoughtful maintenance) has declined.[GitClear-2025] When intent capture is skipped, the agent writes fast but writes the wrong thing, and the resulting churn compounds. Poor intent capture does not just produce bad first drafts. It produces bad second and third drafts too, because the lack of a clear target means revisions are also unanchored.

**The novel.** A product manager writes a three-page document covering every possible scenario, edge case, and future consideration. The agent ingests all of it, loses focus, and implements a subset that may or may not align with the PM's priorities. Discipline: the intent is not the spec. State the outcome, the constraints, and the success criteria. Let the machine surface the edge cases and ask about them one at a time.

**The chain-of-Slack.** A feature request emerges from a twenty-message Slack thread involving four people. Someone copies the thread into a Jira ticket with "see discussion above." The agent reads it and has to reconstruct the consensus from a conversation where half the messages are jokes, one participant changed their mind halfway through, and the final decision was never explicitly stated. Discipline: Slack threads are context, not intent. Someone has to distill the thread into a clear statement of desired outcome before it enters the pipeline.

## Connecting to the Next Stage

Intent capture produces an artifact. That artifact is not a specification - it is the input to spec formalization (Chapter 6). The distinction matters because it sets expectations for both humans and machines.

The human who writes the intent does not need to be a product manager. They do not need to understand EARS syntax or acceptance criteria formats. They need to clearly state what they want, what systems are involved, and how they will know it is done.

The machine that receives the intent is responsible for translating it into a structured specification: user stories, acceptance criteria, edge cases, technical constraints. The machine is also responsible for identifying what is missing and asking for it. A good clarification loop turns a sentence ("add favorites") into a comprehensive spec covering persistence, empty states, toggle behavior, and accessibility - details the human may not have considered.

Alex Gavrilescu's experience building Backlog.md with 99% AI-generated code illustrates the principle cleanly: "The coding part is always done well if the task and the specs are well described."[ANDev-024] The investment at the intent capture stage pays compound returns at every subsequent stage. The few minutes spent writing a clear intent with success criteria save hours of rework when the agent implements the wrong interpretation of an ambiguous request.

The economic case for this investment is stronger than most teams realize. Capers Jones's analysis of over 12,000 software projects found that requirements modeling and requirements inspections each achieve defect removal efficiency (DRE) above 85% - higher than any form of testing alone.[Jones-defects] Testing, even comprehensive testing, tops out at lower DRE rates because it operates after defects have already been encoded into design and code. In a factory where agents compound ambiguity at machine speed, Jones's finding takes on new force: the highest-leverage quality investment is not better test generation or more sophisticated code review. It is better intent capture. A defect caught at the requirements stage costs a fraction of what the same defect costs when discovered through testing or, worse, in production. When agents are writing the code, the multiplication factor is even larger because the agent will confidently implement the wrong interpretation and generate tests that validate the wrong behavior.

The factory does not need perfect input. It needs honest input: a clear statement of what you want, an honest assessment of what you know and do not know, and enough structure for the machine to fill in the rest. That is the bar. It is not high. Most organizations are not clearing it.

---
