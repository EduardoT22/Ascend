# Ascend brand — exactly as the logo

Logo file: `ascend-logo.png` (MIST 2090 portfolio, Eduardo Torres and Thomas Burdell).

- Logo: stylized A, with a sharp swoosh
- Gradient, left to right: pink `#FF4D8D` → magenta `#D500E6` → purple `#7C2FF7` → blue `#2E7DFF`
- Wordmark: ASCEND, dark navy `#0A1931`
- Tagline: RISE. TRACK. BECOME MORE. — in the gradient, spaced letters
- App background (wireframes): near-black navy `#0F0F1E`
- Accent purple (buttons/links): `#A855F7`
- Hydration (wireframes): teal, Calories: orange/yellow — used only for those metrics, not the logo gradient

Use these exact hex codes everywhere: app.py CSS, .streamlit/config.toml,
notebook charts, README. Do not invent a different purple or pink.

## White background version (Nov 19, 2026)
- App background is WHITE #FFFFFF, text navy #0A1931 — not dark.
- Logo file `ascend-logo-transparent.png`: white background removed,
  so the logo blends into white. Corners are fully transparent.
- Buttons, divider, and charts use the gradient above. Q1/Q2 charts
  in app.py are Altair, colored with the 7 brand colors.
