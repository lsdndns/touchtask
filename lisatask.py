import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import csv
import os
import itertools
import random
import time

# -------------------------------
# Experiment setup
# -------------------------------
stimuli = [f"img/img{i}.png" for i in range(1, 11)] # to update 
all_combinations = list(itertools.combinations(stimuli, 3))
random.shuffle(all_combinations)
triple_trials = all_combinations*2
random.shuffle(triple_trials)
practice_trials = random.sample(all_combinations, 5)

images = []

# blocks
block_size = 20 # to update 
blocks = [triple_trials[i:i + block_size] for i in range(0, len(triple_trials), block_size)]

# tracking
current_block = 0
current_trial_in_block = 0
descriptor_index = 0

# timing
trial_start_time = None

# one output file
filename = f"experiment_data_{random.randint(1000,9999)}.csv"

# -------------------------------
# Tkinter setup
# -------------------------------
root = tk.Tk()
root.title("Lisa's task")
root.attributes('-fullscreen', True)
root.bind("<Escape>", lambda e: root.attributes('-fullscreen', False))

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
canvas = tk.Canvas(root, width=screen_width, height=screen_height)
canvas.pack()

image_size = int(screen_height * 0.4)
spacing = int(screen_width * 0.05)

# -------------------------------
# Helper: write a row incrementally
# -------------------------------
def write_csv(row):
    fieldnames = [
        'task', 'trial_num', 'item1', 'item2', 'item3',
        'response_img', 'reaction_time', 'stimulus', 'descriptor'
    ]
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

# -------------------------------
# Triple odd-one-out task
# -------------------------------
def show_practice_trial(index):
    global images, trial_start_time, practice_index
    trial_start_time = time.time()
    canvas.delete("all")
    images = []
    trial = practice_trials[index]

    # Instructions at the top
    canvas.create_text(
        screen_width // 2, 75,
        text="Practice: Click on the texture that is most different from the other two.\n"
             "Entraînement : Cliquez sur la texture la plus différente des deux autres.",
        font=("Helvetica", 24, "bold"), fill="black", justify="center"
    )

    num_images = len(trial)
    total_width = num_images * image_size + (num_images - 1) * spacing
    start_x = (screen_width - total_width) // 2 + image_size // 2
    y_pos = screen_height // 2
    positions = [start_x + i * (image_size + spacing) for i in range(num_images)]

    # Create and display each image
    for i, img_path in enumerate(trial):
        try:
            img = Image.open(img_path).resize((image_size, image_size))
            photo = ImageTk.PhotoImage(img)
            images.append(photo)
            canvas.create_image(positions[i], y_pos, image=photo, tags=("pimg" + str(i)))
            # When any image is clicked, go to next practice trial
            canvas.tag_bind("pimg" + str(i), "<Button-1>", lambda e: next_practice_trial())
        except Exception as e:
            print(f"Error loading {img_path}: {e}")

def next_practice_trial():
    global practice_index
    practice_index += 1
    if practice_index < len(practice_trials):
        show_practice_trial(practice_index)
    else:
        end_training()

def show_block_screen(block_num):
    global current_block, current_trial_in_block
    current_block = block_num
    current_trial_in_block = 0

    if block_num % 2 == 0 and block_num != 0:
        messagebox.showinfo("Take a break", "Take a couple of minutes to rest if needed.\nPress OK when you are ready to continue.")

    messagebox.showinfo("New Block", f"Press Ok to start Block {block_num + 1}.\n")
    show_trial(current_trial_in_block)


def show_trial(trial_index):
    global images, trial_start_time
    trial_start_time = time.time()
    canvas.delete("all")
    images = []
    trial = blocks[current_block][trial_index]

    # Instructions
    canvas.create_text(
        screen_width // 2, 75,
        text="Click on the texture that is most different from the other two.\nCliquez sur la texture la plus différente des deux autres.",
        font=("Helvetica", 24, "bold"), fill="black", justify="center"
    )

    num_images = len(trial)
    total_width = num_images * image_size + (num_images - 1) * spacing
    start_x = (screen_width - total_width) // 2 + image_size // 2
    y_pos = screen_height // 2
    positions = [start_x + i * (image_size + spacing) for i in range(num_images)]

    for i, img_path in enumerate(trial):
        try:
            img = Image.open(img_path).resize((image_size, image_size))
            photo = ImageTk.PhotoImage(img)
            images.append(photo)
            canvas.create_image(positions[i], y_pos, image=photo, tags=("img" + str(i)))
            canvas.tag_bind("img" + str(i), "<Button-1>", lambda e, idx=i: record_response(idx))
        except Exception as e:
            print(f"Error loading {img_path}: {e}")


def record_response(choice_index):
    global current_trial_in_block, current_block
    trial = blocks[current_block][current_trial_in_block]

    response_img = trial[choice_index] if 0 <= choice_index < len(trial) else "NaN"
    rt = time.time() - trial_start_time if trial_start_time else "NaN"

    def clean_name(path):
        return os.path.splitext(os.path.basename(path))[0]

    row = {
        'task': 'triple',
        'trial_num': current_trial_in_block + 1 + current_block * block_size,
        'item1': clean_name(trial[0]) if trial[0] else "NaN",
        'item2': clean_name(trial[1]) if trial[1] else "NaN",
        'item3': clean_name(trial[2]) if trial[2] else "NaN",
        'response_img': clean_name(response_img) if response_img else "NaN",
        'reaction_time': rt,
        'stimulus': "NaN",
        'descriptor': "NaN"
    }

    write_csv(row)

    current_trial_in_block += 1
    if current_trial_in_block < len(blocks[current_block]):
        show_trial(current_trial_in_block)
    else:
        current_block += 1
        if current_block < len(blocks):
            show_block_screen(current_block)
        else:
            end_task1()

# -------------------------------
# Descriptor task
# -------------------------------
def show_descriptor_trial(index):
    global descriptor_index
    descriptor_index = index
    canvas.delete("all")

    stimulus_path = stimuli[index]
    try:
        img = Image.open(stimulus_path).resize((image_size, image_size))
        photo = ImageTk.PhotoImage(img)
        canvas.image = photo
        canvas.create_image(screen_width // 2, screen_height // 2 - 50, image=photo)
    except Exception as e:
        print(f"Error loading {stimulus_path}: {e}")

    instruction = (
        "(English) Type a word that describes this texture.\n"
        "(Français) Tapez un mot qui décrit cette texture.\n"
        "Press Enter when done."
    )
    canvas.create_text(screen_width // 2, screen_height // 2 + image_size // 2 + 50,
                       text=instruction, font=("Helvetica", 24, "bold"), fill="black", justify="center")

    entry = tk.Entry(root, font=("Helvetica", 20))
    entry.place(relx=0.5, rely=0.9, anchor="center", width=400)
    entry.focus()

    def submit_response(event):
        response = entry.get().strip() or "NaN"
        row = {
            'task': 'descriptor',
            'trial_num': "NaN",
            'item1': "NaN",
            'item2': "NaN",
            'item3': "NaN",
            'response_img': "NaN",
            'reaction_time': "NaN",
            'stimulus': os.path.splitext(os.path.basename(stimulus_path))[0],
            'descriptor': response
        }
        write_csv(row)
        entry.destroy()
        if descriptor_index + 1 < len(stimuli):
            show_descriptor_trial(descriptor_index + 1)
        else:
            end_descriptor_task()

    entry.bind("<Return>", submit_response)

# -------------------------------
# Experiment flow
# -------------------------------
def start_experiment():
    messagebox.showinfo("Information",
        "Welcome to Lisa's experiment!\n\n"
        "This experiment entails two tasks.\n"
        "The first task does not take longer than 20 min\n"
        "The second task does not take longer than 5 min\n\n"
        "Press OK to start.")
    instruction_task1()

def instruction_task1():
    messagebox.showinfo("Instructions 1",
        "Task 1\n\n"
        "At each trial, three images appear. Click on the image that is most different from the other two.\n"
        "Before the main task, you will complete five training trials\n\n"
        "Press OK to start the training.")
    global practice_index
    practice_index = 0
    show_practice_trial(practice_index)

def end_training():
    messagebox.showinfo("Instructions 1",
        "Task 1\n\n"
        "Thank you for doing the training. Now it is time to do the main task.\n\n"
        "Press OK to begin.")
    show_block_screen(0)

def end_task1():
    messagebox.showinfo("Done", 
        "Thank you! Task 1 is completed. \n"
        "Press OK to start task 2.\n")
    instruction_task2()

def instruction_task2():
    messagebox.showinfo("Instructions 2",
        "Task 2\n\n"
        "For each image, describe the texture in one word.\n\n"
        "Press OK to start.")
    show_descriptor_trial(0)

def end_descriptor_task():
    messagebox.showinfo("Done",
        "Thank you! Task 2 is completed. \n"
        f"All data saved to {filename}")
    root.destroy()

root.after(100, start_experiment)
root.mainloop()