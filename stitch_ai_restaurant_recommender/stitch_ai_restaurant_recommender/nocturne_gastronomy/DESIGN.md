---
name: Nocturne Gastronomy
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#bbcabd'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#869488'
  outline-variant: '#3c4a40'
  surface-tint: '#49e095'
  primary: '#60f3a6'
  on-primary: '#003920'
  primary-container: '#3dd68c'
  on-primary-container: '#005834'
  inverse-primary: '#006d41'
  secondary: '#c8c6c5'
  on-secondary: '#313030'
  secondary-container: '#4a4949'
  on-secondary-container: '#bab8b7'
  tertiary: '#ffd0b1'
  on-tertiary: '#4f2500'
  tertiary-container: '#ffaa6c'
  on-tertiary-container: '#783c05'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6bfdaf'
  primary-fixed-dim: '#49e095'
  on-primary-fixed: '#002110'
  on-primary-fixed-variant: '#005230'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1c1b1b'
  on-secondary-fixed-variant: '#474646'
  tertiary-fixed: '#ffdcc6'
  tertiary-fixed-dim: '#ffb784'
  on-tertiary-fixed: '#301400'
  on-tertiary-fixed-variant: '#713700'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  headline-xl:
    fontFamily: Newsreader
    fontSize: 44px
    fontWeight: '400'
    lineHeight: 52px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Newsreader
    fontSize: 32px
    fontWeight: '400'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Newsreader
    fontSize: 32px
    fontWeight: '400'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Newsreader
    fontSize: 26px
    fontWeight: '400'
    lineHeight: 34px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Newsreader
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Newsreader
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
    letterSpacing: '0'
  body-lg:
    fontFamily: Manrope
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Manrope
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: '0'
  body-sm:
    fontFamily: Manrope
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-lg:
    fontFamily: Manrope
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.02em
  label-md:
    fontFamily: Manrope
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.03em
  label-sm:
    fontFamily: Manrope
    fontSize: 10px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-desktop: auto
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

The design system establishes a high-craft, dark-mode-only editorial aesthetic tailored for an intelligent culinary concierge. Moving beyond the chaotic visual noise of legacy food aggregators, this aesthetic embodies restraint, sharp curation, and quiet confidence.

The visual style blends **Minimalism** with **Tonal Layering and Low-Contrast Structural Detailing**:
- **Tone:** Discerning, intelligent, intimate, and effortlessly refined.
- **Imagery & Visuals:** No generic stock photography or hyper-saturated food arrays. Visual interest is driven by high-density typography, micro-borders, razor-sharp status indicators, and deliberate contrast.
- **Micro-Interactions:** Snappy, low-friction transitions without bouncy physics. Everything feels weighted, deliberate, and high-performance.

## Colors

The palette is engineered exclusively for an immersive, pitch-dark viewing environment, calibrated to draw immediate focus to curated culinary narratives and actionable metadata.

- **Canvas Background (`#050505`):** The deepest foundation level; frames the central feed and maintains seamless optical immersion.
- **Surface Level 1 (`#121212`):** Primary base for grouped listing cards, contextual overlays, and modal backgrounds.
- **Surface Level 2 (`#141414`):** Secondary interactive cards, nested metadata containers, segmented controls, and hover layers.
- **Structural Borders & Dividers (`#2A2A2A`):** Low-contrast architectural frames that establish separation without visual clutter.
- **Primary Text (`#F2F2F2`):** High-legibility off-white for headers, restaurant names, primary metrics, and titles.
- **Muted Text (`#A3A3A3`):** Neutral gray for tertiary tags, culinary tags, neighborhood annotations, and timestamps.
- **Accent Mint (`#3DD68C`):** Emerald mint reserved strictly for functional utility: primary CTAs, active segmented toggles, precision rating scores, focus rings, and verified status badges.

## Typography

The pairing between the editorial serif (`Newsreader`) and technical sans (`Manrope`) creates tension between literary food criticism and rapid AI curation.

- **Headlines (`Newsreader`):** Used for venue titles, editorial critique excerpts, and section leads. It mimics physical food reviews and boutique tasting menus. Keep tracking tight to retain ink-like weight.
- **Body & Controls (`Manrope`):** Handles dense AI summaries, reservation slots, distance calculations, and metadata. Its geometric construction ensures supreme legibility at small sizes (`10px`–`14px`) against dark backdrops.

## Layout & Spacing

The layout is built around a single, highly focused feed that avoids horizontal scatter and keeps the user centered on recommendations.

- **Desktop Layout:** A single centered column strictly constrained to a maximum width of `960px`, framed automatically with auto side margins. Information sits in structured stacks or compact 2-column detail grids.
- **Mobile Layout:** Full-bleed stacked vertical layout with `1rem` outer canvas padding. Every interactive control maintains a minimum touch target height of `44px`.
- **Rhythm:** Spacing follows a dense 4px/8px modular rhythm. Component internals rely on `space-sm` (`8px`) and `space-md` (`16px`), while structural separation between cards uses `space-lg` (`24px`).

## Elevation & Depth

This system intentionally rejects heavy diffuse dropshadows in favor of flat architectural depth and surface contrast.

- **Tonal Stepping:** Depth is achieved by placing `#141414` elements over `#121212` panels, which sit above the `#050505` canvas.
- **Crisp Outlines:** Surfaces are delineated by a 1px solid stroke of `#2A2A2A`. Hover or active states lighten this boundary stroke to `#3D3D3D` or tint it with the `#3DD68C` accent.
- **Focus & Glow:** When interactive elements (e.g., search bars, rating sliders) receive focus, use an inset or tight 2px outer outline of `rgba(61, 214, 140, 0.4)` without soft blurred diffusion.

## Shapes

The interface embraces a continuous curved silhouette to soften the high-contrast dark palette.

- **Cards & Inputs:** Set to an exact radius of `14px` (`rounded-xl`), creating a uniform container architecture.
- **Badges & Segmented Switches:** Use full-radius pill styling for instant micro-classification.
- **Internal Elements:** Nested tags, thumbnails, and inner rating cells scale down to `8px` (`rounded-sm`) to preserve proportional harmony with their `14px` parent boundaries.

## Components

### Buttons
- **Primary CTA:** Background `#3DD68C`, text `#050505` (`label-lg`, weight 700). Minimum height 44px, horizontal padding 20px, border-radius 14px. Hover brings brightness to 105%.
- **Secondary CTA:** Background `#141414`, border 1px solid `#2A2A2A`, text `#F2F2F2`. Hover elevates border to `#3D3D3D`.
- **Ghost Action:** Transparent background, text `#A3A3A3`, hover text `#F2F2F2`.

### Inputs & Search
- Container height minimum 48px, background `#121212`, border 1px solid `#2A2A2A`, border-radius 14px, padding 0 16px.
- Text `#F2F2F2`, placeholder `#A3A3A3`.
- Focus state: border color `#3DD68C`, box-shadow `0 0 0 1px #3DD68C`.

### Cards (Restaurant Recommendation Card)
- Background `#121212`, border 1px solid `#2A2A2A`, border-radius 14px, padding 20px.
- Structure: Header row with venue name (`headline-md`, Newsreader) and accent rating badge (`#3DD68C` numeric text inside `#141414` container). AI summary block (`body-md`, `#A3A3A3`). Footer row with neighborhood tags, price level indicator, and collapsible disclosure trigger.

### Badges & Chips
- **Status Badges:** Height 24px, pill-radius, background `rgba(61, 214, 140, 0.1)`, border 1px solid `rgba(61, 214, 140, 0.25)`, text `#3DD68C` (`label-sm`).
- **Filter Chips:** Height 32px, background `#141414`, border 1px solid `#2A2A2A`, text `#A3A3A3`. When selected: background `#3DD68C`, text `#050505`, border-color `#3DD68C`.

### Segmented Controls
- Container background `#050505`, border 1px solid `#2A2A2A`, border-radius 12px, padding 4px.
- Segment button: height 36px, radius 8px, text `#A3A3A3`. Selected segment: background `#141414`, border 1px solid `#2A2A2A`, text `#F2F2F2`.

### Rating Sliders
- Track height 4px, background `#2A2A2A`, fill `#3DD68C`.
- Thumb: 20px circle, background `#F2F2F2`, border 2px solid `#3DD68C`.

### Collapsible Disclosures (AI Rationale & Menu Highlights)
- Header acts as clickable target (44px height), `#F2F2F2` text, chevron rotates 180deg.
- Expanded body: bordered top divider (1px `#2A2A2A`), background `#141414`, padding 16px, text `#A3A3A3` with highlight phrases bolded in `#F2F2F2`.