# Chapter 18: Evaluations: Testing the Factory Itself

A team upgrades from one frontier model to its successor. The first few results look promising: cleaner code structure, fewer retries, better test coverage on generated code. The tech lead approves the switch after reviewing five outputs. Three weeks later, a pattern surfaces in code review: the new model consistently bypasses the team's custom ORM wrapper and writes raw database queries. The existing test suite misses this because it checks behavior, not implementation strategy. The review rejection rate climbs from 8% to 22%, but nobody connects "model upgrade" to "ORM bypass" because nobody ran a controlled experiment before deploying the change.

Non-deterministic systems cannot be assessed by example. A single successful run proves nothing about the next run. A single failure might be an outlier. Maria Gorinova from Tessl's AI engineering team puts it sharply: "It is very dangerous if we look at an isolated example that works or doesn't work and then make judgments on this. Because then we're going to make decisions about a product or a feature or even our day-to-day workflow that are based on this one isolated example. That is just an anecdote. It's not reflective of the average."[ANDev-032] Eugene Yan frames the same point as methodology: evals are not artifacts to build once but an ongoing scientific practice requiring sampling, annotation, and calibration of automated judges against ground truth. Skip them, and you are making factory decisions on vibes.[Yan-judge]

Validation (Chapter 11) checks whether a specific agent run produced correct output. Metrics (Chapter 17) track production health over time. Evals sit between: controlled, proactive experiments that measure whether the factory - its models, context, skills, and configuration - can reliably produce correct output across a population of tasks. Without evals, every factory change is a coin flip. With them, you can compare models, prune context, upgrade skills, and onboard new codebases with data instead of anecdotes.

## What Evals Are (and Are Not)

Four related practices sit in this space. They serve different purposes and answer different questions. Conflating them leads to gaps in coverage.

**Validation** (Chapter 11) is a per-run quality gate. It asks: did this specific agent output build, pass tests, and match the spec? It is binary, applied to every factory output, and blocks or passes a single artifact. Validation catches defects in individual runs.

**Benchmarks** - SWE-bench[Jimenez-2310], TerminalBench[TerminalBench], and their descendants - are public standardized test suites. They are useful for comparing models and rough capability estimation before you commit to a vendor. They are not useful for measuring your factory on your codebase. A model that scores 60% on SWE-bench may score 90% on your typical tasks if your codebase is well-documented and your tasks are scoped tightly, or it may score 30% if your stack relies on niche frameworks the model has rarely seen. Benchmarks test generic coding ability against generic problems. Your factory operates against your specific architecture, dependencies, and conventions. The gap between these two contexts is where evals live.

**Evals** are controlled experiments against representative tasks drawn from your own work. They are proactive, synthetic, and run before changes reach production. They answer "can this configuration handle this class of work?" rather than "did this specific run succeed?" Where validation is a gate, evals are a measurement instrument.

**Metrics** (Chapter 17) are continuous production telemetry: first-pass success rate, review rejection rate, cost per task. They are lagging indicators that tell you how the factory performed yesterday. They cannot tell you whether a proposed change will improve or degrade tomorrow's performance.

The critical distinction is between evals and validation. Validation tells you whether one output is acceptable. Evals tell you whether the system that produced the output is reliable across a population of tasks. A factory that validates every run but never evaluates its own capabilities is a factory that catches individual defects but cannot measure - or improve - its overall performance.

Anthropic's agent eval guide adds a practical complication: agent evals are harder than single-turn model evals.[Anthropic-evals] Three properties make them harder. First, mistakes compound over multi-turn tool use: an agent that makes a small error in step 3 of a 12-step task may produce output that is wildly wrong by step 12, and the eval must distinguish "compounding error" from "fundamentally wrong approach." Second, state changes are difficult to reverse: an agent that modifies a database schema during execution cannot simply undo the change, so eval infrastructure must support environment reset between runs. Third, an agent that discovers a better solution than expected can "fail" a rigid eval even though it produced correct output. Eval design for agents must account for legitimate alternative paths to the same outcome, which means scoring criteria should focus on properties of the result (does it work, is it safe, does it follow conventions) rather than on the specific steps taken to produce it.

## The Three Categories

Organize your eval suite around three categories. Each serves a different purpose and runs on a different cadence.

**Capability evals** measure whether the factory can handle the types of tasks you assign to it. Generate representative specs spanning your common task categories: bug fixes in your authentication module, feature additions to your API layer, refactoring of your data pipeline, migration of database schemas, integration of third-party APIs. Run them periodically against the current factory configuration. Track pass rates over time, broken down by task type. A capability eval suite that covers your top ten task types gives you a quantitative answer to "what can the factory do?" instead of a collection of impressions. It also reveals which categories the factory handles well and which it struggles with, guiding where to invest in better context or validation.

**Regression evals** detect degradation after any change to factory configuration: model version, context documents, validation rules, prompt templates. Run a fixed historical set and compare results to the previous configuration. Same principle as regression testing for code, applied to the factory itself. The key property is stability: the scenarios and scoring criteria stay constant so that differences in results reflect genuine changes in factory performance, not changes in the measurement.

**Boundary evals** explore where the factory fails. Push intentionally toward edge-of-capability tasks: complex multi-service changes, unfamiliar frameworks, ambiguous specifications, tasks requiring coordination across multiple repositories. These evals do not need to pass. They need to fail predictably and gracefully - escalating to humans rather than producing subtle defects. Boundary evals are how you discover the factory's limits before a real task hits them. They also serve as an early warning system: when a boundary eval that used to fail starts passing after a model upgrade, the factory's capability envelope has expanded, and you may be able to promote that task type to the regular capability suite.

The three categories have different economics. Capability evals are your core investment and run weekly or on a schedule tied to your deployment rhythm. Regression evals are triggered by configuration changes and can be scoped to the scenarios most likely affected. Boundary evals are expensive and exploratory, run monthly or whenever you change models. Start with five scenarios per category and expand as you learn which task types are most fragile.

## Building the Test Corpus

The eval suite is only as useful as the scenarios it contains. A corpus of unrealistic tasks produces meaningless pass rates. Four sources generate realistic scenarios.

**Mining git history.** Extract representative commits or PRs from the last six to twelve months. Filter by complexity, domain, and outcome: was it merged cleanly, or did it require multiple revisions? These become "can the factory reproduce what humans did?" scenarios. The task description is the original ticket or commit message, and the grading criteria are derived from what actually shipped. Be selective: a 200-scenario corpus mined indiscriminately from git history is less useful than a 30-scenario corpus curated to represent distinct task types, complexity levels, and code areas. Weight the corpus toward the work you actually plan to assign to the factory, not the work that was easiest to extract.

**Synthetic generation.** Use an LLM to generate variations of common task types from your spec templates and acceptance criteria. This fills gaps in the historical corpus: task types that occur frequently but vary in detail, or task types you plan to assign to the factory but have not yet. Husain's recommendation: generate synthetic cases covering all your key features, start by reviewing everything manually, and sample as you scale.[Husain-evals]

**Production failure mining.** Every time a factory-produced PR gets rejected in review, or an agent output fails validation and requires human intervention, add a scenario that captures that failure mode. Record the original spec, the agent's output, the reason for rejection, and the corrected version. This is how the eval corpus tracks the factory's actual weak points rather than imagined ones. A corpus built only from successes misses the cases where the factory struggles most. Over time, the failure-mined scenarios become the most valuable part of the corpus because they test exactly the failure modes that matter to your team.

**Maintaining the corpus.** Version the corpus alongside factory configuration. Retire scenarios that no longer represent current work. Add scenarios from real failures. A stale eval corpus tests yesterday's factory against yesterday's problems, and a clean pass rate from stale scenarios provides false confidence.

> **Case Study: Grader Engineering at Stripe**
>
> Stripe's Minions team invested heavily in eval infrastructure for their autonomous coding agents. Their public benchmark reveals the engineering required to make evals meaningful.[Stripe-Minions-2]
>
> Environments had to be complex enough to be realistic: multi-file repositories, databases, build scripts. But they also had to be structured enough for an unambiguous automated grader with replicable runs. The grader evaluates functional correctness via test suites but also structural criteria: does the change stay within the expected scope? Does it introduce unrelated modifications?
>
> The key insight for factory operators: the grader engineering is as much work as the agent engineering. Designing environments, building deterministic setups, calibrating automated scoring - this infrastructure does not emerge from a weekend hackathon. A factory without a rigorous grader is a factory that cannot measure its own improvement.

## Scoring: LLM-as-Judge

Human review does not scale to the volume of output a factory produces. The solution is automated judges - but they require careful design to avoid replacing one source of unreliability with another.

Husain's three-level framework provides a practical progression.[Husain-evals]

**Level 1: Assertions.** Deterministic, pytest-style checks against specific properties. Does the output compile? Does it import the correct library? Does it contain forbidden patterns? No LLM needed. Fast, cheap, and unambiguous. Every eval suite should start here, and a surprising number of important quality signals can be checked this way.

**Level 2: LLM judge with human calibration.** A judge model evaluates the agent's output against a rubric. The critical discipline is ongoing calibration: track judge agreement with human labels as a continuous task, not a one-time setup. Use precision and recall separately, because raw agreement is misleading on imbalanced datasets where most outputs pass. If the judge agrees with humans 95% of the time but misses 40% of actual failures, that 95% agreement number is hiding a dangerous blind spot. Build a calibration set of 50-100 outputs with known-good human labels. Run every rubric change against this set before deploying it. Track the judge's precision and recall over time, and investigate whenever either metric shifts by more than five percentage points.

**Level 3: A/B comparison.** Only after the product is mature enough to need it. Compare two factory configurations head-to-head on the same task set. This is the methodology for model upgrades, context changes, or any configuration decision where both options produce "acceptable" output but one might be better.

**Binary judgments over numeric scales.** This is one of the strongest practical findings in the eval literature. Avoid 1-5 Likert scales that collapse distinct failure types into a meaningless average. "Agent used a deprecated API" and "agent hallucinated a nonexistent function" both score low on a quality scale, but they require completely different mitigations. Binary pass/fail per criterion preserves the distinction. For subjective criteria where binary is too coarse, use pairwise comparison: is output A better, worse, or equal to output B?[Husain-evals-skills]

**Rubric design requires error analysis first.** Build a vocabulary of failure modes from actual agent traces before writing the rubric. Most teams write rubrics from intuition, then discover that real failures do not map cleanly to the criteria they imagined. Start with an eval-audit process that categorizes existing failures before any judge prompt is written. The taxonomy of actual failures becomes the rubric.[Husain-evals-skills]

> **Case Study: Who Validates the Validators?**
>
> Shankar et al. demonstrate that LLM validators are "unintuitively sensitive to seemingly minor changes in wording or structure."[Shankar-validators] A rephrased rubric can flip judgments on the same output, even when both phrasings appear semantically equivalent to a human reader. Their EvalGen tool addresses this through iterative alignment of LLM-generated evaluation functions with human preferences via mixed-initiative annotation.
>
> The practical takeaway: treat judge prompts with the same rigor as production prompts. Version them. Test them against known-good and known-bad output pairs. Recalibrate when you change the judge model. A judge that was well-calibrated on one model version may behave differently on the next, even if the new model is "better" in aggregate benchmarks. The rubric is code. It deserves tests.

## What to Measure Beyond Correctness

Most coding benchmarks measure functional correctness: does the code produce the right output? That is necessary but insufficient for production factory output. Several dimensions that standard benchmarks ignore matter in practice.

**Abstraction adherence.** Does the agent use existing libraries correctly, or does it reimplement functionality from scratch? This is one of the most common and most expensive failure modes in factory output, because reimplemented code passes all functional tests while creating a maintenance burden that grows with every agent run.

> **Case Study: Measuring Abstraction Adherence**
>
> Maria Gorinova (Tessl, AI Native Dev Ep 032) built an evaluation framework that tests agent capability against specific library APIs - not functional correctness ("does the code work?") but abstraction adherence ("does the code use existing libraries correctly?").[ANDev-032]
>
> The framework analyzes a library, generates coding questions paired with evaluation criteria that test correct use of the library's abstractions, runs the agent, and judges against those criteria. The results quantified what teams had suspected anecdotally: providing curated context about library APIs improved abstraction adherence by 35% on average. For libraries released in the last three years, improvement reached 50%. For features introduced after the model's training cutoff, the improvement was 90%.
>
> The practical implication: abstraction adherence is directly improvable through better context, but only measurable through evals. Without the framework, the team would have known that "context helps" as a general impression. With it, they could measure exactly which context mattered, for which libraries, and by how much.

**Internal quality.** Fowler examines whether AI-assisted code degrades modularity, testability, and readability over time - the "internal quality" that does not surface in test results but determines long-term maintainability.[Fowler-quality] His assessment: the question is under-studied because most research conflates autocomplete usage with agentic usage, which have fundamentally different quality profiles. An autocomplete suggestion that a human reviews and edits has a different quality distribution than a multi-file change generated autonomously by an agent. Factory operators should not wait for the research to catch up. Track review rejection reasons over time and categorize them: functional bugs, structural issues, convention violations, security concerns. If reviewers increasingly flag structural issues - large functions, tight coupling, missing abstractions - the factory has an internal quality problem that functional evals will not catch. Build eval criteria that test for these properties explicitly.

**Code churn as quality proxy.** GitClear's longitudinal analysis of 153 million changed lines tracks code reverted within two weeks as a quality signal. Their finding that churn is projected to double from the pre-AI baseline is a direct warning: high throughput without quality measurement creates maintenance debt faster than it was ever possible to create before.[GitClear-2025]

**Security beyond functional correctness.** Academic work confirms that code passing functional benchmarks still carries measurable security and maintainability defects, with the gap widening for less common languages.[LLM-security-quality] A 109-paper survey found systematic misalignment: academia measures correctness, practitioners care about maintainability and security, and current model behavior satisfies neither fully.[Quality-2511] Your eval suite should include security-focused scenarios alongside correctness scenarios. Generate tasks that require handling user input, database queries, authentication tokens, and file system access, then evaluate not just whether the output works but whether it handles these concerns safely. The static analysis tools from Chapter 11's validation layers catch known vulnerability patterns, but evals can test for the subtler judgment calls: does the agent default to the secure option when the spec is ambiguous?

## The Non-Determinism Problem

Setting temperature to zero does not guarantee identical outputs. GPU floating-point nondeterminism means the same prompt can produce different completions across runs, even with identical settings.[LLM-nondeterminism] This has direct implications for eval design: a single-run evaluation is unreliable. A scenario that passes once and fails once is not a flaky test - it is an honest measurement of a probabilistic system.

**Run each scenario multiple times.** Three to five runs provide fast feedback during development. Ten or more runs give statistical confidence when comparing configurations. Report pass rates with confidence intervals, not single pass/fail results. A scenario that passes three out of five times is meaningfully different from one that passes five out of five, and both are meaningfully different from one that passes one out of five. Single-run results hide this information.

**Use paired comparisons.** Running the same scenarios through two configurations and comparing their results controls for scenario difficulty. A factory that scores 75% on hard scenarios and a factory that scores 90% on easy ones cannot be compared meaningfully. Run both configurations against the same set, and the relative difference is what matters.

**Track trends over time.** A factory that drops from 82% to 78% after a context change has regressed, regardless of the absolute numbers. For rigorous comparison, paired statistical tests with effect size measures provide the minimum rigor needed to distinguish real changes from noise.[Eval-statistics] Most published eval results report means without variance, making it impossible to judge whether reported differences are meaningful. Your internal evals should not repeat this mistake.

## Evaluating Skills and Context

Distinct from evaluating factory output. The question here is not "did this PR pass?" but "does this skill or context document make the agent produce better PRs?"

Fowler and Böckeler draw a useful distinction between **feedforward guides** - context that steers the agent before it acts - and **feedback sensors** that observe output after.[Fowler-harness] Skills, instruction files, and context documents are guides. Evals are sensors. The open question they raise: what is the equivalent of code coverage for a harness? How do you know which agent behaviors your guides actually reach?

The practical methodology is A/B comparison. Run the same scenario set with and without a given skill or context document. Compare pass rates on the same scoring criteria. This is the only reliable way to know whether a piece of context is helping, hurting, or doing nothing. The results can be surprising: a context document that seems obviously helpful may have no measurable impact, while a seemingly minor addition - a list of deprecated APIs, a diagram of service dependencies - may produce large improvements on specific task types. Gorinova's abstraction adherence framework does exactly this for library documentation, and the methodology generalizes to any context type.[ANDev-032]

Sean Roberts connects this to a problem he calls the one-way ratchet.[ANDev-031] Context files - steering rules, architecture documentation, dependency descriptions - accumulate over time. Teams add rules but never remove them, because removal might cause a regression and nobody knows which rules are actually load-bearing. An eval suite makes pruning safe: remove a rule, run the suite, observe whether performance degrades. If it does not, the rule was dead weight consuming the context window. This is the safe pruning mechanism discussed in Chapter 3's context lifecycle.

This use case alone justifies building an eval suite. Without it, context growth is unchecked, and the context-attention tradeoff from Chapter 3 steadily degrades factory performance as rules accumulate faster than anyone removes them.

## Testing Discipline in the Agent Era

Kent Beck argues that test-driven development becomes more important with AI agents, not less. But he identifies a failure mode unique to agent-generated code: agents will modify or delete tests to make them pass rather than fixing the implementation.[Beck-augmented] The test suite must be treated as a human-owned constraint, not an agent-mutable artifact.

This leads to a pattern emerging across factory implementations: **locked tests**. Certain tests represent invariants that no agent run should be allowed to change. The locked set typically includes integration tests against external contracts, regression tests for previously-discovered bugs, and any test that encodes a business rule from the spec. The agent can add new tests. It cannot modify or remove locked ones. This boundary is enforced by the validation layer (Chapter 11) through file-level permissions or pre-commit hooks that reject changes to protected test files.

The decision about which tests to lock is itself an eval decision: you discover which tests are load-bearing by observing what breaks when they are absent. Run the factory on a scenario set, then temporarily unlock a test group and re-run. If pass rates do not change, those tests were not constraining agent behavior. If pass rates drop, the tests were doing real work. This is the testing analog of the context pruning methodology described above - empirical measurement of what matters rather than assumptions about what should matter.

Chad Fowler pushes this further with what he calls the **Phoenix Architecture**.[ANDev-047] In a world of regenerative software where code is routinely replaced rather than maintained, what persists is not the code itself but the invariants, metrics, constraints, and intent captured in evaluations. "The code that we have is a liability and the system is the asset." Under this framing, the eval suite is not an adjunct to the codebase - it is the durable specification of what the system must do. The code is a build artifact that the factory regenerates. The evals are what make that regeneration safe.

This is an aspirational position, not current practice for most organizations. But it clarifies the direction: as factory capability increases, the ratio of investment shifts from writing code to writing evals. The team that writes the best evals ships the best product, because the evals define what "best" means and the factory does the rest. Whether or not you adopt the full Phoenix Architecture, the principle is sound: invest more in specifying what the system should do and less in hand-crafting how it does it. The eval suite becomes the most important artifact the engineering team maintains.

## Eval Tooling and Economics

The tooling landscape ranges from single-purpose scripts to full platforms. Match the tool to your maturity level.

**Start with what you have.** A test runner (pytest, vitest) that invokes the agent, collects output, and runs deterministic assertions. A SQLite database of runs. A script that diffs pass rates between configurations. Husain's strongest practical advice: "Remove all friction from looking at data." Do not buy platforms until you have exhausted simple tools.[Husain-evals]

**Open source frameworks** add structure as your suite grows. promptfoo[promptfoo] is CLI-first, CI/CD-native, and MIT-licensed, with a dedicated guide for evaluating coding agents as integration tests against the full system. Arize Phoenix[Arize-Phoenix] is fully open source and self-hostable, built on OpenTelemetry, with LLM-as-judge, code-based, and human-label evaluators on traces and spans. OpenAI's evals framework[OpenAI-evals-repo] separates evaluation logic from solver logic, supporting both deterministic assertions and model-graded evaluation.

**Hosted platforms** add value when you need team collaboration on eval results, annotation workflows, or production monitoring integration. Tools like Braintrust and LangSmith offer agent-aware tracing combined with eval capabilities, including pairwise comparison interfaces and annotation queues for human labeling. The tradeoff is vendor dependency and cost versus setup time. As with other tooling decisions in this book, the choice depends on your team size, the volume of eval runs, and whether you need collaborative workflows around eval results or just a script that prints a table. Most teams should start with scripts and graduate to platforms only when the collaboration overhead of sharing CSV files becomes a bottleneck.

**Production monitoring closes the loop.** Evals are synthetic. Production is real. When production monitoring reveals a failure mode that the eval suite did not catch, that failure becomes a new eval scenario. Honeycomb argues that SLO-based monitoring catches the long-tail failures that only emerge under real workloads - the kind that no pre-deployment eval suite can fully anticipate.[Honeycomb-agents] The eval suite and the production monitor form a feedback loop: evals catch regressions before deployment, production monitoring catches surprises after, and surprises get encoded back into the eval suite.

**Cost management.** Evals consume tokens. A capability suite of twenty specs run five times each against a frontier model costs real money. Three strategies keep this manageable. First, Level 1 assertions are free: compilation checks, import verification, pattern matching require no LLM calls. Second, use cheaper models for judging when possible. Judge capability matters, but not every judgment needs the frontier model. Calibrate the cheaper judge against human labels and monitor drift. Third, cache agent outputs when tuning the judge. Do not re-run the agent to test a rubric change - score the cached outputs with the new rubric.

Run lightweight evals frequently and expensive evals on schedule. Deterministic assertions on every context change. Full LLM-judged task evals weekly or on significant configuration changes. Boundary evals monthly or on model upgrades. The cost of not running evals is higher than the cost of running them. A context change that silently degrades factory output by 10% costs far more in rework, review time, and production incidents than the tokens spent detecting it.

## The Eval Development Lifecycle

Evals are not infrastructure you build once. They evolve with the factory through a repeating cycle.

**Define what good looks like.** Scenarios, rubrics, pass criteria. This is the hardest step and the most important. The definition of correctness matters more than the words in any individual prompt.[Husain-evals] Get this wrong and every subsequent step optimizes toward the wrong target.

**Run evals and analyze failures.** Not just pass/fail rates - categorize failures. Which scenarios fail? Which rubric criteria? Is the judge miscalibrated, or is the agent genuinely failing? Error categorization turns a number ("78% pass rate") into actionable information ("12% of failures are ORM bypasses, 6% are missing error handling, 4% are hallucinated imports").

**Improve factory configuration based on findings.** Update context documents, adjust skills, modify validation rules. The eval suite is the feedback loop that makes these changes safe. Without it, every configuration change is a gamble. With it, you can measure the impact of each change before it reaches production.

**Observe production.** Evals are synthetic. Production reveals failure modes that no synthetic corpus anticipates. When production surfaces a new pattern - a class of review rejection, a recurring type of validation failure, a security finding from a penetration test - add it to the eval corpus. The suite grows from reality, not imagination. The best eval suites are those where every scenario has a story: "this is here because we shipped a bug that did X."

**Recalibrate.** Models improve. Codebases change. Team conventions evolve. Scenarios that were hard six months ago may be trivial now - and new scenarios that did not exist six months ago may be critical. Retire stale scenarios, promote boundary evals that now pass consistently, add scenarios from newly discovered failure modes. The eval suite should always push against the factory's current boundaries, not its historical ones. A passing eval suite that never changes is not evidence of a capable factory - it is evidence of a stale eval suite. Schedule a quarterly review of the eval corpus itself: which scenarios are still relevant, which have become too easy, which failure categories are missing.

Simon Willison captures the practitioner stance: writing good automated evals is "the most needed skill" for building useful LLM applications.[Willison-evals] For a factory operator, it is the skill that separates engineering from gambling.
