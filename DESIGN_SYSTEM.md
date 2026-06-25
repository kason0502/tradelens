# TradeLens Pro — Design System

> Living doc. Update when tokens, components, or visual conventions change.
> Last updated: 2026-06-25

Aesthetic: **premium fintech / institutional**, dark glass. Charcoal base, electric blue→cyan→purple gradients, frosted glass, soft glows, generous spacing, oversized type on the landing. Calm and trustworthy, not flashy.

## Color tokens (CSS vars in `:root`)
| Token | Value | Use |
|---|---|---|
| `--bg` | `#0B0F14` | page background |
| `--s1..s4` | `#111722 … #243044` | raised surfaces |
| `--ink / --ink2 / --ink3` | `#eff3fb / #aeb9ca / #6f7a8c` | text / muted / faint |
| `--ac` | `#3b82f6` | **primary brand/UI accent (electric blue)** |
| `--cy` | `#22d3ee` | cyan (gradient + icon strokes) |
| `--pp` | `#8b5cf6` | purple (gradient) |
| `--act` | `#93c5fd` | light blue text |
| `--gr / --gt` | `#22c55e / #4ade80` | **UP / profit only** |
| `--rd / --rt` | `#f43f5e / #fb7185` | **DOWN / loss only** |
| `--em` | `#34d399` | "live"/online status dot |
| `--line / --line2` | white @ 6% / 13% | hairline borders |

### Gradients & effects
- `--grad` / `--g-fill`: `linear-gradient(135deg,#3b82f6,#22d3ee,#8b5cf6)` — primary gradient.
- `--g-text`: blue→cyan→violet for gradient text (`.lx-grad`, `.grad-text`).
- `--grad2`: `linear-gradient(135deg,#22d3ee,#3b82f6)`.
- `--glass`: `rgba(255,255,255,.035)` + `backdrop-filter:blur(16-20px)`.
- `--glow`, `--shadow`, `--halo`: soft blue glow + deep soft shadows (never harsh).

### **Rule:** green/red mean direction (up/down, profit/loss) ONLY. Everything brand/interactive is blue/cyan/purple. Don't tint UI chrome green.

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
- **Landing namespace `lx-`**: `.lx-hero`, `.lx-panel` (3D tilt + parallax), `.lx-float`, `.lx-row` (alternating showcase), `.lx-band`, `.lx-step`, `.lx-plan` (pricing; `.hot` = featured), `.lx-final`, `.lx-footer`.

## Motion
- Keyframes: `fadeUp`, `gradShift`, `floatGlow`, `orbA/B/C` (drifting background orbs), `draw` (SVG line draw-in), `candUp` (candle rise), `pulseDot`/`pulse`.
- Reveal: `.lx-reveal` → `.in` via IntersectionObserver. Count-up via `.lx-count[data-to]`. Respect `prefers-reduced-motion`.
- Keep app animations subtle; landing is where motion shines.

## Conventions / do & don't
- DO reuse tokens; DON'T hardcode hex for chrome (use `--ac`, `--cy`, gradients).
- DO keep real data honest; DON'T add fake/sample prices to "look alive."
- DO prefer line icons + plain-language labels with tooltips for jargon (RSI→"Momentum", etc.).
- Landing uses `lx-` classes; the app uses legacy classes (`.card`, `.ntab`, `.metric`, `.setup-grid`…) now re-themed blue/glass — when restyling the app, push it toward the landing's spacing/calm.
