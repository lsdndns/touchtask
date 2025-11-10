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
stimuli = [f"img/img{i}.png" for i in range(1, 5)]
all_combinations = list(itertools.combinations(stimuli, 3))
random.shuffle(all_combinations)
triple_trials = all_combinations
random.shuffle(triple_trials)
images = []

# blocks
block_size = 2
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
def show_block_screen(block_num):
    global current_block, current_trial_in_block
    current_block = block_num
    current_trial_in_block = 0

    if block_num % 2 == 0 and block_num != 0:
        messagebox.showinfo("Take a break", "Take a couple of minutes to rest.\nPress OK to continue.")

    messagebox.showinfo("New Block", f"Block {block_num + 1} will start now.\nPress OK to begin.")
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
        text="Click on the image that is most different from the other two.\nCliquez sur l'image la plus différente.",
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
            end_experiment()

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
        "(English) Type a word or short phrase that describes this image.\n"
        "(Français) Tapez un mot ou une courte phrase qui décrit cette image.\n"
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


def end_descriptor_task():
    messagebox.showinfo("Done", f"Thank you! All data saved to {filename}")
    root.destroy()

# -------------------------------
# Experiment flow
# -------------------------------
def end_experiment():
    messagebox.showinfo("Done", "Thank you! Triple task completed.")
    show_descriptor_trial(0)

def start_experiment():
    messagebox.showinfo("Information",
        "Welcome to Lisa's task!\n\n"
        "(English)\nAt each trial, three images appear. Click on the image most different from the others.\n\n"
        "(Français)\nÀ chaque essai, trois images s'affichent. Cliquez sur celle qui est la plus différente.\n\nPress OK to start.")
    show_block_screen(0)

root.after(100, start_experiment)
root.mainloop()
