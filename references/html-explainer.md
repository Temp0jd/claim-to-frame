# Interactive HTML explainers

An explainer page is a guided lesson, not a dashboard. The reader should leave with a model they can use, not a tour of controls.

## Page contract

```text
Header: thesis + audience + "after this you can..."
Section 1: one concrete case (intuition)
Section 2: step-through mechanism
Section 3: one variable the reader can change
Section 4: worked example or comparison
Section 5: boundaries and failure modes
Section 6: recap + three exit questions
Footer: sources, simplifications, date
```

Order can change, but do not omit the thesis, the mechanism, the boundaries, or the sources.

## Above the fold

- Eyebrow: "Interactive explainer" and the date.
- Title: the thesis, not the topic. "Caching turns repeated work into a lookup" is stronger than "Caching".
- Thesis: one sentence in larger body text.
- Outcomes: three short statements that start with a verb: "predict", "diagnose", "choose".
- Do not put a wall of navigation above the thesis.

## Section recipes

### Intuition

Start with one concrete case. Show the input and the output. Do not start with definitions. Definitions arrive when the reader needs them.

### Mechanism

Use a stepper with 4-7 steps. Each step changes one thing in the diagram and adds one sentence. Keep the previous steps visible but muted. The reader should be able to move backward without losing context.

### One variable

Choose a variable that changes the conclusion, not a cosmetic variable. Show the value, the direction of change, and the consequence. Label the range and the units. If the data is illustrative, say so next to the control.

### Worked example

Use real numbers when you have them. Show the arithmetic or the trace. If the example is synthetic, label it and explain what would change with real data.

### Boundaries

Name at least two cases where the explanation fails: an assumption that breaks, a scale where the metaphor stops working, or a cost the model ignores. This section builds trust; do not hide it in a footnote.

### Check

Use native `<details>` elements for three questions:

1. Recall: state the idea in one sentence.
2. Transfer: predict the result when a variable changes.
3. Boundary: name a case where the explanation fails.

Put the answer inside the `<details>` element. Do not auto-grade; the goal is reflection.

## Interaction patterns

| Pattern | Use when | Implementation | Pitfall |
| --- | --- | --- | --- |
| Stepper | The mechanism has ordered steps | Buttons + one active state | All steps visible at once, so nothing changes |
| Slider | One parameter changes the outcome | Range input + live output | No units, no direction, or fake data |
| Toggle | Two states are meaningfully different | Checkbox or segmented control | Reflows the layout and destroys comparison |
| Hover/focus | A node needs a definition | CSS `:hover`, `:focus-within` | Essential information only on hover |
| Before/after | The reader must compare states | Same layout, two data sets | Different scales between states |
| Quiz | The reader should retrieve, not recognize | `<details>` or short answer | Trivia instead of transfer |
| Timeline | Events have meaningful order and duration | Horizontal scroll or step control | Decorative animation |

Every control must answer: what can the reader now predict or decide that they could not before?

## Visual system

- One accent color for the focal element. One secondary color for contrast. Neutrals for structure.
- Two typefaces at most. Use a system stack; do not load a web font unless the user accepts the dependency.
- Use a spacing scale (4, 8, 12, 16, 24, 32, 48, 64).
- Limit body text to about 65 characters per line.
- Use a clear hierarchy: one `h1`, section `h2`s, step `h3`s.
- Use whitespace and alignment before borders and shadows.
- Respect `prefers-reduced-motion`. Disable non-essential transitions.
- Support light and dark preferences, or commit to one theme with sufficient contrast.

## Technical constraints

- One self-contained `.html` file by default.
- No external scripts, stylesheets, fonts, images, or API calls. Inline SVG and data URIs are acceptable.
- Vanilla JavaScript. No build step. No framework unless the user asks for one.
- Use `file://` as the test environment. If it works there, it works almost anywhere.
- Keep the file under about 1 MB. Compress images and avoid base64 for large assets.
- Use MathML or styled HTML for equations. If you need LaTeX rendering, bundle the renderer or use a build step the user accepts.
- Do not require `localStorage` for the page to work.
- Include a print stylesheet that hides controls and shows the current state.

## Data integrity

- Never invent data. If you need a placeholder, label it "illustrative" next to the control and in the caption.
- Keep the source of every number in the footer or a tooltip.
- Use consistent units and precision. Do not show more digits than the source supports.
- Include a reset button for any state the reader can change.
- When the reader changes a parameter, show the old value or a reference point. A number without a comparison is hard to interpret.

## Accessibility

- Use semantic landmarks: `header`, `nav`, `main`, `section`, `footer`.
- Provide a skip link.
- Use real buttons and inputs, not clickable divs.
- Keep a visible `:focus-visible` outline.
- Associate every input with a `<label>`.
- Use `aria-live="polite"` for values that change without a page reload.
- Give informative images and SVGs a text alternative. Mark decorative images with `alt=""`.
- Do not autoplay audio or video.
- Ensure text and controls meet contrast requirements.
- Test keyboard-only navigation and a narrow viewport.
- Respect `prefers-reduced-motion`.

## Performance

- Inline critical CSS. Avoid large libraries.
- Use `system-ui` font stacks.
- Prefer CSS and SVG animation to JavaScript animation.
- Avoid layout thrash: batch reads and writes.
- Test with the network disabled.

## QA checklist

- [ ] The page opens offline from `file://`.
- [ ] The thesis is visible before scrolling.
- [ ] Every section supports the thesis.
- [ ] The stepper works forward and backward.
- [ ] The slider has a label, units, range, and reset.
- [ ] Illustrative data is labeled.
- [ ] Keyboard navigation works, including the stepper and slider.
- [ ] Focus is visible.
- [ ] Reduced motion disables transitions.
- [ ] The page works at 360 px width.
- [ ] There is one `h1` and a logical heading order.
- [ ] Every image has appropriate alt text.
- [ ] There are no external network requests.
- [ ] Sources and simplifications are present.
- [ ] Three exit questions are present.

## Using the template

Start with `assets/explainer-template.html`. Create a package with:

```bash
python3 scripts/scaffold.py --kind html --title "Your title" --thesis "Your one-sentence thesis" --out ./explainers/your-slug
```

Replace every `{{PLACEHOLDER}}` and every `<!-- EDIT -->` block. Then run:

```bash
python3 scripts/check_artifact.py --kind html ./explainers/your-slug/explainer.html --require-offline
```

Open the file in a browser. Test keyboard-only use, a 360 px viewport, reduced motion, and offline mode.

## When not to use HTML

- The idea is a single lookup or a short definition. Use prose.
- The reader needs a printable procedure. Use STE-lite prose.
- The interaction would only animate decoration. Use a static diagram.
- The page would need a backend, authentication, or live data. Build a small app, not an explainer, and scope it separately.
