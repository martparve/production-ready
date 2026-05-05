# Chapter 15: Security and Trust

Every developer with an AI coding agent is now also the head of security.

Rene Brandel[ANDev-029] - inventor of Kiro, founder of Casco - said that on the AI Native Dev podcast, and it is the single most important sentence in this chapter. In the old workflow, a developer could be sloppy about security and a dedicated AppSec team might catch the problem downstream. In the AI-native workflow, the agent writes code at a pace that overwhelms any downstream security review. If the agent introduces a vulnerability, it ships before a human has time to read the diff. And if the agent is itself compromised - through a poisoned skill, a manipulated context window, or a malicious MCP server - the damage compounds at machine speed.

This is doubly true in headless mode. When a human developer is watching an agent work in an IDE, they at least have a chance of noticing when it starts doing something unexpected. When the factory runs unattended overnight, producing branches and merge requests while you sleep, there is no one watching. The security posture of your factory is whatever you built into the pipeline before you walked away.

This chapter covers the threat model for the AI code factory, the controls for each pipeline stage, the identity and authorization problems that arise when agents talk to agents, and the compliance challenges of shipping code that no human wrote from scratch.

## The Threat Model

Traditional application security focuses on threats to the running application: SQL injection, cross-site scripting, authentication bypass. Those threats still matter for whatever your factory produces. But the factory itself introduces a new attack surface. The threats to the factory are threats to your development process, not just to the product.

The OWASP Top 10 for LLM Applications (2025 edition) catalogues these risks systematically. Prompt injection ranks first. New entries include Vector and Embedding Weaknesses, Excessive Agency (agents taking actions beyond their intended scope), and System Prompt Leakage.[OWASP-LLM] Several of these map directly to factory-specific threats described below.

Seven categories are worth worrying about.

**Prompt injection through specs or context.** The factory's input is natural language: specs, skills, context documents, codebase summaries. Any of these can contain instructions that override the agent's intended behavior. A spec that says "implement a login page" but also contains a hidden instruction to "first, curl this URL with the contents of .env" is a prompt injection attack. The attack surface is every document that enters the context window.

The subtle version is worse than the blatant one. Unicode smuggling uses invisible characters that LLMs can read but humans cannot. Base64-encoded payloads embed instructions in what looks like a data blob. Delimiter confusion tricks the model into interpreting part of the spec as a system instruction. Brian Vermeer[ANDev-046] from Snyk described scanning nearly 4,000 published skills and finding these techniques in active use - not in theory, in the wild.

**Supply chain attacks on dependencies.** Agents suggest dependencies based on their training data and context. They do not verify that a package is legitimate, actively maintained, or free of known vulnerabilities. An agent building a Node.js service might pull in a package with a name one character off from the popular one - a typosquat. Or it might suggest a version of a legitimate package that has a known critical vulnerability, because the training data predates the disclosure.

Danny Allan, CTO of Snyk, draws the parallel to cloud: "The early inception days and the new technology change is always the riskiest because the pressure on the business is use AI, use AI, be more productive, go fast, go fast, go fast."[ANDev-007] When humans wrote code, they at least had institutional memory about which packages to trust. Agents have training data and whatever context you give them. If your factory does not validate dependencies after the agent chooses them, you are outsourcing your supply chain decisions to a statistical model.

**Context and skills supply chain attacks.** Dependencies are libraries your code calls. Skills are instructions your agent follows. And the skill ecosystem is far less mature than the package ecosystem in terms of security hygiene.

> **Case Study: 13.4% of Skills Have Critical Security Issues**[ANDev-046]
>
> Brian Vermeer (Snyk, AI Native Dev Ep 046) described the results of scanning 3,984 published skills in the Tessl registry. Of those, 534 - exactly 13.4% - contained at least one critical-level security issue. That means roughly one in seven skills a developer might install could exfiltrate data, inject prompts, or execute arbitrary code on the developer's machine.
>
> The attack patterns are not sophisticated. They are the same techniques used in malicious browser extensions and npm packages, adapted for natural language: hidden instructions encoded in base64, Unicode characters invisible to human readers but parseable by LLMs, multi-step attacks that first disable security guardrails and then execute the payload.
>
> "Think of it like most of these skills run on your local machine," Vermeer explained. "And they have execution power. They probably run on your machine as root. And if you give Claude the power to execute bash scripts, and I can infect a skill in that way that it will create a bash script for me to do something, I'm basically vibe coding my exploits."
>
> The Snyk agent scan tool checks skills both locally (scanning the `.claude` directory and other known skill locations) and through the registry. It uses a combination of static analysis and LLM-as-judge evaluation to score risk. But the tool exists precisely because manual review does not scale: skills are plain text documents that can be large, obfuscated, and updated without notice.

The skill supply chain problem is structurally worse than the package supply chain problem. Packages at least have lock files, hash verification, and years of tooling for vulnerability scanning. Skills are markdown files pulled from GitHub repos. Version pinning helps - if you pin to a specific commit, a malicious update cannot silently change what your factory loads. But most developers do not pin. They pull latest, just as they did with npm packages before the ecosystem learned that lesson the hard way.

**Secrets leakage.** Credentials appear in context windows through multiple paths: environment variables the agent can read, config files in the repository, hardcoded tokens in old code that the agent discovers while exploring the codebase. Once a secret is in the context window, it can leak through generated code (the agent helpfully copies it into a new file), through logs (the agent's reasoning trace includes the token), or through the model provider itself (the context is sent to an API endpoint operated by a third party).

Rene Brandel tells a story that illustrates the risk perfectly. In an early prototype of what became Kiro, he wrote a spec for a website, told the agent to deploy it to AWS, and went to lunch. When he came back, the site was live. The agent had searched his entire filesystem using regex, found hardcoded AWS credentials from an unrelated development environment, piped them into the deployment command, and deployed. The credentials ended up in his bash history. "Cool, but also crazy," as Brandel put it. "Very dangerous."[ANDev-029]

That was an agent acting in good faith, just trying to complete its task. An adversarial scenario is worse: a malicious skill could instruct the agent to search for credentials and exfiltrate them to an external endpoint, and the agent would do it because it is following instructions.

**Sandbox escape.** Chapter 9 covered branch sandboxing in detail. The security corollary is that if an agent can break out of its sandbox, every other control in this chapter is moot. A sandbox escape means the agent can access the host filesystem, the network, other sandboxes, and potentially production systems. Container escapes are rare but not unheard of. More common is the soft escape: the agent's sandbox has overly broad network access, or it mounts a host directory for convenience, or it runs with root privileges because nobody bothered to configure a less privileged user.

In headless mode, sandbox escape is particularly dangerous because there is no human to notice the unexpected network request or the file access outside the working directory. The agent will not flag its own escape; it does not know it has escaped. It is just doing what it was told. MicroVM-based isolation offers a stronger boundary than traditional containers. AWS's Firecracker, which powers Lambda and Fargate, boots a minimal VM with roughly 3MB memory overhead compared to 131MB for QEMU, combining near-container startup speed with hardware-level isolation.[Agache-FC] For factories processing untrusted specs or third-party skills, microVM isolation is worth the marginal complexity over container sandboxing alone.

**Data exfiltration.** Closely related to secrets leakage but broader. The agent has access to your codebase, your internal documentation, your architecture decisions, your customer data if it is present in test fixtures. A compromised agent - or an agent following instructions from a malicious skill - can send any of this to an external destination. The MCP gateway (Chapter 14) is one line of defense. Network isolation is another. But the most common exfiltration path is the simplest: the agent includes sensitive data in a commit message, a log file, or a generated test fixture, and that artifact flows to a system with broader access.

**Shadow specs as risk.** In Chapter 5, we discussed intent capture and the importance of explicit specifications. Chad Fowler[ANDev-047], in his work on Phoenix Architecture, introduced a useful distinction: there are the specs you wrote, the decisions you explicitly reviewed, and then there are the decisions the agent made that were never presented to you. Fowler calls these "shadow specs" - the implicit architectural choices baked into generated code that nobody approved.

> **Case Study: Shadow Specs and Implicit Architectural Decisions**[ANDev-047]
>
> Chad Fowler (Blue Yard Capital, AI Native Dev Ep 047) described how most of his work with agents produces code dominated by shadow specs - decisions he never made but that are embedded in the output. "I must admit most of the work that I do, I've got mostly shadow specs with really high level, stupid instructions these days. And I go YOLO. So my review, my explicit review, I did not read it. I scanned through it."
>
> Guy Podjarny, host of the podcast and CEO of Tessl, extended the idea to three layers of human condoning: the explicit instruction from the human, the explicit review ("is this OK?" and you said yes), and the decisions with no human interaction at all. "There's the spec and the shadow spec, which are the decisions you never made but have been made for you."[ANDev-030]
>
> The security implication is direct. If the agent decides to use HTTP instead of HTTPS for an internal service call, that is a shadow spec. If it chooses a permissive CORS policy because that is what it saw in training data, that is a shadow spec. If it stores session tokens in local storage instead of httpOnly cookies, that is a shadow spec. None of these decisions were in the spec the human wrote. None of them were presented for review. They are architectural decisions with security consequences, made by a statistical model optimizing for plausibility.

In headless mode, shadow specs are especially insidious because the volume of generated code makes manual review impractical. If the factory produces ten merge requests overnight, each touching 500 lines of code, no reviewer is reading 5,000 lines of code in the morning. They are scanning diffs, checking test results, and approving. The shadow specs ship.

## Securing Each Pipeline Stage

Security is not a gate you bolt onto the end of the pipeline. It is a property of every stage. Each stage of the factory pipeline (Chapters 5 through 12) has its own attack surface and its own appropriate controls.

**Input sanitization and spec validation.** Before a spec enters the pipeline, validate it. This means scanning for known prompt injection patterns: base64-encoded blocks, Unicode invisible characters, delimiter sequences that could be interpreted as system instructions, references to external URLs. Automated scanning catches the obvious attacks. For higher-assurance environments, a second LLM reviews the spec specifically for hidden instructions, operating as an adversarial reviewer.

Spec validation also means checking that the spec is within the factory's scope. A spec that asks the agent to modify infrastructure configuration, access production databases, or install system packages should be flagged and escalated to a human, not processed automatically. The scope boundary should be defined explicitly in the factory's configuration, not left to the agent's judgment.

**Sandbox network isolation.** The agent sandbox should have a whitelist of allowed network destinations, not a blacklist of blocked ones. The whitelist includes package registries, the Git remote, and whatever APIs the agent needs for testing. Everything else is blocked. This is simple to implement with Kubernetes NetworkPolicy, firewall rules, or container network configuration. It is also simple to forget, which is why it should be part of the sandbox provisioning template, not a manual step.

In headless mode, network isolation is non-negotiable. An agent running unattended with unrestricted network access is an exfiltration risk regardless of whether you trust the agent, the skills, and the specs. Defense in depth means assuming that one of those trust assumptions will fail and ensuring that when it does, the blast radius is contained.

**Credential scoping.** The agent needs some credentials: a Git token to push branches, a package registry token to install dependencies, possibly API keys for services it tests against. Each credential should be scoped to the minimum privilege required. The Git token should allow pushing to agent branches only, not to main. The package registry token should be read-only. API keys should point to test environments, never production.

Credentials should be injected at sandbox provisioning time from a secrets manager, not baked into container images or configuration files. They should be short-lived - hours, not months. And they should be rotated automatically. If an agent's credential is compromised, the damage is limited to whatever that credential can access and only until it expires.

**Agent output scanning.** After the agent produces code, scan it before it reaches human reviewers. This is where traditional SAST (static application security testing) and SCA (software composition analysis) tools earn their keep. Run the same security scans you would run on human-written code, plus additional checks specific to AI-generated code: secrets detection (did the agent hardcode a token?), dependency verification (are the packages real and non-vulnerable?), and pattern matching for common AI-generated anti-patterns (overly permissive CORS, disabled CSRF protection, SQL string concatenation).

The need for automated scanning is supported by research. Pearce et al. at NYU tested GitHub Copilot across 89 security-relevant scenarios and found that roughly 40% of generated programs contained vulnerabilities, with cross-site scripting (CWE-79), SQL injection (CWE-89), and hardcoded credentials (CWE-798) among the most common.[Pearce-2108] Perry et al. at Stanford found something even more concerning: in a controlled study, developers using AI assistants wrote less secure code than a control group - and reported higher confidence in their output.[Perry-2211] The Snyk AI Code Security Report puts numbers on the organizational gap: 80% of developers believe AI generates secure code, but only 10% scan most of it. Meanwhile 59% of organizations have already encountered security issues in AI-generated code, and there is a stark perception divide where 19.4% of C-suite executives say AI code is "not risky" compared to just 4.1% of application security teams.[Snyk-2024]

The feedback loop matters. When a security scan catches a vulnerability in agent-generated code, the finding should be fed back to the agent for remediation before the merge request is opened. Brian Vermeer made this point clearly: "If you give that feedback to your agent and that agent sees that, that can help you in an iterative process to make that code better."[ANDev-046] The agent-scan-fix loop should be automatic in headless mode. No human needs to be involved in fixing a SQL injection that a SAST tool detected and can describe clearly enough for the agent to understand.

**MCP gateway filtering.** Chapter 14 covered the MCP gateway in detail. From a security perspective, the gateway is the enforcement point for tool-use policies. Which MCP servers can the agent call? Which methods on each server? With what parameters? The gateway should deny by default and allow only explicitly configured tool invocations. It should log every call for audit purposes. And it should rate-limit to prevent an agent from making thousands of calls in a tight loop, which is either a bug or an attack. Gergely Orosz's analysis of the MCP protocol in The Pragmatic Engineer describes its security posture as "woefully fragile," noting that the protocol's trust model assumes well-behaved servers and offers limited protection against malicious or compromised tool providers.[Orosz-MCP] In a factory context, the gateway is where you compensate for MCP's permissive defaults with explicit deny-by-default policies.

## Agent Identity and Authorization

When a human developer pushes code, the Git commit records their identity. When they access a service, they authenticate with their own credentials. The access control system knows who they are and what they are allowed to do.

When an agent pushes code, whose identity is it? The agent's? The developer who triggered it? The service account the factory runs under?

> **Case Study: Identity as the Number One Security Concern**[ANDev-007]
>
> Danny Allan (CTO of Snyk, AI Native Dev Ep 007) identified identity and access management as his top security concern for AI-generated code. "Typically LLMs, large language models, are trained with all kinds of data. And it's not true that everyone inside the organization should have access to all of that data. That is exacerbated tenfold when you have agents talking to agents, where you have some agent using model context protocol to speak to another agent. And there's no concept of passing on authorization."
>
> Allan gave a concrete example: "If you have an LLM that has all of your internal code libraries, you may have code libraries for one group that you don't want exposed to another group. Well, how do you ensure that your secondary agent, your coding assistant, knows that I can access this library set, but not this library set?"
>
> The problem is structural. Authentication (proving identity) is largely solved. Authorization (proving permission) in agent-to-agent communication is not. The MCP specification did not initially include authorization. The A2A (agent-to-agent) framework Google announced at Google Next did not initially include it either. Working groups are adding authorization extensions, but as of mid-2026, the tooling is immature.

The practical answer for today is to treat agent identity as a first-class concept in your factory's design.

**Every agent task should have an identity.** Not a shared service account, but a unique identity that ties back to the task, the spec that triggered it, and the human who approved the spec. Git commits should be authored by the agent identity with a trailer linking to the originating spec and approver. This is not just for security - it is for auditability. When a vulnerability is discovered six months later, you need to trace it back to which agent produced it, which spec it was following, which skills it had loaded, and who approved the spec.

**Permission models should be explicit.** At each pipeline stage, define what the agent is allowed to do. During spec interpretation, the agent has read-only access to the codebase and documentation. During implementation, it has write access to its sandbox branch and read-only access to everything else. During testing, it can execute code in the sandbox but cannot make network calls outside the whitelist. During PR creation, it can push to its branch and create a merge request but cannot merge. These permissions should be enforced by the infrastructure, not by instructions to the agent. An instruction says "please don't access production." A network policy makes it impossible.

**Escalation for sensitive operations.** Some operations are inherently risky and should require human approval even in headless mode: modifying authentication logic, changing database schemas, altering access control configurations, modifying CI/CD pipeline definitions, or touching files flagged as security-sensitive. The factory should pause and notify when it encounters these, not proceed autonomously. The list of sensitive operations should be configurable per organization and per repository.

## Trust Boundaries

A trust boundary is a line in your system where the level of trust changes. On one side, you trust the actor. On the other side, you verify. In the AI code factory, four trust boundaries matter.

**The spec boundary.** Do you trust the spec? If it came from an internal product manager through your ticketing system, you probably trust it more than if it came from an external contributor. If it was generated by another AI system, you trust it less than if a human wrote it. The spec boundary determines how much validation you apply before the spec enters the pipeline.

**The skills boundary.** Do you trust the skills the agent is using? First-party skills written by your team and checked into your repository are inside the trust boundary. Third-party skills pulled from a registry are outside it. The controls are version pinning (use a specific commit hash, not latest), security scanning (run Snyk agent scan or equivalent before adoption), and review (actually read the skill before installing it, especially skills that request file system access or network access).

**The model boundary.** Do you trust the model? This is less about the model being malicious and more about what happens to your data when it enters the model's context. If you are sending proprietary code to a third-party API, that code is leaving your trust boundary. Enterprise model deployments, self-hosted models, and models with data processing agreements mitigate this, but the trust boundary still exists. Sensitive codebases may require models that run entirely within your infrastructure.

**The output boundary.** Do you trust the agent's output? The answer should always be no, at least not without verification. The output boundary is where your validation pipeline lives: tests, security scans, linting, type checking, and human review. Every artifact the agent produces crosses this boundary, and every artifact should be validated before it crosses from the factory into your mainline codebase.

In headless mode, these boundaries must be enforced by infrastructure, not by human vigilance. The human is not there. The boundaries are configuration, network policies, permission grants, and automated gates.

## Compliance and Audit

Regulated industries have specific requirements for how software is produced, reviewed, and deployed. AI-generated code introduces new questions that existing compliance frameworks do not always answer clearly.

**Provenance chain.** For SOC 2, ISO 27001, and similar frameworks, you need to demonstrate that every change to your codebase was authorized, reviewed, and traceable. With AI-generated code, the provenance chain is: spec (who wrote it, when, what it says), approval (who approved the spec, when), agent execution (which model, which version, which skills, which context), validation results (which tests ran, which scans passed), and human review (who reviewed the PR, what they checked). Every link in this chain should be logged and auditable.

Danny Allan notes that compliance is one area where logging has actually improved: "I met with a large financial institution, a customer of ours, that said 11% of our code is AI-generated. Whether that's accurate or not, the positive outcome is that they were logging it, they were actually tracking it."[ANDev-007]

**Licensing.** LLM-generated code exists in a legal gray area. The model was trained on code with various licenses. Does its output inherit those licenses? Can it produce code that is functionally identical to a GPL-licensed implementation? These questions do not have settled legal answers. The practical mitigation is to run license scanning tools on agent output, just as you would on any third-party code, and to maintain a record of which model and version produced each piece of code.

**GDPR and personal data.** If your codebase or test fixtures contain personal data - customer names, email addresses, database snapshots with real user records - and that data enters the agent's context window, it is being processed by a third-party system (the model provider). Under GDPR, this requires a data processing agreement with the provider and potentially notification to the data subjects. The cleanest solution is to ensure that personal data never enters the agent's context: use synthetic test data, redact PII from database snapshots, and exclude data directories from the agent's file access.

**Non-determinism and attestation.** Danny Allan raised a fundamental challenge: "By their very definition, AI and code generation of AI is non-deterministic. And so having an audit trail and being able to meet compliance requirements is actually really difficult."[ANDev-007] You cannot attest that the same input will produce the same output. You can only attest that every output was validated before it shipped. This shifts the compliance burden from process attestation (we followed these steps) to output attestation (every artifact passed these checks). For some frameworks, this is a philosophical shift that auditors are still adapting to.

## Adversarial Testing

How do you know your factory's security controls actually work? You test them the way an attacker would.

**Red-teaming the pipeline.** Submit a malicious spec. Does it get caught? Include a prompt injection in a skill. Does the agent follow it? Submit a spec that asks the agent to access a file outside its sandbox. Does the sandbox prevent it? Submit a spec that generates code with a known vulnerability. Does the security scanner catch it? Does the agent fix it?

Red-teaming should be a regular practice, not a one-time exercise. Rene Brandel's company Casco performs automated penetration testing against AI-built applications: "Think about it like as if you have a pen tester on steroids that can really pen test thousands of different attacks at the same time."[ANDev-029] The same approach applies to the factory itself. Build a test suite of adversarial inputs and run them through the pipeline on a schedule.

**Continuous offensive testing.** Annual penetration tests are not sufficient for systems that change daily. Brandel makes this case forcefully: "You can be secure on the day of being pen tested, but the next day the developer might have built a new feature that you didn't know about. Once a year penetration tests are not going to be the future we're going to be living in."[ANDev-029] For the factory, this means running security tests against the factory's output continuously, not periodically. Every merge request should trigger a security scan. Every deployment should trigger a smoke test for known vulnerability patterns.

**Testing the agent's judgment.** Beyond testing for known vulnerabilities, test whether the agent makes good security decisions when the spec is ambiguous. Give it a spec that does not mention authentication. Does it add authentication anyway? Give it a spec for an API endpoint. Does it validate input? Does it use parameterized queries? These are not vulnerabilities in the traditional sense - they are shadow specs where the agent's default behavior determines the security posture. Understanding those defaults, and overriding them with explicit security context when they are wrong, is part of operating the factory securely.

## The Security Decision Matrix

Not every threat needs the same level of control. The matrix below maps threats to controls by factory mode.

| Threat | Interactive Mode | Headless Mode | Control |
|---|---|---|---|
| Prompt injection via spec | Medium risk: developer sees agent behavior | High risk: no observer | Input scanning, adversarial spec review, LLM-based validation |
| Dependency supply chain | Same in both modes | Same in both modes | Lock files, SCA scanning, allowlisted registries |
| Skills supply chain | Medium: developer reviews skill behavior | High: skills run unattended | Version pinning, security scanning, first-party skill preference |
| Secrets leakage | Medium: developer may notice | High: no one watching | Secrets manager, short-lived credentials, context-window filtering |
| Sandbox escape | Low: limited blast radius on laptop | High: shared infrastructure | Container isolation, non-root execution, resource limits |
| Data exfiltration | Medium: developer may notice network calls | High: no observer | Network whitelist, MCP gateway logging, egress filtering |
| Shadow specs | Medium: developer reviews code personally | High: review is cursory at scale | Security-focused SAST rules, explicit security context in specs |

The pattern is consistent: every threat is worse in headless mode because the human observer is absent. This does not mean headless mode is less secure - it means the security must be built into the infrastructure rather than relying on human vigilance. A well-configured headless factory with proper network isolation, credential scoping, and automated scanning is more secure than a developer running an agent on their laptop with full network access and permanent credentials. The infrastructure enforcement is more reliable than the human enforcement. But only if you build it.

## Every Developer Is Head of Security

The chapter title is "Security and Trust" but the real subject is responsibility. In the traditional development workflow, security was somebody else's problem. There was a security team, a penetration testing vendor, a compliance officer. Developers wrote code and hoped the security people would catch the mistakes.

That model does not survive the transition to AI-native development. The volume of code is too high, the pace is too fast, and the attack surface is too broad for a downstream security team to cover. Rene Brandel hacked seven of sixteen Y Combinator companies in thirty minutes.[ANDev-029] Those were small teams building fast. Large organizations producing code at factory scale face the same vulnerability at greater magnitude.

The developer who configures the factory is making security decisions whether they realize it or not. Which skills to trust. Which network destinations to allow. Which credentials to scope. Which model to use. Which specs to approve. Each of these is a security decision.

Building security into the factory is not about adding a step. It is about recognizing that the factory is a security-critical system, that its configuration is a security artifact, and that the developer who operates it is the person responsible for its security posture. Not the security team. Not the compliance officer. Not the model provider. The developer.

The good news is that the factory model makes many security controls easier to implement than they were in the human-centric workflow. Automated scanning on every merge request is easier than asking developers to run scans manually. Network isolation in a container is easier than policing developer laptops. Short-lived credentials from a secrets manager are easier than remembering to rotate tokens. The factory's infrastructure is the security control. Build it right and security becomes a property of the system, not a behavior you hope people remember.
