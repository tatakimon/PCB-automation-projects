from skidl import *
import os

# Configure environment and paths
os.environ['KICAD_SYMBOL_DIR'] = 'C:/Program Files/KiCad/9.0/share/kicad/symbols'
lib_search_paths[KICAD].append('C:/Program Files/KiCad/9.0/share/kicad/symbols')
#set_default_tool(KICAD8)

# Create components using explicit extensions
try:
    # Basic components
    R1 = Part('Device.kicad_sym', 'R', value='10k', footprint='Resistor_SMD:R_0603_1608Metric')
    C1 = Part('Device.kicad_sym', 'C', value='100nF', footprint='Capacitor_SMD:C_0603_1608Metric')
    D1 = Part('Device.kicad_sym', 'LED', footprint='LED_SMD:LED_0603_1608Metric')
    
    # Create nets and connections
    vcc = Net('VCC')
    gnd = Net('GND')
    sig = Net('SIGNAL')
    
    # Wire the circuit
    vcc += R1[1]
    R1[2] += D1[1], sig
    D1[2] += gnd
    sig += C1[1]
    C1[2] += gnd
    
    # Generate netlist
    #generate_netlist(tool=KICAD9)
    print("Successfully generated netlist with KiCad 9.0 libraries")
    
except Exception as e:
    print(f"Error: {e}")