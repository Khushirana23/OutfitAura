---
name: Aura
colors:
  surface: '#fbf9f9'
  surface-dim: '#dbdad9'
  surface-bright: '#fbf9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f3f3'
  surface-container: '#efeded'
  surface-container-high: '#e9e8e7'
  surface-container-highest: '#e3e2e2'
  on-surface: '#1b1c1c'
  on-surface-variant: '#4f4445'
  inverse-surface: '#303031'
  inverse-on-surface: '#f2f0f0'
  outline: '#807475'
  outline-variant: '#d2c3c4'
  surface-tint: '#70585b'
  primary: '#70585b'
  on-primary: '#ffffff'
  primary-container: '#fadadd'
  on-primary-container: '#765e61'
  inverse-primary: '#debfc2'
  secondary: '#5e5e5e'
  on-secondary: '#ffffff'
  secondary-container: '#e2e2e2'
  on-secondary-container: '#646464'
  tertiary: '#5d5f5f'
  on-tertiary: '#ffffff'
  tertiary-container: '#e2e2e2'
  on-tertiary-container: '#636465'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#fbdbde'
  primary-fixed-dim: '#debfc2'
  on-primary-fixed: '#281719'
  on-primary-fixed-variant: '#574144'
  secondary-fixed: '#e2e2e2'
  secondary-fixed-dim: '#c6c6c6'
  on-secondary-fixed: '#1b1b1b'
  on-secondary-fixed-variant: '#474747'
  tertiary-fixed: '#e2e2e2'
  tertiary-fixed-dim: '#c6c6c7'
  on-tertiary-fixed: '#1a1c1c'
  on-tertiary-fixed-variant: '#454747'
  background: '#fbf9f9'
  on-background: '#1b1c1c'
  surface-variant: '#e3e2e2'
typography:
  headline-xl:
    fontFamily: Playfair Display
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Playfair Display
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 28px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Playfair Display
    fontSize: 24px
    fontWeight: '500'
    lineHeight: '1.3'
  body-lg:
    fontFamily: DM Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: DM Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-sm:
    fontFamily: DM Sans
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1'
    letterSpacing: 0.1em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1280px
  gutter: 24px
  margin-mobile: 20px
  margin-desktop: 64px
  stack-lg: 48px
  stack-md: 24px
  stack-sm: 12px
---

## Brand & Style

The design system is anchored in a **Minimalist-Luxe** aesthetic, tailored specifically for a high-fashion Gen-Z demographic. The brand personality is effortless, aspirational, and editorial. It prioritizes clarity and whitespace to allow high-quality product photography to command attention.

The visual direction avoids traditional corporate rigidity, opting instead for a "Digital Atelier" feel. It balances feminine softness with professional structure, ensuring the interface feels like a premium concierge rather than just a storefront. Motion should be fluid and staggered, mimicking the movement of fabric.

## Colors

The palette is intentionally restrained to maintain an editorial atmosphere. 

- **Primary (Blush Pink):** Used sparingly for high-intent actions, soft backgrounds, and delicate accents. It provides warmth and brand recognition without overpowering the content.
- **Secondary (Deep Black):** Reserved for core typography, primary CTA buttons, and structural borders. It provides the "professional" grounding for the brand.
- **Surface (Pure White):** The primary canvas. Generous use of white creates the "premium" feel of a physical fashion magazine.
- **Neutrals:** Soft greys are used for secondary text and subtle dividers, ensuring the interface remains breathable.

## Typography

This design system utilizes a classic Serif/Sans-Serif pairing to bridge the gap between traditional luxury and modern digital utility.

- **Headlines:** `Playfair Display` provides an elegant, high-contrast serif look. Use it for editorial headers, product names, and section titles.
- **Body:** `DM Sans` offers a clean, geometric sans-serif experience that remains legible even at small sizes. Its low contrast complements the ornate nature of the serif headlines.
- **Labels:** Always use `DM Sans` in uppercase with increased letter spacing for navigation items, categories, and utility labels to maintain a sophisticated, organized feel.

## Layout & Spacing

The layout philosophy follows a **Fixed Grid** on desktop and a **Fluid Content** model on mobile. 

- **Desktop:** 12-column grid with a maximum width of 1280px. Margins are intentionally wide (64px) to create an "inner-frame" effect typical of premium lookbooks.
- **Mobile:** 4-column fluid grid. Margins shrink to 20px, but vertical rhythm remains loose to prevent visual clutter.
- **Rhythm:** Use the 8px base unit. Product cards should have generous bottom margins to clearly separate collections. Use "whitespace as a divider" rather than physical lines whenever possible.

## Elevation & Depth

To maintain a minimal feel, this design system avoids heavy shadows. 

- **Subtle Depth:** Use very soft, diffused shadows (0px 4px 20px rgba(0,0,0, 0.04)) only for floating elements like navigation bars or cart drawers.
- **Tonal Layering:** Use the Primary Blush color at 5-10% opacity as a background fill for cards to create depth without using shadows.
- **Interaction:** On hover, product cards should not lift. Instead, use a subtle "soft focus" transition or a slight image scale-up (1.05x) to indicate interactivity.

## Shapes

The shape language is **Refined & Rounded**. 

- **Primary Elements:** Buttons and input fields use a standard 0.5rem (8px) radius. This balances the sharp edges of high-fashion photography with the approachability of Gen-Z aesthetics.
- **Product Imagery:** Images should remain sharp (0px radius) to emphasize the architectural lines of the clothing, while UI containers (modals, cards) use the `rounded-lg` (16px) or `rounded-xl` (24px) tokens.

## Components

- **Buttons:** Primary buttons are Solid Black with White text, using the `rounded` token. Secondary buttons use an Outlined Black style or a Solid Blush Pink for promotional actions.
- **Chips:** Used for sizing or filters. These should be pills (max roundedness) with a 1px soft grey border. Active states use a Solid Black fill.
- **Input Fields:** Minimalist design with only a bottom border (1px) that turns Black on focus. Labels should use the `label-sm` typography style.
- **Cards:** Product cards must be borderless. The image should be the dominant element, with the product name in `body-md` and price in `label-sm` (without the uppercase transformation).
- **Navigation:** The header should be persistent but transparent/frosted until scrolling, keeping the focus on the hero photography.
- **Shopping Bag:** A slide-out drawer rather than a new page, using the `rounded-xl` token on its leading edge to create a soft, welcoming layer.