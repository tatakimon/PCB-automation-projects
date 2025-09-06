# ---------------------------------------------------------------------
# skidl_netlist_loader.py  –  works on KiCad 6 … 9, zero external deps
# ---------------------------------------------------------------------
import pcbnew, re, pathlib

NET = r"C:\Users\kerem\Documents\pcb projects\Sifirdan\create_schematic.net"
BOARD_FILE = "demo.kicad_pcb"
MM = pcbnew.FromMM

# -------------- 1. grab components & footprints ----------------------
with open(NET, encoding="utf-8") as f:
    txt = f.read()

comp_re = re.compile(
    r'\(comp \(ref "([^"]+)"\).*?\(footprint "([^"]+)"\)', re.S)
comps = comp_re.findall(txt)                      # list of (Ref, Footprint)

# -------------- 2. grab nets ----------------------------------------
net_re = re.compile(
    r'\(net \(code \d+\) \(name "([^"]+)"\)(.*?)\)\s*\)', re.S)
node_re = re.compile(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)\)')

nets = {}
for net_name, blob in net_re.findall(txt):
    nets[net_name] = node_re.findall(blob)        # list of (Ref, Pin)

# -------------- 3. build BOARD() ------------------------------------
board = pcbnew.BOARD()

# create NetInfo items first
net_objs = {}
for n in nets.keys():
    ni = pcbnew.NETINFO_ITEM(board, n)
    board.Add(ni)
    net_objs[n] = ni

# add footprints
for ref, fpname in comps:
    lib, fld = fpname.split(":")
    fp = pcbnew.FootprintLoad(lib, fpname)
    fp.SetReference(ref)
    board.Add(fp)

# connect pads to nets
for nname, nodes in nets.items():
    netcode = net_objs[nname].GetNet()
    for ref, pin in nodes:
        pad = board.FindFootprintByReference(ref).FindPadByNumber(pin)
        pad.SetNetCode(netcode)

board.BuildConnectivity()
pcbnew.SaveBoard(BOARD_FILE, board)
print(f"✓  {len(comps)} footprints, {len(nets)} nets → {BOARD_FILE}")
