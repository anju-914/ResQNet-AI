ResQNet AI: Dashboard Design Document
This design adapts the Aurum AI dark-and-gold look into a high-contrast coordinator dashboard for ResQNet AI: a live map, a verification queue, and an incident and route panel.
1. Scope
The Aurum design was a marketing landing page. ResQNet is a tool coordinators use under time pressure, so the brand look stays but readability, density, and status clarity come first.
Screens covered: map dashboard, verification queue, incident and route panel (the three screens in the PRD's core path). Resources and settings screens are deferred.
Aurum element
Decision
Reason
Colour palette (#0a0a0a, gold family)
Keep
Brand identity; gold is used for selection, focus, and routes
Inter + Playfair Display Italic
Keep, serif limited
Serif only for the logo and screen titles; everything readable is Inter
Glass cards
Keep, made more opaque
Text over a map needs a stronger backing than 3% white
Dot grid background
Keep on non-map screens only
It adds noise behind a map
Pill buttons, gold hover
Keep
Consistent with the brand, easy touch targets
40 to 48px corner radii
Reduce to 12 to 24px
Large radii waste space in dense lists
0.4em uppercase tracking
Reduce to small labels only
Wide tracking slows scanning
Low-opacity text (white 20 to 40%)
Replace
Fails contrast; see section 3
Hero, satellite cards, neural SVG lines, pricing, team, footer
Drop
Marketing content with no dashboard use
Bouncing pill, mouse parallax, greyscale-to-colour hover
Drop
Distracting on a live-updating screen
2. Principles
Five rules decide every design choice below.
1. Legibility beats atmosphere. Text must be readable at a glance on a bright laptop or a phone outdoors. Decoration never reduces contrast.
2. Status is never colour alone. Every state also has a shape, icon, or label, so it works for colour-blind users and in grayscale.
3. Verified and unverified must look different at a glance. Only verified SOS count as real needs (PRD FR4); unverified ones are visibly provisional.
4. One primary action per view. The verification queue's primary action is Verify; the incident panel's is Plan route. Everything else is secondary.
5. Calm when idle, clear when something changes. Nothing animates continuously except the live-connection dot. New items announce themselves once and then settle.
3. Colour
The brand palette is unchanged; text opacities are raised and a separate status palette is added. Contrast figures are estimates against #0a0a0a and should be checked with a contrast tool.
Brand and surfaces
Token
Value
Use
--bg
#0a0a0a
App background
--panel
rgba(10,10,10,0.85) + blur 12px
Panels floating over the map (stronger than Aurum's 3% glass)
--card
rgba(255,255,255,0.05)
Cards on plain background (queue, lists)
--border
white at 12%
Default border
--gold
#a78b71
Brand accent, active nav, selected item border
--gold-light
#c9b8a0
Team markers
--gold-hover
#e8d5b7
Hover on primary button, focus ring, route line
Text tiers (replaces Aurum's white 20 to 50%)
Tier
Value
Approx. contrast
Use
Primary
white 100%
about 19:1
Titles, raw SOS text, numbers
Secondary
white 70%
about 9:1
Body, field labels
Tertiary
white 60%
about 7:1
Timestamps, hints
Disabled
white 40%
about 3.7:1
Disabled controls only, never content
Status colours
Each state pairs a colour with a shape or label so colour is never the only signal.
State
Colour
Shape / label
High priority need (verified)
#ef4444
Filled circle, large; label "High"
Medium priority need (verified)
#f59e0b
Filled circle, medium; label "Medium"
Low priority need (verified)
#60a5fa
Filled circle, small; label "Low"
Unverified SOS
white 60%
Hollow dashed circle; label "Unverified"
Resolved
#22c55e
Circle with check mark
Rejected
white 40%
Hidden on the map; struck through in the queue history
Team / resource
--gold-light
Square marker with a type icon
Planned route
--gold-hover
Solid 4px line with direction arrows
Blocked road
#ef4444
Dashed line with an ✕ icon at the block
Risk zone
orange to red
Translucent polygon at 18 to 35% fill with an outline; legend shows the scale
Live connection
#22c55e / #f59e0b / grey
Dot + word: Live, Reconnecting, Offline
Priority levels are display-only. How priority is calculated is still undefined in the PRD (see section 8).
4. Type and shape
Inter carries all readable text; Playfair Display Italic is reserved for the logo and screen titles. No text is smaller than 12px and nothing uses font-thin.
Role
Size
Weight / style
Screen title
28px
Playfair Display Italic
Panel header
20px
Inter 600
Card title, raw SOS text
16px
Inter 500
Body, field values
14px
Inter 400
Labels, timestamps
12px
Inter 500; uppercase labels use 0.08em tracking, not 0.4em
Counts, ETAs, people totals
14 to 20px
Inter 600 with tabular numbers, so digits do not jump as values update
Element
Radius
Buttons, filter chips, status badges
Fully rounded
Cards, SOS items
16px
Panels (side panel, floating map panels)
24px
Inputs
12px
Glass: use the --panel recipe only for panels floating over the map, and keep to three blurred elements on screen at once. On the queue and list screens use the flat --card fill with no blur.
Dot grid: the Aurum 32px dot pattern appears on the queue and list screens only, never behind the map.
Glow: the gold glow is limited to the selected item's border (gold at 40%) and the focus ring. No large ambient shadows.
5. Screens
Three screens cover the PRD's core path: see SOS on a map, verify them, and plan a route. All values in the wireframes are example data.
5.1 Map dashboard (default)
The map fills the screen. A left rail switches screens, a right-hand feed lists the newest SOS, and filters and layer toggles float over the map. No dot grid behind the map.
┌──────────────────────────────────────────────────────────────────────────┐
│ ResQNet AI   ● Live    Pending 12  Verified 34  Teams 6         [User ▾] │
├───────┬────────────────────────────────────────────────┬─────────────────┤
│ Map   │ [Need ▾] [Priority ▾] [Status ▾]               │ LIVE FEED       │
│ Queue │                                                │ ┌─────────────┐ │
│ Incid.│                      MAP                       │ │ SOS card    │ │
│ Teams │                                                │ └─────────────┘ │
│       │   ○ unverified   ● verified   ■ team           │ ┌─────────────┐ │
│       │   ━ route   ┅ blocked road                     │ │ SOS card    │ │
│       │                                                │ └─────────────┘ │
│       │ [Layers: SOS Teams Roads Risk]        [ + / - ]│                 │
└───────┴────────────────────────────────────────────────┴─────────────────┘
5.2 Verification queue
One card per pending SOS. The raw message is shown beside what the model extracted so the coordinator can check it in seconds. Verify is the single primary button. Cards use the flat --card fill and the dot grid is allowed here.
┌────────────────────────────────────────────────────────────────────────┐
│ Verification queue · 12 pending          [Sort: Newest ▾] [Language ▾] │
├────────────────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ ○ Unverified · WhatsApp · Hinglish · 2 min ago                     │ │
│ │ "paani bhar gaya hai, 5 log chhat par, sector 5 ke paas"           │ │
│ │ Need [Rescue ▾]  People [5]  Location [Sector 5 ✎]  Conf. 0.86     │ │
│ │ Spam check: low                       [Reject] [Edit] [ Verify ▸ ] │ │
│ └────────────────────────────────────────────────────────────────────┘ │
│ (next SOS card, same layout)                                           │
└────────────────────────────────────────────────────────────────────────┘
5.3 Incident and route panel
Selecting an incident on the map opens a right-hand panel. The route appears on the map in gold; blocking a road re-routes it. Plan route is the primary button.
┌──────────────────────────────────────────────────────────────────────────┐
│ Top bar (same as map screen)                                             │
├───────┬────────────────────────────────────────┬─────────────────────────┤
│ Map   │ Selected incident ringed in gold       │ INCIDENT                │
│ Queue │ Route drawn in gold with arrows        │ Rescue · 5 people       │
│ Incid.│ ✕ Blocked road shown in red            │ Priority: High          │
│ Teams │                                        │ Linked SOS: 3           │
│       │ Click a road for:                      │ Team [Boat 2 ▾]         │
│       │ [Mark road blocked]                    │ ETA 14 min · 6 km       │
│       │                                        │ Blocked on path: 1      │
│       │                                        │ [ Plan route ▸ ]        │
│       │                                        │ [Mark resolved]         │
└───────┴────────────────────────────────────────┴─────────────────────────┘
Deferred: a separate Teams and Resources screen. For the one-day build, teams appear as map markers only.
6. Components
Each component reuses Aurum's pill buttons and gold accents with the readability changes from sections 3 and 4.
Component
Spec
App shell
56px top bar with logo (serif), live indicator, three counters (Pending, Verified, Teams), user menu. 72px left rail with icon + label for Map, Queue, Incidents, Teams. Active item has a gold left border and white text.
SOS card
--card fill, 16px radius, 16px padding. Top line: status badge, source, language, relative time (12px, tertiary). Then the raw message (16px, primary). Then extracted fields as editable chips (Need, People, Location) with a confidence value. Selected card gets a gold border at 40%.
Status badge
Pill with icon + word (Unverified, Verified, Resolved) in the status colour from section 3. 12px, weight 500.
Extracted field chip
Label (12px, tertiary) over value (14px, primary). Edit icon on hover and on keyboard focus. Low-confidence values get an amber outline plus the text "Check"; the confidence threshold is an open item.
Primary button
White fill, black text, pill, 40px minimum height, hover --gold-hover. One per view area (Verify, Plan route).
Secondary button
1px border white at 20%, white text, hover fill white at 5% (Edit, Resolve).
Destructive button
1px red border, red text, hover red at 10% (Reject, Unblock). Rejecting shows an undo toast for 6 seconds instead of a confirm dialog, to keep the queue fast.
Filter chip / dropdown
Pill, --panel fill, 12px label, count badge when a filter is active.
Map markers
As defined in section 3. Clusters show a count and expand on click; selected marker gets a gold ring.
Layer toggle
Floating --panel strip with four checkboxes: SOS, Teams, Roads, Risk. Each has a legend swatch.
Incident panel
24px radius, 360px wide on desktop, full-width bottom sheet on mobile. Sections: summary, linked SOS list, team assignment, route summary (ETA, distance, blocked roads on path), actions.
Live indicator
Dot + word in the top bar: green "Live", amber "Reconnecting", grey "Offline". The only continuously animated element (slow 3s opacity pulse on the green dot).
Toast
Bottom-left, --panel fill, 6s, used for undo, new-SOS count, and errors.
States every component set needs
State
Treatment
Loading
Skeleton cards at final size; no spinners over the map
Empty queue
Short message ("No pending SOS") with the last-checked time
Error
Inline message with a Retry button; the map stays usable
Offline
Top-bar indicator turns grey; actions that need the server are disabled with a tooltip
New SOS arrives
Card slides in once with a gold left bar that fades after 5s; the counter updates; no sound
7. Accessibility, motion, and performance
These rules fix the weaknesses found in the Aurum source (low-contrast text, no focus styles, constant animation, heavy blur).
Accessibility
• Text meets 4.5:1 contrast; use only the text tiers in section 3. Disabled controls are the only exception.
• Every status has a shape or label in addition to colour.
• Visible keyboard focus: 2px ring in --gold-hover with a 2px offset on every interactive element.
• Touch targets are at least 40px.
• New SOS arrivals are announced to screen readers through a polite live region.
• Proposed queue shortcuts: V verify, R reject, E edit, J and K to move between cards. Shortcuts are disabled while a field is being edited.
Motion
• Allowed: panel slide (200ms), card entrance (once), colour and border transitions (200 to 300ms), the live-dot pulse.
• Removed from Aurum: bouncing pill, mouse parallax, looping line pulses, 0.7s scale hovers.
• Respect prefers-reduced-motion: disable the slide, the entrance, and the pulse.
Performance
• At most three backdrop-filter elements visible at once.
• Cluster map markers; load only the markers in the current viewport.
• Animate only opacity and transform, never box-shadow or blur values.
• Tabular numbers for counters so updates do not shift the layout.
8. Build notes and open questions
Build notes (for the one-day build)
• Put the colour, radius, and text-tier tokens in one CSS variables block and map them into the Tailwind config, so a change happens in one place.
• Load Inter and Playfair Display through the framework's font loader instead of a CDN link.
• Build in this order: app shell, map with markers, SOS card and queue, incident panel and route line, then layers and polish.
• Skip for now: Teams and Resources screen, risk-zone styling (until the risk map has real inputs), keyboard shortcuts, mobile bottom sheet.
• Use plain CSS or Tailwind for everything. Do not carry over the Aurum HTML; none of its sections are reused.
Open questions
#
Question
Why it matters
1
Which free dark basemap style will MapLibre use, and what are its usage terms?
Map readability and licensing; not decided in the stack
2
How is priority (High, Medium, Low) calculated?
The PRD has no triage logic, so priority is display-only for now
3
What is the final list of need types?
The dropdown and the icons depend on it; "Rescue", "Medical", and "Food" are placeholders
4
What confidence value triggers the "Check" flag?
Depends on the extraction model's measured accuracy
5
Should Verify ask for confirmation, or rely on undo?
Speed against accidental verification; the doc assumes undo
6
Is the dashboard English only, or also Hindi?
The PRD covers SOS languages, not the coordinator interface
7
Does the dashboard need to work on phones?
Decides whether the bottom-sheet pattern is built