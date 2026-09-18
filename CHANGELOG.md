# Changelog

Written back from the GitHub release notes. There are 50 tags, so patch releases are folded
into their minor version and marked inline (`0.35.1:`).

## 0.38 — 2026-09-18

- Nine new Neon Sign families, 36 themes. v6–v13 keep the four tube bubbles from v4/v5 but drop the wall: constellations, drifting petals, bokeh, plasma threads, spreading ink, a laser mesh, crystal facets, chromatic aberration.
- **Neon Zoo** — the four sets differ by which neon animal hangs on the wall (sea, forest, ice, mixed). The same animals show up as the default profile pictures in the chat list.
- **Custom themes** — pick a background from one theme and bubbles from another and mix them, in the browser ([make page](https://ruminem.github.io/kakaotalk-theme/docs/make.html)) or on a PC with `tools/mix.py`. 168 backgrounds to choose from.
- Neon Sign families moved from `docs/themes/lights.md` to `docs/themes/lights-neon.md`. Bookmarked links to the old page no longer resolve.
- Apache-2.0 license added. Until now the repo had no license, which legally meant all rights reserved.
- All 256 existing themes are unchanged image-for-image; only the version number moved, so they update in place.

## 0.37 — 2026-09-16

- New family: **Neon Sign v5** — neon hung on a dark plaster wall, swept by two warm uplights. Same four bubbles as v4.
- Neon Sign v4's plank wall redrawn with growth-ring grain and a warm bar light. The old straight-line grain read as a barcode.

## 0.36 — 2026-09-16

- Five new Lights families derived from Red: **Blue, Purple, Green, Gold, Pink**. Same black ground, bright bubbles and rising embers, in a new color. Four variants each.
- Three new Neon Sign families: **v2** (shuttered alley), **v3** (tiled basement bar), **v4** (wooden plank wall with four newly drawn bubbles — octagon, bracket, underline, twin tube). Only lit tubes glow, and they glow in their own color.

## 0.35 — 2026-09-15

- Six new Glass families where the material shows on the bubble surface, not just the border: **Sea Glass, Glass Block, Ice, Reeded Glass, Acrylic, Resin**. Four variants each (light / light+background / dark / dark+background).
- Glass chat lists keep their background unblurred behind translucent cells, so the family is visible in the list too.
- Family icons in the README and category pages now jump to the family instead of opening the raw PNG.
- `0.35.1` (2026-09-16): fixed the seams across the top of the iOS chat list. iOS draws the status bar, title and filter chips as separate bands and restarts the background image in each one, so nearly all 110 themes with a list background showed steps at the band edges. The top of every list background is now filled with a per-column average that fades into the artwork below. Acrylic also got a dedicated list background.

## 0.34 — 2026-09-15

- Five new Pattern families on repeating backdrops, with a solid bubble and one prop on the first message: **Gingham, Polka Dot, Terrazzo, Marine Stripe, Checkerboard**. Four variants each.
- Each family gets its own default profile pictures, tiled faintly with the family pattern so the chat list tells them apart.

## 0.33 — 2026-09-15

- Four new Comfort families, built for long reading rather than punch: **Watercolor, Ink Wash, Rainy Window, Papercut**. Four variants each.
- Comfort themes are now checked by number — saturation at or below 0.25, bubble-to-floor contrast between 1.2 and 2.0, text contrast at least 4.5, no pure white or black. A theme that misses the mark fails the build.

## 0.32 — 2026-09-15

- Four new Pixel families in real 8-bit: **Pixel Quest** (RPG dialogue box), **Pixel LCD** (four-tone green screen), **Retro PC** (old desktop windows), **Pixel Farm** (nailed wooden signs). One dot is 4pt, so it stays chunky on a phone; tab icons are pixel art too.
- Two new categories. **Comfort** takes Calm and Hush out of Pattern; **Pixel** takes Arcade out of Character. The themes themselves are unchanged, but their category pages moved — Calm and Hush to `docs/themes/comfort.md`, Arcade to `docs/themes/pixel.md`.

## 0.31 — 2026-09-14

- New family: **Neon Sign**. Glass tubes on a dark brick wall, the center of the tube burning white. The four variants are four bubble designs (twin tube, signboard, electrode, tail).
- Glow shapes are now picked by name from a shared dictionary instead of hand-tuned per theme. Existing themes verified unchanged by hash.
- The README outgrew a phone screen at 1,600 lines, so family details moved into one page per category under `docs/themes/`. The README keeps the thumbnail grids.
- `0.31.1`: redrew the glow on Terminal's two glow variants. The white-tinted edge band read as a gray border on a black-and-green screen, not as light.
- `0.31.2`: Neon Sign's chat list is now neon too — neon profile pictures, neon tab icons that light up only when selected, and the brick wall showing through translucent cells.
- `0.31.3`: that rule extended to every family. 21 families without a character got three motif profile pictures, glow variants got neon tab icons, and any theme with a list background got translucent cells (0.72). Bubbles, chat rooms and lock screens unchanged.

## 0.30 — 2026-09-14

- Ten new families, forty themes. 100 themes to 140.
- Lights: **Fireworks, Lanterns, String Lights, Highway, Terminal**.
- Character: **Cinema, Bakery, Camping, Space, Greenhouse** — shaped bubbles with a prop on the first message and a character profile picture.
- Camping's sign glows with firelight; in dark+background the corner nearest the fire catches it.

## 0.29 — 2026-09-12

- New **Character** category, five families, all bubbles and characters newly drawn: **Post Office** (envelope), **Desk** (sticky note), **Arcade** (pixel steps), **Laundry** and **Laundry Shine** (jelly).
- Props (stamp, tape, tail, droplet) sit only on the first bubble of a run, and only where the bubble does not stretch, so they hold their shape on long messages.
- These families use light / light+background / dark / dark+background instead of the usual glow axis.
- `0.29.1`: Stained Glass backgrounds redrawn with real backlight — pieces in front of the source heat up and keep their color instead of just being dimmed further away.
- `0.29.2`: jelly gloss on the Laundry families rebuilt as stacked layers (reflection, hotspot, pooled light, edge thickness, tinted shadow) instead of white pills on a band.
- `0.29.3`: **Laundry Shine merged into Laundry** — two families that differed only in gloss were not worth separating. The new Laundry is the old Laundry Shine. If you had Laundry Shine installed it will not update; delete it and install Laundry. Top-edge gloss redrawn so light always falls from the upper left, on both sent and received bubbles.

## 0.28

Withdrawn. The two families it added were drawn too close to a reference screenshot, so the whole release was deleted rather than patched.

## 0.27 — 2026-09-12

- New family: **Hush** (olive, mist, plum, sumi). Same numeric standard as Calm, but each color has a name rather than being near-neutral.
- `0.27.1`: Stained Glass backgrounds redrawn as leaded glass pieces instead of blurred color; Rosewood Glass grain redrawn with arching figure and knots the grain flows around. Previews now render at 3× like the phone.

## 0.26 — 2026-09-12

- New family: **Calm** (sage, sand, slate, mocha) — the first set built for tired eyes. Saturation 0.09–0.28, text contrast 7.8–13.1, no pure white or black, no glow and no background image. Its four variants are four colors instead of the usual axis.

## 0.25 — 2026-09-12

- Three new Glass families: **Stained Glass** (four colors as the four variants), **Prism Glass** (cyan top edge, magenta bottom), **Frosted Glass**.
- New **Glass** category — half of Pattern had become glass.
- Includes the 0.24.1 glow border fix.

## 0.24 — 2026-09-12

- New family: **Rosewood Glass** — glass bubbles over wood grain, oak and walnut × background and solid. Glass only reads as glass when there is something behind it, and grain gives it lines to cross.
- The list background keeps the straight grain unblurred; knots and plank seams are left out of that copy so nothing shows a cut edge.
- `0.24.1`: glow borders were going gray. Brightening in RGB drains saturation from dark colors — Red's received bubble fell from 0.81 to 0.09, so a red theme had a gray glow. Now hue is kept and only lightness rises. All 32 glow themes changed; the other 32 files are untouched.

## 0.23 — 2026-09-12

- Every slot in the spec is now filled. Nine attributes and one block were still unused, so those spots kept KakaoTalk's stock artwork under a themed app.
- Newly themed: the add-friend button, the eight lock-screen dots (a different color per position), the keypad press state, and the Android tab bar background.
- iOS tab bar background stays a flat color — the guide has no attribute for an image there, and invented names are silently ignored.

## 0.22 — 2026-09-12

- Two new families: **Cyberpunk** (neon grid horizon and a sliced sun) and **Red** (embers rising over a dark crimson ground). Four variants each.

## 0.21 — 2026-09-12

- **Liquid Glass Solid** and **Liquid Glass Dark Solid** — the glass without a background image.
- Light glass was invisible on a white ground; the edge now has a bright line above and a dark line below, the way light actually bends through glass.
- Midnight `background` and Candy Pop `candy background` lost their glow. They were labeled as background-only but carried a glow, making them duplicates of their own glow+background sibling. **Those two screens change on update**; the old look is the glow+background variant.
- Background art in the same family used to come out identical down to each star. Each theme now seeds its own image.
- Preview images use the same names as the released files.

## 0.20 — 2026-09-12

- **Default profile pictures follow the theme.** Three per theme, the only slot in the spec that takes multiple images, so the chat list shows a mix.
- Previews now draw the real theme artwork instead of their own stand-ins.
- `0.20.1`: the light laid over backgrounds was rebuilt. Lighting all four edges equally looked like a picture frame, not light; the source now sits off the upper-left corner with the opposite corner pressed down.
- `0.20.2`: chat-list backgrounds are blurred into a texture. KakaoTalk stacks opaque things on that list (filter chips, ad cards, cells) and any picture underneath was cut into rectangles at their edges. Chat room and lock screen keep the full image. README thumbnail links now point at the real anchor ids so they work in mobile browsers.

## 0.19 — 2026-09-12

- **Every family is now a set of four** — basic, background, glow, glow+background. 21 themes to 50.
- Ink Mint, Cream Latte and Mixed had no background art at all; each got one drawn from its own palette.
- Variants always appear in the same order, so families can be compared side by side.

## 0.18 — 2026-09-12

- **Tab icons follow the theme.** Seven icons × normal and selected, 14 images per theme. Drawn as filled shapes because lines mush at 28pt. All 21 themes changed.

## 0.17 — 2026-09-12

- **File names say what they are** — `city21.ktheme` became `city-glow-image.ktheme`. Package names and iOS theme IDs changed with them.
- **Installed themes must be deleted and reinstalled.** The theme ID changed, so the new file installs alongside the old one instead of updating it. Done now, while few people had installed anything; names will not change again.

## 0.16 — 2026-09-12

- **Night View became four themes** — basic, background, glow, glow+background. Every family added from here on ships as a set of four, and the variant label shows in the phone's theme list.
- An existing Night View updates in place and is renamed to `Night View Background`.

## 0.15 — 2026-09-12

- Five new themes: **Sea, Forest, Night View, Snowfield, Shapes**, each with its own drawn background.
- The rules for new themes are now enforced in code — no glow, no gradient bubbles, four distinct bubble colors, background art on all three screens. Breaking one stops the build. Themes made before the rule are left alone.

## 0.14 — 2026-09-12

- Two new themes: **Candy Pop v3** (scattered candy background) and **Cherry Blossom Shade v2** (branches and petals).
- Blurred shapes were being clipped to a rectangle by their own canvas. Blur radius is now allowed for as margin.

## 0.13 — 2026-09-12

- **Midnight's background is a real drawing** — stars with a Milky Way band, a crescent with a halo, three ridge layers, atmospheric light at the horizon. Seeded, so the sky does not change between builds.
- Glow rebuilt as a thin band plus a wide band, brighter at the top, with a gamma curve on the outer bleed.
- `0.13.1`: the rectangle around each bubble is gone. The outer bleed's tail stayed at alpha ~17 all the way to the edge of the margin, so the whole rectangle floated faintly. Per-theme icons added, including the one KakaoTalk shows in its theme list. Quality work now goes out as a patch number.
- `0.13.2`: theme icons redrawn to look like app icons (vignette, shadow, top gloss). Pressed states across list names, status messages, last messages and bubble text now shift toward the accent color — KakaoTalk animates between the two states, but most of them had been identical, so nothing happened.

## 0.12 — 2026-09-12

- New theme: **Midnight**, the first to put background art on all three screens, drawn differently for each.
- Lock screen background images are now supported (visible only if you have a KakaoTalk passcode set), and the preview gained a lock screen.
- Full spec written up in `docs/spec.md`.

## 0.11 — 2026-09-12

- Glow rebuilt after seeing it on a phone. The blur was being cut off at the image edge, leaving a visible rectangle; it was a single blur, so the falloff read as a band; and the inner glow was a fixed-width ring. Now three stacked blurs windowed to zero at the edge, and an inner band derived by subtracting a blurred mask.

## 0.10 — 2026-09-12

- Glow moved inside the bubble body. Shrinking the outer margin in 0.8 had made the halo too thin to see, and widening it again would push the bubbles apart. The inner edge costs no frame space.

## 0.9 — 2026-09-12

- Variants (v2) now sit right after their original in every list.
- **Android `versionCode` no longer follows list order.** Reordering would have lowered Mixed v2's code from 9 to 5, and Android refuses that as a downgrade. It is now derived from the theme key and version.

## 0.8 — 2026-09-12

- **Bubbles sit closer together.** The bubble frame height *is* the gap between bubbles, so 12pt of glow margin showed up as empty space. Margin halved and the glow made denser to compensate.
- The preview now lays bubbles out the way KakaoTalk does — frame is text plus insets, artwork fills the whole frame — instead of drawing whatever looks good.

## 0.7 — 2026-09-12

- **Glow was invisible on the phone.** The glow margin eats into the bubble frame, which pushed the text against the body, and the glow itself was spread too thin. Insets now grow with the margin, and the glow is denser near the body.

## 0.6 — 2026-09-12

- Two new themes: **Mixed v2** and **Candy Pop v2**, the originals with glow.
- Glow color follows each bubble, so all four bubble slots glow in their own color.

## 0.5 — 2026-09-12

- **Glow** added, on both glass themes — around the bubble and along the screen edge. Cap insets grow with the glow margin so the light does not smear when a bubble stretches.
- Mixed and Candy Pop bubbles are now solid color. Two-stop gradients looked messy in a theme that already has four bubble colors.

## 0.4 — 2026-09-12

- Two new themes: **Liquid Glass** and **Liquid Glass Dark**. Translucent cells and bubbles let the background show through — all within the spec, nothing faked.
- Bubble drawing merged into one place so the preview and the shipped theme cannot drift apart.

## 0.3 — 2026-09-12

- Five new themes: **Cream Latte, Cherry Blossom Shade, Mixed, Aurora, Candy Pop**, joining Ink Mint. Six in total.
- Everything now generates from one palette table (`tools/themes.py`) — CSS, `colors.xml`, artwork, previews.
- Preview tool added: run `preview.ps1` and get every theme's screens on one page instead of installing them one by one.
- Android splash screens are drawn per theme. iOS has no splash block in the spec.

## 0.2 — 2026-09-12

- **Bubbles got artwork** — a vertical gradient, mint to sky for sent, violet to magenta for received. Vertical so it does not smear when a bubble stretches sideways.
- iOS received-bubble text flipped to white; dark text on violet was unreadable.
- Android splash screen added.

## 0.1 — 2026-09-12

- First release. **Ink Mint**, iOS and Android, colors only — not a single image, to see how far color alone gets.
- iOS bubble colors cannot be changed by color at all; `MessageCellStyle` has no `background-color`, only PNGs. Android bubbles do take a color, so the same v0 changes more there.
- Android APKs are built without gradle: `aapt2` → `zipalign` → `apksigner`. The theme requests no permissions.
