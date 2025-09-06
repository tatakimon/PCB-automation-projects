import pcbnew, re
board = pcbnew.GetBoard()
MM = pcbnew.FromMM

# ── 1. redraw a 300 mm × 100 mm outline ────────────────────────────────────
W, H = 300, 100
for d in list(board.Drawings()):
    if d.GetLayer() == pcbnew.Edge_Cuts:
        board.Remove(d)

rect = [(0,0),(W,0),(W,H),(0,H),(0,0)]
for (x1,y1),(x2,y2) in zip(rect, rect[1:]):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetWidth(MM(0.1))
    seg.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1)))
    seg.SetEnd  (pcbnew.VECTOR2I(MM(x2), MM(y2)))
    board.Add(seg)

# ── 2. placement parameters ────────────────────────────────────────────────
margin = 5
usable_left, usable_right  = margin, W - margin
usable_bottom, usable_top  = margin, H - margin
pitch_x, pitch_y           = 8, 10   # mm

row_for = {
    "CONNECTOR": 9, "POWER": 1, "TIMER": 4,
    "LED_BAR": 0,  "LED_ST": 4, "RES": 6,
    "CAP": 7,      "MISC": 8,
}
row_slot = {}                         # <-- key = row number (int)

def family(fp):
    ref = fp.GetReference()
    if ref.startswith("J"):  return "CONNECTOR"
    if ref.startswith("U"):  return "TIMER"
    if ref.startswith("C"):  return "CAP"
    if ref.startswith("R"):  return "RES"
    if ref.startswith("D_BAR"): return "LED_BAR"
    if ref.startswith("D"):  return "LED_ST"
    if "PWR" in ref:         return "POWER"
    return "MISC"

moved = 0
for fp in board.GetFootprints():
    fam  = family(fp)
    row  = row_for[fam]
    col  = row_slot.get(row, 0)
    row_slot[row] = col + 1           # update slot counter

    # convert grid slot → real mm
    x_mm = usable_left + col * pitch_x
    y_mm = usable_top  - row * pitch_y

    if x_mm > usable_right:           # wrap long rows
        col  = 0
        row_slot[row] = 1
        x_mm = usable_left
        y_mm -= pitch_y

    # clamp inside frame
    x_mm = max(usable_left,  min(x_mm, usable_right))
    y_mm = max(usable_bottom, min(y_mm, usable_top))

    fp.SetPosition(pcbnew.VECTOR2I(MM(x_mm), MM(y_mm)))
    fp.SetOrientationDegrees(0)
    moved += 1

board.BuildConnectivity()
pcbnew.Refresh()
print(f"✓ placed {moved} footprints inside 300 × 100 mm board (5 mm margin)")
