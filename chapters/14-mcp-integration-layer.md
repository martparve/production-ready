# Chapter 14: MCP and the Integration Layer

An agent that can write code but cannot read a Jira ticket, query a database, or check a Sentry error trace is an agent working blind. The code factory described in earlier chapters has a pipeline: intent capture, spec formalization, codebase onboarding, orchestration, validation, review. Every stage requires interaction with external systems. Without a standardized way to connect those systems, each integration is a bespoke adapter: a script that scrapes the GitHub API, a webhook handler that parses Linear payloads, a custom function that queries the production database. MCP eliminates the adapter tax.

The Model Context Protocol[MCP-spec] is a standard published by Anthropic in late November 2024 that lets agents interact with external systems through structured tool definitions. Created by David Soria Parra and Justin Spahr-Summers at Anthropic, MCP uses a JSON-RPC client-server architecture with a deliberately minimal primitive model.[Anthropic-MCP] The server side exposes three primitives: Prompts (templated interaction patterns), Resources (structured data the agent can read), and Tools (functions the agent can invoke with typed arguments). The client side provides two primitives: Roots (filesystem or project scopes that anchor the agent's context) and Sampling (the ability for a server to request LLM completions back through the client). This asymmetry is intentional. Servers expose capabilities; clients provide the intelligence and the security boundary. The design echoes Microsoft's Language Server Protocol (LSP), which standardized how editors interact with language-specific tooling - a parallel that multiple observers have noted and that explains why adoption was so rapid among developers who remembered the pre-LSP era of per-editor, per-language plugins.[Orosz-MCP]

MCP succeeded because it was simple enough that people actually built servers for it. Michael Hunger[ANDev-010] of Neo4j built his first MCP server within two weeks of the protocol's publication. Within months, registries listed thousands of servers. By early 2026, every major agent - Claude Code, Cursor, Codex, Gemini CLI - supported MCP as the default integration layer.

The ecosystem momentum confirmed MCP as a de facto standard rather than a single-vendor experiment. OpenAI adopted MCP support in March 2025. Google DeepMind followed in April 2025. Server downloads grew from roughly 100,000 to over 8 million in the first five months after launch, and by the protocol's first anniversary the SDKs were averaging 97 million monthly downloads.[Anthropic-MCP] In May 2025, Anthropic donated MCP to the newly established Agentic AI Foundation under the Linux Foundation, with Block, OpenAI, Google DeepMind, and Microsoft as co-founders.[AAIF] The governance move matters for factory builders: MCP is no longer a protocol you adopt at the discretion of one company. It is an open standard with multi-vendor governance, which reduces the risk of building your integration layer on it.

## MCP at Every Stage of the Pipeline

The factory pipeline from Chapter 2 has seven stages. MCP servers participate in all of them. Understanding where they fit clarifies why MCP is not a convenience feature but a structural requirement for headless operation.

**Intent capture.** The factory needs to read work items from wherever the team tracks them. MCP servers for Jira, Linear, GitHub Issues, and Shortcut pull tickets into the pipeline. In headless mode, a scheduler polls these servers for new items matching a filter (a specific label, a particular project board, a status transition) and feeds them into the spec formalization stage. Without MCP, this requires a custom webhook integration per tool. With MCP, the agent calls `get_issues` with a filter and gets structured data back.

**Spec formalization.** Turning a work item into a machine-actionable spec requires context: API documentation, architectural decision records, style guides, existing specs as examples. MCP servers for documentation systems make this context available on demand. David Cramer at Sentry describes a pattern his team built: an MCP server that exposes Sentry's public documentation through search and retrieval tools. "We took our public docs, generated lockdown files - cleaned up markdown for every page - and expose it through our MCP as tools: a search docs tool and a get docs tool."[ANDev-015] The same approach works for internal documentation: architecture docs, API contracts, coding standards. The agent pulls exactly the documentation it needs at the moment it needs it, rather than having everything pre-loaded into the context window.

**Codebase onboarding.** Before an agent writes a line of code, it needs to understand the repository: the project structure, dependency graph, naming conventions, existing patterns. MCP servers for code search and codebase intelligence provide this. Graph-based approaches are particularly effective here. Michael Hunger describes using Neo4j's MCP server to expose not just data but schema metadata: "As a dev, I can use the schema to generate GraphQL type definitions or Java classes or Python entity classes."[ANDev-010] The schema gives the agent structural understanding that goes beyond what file search alone provides.

**Orchestration.** The orchestrator dispatches agents to write code, but those agents need to interact with the development environment: run builds, execute tests, invoke linters, spin up databases for integration testing. MCP servers wrap these infrastructure APIs. Hunger describes the pattern: "I said, we need to build this application, but I want you to test run all the queries against the real test database. So while it was generating the code, at the same time it took the queries and validated them against the test database."[ANDev-010] The MCP server for the cloud database gave the agent the ability to self-validate during code generation - a feedback loop that is impossible without tool access.

**Validation.** Security scanning, compliance checking, license auditing, performance benchmarking. Each of these is a tool that the validation stage needs to invoke. MCP servers make them available as structured tool calls rather than requiring the orchestrator to shell out to CLI tools and parse stdout.

**Monitoring and feedback.** The most powerful integration closes the loop between production and development. Sentry's MCP server[Sentry-MCP] is the canonical example: an agent working on a bug fix can query production error traces, read stack traces, check error frequencies, and pull root cause analysis directly through MCP tool calls. Cramer describes the workflow: "You can just drop in a link to a Sentry issue. It'll pull in the right context. If you use SEER, it'll pull in SEER's context as well."[ANDev-015] The agent gets production observability data without a developer serving as intermediary.

## The Federation Layer

When you connect a dozen MCP servers to a single agent, it becomes a federation layer across systems that were never designed to work together.

Michael Hunger articulates this clearly: "In your assistant, basically all the things come together as tools. And then the assistant actually creates this almost like a federation layer across them. It takes the context of your code and your project into account plus the instructions and the conversations. So it can cross systems without you having to copy over stuff."[ANDev-010]

Consider what this means in practice. An agent can take a failing test from the CI/CD system, correlate it with a production error from Sentry, find the relevant ticket in Linear, pull the associated documentation, and propose a fix - all in a single agentic loop. Before MCP, each of those steps required a developer to open a different tool, copy information between systems, and synthesize the result mentally. The agent does the same thing, but through tool calls, and it does it at 3 AM on a Saturday when nobody is watching.

This federation capability is the real power of MCP in the factory. Individual tool calls are useful; the ability to chain them across systems in service of a higher-level goal is transformative. It is also what makes MCP security so important.

> **Case Study: Sentry's MCP Server and Embedded Agents**[ANDev-015]
>
> David Cramer (Sentry, Ep 015) describes building Sentry's MCP server as a side project that became a core product capability. The server does more than map API calls: it embeds agents inside the tools themselves. "Our MCP now actually has two agents embedded inside of it," Cramer explains. "A bunch of the tool calls are just roughly translate this input to one or more API calls and then translate that output into one response. But now there's a couple of search endpoints that actually map to a natural language input that then gets thrown inside of another agent that then gets mapped to API calls."
>
> The practical result: a developer in Claude Code can ask "what was the total token consumption of X service yesterday?" and get an answer through Sentry's MCP. The query flows from the coding agent to the MCP server, into an embedded agent that translates the natural language question into the correct Sentry API calls with the right aggregation functions, executes them, and returns the result. This is an agent calling a tool that contains an agent calling other tools - nested non-determinism. Cramer is candid about the cost: "Good luck ever getting it on the guardrails. It gets so lost in words. No matter how you try to steer it, it always ends up getting lost again because it's a very lossy compression."

## Agents Inside Tools: Nested Non-Determinism

Cramer's embedded agents pattern represents a design choice every factory builder will face: should an MCP tool be a thin wrapper around a deterministic API call, or should it contain intelligence of its own?

The thin wrapper approach is predictable. The MCP tool receives structured input, makes one or more API calls, and returns structured output. The logic is deterministic. The calling agent provides the intelligence; the tool provides the execution. This works for 80% of integrations.

The embedded agent approach handles the remaining 20%: cases where the input is ambiguous and needs interpretation, where the right API call depends on the data shape, or where the tool needs to make decisions that require understanding context. Sentry's search endpoints are a good example. A user asking about "token consumption" needs the tool to understand what that maps to in Sentry's data model, which aggregation function to use, and how to structure the query. Encoding all possible query patterns as deterministic mappings would require maintaining an enormous lookup table. An embedded agent handles novel queries gracefully.

The cost is compounding non-determinism. When an agent calls a tool that contains an agent, the outer agent cannot predict what the inner agent will do. Failures in the inner agent are opaque to the outer agent. Debugging requires inspecting two separate conversation logs. Token consumption roughly doubles. And as Cramer describes, getting the inner agent to behave consistently is difficult: "It's not simple versus complex. The implementation is unbelievably simple and I can give it a full spec of exactly the architecture. It's just a chain of function calls and it would still go way off the rails."[ANDev-015]

The pragmatic approach: start with thin wrappers. Introduce embedded agents only when deterministic mapping genuinely cannot handle the use case. And when you do embed agents in tools, instrument them aggressively - log every inner agent decision, set strict token budgets, and implement timeout-based circuit breakers.

## Agent-to-Agent Communication: ACP

MCP connects agents to tools, but what connects agents to other agents?

The Agent Communication Protocol[ACP], created by Zed and announced in early 2026, addresses this gap. Cameron McLaughlin of Zed describes the motivation through an analogy: "We all remember the world before LSP and how every editor had to make their own extension for every language. LSP was pretty revolutionary in allowing lots of editors to speak the same language. It's obvious to us that we need a similar protocol for agents."[Zed-ACP]

ACP standardizes how agents communicate regardless of which harness they run in. A Zed agent can delegate a task to Claude Code, receive the result, and pass it to Codex - all through the same protocol. The factory implications are significant: rather than being locked into a single agent provider, the orchestrator can route tasks to whichever agent is best suited. Code generation goes to Claude Code. Test generation goes to Codex. Documentation goes to Gemini. Each agent operates in its own environment but communicates through ACP.

McLaughlin notes that even competitors see the value: "JetBrains is also working with us on ACP. It's a big collaborative push. You would think JetBrains and Zed are big competitors, but it's in everyone's interest to have this standard."[Zed-ACP] The LSP parallels are exact. Before LSP, every editor maintained language-specific extensions. After LSP, language servers became portable across editors. ACP aims to do the same for agents: make agentic capabilities portable across harnesses.

For the factory, ACP complements MCP rather than replacing it. MCP is agent-to-system (the agent reads a database, calls an API). ACP is agent-to-agent (one agent delegates to another, receives results, coordinates work). Together, they form the nervous system of the integration layer.

## MCP Gateway Patterns for Enterprise

Connecting agents to everything sounds powerful until you are the security team responsible for what they can access. Enterprise deployment of MCP requires a control layer between agents and the MCP servers they call.

Michael Hunger proposes the concept of proxy MCP servers: "One MCP server that proxies another one and actually does filtering of the content that goes through. You basically add a layer of security on the ingoing and outgoing data where you can validate certain things."[ANDev-010]

This is the MCP gateway pattern. An enterprise deploys a gateway service that sits between agents and the production MCP servers. The gateway enforces:

- **Access control.** Which agents can call which tools. A junior developer's agent might have read-only access to the production database MCP server; a senior engineer's agent gets write access. The CI/CD agent gets deployment tools; ad hoc coding agents do not.
- **Request filtering.** Blocking certain queries before they reach the MCP server. A gateway can prevent agents from requesting customer PII, strip sensitive parameters from queries, or reject API calls that would modify production state.
- **Response filtering.** Scrubbing sensitive data from MCP responses before they reach the agent's context window. The agent gets the information it needs to do its job without the raw credentials, API keys, or customer data.
- **Logging and auditing.** Every tool call passes through the gateway and gets logged. When something goes wrong, you have a complete audit trail of which agent called which tool with what arguments and what response came back.
- **Rate limiting.** Preventing a runaway agent from hammering an MCP server with thousands of requests. Token budgets at the agent level are one control; request rate limits at the gateway level are another.

Hunger predicts this will become standard practice: "We will see more and more that companies will establish these MCP kind of gateways. Where they have these are the allowed MCP servers in our organization. We add these kind of security authorization controls and also filter and validation."[ANDev-010]

The gateway pattern mirrors what enterprises already do with API gateways for their microservices. The same principles apply: centralized policy enforcement, traffic visibility, and the ability to change security rules without modifying individual MCP servers.

## WebMCP: Agents Meet the Browser

MCP connects agents to backend systems. WebMCP extends the same concept to the browser.

Today, when an agent needs to interact with a web application, it takes screenshots and clicks on coordinates - literally simulating a human user. This is slow, expensive in tokens, and fragile. Maximiliano Firtman describes the problem: "The agent takes screenshots and then analyzes them with an image model. But what happens if in those five to ten seconds, the JavaScript moves that button? So it doesn't work. Then another screenshot is taken. It's inefficient, both in time and in cost."[ANDev-048]

WebMCP[WebMCP], an experimental API from the Chrome team, offers a different approach. Web developers register JavaScript functions as tools that agents can call directly. The API is remarkably simple: `navigator.model.context.registerTool` takes a name, a description in natural language, and a JavaScript function. The agent reads the tool descriptions, decides which to invoke, and calls the function directly instead of navigating the UI visually.

The airline website example makes the value concrete. Instead of an agent opening a date picker, scrolling through months, clicking on dates, and hoping the calendar widget behaves predictably, the developer exposes a `searchFlights` tool with typed parameters (origin, destination, dates, trip type) and the agent calls it programmatically. The interaction drops from 30 seconds of screenshot-click-screenshot-click cycles to a single function call.

For the factory, WebMCP has two implications. First, it offers an additional integration surface for internal tools that have web UIs but no APIs - many enterprise tools fall into this category. Second, it creates a new class of MCP-like integration that runs client-side rather than server-side. Payment flows through Apple Pay or Google Pay, shopping cart management, and anything involving client-side state can be exposed through WebMCP without building a server-side API.

The limitation is that WebMCP currently works only in visible browsers, not headless. For a headless factory, that means WebMCP is not yet a direct tool. But the direction matters: as agent-web interaction matures, the factory will increasingly need to interact with web-based services that lack traditional APIs, and WebMCP provides the standardized path.

## MCP Security: One in Seven Can Hack Your Machine

Every MCP server you connect to your factory is an attack surface.

Gergely Orosz's analysis in *The Pragmatic Engineer* described MCP's security model as "woefully fragile."[Orosz-MCP] His concern is specific: MCP servers typically run with the same permissions as the user's development environment, which often means SSH key access, cloud credentials, and write access to production repositories. An attacker who compromises an MCP server - or publishes a malicious one - inherits those permissions. Orosz notes that the LSP parallel cuts both ways. LSP made language tooling universal, but it also created a class of extensions that run with elevated privileges inside every developer's editor. MCP replicates that pattern at a higher stakes level because the agent calling the tools has autonomous decision-making capability that a language server never had.

A joint scan by Snyk and Tessl of 3,984 published skills (the broader category that includes MCP server configurations) found that 13.4% - 534 skills - contained at least one critical security issue.[ANDev-046] That is roughly one in seven.

> **Case Study: Scanning 3,984 Skills for Security Vulnerabilities**[ANDev-046]
>
> Brian Vermeer of Snyk (Ep 046) describes the threat taxonomy they discovered: prompt injection via hidden instructions (obfuscated through base64 encoding, Unicode smuggling, or non-Latin languages), data exfiltration through side channels, credential theft, unverifiable dependencies, and arbitrary code execution. The attack patterns are not novel in isolation, but the delivery mechanism is new. "Think of it like most of these skills run on your local machine," Vermeer explains. "They have execution power. They probably run on your machine as root. And if you give Claude the power to execute bash scripts and I can infect a skill in a way that it will create a bash script for me to do something - I'm basically vibe coding my exploits now."
>
> The trust model makes it worse. A malicious MCP server or skill earns trust by working correctly initially, then updates with a side effect: "We put something extra. We put a side effect in. Or we return, instead of just your calendar items, we return an instruction. But you already trust it." This is software supply chain attacks applied to the agent tool layer.

The GitHub MCP server vulnerability that Hunger and Simon Maple[ANDev-010] discuss (Ep 010) illustrates the pattern concretely. A user connects the official GitHub MCP server to their agent, giving it access to both public and private repositories. A malicious actor creates an issue in a public repository containing prompt injection instructions. The agent, attempting to resolve issues, follows those instructions and leaks private repository content into a public pull request. The MCP server itself is not compromised - it correctly executes the authorized API calls. The attack exploits the fundamental LLM problem: the model cannot distinguish between data to process and instructions to follow.

Hunger identifies the core issue: "The data and control plane are merged. That's one of the big challenges that we need to solve in AI systems anyway. Currently data and instructions are not separate."[ANDev-010] Until models can reliably tag and differentiate between instruction tokens and data tokens, every MCP server that returns user-controlled content is a potential injection vector.

For the factory, MCP security is not optional hardening - it is a prerequisite for headless operation. A factory running unattended at 3 AM cannot rely on a human to catch a suspicious tool call. The mitigations are layered:

1. **Version pinning.** Never run `npx something@latest` for an MCP server. Pin to a specific version and audit before upgrading. As Vermeer warns: "It was safe yesterday. Today it's not. And you're pulling that in. And you're none the wiser."[ANDev-046]

2. **Gateway filtering.** The enterprise gateway pattern described earlier is your primary defense. Filter requests, sanitize responses, log everything.

3. **Least privilege.** Hunger's personal practice: "I only give it access to my open source repos. I don't ever give it access to my private repos."[ANDev-010] Apply the same principle to factory integrations. The agent writing code does not need access to the production database. The agent reading Sentry errors does not need write access to the deployment pipeline.

4. **Automated scanning.** Tools like Snyk's agent-scan can audit installed MCP servers and skills for known vulnerability patterns. Run these scans in CI, not just once at install time.

5. **Sandboxing.** Run MCP servers in isolated environments. A compromised MCP server in a container with no network access beyond its target API limits the blast radius.

6. **Deterministic guards over agent judgment.** Do not rely on the agent to decide what is safe. Put authorization decisions in deterministic code: the gateway, the sandbox boundaries, the access control rules. As Simon Maple puts it: "You're putting the security, the authorization in the hands of a deterministic model. Something that has strong authorization and authentication built in."[ANDev-010]

## Building Your MCP Layer: A Decision Matrix

Not every external system needs an MCP server. The decision matrix for your factory:

| Criterion | Build/Adopt MCP Server | Use Direct API / CLI |
|---|---|---|
| Agent needs to decide when to use it | Yes | No |
| Multiple agents need access | Yes | Maybe |
| Interaction requires natural language interpretation | Yes | No |
| Single, predictable API call pattern | No | Yes |
| Used only in deterministic pipeline steps | No | Yes |
| Contains sensitive data | Yes (with gateway) | Yes (with guards) |

MCP servers shine when the agent needs autonomy in deciding which tool to use and how to invoke it. If the integration is always the same call with the same parameters, triggered at the same pipeline stage, a direct API call in your orchestration script is simpler and more predictable.

For a factory getting started, the essential MCP servers are:

- **Work tracker** (Jira, Linear, GitHub Issues): pulling intent into the pipeline
- **Documentation** (internal docs, library docs via Context7 or similar): providing specs and API references
- **Code search**: navigating the codebase
- **Build and test runner**: executing feedback loops during code generation
- **Monitoring** (Sentry or equivalent): closing the production-to-development loop

Everything else can be added incrementally as you identify bottlenecks where a developer is manually copying information between systems.

## The Integration Tax

MCP does not eliminate integration work - it standardizes it. You still need to choose which servers to run, configure authentication, manage versions, enforce security policies, and handle the inevitable cases where an MCP server returns unexpected data or goes down entirely. What MCP eliminates is the *per-agent* integration tax. Without MCP, every agent needs its own adapter for every system. With MCP, you build the integration once and every agent in your factory can use it. The N-by-M problem of agents times systems reduces to an N-plus-M problem of agents plus servers.

Hunger draws the parallel to GraphQL's adoption in 2016: "It kind of feels a lot like in the spirit of when GraphQL came out. There's the spec, the working groups, everyone is jumping on it. There's lots of energy and enthusiasm. It's a grassroots movement."[ANDev-010] The comparison is apt. GraphQL succeeded because it solved a real problem (over-fetching and under-fetching in REST APIs) with a simple enough protocol that adoption was practical. MCP succeeds for the same reason: it solves a real problem (connecting agents to systems) with a protocol simple enough that a single developer can build a server in a weekend.

The protocol will mature, the security story will improve, server registries will consolidate, gateway products will emerge. The fundamental architecture - agents talking to external systems through structured tool definitions - is the settled answer to the integration question. Build your factory's integration layer on it.

---
