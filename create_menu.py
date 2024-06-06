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
def get_today():
    today = datetime.now()
    return today

# Function to read WordPress credentials from a file
def read_wp_credentials(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
        username = lines[0].strip().split(': ')[1]
        password = lines[1].strip().split(': ')[1]
    return username, password

# Function to check for common words between two strings
def has_common_word(str1, str2):
    set1 = set(str1.lower().split())
    set2 = set(str2.lower().split())
    return not set1.isdisjoint(set2)

# Function to ensure no common words for a day and its neighbors
def no_common_words_around(day_index, breakfast_items, dinner_items):
    if has_common_word(breakfast_items[day_index], dinner_items[day_index]):
        return False
    if day_index > 0 and has_common_word(breakfast_items[day_index], dinner_items[day_index - 1]):
        return False
    if day_index < len(breakfast_items) - 1 and has_common_word(breakfast_items[day_index], dinner_items[day_index + 1]):
        return False
    return True

# Function to check for no consecutive duplicate items
def no_consecutive_duplicates(items):
    for i in range(1, len(items)):
        if items[i] == items[i - 1]:
            return False
    return True

# Read CSV files into dataframes
main_items_df = read_csv('main_items.csv')
side_items_df = read_csv('side_items.csv')
breakfast_items_df = read_csv('breakfast_items.csv')

# Extract items and weights into lists
main_items = main_items_df['Item'].tolist()
main_weights = main_items_df['Weight'].tolist()
side_items = side_items_df['Item'].tolist()
side_weights = side_items_df['Weight'].tolist()
breakfast_items = breakfast_items_df['Item'].tolist()
breakfast_weights = breakfast_items_df['Weight'].tolist()

# Randomly select 7 unique items from the main items list based on weights
selected_main_items = random.choices(main_items, weights=main_weights, k=7)
selected_main_items = list(set(selected_main_items))  # Ensure unique items

# Ensure we have exactly 7 items by adding more if needed
while len(selected_main_items) < 7:
    additional_items = random.choices(main_items, weights=main_weights, k=7 - len(selected_main_items))
    selected_main_items.extend(additional_items)
    selected_main_items = list(set(selected_main_items))

# Initialize breakfast and dinner items lists
selected_breakfast_items = []
paired_dinner_items = []
used_sides = set()

# Pair items with sides if necessary and prepare dinner items
for item in selected_main_items:
    if needs_side(item):
        available_sides = list(set(side_items) - used_sides)
        if available_sides:
            side_item = random.choices(available_sides, weights=[side_weights[side_items.index(s)] for s in available_sides], k=1)[0]
            used_sides.add(side_item)
            paired_dinner_items.append(f"{item} ({side_item})")
        else:
            paired_dinner_items.append(item)  # No available side items left
    else:
        paired_dinner_items.append(item)

# Select breakfast items ensuring no common words with corresponding dinner and its neighbors
# and no consecutive duplicate items
MAX_RETRIES = 10
for i in range(7):
    retries = 0
    while retries < MAX_RETRIES:
        breakfast_item = random.choices(breakfast_items, weights=breakfast_weights, k=1)[0]
        if len(selected_breakfast_items) > i:
            selected_breakfast_items[i] = breakfast_item
        else:
            selected_breakfast_items.append(breakfast_item)
        if no_common_words_around(i, selected_breakfast_items, paired_dinner_items) and no_consecutive_duplicates(selected_breakfast_items):
            break
        retries += 1
    if retries == MAX_RETRIES:
        selected_breakfast_items[i] = "Surprise Breakfast"

# Ensure no consecutive duplicate dinner items
for i in range(7):
    retries = 0
    while retries < MAX_RETRIES:
        dinner_item = paired_dinner_items[i]
        if i > 0 and paired_dinner_items[i] == paired_dinner_items[i - 1]:
            additional_items = random.choices(main_items, weights=main_weights, k=1)
            for item in additional_items:
                if item not in paired_dinner_items:
                    if needs_side(item):
                        available_sides = list(set(side_items) - used_sides)
                        if available_sides:
                            side_item = random.choices(available_sides, weights=[side_weights[side_items.index(s)] for s in available_sides], k=1)[0]
                            used_sides.add(side_item)
                            dinner_item = f"{item} ({side_item})"
                        else:
                            dinner_item = item  # No available side items left
                    else:
                        dinner_item = item
        if no_consecutive_duplicates(paired_dinner_items):
            paired_dinner_items[i] = dinner_item
            break
        retries += 1
    if retries == MAX_RETRIES:
        paired_dinner_items[i] = "Surprise Dinner"

# Calculate the dates starting from the next day
next_day = get_today()
dates = [next_day + timedelta(days=i) for i in range(7)]

# Format the dates and days of the week
days_of_week = [date.strftime('%A') for date in dates]
days_with_dates = [f"{date.strftime('%d-%m-%Y')} ({day})" for day, date in zip(days_of_week, dates)]

# Combine days, dates, and paired items into a list of tuples
menu = list(zip(days_with_dates, selected_breakfast_items, paired_dinner_items))

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
    # Read WordPress credentials
    wp_user, wp_password = read_wp_credentials('wp_config.txt')

    # WordPress REST API Credentials and URL
    wp_url = "https://thundyill.com/wp-json/wp/v2/pages/899"

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
