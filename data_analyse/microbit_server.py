import serial
import matplotlib.pyplot as plt
from collections import defaultdict

# Questions, possible answers, and correct answers
questions = ["Q1 what day is today?", "Q2 what month is it now?",
             "Q3 what city are we in?", "Q4 what country are we in?"]
possible_answers = [["Friday", "Sunday"], ["July", "August"],
                    ["Hamilton", "NYC"], ["NZ", "USA"]]

# Function to read from the serial port
def read_from_serial(curr_ser):
    return curr_ser.readline().decode('utf-8').strip()

# Function to update and plot scores
def plot_scores(current_score, iter_num, round_winner, fig, ax1, ax2):
    # Clear the previous plot contents
    ax1.clear()
    ax2.clear()

    # First subplot: current question with two possible answers
    ax1.set_title(f'Round {iter_num} Question')
    ax1.text(0.5, 0.8, questions[iter_num - 1], ha='center', va='center', fontsize=12, fontweight='bold')
    ax1.text(0.25, 0.5, f"A) {possible_answers[iter_num - 1][0]}", ha='center', va='center', fontsize=12)
    ax1.text(0.75, 0.5, f"B) {possible_answers[iter_num - 1][1]}", ha='center', va='center', fontsize=12)
    ax1.axis('off')

    # Second subplot: scores
    devices = list(current_score.keys())
    scores_list = [current_score[device] for device in devices]

    # Plot scatter plot
    for i, device in enumerate(devices):
        ax2.scatter(device, scores_list[i], color='blue', marker='x', s=100)  # 'X' mark for all players
        if device == round_winner:
            ax2.scatter(device, scores_list[i], color='red', marker='o', s=150)  # Red 'O' mark for the round winner

    ax2.set_xlabel('Players')
    ax2.set_ylabel('Scores')
    ax2.set_yticks([])
    ax2.set_title(f'Round {iter_num} Scores')
    ax2.set_ylim(min(scores_list) - 10, max(scores_list) + 10)
    ax2.set_xticks(devices)
    ax2.tick_params(axis='x', rotation=45)

    # Annotate the scores on the plot
    for device_ind, curr_score in enumerate(scores_list):
        ax2.text(devices[device_ind], curr_score + 2, f'{curr_score}', ha='center', va='bottom')

    fig.tight_layout()
    fig.canvas.draw()
    fig.canvas.flush_events()  # Ensure the plot updates immediately
    fig.show()

# Function to plot histogram of scores
def plot_hist(all_scores):
    plt.figure()
    plt.hist(list(all_scores.values()), bins=range(min(all_scores.values()), max(all_scores.values()) + 10, 10),
             edgecolor='black')
    plt.xlabel('Scores')
    plt.ylabel('Frequency')
    plt.title('Histogram of Scores')
    plt.grid(True)
    plt.tight_layout()
    plt.show(block=True)

# Initialize serial connection (adjust the COM port as necessary)
ser = serial.Serial('COM11', 115200, timeout=1)

# Dictionary to store scores
scores = defaultdict(int)
round_number = -1
tot_rounds = 4
answers = [1, 1, 1, 1]
# Questions and answers received from the micro:bit
questions = []
possible_answers = []

# Initialize plot
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

try:
    while round_number <= tot_rounds:
        while True:
            line = read_from_serial(ser)
            if line.startswith('Start round:'):
                round_number = int(line.split(':')[-1])
                response = b'-1\r\n' if round_number >= len(answers) else b'0\r\n' if answers[round_number] == 0 else b'1\r\n'
                ser.write(response)
                break
        print(f"Waiting for data for round {round_number}...")  # Debug log

        # Question and answers for the round
        question = questions[round_number]
        possible_answers = answers[round_number]

        # Read the responses and scores for the round
        round_winner = None
        while True:
            line = read_from_serial(ser)
            if line.startswith('Start scores message'):
                ser.write(b'ack\r\n')
                break

        while True:
            line = read_from_serial(ser)
            if line.startswith('Device'):
                print(f"Received device score: {line}")  # Debug log
                parts = line.split(',')
                device_id = parts[0].split()[1]
                score = int(parts[1].split()[1])
                scores[device_id] = score
                winner = int(parts[2].split()[1])
                if winner:
                    round_winner = device_id
            elif line.startswith('Finish'):
                break

        # Plot the scores
        plot_scores(scores, round_number, round_winner, fig, ax1, ax2)
        round_number += 1

    # After the game ends, plot a histogram of scores
    # TODO: fix histogram
    plot_hist(scores)

finally:
    # Ensure the plot remains open after the serial connection is closed
    plt.ioff()
    plt.show()
    ser.close()
