import os
import smartsheet
import openai
import sys
import json
import time

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SMARTSHEET_API_KEY = os.getenv("SMARTSHEET_API_KEY")

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Initialize Smartsheet client
smart = smartsheet.Smartsheet(SMARTSHEET_API_KEY)
smart.errors_as_exceptions(True)

def generate_columns(sheet_type):
    """
    Uses OpenAI to generate a list of dictionaries representing column definitions.
    """
    prompt = f"""
    You are a Python code generator that creates structured column definitions for a Smartsheet sheet.

    Think of what column headers would be useful for a {sheet_type} sheet. 

    Generate a **Python list of dictionaries**, where each dictionary represents a column.

    Each column must have:
    - "title": The column name.
    - "type": The column type, chosen from these valid Smartsheet types:
      - "TEXT_NUMBER"
      - "DATE"
      - "DATETIME"
      - "CONTACT_LIST"
      - "CHECKBOX"
      - "PICKLIST"
      - "DURATION"
      - "PREDECESSOR"
      - "ABSTRACT_DATETIME"
     
    Return only a valid Python list of dictionaries—**no extra text or explanations**. This output will be read by Python, so anything other than a valid Python dictionary will break the code.

    **Return only the Python list of dictionaries, without explanations.**
    """

    #removed from above, susspecting causing errors 
    # - "MULTI_CONTACT_LIST"
    # - "MULTI_PICKLIST"


    print(prompt)
    print(" ")
    print(" ")
    print("Pinging OpenAI...")

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )

    column_text = response.choices[0].message.content

    try:
        # Convert OpenAI response from string to Python list of dictionaries
        columns = eval(column_text)  # Convert text into a Python list
        if isinstance(columns, list):  # Ensure the output is a list
            return columns
        else:
            print("Error: OpenAI response is not a list.")
            return []
    except Exception as e:
        print(f"Error converting OpenAI response to a dictionary: {e}")
        return []

def fill_grid(sheet_id, column_dict, user_prompt):
    """
    Generates structured data using OpenAI and writes it to a Smartsheet sheet.
    """
    # Construct the OpenAI prompt
    ai_prompt = f"""
    You are a Python code generator that creates structured Python dictionaries. Follow these instructions carefully:

    1. Input: You will receive a **Python dictionary** where the keys represent **column names** in a Smartsheet.  
    2. Output: You must generate a new Python dictionary that:
       - Contains multiple **example rows** of data. at least 10 rows unless otherwise specified.
       - Uses the **same keys** as provided in the input dictionary.
       - Populates each key with **realistic example values** based on the column name and User Description. 
       - If the key represents a date, Must be formatted as YYYY-MM-DD (ISO 8601).
       - If the key represents a CONTACT_LIST, the value must be a valid email address (e.g., "johndoe@example.com") instead of a plain name.
       - If the key represents a DURATION: Must be an integer representing the number of days (e.g., 30, not "30 days").
       - If the key represents a Percentages (e.g., % Complete): Must be an integer between 0 and 100 (e.g., 75, not "75%").
       - **Outputs only valid Python code—no explanations, comments, or extra text.**

    Column Dictionary:
    {json.dumps(column_dict, indent=4)}

    User Description of Data:
    "{user_prompt}"

    Return a valid Python list of dictionaries only.
    """

   
    print(ai_prompt)
    print(" ")
    print(" ")
    print("Pinging OpenAI...")

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an AI that generates structured data."},
                  {"role": "user", "content": ai_prompt}],
        temperature=0.7
    )

    ai_output = response.choices[0].message.content.strip()

    print("Received AI response:")
    print(ai_output)

    # Convert AI output to a Python dictionary
    try:
        generated_data = eval(ai_output)  # Ensure safety with trusted API responses
        if not isinstance(generated_data, list):
            raise ValueError("Generated data is not in the expected format.")
    except Exception as e:
        print(f"Error parsing AI response: {e}")
        return

    # Write data to Smartsheet
    add_rows_to_smartsheet(sheet_id, generated_data)

def add_rows_to_smartsheet(sheet_id, row_data):
    rows = []
    for row in row_data:
        new_row = smartsheet.models.Row()
        for col_name, value in row.items():
            if value is None or value == "":  # Skip empty values
                print(f"Skipping empty value for column: {col_name}")
                continue

            cell = smartsheet.models.Cell()
            cell.column_id = get_column_id(sheet_id, col_name)
            cell.value = value
            new_row.cells.append(cell)

        if new_row.cells:  # Only add non-empty rows
            rows.append(new_row)

    if rows:
        smart.Sheets.add_rows(sheet_id, rows)
    else:
        print("No valid rows to add.")
   
def get_column_id(sheet_id, column_name):
    """
    Retrieves the column ID for a given column name in the Smartsheet sheet.
    """
    sheet = smart.Sheets.get_sheet(sheet_id)
    for column in sheet.columns:
        if column.title == column_name:
            return column.id
    raise ValueError(f"Column '{column_name}' not found in the sheet.")

def main():
    try:
        # Warning sheet clear
        print("***")
        print("Warning, running this app will clear all data in your sheet")
        print("***")

        # Prompt user for Sheet ID
        sheet_id = input("Please enter the Smartsheet Sheet ID: ")

        # Fetch the sheet to get column details
        print(f"Fetching details for sheet ID: {sheet_id}")
        sheet = smart.Sheets.get_sheet(sheet_id)
        print(f"Sheet '{sheet.name}' retrieved successfully.")

        # **Step 1: Delete all columns except the primary column**
        print("Deleting all columns except the primary column...")
        for column in sheet.columns:
            if column.primary:
                print(f"Skipping primary column '{column.title}' (ID: {column.id})")
                continue  # Skip deleting the primary column
            print(f"Deleting column '{column.title}' (ID: {column.id})")
            smart.Sheets.delete_column(sheet_id, column.id)

        # Fetch the sheet again to confirm all columns except the primary column are deleted
        sheet = smart.Sheets.get_sheet(sheet_id)

        # **Step 2: Delete all cell data
        sheet = smart.Sheets.get_sheet(sheet_id)

        print(f"checking cells on sheet: '{sheet.name}' with {len(sheet.rows)} rows.")

        # Collect all row IDs
        row_ids = [row.id for row in sheet.rows]

        # set Perams
        batch_size=100
        sleep_duration=1

        # Delete rows in batches
        for i in range(0, len(row_ids), batch_size):
            batch = row_ids[i:i + batch_size]
            print(f"Deleting rows {i + 1} to {i + len(batch)}...")
            smart.Sheets.delete_rows(sheet_id, batch)
            print(f"Deleted rows {i + 1} to {i + len(batch)}.")
            time.sleep(sleep_duration)  # Pause to respect rate limits

        print("All rows have been successfully deleted.")

        # **Step 3: Get new columns from OpenAI**
        sheet_type = input("Enter the type of sheet you want to update: ")
        NEW_COLUMNS = generate_columns(sheet_type)

        # Debugging: Print the generated columns
        print("Generated Columns from OpenAI:", json.dumps(NEW_COLUMNS, indent=4))

        # **Step 4: Create new columns in Smartsheet**
        print("Creating new columns...")
        column_objects = []
        for c in NEW_COLUMNS:
            column = smart.models.Column()
            column.title = c["title"]
            print("Adding Coulumn: " + c["title"])
            column.type = c["type"]
            column.index = 1 
            column_objects.append(column)

        # Send request to Smartsheet
        response = smart.Sheets.add_columns(sheet_id, column_objects)

        if response.message == "SUCCESS":
            print("New columns added successfully!")
        else:
            print(f"Failed to add new columns: {response}")

        # Ask the user for grid data description
        user_input = input("What data would you like to fill the grid with? ")

        fill_grid(sheet_id, NEW_COLUMNS, user_input)


    except smartsheet.exceptions.ApiError as e:
        print(f"Smartsheet API error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()