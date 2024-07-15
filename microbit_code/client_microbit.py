from microbit import *
import radio
import machine
import struct
import random

def microbit_friendly_name():
    length = 5
    letters = 5
    codebook = [
        ['z', 'v', 'g', 'p', 't'],
        ['u', 'o', 'i', 'e', 'a'],
        ['z', 'v', 'g', 'p', 't'],
        ['u', 'o', 'i', 'e', 'a'],
        ['z', 'v', 'g', 'p', 't']
    ]
    name = []

    # Derive our name from the nrf51822's unique ID
    _, n = struct.unpack("II", machine.unique_id())
    ld = 1;
    d = letters;

    for i in range(0, length):
        h = (n % d) // ld;
        n -= h;
        d *= letters;
        ld *= letters;
        name.insert(0, codebook[i][h]);

    return "".join(name);

# system params
wait_time_ms = 5000 # 5 seconds timeout
device_id = microbit_friendly_name()
print(device_id)

# Initialize radio
radio.on()
radio.config(group=7)

radio.send(device_id + ",init")
print("Initializing device ", device_id)
display.clear()

# Main loop
while True:
    incoming = radio.receive()
    if incoming:
        parts = incoming.split(',')
        if len(parts) == 3 and parts[0] == device_id and parts[1] == "assign":
            assigned_letter = parts[2]
            display.show(assigned_letter)
            sleep(2000)
            display.clear()
        if len(parts) == 2 and parts[1] == "ping":
            # Display question mark
            display.show('?')

            # Wait for player's response
            response = -1
            start_time = running_time()
            while running_time() - start_time < wait_time_ms:  
                if button_a.is_pressed():
                    response = 0
                    break
                elif button_b.is_pressed():
                    response = 1
                    break
                sleep(100)  # Check button presses every 100ms

            response_time = running_time() - start_time
            
            # Add a random delay to avoid collisions
            sleep(random.randint(50, 500))
            
            radio.send(device_id + "," + str(response) + "," + str(response_time))
            display.clear()

            while True:
                incoming_result = radio.receive()
                if incoming_result:
                    parts_result = incoming_result.split(',')
                    if len(parts_result) == 3 and parts_result[0] == device_id and parts_result[1] == "result":
                        if parts_result[2] == "correct":
                            print("I was right\r\n")
                            display.show(Image.HAPPY)
                        elif parts_result[2] == "wrong":
                            print("I was wrong\r\n")
                            display.show(Image.SAD)
                        else:
                            print("neutral\r\n")
                            display.show(Image.SQUARE)
                        sleep(2000)
                        display.clear()
                        break
                sleep(100)
