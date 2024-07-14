from microbit import *
import radio

# Initialize radio and UART
print("Initializing main micro:bit")
display.show(Image.HEART)
sleep(1000)
display.clear()
radio.on()
radio.config(group=7)
uart.init(baudrate=115200)

correct_answer = 3
# Game parameters
tot_devices = 2
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J','K','L']

# Scores dictionary to track each player's score
first_correct = None
# Initialize set to track initialized devices
scores = {}
secondaries_letter = {}
# Wait for all devices to send their initialization message
while len(scores) < tot_devices:
    incoming = radio.receive()
    if incoming:
        parts = incoming.split(',')
        if len(parts) == 2 and parts[1] == "init":
            device_id = parts[0]
            if device_id not in scores:
                letter = letters[len(scores)]
                scores[device_id] = 0
                secondaries_letter[device_id] = letter
                radio.send(device_id + ",assign," + letter)
                print("Device {} initialized with letter {}".format(device_id, letter))

# Main loop
quiz_round = -1
terminate = False
while not terminate:
    quiz_round+=1
    # Ensure PC receives initial message
    initial_message_ack = False
    while not initial_message_ack:
        uart.write('Start round:{}\r\n'.format(quiz_round))
        sleep(1000)
        if uart.any():
            correct_answer = int(uart.read().decode('utf-8').strip())
            initial_message_ack = True
            if correct_answer < 0:
                terminate = True
    if terminate:
        continue
    
    responses = {}

    # Display ! symbol on main micro:bit
    display.show('!')
    # Wait for the main micro:bit's button to be clicked
    while not (button_a.is_pressed() or button_b.is_pressed()):
        sleep(100)
    display.clear()

    # Send "ping" to each secondary device
    for device, _ in scores.items():
        radio.send(device + ",ping")

    # Wait for responses or until all devices respond
    wait_time_ms = 5000
    end_time = running_time() + wait_time_ms
    while running_time() < end_time and len(responses) < tot_devices:
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
    for device_id,_ in scores.items():
        if device_id in responses:
            response, response_time = responses[device_id]
            if response == correct_answer:
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

    # Notify secondary devices of the results
    for device_id,_ in scores.items():
        if device_id in responses:
            if responses[device_id][0] == correct_answer:
                radio.send(device_id + ",result,correct")
            else:
                radio.send(device_id + ",result,wrong")
        else:
            radio.send(device_id + ",result,neutral")
    
    # Send responses and scores to PC
    uart.write('Responses and Scores #{}:\r\n'.format(quiz_round + 1))
    for device_id,_ in scores.items():
        if device_id in responses:
            response_value = responses[device_id][0]
            is_winner = 1 if device_id == first_correct else 0
            uart.write('Device {} is {}, Score: {}, Winner: {}\r\n'.format(secondaries_letter[device_id], response_value, scores[device_id], is_winner))
        else:
            uart.write('Device {} is 0, Score: {}, Winner: 0\r\n'.format(secondaries_letter[device_id], scores[device_id]))

    # Wait for wait_time_ms before next iteration
    sleep(wait_time_ms)
    first_correct = None
