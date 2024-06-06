# Weekly Menu Generator

This project generates a weekly menu in an HTML format and optionally updates a WordPress page with the generated menu. The menu items are selected based on their weights from CSV files and paired with side items if necessary. It ensures that no two consecutive days have the same breakfast and/or dinner items.

## Features

- Randomly select 7 unique menu items from a list based on weight.
- Pair menu items with side items if specified.
- Ensure no common words between breakfast and dinner items for the same day and adjacent days.
- Ensure no two consecutive days have the same breakfast and/or dinner items.
- Generate an HTML file displaying the weekly menu.
- Optionally update a WordPress page with the generated menu.

## Prerequisites

- Python 3.x
- Required Python packages (listed in `requirements.txt`)

## Installation

1. **Clone the repository**:

    ```sh
    git clone https://github.com/yourusername/weekly-menu-generator.git
    cd weekly-menu-generator
    ```

2. **Install the required packages**:

    ```sh
    pip install -r requirements.txt
    ```

3. **Prepare the CSV files**:

    Ensure you have the following CSV files in the project directory:

    - `main_items.csv`
    - `side_items.csv`
    - `breakfast_items.csv`

4. **Prepare the HTML template**:

    Ensure you have a file named `template.html`.

5. **Prepare the WordPress configuration file**:

    Create a file named `wp_config.txt` with the following content:

    ```txt
    username: your_username
    password: your_application_password
    ```

## Usage

1. **Generate the weekly menu**:

    ```sh
    python generate_menu.py
    ```

    This will generate a `weekly_menu.html` file in the project directory.

2. **Update the WordPress page**:

    To update the WordPress page with the generated menu, use the `--update_wp` flag:

    ```sh
    python generate_menu.py --update_wp
    ```

    Ensure that the `wp_url`, `wp_user`, and `wp_password` variables in the script are correctly set.

## Script Overview

The script performs the following tasks:

1. Reads menu, side items, and breakfast items from CSV files.
2. Selects 7 unique menu items based on weight.
3. Pairs items with side items if specified.
4. Ensures no common words between breakfast and dinner items for the same day and adjacent days.
5. Ensures no two consecutive days have the same breakfast and/or dinner items.
6. Generates an HTML file displaying the weekly menu.
7. Optionally updates a WordPress page with the generated content.
