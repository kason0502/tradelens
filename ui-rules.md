# STRATA — UI Rules

> Last updated: 2026-07-01
> Enforce these rules in every UI change. No exceptions without explicit approval.

## Core Principles

### 1. Data First, Chrome Second
Every pixel exists to serve data. If a visual element doesn't help the trader make a decision, remove it. Bloomberg's power comes from density without clutter — aspire to that.

### 2. Trust Through Honesty
- **Real data only.** Never fake, simulate, or approximate prices.
- **Label everything.** Every number carries its source, window, and sample size.
- **Admit uncertainty.** "Consistent with the edge generalizing" > "Validated on X".
- **Show the math.** Click-to-expand proof windows for any claim.

### 3. One Accent, Zero Confusion
- **Emerald `#22c55e`** is the brand accent. Used for active states, CTAs, and chrome highlights.
- **Green `--gr` / Red `--rd`** mean UP/DOWN (P&L direction) ONLY. Never decorative.
- **No other accent colors.** Multi-series charts use a controlled palette (`ST_COLORS`) as a data-viz exception.

---

## Color System

### Surfaces (dark → light)
```
--bg:  #050505   Page background (near-black)
--s1:  #0c0c0e   Card/panel background
--s2:  #14141a   Input fills, secondary surfaces
--s3:  #1a1a22   Hover states, raised surfaces
--s4:  #222328   Borders, elevated elements
```

### Text (light → dim)
```
--ink:  #f3f4f6   Primary text (high contrast)
--ink2: #a6abb5   Secondary text (labels, descriptions)
--ink3: #6a6d76   Tertiary text (timestamps, units, footnotes)
```

### Semantic Colors
```
--ac:  #22c55e    Accent (brand emerald)
--act: #86efac    Accent text (lighter emerald)
--gr:  #22c55e    UP / Profit (semantic green)
--gt:  #4ade80    UP text (lighter)
--rd:  #f43f5e    DOWN / Loss (semantic red)
--rt:  #fb7185    DOWN text (lighter)
--em:  #34d399    Live/online status
```

### Borders
```
--line:  rgba(255,255,255,0.06)   Hairline borders
--line2: rgba(255,255,255,0.13)   Emphasized borders
```

---

## Typography

### Font Stack
- **Sans:** `-apple-system, Inter, Segoe UI, system-ui` — for all UI text
- **Mono:** `SF Mono, Fira Code, monospace` — for prices, tickers, numeric data

### Scale
- Display (landing): `clamp(2rem, 5vw, 86px)`, weight 800, tracking -0.04em
- Heading: 20-24px, weight 700
- Body: 14-15px, weight 400
- Label: 10-11px, uppercase, letter-spacing 0.08em, color `--ink3`
- Numeric: 22px tabular-nums, font-variant-numeric: tabular-nums

### Number Display Rules
1. **Always tabular-nums** — numbers must align in columns
2. **True minus U+2212** for negatives (not hyphen-minus)
3. **Unit spans** — trailing `$`, `%`, `x`, `d`, `R` in `.nu` spans (0.7em, `--ink3`)
4. **Mono font** for all prices and numeric values
5. **Right-align** numeric columns in tables

---

## Component Rules

### Cards (`.card`)
- **FLAT design** — `background: var(--s1)`, 1px `--line` border
- Hover: border-color shift only — NO blur, NO lift, NO glow
- No backdrop-filter on cards (removed as of 2026-07-01)
- Exception: `.appnav`, `.acct-chip`, `.dte-row`, `.metric` retain glass

### Stat Tiles
- Value: 22px tabular-nums
- Label: 10px uppercase, letter-spacing 0.08em
- Sub: 10.5px, `--ink3`
- Use existing classes: `.bt-stat`, `.bt-score`, `.sp-grid`, app `.stat`
- **Do NOT invent new stat tile families**

### Skeleton Loaders (`.skel-card`)
- Fixed height, `skelShine` shimmer via `::after`
- Animation off under `prefers-reduced-motion`
- Use instead of "Loading…" text to prevent layout shift

### Pay-Lock Cards (`.pay-lock`)
- Solid border + accent top hairline (`::before`)
- Line-SVG lock badge (no emoji)
- Optional blurred real-content teaser (`.pl-prev`, blur 6px)
- Teaser reuses REAL renderer output — never fork markup

### Icons
- **Line SVGs** (stroke `--cy`, 1.8-2.2 stroke-width)
- **No emoji** in chrome — replace on sight
- Labels: plain language with tooltips for jargon

---

## Layout Rules

### App Structure
```
.appnav (sidebar, 200px)  |  .page-wrap
                           |    .appbar (sticky movers tape)
                           |    .main-col (max-width ~1180px, centered)
                           |      tab panes
```

### Mobile Breakpoints
- **≤1080px:** Sidebar collapses to icon rail
- **≤640px:** Icon rail minimum
- **≤520px:** Bottom dock navigation (horizontal scroll)
- **≤480px:** Full-width cards, single column, no side gutters

### Panel Grid
- Default: `1fr 352px` (main + sidebar) — collapses at ≤980px
- Use CSS Grid, not flexbox, for panel layouts
- Minimum card width: 280px
- Gap: 12-16px between panels

---

## Motion Rules

### Allowed Animations
- `fadeUp` — panel entrance (0.3s ease-out)
- `skelShine` — skeleton loader shimmer
- `tabIn` — tab switch transition
- `tweenPrice` — live price number animation
- `gradShift` — CTA button gradient
- `#fxCanvas` — full background animation system (the ONE deliberate exception)

### Forbidden
- Bounce effects on data elements
- Spinning loaders (use skeleton shimmer instead)
- Auto-playing video backgrounds
- Parallax on data panels (reserved for landing only)

### `prefers-reduced-motion`
ALL animations must respect this. Test by enabling it.

---

## Sentiment-Reactive Theme

The UI reflects market sentiment:
- **Bullish/Neutral:** Emerald accent throughout
- **Bearish:** Red accent override via `body.bearish`
- `setMood(sentiment)` toggles `--ac-rgb` and `window.FX_MOOD`
- P&L candle colors (`--gr`/`--rd`) stay semantic — they do NOT flip

---

## STRATA Brand Elements

### Logo Motif
- Three ascending blocks (`.ct-glyph`) — use on **flagship card titles only**
- Keep it scarce — max 3 instances across the entire app
- "Rising strata" = the geological layers metaphor

### Strata Bands
- Alternating ~1.5-2% white horizontal bands
- Used ONLY inside `strataChart` and app's compact `equitySVG`

### Layered Dividers
- 3 stacked hairlines at 6/4/2% opacity with width offsets
- Landing sections only

---

## Anti-Patterns (Never Do These)

1. ❌ Fake/simulated market data
2. ❌ Multiple accent colors
3. ❌ Emoji in UI chrome
4. ❌ Backdrop-filter on cards
5. ❌ Hover animations that lift cards
6. ❌ Gradient fills on data surfaces
7. ❌ Stock photos or decorative illustrations
8. ❌ "AI" badge/glow on every element
9. ❌ Modal dialogs for non-critical actions
10. ❌ Auto-scrolling content that disrupts reading

---

## Quality Checklist (Before Any UI PR)

- [ ] All numbers use tabular-nums + mono font
- [ ] Negative numbers use U+2212
- [ ] Units in `.nu` spans
- [ ] No new emoji introduced
- [ ] Mobile tested at 375px and 520px
- [ ] `prefers-reduced-motion` respected
- [ ] Skeleton loaders for async content
- [ ] Semantic green/red used correctly (P&L only)
- [ ] No new accent colors introduced
- [ ] Accessibility: focusable, labeled, sufficient contrast
