from tkinter import *
import pandas as pd
import requests
import urllib
import openpyxl
import ast
import re
from tkinter import messagebox
import datetime

data = pd.DataFrame(columns=["Start Date", "End Date", "Location"])
'''
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
entry_one = None
entry_two = None
entry_three = None

def setup_first_two_questions():
    global entry_one, entry_two
    Label(master, text="Please enter dates as mm/dd/yyyy").pack(pady=5)
    Label(master, text="What is the first day of your travel?").pack(pady=3)
    
    entry_one = Entry(master)
    entry_one.pack(pady=3)

    Label(master, text="What is the last day of your travel?").pack(pady=3)
    entry_two = Entry(master)
    entry_two.pack(pady=3)

    entry_one.bind('<Return>', lambda event: callback())
    entry_two.bind('<Return>', lambda event: callback())
    
    Button(master, text="OK", width=10, command=callback).pack(pady=5)

def check_dates():
    if submit_date(entry_one) and submit_date(entry_two):
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
    if entry_one.get() and entry_two.get():
        for widget in master.winfo_children():
            widget.pack_forget()
        show_third_question()
        Button(master, text="OK", width=10, command=final_callback).pack(pady=5)

def final_callback():
    global data
    first_answer = entry_one.get()
    second_answer = entry_two.get()
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
    
    call_gsa_api(city, state)

# Call the GSA API
def call_gsa_api(city, state):
    global data
    base_url = "https://api.gsa.gov"
    api_key = ""  # Insert your API key here

    endpoint = f"/travel/perdiem/v2/rates/city/{urllib.parse.quote(city)}/state/{urllib.parse.quote(state)}/year/2025"
    
    url = f"{base_url}{endpoint}?api_key={urllib.parse.quote(api_key)}"
    
    print(url)

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(data)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

setup_first_two_questions()
master.mainloop()
'''

data
base_url = "https://api.gsa.gov"
api_key = ""  # Insert your API key here

endpoint = f"/travel/perdiem/v2/rates/city/Chicago/state/IL/year/2025"
    
url = f"{base_url}{endpoint}?api_key={urllib.parse.quote(api_key)}"
    
print(url)

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    print(data)
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")


df = pd.DataFrame(data['rates'])

df['rate'] = df['rate'].astype(str)

df = df['rate'].str.split('}', expand=True)

df = df.drop(df.columns[[12, 14]], axis=1)

df.columns = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Rest']

df[['Blank', 'Meals', 'Zip', 'County', 'City', 'Standard Rate']] = df['Rest'].str.split(',', expand=True)

df = df.drop('Blank', axis=1)

# Split Meals
split_meals = df['Meals'].str.split("'meals'", expand=True)
split_meals = split_meals[1].str.split(":", expand=True)
split_meals = split_meals[1].str.split(',', expand=True)
split_meals = split_meals.iloc[:, :1]

#Get just city names
split_city = df['City'].str.split("'city'", expand=True)
split_city = split_city[1].str.split(",", expand=True)
split_city[0] = split_city[0].str.strip("': '")
split_city = split_city.iloc[:, :1]

# Get the year. Could potentially be changed to just a static variable for the year
split_year = df['Standard Rate'].str.split("'standardRate'", expand=True)
split_year = split_year[1].str.split(",", expand=True)
split_year[0] = split_year[0].str.strip("': '")
split_year = split_year.iloc[:, :1]

# Removes a string ahead of the data in column 0 to make it easier to parse
complete_split = pd.DataFrame()
#value_to_remove = "[{'oconusInfo': None, 'rate': [{'months': {'month': ["
#df['January'] = df['January'].replace(value_to_remove, '')
complete_split = df

df.to_excel("df.xlsx")

# Get the housing per diem for just January because it has a different layout than every other month
split_all = df['January'].str.split("'value'", expand=True)
split_all = split_all.drop(split_all.columns[0], axis=1)
split_all = split_all[1].str.split(",", expand=True)
split_all[0] = split_all[0].str.strip(": ")
split_all = split_all.iloc[:, :1]
complete_split[0] = split_all

# Get the housing per diem for every other month using a loop
i = 1
while i < 12:
  split_all = df[i].str.split("'value'", expand=True)
  split_all = split_all.drop(split_all.columns[0], axis=1)
  split_all = split_all[1].str.split(",", expand=True)
  split_all[0] = split_all[0].str.strip(": ")
  split_all = split_all.iloc[:, :1]
  complete_split[i] = split_all
  i += 1

# Add columns names and meals, the actual city name, the city as shown by the GSA, the state given by the GSA, the year given by the GSA, and
# puts it into an excel sheet
complete_split = complete_split.iloc[:, :12]

complete_split.columns = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
complete_split['MIE'] = split_meals
#complete_split['City'] = city
complete_split['GSA City'] = split_city
complete_split['Year'] = split_year

df.to_excel('df.xlsx', index=False)