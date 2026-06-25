# TradeLens Pro — Design System

> Living doc. Update when tokens, components, or visual conventions change.
> Last updated: 2026-06-25

Aesthetic: **Bloomberg/terminal minimal** — pure black, data-first, professional. Mostly black with dark-gray surfaces, white type, ONE accent used sparingly to direct attention. No big gradients, no glowing blobs, no decorative graphics. Huge bold headlines, lots of whitespace, 8px rhythm.

## Color tokens (CSS vars in `:root`)
| Token | Value | Use |
|---|---|---|
| `--bg` | `#050505` | page background (near-black) |
| `--s1..s4` | `#0c0c0e … #222328` | dark-gray surfaces |
| `--ink / --ink2 / --ink3` | `#f3f4f6 / #a6abb5 / #6a6d76` | text / muted / faint |
| `--ac` | `#2f81f7` | **the single accent (blue)** — use only to direct attention |
| `--cy` / `--pp` | = `--ac` | collapsed to the single accent (legacy names) |
| `--act` | `#7db3ff` | lighter accent text |
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
