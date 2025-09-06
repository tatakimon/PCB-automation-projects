import pcbnew

board = pcbnew.GetBoard()

nets = board.GetNetsByName()

for netname, net in nets.items():
    print(f"Net Name: {netname}, Net Code: {net.GetNetCode()}")

for module in board.GetModules():
    print(f"Module: {module.GetReference()}, Position: {module.GetPosition()}, Orientation: {module.GetOrientation()}")
import os, runpy
