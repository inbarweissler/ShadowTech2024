# ShadowTech2024

## Introduction
This is a quiz game played between a main micro:bit and multiple secondary devices, with a PC server for visualization.

## How to Run
1. **Main Micro:bit Setup:**
   - Flash `master_microbit.py` to the main micro:bit using [MicroPython Online Compiler](https://python.microbit.org/v/3).
   
2. **Secondary Micro:bit Setup:**
   - Similarly, flash `client_microbit.py` to each secondary micro:bit.
   
3. **PC Server Setup:**
   - Install required Python libraries (`matplotlib`, `pyserial`).
   - Adjust the COM port in `microbit_server.py` to match your setup.
   - Run `microbit_server.py` using Python.

## Student Task
A detailed task for the students is provided [here](https://virscient.atlassian.net/wiki/spaces/CNS/pages/edit-v2/1056079890) 

## Final Notes
The demo was tested successfully with 2 secondary devices. 
While testing, we experienced radio collisions due to multiple responses on the same channel, and a random delay was added to mitigate this issue. 
This now works better, but we may still suffer from collisions when the number of devices is increased.
