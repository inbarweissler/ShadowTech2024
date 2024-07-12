from microbit import *
import radio

# Initialize radio
radio.on()
radio.config(channel=7)

# Unique ID for the device (Change for each secondary device)
device_id = 'A'  # Replace with 'B' for the second device
radio.send(device_id + ",init")
display.show(Image.HEART_SMALL)
print("Initializing device ", device_id)
sleep(1000)
display.clear()

# Main loop
while True:
    incoming = radio.receive()
    if incoming:
        parts = incoming.split(',')
        if len(parts) == 3 and parts[1] == "ping":
            correct_answer = int(parts[2])
            # Display question mark
            display.show('?')

            # Wait for player's response
            response = 0
            start_time = running_time()
            while running_time() - start_time < 3000:  # 3 seconds timeout
                if button_a.is_pressed():
                    response = 1
                    break
                elif button_b.is_pressed():
                    response = 2
                    break
                sleep(100)  # Check button presses every 100ms

            # Send response to the main micro:bit (only send the first response)
            response_time = running_time() - start_time
            radio.send(device_id + "," + str(response) + "," + str(response_time))
            display.clear()

            # Wait for result command before continuing
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
                            display.show(Image.HEART_SMALL)
                        sleep(2000)
                        display.clear()
                        break
                sleep(100)  # Check for result message every 100ms
