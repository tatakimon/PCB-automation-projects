import pcbnew
import wx

def layout_board_in_console():
    """
    This function runs inside the KiCad Python Console to automate PCB layout.
    It gets the currently active board and manipulates it directly.
    """
    print("--- Starting KiCad Console Layout Script ---")

    # --- Step 1: Get the Currently Active Board ---
    # This is the main difference from the headless script.
    # We get a reference to the board currently open in the editor.
    pcb = pcbnew.GetBoard()
    if not pcb:
        print("Error: No board is currently loaded.")
        return

    # Define component references
    R_REF = 'R1'
    C_REF = 'C1'
    LED_REF = 'D1'

    # --- Step 2: Define the Board Outline ---
    # We create line segments on the Edge.Cuts layer.
    print("Defining board outline on Edge.Cuts layer...")
    seg = pcbnew.DRAWSEGMENT(board)
    seg.SetLayer(pcbnew.Edge_Cuts)
    start = pcbnew.VECTOR2I(pcbnew.FromMM(10), pcbnew.FromMM(20))
    end   = pcbnew.VECTOR2I(pcbnew.FromMM(50), pcbnew.FromMM(60))

    seg.SetStart(start)
    seg.SetEnd(end)

    board.Add(seg)
    pcbnew.Refresh()


    
    # First, remove any existing outline segments to avoid duplicates
    for drawing in pcb.GetDrawings():
        if drawing.GetLayer() == pcbnew.Edge_Cuts:
            pcb.Remove(drawing)

    points = [
        pcbnew.wxPointMM(100, 100),
        pcbnew.wxPointMM(130, 100),
        pcbnew.wxPointMM(130, 125),
        pcbnew.wxPointMM(100, 125)
    ]

    for i in range(len(points)):
        start_point = points[i]
        end_point = points[(i + 1) % len(points)] # Wrap around to close the rectangle
        segment = pcbnew.PCB_SHAPE(pcb, pcbnew.SHAPE_T_SEGMENT)
        segment.SetStart(start_point)
        segment.SetEnd(end_point)
        segment.SetLayer(pcbnew.Edge_Cuts)
        segment.SetWidth(int(0.15 * 1e6)) # Width in nanometers
        pcb.Add(segment)

    # --- Step 3: Place Components ---
    print("Placing components...")
    r1 = pcb.FindModule(R_REF)
    d1 = pcb.FindModule(LED_REF)
    c1 = pcb.FindModule(C_REF)

    if r1:
        r1.SetPosition(pcbnew.wxPointMM(105, 110))
        r1.SetOrientationDegrees(90)
        print(f"Placed {R_REF}")
    else:
        print(f"Warning: Could not find {R_REF}")

    if d1:
        d1.SetPosition(pcbnew.wxPointMM(115, 110))
        d1.SetOrientationDegrees(-90)
        print(f"Placed {LED_REF}")
    else:
        print(f"Warning: Could not find {LED_REF}")

    if c1:
        c1.SetPosition(pcbnew.wxPointMM(125, 110))
        c1.SetOrientationDegrees(90)
        print(f"Placed {C_REF}")
    else:
        print(f"Warning: Could not find {C_REF}")

    # --- Step 4: Route the Tracks ---
    print("Routing tracks on F.Cu (Front Copper) layer...")
    
    if not all([r1, d1, c1]):
        print("\nError: One or more components not found. Skipping routing.")
    else:
        # Helper function to create a track
        def route_track(pad1, pad2):
            track = pcbnew.PCB_TRACK(pcb)
            track.SetStart(pad1.GetPosition())
            track.SetEnd(pad2.GetPosition())
            track.SetWidth(int(0.25 * 1e6)) # 0.25mm width in nanometers
            track.SetLayer(pcbnew.F_Cu)
            pcb.Add(track)
            # Associate track with the net from the pad
            track.SetNet(pad1.GetNet())

        # Net: GND (C1 pin 2 to D1 pin 2)
        try:
            print(f"Attempting to route GND between {C_REF} pin 2 and {LED_REF} pin 2...")
            route_track(c1.Pads()[1], d1.Pads()[1])
            print(" -> GND route successful.")
        except Exception as e:
            print(f" -> Error routing GND net: {e}")

        # Net: SIGNAL (R1 pin 2 -> D1 pin 1 -> C1 pin 1)
        try:
            print(f"Attempting to route SIGNAL from {R_REF} to {LED_REF}...")
            route_track(r1.Pads()[1], d1.Pads()[0])
            print(" -> R1-D1 route successful.")
            
            print(f"Attempting to route SIGNAL from {LED_REF} to {C_REF}...")
            route_track(d1.Pads()[0], c1.Pads()[0])
            print(" -> D1-C1 route successful.")
        except Exception as e:
            print(f" -> Error routing SIGNAL net: {e}")

    # --- Step 5: Refresh the View ---
    # This updates the editor window to show the changes.
    print("\nRefreshing PCB Editor view...")
    pcbnew.Refresh()
    print("--- Script Finished Successfully ---")

# --- Execute the function ---
layout_board_in_console()
