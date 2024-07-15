import csv
import serial
import matplotlib.pyplot as plt


# Global parameters
master_port = 'COM10'
questions = []
possible_answers = []
answers = []
round_number = -1


# Function to read from the serial port
def read_from_serial(curr_ser):
    return curr_ser.readline().decode('utf-8').strip()


# Function to plot the current question and possible answers
def plot_question(fig, ax1, ax2, iter_num):
    ax1.clear()
    ax2.clear()
    ax1.set_title(f'Round {iter_num + 1} Question')
    ax1.text(0.5, 0.8, questions[iter_num], ha='center', va='center', fontsize=12, fontweight='bold')
    ax1.text(0.25, 0.5, f"A) {possible_answers[iter_num][0]}", ha='center', va='center', fontsize=12)
    ax1.text(0.75, 0.5, f"B) {possible_answers[iter_num][1]}", ha='center', va='center', fontsize=12)
    ax1.axis('off')
    ax2.axis('off')
    fig.canvas.draw()
    fig.canvas.flush_events()
    fig.show()


# Function to update and plot scores
def plot_scores(current_score, iter_num, round_winner, fig, ax1, ax2):
    # Clear the previous plot contents
    ax1.clear()
    ax2.clear()

    # First subplot: current question with two possible answers
    ax1.set_title(f'Round {iter_num + 1} Question')
    ax1.text(0.5, 0.8, questions[iter_num], ha='center', va='center', fontsize=12, fontweight='bold')
    ax1.text(0.25, 0.5, f"A) {possible_answers[iter_num][0]}", ha='center', va='center', fontsize=12)
    ax1.text(0.75, 0.5, f"B) {possible_answers[iter_num][1]}", ha='center', va='center', fontsize=12)
    ax1.axis('off')

    # Second subplot: scores
    devices = list(current_score.keys())
    scores_list = [current_score[device] for device in devices]

    # Plot scatter plot
    for i, device in enumerate(devices):
        ax2.scatter(device, scores_list[i], color='blue', marker='x', s=100)  # 'X' mark for all players
        if device in round_winner:
            ax2.scatter(device, scores_list[i], color='red', marker='o', s=150)  # Red 'O' mark for the round winner

    ax2.set_xlabel('Players')
    ax2.set_ylabel('Scores')
    ax2.set_yticks([])
    ax2.set_title(f'Round {iter_num + 1} Scores')
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


# Function to display the winner message and image
def display_winner(fig, ax1, final_winner):
    # Clear the figure
    fig.clear()
    ax = fig.add_subplot(111)

    # Display winner text
    ax.text(0.5, 0.5, f"And the winner\\s is...\n\n {",".join(map(str, final_winner))}", ha='center', va='center',
            fontsize=40, fontweight='bold')
    ax.axis('off')

    fig.show()


def parse_csv(file_path):
    # Clear any previously read questions and answers
    questions.clear()
    possible_answers.clear()
    answers.clear()

    # Parse CSV file to get questions and answers
    with open(file_path, mode='r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            question_part, answers_part, solution_part = row[0].split('|')
            curr_answers = answers_part.split(' ')
            questions.append(question_part.strip())
            possible_answers.append([curr_answers[0].strip(), curr_answers[1].strip()])
            answers.append(solution_part.strip())
    # Determine the total number of rounds based on the number of questions
    return len(questions)


# Initialize serial connection (adjust the COM port as necessary)
ser = serial.Serial(master_port, 115200, timeout=1)

# Dictionary to store scores
scores = dict()

# Initialize plot
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

try:
    tot_rounds = parse_csv('questions.csv')
    while round_number <= tot_rounds:
        while True:
            line = read_from_serial(ser)
            if line.startswith('Start round:'):
                round_number = int(line.split(':')[-1])
                print(f"preparing for round {round_number}")  # Debug log
                response = b'-1\r\n' if round_number >= len(answers) else b'0\r\n' if answers[
                                                                                          round_number] == 0 else b'1\r\n'
                ser.write(response)
                break
        if round_number >= tot_rounds:
            break
        print(f"Waiting for data for round {round_number}...")  # Debug log

        round_winner = []

        # Plot the current question and possible answers
        plot_question(fig, ax1, ax2, round_number)

        # Read the responses and scores for the round
        while True:
            line = read_from_serial(ser)
            if line.startswith('Responses and Scores'):
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
                    round_winner.append(device_id)
            else:
                break

        # Plot the scores
        plot_scores(scores, round_number, round_winner, fig, ax1, ax2)

    if round_number > 0:
        # Determine the final winner
        max_value = max(scores.values())
        final_winner = []
        for key in scores.keys():
            if scores[key] == max_value:
                final_winner.append(key)

        # Display the winner message and image
        display_winner(fig, ax1, final_winner)

finally:
    # Ensure the plot remains open after the serial connection is closed
    plt.ioff()
    plt.show()
    ser.close()
