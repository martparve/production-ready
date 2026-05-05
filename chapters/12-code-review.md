# Chapter 12: Code Review: The Second Human Gate

The PR lands in your queue at 9:14 AM. You were not there when it was written. You did not pair on it, did not watch the agent iterate, did not see the three false starts it took before the tests passed. You have a diff, a description, a link to the spec, and a validation report. That is the entirety of your context for deciding whether this change ships to production.

This is code review in a headless factory. The author is a machine, the reviewer is you, and the dynamics differ from anything the industry practiced for the last thirty years.

## What Stays the Same

The good news: most of what makes a strong code reviewer has not changed. Architectural judgment still matters. Business logic correctness still matters. Security still matters. Maintainability still matters. The reviewer's job is still to ask: does this change do what it should, is it safe, and will future engineers be able to understand it?

These concerns are durable because they are properties of the system, not the author. A SQL injection vulnerability exists whether a human or a machine introduced it, and the reviewer's job is to catch it.

The same applies to architectural fitness. A machine-generated PR that introduces a synchronous HTTP call inside an event-driven pipeline is making an architectural mistake regardless of its origin. A reviewer who understands the system's design principles will spot this whether the diff came from a junior engineer, a senior engineer, or Claude.

## What Changes

Three things are different when the author is a machine, and each one shifts how you should spend your review time.

**No ego.** Human code review carries social weight. You phrase feedback carefully. You distinguish between "this is wrong" and "have you considered an alternative approach?" You calibrate directness based on the author's seniority and your relationship with them. None of that applies when reviewing machine-generated code. You can be blunt, specific, and demanding without worrying about morale. "This is wrong, regenerate it" is a perfectly reasonable review comment when the author cannot have its feelings hurt.

A surprising amount of review friction in human teams comes from the social overhead of delivering feedback. Removing that overhead changes the velocity of the review cycle and, more importantly, the reviewer's willingness to reject marginal work. When the cost of rejection is "the machine runs again for twenty minutes" instead of "a colleague spends another afternoon on this," reviewers hold a higher bar.

**Volume is far higher.** Stripe processes roughly 1,300 agent-generated PRs per week.[ANDev-052] Even teams far smaller than Stripe are seeing 3-10x increases in PR volume when they adopt agentic workflows. This volume changes what is feasible. You cannot review 1,300 PRs per week with the same line-by-line scrutiny you applied to 130. Something has to give.

**The reviewer assesses spec match, not style preference.** In traditional code review, a significant portion of comments are about style, naming, and idiomatic patterns. These are valid concerns, but they are concerns about how the code was written, not what it does. When an agent writes code, style enforcement belongs in the linter and the context configuration, not in the review. The human reviewer's time is better spent on the question that automated tools cannot answer: does this implementation faithfully execute the spec?

## The Human Bottleneck

The volume problem is not theoretical. It is the single most discussed operational challenge in teams that have adopted headless development.

> **Case Study: The Simon Willison Warning**
>
> Thomas Dohmke, former CEO of GitHub and founder of Entire, cited Simon Willison's[Willison-context] observation on the AI Native Dev podcast (Ep 050): "You have to get comfortable with not reviewing every single line of code before we deploy them into production, because the sheer amount of code that a single agent can write 24/7 - now you parallelize that into running 10 agents in parallel all the time - it's never going to be able to review all the code without the one human doing that becoming the major bottleneck and effectively erasing some of the productivity gains from these agents."[ANDev-050]
>
> Guy Podjarny[Simon] reinforced the point: "If humans are the bottleneck, then you get human traits like review fatigue, but then you also just see slowness. This is the human speed limiting how much can the AI code and build up."
>
> The cloud era analogy is instructive. When continuous deployment replaced quarterly releases, the industry could not keep manual QA gates. Teams that just removed the gate and let code flow broke things. Teams that automated the gate - with CI, automated testing, staged rollouts - shipped faster and with higher quality. The same transition is happening now with code review.

The bottleneck manifests in predictable ways. Senior engineers - the ones best qualified to review complex changes - are the ones most likely to be buried. Merrill Lutsky, CEO of Graphite, described this directly: "Many of their most senior engineers are now just buried in mountains of PRs from more junior folks that are just churning these out with AI tooling."[ANDev-025]

But scale alone does not make review impossible. Sadowski et al. studied code review at Google across more than nine million reviewed changes and found that every single change to the codebase, without exception, goes through review.[Sadowski-2018] Google achieves this through rigorous tooling and process discipline: automated reviewer assignment, mandatory review before merge, and a culture where review is not optional overhead but a core engineering activity. The lesson for factory operators is that review can scale to enormous volumes if the tooling and process are deliberately designed for it. The problem is not that 1,300 PRs per week cannot be reviewed. The problem is that 1,300 PRs per week cannot be reviewed with the same ad hoc process that worked for 130.

The temptation is to review less carefully. The correct response is to review differently.

## Three Phases of Review Evolution

Merrill Lutsky outlined a framework on the AI Native Dev podcast (Ep 025) that maps neatly to where most teams are and where they are heading.[ANDev-025] The three phases describe not just how review changes, but how the reviewer's attention shifts upward through layers of abstraction.

**Phase 1: Reviewing code quality.** This is where most teams are today, or were recently. The reviewer reads every line of the diff, checking for bugs, logic errors, style violations, and security issues. It is the same review you would give a human author's code. It works, but it does not scale. When PR volume triples, Phase 1 review becomes the bottleneck that erases the productivity gains from agentic development.

**Phase 2: Reviewing spec compliance.** The reviewer's primary question shifts from "is this code well-written?" to "does this implementation match the spec?" The reviewer still reads code, but a lot of the detail work - style consistency, common bug patterns, security surface scanning - is handled by AI review tools. The human focuses on the higher-order question: did the agent build the right thing? This phase requires that specs exist and are detailed enough to review against. Teams that skipped the spec formalization step (Chapter 6) cannot enter Phase 2.

**Phase 3: Reviewing system-level impact.** The reviewer rarely inspects code directly. Instead, they review the artifact: the running feature, the test results, the performance profile, the behavioral diff against the spec. Lutsky described this phase as resembling "what working with an external dev agency would be, where you're giving just high level specs and then you're getting back the artifact of the finished product."[ANDev-025] This phase requires mature validation infrastructure - automated testing, behavioral verification, and deployment confidence scoring. Most teams in mid-2026 are somewhere between Phase 1 and Phase 2.

The transition between phases is not a binary switch. A team will use Phase 3 review for low-risk UI changes while still applying Phase 1 scrutiny to authentication logic. The phases describe a spectrum of trust, and trust varies by risk tier.

## Review Strategies

Four strategies help reviewers manage volume without sacrificing quality.

### Spec-Diff Review

The most important shift in review technique: instead of reading the code and forming an opinion about what it does, start with the spec and check whether the code does what the spec says.

This inverts the traditional review flow. In human-authored code, the reviewer builds a mental model of the change by reading the diff, then evaluates whether that mental model is correct. In machine-authored code, the mental model already exists in the spec. The reviewer's job is comparison, not construction.

Spec-diff review is faster because it is a focused activity. You are not asking open-ended questions like "is this good code?" You are asking closed questions: "The spec says the endpoint returns a 404 when the resource does not exist. Does the code do that?" This is easier to verify and harder to get wrong.

It also shifts the burden of self-documentation onto the factory. If the PR does not include a link to its spec, or if the spec is too vague to review against, that is a pipeline problem, not a review problem. The reviewer should reject the PR and send it back.

### Behavioral vs. Structural Review

Does it do the right thing? That is the primary question. Is it built the right way? That is secondary.

This prioritization matters because reviewer time is finite. A machine-generated implementation that uses an unusual pattern but produces correct behavior is less concerning than one that uses idiomatic patterns but misses an edge case. Behavioral correctness is non-negotiable. Structural elegance is negotiable.

This does not mean structural quality is irrelevant. Code that is hard to read, poorly abstracted, or unnecessarily complex creates maintenance debt. But in a world where code is increasingly disposable - where regenerating an implementation is cheaper than refactoring it - structural concerns carry less weight than they did when code was handcrafted and expected to survive for years.

### Risk-Tiered Review

Not all code changes carry the same risk. A change to the authentication system, a payment processing update, or a database migration can cause catastrophic damage if it goes wrong. A copy change in a tooltip, a CSS adjustment, or a new logging statement cannot.

Risk-tiered review assigns review depth based on the blast radius of the change:

- **Deep human review:** Authentication, authorization, payments, data migrations, cryptographic operations, compliance-sensitive code. A senior engineer reads every line. No AI-only review permitted.
- **AI-assisted human review:** Business logic, API endpoints, data model changes, integration points. An AI reviewer makes a first pass; a human reviewer validates the AI's findings and checks spec compliance.
- **AI review with human override:** UI components, copy changes, test additions, tooling updates, configuration changes. An AI reviewer approves or flags; a human spot-checks a sample and approves the batch.

The boundaries between tiers should be codified, not left to judgment. Use CODEOWNERS files, path-based rules, or label-based policies to route PRs to the appropriate review tier automatically. If every PR requires the same level of scrutiny, you will either under-review the dangerous ones or over-review the trivial ones.

### Stacked PRs for Reviewability

Large agent-generated changes are hard to review as monolithic PRs. A 2,000-line diff from an agent that worked autonomously for an hour is cognitively overwhelming, even for an experienced reviewer. This is not just a feeling - it is measurable. Bosu et al. studied code review quality at Microsoft across thousands of reviews and found that the more files included in a change, the lower the quality of review comments.[MS-CodeReview] Reviewers facing large diffs produce shallower, less actionable feedback. The cognitive load of holding a large change in working memory crowds out the deeper reasoning needed to catch architectural and logic errors. For factory output, this means agents should be configured - or the orchestrator should enforce - small, focused PRs rather than large multi-file changes. A factory that produces ten 200-line PRs will get better review outcomes than one that produces a single 2,000-line PR, even though the total code volume is identical.

Cohen et al. reached a complementary conclusion in the largest published study of code review practices, covering 2,500 reviews of 3.2 million lines of code at Cisco.[Cohen-review] Lightweight reviews - focused, time-boxed, with clear checklists - were seven times faster than formal inspection processes while catching comparable defect rates. The implication for factory review is clear: the right response to volume is not heavyweight inspection of every PR but lightweight, structured review with deep inspection reserved for high-risk changes.

> **Case Study: Graphite's Stacked PR Workflow**
>
> Merrill Lutsky argued on the AI Native Dev podcast (Ep 025) that stacked PRs become more valuable, not less, when agents generate the code. "Especially for background agents, if you just kind of let them run wild, the result is you get multi-thousand line, unintelligible PRs."[ANDev-025] Graphite's[Graphite] MCP integration allows agents to create stacked PRs - smaller, sequential changes that build on each other - precisely because it makes review tractable on the other side.
>
> Lutsky also highlighted a benefit specific to machine-generated code: revertability. "Having smaller pieces and a clear history enables you to more easily figure out what was the change that introduced this problem. It lets you roll back more precisely." When an agent introduces a regression in line 1,847 of a monolithic PR, finding it is archaeology. When the same regression is in a 200-line stacked PR, it is obvious.
>
> The stacked PR workflow also supports a review pattern that maps naturally to agentic development: the agent keeps working on the next piece while the reviewer examines the current one. This decouples development from review, which is exactly what you need when the developer never gets tired and the reviewer does.

## Review Ergonomics

The interface you review in affects the quality of your review. This sounds obvious, but teams routinely ignore it.

> **Case Study: David Cramer on Review UX**
>
> David Cramer, co-founder of Sentry, spent eight weeks building exclusively through agents without writing code by hand (Ep 015). His strongest opinion coming out of the experiment was about review interfaces: "Claude Code is actually not a great user interface for where we are with this stage of technology. If I use Cursor and I run through their agent and I generate a change set in real time, I'm getting the diffs in my editor. I'm able to approve blocks of code really seamlessly. I'm able to jump between these files really seamlessly."[ANDev-015]
>
> Cramer's argument is not about which agent is smarter. It is about which interface lets the human reviewer do their job effectively. "The right answer is humans should be in the loop. And I think Cursor's user experience is a much better version of humans in the loop because I incrementally review things. The context for me is smaller."
>
> The takeaway is not "use Cursor." It is that review UX is a first-class concern when PR volume increases 3-10x. A review interface that was adequate at 130 PRs per week becomes a bottleneck at 1,300.

When review volume is high, every friction point in the review interface compounds. How many clicks does it take to see the spec alongside the diff? Can you jump from a test failure to the code that caused it? Can you see the validation report without leaving the PR? Can you approve a batch of low-risk PRs in a single action?

These are tooling questions, but they have direct quality implications. A reviewer who is fighting the interface is a reviewer who is cutting corners.

## AI-Assisted Review: The Second Layer

A pattern that is rapidly gaining adoption: use a second AI to review the first AI's code. The human then reviews the AI review, not the raw code.

This is layered confidence. The code-generating agent has a certain error rate. The review agent has a different, partially overlapping error rate. The probability of both agents making the same mistake on the same change is meaningfully lower than either one alone. The human reviewer then operates on the AI review's output - a set of flagged concerns, confidence scores, and spec compliance assessments - rather than reading every line of the diff.

Merrill Lutsky described Graphite's approach: "Can we take a lot of the work that a human reviewer would do, and hand that to AI, have it catch many of the bugs and nits and style inconsistencies, follow custom rules, find security vulnerabilities? Can it do that first pass at code review and shortcut that so that by the time you loop in a human colleague, they're able to look for higher order problems and not have to spend as much time nitpicking and reading every single line of code?"[ANDev-025]

The key insight is what AI review does well and where it falls short. Lutsky was specific: "It's great at finding bugs and logic errors. It's very good at style guide adherence. It's good at finding security vulnerabilities." Where does it struggle? "Higher level architecture decisions. I don't think we yet have the context to be able to do that."[ANDev-025] And validating end-to-end behavior - confirming that the change actually does what it was supposed to do in the running system.

This maps to a clear division of labor. AI review handles the mechanical checks: logic errors, style violations, common vulnerability patterns, spec clause matching. Human review handles the judgment calls: architectural fitness, business logic correctness, system-level implications, and the question of whether this feature should exist at all.

Microsoft's engineering team deployed AI-powered code review across their organization in 2025 and published their findings.[MS-CodeReview] The results showed faster PR completion times, improved code quality metrics, and - perhaps most valuably - enhanced onboarding for new team members who could use the AI reviewer's comments as a learning tool. This is the "AI reviews AI" pattern working in production at scale: machine-generated code reviewed by a machine reviewer, with humans operating at a higher layer. The pattern works because the reviewing AI and the generating AI have different failure modes. The generating agent optimizes for task completion. The reviewing agent optimizes for defect detection and policy compliance. Their errors are largely uncorrelated.

Vijaykumar et al. investigated what LLM-based code review can do that traditional static analysis cannot.[Vijaykumar-2404] Their key finding: LLM reviewers can predict future risks - identifying code patterns that are technically correct today but likely to cause problems as the system evolves. Static analysis checks current-state rules (is this variable used? does this type match?). LLM review checks trajectory (this function is accumulating responsibilities in a way that will become a maintenance burden; this error handling pattern will break when the upstream API adds a new error code). For factory output, this distinction matters because agents produce code that passes all current tests by construction - the validation pipeline ensures it. The interesting review question is not "does this work now?" but "will this still work in six months?" That is exactly the question LLM reviewers are beginning to answer.

## The Rejection Loop

When a reviewer rejects a machine-generated PR, the feedback goes back to the agent. The quality of that feedback determines whether the next attempt is better or just differently wrong.

Structured rejection has three components:

1. **Reference the spec clause.** "Section 3.2 requires that the endpoint return a 404 when the resource is not found." This anchors the feedback to a shared source of truth.
2. **Point to the code.** "Lines 47-52 of `handlers/resource.go` return a 500 instead." This makes the problem concrete and locatable.
3. **State the correct behavior.** "The handler should check `resource == nil` and return a 404 with the standard error envelope." This gives the agent a target.

The alternative - vague feedback like "this doesn't seem right" or "fix the error handling" - works poorly with human authors and works even worse with agents. Agents cannot read between the lines. They cannot infer what you meant from what you said. They need explicit, structured feedback tied to specific code locations and specific spec requirements.

Two rejection strategies are worth distinguishing. **Reject-and-reiterate** sends the feedback to the same agent session, which attempts to fix the issues in place. This works for small, localized problems where the agent's existing context is valuable. **Reject-and-regenerate** discards the current implementation and starts fresh with the feedback incorporated into the initial prompt. This works better for fundamental problems where the agent's approach was wrong, not just its execution.

The choice between the two depends on how much of the implementation is salvageable. If the agent got the architecture right but missed an edge case, iterate. If the agent built the wrong thing entirely, regenerate. Trying to iterate your way out of a fundamentally wrong approach wastes more tokens and reviewer time than starting over.

## Tooling

The code review tooling landscape for AI-native workflows is evolving rapidly. Several categories of tools address different parts of the problem.

**AI review agents.** CodeRabbit[CodeRabbit], Graphite Agent, and Qodo[Qodo] (formerly PR-Agent) provide automated first-pass review. They comment on PRs with bug findings, style violations, and security concerns. The quality varies by language and codebase, but the best of them meaningfully reduce the surface area a human reviewer needs to cover. Custom review agents built on top of Claude or GPT, configured with your team's specific rules and style guides, can outperform generic tools because they operate with your context.

**Review workflow tools.** Graphite, GitHub's native review features, and GitLab's merge request workflow handle the mechanics of review assignment, approval gates, and merge policies. CODEOWNERS files route PRs to the right reviewers based on file paths. Branch protection rules enforce minimum approval counts. These tools become more important, not less, when PR volume increases.

**Spec-linked review.** The factory should attach the originating spec to every PR. Some teams do this through PR templates that require a spec link. Others use automation that pulls the spec reference from the branch name or commit metadata. The goal is that no reviewer should ever look at a diff and wonder "what was this supposed to do?" If the spec link is missing, the PR is not ready for review.

**Validation reports.** The most advanced headless factories attach validation reports to every PR: test results, coverage deltas, performance benchmarks, security scan results, and confidence scores from the generating agent. These reports serve the reviewer who was not present during execution. They replace the "session memory" that a human pair-programming partner would have had.

## The Decision Matrix

Not every PR requires the same review process. The following matrix helps teams assign the right level of scrutiny based on two dimensions: the risk tier of the change and the maturity of your validation infrastructure.

**Fully human review.** Use for: authentication, authorization, payment processing, data migrations, cryptographic operations, privacy-sensitive code, and any change that could cause irreversible damage. No delegation to AI reviewers. A senior engineer reads every line, compares against the spec, and validates the behavioral impact.

**AI-assisted human review.** Use for: business logic, API changes, data model modifications, integration code, and anything that touches multiple services. An AI reviewer makes the first pass. A human reviewer validates the AI's findings, checks spec compliance, and evaluates architectural fitness. This is the sweet spot for most production code.

**AI review with human override.** Use for: UI components, copy changes, documentation updates, test additions, tooling configuration, and dependency updates. An AI reviewer approves or flags. A human spot-checks a sample - perhaps 1 in 5 - and approves the batch. Low-risk changes that pass automated validation and AI review should not consume senior engineering time.

**Progressive gate reduction.** As your validation infrastructure matures - as your automated tests become more comprehensive, your AI reviewers more accurate, your deployment rollback more reliable - you can progressively relax review gates for lower-risk tiers. The timeline is team-specific, but a reasonable progression might be:

- Month 1-3: All PRs get full human review. You are building trust.
- Month 3-6: Low-risk PRs move to AI review with human override. Medium-risk PRs get AI-assisted human review.
- Month 6-12: Medium-risk PRs with high confidence scores and clean validation reports move to AI review with human spot-check. High-risk PRs remain fully human.
- Month 12+: Review tiers are driven by automated risk scoring, with humans concentrated on the changes that matter most.

This progression only works if you are measuring outcomes. Track escaped defects by review tier. If AI-only review is letting bugs through in a category, that category moves back up the scrutiny ladder.

## The Changing Purpose of Code Review

Something gets lost in the volume discussion: code review was never just about catching bugs.

Merrill Lutsky made this point explicitly: "A lot of folks get stuck on the idea of code review being the only value of code review being this validation step. I think the other two pieces that are often missed: code review is super important in sharing knowledge across the team. It's also a great moment of teaching where you get feedback and you're able to improve the way you're approaching your projects."[ANDev-025]

Bacchelli and Bird's landmark study at Microsoft confirmed this empirically: in a study of professional developers, the primary value of code review was knowledge transfer and shared code ownership, not defect detection.[Bacchelli-2013] Reviewers reported that understanding code written by others - building a mental model of what changed and why - was the outcome they valued most. Bug-finding, while important, ranked below knowledge dissemination, team awareness, and finding alternative solutions.

If the primary purpose of human review is knowledge transfer, and the agent does not learn from review feedback (context updates are still a manual step), then the traditional review loop is broken in one direction. The agent produces code, the human reviews it and learns about the system, but the agent does not absorb the reviewer's insights for next time. Review of agent code needs a different framing: it is less about improving the author and more about keeping the human team literate in their own system. The reviewer is not teaching - they are studying.

In a headless factory, the knowledge-sharing function of review becomes more important, not less. When an engineer reviews a machine-generated PR, they are learning what the agent built, how it interpreted the spec, and what patterns it chose. This is how the team maintains a mental model of its own system despite not having written much of the code. If review becomes purely a rubber-stamping exercise, the team loses situational awareness of its codebase.

The teaching function transforms. You are no longer teaching the junior engineer who wrote the code. You are teaching the context layer that configures the agent. When a review catches a recurring problem - the agent keeps choosing the wrong serialization format, or it consistently underestimates the complexity of error handling in a particular service - that learning should flow back into the agent's context configuration: the CLAUDE.md, the style guides, the skill definitions. Review feedback that changes agent behavior is worth ten times more than review feedback that fixes a single PR.

## Making the PR Self-Documenting

In a headless factory, the reviewer was not present during execution. They have no session memory of what the agent tried, what it struggled with, or what tradeoffs it made. The PR must compensate for this absence.

A well-structured machine-generated PR includes:

- **Spec link.** The originating specification, so the reviewer can assess compliance.
- **Validation report.** Test results, coverage data, security scan output, and performance benchmarks.
- **Confidence score.** The agent's own assessment of how confident it is in the implementation. A low confidence score signals that extra scrutiny is needed.
- **Decision log.** Key decisions the agent made during implementation, especially where the spec was ambiguous. "The spec did not specify behavior when both flags are set. I chose to prioritize flag A based on the pattern in `existing_handler.go`."
- **Scope boundaries.** What the PR intentionally does not do. "This PR does not migrate existing records. That is tracked in JIRA-4521."

Each of these elements reduces the reviewer's cognitive load. Without them, the reviewer must reconstruct the agent's reasoning from the diff alone, which is slow, error-prone, and demoralizing at scale.

## Where This Is Heading

Code review is transitioning from manual, line-by-line inspection to a layered, risk-stratified, partially automated process.

The end state is not "no human review." It is "human review concentrated where it matters." Humans reviewing architectural decisions, business logic correctness, and system-level impact. Machines handling style enforcement, common bug patterns, and spec-clause verification. Every PR carrying enough context that a reviewer who was never in the room can make a confident judgment in minutes rather than hours.

Peter Steinberger, creator of the Clawd personal assistant, illustrates the far end of this trajectory. He has abandoned traditional code review entirely: "It takes me ten times more time to review that than to just type 'fix' in Codex and wait a few minutes."[PE-24] He proposes renaming pull requests to "prompt requests" - the input is a natural language description, not a code diff, and the review should evaluate whether the prompt was correct, not whether every line of generated code matches the reviewer's preferences. This is a boundary case, not a recommendation: Steinberger is a solo developer on a self-described YOLO project, and even the podcast episode acknowledges that "Clawd is more of a YOLO project than most production apps." But boundary cases illuminate trajectories. As the factory's defect rate drops, the economics of line-by-line review will increasingly favor Steinberger's approach: verify the spec, verify the validation passed, and trust the production line.

David Cramer captured the current moment precisely: "You can't pretend these things can do things they can't do. And you need a human in the loop."[ANDev-015] The question is not whether humans remain in the loop. The question is what size loop, and at what altitude.

Teams that answer this question well will ship at a pace their competitors cannot match. Teams that refuse to answer it - insisting on the same review process at 10x the volume - will drown their best engineers in a backlog of diffs and wonder why the factory is not delivering the productivity gains they were promised.

The review is not the bottleneck. The wrong kind of review is the bottleneck.
