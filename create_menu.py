import pandas as pd
import random
from jinja2 import Template
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
import argparse

# Function to read CSV files
def read_csv(file_name):
    return pd.read_csv(file_name)

# Function to check if an item should be paired with a side
def needs_side(item):
    return 'side' in item.lower()

# Function to get the next day from the current date
def get_next_day():
    today = datetime.now()
    return today + timedelta(days=1)

# Read CSV files into dataframes
main_items_df = read_csv('main_items.csv')
side_items_df = read_csv('side_items.csv')

# Extract items and weights into lists
main_items = main_items_df['Item'].tolist()
main_weights = main_items_df['Weight'].tolist()
side_items = side_items_df['Item'].tolist()
side_weights = side_items_df['Weight'].tolist()

# Randomly select 7 unique items from the main items list based on weights
selected_main_items = random.choices(main_items, weights=main_weights, k=7)
selected_main_items = list(set(selected_main_items))  # Ensure unique items

# Ensure we have exactly 7 items by adding more if needed
while len(selected_main_items) < 7:
    additional_items = random.choices(main_items, weights=main_weights, k=7 - len(selected_main_items))
    selected_main_items.extend(additional_items)
    selected_main_items = list(set(selected_main_items))

# Pair items with sides if necessary
paired_items = []
used_sides = set()

for item in selected_main_items:
    if needs_side(item):
        available_sides = list(set(side_items) - used_sides)
        if available_sides:
            side_item = random.choices(available_sides, weights=[side_weights[side_items.index(s)] for s in available_sides], k=1)[0]
            used_sides.add(side_item)
            paired_items.append(f"{item} ({side_item})")
        else:
            paired_items.append(item)  # No available side items left
    else:
        paired_items.append(item)

# Calculate the dates starting from the next day
next_day = get_next_day()
dates = [next_day + timedelta(days=i) for i in range(7)]

# Format the dates and days of the week
days_of_week = [date.strftime('%A') for date in dates]
days_with_dates = [f"{date.strftime('%d-%m-%Y')} ({day})" for day, date in zip(days_of_week, dates)]

# Combine days, dates, and paired items into a list of tuples
menu = list(zip(days_with_dates, paired_items))

# Read the HTML template
with open('template.html', 'r') as file:
    template = Template(file.read())

# Render the HTML with the menu
html_content = template.render(menu=menu)

# Write the generated HTML to a file
with open('weekly_menu.html', 'w') as file:
    file.write(html_content)

print("Weekly menu generated and saved as 'weekly_menu.html'.")

# Command-line argument parsing
parser = argparse.ArgumentParser(description="Generate weekly menu and optionally update WordPress page.")
parser.add_argument('--update_wp', action='store_true', help="Update the WordPress page with the generated menu")

args = parser.parse_args()

if args.update_wp:
    # WordPress REST API Credentials and URL
    wp_url = "https://thundyill.com/wp-json/wp/v2/pages/899"
    wp_user = "bot_user"
    wp_password = 'Best Password Here'

    # Update WordPress Page
    data = {
        'content': html_content
    }

    response = requests.post(wp_url, json=data, auth=HTTPBasicAuth(wp_user, wp_password))

    if response.status_code == 200:
        print("WordPress page updated successfully.")
    else:
        print("Failed to update WordPress page.")
        print("Response:", response.content)
