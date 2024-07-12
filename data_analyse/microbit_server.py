import serial
import matplotlib.pyplot as plt
from collections import defaultdict
import time


# Function to read from the serial port
def read_from_serial(curr_ser):
    return curr_ser.readline().decode('utf-8').strip()


# Function to update and plot scores
def plot_scores(all_scores, iter_num):
    plt.clf()  # Clear the current figure
    devices = list(all_scores.keys())
    scores_list = [all_scores[device] for device in devices]

    # Find the highest score(s)
    max_score = max(scores_list)
    max_indices = [i for i, score in enumerate(scores_list) if score == max_score]

    # Plot scatter plot
    for i, device in enumerate(devices):
        if i in max_indices:
            plt.scatter(device, scores_list[i], color='red', marker='o', s=150)
        else:
            plt.scatter(device, scores_list[i], color='blue', marker='x', s=100)

    plt.xlabel('Players')
    plt.ylabel('Scores')
    plt.title(f'Round {iter_num} Scores')
    plt.ylim(min(scores_list) - 10, max(scores_list) + 20)
    plt.xticks(rotation=45)

    # Annotate the scores on the plot
    for device_ind, curr_score in enumerate(scores_list):
        plt.text(devices[device_ind], curr_score, f'{curr_score}', ha='center', va='bottom')

    plt.tight_layout()
    plt.draw()
    plt.pause(0.01)  # Pause to update the plot


# Initialize serial connection (adjust the COM port as necessary)
ser = serial.Serial('COM11', 115200, timeout=1)

# Dictionary to store scores
scores = defaultdict(int)
round_number = 1

# Initialize plot
plt.ion()
fig, ax = plt.subplots()

try:
    while True:
        # Read line from serial
        line = read_from_serial(ser)

        if line.startswith('Responses and Scores:'):
            # Wait for the full block of scores to be transmitted
            responses_and_scores = []
            while True:
                line = read_from_serial(ser)
                if not line:
                    break
                responses_and_scores.append(line)

            # Parse responses and scores
            for entry in responses_and_scores:
                parts = entry.split(',')
                device_id = parts[0].split()[1]
                score = int(parts[-1].split()[-1])
                if "Score" in entry:
                    scores[device_id] = score

            # Plot scores
            plot_scores(scores, round_number)
            round_number += 1

            # Display the plot
            plt.show(block=False)
            plt.pause(0.01)

            # Wait before the next round
            time.sleep(5)
finally:
    ser.close()
