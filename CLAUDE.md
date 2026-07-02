# CLAUDE.md — working agreement for this repo

STRATA (formerly TradeLens Pro) is a **single-file** app: everything is in `index.html` (no build step, no framework; Chart.js + TradingView via CDN). Start by reading the living docs below — they are the source of truth, not chat history.

## Living docs — READ at the start, UPDATE before you finish
At the **start** of a session, read:
- `DIRECTIVE.md` — the owner's Master Engineering Directive: mission, product standard ("would a serious futures trader happily pay for this?"), specialist lenses (Atlas/Orion/Athena/Nova/Sentinel/Forge/Pulse → mapped onto the agent pipeline), autonomy rules, current stack reality.
- `PROJECT_CONTEXT.md` — what/why/status, how to run, constraints.
- `ARCHITECTURE.md` — code structure, key functions, data flow.
- `DESIGN_SYSTEM.md` — tokens, colors, components, conventions.
- `TODO.md` — prioritized outstanding work.

Before you **finish any session that changed code**, update the relevant docs in the same commit:
- `CHANGELOG.md` — add a dated entry (newest first) for what shipped.
- `TODO.md` — check off done items, add new ones discovered.
- `ARCHITECTURE.md` / `DESIGN_SYSTEM.md` / `PROJECT_CONTEXT.md` — only if structure, tokens, or status/scope changed.
- Bump the "Last updated" date in any doc you touch.

Keep docs concise and high-signal; they exist so work can continue after context is lost.

## House rules (see DESIGN_SYSTEM.md / PROJECT_CONTEXT.md for detail)
- **Real market data only** — never fake/simulate prices.
- **Green/red = up/down (P&L) only.** Brand/UI accent is electric blue; gradients are blue→cyan→purple.
- Prefer line-icon SVGs over emoji in UI chrome; plain-language labels with tooltips for jargon.
- Commit when work is done; LF→CRLF warnings are harmless.

## The agent team & pipeline (`.claude/agents/`)
Five agents, one pipeline. Agents cannot call each other — the MAIN SESSION orchestrates: run a stage, pass its report into the next stage's prompt, enforce the loops.

```
edge-finder → critic → architect → builder → qa-test
```
- **edge-finder** 🧠 — strategy research on real data (gated: OOS/robustness/costs). Research only; NEVER edits the product. "No edge found" is a normal verdict.
- **critic** 🔍 — adversarial review (bugs, UI/UX, security, logic, performance) + challenges edge-finder's research. Read-only; findings carry file:line + the fix.
- **architect** 👷 — reviews designs BEFORE implementation: fit, duplication, scale, simpler way, future cost. APPROVE / APPROVE-WITH-CHANGES / REJECT; its required changes bind the builder. Read-only.
- **builder** 🔨 — implements ONLY approved/assigned scope on both surfaces, verifies in-preview (incl. a fresh-browser `localStorage.clear()` pass). Never invents features. Does not commit.
- **qa-test** ✅ — regression sweep after the builder (landing, tabs, paywall test-mode flows, backtester, desktop app). PASS/FAIL with repro steps.

**Loops:** QA FAIL → back to builder with the regression list. Architect REJECT → back to the proposer (redesign before any code). Not every task needs all five: a pure bugfix = critic(or user report) → builder → qa-test; research without shipping = edge-finder → critic. The main session commits, pushes, and updates the living docs after QA passes.

## Preview / verify
- No Node/Python on this machine. Use preview config `tradelens` (`.claude/serve.ps1`, port 8777) → `http://localhost:8777`.
- **`serve.ps1` is also the live-data proxy** (`/api/yf?url=…`, server-side PowerShell fetch of Yahoo/Stooq) — this is what makes stock data load reliably without flaky public CORS proxies. If you change `serve.ps1`, **restart the preview** for it to take effect.
- The **screenshot tool can't capture this page** (live TradingView iframe + offscreen tab freezes animations → timeout). Verify with `preview_eval` / computed styles / console logs, and ask the user to view in a real browser.
