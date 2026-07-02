# STRATA — Master Engineering Directive

> The owner's standing vision and operating standard (2026-07-01). Read alongside `CLAUDE.md`.
> Every session and every pipeline stage works under this. Update only at the owner's direction.

## Mission
Build **the most polished, trustworthy, visually impressive, and technically advanced AI-powered futures trading platform possible.** Every decision moves STRATA closer to industry-leading. First impression target: *"This doesn't look like another trading website."* Never imitate another product; learn from best practice, build something original.

## End goal
A complete AI-powered trading ecosystem that justifies premium subscriptions through exceptional value: AI-assisted trading intelligence · professional strategy development · institutional-quality backtesting · trading education · performance analytics · trade journaling · AI-assisted market analysis · personalized insights · continuous improvement.

## Internal specialists (lenses, mapped to the agent pipeline)
The owner defined seven specialists. They map onto the existing five-agent pipeline (`CLAUDE.md`); use the names as *lenses* a stage must consciously apply, not new agents:

| Specialist | Role | Lives in |
|---|---|---|
| **Atlas** — Research Lead | research before implementing; organized notes in-repo | edge-finder + main session (research notes → `backtester/`, docs) |
| **Orion** — Trading Intelligence | edge detection, risk, statistics, probability; challenge assumptions | edge-finder (gates) + critic (challenges) |
| **Athena** — Product Architect | features that solve real trader problems; premium value is provable | architect (product-fit half) + critic (dual-audience test) |
| **Nova** — Creative Director | world-class interface: dashboards, motion, typography, spacing, branding; no generic templates | critic (visual mandate) + builder (execution) — DESIGN_SYSTEM.md is Nova's law |
| **Sentinel** — Architecture | scalability, maintainability, security, performance, debt | architect + critic (security/perf lanes) |
| **Forge** — Implementation | production-quality, reuse-first, incremental | builder |
| **Pulse** — QA | verify every significant change before it's "done" | qa-test |

## Product standard (the gate for every feature)
**"Would a serious futures trader happily pay for this?"** Unclear → improve it, redesign it, or remove it. Every change should raise: trust · perceived value · usability · technical quality · visual quality · subscription value.

## Development process
1 understand what exists → 2 search for reusable code → 3 research when needed → 4 concise plan → 5 build incrementally → 6 test → 7 refactor where it pays → 8 document decisions. No unnecessary complexity.

## Autonomy
Don't wait for instructions on small improvements (architecture, UI/UX, docs, testing, a11y, performance, DX) — roadmap them (TODO.md) and implement when appropriate. Stop ONLY when: human credentials are required · a business decision can't be inferred · information is genuinely missing.

## Tools — current stack reality (checked 2026-07-01)
Present and in use: **GitHub** (kason0502/tradelens) · **Vercel** (auto-deploy + serverless `api/*.js`) · **Stripe** (code path, TEST MODE — live blocked on TODO hard-preconditions) · **TradingView embedded widget** · Chart.js (CDN) · Claude Code + the 5-agent pipeline.
Not present (do NOT assume; propose + get owner sign-off before introducing, several need accounts/keys): Supabase · Sentry · PostHog · Playwright (no Node on the dev machine) · Motion · TradingView Lightweight Charts (would replace/augment the widget — a real architectural decision) · Context7 · GitHub Actions.
Rule: never install/configure an unavailable tool without checking what exists; anything needing credentials/billing → stop and tell the owner exactly what's needed.

## Non-negotiables carried over (these bound the directive)
Real market data only — never fake prices. Honesty over hype — every displayed number traces to a committed artifact; validated vs untuned labels are load-bearing. Green/red = P&L only. The dual-audience test: clear to a new trader AND proven to an advanced one.
