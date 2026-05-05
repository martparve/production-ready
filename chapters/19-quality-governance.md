# Chapter 19: Quality Governance: Org-Wide Standards

The factory runs across multiple teams. Three write TypeScript. Two write Python. One writes Rust. The rest mix and match depending on when they started and what they inherited. Each team has its own repo, its own CI config, its own instruction files, its own conventions. The agents serving each team have been tuned for that team's stack and workflow.

Now someone asks: "Do all our APIs validate input against injection attacks?" And nobody can answer confidently, because the question cuts across every team, every repo, every agent configuration, and every CI pipeline in the organization.

The governance problem is not whether individual teams produce good code - the validation gates from Chapter 11 handle that. The governance problem is whether the organization as a whole maintains consistent quality floors that no team can accidentally drop below. In a traditional org, governance relies on humans following documented standards. In a headless factory, that approach fails. Humans are not writing the code. They are not even present when the code is produced. If governance is not encoded in infrastructure, it does not exist.

## What Gets Governed at Org Level

The first instinct is to govern everything. Resist it. Every org-level standard creates friction for every team, on every task, forever. The leverage of centralized governance comes from restraint: a few critical standards that prevent catastrophic failures, not a comprehensive style guide that annoys everyone into workarounds.

In practice, organizations that run headless factories have converged on seven categories worth governing at the org level.

**Security minimums.** No hardcoded secrets in source. Dependency audit for known vulnerabilities. Static application security testing (SAST) on every change. These are non-negotiable because a single team's mistake becomes the entire organization's breach. The agent does not know which secrets are test-only and which are production. The pipeline has to catch all of them.

**Test coverage floors.** Not aspirational targets - hard floors. If your org says 70% line coverage, no team ships below 70%. The number matters less than its enforcement. A floor of 50% that is actually enforced beats a target of 90% that three teams quietly ignore. And in a headless factory, agents are prone to writing tests that exercise the happy path and skip edge cases. The coverage floor is a blunt instrument that forces the agent to keep going.

**API design rules.** Consistent error formats. Versioning schemes. Authentication patterns. When fifteen teams each invent their own error response structure, every team that consumes another team's API pays a tax. Org-level API standards reduce that tax to zero for the common cases. These are especially important for agent-produced APIs because agents default to whatever patterns they saw most frequently in training data, which may bear no resemblance to your internal conventions.

**Accessibility.** WCAG 2.1 AA compliance, or whatever your regulatory environment requires. This one gets governance because teams consistently underweight it when left to their own judgment, and because the cost of retrofitting accessibility is five to ten times the cost of building it in. Agents produce inaccessible UI by default unless explicitly told not to. A governance gate catches what the agent missed.

**Performance budgets.** Maximum page load time. Maximum API latency at p95. Maximum bundle size. These prevent the slow creep that happens when each team adds "just one more dependency" and nobody notices the cumulative effect until the product is measurably slower than the competition.

**Data handling.** PII classification, encryption at rest and in transit, data retention policies. These are governed centrally because the regulatory consequences of getting them wrong are borne by the entire company, not the individual team. An agent that stores email addresses in a plaintext log file may have technically completed its task. The GDPR auditor will not be impressed.

**Documentation for public interfaces.** Any interface consumed by teams outside your own - APIs, libraries, event schemas - must have documentation that meets an org-defined minimum: description, input/output types, error conditions, at least one example. This standard exists because in an AI-native org, the consumers of your interface are also agents. An undocumented API is an API that no agent can use correctly without hallucinating, which means every consumer team eats the cost of your team's documentation gap.

Seven categories. Not seventy. The temptation to add "code style consistency" or "preferred logging framework" or "mandatory use of the internal component library" is strong, and usually wrong. Those are team-level concerns. They matter, but they do not merit org-level governance unless there is a concrete, measurable cost to inconsistency across teams.

## How Standards Are Encoded

A standard that exists only as a document in Confluence is not a standard - it is a suggestion. In the headless factory, standards must be machine-readable because the machines are doing the work.

Standards encode into two delivery mechanisms, mirroring the context hierarchy from Chapter 8.

**Org-level instruction files.** These sit at the top of the hierarchy. Every agent session in every repo inherits them. They contain the behavioral rules that agents must follow: "never commit files containing secrets," "all API responses must use the standard error envelope," "all new React components must include aria labels." These are the rules category from Chapter 3 - always-on, unconditional, non-negotiable.

The instruction files live in a central repository, version-controlled and owned by a standards body (more on who that is shortly). They are distributed to individual repos through whatever mechanism the org uses: git submodules, package dependencies, CI script that pulls latest at build time, or a dedicated context registry. The mechanism matters less than the invariant: no team can edit, override, or delete the org-level instructions in their own repo. The pipeline rejects the attempt.

**Shared validation gate configs.** These are the CI-side enforcement. Org-level SAST rules, coverage thresholds, dependency audit policies, performance budgets - all defined as configs in the central repo and referenced by every team's CI pipeline. When the pipeline runs, it pulls the current org configs and applies them. A team cannot pass CI by removing a security check from their local config because the check does not live in their local config.

This creates a clean separation. Instruction files tell the agent what to do. Validation gates check whether the agent did it. Both are necessary. Instructions without validation means you are hoping the agent follows the rules. Validation without instructions means you are waiting for the agent to fail and then catching the failure. Together, they form a closed loop: the agent receives the standard, attempts to follow it, and the pipeline verifies compliance before the code can merge.

The central repo should be treated like infrastructure code. Changes go through pull requests. Reviews require at least two approvers from the standards body. Every change is tagged with a semver release. Breaking changes get migration guides. This is not bureaucracy for its own sake - it is risk management. A bad rule pushed to every agent session across fifteen teams will produce fifteen teams' worth of broken output before anyone notices.

## Hooks as Automated Governance

Chapter 11 covered validation gates that run in CI. But governance can also fire during development, not just after the code is committed. This is where hooks come in.

Kiro[Kiro], the spec-driven IDE built at AWS, introduced a hook model that fires on file-level events: file create, file save, file delete, and PR open. Each hook watches for a glob pattern and triggers an agent action when matched.

> **Case Study: Real-Time Standards Enforcement with Hooks**
>
> Nikhil Swaminathan[ANDev-016] (Product Lead, Kiro) demonstrated hooks as a governance mechanism during a live demo. His team had configured a "component SRP validator" hook that fired whenever a new React component was created. The hook analyzed the component and flagged single-responsibility principle violations before the developer moved on to the next file.
>
> "As a team, I can enforce these practices across my team," Swaminathan explained. "So even when we come up with the design, we are actually making the right decisions." Other hooks in the demo included a documentation updater that kept the README in sync when TypeScript files changed, and a localization checker that ensured string literals were properly internationalized.
>
> Richard Threlkeld (Engineer, Kiro) emphasized composability: "All these things are fully composable in the system. Hooks can trigger at spec workflow stages for matching file globs. Similarly, steering can mention 'do X in spec workflow.'" The practical effect is that governance rules fire in real time during agent execution, catching violations at the moment they are introduced rather than minutes later in CI.

The hook model changes the economics of governance. A CI gate catches a violation after the agent has finished all its work, requiring the agent to re-enter the task, understand the violation, and fix it - potentially cascading changes through multiple files. A hook catches the violation immediately, while the agent still has full context on what it was doing. The fix is cheaper. The feedback loop is tighter.

For org-level governance, hooks become particularly powerful when they are centrally defined and distributed alongside org-level instruction files. A security hook that flags hardcoded credentials on file save. An API design hook that validates response structures when controller files change. An accessibility hook that checks ARIA attributes when JSX files are created. These fire regardless of which team is writing the code, enforcing the same standards with the same timing everywhere.

The combination of hooks (real-time, during development) and CI gates (batch, after completion) creates defense in depth. The hook catches most violations early and cheap. The CI gate catches anything the hook missed, because hooks depend on glob patterns that may not cover every case, and because agents can modify files without triggering the expected events if they use bulk operations.

## The Inheritance Model

The simplest governance model is also the right one: the org sets the floor, teams can raise it, nobody can lower it.

This mirrors the instruction file hierarchy from Chapter 8, but with a critical enforcement difference. In the instruction hierarchy, a module-level file can override a repo-level convention because there might be a legitimate local reason to diverge. In the governance model, a team-level config cannot override an org-level gate. The override direction is one-way: stricter only.

If the org floor for test coverage is 70%, a team can set their floor to 85%. They cannot set it to 60%. If the org requires SAST on every PR, a team can add additional security checks. They cannot disable SAST for their repo. If the org mandates that all APIs return errors in the standard envelope, a team can add extra fields to the envelope. They cannot use a different format.

This works because the enforcement happens in CI infrastructure that teams do not control. The org-level validation gates run from centrally managed configs. Teams add their own gates on top. The pipeline evaluates all gates. A PR must pass both the org gates and the team gates to merge.

Practically, the config structure looks like this: the org publishes a base CI config. Each team's pipeline extends that base config with team-specific additions. The base config is pulled fresh on every pipeline run, so teams automatically get updates. The extension mechanism is additive only - teams can add steps, add checks, add thresholds. They cannot remove or lower anything from the base.

This creates a predictable floor. When someone asks "do all our APIs validate input?" the answer is provably yes, because the validation check runs in every pipeline and cannot be removed. The proof is not "we told teams to do it." The proof is "the infrastructure enforces it."

## Distribution and Versioning

Org-level standards change. New security threats emerge. Regulatory requirements shift. The standards body learns from production incidents and tightens requirements accordingly. The distribution mechanism must handle these changes without breaking every team's pipeline simultaneously.

Three distribution models are common in practice.

**Git submodules.** The org standards repo is included as a submodule in every team repo. Teams run `git submodule update` to get the latest. This is simple but has a well-known failure mode: teams forget to update, and their standards drift behind. In a headless factory, the factory infrastructure can enforce that submodules are updated to the latest tagged release before every pipeline run.

**Package dependencies.** Org standards are published as a package (npm, pip, internal registry) that team repos declare as a dev dependency. Version pinning with automated upgrade PRs (Dependabot, Renovate) keeps teams current. This has better tooling than submodules but introduces the package manager as a dependency of governance.

**CI-time pull.** The pipeline itself fetches the current org configs at runtime, directly from the central repo. No local copy exists in the team repo. This is the most reliable enforcement mechanism because there is nothing local to drift or override. The tradeoff is that a bad push to the central repo affects all teams immediately.

Regardless of mechanism, versioning matters. Org configs should follow semantic versioning. A patch release (1.0.1) fixes a bug in an existing rule. A minor release (1.1.0) adds a new check that teams should pass without changes. A major release (2.0.0) changes an existing check in a way that may require teams to update their code.

Grace periods prevent major releases from breaking everything at once. When the standards body introduces a new requirement - say, mandatory input validation on all API endpoints - the rollout follows a pattern: announce the requirement, release the check in warning-only mode for thirty days, publish a migration guide with examples, then flip the check to blocking. Teams that prepared during the grace period are unaffected. Teams that ignored the warnings have thirty days of CI warnings in their build logs that document exactly when they were told and what they need to do.

The migration guide is not optional, especially in a headless factory. The guide is context that the agent needs to fix the code. A migration guide that says "update all API endpoints to validate input" is useless. A migration guide that says "add `validateInput(req.body, schema)` as the first line of every route handler, where `schema` is the Zod schema exported from the adjacent `.schema.ts` file" is something an agent can act on directly. Write migration guides for machines, not for people.

## Mapping to a Recognized Framework

The governance categories above are practical, derived from what breaks in production. But they also map cleanly to the NIST AI Risk Management Framework (AI RMF 1.0), published with input from over 240 contributing organizations and updated in July 2024 with a Generative AI Profile (NIST AI 600-1) that addresses LLM-specific risks.[NIST-AI] The framework defines four core functions: Govern, Map, Measure, and Manage. In the factory context, Govern corresponds to the org-level instruction files, quality gates, and policies that constrain agent behavior - the rules the factory cannot override. Map is the process of identifying which factory outputs carry risk: a generated API endpoint handling financial data is not the same risk class as a generated utility function for string formatting. Measure translates directly to evals and validation metrics - coverage floors, SAST results, spec compliance scores, first-pass success rates. Manage is the feedback loop: when a validation gate catches a pattern of failures, the standards body updates the instruction files or tightens the gate, closing the cycle. NIST's framework is voluntary, not regulatory, but it gives the governance model described in this chapter a recognized structure that auditors, compliance teams, and regulators understand. Organizations building headless factories should be mapping their governance artifacts to NIST's four functions now, because the regulatory landscape is moving fast.

## The Regulatory Landscape

The EU AI Act (Regulation 2024/1689) is the first comprehensive AI regulation to reach full legal force, with complete application beginning August 2026.[EU-AI-Act] It classifies AI systems into four risk tiers: minimal, limited, high, and unacceptable. Factories generating code for high-risk applications - medical device software, financial trading systems, critical infrastructure control - will need to demonstrate compliance with requirements covering transparency, human oversight, and technical documentation. The practical implications are more immediate than most engineering leaders realize. The Act's General-Purpose AI (GPAI) provisions require logging of training data, watermarking of AI-generated outputs, and provenance tracking - requirements that touch the factory's core pipeline. The audit trail the factory already produces (spec approval, implementation trace, validation results, merge decision) is the raw material for compliance documentation. Organizations that have been treating this trail as a debugging convenience will need to treat it as a legal record. Augment Code's analysis of the Act's impact on engineering teams identifies three compliance categories: documentation obligations (what was generated, by which model, with what inputs), risk assessment requirements (which outputs require human review before deployment), and ongoing monitoring mandates (tracking the behavior of AI-generated code in production).[Augment-EU] For factory operators, the practical takeaway is that the governance infrastructure described in this chapter - centralized standards, automated enforcement, compliance dashboards, exception tracking - is not just good engineering practice. It is the foundation for regulatory compliance in any jurisdiction that follows the EU's lead, and several already are.

## The Perception Gap in Governance

Governance decisions do not happen in a vacuum. They happen inside organizations where leadership and engineers often have sharply different views of what AI tooling delivers. The DX/Atlassian State of Developer Experience 2024 report found that 38% of engineering leaders see AI tools as a significant productivity booster, while 62% of developers say those same tools have little or no measurable impact on their productivity.[DX-2024] This perception gap matters for governance because it shapes what gets funded, what gets measured, and what gets enforced. Leaders who believe AI is delivering large gains may resist governance investment on the grounds that "it's already working." Engineers who see minimal impact may resist adoption of governance tools they perceive as overhead on top of a system that is not helping them. The governance body must account for both perspectives: building measurement infrastructure that produces objective data (not opinion surveys) about factory output quality, and using that data to calibrate both leadership expectations and engineering feedback. Without this grounding in measured reality, governance becomes either too lax (because leadership assumes everything is fine) or too burdensome (because engineers demand excessive checks on output they do not trust).

## Compliance Validation

Governance without visibility is governance on faith. You need to know the current compliance state of every team, every repo, every pipeline.

The compliance dashboard aggregates validation gate results across the organization. At minimum, it answers four questions:

1. Which repos are currently passing all org-level gates?
2. Which repos have failing gates, and which gates are they failing?
3. How long has each failure persisted?
4. What is the trend - are failures increasing or decreasing?

The dashboard is not a vanity metric. It is the input to a prioritization decision. If three repos have been failing the dependency audit gate for two weeks, that is an operational problem, not a reporting problem. Someone needs to fix it or grant an explicit exception.

Automated compliance audits run on a schedule independent of CI. A nightly job scans all repos for compliance with current standards, even repos that have not had a recent commit. This catches drift: a dependency that was safe last month but now has a known vulnerability, a certificate that was valid when deployed but expires next week, a standard that was tightened since the repo's last pipeline run.

Exception management keeps the system honest. Sometimes a team has a legitimate reason to temporarily violate an org standard. Legacy code that predates the standard. A third-party library that requires a specific pattern incompatible with the rule. A time-sensitive hotfix that cannot wait for full compliance.

Exceptions must have three properties: they must be explicit (documented in the central system, not hidden in a team's local config), they must have an expiry date (not "until we get around to fixing it" but "expires 2026-09-15"), and they must have an owner (a named person responsible for resolving the exception before it expires). When the expiry date passes, the exception disappears and the gate starts blocking again. If the team has not fixed the underlying issue, their pipeline breaks - which is exactly the intended behavior, because it forces resolution rather than allowing indefinite drift.

## The Governance Body

Someone has to own the standards. The options are well-understood.

**Dedicated platform team.** A team whose job is to maintain the factory infrastructure, including org-level standards. This is the cleanest model. The platform team owns the central config repo, manages releases, runs compliance dashboards, and supports teams with migration. The risk is disconnection: a platform team that has never worked in the product codebases may create standards that are theoretically sound and practically infuriating.

**Cross-team architecture guild.** Representatives from each team meet regularly to propose, debate, and approve standards. This has better buy-in because the people setting standards also live with them. The risk is speed: a guild that meets biweekly takes months to ratify a new standard, and by the time it ships, the threat it was designed to address has already caused damage.

**CTO/CPO office.** Executive mandate. Fast. Clear. Carries authority. The risk is obvious: standards set without practitioner input tend to be either too vague to enforce or too specific to the wrong stack.

The practical answer is a combination. A small platform team maintains the infrastructure and proposes standards. A lightweight RFC (request for comments) process gives teams a window to provide feedback. The CTO has final authority to break ties or mandate urgent changes (like a new security requirement after an incident).

The RFC process needs guardrails to avoid becoming a committee. Set a feedback window of one week. If no blocking objections are raised, the RFC is accepted by default. Blocking objections must include a concrete alternative, not just "I don't like it." The goal is not consensus - it is informed decision-making with a bias toward action.

How to avoid bottleneck: keep the number of org-level standards small. Every standard you add to the org level is a standard you must maintain, distribute, support, migrate, and enforce across every team forever. The bar for addition should be high: "does this prevent a category of failure that crosses team boundaries and has significant business impact?" If yes, govern it centrally. If no, let teams decide for themselves.

## Handling Non-Compliance

A team is failing an org gate. Now what?

The default response in many organizations is blame. Who turned this off? Why isn't this fixed? This is exactly wrong. In a headless factory, non-compliance almost always has a root cause in context or configuration, not in human negligence. The agent did not follow the standard because its instruction file was stale. The gate failed because the team's CI config pulled an old version of the org base. The dependency audit flagged a false positive that the team worked around by disabling the check entirely.

The response to non-compliance should follow a diagnostic sequence:

**First: is the context correct?** Does the team's instruction file include the current org-level rules? Is the agent actually receiving the standard it is supposed to follow? If the agent never saw the rule, the agent cannot follow it. Fix the context delivery.

**Second: is the configuration correct?** Is the team's CI pipeline extending the current org base config? Is the submodule up to date? Is the package dependency pinned to the right version? Configuration drift is the most common cause of non-compliance in a distributed factory.

**Third: is the standard itself practical?** If multiple teams are failing the same gate, the standard may be wrong. A coverage threshold of 90% may be appropriate for a mature service but unreachable for a prototype. An API format rule may conflict with a framework's built-in conventions. The governance body should review standards that cause widespread failure, not double down on enforcement.

**Fourth: does the team need support?** Some standards require significant refactoring to adopt. A team with 200 API endpoints that do not validate input needs help, not a deadline. The platform team should provide tooling, migration scripts, and agent-ready context documents that make compliance achievable.

Escalation is the last step, not the first. And escalation means "leadership helps remove blockers," not "leadership applies pressure." The goal of governance is consistent quality, not consistent punishment.

## Tooling and Decision Matrix

Choosing governance tooling is a build-versus-buy decision with strong opinions on both sides. Here is a decision matrix based on what works in practice.

| Concern | Tool/Approach | Notes |
|---------|---------------|-------|
| Secret detection | Pre-commit hooks + CI gate (Gitleaks, TruffleHog) | Must run both locally and in CI. Agents bypass local hooks in headless mode, so CI gate is mandatory. |
| Dependency audit | Dependabot/Renovate + SBOM generation | Automated PRs for vulnerable deps. SBOM for compliance reporting. |
| SAST | Semgrep, CodeQL, or Snyk Code | Custom rules for org-specific patterns. Run as CI gate with centrally managed rulesets. |
| Coverage enforcement | Native test runner + threshold in CI config | `--coverage --min-coverage=70` or equivalent. Org threshold in base config, team threshold in team config. |
| API linting | Spectral (OpenAPI), custom schema validators | Validate against org API style guide on every spec change. |
| Accessibility | axe-core, Pa11y in CI | Run against rendered output, not just source. Agents produce inaccessible markup at high rates. |
| Performance budgets | Lighthouse CI, custom bundle size checks | Track over time. Alert on regression, block on threshold breach. |
| Compliance dashboard | Custom aggregation from CI results, or commercial (Backstage, Cortex) | Must aggregate across all repos. Nightly scan for drift detection. |
| Instruction file distribution | Git submodules, package deps, or CI-time pull | CI-time pull is most tamper-resistant. |
| Exception tracking | Custom database or ticketing system with expiry dates | Must be queryable by the compliance dashboard. |

The most common mistake is over-investing in commercial governance platforms before establishing what standards you actually need. Start with a central git repo, a base CI config, and a spreadsheet tracking compliance. Graduate to purpose-built tooling when the manual approach breaks down, which usually happens around twenty repos or fifty developers.

## Governance as Factory Infrastructure

In a traditional org, governance is a cultural practice. You write standards, you train people, you hope they follow the rules, you audit periodically and find that they did not. The cycle repeats.

In a headless factory, governance is infrastructure. The standards are code. The enforcement is automated. The compliance state is measured continuously. A new standard goes from RFC to universal enforcement through a deployment pipeline, not through an email campaign.

> **Case Study: Steering and Hooks as Governance Primitives**
>
> Nikhil Swaminathan described how Kiro's steering files - markdown documents that guide agent behavior on every interaction - function as governance primitives when shared across teams. "All these files are actually in your repository. So if I switch to the Explorer view, you'll see there's this .kiro folder here. The steering files are just markdown files. You can check them in."[ANDev-016]
>
> When asked whether these could be shared at the org level, Swaminathan confirmed it was the most-requested feature from early customers: "A big feature request we've been getting is, 'hey, we have actually multiple teams that need to align on certain rules. How do we define that?'" The pattern of repo-checked governance artifacts, composable with hooks that enforce them in real time, points toward a model where governance is not something teams adopt but something the factory applies.

This is the power of the headless model for governance. In interactive development, governance is a tax on developer attention. Developers have to remember the rules, check their own compliance, and choose to follow the standards even when they are in a hurry. Some do. Some do not. The result is inconsistency.

In headless mode, the agent has no choice. It receives the org-level instructions, produces code, and the pipeline validates the output against org-level gates. If the output fails, it does not merge. The agent does not get tired, does not cut corners on Friday afternoon, does not decide that this one PR is too urgent for the usual checks. Governance is not a request - it is a constraint of the execution environment. That distinction is the difference between a quality program and a quality system. Programs depend on human compliance. Systems enforce invariants mechanically. The headless factory makes mechanical enforcement the default, which means the quality floor is real - not aspirational, not documented-but-ignored, but actually, measurably real. Every commit, every repo, every team.

Build the floor into the infrastructure. Then stop worrying about whether people are following the rules.
