
Reference


Ideas


API


Project

Untitled project

        if len(parts) == 2 and parts[1] == "init":
            if device_id not in scores:
                scores[device_id] = 0
            print("Device {} initialized".format(device_id))
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

