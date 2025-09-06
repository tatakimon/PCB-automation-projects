import pcbnew, re
board = pcbnew.GetBoard()
MM = pcbnew.FromMM

# ────────── 1  Draw a 125 mm × 125 mm outline ───────────────────────────────
SIDE = 125
for d in list(board.Drawings()):
    if d.GetLayer() == pcbnew.Edge_Cuts:
        board.Remove(d)

rect = [(0,0),(SIDE,0),(SIDE,SIDE),(0,SIDE),(0,0)]
for (x1,y1),(x2,y2) in zip(rect, rect[1:]):
    s = pcbnew.PCB_SHAPE(board)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetWidth(MM(0.1))
    s.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1)))
    s.SetEnd  (pcbnew.VECTOR2I(MM(x2), MM(y2)))
    board.Add(s)

# ────────── 2  Tight grid placement inside a 5 mm margin ────────────────────
MARGIN   = 5
left, right   = MARGIN, SIDE - MARGIN
bottom, top   = MARGIN, SIDE - MARGIN
pitch_x = 8    # mm
pitch_y = 8

def family(fp):                       # crude classifier – tweak as needed
    r = fp.GetReference()
    if r.startswith("J"):         return "CONN"
    if r.startswith("U"):         return "IC"
    if r.startswith("C"):         return "CAP"
    if r.startswith("R"):         return "RES"
    if r.startswith("D_BAR"):     return "BAR"
    if r.startswith("D"):         return "LED"
    if "PWR" in r:                return "POWER"
    return "MISC"

# one logical row per family
row_for = {"BAR":0,"LED":2,"RES":4,"CAP":5,"IC":6,"POWER":7,"CONN":8,"MISC":9}
row_col = {}          # how many parts already in each row

def clamp_xy(fam, x_mm, y_mm, left, right, bottom):
    if fam == "POWER":     x_mm = left              # stick to left edge
    if fam == "CONN":      y_mm = bottom            # stick to bottom edge
    return max(left,x_mm), max(bottom,y_mm)

moved = 0
for fp in board.GetFootprints():
    fam  = family(fp)
    row  = row_for.get(fam, 9)
    col  = row_col.get(row, 0)
    row_col[row] = col + 1

    x_mm = left + col * pitch_x
    y_mm = top  - row * pitch_y
    x_mm, y_mm = clamp_xy(fam, x_mm, y_mm, left, right, bottom)

    if x_mm > right:                 # wrap if we overflow
        col = 0; row_col[row] = 1
        x_mm = left
        y_mm -= pitch_y

    fp.SetPosition(pcbnew.VECTOR2I(MM(x_mm), MM(y_mm)))
    fp.SetOrientationDegrees(0)
    moved += 1

board.BuildConnectivity()
pcbnew.Refresh()
print(f"✓ placed {moved} footprints in 125 × 125 mm, ≥5 mm from edge")
