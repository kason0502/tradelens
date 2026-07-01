# TradeLens Pro — Design System

> Living doc. Update when tokens, components, or visual conventions change.
> Last updated: 2026-07-01 (pipeline run 2: number craft + strata motif + chart frame)

**Number craft (2026-07-01, both surfaces):** all numeric displays use `font-variant-numeric:tabular-nums` (site rule ~1130, app rule ~68 — add new numeric classes to those lists); negatives render the true minus **U+2212** (via `_bt$`/`_numU` on the site, `_statTxt` in the app — display-only, never parsed); trailing units (`$ % x d R`) render in `.nu` spans (0.7em, `--ink3`) so the digits carry the weight. **Unified stat-tile spec:** value 22px tabular / label 10px uppercase letter-spacing .08em / sub 10.5px `--ink3` — applies to `.bt-stat`, `.bt-score`, `.sp-grid` cells, app `.stat` (don't invent a fifth tile family).
**STRATA brand motif:** (1) `.ct-glyph` — the logo's 3-ascending-blocks as a `::before` mask-SVG on **flagship card titles only** (edge card, Backtester explainer, app rail backtest card — keep it scarce or it becomes wallpaper); (2) **strata bands** — alternating ~1.5–2% white horizontal bands, implemented ONLY inside `strataChart` (and the app's compact equitySVG); (3) **layered landing dividers** — 3 stacked hairlines at 6/4/2% opacity with width offsets between landing sections. **`strataChart`** is the site's single chart frame: time-scaled x-axis + year ticks, 3–4 y-ticks, end-value chip, max-DD region `rgba(244,63,94,.06)`, dashed baseline; label-less data falls back to index spacing + a "spaced by trade, not time" caption. **Phone dock:** ≤520px the `.appnav` docks to the bottom as a horizontally-scrollable icon bar; content takes the full width.

**Flat card language is now app-wide (2026-07-01):** `.card` was rethemed from glass (blur + hover-lift + glow) to the flat panel language — `background:var(--s1)`, 1px `--line` border, hover = border-color shift only, **no backdrop-filter**. This unifies the app with `.dash-panel` and the landing's `lx-` surfaces (one chrome language) and removes 7+ simultaneous blurs from the Futures tab. `--glass` remains ONLY on `.appnav`, `.acct-chip`, `.dte-row`, `.metric` (next candidates if the flattening continues). New components:
- **`.skel-card` + `skelCard(h)`** — shared skeleton loading block (fixed height, `skelShine` shimmer via `::after`; animation off under reduced-motion). Use instead of one-line "Loading…" cards to avoid layout shift. Adopted by the Futures tab; other `loading-label` call sites should adopt when touched.
- **`.pay-lock` anatomy** — solid border + accent top hairline (`::before`), line-SVG lock badge (no emoji), optional **`.pl-prev`** blurred-real-content teaser behind the lock (`filter:blur(6px)`, `aria-hidden`, `pointer-events:none`, fade mask; must reuse the REAL renderer, e.g. `po3CardHTML` — never fork markup for a preview).
- **`.ac-dot`/`.ac-badge`** now use accent tokens (`--ac`/`--act`/`--ac-rgb`) — they mood-flip and the green=P&L rule holds. NOTE (todo'd): `.pay-badge`/`.pt-cur`/`.pt-feats li::before` still use P&L green — same one-line fix when next touched.
- **Trader-app boot fast-path:** full 4.8s cinematic only on first run (`tlpro_boot_seen_v1`); repeats reveal in ~0.3s on first data load with a 2.5s dead-feed fallback.

**Backdrop wave ribbons (session 35):** the `#fxCanvas` living-market layer now renders **flowing market wave ribbons** (3 layered translucent price curves, scrolling + parallax, mood-tinted) instead of the old perspective floor-grid (`waves[]` config in the end-of-script IIFE; `waveT` drives the scroll). Backdrop intensity was raised overall (brighter aurora blobs + constellation, canvas opacity .96) so it reads more clearly behind the data without competing with it. Keep it ambient — the rule is still "noticeable, not distracting."

**Animated logo backdrop (session 34):** `.bg-logo` — a faint `logo.png` watermark behind the app (z-0, below z-1 content), accent-tinted glow via `--ac-rgb` (so it flips red in bearish mood), slow float/breathe (`bgLogoFloat`/`bgGlow`), reduced-motion-safe. This is a sanctioned backdrop layer like `#fxCanvas` — keep it faint (opacity ~.05). `.tab-pane.active` uses a short `tabIn` fade-up. New tab components: `.learn-grid`/`.learn-card`/`.learn-text` (visual-academy cards; each SVG diagram framed). `.st-legend`/`.st-leg`/`.st-rank`/`.st-pos` (relative-strength legend + leaderboard) — multi-series lines use a small distinct palette `ST_COLORS` (data-viz exception to the one-accent rule; first series is the accent). Split additions: `.split-grid.n3`, `.sp-notes` (notepad textarea), `.sp-mxrow` (compact market-grid row).

**Matrix / Charts / Split components (session 33):** `.mx-grid`/`.mx-card` (auto-fill market cards, accent left-border keyed to signal class ok/wait/no, hover-lift, `futSparkSVG` trend line, `.mx-stats` 3-up) → click opens Charts. `.ch-bar`/`.ch-search`/`.ch-chip` (TradingView lookup: search input + selectable symbol chips, `.on` = active). `.split-grid.n1|n2|n4` + `.sp-pane`/`.sp-head`/`.sp-sel`/`.sp-body` (side-by-side panes, fixed heights per layout, `<select>`s use `--s3` fill; collapses to 1 col <760px). `.split-layouts`/`.sl-btn` layout toggle. `.pb-phases`/`.pb-phase` (numbered phase legend under the playbook diagram). All from existing tokens; sparkline/diagram use semantic `--gr`/`--rd` for up/down, accent only for the slow MA / chrome.

**Toolkit tabs (session 32):** new components, all built from existing tokens — `.calc-form`/`.calc-field` (labelled inputs + select, `--s2` fill, accent focus ring) → `.calc-out`/`.co` result tiles; `.spec-tbl` (right-aligned numeric contract-spec table); `.sess-row` (session clock row, `.on` = open → green dot + tinted border); `.pb-check` (live checklist, `.yes`/`.no` → green/red icon chip) + `.pb-rule`/`.pb-num` (numbered rule list). Candlesticks use the semantic `--gr`/`--rd` (up/down only) — not the accent.

Aesthetic: **premium dark terminal** — near-black, data-first, professional, with depth. Dark-gray surfaces, white type, an **emerald-green accent**, and a crafted animated background (`#fxCanvas`) + a floating glass nav. (As of session 8 the look moved from "flat minimal" toward "premium/designed" with deliberate glow/depth where the user asked for it — see the background + nav notes below.)

## Color tokens (CSS vars in `:root`)
| Token | Value | Use |
|---|---|---|
| `--bg` | `#050505` | page background (near-black) |
| `--s1..s4` | `#0c0c0e … #222328` | dark-gray surfaces |
| `--ink / --ink2 / --ink3` | `#f3f4f6 / #a6abb5 / #6a6d76` | text / muted / faint |
| `--ac` | `#22c55e` | **emerald-green accent** — brand + bullish; used generously in chrome (was blue `#2f81f7` ≤ session 7) |
| `--cy` / `--pp` | = `--ac` | collapsed to the single accent (legacy names) |
| `--act` | `#86efac` | lighter accent text |
| `--gr / --gt` | `#22c55e / #4ade80` | **UP / profit only** |
| `--rd / --rt` | `#f43f5e / #fb7185` | **DOWN / loss only** |
| `--em` | `#34d399` | "live"/online status dot |
| `--line / --line2` | white @ 6% / 13% | hairline borders |

### Gradients & effects
- `--grad`, `--grad2`, `--g-fill`, `--g-text` = the **solid accent** now (gradients were removed for the black-minimal direction). `.lx-grad`/`.grad-text` therefore render solid accent text.
- `--glass`: `rgba(255,255,255,.022)` + subtle `backdrop-filter` — glass only where it adds depth.
- `--glow`/`--halo`: reduced to near-flat soft shadows (no colored glow blobs). `--shadow`: deep soft black shadow.
- Background: faint masked grid + ONE very subtle top glow (`body::after`). The `.lx-orb` glowing blobs are `display:none`.

### **Rules:** ONE accent only — use it sparingly to direct attention. green/red mean direction (up/down, P&L) ONLY. No big gradients, no glowing blobs, no decorative/AI/stock graphics. Realism (terminal panels, real data shapes) over decoration.

## Spacing & shape
- Radius: `--radius:18px`, `--rsm:13px`, `--rxs:8px` (cards 16–20px). Landing media/panels 20px.
- Spacing leans generous; landing sections ~88–120px vertical. App column max-width ~1180px, centered.

## Typography
- Sans: system stack (`-apple-system, Inter, Segoe UI…`). Mono: `--mono` (SF Mono/Fira Code) for prices, tickers, numbers.
- Landing display type is oversized (`clamp` up to ~86px), tight tracking (`letter-spacing:-.04em`), weight 800.
- App headings smaller; labels are small-caps muted.

## Components
- **Card** `.card` — FLAT since 2026-07-01: `var(--s1)` fill, hairline `--line` border, hover = border-color shift only (no blur/lift/glow — see the top note). `.glass` remains translucent where still used.
- **Buttons:** `.lx-btn.primary` / `.go-btn` = animated gradient (`gradShift`), white text. `.lx-btn.ghost` / `.nbtn` = glass outline, blue hover.
- **Nav:** glass blurred bar; active tab = gradient underline. Landing nav solidifies on scroll (`.scrolled`).
- **Icons:** minimal **line SVGs** (stroke `--cy`), 1.8–2.2 stroke. **Avoid emoji** in chrome (legacy emoji still linger in some inner tabs — replace when touched).
- **Sentiment-reactive theme:** the accent is a flippable RGB token `--ac-rgb` (chrome greens are `rgba(var(--ac-rgb),…)`). `body.bearish` overrides `--ac`/`--ac-rgb`/`--act`/`--bt`/`--grad` to **red**; `setMood(sentiment)` (from `renderDash`) toggles it + `window.FX_MOOD` (which colour-eases the `#fxCanvas`). Green = bullish/neutral, red = bearish. P&L candle colours (`--gr/--rd`) stay semantic and do NOT flip. Keep this — the whole UI reflecting the read is intentional.
- **Logo = original bull-head line mark** (white on the accent tile, so it glows red when bearish). **Mascots:** `BULL_SVG`/`BEAR_SVG` original line-art shown in the dashboard AI-read panel (`.mood-beast`), bull for bullish/neutral, bear for bearish.
- **Animated background (deliberate exception to "no glow"):** `#fxCanvas` is a site-wide living-market backdrop — aurora depth-blobs + perspective grid + parallax data-constellation + trade-print flashes. The user explicitly asked for this "wow" depth, so the old "no glowing blobs" rule does **not** apply to this background layer (it still applies to chrome/cards/buttons). Don't flatten it away.
- **Brand:** **STRATA** (was TradeLens). Logo mark = three ascending blocks ("rising strata") in white on the solid-accent (`--ac`) tile; wordmark "STRATA" + sub "Structure Terminal". Used in `.appnav` (app), `.lx-nav` (landing) and the footer.
- **App nav namespace `appnav`/`snav`** — a **premium animated floating rail** (inset 14px, rounded glass, layered shadow, accent top-hairline; icon-rail under 1080/640px). `.appnav-logo` → grouped `.snav` items → `.appnav-foot`. Interactions (all in `initPremiumNav`, spring `cubic-bezier(.34,1.56,.5,1)`): **gliding active pill** `#snavGlide` (moved from `mainTab`→`snavGlideTo`), **hover highlight** `#snavHover`, **cursor glow** `#snavCursor`, **magnetic hover** (item transform toward cursor), spring icon hover. The app top bar `.appbar` carries the streaming **movers banner** (`.mv` cells). High Volume cards = `.mvc`. Don't revert this to a plain navbar — it's intentional brand identity.
- **Dashboard namespace `dash-`** (the post-launch terminal, written by `renderDash`): `.dash-cmd` (ask bar) → `.dash-head` (ticker header) → `.dash-grid` (`1fr 352px`, collapses ≤980px) of `.dash-panel`s: chart / Trade Plan (`.lv-table`, `.dp-*`) / AI read (`.conv-bar`) / `.dash-metrics` (`.dm`) / signals (`.sig-row`). Flat `--s1` panels, hairline borders, mono numerals, **one** accent. Replaces the old `.cp-*` chat.
- **Landing namespace `lx-`**: `.lx-hero`, `.lx-panel` (3D tilt + parallax), `.lx-float`, `.lx-row` (alternating showcase), `.lx-band`, `.lx-step`, `.lx-plan` (pricing; `.hot` = featured), `.lx-final`, `.lx-footer`. As of session 6 these are flat dark surfaces + hairline borders + single accent (the residual blue→cyan→purple gradients and glows were removed).

## Motion
- Keyframes: `fadeUp`, `gradShift`, `floatGlow`, `orbA/B/C` (drifting background orbs), `draw` (SVG line draw-in), `candUp` (candle rise), `pulseDot`/`pulse`.
- Reveal: `.lx-reveal` → `.in` via IntersectionObserver. Count-up via `.lx-count[data-to]`. Respect `prefers-reduced-motion`.
- Keep app animations subtle; landing is where motion shines.

## Conventions / do & don't
- DO reuse tokens; DON'T hardcode hex for chrome (use `--ac`, `--cy`, gradients).
- DO keep real data honest; DON'T add fake/sample prices to "look alive."
- DO prefer line icons + plain-language labels with tooltips for jargon (RSI→"Momentum", etc.).
- Landing uses `lx-` classes; the app uses legacy classes (`.card`, `.ntab`, `.metric`, `.setup-grid`…) now re-themed blue/glass — when restyling the app, push it toward the landing's spacing/calm.
