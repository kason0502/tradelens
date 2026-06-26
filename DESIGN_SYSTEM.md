# TradeLens Pro — Design System

> Living doc. Update when tokens, components, or visual conventions change.
> Last updated: 2026-06-26 (session 7)

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
- **Glass card** `.glass` / `.card` — translucent + blur + hairline border + soft shadow; hover lifts with a faint blue glow.
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
