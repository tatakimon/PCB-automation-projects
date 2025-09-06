import pcbnew, re
board = pcbnew.GetBoard()
MM = pcbnew.FromMM

# ── quick family classifier (edit as you like) ──────────────────────────────
def fam(fp):
    r = fp.GetReference()
    if r.startswith("J"): return "CONN"
    if r.startswith("U"): return "IC"
    if r.startswith(("C","C_")): return "CAP"
    if r.startswith(("R","R_")): return "RES"
    if r.startswith("D_BAR"): return "BAR"
    if r.startswith("D"): return "LED"
    return "MISC"

order = ["CONN","IC","BAR","LED","RES","CAP","MISC"]
pitch  = 8                # mm grid both X and Y
row_y  = {f:i for i,f in enumerate(order)}  # simple : each family one row
slot   = {}               # col counter per row

# ── place tightly on origin-centred grid ────────────────────────────────────
for fp in board.GetFootprints():
    f   = fam(fp)
    row = row_y.get(f, len(order))
    col = slot.get(row, 0)
    slot[row] = col + 1

    x_mm = col * pitch
    y_mm = row * pitch
    fp.SetPosition(pcbnew.VECTOR2I(MM(x_mm), MM(y_mm)))
    fp.SetOrientationDegrees(0)

board.BuildConnectivity()

# ── compute bounding box of *all* copper (pads included) ────────────────────
xs, ys = [], []
for fp in board.GetFootprints():
    b = fp.GetBoundingBox(False, False)
    xs += [b.GetLeft(), b.GetRight()]
    ys += [b.GetTop(),  b.GetBottom()]

minx, maxx = min(xs), max(xs)
miny, maxy = min(ys), max(ys)

# ── redraw Edge.Cuts 3 mm outside that box ──────────────────────────────────
margin = MM(3)
L, R = minx - margin, maxx + margin
B, T = miny - margin, maxy + margin

# delete old outline
for d in list(board.Drawings()):
    if d.GetLayer() == pcbnew.Edge_Cuts:
        board.Remove(d)

rect = [(L,B),(R,B),(R,T),(L,T),(L,B)]
for (x1,y1),(x2,y2) in zip(rect, rect[1:]):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetWidth(MM(0.1))
    seg.SetStart(pcbnew.VECTOR2I(x1, y1))
    seg.SetEnd  (pcbnew.VECTOR2I(x2, y2))
    board.Add(seg)


board.BuildConnectivity()   # keep this line
pcbnew.Refresh()             # <─ call Refresh from the pcbnew module

print(f"✓ compacted: {pcbnew.ToMM(R-L):.1f} mm × "
      f"{pcbnew.ToMM(T-B):.1f} mm (3 mm margin)")