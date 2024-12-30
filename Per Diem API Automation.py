from tkinter import *
import pandas as pd
import requests
import urllib
import openpyxl
import ast
import re
import datetime
import calendar
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import shutil
import os

data = pd.DataFrame(columns=["Start Date", "End Date", "Location"])

master = Tk()
master.title("")

# Center the window on the screen
window_width = 300
window_height = 175
screen_width = master.winfo_screenwidth()
screen_height = master.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
master.geometry(f"{window_width}x{window_height}+{x}+{y}")
start_date = None
end_date = None
entry_three = None

def setup_first_two_questions():
    global start_date, end_date
    Label(master, text="Please enter dates as mm/dd/yyyy").pack(pady=5)
    Label(master, text="What is the first day of your travel?").pack(pady=3)

    start_date = Entry(master)
    start_date.pack(pady=3)

    Label(master, text="What is the last day of your travel?").pack(pady=3)
    end_date = Entry(master)
    end_date.pack(pady=3)

    start_date.bind('<Return>', lambda event: callback())
    end_date.bind('<Return>', lambda event: callback())

    Button(master, text="OK", width=10, command=callback).pack(pady=5)

def check_dates():
    if submit_date(start_date) and submit_date(end_date):
        for widget in master.winfo_children():
            widget.pack_forget()
        show_third_question()

def show_third_question():
    global entry_three
    Label(master, text="Where are you traveling?").pack(pady=3)
    entry_three = Entry(master)
    entry_three.pack(pady=3)

    entry_three.bind('<Return>', lambda event: final_callback())
    entry_three.focus_set()

def callback():
    if start_date.get() and end_date.get():
        for widget in master.winfo_children():
            widget.pack_forget()
        show_third_question()
        Button(master, text="OK", width=10, command=final_callback).pack(pady=5)

def final_callback():
    global data
    first_answer = start_date.get()
    second_answer = end_date.get()
    third_answer = entry_three.get()

    if first_answer and second_answer and third_answer:
        new_entry = pd.DataFrame({
            "Start Date": [first_answer], 
            "End Date": [second_answer], 
            "Location": [third_answer]
        })
        data = pd.concat([data, new_entry], ignore_index=True)
        extract_city_state(third_answer) 
    master.destroy()

def extract_city_state(location):
    # Split the location into city and state
    city_state = location.split(",")

    if len(city_state) != 2:
        print("Please enter both city and state separated by a comma.")
        return

    # Extract city and state
    city = city_state[0].strip()
    state = city_state[1].strip()

    
data
base_url = "https://api.gsa.gov"
api_key = ""  # Insert your API key here

endpoint = f"/travel/perdiem/v2/rates/city/" + city + "/state/"+ state +"/year/2025"

url = f"{base_url}{endpoint}?api_key={urllib.parse.quote(api_key)}"

print(url)

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    print(data)
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

test = pd.DataFrame(data)
test.to_excel("test.xlsx")

df = pd.DataFrame(data['rates'])

df['rate'] = df['rate'].astype(str)

df = df['rate'].str.split('}', expand=True)

df = df.drop(df.columns[[12, 14]], axis=1)

df.columns = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December', 'Rest']

df[['Blank', 'Meals', 'Zip', 'County', 'City', 'Standard Rate']] = df['Rest'].str.split(',', expand=True)

df = df.drop('Blank', axis=1)

# Split Meals
split_meals = df['Meals'].str.split("'meals'", expand=True)
split_meals = split_meals[1].str.split(":", expand=True)
split_meals = split_meals[1].str.split(',', expand=True)
split_meals = split_meals.iloc[:, :1]

# Get just city names
split_city = df['City'].str.split("'city'", expand=True)
split_city = split_city[1].str.split(",", expand=True)
split_city[0] = split_city[0].str.strip("': '")
split_city = split_city.iloc[:, :1]

# Get the year. Could potentially be changed to just a static variable for the year
split_standard_rate = pd.DataFrame()
split_standard_rate = df['Standard Rate'].str.split("'standardRate'", expand=True)
split_standard_rate = split_standard_rate[1].str.split(",", expand=True)
split_standard_rate[0] = split_standard_rate[0].str.strip("': '")
split_standard_rate = split_standard_rate.iloc[:, :1]

# Removes a string ahead of the data in column 0 to make it easier to parse
complete_split = pd.DataFrame()
# value_to_remove = "[{'oconusInfo': None, 'rate': [{'months': {'month': ["
# df['January'] = df['January'].replace(value_to_remove, '')
complete_split = df

df.to_excel("df.xlsx")

# Get the housing per diem for just January because it has a different layout than every other month
split_all = df['January'].str.split("'value'", expand=True)
split_all = split_all.drop(split_all.columns[0], axis=1)
split_all = split_all[1].str.split(",", expand=True)
split_all[0] = split_all[0].str.strip(": ")
split_all = split_all.iloc[:, :1]
complete_split['January'] = split_all

complete_split.to_excel("complete_split.xlsx")

# Get the housing per diem for every other month using a loop
i = 1
while i < 12:
#    split_all = df[i].str.split("'value'", expand=True)
    split_all = df.iloc[:, i].str.split("'value'", expand=True)
    split_all = split_all.drop(split_all.columns[0], axis=1)
    split_all = split_all[1].str.split(",", expand=True)
    split_all[0] = split_all[0].str.strip(": ")
    split_all = split_all.iloc[:, :1]
    complete_split[i] = split_all
    i += 1
#complete_split.to_excel('complete_split.xlsx', index=False)

# Add columns names and meals, the actual city name, the city as shown by the GSA, the state given by the GSA, the year given by the GSA, and
# puts it into an excel sheet
df.iloc[:, 1:12] = df.iloc[:, 18:29].values
complete_split = complete_split.iloc[:, :12] # Need to get the actual numbers from Feb - December (18-29) and replace 1-11

complete_split.columns = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                          'October', 'November', 'December']
complete_split['MIE'] = split_meals
# complete_split['City'] = city
complete_split['GSA City'] = split_city
complete_split['StandardRate'] = split_standard_rate

complete_split.to_excel('complete_split.xlsx', index=False)

df = complete_split

# START TO SPLIT THE DATES HERE
#start_date = "06/22/2025"
#end_date = "07/25/2025"

# Create function to find single day events
def check_same_day(start_date, end_date):
    if start_date == end_date:
        df['Same Day'] = True
        end_date_cost = 0
    else:
        df['Same Day'] = False

# Make dates into datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Creates a function that gives how many days are spent in each month if the dates are in multiple separate months
def days_in_month(year, month):
    """Returns the number of days in the given month and year."""
    return calendar.monthrange(year, month)[1]
def days_spent_in_months(start_date, end_date):
    # Ensure start_date is before end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    # Initialize variables to store days spent in each month
    days_in_first_month = 0
    days_in_last_month = 0
    full_months = 0

    # Calculate days spent in the first month (from start_date to the end of that month)
    start_month_days = days_in_month(start_date.year, start_date.month)
    days_to_add = 1
    days_in_first_month = pd.Timedelta(days=(start_month_days - start_date.day)) + pd.Timedelta(days=days_to_add)


    # Calculate days spent in the last month (from the first of the month to end_date)
    days_in_last_month = end_date.day

    return days_in_first_month, days_in_last_month

# Determines if dates are in the same month
def same_month_pd(start_date, end_date):
    return (start_date.year == end_date.year) & (start_date.month == end_date.month)

# Calls the function to determine how many days if the two are in fact not in the same month
if same_month_pd(start_date, end_date) == False:
    days_in_first_month, days_in_last_month = days_spent_in_months(start_date, end_date)
else:
    days_in_first_month, days_in_last_month = days_spent_in_months(start_date, end_date)

# If the days are in the same month, determines how many days are spent at an event
if same_month_pd(start_date, end_date) == True:
    days_to_add = 1
    number_of_days = end_date - start_date + pd.Timedelta(days = days_to_add)
    print(number_of_days)

# Get start and end month names
start_month_name = start_date.strftime("%B")
end_month_name = end_date.strftime("%B")

'''
if start_month_name in df.columns:
    # Multiply the value of the housing per diem for the specified month of that column by the number of days
    days_in_first_month = days_in_first_month.days
    days_in_first_month = int(days_in_first_month)
    start_month_per_diem_cost = df[start_month_name].iloc(0)
    start_month_per_diem_cost = int(start_month_per_diem_cost)
    start_month_cost = start_month_per_diem_cost * days_in_first_month
'''

if start_month_name in df.columns:
    # Extract the value for the first row of the specified month column
    start_month_per_diem_cost = df[start_month_name].iloc[0]
    start_month_per_diem_cost = int(start_month_per_diem_cost)
    days_in_first_month = days_in_first_month.days  # Convert TimeDelta days to an int
    start_month_cost = start_month_per_diem_cost * (days_in_first_month + 2)
    end_month_cost = 0

if same_month_pd(start_date, end_date) == False:
    if end_month_name in df.columns:
        end_month_per_diem_cost = df[end_month_name].iloc[0]
        end_month_per_diem_cost = int(end_month_per_diem_cost)
        end_month_cost = end_month_per_diem_cost * (days_in_last_month + 1) + (start_month_per_diem_cost + 1)

total_housing_cost = start_month_cost + end_month_cost

df['Housing'] = total_housing_cost

if same_month_pd(start_date, end_date) == True:
    total_days = days_in_first_month
else:
    total_days = days_in_first_month + days_in_last_month

mie = df['MIE']
mie = int(mie)
total_mie = mie * total_days + (.75*(2*mie))
print(total_mie)

total_cost = total_housing_cost + total_mie

end_df = pd.DataFrame()
end_df['Housing'] = total_housing_cost
end_df['Total MIE'] = total_mie
end_df['Total Cost'] = total_cost


# Function to create the pop-up with multiple values displayed and download option
def create_popup_with_values_and_download(values_to_display, existing_file_path):
    # Create a new tkinter window (root)
    root = tk.Tk()

    # Hide the main window (we only want the pop-up)
    root.withdraw()

    # Create a new top-level window for the pop-up
    popup = tk.Toplevel(root)
    popup.title("View Values and Download File")

    # Labels and Text widget to display multiple values
    label = tk.Label(popup, text="Values to Display:")
    label.pack()

    # Create a Text widget for displaying multiple values (read-only)
    text_box = tk.Text(popup, height=10, width=50)
    text_box.pack()

    # Insert the multiple values into the text box (convert all to string)
    text_box.insert(tk.END, "\n".join(map(str, values_to_display)))

    # Make the text box read-only (optional)
    text_box.config(state=tk.DISABLED)

    # Function to process the user's choice and save the file
    def process_and_download():
        # Check if the existing file exists
        if not os.path.exists(existing_file_path):
            messagebox.showerror("Error", f"The source file '{existing_file_path}' does not exist.")
            return

        # Move the file to a temporary location where the user can download it
        temp_dir = tempfile.gettempdir()  # Get the system's temporary directory
        temp_file_path = os.path.join(temp_dir, os.path.basename(existing_file_path))

        try:
            # Move (or copy) the file to the temporary directory
            shutil.copy(existing_file_path, temp_file_path)

            # Ask the user where to save the file using file dialog
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                     filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
                                                     initialfile=os.path.basename(existing_file_path),
                                                     title="Save Excel File As")
            if file_path:
                # Copy the file from the temp location to the user's selected path
                shutil.move(temp_file_path, file_path)
                messagebox.showinfo("Success", f"Excel file has been saved at {file_path}")
            else:
                # If user cancels, delete the temporary file
                os.remove(temp_file_path)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    # Button to process and download the Excel file
    download_button = tk.Button(popup, text="Download Excel File", command=process_and_download)
    download_button.pack()

    # Button to cancel the pop-up
    cancel_button = tk.Button(popup, text="Cancel", command=popup.destroy)
    cancel_button.pack()

    # Run the Tkinter event loop
    root.mainloop()

# Example usage
total_housing_cost = str(total_housing_cost)
total_mie = str(total_mie)
total_cost = str(total_cost)
values_to_display = [
    "Total Housing Cost: " + total_housing_cost,
    "Total MIE Cost: " + total_mie,
    "Total Cost: " + total_cost
]  # These are the multiple values you want to display in the pop-up
existing_file_path = "end_df.xlsx"  # Path to the existing file
create_popup_with_values_and_download(values_to_display, existing_file_path)


#Needs work for making downloading the excel file work
