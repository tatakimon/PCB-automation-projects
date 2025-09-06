import pcbnew
bbox = board.GetBoardEdgesBoundingBox()   # KiCad 9 helper
w = pcbnew.ToMM(bbox.GetWidth())
h = pcbnew.ToMM(bbox.GetHeight())
print(f"Edge-Cuts size: {w:.2f} mm × {h:.2f} mm")