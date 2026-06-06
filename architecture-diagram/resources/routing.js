/**
 * Routing Reference for SVG Diagrams
 *
 * Coordinate naming conventions:
 *   cxA/cyA   = center x/y of component A
 *   topA      = A's top edge y
 *   bottomA   = A's bottom edge y
 *   leftA     = A's left edge x
 *   rightA    = A's right edge x
 *   gapY      = empty y-band with no components in the route path
 *
 * Section 1: Architecture overview diagrams
 * - Horizontal service chains keep most links left-to-right.
 * - Layered boundaries should route between bands, not through boxes.
 * - Use L-shaped and U-shaped paths to avoid crossings and obstacles.
 * - Pseudo-path: M rightA cyA L gapX cyA L gapX cyB L leftB cyB
 * - Example: service A -> gateway -> service B, detour around an obstacle with
 *   M rightA bottomA L rightA gapY L obsRight+10 gapY L obsRight+10 topB-20
 *   L cxB topB-20 L cxB topB-2
 *
 * Section 2: Flowcharts
 * - Top-down process steps should stay vertically aligned when possible.
 * - Decision branches split cleanly left/right or down/out with clear labels.
 * - Keep short labels away from nodes and route around nearby boxes.
 * - Pseudo-path: M cxA bottomA L cxA gapY L cxB gapY L cxB topB-2
 * - Example: start -> decision -> next step, with the label placed near the
 *   elbow instead of on top of a node.
 *
 * Spacing constants:
 *   Arrow end offset (from component edge): 2px
 *   Arrow start (from component edge):      0px
 *   Minimum gap for through-arrow:          30px
 *   Standard sibling gap:                   30-40px
 *   Layer boundary padding:                 15-20px
 *   Label offset from arrow line:           6-8px
 *   Obstacle clearance:                    10px
 *
 * Self-check:
 *   [ ] Every x/y segment stays outside component rectangles
 *   [ ] Arrow ends 2px from the target edge
 *   [ ] Labels do not overlap nodes or boundaries
 *   [ ] Crossings are intentional only
 *   [ ] If a route passes between boxes, the gap is at least 30px
 */
