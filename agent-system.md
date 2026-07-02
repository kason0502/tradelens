# STRATA — Agent System

> Last updated: 2026-07-01
> Orchestrator: Hermes Agent (autonomous build system)

## Overview

STRATA uses a two-tier agent system:
1. **Hermes Agent** (this system) — the autonomous build orchestrator with real tool access
2. **Claude Code Agents** (`.claude/agents/`) — specialized pipeline agents for Claude Code sessions

Hermes acts as the master coordinator, delegating work through its `delegate_task` system to specialized subagents, while the Claude Code agents handle the existing 5-stage pipeline.

---

## Hermes Agent Roles

Hermes delegates work to subagents via `delegate_task`. Each "role" is implemented as a focused prompt to a subagent, not a persistent process. Hermes keeps context via memory + skills.

### 1. Research Agent
**Trigger:** New feature exploration, competitor analysis, market research
**Capabilities:**
- Web browsing and search
- Academic paper analysis (via arXiv skill)
- Competitor feature audits
- Technology evaluation
**Artifacts:** Research documents in `.hermes/research/`
**Example delegation:**
```
delegate_task(goal="Research how TradingView implements their multi-chart sync...")
```

### 2. UI/UX Agent
**Trigger:** Visual improvements, component design, responsive layout work
**Capabilities:**
- Browser testing (navigate, screenshot, interaction testing)
- CSS/HTML analysis and generation
- Accessibility auditing
- Cross-device layout validation
**Artifacts:** Design specs, CSS patches, screenshots
**Quality gate:** Must pass visual regression check before merge

### 3. Trading Edge Discovery Agent
**Trigger:** Periodic research cycles, new data availability
**Capabilities:**
- Analyze market data patterns
- Literature review on trading strategies
- Statistical validation of potential edges
- Document findings with honest assessment
**Artifacts:** Edge reports with in-sample/OOS splits, reject rate
**Quality gate:** Must pass the edge-finder → critic pipeline (no false positives)
**Rule:** "No edge found" is a normal, valid outcome. Never fabricate edges.

### 4. Strategy Design Agent
**Trigger:** Validated edge from Discovery, strategy improvement request
**Capabilities:**
- Translate edges into implementable rules
- Define entry/exit/position-sizing logic
- Specify backtest parameters
- Design risk management rules
**Artifacts:** Strategy specification documents
**Quality gate:** Architect approval required before implementation

### 5. Backtesting Agent
**Trigger:** New strategy design, parameter changes, new data
**Capabilities:**
- Run Python backtester scripts
- Generate statistical reports
- Validate results against benchmarks
- Produce equity curves and trade logs
**Artifacts:** results.json, statistical reports, equity curves
**Quality gate:** Minimum 100 trades, PF > 1.3, positive after costs

### 6. Security/Architecture Agent
**Trigger:** Code review, new feature architecture, deployment changes
**Capabilities:**
- Static code analysis
- Dependency audit
- API security review
- Architecture design review
**Artifacts:** Security reports, architecture diagrams
**Quality gate:** No P0/P1 issues before deployment

### 7. Implementation Agent
**Trigger:** Approved designs from Architect, bug fixes from QA
**Capabilities:**
- Code generation and modification
- File system access
- Terminal commands (build, test, git)
- Browser verification
**Artifacts:** Code changes, commits
**Quality gate:** Must pass QA before merge

### 8. QA Testing Agent
**Trigger:** After implementation, before deployment
**Capabilities:**
- Browser-based testing (navigate, click, verify)
- Console error detection
- Visual regression checking
- Cross-browser validation
**Artifacts:** Test reports with pass/fail and repro steps
**Quality gate:** PASS required for deployment

---

## Coordination Patterns

### Pipeline (Sequential)
For feature development:
```
Research → Strategy Design → Architecture Review → Implementation → QA → Deploy
```

### Parallel (Independent)
For maintenance:
```
[Security Audit] [UI Polish] [Edge Research] — all run independently
```

### Reactive (Event-Driven)
For bugs:
```
QA FAIL → Implementation fix → QA retest
```

---

## Hermes Delegation Constraints

- **Max 3 concurrent subagents** (configured via `delegation.max_concurrent_children`)
- **Max depth 1** (subagents cannot delegate further)
- **Subagents are leaf workers** — no access to `delegate_task`, `clarify`, `memory`, or `send_message`
- **Context must be self-contained** — subagents have NO memory of the conversation
- **Results are self-reports** — verify claims (file written? test passed?) before trusting

### Best Practices
1. Pass ALL relevant context (file paths, error messages, constraints) in the delegation
2. Require subagents to return verifiable handles (paths, URLs, HTTP status)
3. Verify results yourself after subagent returns
4. Batch independent work into parallel delegations (max 3)
5. Save successful workflows as Hermes skills for reuse

---

## Existing Claude Code Agents (`.claude/agents/`)

These run inside Claude Code sessions, not Hermes:

| Agent | Role | Writes Code? |
|-------|------|-------------|
| `edge-finder` | Strategy research on real data | No |
| `critic` | Adversarial review (bugs, UX, security) | No (read-only) |
| `architect` | Design review before implementation | No (read-only) |
| `builder` | Implements approved scope | Yes |
| `qa-test` | Regression sweep after builder | No |

**Pipeline:** edge-finder → critic → architect → builder → qa-test
**Orchestrator:** The Claude Code main session runs the pipeline, passing reports between stages.

---

## Integration Between Systems

Hermes and Claude Code agents serve different purposes:
- **Hermes:** Strategic coordination, research, cross-session memory, automation, deployment
- **Claude Code:** Tactical code changes within a focused coding session

When Hermes identifies work that needs Claude Code agents:
1. Hermes writes a task spec to a file
2. User runs the Claude Code pipeline on it
3. Hermes verifies the results via file system / browser testing

---

## Continuous Improvement

After every successful workflow:
1. Hermes saves the approach as a **skill** (`skill_manage`)
2. Skills are loaded automatically in future similar tasks
3. Failed approaches are documented in skill pitfalls
4. Research findings are persisted in memory for cross-session access

### Skill Categories for STRATA
- `strata-dev` — main development workflow
- `strata-research` — trading research methodology
- `strata-qa` — QA and testing procedures
- `strata-deploy` — deployment and release workflow
