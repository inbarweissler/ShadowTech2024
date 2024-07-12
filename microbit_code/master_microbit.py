from microbit import *
import radio
import random

# Initialize radio and UART
print("Initializing main micro:bit")
display.show(Image.HEART)
sleep(1000)
display.clear()
radio.on()
radio.config(channel=7)
uart.init(baudrate=115200)

# List of device IDs
devices = ['A', 'B']

# Initialize set to track initialized devices
initialized_devices = set()

# Initialize the correct answer list (10 values of 1 or 2)
correct_answers = [random.choice([1, 2]) for _ in range(10)]
answer_index = 0

# Scores dictionary to track each player's score
scores = {device: 0 for device in devices}
first_correct = None

# Main loop
while True:
    responses = {}

    # Wait for all devices to send their initialization message
    while len(initialized_devices) < len(devices):
        incoming = radio.receive()
        if incoming:
            parts = incoming.split(',')
            if len(parts) == 2 and parts[1] == "init":
                device_id = parts[0]
                initialized_devices.add(device_id)
                print("Device {} initialized".format(device_id))

    # Display ! symbol on main micro:bit
    display.show('!')
    # Wait for the main micro:bit's button to be clicked
    while not (button_a.is_pressed() or button_b.is_pressed()):
        sleep(100)
    display.clear()

    # Send correct answer and "ping" to each secondary device
    for device in devices:
        radio.send(device + ",ping," + str(correct_answers[answer_index]))

    # Wait for responses or until all devices respond
    wait_time_ms = 3000
    end_time = running_time() + wait_time_ms
    while running_time() < end_time and len(responses) < len(devices):
        incoming = radio.receive()
        if incoming:
            parts = incoming.split(',')
            if len(parts) == 2 or len(parts) == 3:
                try:
                    device_id, response = parts[0], parts[1]
                    if len(parts) == 3:
                        time_response = parts[2]
                        responses[device_id] = (int(response), int(time_response))
                    else:
                        responses[device_id] = (int(response), end_time)
                except ValueError as e:
                    print("Error converting response to int:", e)

    # Calculate points and determine first correct response
    min_time = wait_time_ms
    for device_id in devices:
        if device_id in responses:
            response, response_time = responses[device_id]
            if response == correct_answers[answer_index]:
                scores[device_id] += 10
                if first_correct is None or response_time < min_time:
                    first_correct = device_id
                    min_time = response_time
            else:
                scores[device_id] -= 10
        else:
            # Neutral response (no button press)
            scores[device_id] += 0

    if first_correct:
        scores[first_correct] += 5

    # Notify secondary devices of the results and to clear ?
    for device in devices:
        if device in responses:
            if responses[device][0] == correct_answers[answer_index]:
                radio.send(device + ",result,correct")
            else:
                radio.send(device + ",result,wrong")
        else:
            radio.send(device + ",result,neutral")

    answer_index = (answer_index + 1) % 10

    # Print responses and scores to terminal using uart.write
    uart.write('Responses and Scores:\r\n')
    for device_id in devices:
        if device_id in responses:
            response_value = responses[device_id][0]
            uart.write('Device {} is {}, Score: {}\r\n'.format(device_id, response_value, scores[device_id]))
        else:
            uart.write('Device {} is 0, Score: {}\r\n'.format(device_id, scores[device_id]))

    # Wait for 5 seconds before next iteration
    sleep(5000)
    first_correct = None
