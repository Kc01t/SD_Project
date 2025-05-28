import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
import datetime
import webbrowser
import pygame
import json

# Initialize pygame mixer for audio
pygame.mixer.init()

# File to store meeting data
meeting_data_file = "meeting_data.json"

# Function to handle adding hyperlinks and meeting reminders
def add_hyperlink_with_reminder():
    link_name = link_name_entry.get()
    link_url = link_url_entry.get()

    if link_name and link_url:
        hyperlink_listbox.insert(tk.END, f"{link_name}: {link_url}")
        link_name_entry.delete(0, tk.END)
        link_url_entry.delete(0, tk.END)
        
        meeting_date = simpledialog.askstring("Meeting Date", f"Enter meeting date for '{link_name}' (YYYY-MM-DD):")
        if meeting_date:
            try:
                meeting_date = datetime.datetime.strptime(meeting_date, "%Y-%m-%d")
                meeting_time = simpledialog.askstring("Meeting Time", f"Enter meeting time for '{link_name}' (HH:MM):")
                if meeting_time:
                    try:
                        meeting_datetime = datetime.datetime.strptime(meeting_time, "%H:%M")
                        meeting_datetime = meeting_datetime.replace(year=meeting_date.year, month=meeting_date.month, day=meeting_date.day)
                        now = datetime.datetime.now()
                        time_difference = meeting_datetime - now
                        if time_difference.total_seconds() > 0:
                            meeting_reminder = f"Meeting for '{link_name}' at {meeting_datetime.strftime('%Y-%m-%d %H:%M')}"
                            meeting_reminders.append((meeting_datetime, meeting_reminder, link_url))
                            # Save meeting data to the JSON file
                            save_meeting_data()
                    except ValueError:
                        messagebox.showwarning("Warning", "Invalid time format. Please use HH:MM.")
                else:
                    messagebox.showwarning("Warning", "Meeting time not provided.")
            except ValueError:
                messagebox.showwarning("Warning", "Invalid date format. Please use YYYY-MM-DD.")
    else:
        messagebox.showwarning("Warning", "Please enter both a name and a hyperlink URL.")

# Function to handle opening selected hyperlink
def open_hyperlink():
    selected_index = hyperlink_listbox.curselection()
    if selected_index:
        selected_link = hyperlink_listbox.get(selected_index)
        webbrowser.open(selected_link.split(': ')[1])
    else:
        messagebox.showwarning("Warning", "Please select a hyperlink.")

# Function to update the opacity based on the slider value
def update_opacity(value):
    opacity = float(value) / 100.0
    app.attributes('-alpha', opacity)

# Function to check for meeting reminders
def check_meeting_reminders():
    now = datetime.datetime.now()
    for meeting_datetime, meeting_reminder, link_url in meeting_reminders:
        time_difference = meeting_datetime - now
        if 0 <= time_difference.total_seconds() < 60:
            messagebox.showinfo("Meeting Reminder", meeting_reminder)
            meeting_reminders.remove((meeting_datetime, meeting_reminder, link_url))
            # Open the hyperlink in the web browser
            webbrowser.open(link_url)
            # Play an alert sound
            play_alert_sound()

# Function to play an alert sound
def play_alert_sound():
    pygame.mixer.music.load("alert_sound.mp3")  # Change "alert_sound.mp3" to the path of your program's alert sound file
    pygame.mixer.music.play()

# Function to save meeting data to a JSON file
def save_meeting_data():
    with open(meeting_data_file, "w") as file:
        json.dump(meeting_reminders, file)

# Function to load meeting data from a JSON file
def load_meeting_data():
    try:
        with open(meeting_data_file, "r") as file:
            loaded_data = json.load(file)
            meeting_reminders.extend(loaded_data)
    except FileNotFoundError:
        messagebox.showinfo("Info", "No meeting data found.")

# Function to open the settings dialog
def open_settings_dialog():
    settings_dialog = tk.Toplevel(app)
    settings_dialog.title("Settings")

    # Create a button to save meeting data to a JSON file
    save_button = tk.Button(settings_dialog, text="Save Meeting Data", command=save_meeting_data)
    save_button.pack()

    # Create a button to load meeting data from a JSON file
    load_button = tk.Button(settings_dialog, text="Load Meeting Data", command=load_meeting_data)
    load_button.pack()

    # Create a label and slider for opacity control in the dialog
    opacity_label = tk.Label(settings_dialog, text="Opacity:")
    opacity_label.pack()
    opacity_slider = ttk.Scale(settings_dialog, from_=0, to=100, orient="horizontal", command=update_opacity)
    opacity_slider.set(100)  # Initialize opacity to 100%
    opacity_slider.pack()

    # Create a button to mute/unmute in the dialog
    mute_unmute_button = tk.Button(settings_dialog, text="Mute", command=lambda: on_settings_selected("Mute"))
    mute_unmute_button.pack()

# Function to open the day view calendar
def display_day_view_calendar():
    day_view_window = tk.Toplevel(app)
    day_view_window.title("Day View Calendar")

    # Create a label to display the current date
    current_date_label = tk.Label(day_view_window, text=datetime.date.today().strftime("%Y-%m-%d"))
    current_date_label.pack()

    # Create a frame to display events for the day
    day_view_frame = ttk.Frame(day_view_window)
    day_view_frame.pack()

    # Get the schedule for the current day
    schedule = get_day_schedule()

    for event_name, start_time, end_time in schedule:
        event_label = tk.Label(day_view_frame, text=f"{event_name}: {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}")
        event_label.pack()

# Function to get the schedule for the current day from the stored meeting data
def get_day_schedule():
    today = datetime.date.today()
    schedule = []
    for meeting_datetime, meeting_reminder, link_url in meeting_reminders:
        if meeting_datetime.date() == today:
            event_name = meeting_reminder.split(" for ")[1].split(" at ")[0]
            start_time = meeting_datetime
            end_time = start_time + datetime.timedelta(minutes=60)  # Assuming meetings are 1 hour long
            schedule.append((event_name, start_time, end_time))
    return schedule

# Create the main application window
app = tk.Tk()
app.title("Zinks")

# Create a frame for the toolbar
toolbar_frame = ttk.Frame(app)
toolbar_frame.pack(side=tk.TOP, fill=tk.X)

# Create a "File" button on the toolbar
file_button = ttk.Button(toolbar_frame, text="File", command=open_settings_dialog)
file_button.pack(side=tk.LEFT)

# Create a label and entries for adding hyperlinks
link_name_label = tk.Label(app, text="Link Name:")
link_name_label.pack()
link_name_entry = tk.Entry(app, width=40)
link_name_entry.pack()

link_url_label = tk.Label(app, text="Hyperlink URL:")
link_url_label.pack()
link_url_entry = tk.Entry(app, width=40)
link_url_entry.pack()

# Create a button to add hyperlinks and meeting reminders
add_button = tk.Button(app, text="Add Hyperlink with Reminder", command=add_hyperlink_with_reminder)
add_button.pack()

# Create a listbox to display added hyperlinks
hyperlink_listbox = tk.Listbox(app, width=40)
hyperlink_listbox.pack()

# Create a button to open selected hyperlink
open_button = tk.Button(app, text="Open Hyperlink", command=open_hyperlink)
open_button.pack()

# Create a list to store meeting reminders (datetime, reminder_message, link_url)
meeting_reminders = []

# Load meeting data on startup
load_meeting_data()

# Check for meeting reminders periodically
app.after(1000, check_meeting_reminders)

# Create a button to open the day view calendar
day_view_button = tk.Button(app, text="Day View Calendar", command=display_day_view_calendar)
day_view_button.pack()

# Start the application main loop
app.mainloop()
