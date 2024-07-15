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

# Game parameters
# TODO: update this value, current settings wait until all tot_devices are connected
tot_devices = 2
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J','K','L']
correct_answer = 3 # The correct answer will be either 0 or 1
wait_time_ms = 6000 # 6 seconds timeout

# Initialize set to track initialized devices
scores = {}
secondaries_letter = {}
is_round_winner = {}
device_last_response = {}
last_response_time = {}

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

    display.show('!')

    while not (button_a.is_pressed() or button_b.is_pressed()):
        sleep(100)
    display.clear()

    # Send "ping" to each secondary device
    for device, _ in scores.items():
        radio.send(device + ",ping")

    # Wait for responses or until all devices respond
    response_dict = {}
    end_time = running_time() + wait_time_ms
    while running_time() < end_time and len(response_dict) < tot_devices:
        incoming = radio.receive()
        if incoming:
            parts = incoming.split(',')
            if len(parts) == 3: # Client: radio.send(device_id + "," + str(response) + "," + str(response_time))
                try:
                    device_id, response, time_response = parts[0], parts[1], parts[2]
                    if device_id not in response_dict:
                        response_dict[device_id] = 1
                        device_last_response[device_id] = int(response)
                        last_response_time[device_id] = int(time_response)
                        is_round_winner[device_id] = 0
                except ValueError as e:
                    print("Error converting response to int:", e)

    # Calculate points and notify secondary devices
    min_time = wait_time_ms
    
    for device_id,_ in scores.items():
        if device_id not in response_dict:
            response_dict[device_id] = 0
            continue
        if device_last_response[device_id] == correct_answer:
            scores[device_id] += 10
            if last_response_time[device_id] < min_time:
                min_time = last_response_time[device_id]
            radio.send(device_id + ",result,correct")
        elif device_last_response[device_id] == -1:
            scores[device_id] += 0
            radio.send(device_id + ",result,neutral")
        else:
            scores[device_id] -= 10
            radio.send(device_id + ",result,wrong")
    
    # Another loop to check who won this round
    for device_id,_ in scores.items():
        if response_dict[device_id]:
            if last_response_time[device_id] == min_time and device_last_response[device_id] == correct_answer:
                scores[device_id] += 5
                is_round_winner[device_id] = 1
    
    # Send responses and scores to PC
    uart.write('Responses and Scores #{}:\r\n'.format(quiz_round + 1))
    for device_id,_ in scores.items():
        if response_dict[device_id]:
            uart.write('Device {} is {}, Score: {}, Winner: {}\r\n'.format(secondaries_letter[device_id], device_last_response[device_id], scores[device_id], is_round_winner[device_id]))

    sleep(wait_time_ms)
