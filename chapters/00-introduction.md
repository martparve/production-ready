# Production Ready

## Building and Operating an AI Code Factory

**Mart Parve**

*A mid-2026 snapshot for technical leaders adopting AI-native development*

---

# Introduction

I started writing code in 1987, a ten-year-old boy in Soviet Estonia. There were no computers at home, but I had relatives and parents of friends who worked in academia, where computers were available. They were kind enough to let kids use the machines after hours.

I did not become a software engineer. I studied journalism, and in 2003 I became the technology editor of a national newspaper - briefly, before settling into a longer run of radio shows, podcasts, and columns about technology. Being a technology journalist meant being a bit outside of how technology is actually made.

In 2006, I moved from writing about technology to managing it. I joined the Look at World Foundation, a cooperation between the Estonian government, banks, and telecoms to increase adoption of the national digital identity and signature. The project grew usage from about 6,000 to 600,000 through a combination of technology communication, product development, and joint projects across government and private sector institutions.

After that came startups. I worked as a product manager and CPO at several companies, including Miros, an AI-powered visual search startup I co-founded. Along the way I picked up a BA and MSc in business economics, became an ICF-certified executive coach, and started teaching "Storytelling with Data" part-time at a high school.

I have always been the kind of business person who spends more time with engineers and users than with other business people. I like their logical, occasionally blunt, get-things-done worldview. I enjoy helping them unlock their potential by helping them clarify and articulate their vision and plans, and making certain that their work results in real value.

In early 2026, I watched a CEO I advise rebuild his SaaS product using Claude Code. He is a deeply technical person but not a software engineer. He learned disciplined specification-driven development in a couple of weeks, then built a new version of his product that already had several features the old one was missing - features that gave the product a serious competitive advantage in its market.

Two things stood out. First, the velocity: not just faster coding, but a compression of the entire path from intent to deployed product. Second, experience and domain knowledge trumped technical skills. There is almost no correlation between technical skill level and AI agent adoption success. Everyone I have seen achieve great results with agents fast is a conceptual thinker - someone who can decompose a problem, specify what they want, and evaluate the output critically. Metacognition, not syntax.

But I also saw the other side. Skilled engineers seeking out the first disappointment to get stuck at. Organizations deploying AI coding tools without any shared vocabulary, any common pipeline, any organizational strategy.

I became more and more interested in AI-native development, and increasingly convinced that there was a gap in the available material. There are product tutorials for specific tools. There are academic papers measuring code quality. But there is no systems engineering reference for the leader who needs to take an organization from ad-hoc AI coding to a systematic, scalable code factory - covering the full pipeline from business intent to deployed code, with honest trade-offs at every decision point.

So I wrote one.

### How This Book Was Written

This book was written with Claude Code, using a documentation-as-code workflow: structured specifications, iterative agent-driven generation, human review at every stage, version control, and continuous validation. In this sense it is a product of AI-native storytelling. The source material includes hundreds of podcast episodes, academic papers and industry reports, and through all that, the practical experience of engineering teams at Stripe, OpenAI, Google, Netlify, and dozens of other organizations. 

A special shout out goes to the AI Native Dev podcast for bringing together a wide spectrum of industry experience.

## Who This Book Is For

You lead engineering at a software company and you want to move beyond ad-hoc AI coding toward a systematic, scalable approach. You have shipped real software, hired real people, dealt with real production incidents at 3 AM. You are not looking for hype or theory. You want a blueprint.

Your engineers are already using AI coding tools. Some love them. Some are skeptical. Nobody is using them the same way. There is no shared vocabulary, no common pipeline, no organizational strategy.

This book gives you and your engineering leads a shared reference. Read it together, argue about the decisions, then build the factory that fits your organization. At each pipeline stage, the book describes what is needed and what the options are - with honest trade-offs rather than a single "best practice" pretending to be universal. Your constraints are your own. The book gives you the information to make informed choices within them.

**If you are a CPO or VP of Engineering** who needs to lead the adoption from first experiment to full factory, this book aims to support your "decision tree" from beginning to end.

**If you are a tech lead** who needs to understand what is being built, how your team fits in, and what changes in your daily work, this book lays out the technical "chess board" to plan your architecture, tooling and adoption.

**If you are a platform engineer** who will build and maintain the factory infrastructure, this book lays out an array of potential components, what they require, and how each connects to the rest of the system.

## What This Book Is

At its core, this is a systems engineering book. The system happens to include AI agents as workers, but the problems it tackles are familiar ones: workflow design, quality control, feedback loops, human-machine handoff points, and scaling a production system without it falling apart. The mental model is closer to manufacturing than to traditional software development. When a factory produces a defective unit, you fix the production line, not the unit. The same principle applies here: the engineer's job is building and tuning the factory, not hand-finishing every piece of output.

The book follows a unit of work through the entire pipeline - from a business request expressed in natural language, through specification, agent execution, automated validation, human review, and deployment. At each stage, it tries to lay out the architectural decisions, the tooling options, the trade-offs, and the failure modes. It then covers cross-cutting concerns that span the pipeline: security, cost, observability, governance, and organizational rollout.

The destination architecture is what this book calls the headless factory: cloud-hosted, event-driven agent execution that runs without a developer sitting in an IDE. Not every organization will reach that point, and not every organization needs to. The pipeline stages are the same whether your agents run inside an IDE or as headless cloud processes. The difference is the degree of automation at each stage.

## What This Book Is Not

This is not a tutorial on prompt engineering. It is not a product guide for any specific AI coding tool. It is not a manifesto about how AI will replace all developers by next Tuesday. And it is not a theoretical framework disconnected from practice.

The book names specific tools - Claude Code, Cursor, Codex, GitHub Copilot, and others - because discussing architecture without concrete examples gets abstract fast. But the recommendations are about capabilities and trade-offs, not brand loyalty. If a tool named here is outdated by the time you read this, the pipeline stage it served still exists, and another tool will fill the gap.

## How to Read This Book

**Part I (Chapters 1-4)** sets up the paradigm and vocabulary. What is an AI code factory? What is the context development lifecycle? What does the tooling landscape look like in mid-2026? Read this part sequentially - the rest of the book assumes you have this foundation.

**Part II (Chapters 5-14)** follows a unit of work through the pipeline, from business intent to deployed code. You can read it front to back, or jump to the pipeline stage you care about most. Each chapter is designed to stand on its own, though they reference each other. If you are trying to solve a specific problem - "how do we sandbox agent execution?" or "what should our code review process look like?" - go directly to the relevant chapter.

**Part III (Chapters 15-22)** covers cross-cutting concerns: security, cost economics, observability, evaluations, governance, a detailed case study of Stripe's Minions system, the organizational rollout roadmap, and the long-term evolution of the factory. If you need to start planning before you finish the book, Chapter 21 (The Rollout Roadmap) is designed to be useful on its own.

A note on recurring themes: several architectural principles come up across multiple chapters. The context-attention tradeoff (Chapter 3) - the tension between giving agents more context and maintaining their attention to any specific instruction - surfaces in many design decisions. The amplification thesis (Chapter 1) - the idea that AI amplifies existing engineering maturity rather than substituting for it - shapes the recommendations about prerequisites and rollout sequencing. When you encounter these themes repeatedly, it is the same principle at work in a different layer of the system.

## A Note on Shelf Life

This book is a mid-2026 snapshot, and it knows it. Some of the specific tools named here will not exist in two years. Some of the limitations described will be solved by the time you read this. Some of the recommendations will look conservative in hindsight, others aggressive.

My hope is that the overall architecture - intent, spec, implement, validate, review, deploy, monitor - will prove more durable than the specific tools. The context engineering discipline at the center of it all seems likely to grow in importance as models get more capable. But predictions are hard, especially about the future. 

