# RoomWaves Design System Guide

This guide defines and standardises the design patterns, interactive elements, and architectural rules used in RoomWaves.

---

## 1. Core Visual Language

RoomWaves uses a **technical, high-contrast, sage-marine** aesthetic:
- **Foundations**: Hard edges, pure black backgrounds (`#000000`), and layered gray-sage elevations.
- **Accents**: Warm Sage (`#83BCA9`) as the main interactive signal, paired with Warm Peach (`#E09F67`) for secondary accents.
- **Typography**: Humanist `Varta` for clean interface navigation (strictly limited to weights 300 and 400), and `JetBrains Mono` for precise metrics and mathematical values (which can use weights up to 700).
- **Borders & Shadows**: Depth is created through a mix of tonal color shifts and Flat Architectural hard borders with offset solid shadows.

---

## 2. Typography Constraints & Standards

### A. Font Weight Limitations (Varta Restriction)
- **Varta (`font-ui` & `font-brand`)**: Strictly forbidden from exceeding weight `400`. Only `300` (Light) and `400` (Regular) weights are permitted. Bold Varta elements are not allowed to maintain a clean, lightweight, humanist appearance.
- **JetBrains Mono (`font-mono`)**: Allowed to use bold weights (`500`, `600`, `700`) for technical numbers, frequencies, code variables, and telemetry parameters to pop out on dashboards.

### B. Font Size Minimum Limit
- **General Rule**: No readable user-facing text, parameters, button text, badges, tags, or table headers may be sized below `13px`. Bounding text to a minimum of `13px` ensures strong readability and contrast.

---

## 3. Global Site Navigation & Header

The main site navigation header operates at a fixed height of `70px` and behaves dynamically based on scroll position:
- **At Top**: `transparent` background with no border or blur.
- **Scrolled**: Semi-translucent deep marine (`rgba(0, 26, 35, 0.94)`) with an `18px` backdrop-filter blur and a bottom border.

### Interactive Buttons

#### A. Navigation Dropdowns (`NavDropdown`)
Dropdown buttons use a custom animated `.circles` dot indicator next to their labels. On hover, the background dot(s) retract behind the front teal-black dot:
- **Default Variant**: 1 offset dot (`left: 8px; top: 4px;`) collapsing to center on hover.
- **Corners Variant**: 4 dots at the corners collapsing to center on hover.
- **Horizontal Variant**: 2 side dots collapsing to center on hover.
- **Triangle Variant**: 3 dots forming a triangle collapsing to center on hover.

#### B. Modelling Button (`builder-btn`)
- **Idle**: 5% opacity sage background, active signal border, and active text.
- **Hover**: 15% opacity sage background, active dim border, and the plus icon rotates `90deg` and scales to `1.2x` using an elastic easing curve.

#### C. Log In Button (`login-btn-new`)
- **Idle**: Solid white background pill, teal-black text (`var(--surface-0)`).
- **Hover**: Translates `translateY(-1px)` and dims opacity to `90%` for a tactile lift.

---

## 4. Home View Hero Section

The hero section covers the full viewport height minus the header (`calc(100vh - 70px)`).

### Layout
- **Left Head**: "3D Model your Room Acoustics" (Varta Light, 48px, line-height 1.1).
- **Right Head**: "No knowledge required." (Varta Light, 48px, text-align right).
- **Background Layer**: 3D particle canvas (`HeroWave3D`) with a vertical gradient mask:
  ```css
  mask-image: linear-gradient(to bottom, black 60%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, black 60%, transparent 100%);
  ```
  This ensures the canvas blends seamlessly into the teal-black content sections below.

### "Model Now" CTA Button
- **Style**: Sage border (`2px solid var(--accent-lime)`), `12px 32px` padding, fully rounded, with a `rgba(131, 188, 169, 0.2)` background and sage glow.
- **State Animations**: 
  - **Idle**: Slow breath pulsing box-shadow.
  - **Hover**: Translates `translateX(10px)` with background changing to `rgba(131, 188, 169, 0.3)` and box-shadow expanding to `0 0 30px`.

---

## 5. Standard Buttons

Every button in the application must fit into one of these four standardized categories:
- **Primary Action (Emissive Pill)**: Fully rounded pill button, background `rgba(131, 188, 169, 0.2)`, border `2px solid var(--accent-lime)`. Animates with a breathing glow and translates on hover. Used for key conversion calls (e.g. hero CTA).
- **Tactile Nav Button**: Rounded capsule button (30px radius), border `1px solid var(--border-default)`. Displays custom `.circles` dot indicators. Used for navbar selections and secondary options.
- **Utility Tonal Button**: Rectangular utility button (4px radius), border `1px solid var(--border-default)`, background `var(--surface-2)`. Transitions border color to bold and background to surface 3 on hover. Used for builder toolbar decks, options widgets, and forms.
- **Solid Contrast Pill**: White pill background, dark teal-black text (`var(--surface-0)`). Used for main authentication triggers (e.g. log in).

---

## 6. Standard Cards & Panels (Neo-Brutalist Style)

All panels and container layout cards are structured using three distinct elevation models:
- **Flat Architectural Glass Card (Setup panel style)**: Used strictly for **major container docks** (builder setup panel, toolbar decks, major dashboards). Combines a translucent glass background (`rgba(0, 26, 35, 0.65)`), backdrop blur (`blur(10px)`), a lighter translucent border (`1px solid rgba(255, 255, 255, 0.2)`), standard rounded corners (`var(--radius-md)` / 8px), standard padding (`24px`), and a sharp `4px 4px` offset zero-blur shadow.
  - **3D Lift Animation**: On hover, the card raises up and left, and the offset zero-blur shadow expands beneath it to create a tactile lift:
    ```css
    transform: translate(-3px, -3px);
    box-shadow: 4px 4px 0px 0px var(--surface-0);
    transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
    ```
  - **Color Adaptation**: Standard shadows use `var(--surface-0)` (`#000000`). When active or highlighted, adapt the shadow color to `var(--accent-lime)` (`#83BCA9`).
- **Glassmorphic Floating Card**: Translucent white overlay background (`rgba(255, 255, 255, 0.05)`), border `1px solid rgba(255, 255, 255, 0.10)`, standard rounded corners (`var(--radius-md)` / 8px), standard padding (`24px`), and a `12px` backdrop blur. Used for floating controls, tool tips, and overlays.
- **Elevated Tonal Card**: Flat background (`var(--surface-1)`) and low-contrast borders (`var(--border-ghost)`). Rounded corners are locked to `var(--radius-md)` (8px) and padding is standard `24px`. Used for swatches, icon tiles, room grid lists, collection items, and nested UI panels.
- **Floating Pill Panel (Toolbar Dock Style)**: Floating HUD panels (e.g. `BuilderToolbar.vue`) must use a capsule profile (`border-radius: var(--radius-pill)` / 9999px), translucent panel background (`var(--surface-2)`), thin border (`1px solid var(--border-default)`), and circular tool buttons (`border-radius: 50%`).

---

## 7. Design Tokens Reference

### Theme Variables

#### A. Dark Theme (Default)
- **Surface 0 (Base)**: `#000000` (Pure Black · app base, 3D canvas background, hero bg)
- **Surface 1 (Containers)**: `#0A0A0C` (Near Black · cards, primary layouts)
- **Surface 2 (Inner Panels)**: `#141416` (Dark Charcoal · nested panels, inputs)
- **Surface 3 (Overlays/Modals)**: `#1E1E21` (Mid Charcoal · modals, elevated overlays)
- **Surface 4 (Active/Hover)**: `#2A2A2E` (Lift Charcoal · hover states, active backgrounds)
- **Warm Sage (Primary Accent)**: `#83BCA9`
- **Sage Pressed (Primary Accent Hover)**: `#6FA794`
- **Warm Peach (Secondary Accent)**: `#E09F67`
- **Border Ghost**: `#0C313E` (quiet dividers, card borders)
- **Border Default**: `#124254` (standard interactive boundaries)
- **Border Bold**: `#1E586E` (selected states, focused accents)

#### B. High-Contrast Light Theme
- **Surface 0 (Base)**: `#F4F6F5` (Soft grey-sage base background)
- **Surface 1 (Containers)**: `#FFFFFF` (Pure White cards/containers for elevated pop)
- **Surface 2 (Inner Panels)**: `#EEF2F0` (Slightly darker grey-sage for faders/nested panels)
- **Surface 3 (Overlays/Modals)**: `#E1E7E4` (Modals and dropdown elements)
- **Surface 4 (Active/Hover)**: `#D4DBD8` (Hover states)
- **Primary Accent**: `#1F6851` (Deep sage green for high text contrast)
- **Primary Accent Hover**: `#164E3C`
- **Secondary Accent**: `#8E4B16` (Deep warm peach/amber)
- **Text White (Headers)**: `#0B1714` (Deep charcoal-teal)
- **Text Offwhite (Subheadings)**: `#152924`
- **Text Silver (Body)**: `#2C3E3A` (Highly readable body text)
- **Text Gray (Muted labels)**: `#4A605B`
- **Border Ghost**: `rgba(0, 0, 0, 0.08)`
- **Border Default**: `#BFCFC9`
- **Border Bold**: `#1F6851`

### Border Radii Scale
- **Radius Small (sm)**: `4px` (Form controls, HUD buttons, badges)
- **Radius Medium (md)**: `8px` (Standard cards, room lists, configuration panels)
- **Radius Large (lg)**: `12px` (Bento cards, main setups, popup containers)
- **Radius Pill (pill)**: `9999px` (Navbar selection tabs, floating toolbars, pill buttons)

### Easing Transitions
- **Premium Ease (Reveal / Page Transitions)**: `cubic-bezier(0.2, 1, 0.3, 1)`
- **Material Ease (Hover / Interactions)**: `cubic-bezier(0.4, 0, 0.2, 1)`
- **Elastic Ease (Icon Reveals)**: `cubic-bezier(0.68, -0.55, 0.27, 1.55)`
- **Direct Ease (Drawers / Overlays)**: `cubic-bezier(0.25, 0, 0.25, 1)`

