#!/usr/bin/env python3
#
# skidl_hierarchical_design.py
#
from skidl import *
import os

# -----------------------------------------------------------------------------
# 1) Configure KiCad symbol library paths
# -----------------------------------------------------------------------------
os.environ["KICAD_SYMBOL_DIR"] = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"
lib_search_paths[KICAD].append(
    r"C:\Program Files\KiCad\9.0\share\kicad\symbols"
)
set_default_tool(KICAD)

# -----------------------------------------------------------------------------
# 2) Sub-sheet: Basic analog front-end (R1, C1, LED D1)
# -----------------------------------------------------------------------------
@subcircuit
def analog_frontend():
    # Parts
    R1 = Part("Device", "R", value="10k", footprint="Resistor_SMD:R_0603_1608Metric")
    C1 = Part("Device", "C", value="100nF", footprint="Capacitor_SMD:C_0603_1608Metric")
    D1 = Part("Device", "LED", footprint="LED_SMD:LED_0603_1608Metric")

    # Nets
    vcc = Net("VCC")
    gnd = Net("GND")
    sig = Net("SIGNAL")

    # Connections
    vcc += R1[1]
    R1[2] += D1[1], sig
    D1[2] += gnd
    sig += C1[1]
    C1[2] += gnd

    # Return nets for top-level wiring
    return vcc, gnd, sig

# -----------------------------------------------------------------------------
# 3) Sub-sheet: RAM chip IS43LQ32256A-062BLI
# -----------------------------------------------------------------------------
@subcircuit
def ram_chip():
    # Instantiating the SDRAM device
    ram = Part(
        "Memory_IS43",
        "IS43LQ32256A-062BLI",
        footprint="Memory:TSOP-II-48_14.4x11.8mm_P0.65mm"
    )

    # Create buses and nets
    addr = Bus("A", 19)     # A[0..18]
    data = Bus("DQ", 16)    # DQ[0..15]
    ce_n = Net("CE_N")
    oe_n = Net("OE_N")
    we_n = Net("WE_N")

    # Wire nets to pins (pin names may vary—adjust per your symbol)
    ram["A0":"A18"] += addr
    ram["DQ0":"DQ15"] += data
    ram.CE_N  += ce_n
    ram.OE_N  += oe_n
    ram.WE_N  += we_n

    return addr, data, ce_n, oe_n, we_n

# -----------------------------------------------------------------------------
# 4) Sub-sheet: FPGA device XCZU4CG-2SFVC784E
# -----------------------------------------------------------------------------
@subcircuit
def fpga_device():
    # Instantiating the Zynq UltraScale+ device
    fpga = Part(
        "Xilinx", 
        "xczu4cg-2sfvc784e",
        footprint="BGA:ZYNQ_Ultrascale+-23x23mm_UBGA-784"
    )

    # Example nets/buses
    reset_n = Net("RESET_N")
    clk_p   = Net("CLK_P")
    clk_n   = Net("CLK_N")
    io_bus   = Bus("IO", 32)

    # Wire a few pins (pin names are examples—update to match your symbol)
    fpga.RESET_N  += reset_n
    fpga.CLK_P    += clk_p
    fpga.CLK_N    += clk_n
    fpga["IO0":"IO31"] += io_bus

    return reset_n, clk_p, clk_n, io_bus

# -----------------------------------------------------------------------------
# 5) Main sheet: Instantiate subsheets & generate netlist
# -----------------------------------------------------------------------------
def main():
    # a) Analog frontend
    vcc, gnd, sig = analog_frontend()

    # b) SDRAM chip
    addr, data, ce_n, oe_n, we_n = ram_chip()

    # c) FPGA device
    reset_n, clk_p, clk_n, io_bus = fpga_device()

    # d) Top-level wiring examples
    # Tie power rails
    VCC  = Net("VCC")  # New net object merges with analog vcc
    GND  = Net("GND")  # Merges with analog gnd

    # Connect FPGA IO bus lines D[0..15] to SDRAM DQ bus
    io_bus[0:16] += data

    # Drive control signals from FPGA to SDRAM
    ce_n += Net("FPGA_DDR_CE_N")
    oe_n += Net("FPGA_DDR_OE_N")
    we_n += Net("FPGA_DDR_WE_N")

    # Example clock to FPGA
    clk_p += Net("SYS_CLK_P")
    clk_n += Net("SYS_CLK_N")

    # e) Generate the KiCad netlist
    generate_netlist()
    print("✅ Netlist generated successfully!")

if __name__ == "__main__":
    main()