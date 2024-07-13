# ShadowTech2024

## Introduction
This project involves a game played between a main micro:bit and multiple secondary micro:bits, with a PC server for visualization.

## How to Run
1. **Main Micro:bit Setup:**
   - Flash `master_microbit.py` to the main micro:bit using [MicroPython Online Compiler](https://python.microbit.org/v/3).
   - Ensure radio channel configuration matches in all micro:bits.
   
2. **Secondary Micro:bit Setup:**
   - Flash `client_microbit.py` to each secondary micro:bit with unique device IDs (`A`, `B`, etc.).
   
3. **PC Server Setup:**
   - Install required Python libraries (`matplotlib`, `pyserial`).
   - Adjust the COM port in `microbit_server.py` to match your setup.
   - Run `microbit_server.py` using Python.

## Serial Communication Background
Micro:bits communicate via radio signals, while the main micro:bit communicates with the PC server over USB using UART. This setup ensures real-time score updates and game control.

## Embedded Systems Perspective
Micro:bits are programmed using MicroPython, providing a simplified yet powerful platform for embedded systems development.

For further details and troubleshooting, refer to the comments in the code files (`master_microbit.py`, `client_microbit.py`, `microbit_server.py`).
