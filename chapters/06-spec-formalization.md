# Chapter 6: Spec Formalization: The Machine Translates Intent

This is the chapter where the factory starts producing.

Everything before this was preparation: building context, selecting tools, designing the pipeline. Now a human has an idea for a feature. Something needs to happen to that idea before agents can act on it safely. That something is spec formalization - the process of translating raw business intent into structured, testable, executable specifications that agents can implement without drifting into hallucinated requirements or shadow decisions.

Spec formalization is the first point in the pipeline where AI does real work. A human walks in with a sentence - "add the ability to favorite items" - and a machine walks out with behavioral contracts, acceptance criteria, interface definitions, data model changes, edge cases, and error handling strategies. The quality of that translation determines whether the rest of the pipeline produces working software or expensive garbage.

Baruch Sadogursky, a longtime developer advocate, puts it in brutally practical terms: "The code is absolutely disposable. It's garbage to begin with. No one even looked at it ever because we don't care. As long as the tests pass."[ANDev-009] If the code is disposable, the spec is the only thing that matters. Everything downstream is compilation.

## What a Good Spec Contains

A spec is not a PRD. A PRD is literature - a narrative document that describes what the product should feel like, why it matters, who it serves. Product managers write beautiful PRDs. They are poetry, as Sadogursky observes.[ANDev-009] And poetry is terrible input for a compiler.

A spec is a contract. It defines what the system must do in terms precise enough that a machine can verify compliance. The difference between a PRD and a spec is the difference between "the user should be able to find their favorite items easily" and "when a user clicks the heart icon on a product card, the system shall add that product to the user's favorites list and persist the selection across browser sessions."

A complete spec contains several categories of information, each serving a different verification purpose.

**Behavioral contracts** are the core. These define inputs, outputs, preconditions, postconditions, and invariants for each piece of functionality. A behavioral contract for a favorites feature might specify: given a logged-in user viewing a product, when the user clicks the favorite toggle, then the product appears in the user's favorites list, the heart icon changes to filled state, and the favorites count increments by one. The contract also specifies what must NOT happen: favoriting a product must not modify the cart, must not trigger a purchase flow, must not alter the product's public rating.

The intellectual foundation for this approach predates AI-native development by decades. Bertrand Meyer's Design by Contract, introduced in *Object-Oriented Software Construction* in 1997, established that preconditions, postconditions, and invariants could serve simultaneously as specification, documentation, and runtime validation.[Meyer-OOSC] Meyer's key insight was that a single artifact - the contract - eliminates the drift between what a system is supposed to do and what it actually does. In a factory context, this convergence is not just convenient, it is essential. When the spec, the documentation, and the runtime checks are the same artifact, agents cannot silently deviate from intent. The contract is not a description of the code; it is the constraint the code must satisfy, and violations are detectable automatically rather than through human inspection.

**Acceptance criteria in testable form** translate each behavioral contract into something a test runner can evaluate. "The system shall display a heart icon" is testable. "The experience should feel intuitive" is not. Every acceptance criterion in a good spec can be mechanically converted into at least one automated test.

The bridge between behavioral contracts and testable acceptance criteria has a name: Behaviour-Driven Development. Dan North introduced BDD in 2006 to solve a specific coaching problem - developers struggled with test-driven development because the word "test" made them think about implementation rather than behavior.[North-BDD] North's solution was the Given/When/Then format: Given a precondition, When an action occurs, Then an observable outcome follows. This format is directly usable as acceptance criteria that agents can verify programmatically. A spec line reading "Given a logged-in user, When they click the heart icon, Then the product appears in their favorites list" is both a human-readable behavioral description and a machine-parseable test skeleton. For factory specs, the Given/When/Then structure does double duty - it communicates intent to the human reviewer and provides the acceptance test structure the agent needs to validate its own implementation.

**Interface definitions** specify how this feature connects to the rest of the system. What API endpoints does it expose? What events does it emit? What data does it consume from other services? Interface definitions are the contracts between components, and they tend to be the most stable layer of a spec because changing them requires coordinating with everything downstream.

**Data model changes** describe what new entities, fields, or relationships this feature introduces.

**Edge cases and error conditions** cover the scenarios that a vibe-coded prototype would silently ignore. What happens when the user favorites an item that gets deleted from the catalog? When the favorites list exceeds storage limits? When the persistence layer is temporarily unavailable? These cases separate production software from demos.

**Non-functional requirements** are the hardest category to formalize, and the one most likely to be forgotten entirely. Sadogursky is blunt about the challenge: "Cross non-functional concerns are hard to express as behavior. Security constraints, performance requirements - it's impossible to express in given-when-then. Because the whole idea of behavioral driven development is to express behavior."[ANDev-009]

But "hard to express" is not the same as "impossible to test." A performance requirement like "the favorites endpoint responds in under 200ms at the 95th percentile under 1,000 concurrent users" is perfectly testable - you just need a load testing framework rather than a unit test runner. A security requirement like "only authenticated users can modify favorites lists" is testable through authorization checks. A compliance requirement like "user favorites data must be deletable within 30 days of a GDPR erasure request" is testable through an end-to-end data lifecycle verification.

The trick is encoding these requirements in a format that connects to automated verification. Rene Brandel, the inventor of Kiro[Kiro] and now founder of the security testing company Casco, recommends a pragmatic approach: "Have a little access-control.md file as part of your stack somewhere. Just say, here are the different roles that exist, this is what these roles are supposed to do. Something very simple as that immediately adds so much semantic context into the code that gets generated."[ANDev-029] Non-functional requirements do not need the same format as behavioral specs. They need to be captured, testable, and discoverable by agents - even if they live in separate context files rather than inline with the behavioral spec.

### Example: A Complete Spec

The favorites feature used throughout this section looks like this when fully formalized. This example combines behavioral contracts, acceptance criteria in Given/When/Then form, interface definitions, data model changes, edge cases, and non-functional requirements into a single document.

```markdown
# Feature: Product Favorites

## Behavioral Requirements (EARS)

- When a logged-in user clicks the heart icon on a product card,
  the system shall add that product to the user's favorites list
  and persist the selection across sessions.

- When a logged-in user clicks the heart icon on an already-favorited
  product, the system shall remove that product from the favorites list.

- While a user is not authenticated, the system shall display the
  heart icon in a disabled state and shall not allow favorite actions.

- The system shall not modify the shopping cart, trigger a purchase
  flow, or alter a product's public rating as a side effect of
  favoriting or unfavoriting.

## Acceptance Criteria

Scenario: Adding a favorite
  Given a logged-in user viewing a product card
  When the user clicks the heart icon
  Then the product appears in the user's favorites list
  And the heart icon changes to filled state
  And the favorites count increments by one

Scenario: Removing a favorite
  Given a logged-in user viewing a favorited product
  When the user clicks the filled heart icon
  Then the product is removed from the favorites list
  And the heart icon changes to outline state
  And the favorites count decrements by one

Scenario: Unauthenticated user
  Given a user who is not logged in
  When the user views a product card
  Then the heart icon is visible but disabled
  And clicking the heart icon has no effect

## Interface

POST   /api/v1/favorites         - Add a product to favorites
DELETE /api/v1/favorites/{id}    - Remove a product from favorites
GET    /api/v1/favorites         - List user's favorites (paginated)

All endpoints require authentication. Responses follow the existing
API envelope format (data, meta, errors).

Events emitted:
- product.favorited   { user_id, product_id, timestamp }
- product.unfavorited { user_id, product_id, timestamp }

## Data Model

New table: user_favorites
- id:         UUID (primary key)
- user_id:    UUID (foreign key -> users.id, indexed)
- product_id: UUID (foreign key -> products.id, indexed)
- created_at: timestamp
- Unique constraint on (user_id, product_id)

## Edge Cases

- User favorites a product that is subsequently deleted from the
  catalog: the favorite entry remains but the product card displays
  "No longer available." The entry is removable.

- User has reached the favorites list storage limit (1,000 items):
  the system returns a 422 with message "Favorites limit reached"
  and does not add the item.

- Persistence layer temporarily unavailable: the system returns a
  503, does not update the UI optimistically, and logs the failure
  for retry.

## Non-Functional Requirements

- The GET /api/v1/favorites endpoint responds in under 200ms at
  P95 under 1,000 concurrent users.

- Only authenticated users can read or modify their own favorites.
  No user can access another user's favorites list.

- User favorites data is deletable within 30 days of a GDPR
  erasure request.
```

This is one feature, roughly 80 lines. A real production spec contains more - migration scripts, rollback procedures, monitoring additions - but the structure holds. Every line is either testable by a machine or reviewable by a human. Nothing requires interpretation.

## Three Levels of Spec Rigor

Not every team needs the same relationship between specs and code. The industry is converging on three distinct levels, each with different trade-offs in cost, flexibility, and reliability.

### Spec-First

Spec-first is the conservative approach: write the spec, review it, approve it, then hand it to agents for implementation. The spec exists before any code is written, and the implementation must satisfy the spec. This is the methodology that most closely mirrors traditional software engineering practices, just with agents replacing human developers in the implementation phase.

The advantage is predictability. You know exactly what the system is supposed to do before any code exists. The spec serves as a shared reference for product managers, engineers, and agents. Changes flow from spec updates, not from ad hoc conversations with agents.

The disadvantage is speed. Spec-first requires upfront investment in spec quality before you see any running software. For teams accustomed to the rapid feedback of vibe coding, this feels like a regression. Cian Clarke, Head of AI at NearForm, measured the gap: "What used to be seeing outputs in 20 minutes to an hour" becomes "outputs at the end of a five, six hour documentation session." But he also measured the quality difference: two days of spec authoring produced software that "would have taken me a month to produce otherwise, and was probably better code than I would have written. A repository with linted code that had two, three, 400 unit tests, automation tests, an architecturally separate front end, the backend infrastructure as code."[ANDev-034]

Spec-first is the right choice when the cost of rework exceeds the cost of specification. For production features in regulated industries, for systems that need audit trails, for any feature where "we'll fix it later" means "we'll pay ten times more later" - spec-first pays for itself immediately.

### Spec-Anchored

Spec-anchored is the pragmatic middle ground. The spec and code are developed together, with the spec serving as reference rather than rigid prerequisite. You might write a rough spec, generate some code, realize the spec missed an edge case, update the spec, regenerate. The spec is the anchor - the thing you return to when you need to verify intent - but it does not block implementation.

This is where most teams are landing in practice. Kiro's workflow embodies this approach: requirements lead to design leads to task decomposition, but at any point you can edit the spec, inject new requirements, or even switch to vibe mode for targeted changes. Richard Threlkeld, an engineer on the Kiro team, explains the philosophy: "Sometimes you actually have more domain knowledge than what you can encode in a document. When tools try to put rigid structures in place - you can't do this or go down this path - it actually ends up compounding and having a lot of friction for customers."[ANDev-016]

The risk of spec-anchored development is spec drift. As code evolves through a mix of spec-driven and vibe-driven changes, the spec can fall out of sync with reality. Threlkeld compares the lifecycle of specs to comments in code: "If you put comments in code at that point in time, it's temporal and they will hold as people and teams edit them over time. They can drift."[ANDev-016] Managing that drift is a team discipline problem, not a tooling problem - at least for now.

### Spec-as-Source

Spec-as-source is the most radical position: the spec is the only source of truth, and the code is a disposable build artifact. Throw away the code, regenerate from the spec, and you should get functionally equivalent software. The code is not maintained, not refactored, not debugged. It is compiled from the spec, validated against tests, and deployed. When requirements change, you update the spec and recompile.

This is the destination that Chad Fowler's Phoenix Architecture points toward. Fowler, a VC at Blue Yard Capital with a deep technical background including CTO stints at Wunderlist and Microsoft, has been writing about regenerative software for years. His thesis is simple: "Any software in the system you should think about like it's a build artifact. The top level asset is some sort of specification for the system. The code you should think about is just an implementation detail."[ANDev-047]

Spec-as-source is not mainstream practice today. It requires a level of spec completeness and a modular architecture that most existing systems lack. But for greenfield projects with well-bounded scope, it is already working. Fowler himself practices it: "On my IRC system, I will go through runs where I have it just look for all the possible edge cases we might not have thought of for a certain class of bugs. And I get multiple models, multiple times to do this. Then I review it and I have it create tests that discover bugs. And then I have it work until the tests run all the time."[ANDev-047]

The three levels are not a maturity model where everyone should aspire to spec-as-source. They are a trade-off spectrum. Spec-first optimizes for predictability. Spec-anchored optimizes for iteration speed. Spec-as-source optimizes for replaceability. Your choice depends on what you are building, who is building it, and how much you trust your spec to capture the full intent.

## Phoenix Architecture and the Disposable Code Thesis

Fowler's Phoenix Architecture deserves special attention because it represents the most complete articulation of where spec formalization leads when taken to its logical conclusion.

The core insight draws from immutable infrastructure. In the 2000s, sysadmins were proud of servers with two-year uptimes. Then containers arrived, and the industry learned that the path to reliability was not preserving servers but destroying and rebuilding them constantly. If change is hard, do it all the time until it is not.

Fowler applies the same logic to code. At Wunderlist, he enforced a rule: "You can do code in any language you want as long as it's no more than this big" - roughly a page of code in an editor. With consistent calling conventions and bounded scope, components became genuinely replaceable. When a Haskell service could no longer be recompiled because the toolchain had rotted underneath it, someone rewrote it in Go in an afternoon and deployed it. When Wunderlist shipped a major release running on hundreds of expensive Ruby on Rails servers, the team replaced 70% of the codebase with Clojure, Go, and Rust over three months, cutting hosting costs to 25% of the launch baseline.[ANDev-047]

The Phoenix Architecture codifies this for the AI era. Code is generated from specs, validated against tests, and deployed. When requirements change, code is regenerated, not patched. The system survives because its shape is defined by interfaces and calling conventions, not by code inside any component. Fowler calls this "pace layers" - interfaces change slowly, implementations change fast, data schemas sit in between.[ANDev-047]

> **Case Study: The Intent Integrity Chain**
>
> Baruch Sadogursky describes what he calls the "intent integrity chain" - a verification pipeline that guarantees human intent survives all the way from idea to deployed code.[ANDev-009] The chain works in stages: human intent is captured in a prompt or software definition document. AI generates structured specs (in Gherkin or a similar format) from that intent. Humans review the specs because they are readable - "in your language, there are hundreds of translations of Gherkin spec, you can read it in Urdu if you feel like." The reviewed specs are compiled deterministically into tests - no AI involved in this step, because "if you run it 10 times you'll get the same thing 10 times." Then agents generate code until the tests pass. The tests are protected as read-only artifacts so agents cannot modify them to cheat.
>
> The critical property is that the spec-to-test step is deterministic. Sadogursky is emphatic about this: "We don't need a monkey. We take an algorithm and compile the specs into tests deterministically, every time." This removes the stochastic element precisely where trustworthiness matters most. The chain does use AI at two points - generating specs from intent and generating code from tests - but both of those AI steps are bounded by human-reviewable artifacts. You review the specs. You validate through tests. The monkey types on the typewriter, but the monkey never decides what Shakespeare is supposed to say.
>
> The model has a clear limitation: behavioral specs cannot capture non-functional requirements like security constraints or performance targets. Sadogursky acknowledges this openly. But the chain itself does not depend on Gherkin or any specific spec format. "The intent integrity chain doesn't change. You only have a better tool in this part when you need to go from spec to code. Everything else remains the same."

The Phoenix Architecture adds another layer to this chain: the code is never maintained. It is always regenerated. This means the spec does not merely describe the system - it IS the system, in the same way that source code IS the program. Everything below the spec is compilation output.

## Shadow Specs: The Hidden Debt of Autonomous Agents

There is a dark side to autonomous code generation that most spec-driven methodologies do not adequately address: shadow specs.

When an agent implements a feature from a spec, it makes hundreds of decisions the spec does not cover. Which HTTP client library to use. How to structure error retry logic. Whether to use optimistic or pessimistic locking. How to handle timezone conversions. Each of these decisions is an implicit specification - a choice that shapes system behavior without anyone explicitly approving it.

Guy Podjarny[ANDev-030], CEO of Tessl, coined the term and defines three layers of human blessing in agent-generated systems:

1. **Explicit instruction** - the human directly specified this behavior.
2. **Explicit review** - the human read this and said yes (though "did you really read it? I don't know").
3. **No human interaction** - the agent decided this on its own.

The third layer is the shadow spec. Fowler encountered it firsthand: "On my IRC system, I actually have two parallel web apps by accident. I have a really nice one that I've been iterating with and then the one that the agents just decided they were going to make. And it's linked some places. So I have to remove it. But at least I know in this case that I made this decision."[ANDev-047]

The problem with shadow specs is that they accumulate. Each individual shadow decision seems harmless. The agent picked React instead of Vue? Fine, both work. The agent chose JWT for auth tokens? Reasonable default. The agent structured the database with denormalized tables for read performance? That is a significant architectural decision masquerading as an implementation detail.

Over time, these shadow decisions form a coherent but implicit architecture that may conflict with the explicit spec. The explicit spec says "the system shall support multi-tenant data isolation." The shadow spec implemented single-tenant patterns throughout because that was simpler for each individual task. Nobody noticed because nobody reviewed the shadow layer.

Fowler's Phoenix Architecture addresses shadow specs through regeneration - since code is constantly rebuilt, shadow decisions do not accumulate. For teams not practicing full regeneration, Fowler is working on hash-based intent tracking: "You can do hash-based tracking of these intents all the way through, like cryptographic hashes, which gives you that build system thing. But it also gives the ability to add provenance."[ANDev-047]

Until such tooling matures, the practical defense is straightforward: constrain the surface area where agents make autonomous decisions. Use steering files to specify library choices. Use architectural decision records to lock patterns. Use locked tests to enforce invariants. The more explicit you make the decisions that would otherwise be shadows, the less hidden debt you accumulate.

Qodo's 2025 State of AI Code Quality report provides empirical support for this approach: developers cite context gaps more often than hallucinations as the primary cause of poor AI-generated code quality.[Qodo-2025] This finding reframes the problem. The popular narrative treats hallucination as the core risk of AI code generation - the agent inventing APIs that do not exist or libraries that were never imported. But the more common failure is the agent making reasonable decisions based on incomplete information. It does not hallucinate; it fills gaps with plausible defaults that happen to be wrong for your system. Better specs - more complete context about architectural choices, library preferences, and design constraints - are the primary intervention against shadow specs. The spec is not just telling the agent what to build. It is telling the agent what decisions have already been made so it does not make them again, differently.

## Spec Formats and Trade-offs

The question of how to format a spec is not purely aesthetic. The format determines what machines can verify, what humans can review, and how efficiently the spec fits in a context window.

### EARS (Easy Approach to Requirements Syntax)

EARS[Mavin-EARS] is the format Kiro chose for its requirements layer. It uses structured natural language templates: "When [trigger], the system shall [behavior]" for event-driven requirements, "While [state], the system shall [behavior]" for state-driven ones, and unconditional "The system shall [behavior]" for invariants.

Threlkeld explains why EARS is more than a readability convention: "This wasn't just a clever thing that we figured out with auto formalization. It's actually an extension of temporal logic, which is an extension of first order logic. So this gives us a lot of power behind the scenes on being able to control what the model does, how we verify certain parts of the process."[ANDev-016]

The temporal logic foundation means EARS requirements can be mechanically checked for properties like logical consistency, completeness, and contradiction - something that freeform requirements cannot support. If one requirement says "when the user submits a form, the system shall send a confirmation email" and another says "the system shall never send automated emails to unverified addresses," a temporal logic checker can flag the conflict. A human reading freeform paragraphs might miss it entirely.

EARS is not a toy notation invented for demos. Mavin et al. developed and validated the syntax at Rolls-Royce for aero engine control systems - safety-critical software where ambiguous requirements can have catastrophic consequences.[Mavin-EARS] Their IEEE RE 2009 paper identifies eight common problems in natural-language requirements (ambiguity, vagueness, complexity, omission, duplication, wordiness, inappropriate implementation, and untestability) and shows how five EARS templates using keywords (While, When, Where, If/Then, and unconditional "shall") systematically address each one. The industrial validation matters because it demonstrates that constrained natural language can work at the level of rigor required by aerospace certification, not just agile user stories.

The trade-off is rigidity. EARS templates constrain expression. Some requirements do not fit naturally into when-while-shall patterns, and forcing them creates awkward contortions that are technically parseable but humanly unreadable.

### The SpecKit Triplet

GitHub's open-source SpecKit[SpecKit] format uses a three-document structure: `requirements.md` for what the system should do, `design.md` for how it should be built, and `tasks.md` for the implementation plan. Each document serves a different audience and a different stage of the pipeline.

This triplet maps directly to how most software teams already think. Product managers own requirements. Technical leads own design. Engineers own tasks. The format's strength is familiarity - there is virtually no learning curve for teams that already write PRDs and technical design documents. Its weakness is the gap between documents. Requirements and design can drift out of sync, and there is no formal mechanism to detect when they do.

### BMAD (Build More Architect Dream)

BMAD is an open-source framework now on its sixth version, created by Brian Madsen[BMAD] and maintained by a growing community of contributors. Clarke describes it as "really intelligent context engineering" and "the best approximation we have right now of what a comprehensive spec-driven workflow looks like."[ANDev-034]

BMAD's distinctive features are document sharding and role modules. Sharding splits large specification documents so that only relevant sections are loaded into the context window for a given task. A 15,000-word PRD does not need to be in context when the agent is implementing a database migration - only the data model section does. This directly addresses the context saturation problem described in Chapter 3.

Role modules let teams configure different agent personas for different stages. An architect agent generates the system design. A frontend engineer agent implements the UI. A QA agent writes tests. Each role loads different subsets of the spec and different behavioral instructions. This solves a real problem that Clarke identified in consultancy work: existing spec-driven tools assume a single full-stack developer, but real teams have specialists. "We need to better solve for that collaboration piece. The limitation is purely technical. It is that right now we are mixing the work of the backend and the frontend engineer in our decomposed task lists."[ANDev-034]

V6 also introduced project scale selection, letting teams right-size the spec overhead for the project at hand. A rapid prototype does not need the same spec depth as a production microservice.

### Tessl's Context-Engineering-First Approach

Tessl takes a fundamentally different position. Rather than prescribing a spec format, Tessl focuses on building, testing, and distributing the context that makes agents effective - treating the agent's instructions as the primary artifact rather than the system's specification.

Podjarny articulates the distinction: instead of speccing the program, you are speccing the programmer.[ANDev-030] The same spec given to different models produces different results because Opus is creative but sometimes ignores instructions, while smaller models follow instructions more literally but lack judgment. The implication is that the spec alone is insufficient - you also need evaluations that verify the agent's decision-making behavior, not just the system's functional behavior.

This approach is less about a specific spec format and more about the lifecycle of the instructions that surround the spec: how you author them, how you test them against different models, how you distribute them across teams, and how you maintain them as models evolve.

### Plain Markdown with Conventions

The lowest-barrier approach: write your spec in markdown with team conventions for structure. This is what most teams start with, and it works surprisingly well for small projects. The problem is scale. Without formal structure, specs grow organically, conventions drift between authors, and there is no tooling for contradiction detection or automated test generation. Plain markdown is where you start. It is rarely where production teams stay.

### Choosing a Format

The decision matrix comes down to three axes.

**Formality versus accessibility.** EARS and formal methods give you verification power but raise the barrier to participation. Plain markdown lets anyone contribute but gives you nothing to verify against. Most teams land somewhere in the middle - structured enough that machines can parse intent, informal enough that product managers will actually write and review the document.

**Single document versus multi-document versus sharding.** A single spec file is simple but creates context window pressure for large features. Multi-document approaches (like SpecKit's triplet) distribute the load but introduce synchronization problems. Sharding (like BMAD's approach) solves both but adds framework complexity.

**Agent-coupled versus agent-agnostic.** Kiro's EARS integration gives you deep tooling but locks you to Kiro. BMAD works across IDEs and model providers. Plain markdown works everywhere. The more coupled the format is to specific tooling, the better the tooling experience and the higher the switching cost.

> **Case Study: Spec-Driven Development as a Revelation**
>
> Cian Clarke at NearForm is a self-described "vibe coding skeptic."[ANDev-034] His consultancy delivers software to enterprises using teams of senior engineers - the average experience in the company runs about eight years. These are not people looking for shortcuts. They are looking for quality at speed.
>
> Clarke discovered spec-driven development through NearForm's Ignite discovery process[NearForm-Ignite], where stakeholders align on requirements before engineering begins. His team noticed that AI note-takers in these sessions could distill meeting transcripts into requirements documents, which could then feed directly into structured spec frameworks. A team member named James discovered BMAD and connected the artifacts.
>
> The revelation for Clarke was not the concept - it was the output quality. Two days of spec authoring produced a repository that would have taken a month to build by hand: linted code, hundreds of unit and automation tests, separated front-end and back-end, infrastructure as code. "As a pretty vibe coding skeptic, this was a revelation for me because all of a sudden you're actually able to steer what the model did."
>
> NearForm has since rolled BMAD out as their default methodology for greenfield AI-native projects. The biggest remaining challenge is scaling it beyond individual contributors: "How do you scale a spec-driven framework to an entire team of developers rather than an individual contributor that is taking on the role of DevOps plus front-end engineer plus back-end engineer?" They are solving this by codifying team roles within BMAD's module system and syncing generated backlogs with issue management systems like GitHub Issues, allowing the spec-driven workflow to drive parallel work across a team.

## How the Machine Does Translation

The mechanics of spec formalization follow a pattern that varies in implementation but is consistent in structure across tools.

**Step 1: Ingest intent.** The machine receives human intent in whatever form it arrives - a prompt, a PRD, a meeting transcript, a Jira ticket description. The richer the input, the fewer gaps the machine needs to fill with assumptions.

**Step 2: Analyze codebase context.** Before generating any spec, the machine reads the existing codebase to understand current architecture, patterns, and constraints. This step is what separates spec generation from a generic "write me requirements" prompt - the machine grounds its output in what already exists.

**Step 3: Generate structured spec.** The machine produces a spec in whatever format the framework prescribes. The quality of this generation depends heavily on the quality of the input and context. Brandel's multiplication principle applies here with devastating force: "If you have one bad line of a user story or a specification when you first research what you're supposed to be doing, that will lead to a thousand bad lines of design. And a thousand bad lines of design will lead to a million bad lines of code."[ANDev-029]

**Step 4: Clarification loop (optional but recommended).** The machine identifies ambiguities, missing edge cases, and potential conflicts in its own output and asks the human to resolve them. Brandel recommends actively soliciting this: "Ask Claude, hey, what am I missing in this specification? And then you'll realize there are some questions here that are super relevant when you're actually going down the implementation route that you forgot to ask yourself."[ANDev-029]

This step is where spec formalization diverges most sharply from vibe coding. In vibe coding, the LLM says "yes, you're absolutely right" and builds whatever you asked for. In spec formalization, the LLM asks hard questions because the spec is the wrong place to be agreeable. Brandel puts it directly: "The people that only agree with you are not going to be the most productive to the ultimate outcome you're trying to drive. You actually want to be asked the hard questions."[ANDev-029]

**Step 5: Human review and approval.** The human reads the spec and either approves it, modifies it, or sends it back for another pass. This is the critical control point. Sadogursky argues that spec review is fundamentally different from code review because specs are readable by everyone at the table - product managers, business stakeholders, engineers, even customers. "Coming back to the biggest benefit of the spec - because it is readable, we can actually review it. Spec is different because it's readable, in your language."[ANDev-009]

## Spec-to-Test Traceability: An Honest Assessment

One of the most appealing promises of spec-driven development is bidirectional traceability between specs and tests. Change a spec, and the tests update. Discover a failing test, and trace it back to the spec clause that it validates. In theory, this creates a closed loop where spec, tests, and code are always in sync.

In practice, this is largely an unsolved problem.

Brandel is the person best positioned to assess this - he built Kiro and tried to implement this exact feature. His verdict is sobering: "We tried basically aligning up specifications to tests, to end-to-end tests. Effectively, every single spec just maps to an end-to-end test. This bidirectional sync, while it is an aspirationally good idea, and I think looks really cool on paper and on demos, it was actually not practically implementable."[ANDev-029]

The obstacles are both technical and semantic. Language is unbounded - one spec clause can map to multiple tests, multiple spec clauses can share a test, and specifications can overlap or conflict in ways that are obvious to humans but invisible to automated mapping systems. Brandel explains: "One person might say, this functionality should perform user invite flows with admins only. And another spec says, no, it should only provide user invite flows with members only. And so there's conflicts, there's a lot of these different problems."[ANDev-029]

What IS achievable today:

- **One-directional test generation.** Generate tests from specs, then lock them. This is Sadogursky's intent integrity chain - deterministic compilation from spec to test, with no reverse path needed.
- **Requirements tracing through tags.** Kiro tags implementation tasks with the requirement IDs they satisfy, giving you forward traceability from spec to code without the complexity of maintaining backward links.
- **Human-verified traceability.** A human reviews the spec, reviews the tests, and verifies that they correspond. This is manual and does not scale, but it is honest about what it is.

The industry will likely solve bidirectional sync eventually. But any vendor claiming they have solved it today is either working on a very narrow domain or overstating their capabilities.

> **Case Study: Kiro's Iterative Spec Workflow**
>
> The Kiro team tried three approaches before landing on their current spec workflow. First, they tried forcing every spec through a TDD flow - write tests from requirements, then generate code until tests pass. "From our early tests, we found that that generally worked pretty well," Nikhil Swaminathan[ANDev-016] recalls, "but then when actually putting that in front of users and customers, it was not typically how they were working. TDD is great. People follow it, but a lot of users were just not doing that."
>
> Second, they tried generating specs for existing code - right-click a folder, generate a specification for what is in there. Users found it interesting but could not action on it. "It was like generating information about what's there, but that's kind of like what we have with steering. How do I actually action on this and build something new?"
>
> The approach that worked was requirements-design-tasks, grounded in codebase analysis. Start with a user prompt ("add favorites"). Generate requirements in EARS format. Generate a design document that incorporates existing architecture. Decompose into ordered implementation tasks. At each stage, the user can edit, add, remove, and iterate. Swaminathan demonstrates this live: he adds a requirement, removes one ("I don't really care about the count indicator"), refines the acceptance criteria, and moves forward when satisfied.
>
> The design phase is where Kiro reads the existing codebase to determine patterns: existing state management, component structures, data models. The implementation plan that follows is grounded in reality rather than imagined from scratch. Combined with steering files and hooks (automated triggers that enforce conventions on every code change), the workflow produces spec-driven code with continuous quality enforcement.

## The Spec Is the Per-Feature Source of Truth

All of these formats, frameworks, and tools converge on one foundational claim: the spec is the per-feature source of truth. Not the code. Not the tests. Not the PR description. The spec.

This is a significant departure from how most software teams operate today, where the code is the source of truth and everything else - documentation, tickets, design docs - is downstream commentary that may or may not be current. In spec-driven development, the relationship inverts. The spec is upstream. The code is downstream. If the spec and the code disagree, the spec is right and the code needs to be regenerated.

Sadogursky captures the full chain: "We start with the prompt. We have the spec - this is your source of truth. Because it's still readable by all the humans. We can agree on it and iterate on it. And we evolve it as we've seen fit - replace it, edit it, regenerate it. But in the end of the day, what we all agree upon will be the spec."[ANDev-009]

Clarke's team at NearForm sees the same pattern playing out in practice: the spec-as-truth model works immediately for greenfield projects and is slowly becoming viable for brownfield ones as the tooling matures. "I think as the frameworks evolve, we will end up more in a world of spec as source where the really important artifact is the spec, cascading all the way back to the product requirements document."[ANDev-034]

This has an important organizational consequence. If the spec is the source of truth, spec authorship and review become the highest-leverage activities in the development process. The person who writes the spec has more influence over the final product than the person (or agent) who writes the code.

Brandel's multiplication effect makes this concrete: one good line of spec leads to a thousand good lines of design and a million good lines of code. One bad line of spec leads to the same multiplied failure.[ANDev-029]

## Tooling Summary

The practical landscape: **Kiro** for integrated, opinionated spec workflows with native EARS; **BMAD** for open-source flexibility with document sharding and role modules; **SpecKit** for familiar three-document structure with minimal overhead; **Tessl** for context engineering across teams and harnesses; and **custom prompt chains** for organizations with strong opinions and engineering capacity.

Most mature teams will combine elements. The framework wars matter far less than the practice. Any structured approach to capturing intent before code generation is dramatically better than none. The spec does not have to be perfect. It has to exist.

## What Comes Next

Spec formalization is stage one of the factory's production work. The spec exists. It has been reviewed. It defines what the system should do in testable terms.

The next stage is harder: taking that spec and producing code that actually satisfies it - reliably, at scale, without requiring a human to verify every line. That is the code generation problem, and it is where the factory either proves its value or reveals its limitations.

But notice what spec formalization has already accomplished. The human wrote a sentence: "add favorites." The machine produced behavioral contracts, acceptance criteria, interface definitions, data models, edge cases, and error handling strategies. It asked clarifying questions. It checked for contradictions. It grounded the design in the existing codebase. And it produced all of this in a format that both humans and machines can read, review, and verify.

The monkey is ready to start typing. But now the monkey has a spec, and the spec has teeth.

---
