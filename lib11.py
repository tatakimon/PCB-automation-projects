#!/usr/bin/env python3
"""
File: leds_timer_bargraph.py
Standalone LED Bargraph & NE555 Timer–LED Circuit Examples
"""

import os
from skidl import *

# -----------------------------------------------------------------------------
# 1) Configure KiCad symbol library paths and default tool
# -----------------------------------------------------------------------------
def setup_kicad():
    """Setup KiCad environment for SKiDL."""
    os.environ["KICAD_SYMBOL_DIR"] = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"
    lib_search_paths[KICAD].append(r"C:\Program Files\KiCad\9.0\share\kicad\symbols")
    set_default_tool(KICAD)
    print("✓ KiCad environment configured")


# -----------------------------------------------------------------------------
# 2) LED bargraph display sub-circuit
# -----------------------------------------------------------------------------
def create_led_bargraph():
    """Create a 2×6 odd/even pin header driving six LEDs (bargraph)."""
    print("Creating LED bargraph display...")
    # Connector (2×6 odd/even)
    conn = Part(
        "Connector_Generic",             # Library filename (no .kicad_sym)
        "Conn_02x06_Odd_Even",           # Symbol name
        ref="J_CONTROL",
        footprint="Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical",
    )

    # Common nets
    gnd = Net("GND")

    # Instantiate LEDs + series resistors, wire to connector
    for i in range(6):
        led = Part(
            "Device", 
            "LED", 
            ref=f"D{i+1}", 
            footprint="LED_SMD:LED_0603_1608Metric"
        )
        r = Part(
            "Device", 
            "R", 
            ref=f"R{i+1}", 
            value="330", 
            footprint="Resistor_SMD:R_0603_1608Metric"
        )

        # Map odd connector pins 1,3,5,... to LED anodes
        pin_num = str(2 * i + 1)
        conn[pin_num] += led[1]

        # LED cathode → resistor → GND
        led[2] += r[1]
        r[2]   += gnd


# -----------------------------------------------------------------------------
# 3) NE555 timer driving a single LED
# -----------------------------------------------------------------------------
def create_timer_led_circuit():
    """Create a 555 timer astable circuit that flashes an LED."""
    print("Creating NE555 timer → LED circuit...")
    # Timer IC
    timer = Part("Timer", "NE555", ref="U1")

    # Timing network
    r_t = Part(
        "Device", 
        "R", 
        ref="R10", 
        value="10k", 
        footprint="Resistor_SMD:R_0603_1608Metric"
    )
    c_t = Part(
        "Device", 
        "C", 
        ref="C10", 
        value="100nF", 
        footprint="Capacitor_SMD:C_0603_1608Metric"
    )

    # Output LED + series resistor
    led = Part(
        "Device", 
        "LED", 
        ref="D10", 
        footprint="LED_SMD:LED_0603_1608Metric"
    )
    r_l = Part(
        "Device", 
        "R", 
        ref="R11", 
        value="330", 
        footprint="Resistor_SMD:R_0603_1608Metric"
    )

    # Nets
    vcc = Net("VCC")
    gnd = Net("GND")
    out = timer["OUT"]

    # Power rails
    vcc += timer["VCC"]
    gnd += timer["GND"]

    # Astable RC network between discharge, threshold, trigger
    # 555 Discharge (pin 7) is open-collector, so tie via resistor & cap
    vcc  += r_t[1]
    r_t[2] += c_t[1]
    c_t[2] += gnd

    # Output drives LED
    out   += led[1]
    led[2] += r_l[1]
    r_l[2] += gnd


# -----------------------------------------------------------------------------
# 4) Main: Build circuit & generate netlist
# -----------------------------------------------------------------------------
def main():
    setup_kicad()
    create_led_bargraph()
    create_timer_led_circuit()
    generate_netlist()
    print("✅ Netlist generated successfully!")

if __name__ == "__main__":
    main()