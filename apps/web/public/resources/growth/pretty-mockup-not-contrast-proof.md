# A beautiful AI mockup is not proof of readable contrast

Do not judge text contrast from a generated screenshot alone. Antialiasing, gradients and guessed colours make visual inspection an unreliable substitute for measuring the actual foreground and background.

## A small test with real colours

Try gold #D4971B on cream #FDF7EE, white #FFFFFF on burgundy #7C1F16, and warm grey #84766A on cream #FDF7EE. Enter the actual hex pairs into the contrast calculator in the linked activity. Record the ratio and whether the pair meets the relevant threshold.

## Keep the thresholds separate

- WCAG AA ordinary text generally needs 4.5:1.
- Large text generally needs 3:1, using the standard size/weight definitions—not merely a large-looking screenshot.
- A contrast pass alone is not a complete accessibility audit: keyboard use, names, structure, focus and other requirements remain.

## Make a change and test again

Choose one failing pair. Change the actual text colour or background in an editable heading or button, then recompute the ratio. Keep the before/after values and one remaining limitation. Do not declare the entire interface accessible from this single test.

## Try the full exercise

Open Practice is an independent, non-accredited collection of practical activities. The local calculator, fictional inputs and offline materials are free. An image generator is optional and its output is not an accessibility certificate.


Try the complete exercise: https://open-practice.open-practice.workers.dev/activities/contrast-check.html?src=devto

Original source: https://open-practice.open-practice.workers.dev/demonstrations/pretty-mockup-not-contrast-proof.html
