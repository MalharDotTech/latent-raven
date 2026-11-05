Implemented the mobile updates while preserving the gold/dark look.

- `/`: smaller logo, fluid headings, stacked explainer steps and actions.
- `/play`: single-column forms, 16px inputs, large upload/consent targets, full-width submit.
- Round: full-width rating cards and lock button, clear locked state, stacked judges, wrapping quotes, large feedback segments, comfortable finish textarea.
- Leaderboard/engine room: scrollable tables with gold edge fades and swipe hints, scaling SVGs, stacked explainer.
- Shared: compact navigation, safe-area padding, `100dvh`, visible focus, reduced-motion support, contained confetti.

Verification passed: 50 TestClient checks, zero findings from [ui3_audit.py](/Users/malhar/swadharma/Code/imocha-raven/.logs/ui3_audit.py), JavaScript checks, and 225 desktop layout declarations compared unchanged.

No browser was used. Actual iPhone/Android overflow, keyboard behavior, and desktop visual appearance remain unverified.