# Chapter 7: Spec Review and Approval: The First Human Gate

A wrong spec costs ten times more than wrong code.

This is not a metaphor. When a machine-generated spec misinterprets business intent - conflating "favorites" with "bookmarks," missing a persistence requirement, assuming a feature is user-scoped when the business wanted it organization-scoped - every downstream artifact amplifies the error. The agent writes code that faithfully implements the wrong thing. Tests pass because they validate the wrong behavior. Code review approves because the implementation matches the spec. The mistake surfaces weeks later in production, or worse, in a customer complaint.

The spec review is where this cascade gets cut. It is the highest-leverage review in the entire pipeline, and it is the one most teams spend the least time thinking about.

## Why Spec Review Is Different from Code Review

Code review asks: "Is this implementation correct?" Spec review asks a harder question: "Are we building the right thing?"

The distinction matters because the two reviews require fundamentally different skills. Code review is pattern matching against known good practices: correct error handling, proper resource cleanup, adherence to the type system. An experienced engineer can review code in a language they have not written in years and still catch most defects. The review is grounded in implementation primitives that transfer across domains.

Spec review has no such primitives. It requires understanding the business domain, the user's mental model, the organizational context, and the existing system's behavior. A behavioral statement like "when a customer views a product card, the system shall display a heart icon" looks perfectly reasonable in isolation. Whether it is correct depends on questions the spec cannot answer by itself: Does the business want the heart icon to indicate personal favorites or social proof? Should it appear for logged-out users? Does it conflict with the wishlist feature another team shipped last quarter?

Research on code review confirms something practitioners have long suspected: review's primary value is not bug-finding. Bacchelli and Bird's study of code review at Microsoft, presented at ICSE 2013, found that reviewers deliver more value through knowledge transfer, team awareness, and shared understanding than through defect detection.[Bacchelli-2013] If this is true for code review - where defect detection seems like the obvious goal - the implication for spec review is even stronger. Spec review's primary value is not catching errors in the specification, though it does that. Its primary value is building shared understanding of intent across the team. When a product manager, an architect, and a domain expert all review the same spec, they leave with a common mental model of what the system will do. That shared understanding prevents an entire class of integration failures, miscommunications, and "I thought you meant..." conversations downstream.

This is precisely why spec review is more accessible than code review. You do not need to understand Python or React to evaluate whether a behavioral description matches business intent. A product manager, a designer, a domain expert - anyone who understands what the software is supposed to do can participate meaningfully in spec review. They cannot review code. They can absolutely review specs.

Cian Clarke at NearForm puts it directly: "If you are writing outputs purely for the consumption of a model, you're probably not really reviewing what it is that's been generated. If you're generating a PRD off of a transcript and just blindly accepting it, you've probably missed the purpose of spec driven development in the first place."[ANDev-034] The review is the point. Skip it, and you have added process without adding value.

## What to Look For

Spec review covers six dimensions. Most review failures happen because reviewers check only the first two and wave through the rest.

**Business intent alignment.** Does the spec capture what the stakeholder actually asked for? This is the most obvious check and the one most teams already do. But it is also where the subtlest errors hide, because AI-generated specs are fluent and confident. They read well even when they are wrong. A spec that plausibly describes a feature is not the same as a spec that accurately describes the feature the business needs. Reviewers must fight the tendency to skim past well-written text.

**Behavioral completeness.** Are all the edge cases covered? What happens when the list is empty? When the user is logged out? When the network fails mid-operation? Nikhil Swaminathan from the Kiro[Kiro] team illustrates this with a simple example: "With favorites, when I add something as a favorite, if a user can click and unclick it to unfavorite, right? Is there a count that needs to be displayed? If you actually start building out the feature, there's a lot of details and nuances that go into almost every feature you build."[ANDev-016] A spec that describes the happy path is a spec that is half-finished.

**Architectural fitness.** Does the proposed behavior fit the existing system architecture? A spec might correctly describe a feature but require a data model change that conflicts with an in-flight migration, or assume synchronous communication in a system that is event-driven. The architect's job in spec review is to catch these mismatches before the agent spends tokens implementing something that will need to be torn out.

**Interface correctness.** Does the spec describe interactions with other system components accurately? If the spec references an API endpoint, does that endpoint exist? If it proposes a new data type, is the naming consistent with the existing schema? Interface errors in specs are particularly expensive because they create integration defects that surface only when components are assembled.

**Non-functional requirements.** Are performance, security, and accessibility requirements stated in testable terms? "The system shall be fast" is not a requirement. "The favorites list shall load within 200ms for up to 1,000 items" is. Non-functional requirements that are not testable will not be tested, which means the agent will ignore them during implementation and validation.

**Scope discipline.** Research on code review at Microsoft, analyzing 1.5 million review comments, found that review quality degrades as the number of files under review increases. The more surface area a reviewer must cover, the less attention each piece receives. Reviewer expertise also matters: usefulness of review feedback plateaus roughly a year after a reviewer joins a project, suggesting that deep familiarity with a codebase yields diminishing returns beyond a certain point.[MS-CodeReview] Both findings translate directly to spec review. Keep specs focused - one feature, one behavioral domain - so reviewers can give concentrated attention. A spec covering three unrelated features will receive worse review feedback than three separate specs, even from the same reviewer. And rotate review assignments: a fresh pair of eyes on a spec catches assumptions that a long-tenured reviewer has internalized so deeply they no longer question them.

**Conflict detection.** Does this spec contradict any existing behavior or any other spec currently in the pipeline? This is the hardest dimension to evaluate because it requires knowledge of the full system and all concurrent work. Richard Threlkeld from the Kiro team describes the ambition: "Multiple people could view what you're going through here, even if you had 10, 15, 20 requirements, and compare these together to see if there's logical contradictions."[ANDev-016] Tooling is catching up to this need, but in mid-2026 it remains largely a manual check.

## Two Review Roles

Spec review is not a single activity performed by a single role. It decomposes into two distinct reviews that require different expertise and carry different authority.

### The Intent Author

The intent author is the person who originated the request: the product manager, business stakeholder, or domain expert who said "I need the system to do X." Their review validates a single question: did the AI correctly interpret what I asked for?

This review is accessible to non-engineers because specs describe behavior, not implementation. An EARS-format[Mavin-EARS] requirement like "when a customer views a product card, the system shall display a heart icon that toggles the item's favorite status" is readable by anyone who understands the product. The intent author does not need to evaluate whether the underlying data model is correct or whether the proposed state management approach is sound. They need to confirm that the described behavior matches their mental model of the feature.

The intent author also catches requirements that were never stated but were assumed. Clarke describes this gap precisely: "As engineers, if we had a gap in requirements documentation, we would go and ask a clarifying question of a product manager. The model just makes shit up."[ANDev-034] The spec review is where the intent author fills in the gaps the AI hallucinated over.

### The Technical Reviewer

The technical reviewer is typically a tech lead or architect. Their review validates a different set of questions: Is this implementable? Is it architecturally sound? Does it conflict with existing system behavior or in-flight work? Will it scale?

The technical reviewer reads the same spec as the intent author but sees different things. Where the intent author reads "the system shall persist favorites across browser sessions" and thinks "yes, that is what I wanted," the technical reviewer thinks "that implies server-side storage, which means a new database table, a new API endpoint, authentication changes, and GDPR implications for stored user preferences."

These two reviews can happen simultaneously or sequentially, but they cannot be skipped. A spec approved only by the intent author may be correct in intent but infeasible in execution. A spec approved only by the technical reviewer may be implementable but wrong. You need both.

## Collaborative Spec Authoring

Not all specs emerge from the machine and land on a reviewer's desk. Some of the most effective spec-driven workflows are collaborative from the start, with multiple stakeholders shaping the spec together before it ever reaches a formal review gate.

> **Case Study: NearForm's Ignite Process**[ANDev-034]
>
> Cian Clarke, Head of AI at NearForm, describes a collaborative discovery process called "Ignite"[NearForm-Ignite] that predates their adoption of AI-native development but maps naturally onto the spec-driven pipeline. In Ignite sessions, stakeholders - product managers, engineers, domain experts - gather to align on what they want to build. AI note-takers capture the conversation context, which is then distilled into requirements documents and playback decks.
>
> "We noticed that we could use things like AI note takers within the meeting to be able to capture a lot of that context and then distill it down into playback decks and also distill it down into requirements documents," Clarke explains. "It was the folk who were facilitating these sessions that observed that actually you can get really good requirements documentation and backlogs off the back of these meetings, just talking about how and what it is exactly that we want to build."
>
> The critical insight is that these sessions produce specs as a byproduct of alignment conversations that would have happened anyway. The specs are not an additional artifact that someone has to write; they are a structured capture of decisions that were already being made. This makes the subsequent review lighter because the stakeholders who will review the spec were present when it was authored. They are confirming what they remember agreeing to, not encountering someone else's interpretation for the first time.
>
> NearForm pairs this collaborative authoring with a framework called BMAD[BMAD] (Build More Architect Dream), an open-source spec-driven workflow that Clarke describes as "the best approximation we have right now of what a comprehensive spec driven workflow looks like." The combination of collaborative authoring with structured specification gives their teams both alignment and precision: stakeholders agree on what to build, then the framework ensures the agreement is expressed in terms an agent can execute on.

The factory should support both patterns. For routine features where the business intent is clear and the technical path is well-understood, a spec-then-review workflow is efficient: the AI generates a spec from captured intent, reviewers approve or modify it, and the pipeline continues. For complex or ambiguous features where the business intent itself is uncertain, collaborative authoring avoids the waste of generating and reviewing specs that are likely wrong.

The decision between the two patterns is a function of uncertainty. Low uncertainty in both business intent and technical approach favors spec-then-review. High uncertainty in either dimension favors collaborative authoring. Most teams develop an instinct for which pattern to use after a few iterations, though making it explicit in your process documentation helps new team members navigate the choice.

## Where Negotiation Happens

Specs are the meeting point between business intent and technical reality. Sometimes they collide.

A stakeholder wants real-time collaborative editing. The architect knows the existing system is built on a request-response model with no WebSocket infrastructure, and the timeline is two weeks. A stakeholder wants favorites to sync across devices. The technical reviewer knows this requires user accounts, and the product currently has no authentication system.

These conflicts must be resolved in the spec, not in the code. If negotiation is deferred to implementation, one of two things happens: the agent builds something that meets the spec but is architecturally unsound, or the implementing engineer quietly descopes the feature without the stakeholder's knowledge. Both outcomes are worse than a difficult conversation at spec review time.

Spec review is the cheapest place to have that conversation. No code has been written. No agent tokens have been spent. No tests need to be thrown away. The only cost is human time in discussion, and that discussion would have happened eventually, just at a point where changing direction is far more expensive.

Clarke frames the cost curve starkly: "Ambiguity at a minimum becomes some sort of hallucinated feature that the model has made up and potentially becomes masses of rework and wasted tokens. And ultimately real code smell in the repository as well."[ANDev-034] Requirements debt, as he calls it, is the new technical debt: the cost of incomplete or incorrect specs that propagate through the pipeline and create defects that are harder to trace because they look like implementation bugs but are actually specification bugs.

## Spec Review Workflows

Three workflow patterns have emerged for spec review in AI-native teams.

### Git-Based Review

Specs live in the repository alongside code, typically in a dedicated directory (Kiro[Kiro] uses `.kiro/specs/`, BMAD[BMAD] uses a configurable structure). Changes to specs flow through the same pull request process as code changes: create a branch, modify the spec, open a PR, request reviews from both the intent author and technical reviewer.

This workflow has the advantage of familiarity. Every engineer already knows how to use pull requests. The review interface supports inline comments, threaded discussions, and approval gates. Version history is automatic. The spec and the code it produces live in the same repository, making it possible to trace requirements through implementation.

The disadvantage is that non-engineers may not be comfortable in GitHub or GitLab. Product managers who live in Jira or Notion may resist reviewing markdown files through a pull request interface. This is a tooling gap, not a fundamental problem - the content is readable, just the delivery mechanism is unfamiliar. Some teams bridge this gap with preview links that render the markdown spec in a readable web view, or with integrations that post spec summaries to the tools non-engineers already use.

### Collaborative Editing

Specs are authored and reviewed in a shared document, with multiple stakeholders editing simultaneously. The finished spec is then committed to the repository for the pipeline to consume. Google Docs, Notion, or similar tools serve as the authoring surface; git serves as the system of record.

This pattern works well for the collaborative authoring model described above, where the spec emerges from a group discussion. It is less effective for reviewing machine-generated specs, where the value lies in careful reading and critique rather than co-authoring.

### Approval Gates in the Pipeline

Some tools build spec approval directly into the development workflow. Kiro's spec workflow includes explicit transition points between requirements, design, and task phases, with the expectation that a human reviews and approves before the agent proceeds. The Kiro team internally dogfoods this pattern: "We're trying to take the requirements and design, generate them within the code base, and then take those as artifacts and sit with the team and decide whether those look good or not,"[ANDev-016] as Swaminathan describes their process.

BMAD[BMAD] implements approval through its workflow stages, where the transition from spec authoring to backlog decomposition serves as an implicit review gate. Teams can make this gate explicit by requiring a manual commit or approval step before the agent begins implementation.

The choice between these workflows depends on team composition and existing tooling. A team of engineers comfortable with GitHub will find git-based review natural. A team that includes non-technical stakeholders may need collaborative editing or an approval gate with a friendlier interface.

## The Right Level of Formality

Not every spec needs the same level of review. A fix for a button alignment bug does not require an architecture review, and a new authentication system should not be reviewed by a single engineer in an async PR.

The decision matrix has two axes: scope of change and reversibility.

The evidence favors lightweight processes for most review work. Cohen et al.'s study at Cisco, analyzing 2,500 code reviews across 3.2 million lines of code, found that lightweight reviews were seven times faster than formal inspections while catching a comparable density of defects.[Cohen-review] The same economics apply to spec review. Heavyweight review ceremonies - scheduled meetings, multiple sign-off rounds, formal inspection checklists - are justified only for high-risk specs. For routine feature work, a focused checklist and one or two async reviewers catch the defects that matter without creating a bottleneck that slows the factory to human meeting-scheduling speed.

**Lightweight review (single approver, async):** Small features, bug fixes, and changes to existing behavior that are easily reversible. One reviewer with domain knowledge approves through the standard PR process. Turnaround: hours.

**Standard review (two approvers, async):** New features that touch multiple components or introduce new behavioral contracts. Both an intent author and a technical reviewer approve. Reviewers have 24-48 hours to respond. Most feature work falls here.

**Formal review (multiple approvers, synchronous):** Large features, architectural changes, or anything that affects multiple teams. Requires a synchronous meeting where stakeholders discuss the spec together. The Ignite-style collaborative session is one format; a traditional design review meeting is another. Turnaround: scheduled within the sprint.

Approval authority follows scope. An individual contributor can approve a spec that affects only their component. A tech lead approves specs that affect their team's domain. An architect or principal engineer approves specs that cross team boundaries or change shared infrastructure.

These levels should be codified in your factory's process documentation, not left to judgment. Without explicit guidance, teams default to either too little review (rubber-stamping everything) or too much (requiring architecture review for CSS changes). Both waste time; only one is dangerous.

## Specs as Testable Artifacts

One of the most productive shifts in spec review comes from reading each behavioral statement as a test case.

An EARS-format[Mavin-EARS] requirement like "when the favorites list is empty, the system shall display an appropriate empty state" is simultaneously a feature description and a test specification. A reviewer who reads it as a test immediately asks: What does "appropriate" mean? Is it an illustration, a text message, or both? What does the empty state say? Is there a call to action?

Clarke observes this dual nature explicitly: "That requirements writing style - EARS - is setting you up quite nicely for a specification of what a test to subsequently validate that requirement would be. Actually getting a succinct statement of what that requirement is and being able to use it as a testable artifact is highly valuable."[ANDev-034]

This means spec reviewers should ask of every behavioral statement: can this be tested automatically? If not, the requirement is either too vague to implement or too vague to validate. Either way, it needs refinement before leaving the review gate. Vague specs produce vague tests, which produce false confidence in code that may not do what anyone intended.

> **Case Study: Kiro's Internal Dogfooding**[ANDev-016]
>
> The Kiro team at AWS uses their own spec-driven workflow internally, treating the process as both product development and product validation. Nikhil Swaminathan describes the practice: "We have PMs owning the requirements, engineering owning design. How do we put them in places where they're easy to share?" The team generates requirements and design specs within the codebase, then reviews them collaboratively before implementation begins.
>
> Their internal experience surfaced a key finding about review friction. Early iterations tried to enforce TDD through the spec workflow, requiring every spec to pass through a test-driven flow before implementation could begin. The approach worked technically but failed in practice: "When actually putting that in front of users and customers, it was not typically how they were working. TDD is great, people follow it, but a lot of users were just not doing that," Swaminathan explains. The team pivoted to making TDD an optional steering rule rather than a mandatory spec workflow stage, giving teams flexibility in how they move from spec to implementation.
>
> This mirrors a broader lesson about spec review processes: the review gate must match the team's existing workflow or it will be routed around. A review process that is too rigid gets abandoned. A review process that is too loose provides no value. The effective middle ground is explicit about what must be reviewed (business intent alignment, architectural fitness) while flexible about how the review happens (PR comments, synchronous meeting, collaborative editing session).

## When the Spec Is Wrong

No review process catches everything. When a spec error escapes into implementation, the cost depends on how far it traveled.

If the agent is mid-implementation when someone notices the spec is wrong, the cheapest option is usually to stop, fix the spec, and restart the implementation from scratch. Agent time is cheap. Human time spent debugging an agent that is faithfully implementing the wrong spec is expensive.

If the error reaches code review, the reviewer should trace the problem back to the spec rather than patching the code. A code-level fix for a spec-level problem creates a divergence between the spec and the implementation - the exact kind of "spec drift" that erodes the value of the spec-driven approach over time. Richard Threlkeld compares spec drift to code comments: "If you put comments in code at that point in time, they will hold as people and teams edit them over time. They can drift. So you have to think about it as a similar artifact in your system and build controls around it."[ANDev-016]

If the error reaches production, the fix starts with the spec, not the code. Update the spec to reflect the correct behavior, then let the pipeline regenerate the implementation. This discipline feels slow in the moment but prevents the gradual accumulation of undocumented behavioral changes that make specs unreliable.

## Scaling Spec Review

As the factory scales - more teams, more concurrent features, more specs flowing through the pipeline - spec review becomes a bottleneck if it depends on a small number of senior reviewers. Some teams treat this as evidence that review cannot scale with factory throughput. The evidence says otherwise. Sadowski et al.'s study of code review at Google, published at ICSE-SEIP 2018, documents a system where over nine million changes underwent mandatory review, with every single change requiring at least one reviewer's approval before merging.[Sadowski-2018] Google did not achieve this by making review optional for small changes or by exempting certain teams. They achieved it by making the process lightweight enough that it could be applied universally without becoming a bottleneck. The lesson for spec review is that universality and speed are not opposed - they require each other. A review process that is too heavy to apply universally will be applied selectively, and the specs that skip review will be the ones that needed it most.

Two strategies help.

**Distribute review authority.** Not every spec needs the architect. Define clear ownership boundaries so that each team's tech lead can approve specs within their domain without escalation. Reserve architect-level review for specs that cross domain boundaries.

**Invest in automated pre-review.** Before a human sees the spec, automated checks can catch the mechanical problems: contradictions with existing specs, references to nonexistent APIs, missing non-functional requirements, formatting issues. This is where agent harnesses earn their keep - a review agent that scans the spec against the existing codebase and flags potential conflicts reduces the human reviewer's cognitive load significantly.

Neither strategy eliminates the need for human judgment. Automated checks catch structural problems, not semantic ones. A spec can be internally consistent, well-formatted, and reference only existing APIs while still being the wrong feature to build. That determination requires a human who understands the business context.

## The Spec Review Checklist

For teams standing up their first spec review process, a simple checklist gets you 80% of the value.

1. Does the spec match what the stakeholder actually requested? (Ask them.)
2. Are all behavioral statements testable?
3. Are edge cases and error conditions covered?
4. Does the proposed behavior conflict with any existing system behavior?
5. Are non-functional requirements stated with measurable thresholds?
6. Is the proposed architecture compatible with the existing system?
7. Are there other specs in the pipeline that touch the same components?

If a reviewer can answer "yes" to all seven, the spec is ready to proceed. If any answer is "no" or "I'm not sure," the spec goes back for revision. No partial approvals, no "we'll figure it out during implementation." The whole point of this gate is to resolve ambiguity before tokens are spent on code.

The spec review is the cheapest mistake you will ever catch. Every hour spent here saves a day downstream.
