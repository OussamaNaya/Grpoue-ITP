---
name: Fournitex ADV Interior
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#434655'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#737686'
  outline-variant: '#c3c6d7'
  surface-tint: '#0053db'
  primary: '#004ac6'
  on-primary: '#ffffff'
  primary-container: '#2563eb'
  on-primary-container: '#eeefff'
  inverse-primary: '#b4c5ff'
  secondary: '#505f76'
  on-secondary: '#ffffff'
  secondary-container: '#d0e1fb'
  on-secondary-container: '#54647a'
  tertiary: '#943700'
  on-tertiary: '#ffffff'
  tertiary-container: '#bc4800'
  on-tertiary-container: '#ffede6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003ea8'
  secondary-fixed: '#d3e4fe'
  secondary-fixed-dim: '#b7c8e1'
  on-secondary-fixed: '#0b1c30'
  on-secondary-fixed-variant: '#38485d'
  tertiary-fixed: '#ffdbcd'
  tertiary-fixed-dim: '#ffb596'
  on-tertiary-fixed: '#360f00'
  on-tertiary-fixed-variant: '#7d2d00'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  title-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-base:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  data-tabular:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  gutter: 24px
  margin-mobile: 16px
  sidebar-width: 260px
---

## Brand & Style
The design system is engineered for high-stakes financial operations, focusing on clarity, precision, and a sense of calm authority. As an internal tool for debt collection and invoice management, the UI prioritizes data density without sacrificing readability or causing cognitive fatigue.

The aesthetic follows a **Modern Corporate** direction. It utilizes generous whitespace, a structured information hierarchy, and soft elevation to distinguish between different functional zones. The interface feels systematic and reliable, using subtle motion and clear state changes to guide users through complex workflows.

## Colors
The palette is rooted in **Corporate Blue**, used strategically for primary actions and focus states to reinforce trust. **Slate Gray** provides a sophisticated neutral base for secondary information and iconography.

*   **Backgrounds:** Use `#f8fafc` (Slate 50) for the main application background to reduce glare. Use pure white `#ffffff` for cards and content containers.
*   **Semantic Accents:** Use high-clarity tones for status indicators. Critical (Red) is reserved for overdue payments or system errors; Warning (Orange) for pending deadlines; and Info (Yellow) for general invoice updates.
*   **Borders:** Use `#e2e8f0` for subtle structural separation.

## Typography
This design system utilizes **Inter** for its exceptional legibility in data-heavy environments. 

*   **Tabular Data:** For invoice numbers and currency amounts, enable tabular figures (`tnum`) to ensure numbers align vertically in data tables.
*   **Hierarchy:** Use `label-caps` for table headers and section overlines. Use `title-sm` for card headings to maintain a compact yet clear vertical rhythm.
*   **Readability:** Maintain a maximum line length of 70 characters for body text in descriptions or modal notes to ensure readability.

## Layout & Spacing
The layout follows a **Fluid Grid** with fixed-width sidebar navigation. 

*   **Desktop:** 12-column grid. The main content area uses `lg` (24px) margins and gutters. 
*   **Sidebar:** Fixed at `260px`. It should remain persistent or collapsible to an icon-only rail on smaller viewports.
*   **Containers:** Use a maximum content width of `1440px` for the dashboard to prevent data tables from becoming too wide to track horizontally.
*   **Rhythm:** Vertical spacing between cards should be `lg` (24px), while spacing inside cards (padding) should be `md` (16px) or `lg` (24px) depending on the content density.

## Elevation & Depth
Depth is created through **Ambient Shadows** and surface layering. 

*   **Level 0 (Base):** Background color `#f8fafc`.
*   **Level 1 (Cards):** White background with a very soft, diffused shadow: `0px 1px 3px rgba(0,0,0,0.05), 0px 4px 6px rgba(0,0,0,0.02)`.
*   **Level 2 (Modals/Dropdowns):** White background with a more pronounced shadow to imply focus: `0px 10px 15px -3px rgba(0,0,0,0.1), 0px 4px 6px -2px rgba(0,0,0,0.05)`.
*   **Borders:** Use 1px solid borders (`#e2e8f0`) as the primary separator for table rows and sidebar divisions rather than shadows to keep the UI feeling "flat" and professional.

## Shapes
The design system uses a **Rounded** language to soften the corporate atmosphere. 

*   **Main Containers:** Large cards and modals use `rounded-xl` (1.5rem) to create a modern, approachable feel.
*   **Form Elements:** Input fields and buttons use standard `rounded-lg` (1rem).
*   **Status Badges:** Use a pill-shaped `rounded-full` for status badges (e.g., "Paid", "Overdue") to distinguish them from interactive buttons.

## Components
Consistent component behavior ensures the internal tool remains efficient for power users.

*   **Sidebar:** Dark or light variant. Active states should use a vertical 4px blue bar on the left edge and a subtle blue tint background for the menu item.
*   **Stats Cards:** Feature a large `headline-md` value, a `label-caps` title, and a small trend indicator (green/red) at the bottom.
*   **Data Tables:** 
    *   Header: Gray background or simple border-bottom with uppercase labels.
    *   Rows: Hover state change to a very light blue tint (`#eff6ff`).
    *   Badges: Low-saturation background with high-saturation text (e.g., Light Red background with Dark Red text for "Critical").
*   **Alert Cards:** Bordered boxes with a left-accent color strip. Icons should correspond to the semantic color.
*   **Modal Dialogs:** Centered, max-width `600px`, using a dark semi-transparent backdrop (`rgba(15, 23, 42, 0.5)`).
*   **Input Fields:** Default state has a light gray border; focus state uses a 2px Corporate Blue ring with a subtle outer glow.