from skidl import *
import os
import os
print(os.listdir('C:/Users/kerem/Documents/KiCad_Libraries/'))

# Configure environment and paths
os.environ['KICAD_SYMBOL_DIR'] = 'C:/Program Files/KiCad/9.0/share/kicad/symbols'
lib_search_paths[KICAD].append('C:/Program Files/KiCad/9.0/share/kicad/symbols')

# Add your local library paths
lib_search_paths[KICAD].append('C:/Users/kerem/Documents/KiCad_Libraries/XCZU4CG-2SFVC784E')
lib_search_paths[KICAD].append('C:/Users/kerem/Documents/KiCad_Libraries')  # Add parent directory too

# Create the circuit
def create_lpddr4_fpga_netlist():
    """Create netlist for LPDDR4 memory connected to Xilinx FPGA"""
    
    # Load libraries - adjust these to match your actual library names
    # Try to load from your local library first
    try:
        fpga_lib = SchLib('XCZU4CG-2SFVC784E')  # Your local FPGA library
    except:
        print("Trying alternative library names...")
        fpga_lib = SchLib('xczu4cg')  # Alternative name
    
    # For memory, try common library names
    try:
        memory_lib = SchLib('Memory_RAM')  # KiCad standard memory library
    except:
        try:
            memory_lib = SchLib('memory')  # Alternative name
        except:
            memory_lib = SchLib('Memory')  # Another alternative
    
    device_lib = SchLib('Device')  # Standard KiCad library for passives
    
    # Create main components
    print("Creating main components...")
    
    # FPGA - Xilinx XCZU4CG-2SFVC784E
    # Try different part names that might exist in your library
    try:
        fpga = Part(fpga_lib, 'XCZU4CG-2SFVC784E', ref='U1', 
                    footprint='Package_BGA:Xilinx_SFVC784')
    except:
        try:
            fpga = Part(fpga_lib, 'XCZU4CG', ref='U1', 
                        footprint='Package_BGA:Xilinx_SFVC784')
        except:
            # If specific part not found, create a generic part with the pins we need
            print("Creating FPGA part with required pins...")
            fpga = Part('Device', 'Generic_FPGA', ref='U1')
    
    # LPDDR4 Memory - IS43LQ32256A-062BLI
    try:
        ddr4 = Part(memory_lib, 'IS43LQ32256A-062BLI', ref='U2',
                    footprint='Package_BGA:WFBGA-200_10.0x14.5mm_P0.8x0.65mm')
    except:
        try:
            ddr4 = Part(memory_lib, '43LQ32256A-062BLI', ref='U2',
                        footprint='Package_BGA:WFBGA-200_10.0x14.5mm_P0.8x0.65mm')
        except:
            # If specific part not found, create a generic LPDDR4 part
            print("Creating generic LPDDR4 part...")
            ddr4 = Part('Device', 'Generic_LPDDR4', ref='U2')
    
    # Create power supply nets
    VDD1 = Net('VDD1')      # 1.8V for LPDDR4 core
    VDD2 = Net('VDD2')      # 1.1V for LPDDR4 I/O core
    VDDQ = Net('VDDQ')      # 1.1V for LPDDR4 I/O
    VCCO_DDR = Net('VCCO_DDR_504')  # 1.2V for FPGA bank 504
    GND = Net('GND')
    
    # ZQ calibration resistor
    print("Adding ZQ calibration resistor...")
    r_zq = Part(device_lib, 'R', value='240', ref='R1',
                footprint='Resistor_SMD:R_0402_1005Metric')
    ddr4['ZQ'] += r_zq[1]
    r_zq[2] += GND
    
    # RESET pull-down resistor
    print("Adding RESET pull-down...")
    r_reset = Part(device_lib, 'R', value='1k', ref='R2',
                   footprint='Resistor_SMD:R_0402_1005Metric')
    ddr4['RESET_n'] += r_reset[1]
    r_reset[2] += GND
    
    # ODT pull-up resistors (to VDD2)
    print("Adding ODT pull-ups...")
    r_odt_a = Part(device_lib, 'R', value='10k', ref='R3',
                   footprint='Resistor_SMD:R_0402_1005Metric')
    r_odt_b = Part(device_lib, 'R', value='10k', ref='R4',
                   footprint='Resistor_SMD:R_0402_1005Metric')
    ddr4['ODT_CA_A1'] += r_odt_a[1]
    ddr4['ODT_CA_B1'] += r_odt_b[1]
    r_odt_a[2] += VDD2
    r_odt_b[2] += VDD2
    
    # CKE pull-down resistors (optional, for debug)
    print("Adding CKE pull-downs...")
    r_cke0_a = Part(device_lib, 'R', value='10k', ref='R5',
                    footprint='Resistor_SMD:R_0402_1005Metric')
    r_cke0_b = Part(device_lib, 'R', value='10k', ref='R6',
                    footprint='Resistor_SMD:R_0402_1005Metric')
    ddr4['CKE0_A'] += r_cke0_a[1]
    ddr4['CKE0_B'] += r_cke0_b[1]
    r_cke0_a[2] += GND
    r_cke0_b[2] += GND
    
    # Power supply decoupling capacitors
    print("Adding decoupling capacitors...")
    
    # Bulk capacitors for each power rail
    bulk_caps = []
    for i, (rail, value) in enumerate([
        (VDD1, '22u'), (VDD2, '22u'), (VDDQ, '22u'), (VCCO_DDR, '22u')
    ]):
        cap = Part(device_lib, 'C', value=value, ref=f'C{i+1}',
                   footprint='Capacitor_SMD:C_0805_2012Metric')
        cap[1] += rail
        cap[2] += GND
        bulk_caps.append(cap)
    
    # High-frequency decoupling for DDR4 power pins
    hf_cap_values = ['0.22u', '0.1u', '0.01u']
    hf_caps = []
    cap_ref = 5  # Starting reference after bulk caps
    
    for rail in [VDD1, VDD2, VDDQ]:
        for value in hf_cap_values * 4:  # 12 caps per rail
            cap = Part(device_lib, 'C', value=value, ref=f'C{cap_ref}',
                       footprint='Capacitor_SMD:C_0201_0603Metric')
            cap[1] += rail
            cap[2] += GND
            hf_caps.append(cap)
            cap_ref += 1
    
    # FPGA DDR bank decoupling
    for i in range(12):
        cap = Part(device_lib, 'C', value='0.1u', ref=f'C{cap_ref}',
                   footprint='Capacitor_SMD:C_0201_0603Metric')
        cap[1] += VCCO_DDR
        cap[2] += GND
        cap_ref += 1
    
    # Connect data signals - Channel A
    print("Connecting Channel A data signals...")
    for i in range(16):
        # Data bits
        fpga[f'PS_DDR4_DQ{i}_504'] += ddr4[f'DQ{i}_A']
    
    # Data mask signals - Channel A
    fpga['PS_DDR4_DM0_504'] += ddr4['DM0_A']
    fpga['PS_DDR4_DM1_504'] += ddr4['DM1_A']
    
    # Data strobe signals - Channel A (differential)
    fpga['PS_DDR4_DQS0_P_504'] += ddr4['DQS0_t_A']
    fpga['PS_DDR4_DQS0_N_504'] += ddr4['DQS0_c_A']
    fpga['PS_DDR4_DQS1_P_504'] += ddr4['DQS1_t_A']
    fpga['PS_DDR4_DQS1_N_504'] += ddr4['DQS1_c_A']
    
    # Connect data signals - Channel B
    print("Connecting Channel B data signals...")
    for i in range(16):
        # Data bits (offset by 16 for channel B)
        fpga[f'PS_DDR4_DQ{i+16}_504'] += ddr4[f'DQ{i}_B']
    
    # Data mask signals - Channel B
    fpga['PS_DDR4_DM2_504'] += ddr4['DM0_B']
    fpga['PS_DDR4_DM3_504'] += ddr4['DM1_B']
    
    # Data strobe signals - Channel B (differential)
    fpga['PS_DDR4_DQS2_P_504'] += ddr4['DQS0_t_B']
    fpga['PS_DDR4_DQS2_N_504'] += ddr4['DQS0_c_B']
    fpga['PS_DDR4_DQS3_P_504'] += ddr4['DQS1_t_B']
    fpga['PS_DDR4_DQS3_N_504'] += ddr4['DQS1_c_B']
    
    # Connect command/address signals
    print("Connecting command/address signals...")
    for i in range(6):
        # Channel A CA signals
        fpga[f'PS_DDR4_A{i}_504'] += ddr4[f'CA{i}_A']
        # Channel B CA signals (using upper address bits)
        fpga[f'PS_DDR4_A{i+6}_504'] += ddr4[f'CA{i}_B']
    
    # Connect clock signals (differential)
    print("Connecting clock signals...")
    fpga['PS_DDR4_CK0_P_504'] += ddr4['CK_t_A']
    fpga['PS_DDR4_CK0_N_504'] += ddr4['CK_c_A']
    fpga['PS_DDR4_CK1_P_504'] += ddr4['CK_t_B']
    fpga['PS_DDR4_CK1_N_504'] += ddr4['CK_c_B']
    
    # Connect control signals
    print("Connecting control signals...")
    fpga['PS_DDR4_CS0_504'] += ddr4['CS_A']
    fpga['PS_DDR4_CS1_504'] += ddr4['CS_B']
    fpga['PS_DDR4_CKE0_504'] += ddr4['CKE0_A']
    fpga['PS_DDR4_CKE1_504'] += ddr4['CKE0_B']
    fpga['PS_DDR4_ODT0_504'] += ddr4['ODT_CA_A1']
    fpga['PS_DDR4_ODT1_504'] += ddr4['ODT_CA_B1']
    fpga['PS_DDR4_RESET_504'] += ddr4['RESET_n']
    
    # Connect power pins
    print("Connecting power supplies...")
    
    # LPDDR4 power connections
    ddr4['VDD1'] += VDD1
    ddr4['VDD2'] += VDD2
    ddr4['VDDQ'] += VDDQ
    ddr4['VSS'] += GND
    ddr4['VSSQ'] += GND
    
    # FPGA DDR bank power
    fpga['VCCO_DDR_504'] += VCCO_DDR
    fpga['GND'] += GND
    
    # Additional FPGA configuration pins for DDR4
    print("Connecting FPGA DDR configuration pins...")
    
    # Alert signal (optional, for parity/CRC errors)
    fpga['PS_DDR4_ALERT_504'] += Net('DDR4_ALERT')
    
    # Reference voltage (typically VDDQ/2 = 0.55V for LPDDR4)
    vref = Net('VREF_DDR')
    fpga['VREF_504'] += vref
    
    # Create voltage divider for VREF (optional, often internal)
    r_vref1 = Part(device_lib, 'R', value='1k', ref='R7',
                   footprint='Resistor_SMD:R_0402_1005Metric')
    r_vref2 = Part(device_lib, 'R', value='1k', ref='R8',
                   footprint='Resistor_SMD:R_0402_1005Metric')
    VDDQ += r_vref1[1]
    r_vref1[2] += vref, r_vref2[1]
    r_vref2[2] += GND
    
    # Add test points for debugging
    print("Adding test points...")
    test_nets = [
        ('TP_VDD1', VDD1), ('TP_VDD2', VDD2), ('TP_VDDQ', VDDQ),
        ('TP_VCCO', VCCO_DDR), ('TP_VREF', vref), ('TP_GND', GND)
    ]
    
    for i, (name, net) in enumerate(test_nets):
        tp = Part(device_lib, 'TestPoint', ref=f'TP{i+1}',
                  footprint='TestPoint:TestPoint_Pad_D1.0mm')
        tp[1] += net
    
    print("Netlist generation complete!")
    
    # Generate the netlist
    return generate_netlist()

# Main execution
if __name__ == "__main__":
    print("SKiDL LPDDR4-FPGA Netlist Generator")
    print("====================================")
    #print(f"SKiDL version: {skidl_version}")
    print(f"Library search paths: {lib_search_paths[KICAD]}")
    
    # Create the netlist
    create_lpddr4_fpga_netlist()
    
    # Generate netlist in KiCad format
    print("\nGenerating KiCad netlist file...")
    generate_netlist(file_='lpddr4_fpga.net')
    print("Netlist saved as: lpddr4_fpga.net")
    generate_svg(file_='lpddr4_fpga.svg')
    print("Netlist saved as: lpddr4_fpga.svg")

    
    # Optional: Generate other formats
    # generate_xml(file_='lpddr4_fpga.xml')  # XML format
    # generate_graph(file_='lpddr4_fpga.svg')  # Visual representation