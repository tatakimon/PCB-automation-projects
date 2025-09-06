#!/usr/bin/env python3
"""
File: leds.py
Standalone LED Circuit Examples  
Single LEDs, arrays, different colors, indicators
"""

import os
from skidl import *


def setup_kicad():
    """Setup KiCad environment for LED circuits"""
    os.environ['KICAD_SYMBOL_DIR'] = 'C:/Program Files/KiCad/9.0/share/kicad/symbols'
    lib_search_paths[KICAD].append('C:/Program Files/KiCad/9.0/share/kicad/symbols')
    set_default_tool(KICAD8)
    print("✓ KiCad environment configured")
    from skidl import SchLib

    #lib = SchLib('Connector_Generic.kicad_sym')
    

def create_single_led_circuit():
    """
    Create basic single LED circuit
    Power -> Resistor -> LED -> Ground
    """
    
    print("Creating single LED circuit...")
    
    # Power nets
    vcc = Net('VCC')
    gnd = Net('GND')
    
    # Input power connector
    power_conn = Part('Connector.kicad_sym', 'Conn_01x02_Pin',
                     ref='J1',
                     footprint='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
    
    power_conn[1] += vcc  # +3.3V input
    power_conn[2] += gnd  # Ground
    
    # Current limiting resistor
    led_resistor = Part('Device.kicad_sym', 'R',
                       ref='R1',
                       value='330',
                       footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
    
    # LED
    led = Part('Device.kicad_sym', 'LED',
              ref='D1',
              value='Red',
              footprint='LED_THT:LED_D5.0mm')
    
    # Circuit connections: VCC -> Resistor -> LED -> Ground
    vcc += led_resistor[1]
    led_resistor[2] += led[1]  # LED Anode
    led[2] += gnd              # LED Cathode
    
    print("✓ Single red LED circuit created")

def create_multi_color_leds():
    """
    Create multiple color LED circuits
    Red, Green, Blue, Yellow LEDs with individual resistors
    """
    
    print("Creating multi-color LED circuits...")
    
    # Power nets
    vcc = Net('VCC')
    gnd = Net('GND')
    
    # Input power
    power_conn = Part('Connector.kicad_sym', 'Conn_01x02_Pin',
                     ref='J_POWER',
                     footprint='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
    
    power_conn[1] += vcc
    power_conn[2] += gnd
    
    # LED configurations: (color, resistor_value, forward_voltage)
    led_configs = [
        ('Red', '330', '2.0V'),
        ('Green', '330', '2.2V'), 
        ('Blue', '220', '3.0V'),    # Lower resistance for higher Vf
        ('Yellow', '330', '2.1V'),
        ('White', '220', '3.2V')    # Lower resistance for higher Vf
    ]
    
    for i, (color, resistance, vf) in enumerate(led_configs, 1):
        # Current limiting resistor
        resistor = Part('Device.kicad_sym', 'R',
                       ref=f'R{i}',
                       value=resistance,
                       footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
        
        # LED
        led = Part('Device.kicad_sym', 'LED',
                  ref=f'D{i}',
                  value=color,
                  footprint='LED_THT:LED_D5.0mm')
        
        # Connect LED circuit
        vcc += resistor[1]
        resistor[2] += led[1]  # Anode
        led[2] += gnd          # Cathode
        
        print(f"  ✓ {color} LED with {resistance}Ω resistor (Vf={vf})")
    
    print("✓ Multi-color LED circuits created")

def create_led_array():
    """
    Create LED array/matrix
    4x4 LED array for display purposes
    """
    
    print("Creating 4x4 LED array...")
    
    # Power nets
    vcc = Net('VCC')
    gnd = Net('GND')
    
    # Power input
    power_conn = Part('Connector.kicad_sym', 'Conn_01x02_Pin',
                     ref='J_ARRAY_PWR',
                     footprint='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
    
    power_conn[1] += vcc
    power_conn[2] += gnd
    
    # Create 4x4 LED array
    for row in range(1, 5):
        for col in range(1, 5):
            led_num = (row - 1) * 4 + col
            
            # Each LED gets its own resistor
            resistor = Part('Device.kicad_sym', 'R',
                           ref=f'R{led_num:02d}',
                           value='470',
                           footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal')
            
            # LED
            led = Part('Device.kicad_sym', 'LED',
                      ref=f'D{led_num:02d}',
                      value='Red',
                      footprint='LED_THT:LED_D3.0mm')  # Smaller LEDs for array
            
            # Connect: VCC -> Resistor -> LED -> GND
            vcc += resistor[1]
            resistor[2] += led[1]  # Anode
            led[2] += gnd          # Cathode
    
    print("✓ 4x4 LED array created (16 LEDs total)")

def create_led_bargraph():
    """
    Create LED bargraph/level indicator
    10 LEDs in a row for level indication
    """
    
    print("Creating LED bargraph display...")
    
    # Power nets
    vcc = Net('VCC')
    gnd = Net('GND')
    
    # Power input
    power_conn = Part('Connector.kicad_sym', 'Conn_01x02_Pin',
                     ref='J_BAR_PWR',
                     footprint='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
    
    power_conn[1] += vcc
    power_conn[2] += gnd
    
    # Control connector (for microcontroller)
    #control_conn = Part('Connector.kicad_sym', 'Conn_02x06_Odd_Even',
     #                  ref='J_CONTROL',
      #                 footprint='Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical')
    
    control_conn = Part(
    'Connector_Generic.kicad_sym',       # ← SKiDL will append .kicad_sym
    'Conn_02x06_Odd_Even',
    ref='J_CONTROL',
    footprint='Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical')

    
    # Power pins on control connector
    control_conn[11] += vcc  # VCC
    control_conn[12] += gnd  # GND


    
    
    # Create 10 LEDs for bargraph
    led_colors = ['Green'] * 6 + ['Yellow'] * 2 + ['Red'] * 2  # Traffic light style
    
    for i in range(1, 11):
        # Current limiting resistor
        resistor = Part('Device.kicad_sym', 'R',
                       ref=f'R_BAR{i:02d}',
                       value='470',
                       footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal')
        
        # LED
        led = Part('Device.kicad_sym', 'LED',
                  ref=f'D_BAR{i:02d}',
                  value=led_colors[i-1],
                  footprint='LED_THT:LED_D3.0mm')
        
        # Control signal net
        control_signal = Net(f'LED_CTRL_{i}')
        
        # Connect: Control -> Resistor -> LED -> GND
        if i <= 10:  # Connect to control pins
            control_conn[i] += control_signal
        
        control_signal += resistor[1]
        resistor[2] += led[1]  # Anode
        led[2] += gnd          # Cathode
        
        print(f"  ✓ {led_colors[i-1]} LED {i} in bargraph")
    
    print("✓ 10-LED bargraph created")

def create_rgb_led():
    """
    Create RGB LED circuit
    Red, Green, Blue LEDs for color mixing
    """
    
    print("Creating RGB LED circuit...")
    
    # Power nets
    vcc = Net('VCC')
    gnd = Net('GND')
    
    # Power input
    power_conn = Part('Connector.kicad_sym', 'Conn_01x02_Pin',
                     ref='J_RGB_PWR',
                     footprint='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
    
    power_conn[1] += vcc
    power_conn[2] += gnd
    
    # RGB control connector
    rgb_control = Part('Connector.kicad_sym', 'Conn_01x06_Pin',
                      ref='J_RGB_CTRL',
                      footprint='Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical')
    
    # Power pins
    rgb_control[5] += vcc  # VCC
    rgb_control[6] += gnd  # GND
    
    # RGB LED components
    rgb_colors = [('Red', '330'), ('Green', '330'), ('Blue', '220')]
    
    for i, (color, resistance) in enumerate(rgb_colors, 1):
        # Current limiting resistor
        resistor = Part('Device.kicad_sym', 'R',
                       ref=f'R_RGB_{color[0]}',
                       value=resistance,
                       footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
        
        # LED
        led = Part('Device.kicad_sym', 'LED',
                  ref=f'D_RGB_{color[0]}',
                  value=color,
                  footprint='LED_THT:LED_D5.0mm')
        
        # Control signal
        control_signal = Net(f'RGB_{color.upper()}_CTRL')
        rgb_control[i] += control_signal
        
        # Connect: Control -> Resistor -> LED -> GND
        control_signal += resistor[1]
        resistor[2] += led[1]  # Anode
        led[2] += gnd          # Cathode
        
        print(f"  ✓ {color} channel with {resistance}Ω resistor")
    
    print("✓ RGB LED circuit created")

def create_blinking_led():
    """
    Create blinking LED circuit with 555 timer
    Self-oscillating LED flasher
    """
    
    print("Creating blinking LED circuit...")
    
    # Power nets
    vcc = Net('VCC')
    gnd = Net('GND')
    
    # Power input
    power_conn = Part('Connector.kicad_sym', 'Conn_01x02_Pin',
                     ref='J_BLINK_PWR',
                     footprint='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
    
    power_conn[1] += vcc
    power_conn[2] += gnd
    
    # 555 Timer IC
    timer_555 = Part('Timer.kicad_sym', 'NE555P',
                    ref='U_TIMER',
                    footprint='Package_DIP:DIP-8_W7.62mm')
    
    # 555 Timer connections
    timer_555['VCC'] += vcc
    timer_555['GND'] += gnd
    
    
    
    # Timing components
    # Timing resistor
    r_timing = Part('Device.kicad_sym', 'R',
                   ref='R_TIMING',
                   value='100k',
                   footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
    
    # Timing capacitor
    c_timing = Part('Device.kicad_sym', 'C',
                   ref='C_TIMING',
                   value='10uF',
                   footprint='Capacitor_THT:C_Radial_D5.0mm_P2.50mm')
    
    # LED and current limiting resistor
    led_resistor = Part('Device.kicad_sym', 'R',
                       ref='R_LED_BLINK',
                       value='330',
                       footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
    
    blink_led = Part('Device.kicad_sym', 'LED',
                    ref='D_BLINK',
                    value='Red',
                    footprint='LED_THT:LED_D5.0mm')
    
    # 555 timer configuration for astable operation
    # This is a simplified connection - full 555 circuit would need more pins connected
    timer_output = Net('TIMER_OUTPUT')
    timer_555['Q'] += timer_output
    
    # LED circuit: Timer output -> Resistor -> LED -> GND
    timer_output += led_resistor[1]
    led_resistor[2] += blink_led[1]  # Anode
    blink_led[2] += gnd              # Cathode
    
    print("✓ Blinking LED circuit created (555 timer based)")

def generate_led_circuits():
    """Generate netlist and BOM for LED circuits"""
    
    setup_kicad()
    
    # Create different LED circuits (choose which ones to include)
    create_single_led_circuit()
    create_multi_color_leds()
    create_led_array()
    create_led_bargraph()
    create_rgb_led()
    create_blinking_led()
    
    # Generate outputs
    generate_netlist(file_='schematic_1.net')
    #generate_bom(file_='schematic_1.csv')
    generate_svg(file_='schematic_1.svg')

    print("\n" + "="*50)
    print("LED Circuits Generated Successfully!")
    print("="*50)
    print("Files created:")
    print("- led_circuits.net (KiCad netlist)")
    print("- led_circuits.csv (Bill of Materials)")
    
    print("\nCircuits included:")
    print("1. Single LED circuit (basic red LED)")
    print("2. Multi-color LEDs (Red, Green, Blue, Yellow, White)")
    print("3. 4x4 LED array (16 LEDs total)")
    print("4. LED bargraph (10 LEDs - traffic light colors)")
    print("5. RGB LED circuit (color mixing)")
    print("6. Blinking LED (555 timer based)")
    
    print("\nLED Specifications:")
    print("- Forward voltage: 2.0V (Red) to 3.2V (White/Blue)")
    print("- Forward current: ~10-15mA per LED")
    print("- Resistor values: 220Ω to 470Ω depending on LED color")

if __name__ == "__main__":
    generate_led_circuits()