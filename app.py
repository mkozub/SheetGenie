import os
import json
import requests
from flask import Flask, render_template, request, jsonify
import smartsheet
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SMARTSHEET_API_KEY = os.getenv("SMARTSHEET_API_KEY")

# Initialize Smartsheet client with SDK 3.0
smartsheet_client = smartsheet.Smartsheet(SMARTSHEET_API_KEY)

@app.route('/')
def index():
    print("Index route called")
    return render_template('index.html')

@app.route('/diagnostic')
def diagnostic():
    print("Diagnostic page requested")
    return render_template('diagnostic.html')

@app.route('/test')
def test():
    print("Test route called")
    return jsonify({"message": "API is working!"})

@app.route('/verify_sheet', methods=['POST'])
def verify_sheet():
    print("Verify sheet endpoint called")
    sheet_id = request.json.get('sheet_id')
    print(f"Received sheet_id: {sheet_id}")
    
    try:
        # Attempt to get sheet information to verify it exists using SDK 3.0
        print("Attempting to get sheet from Smartsheet API")
        sheet = smartsheet_client.Sheets.get_sheet(sheet_id)
        print(f"Sheet found: {sheet.name}")
        return jsonify({
            'success': True,
            'sheet_name': sheet.name
        })
    except Exception as e:
        print(f"Error verifying sheet: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/generate_columns', methods=['POST'])
def generate_columns():
    sheet_purpose = request.json.get('sheet_purpose')
    
    # OpenAI API URL
    url = "https://api.openai.com/v1/chat/completions"
    
    # Structured prompt for column generation
    prompt = f"""
    You are a Python code generator that creates structured column definitions for a Smartsheet sheet.

    Think of what column headers would be useful for a {sheet_purpose} sheet.

    Generate a Python list of dictionaries, where each dictionary represents a column.

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
      - "ABSTRACT_DATETIME"

    Return only a valid Python list of dictionaries—no extra text or explanations.
    """
    
    # Request payload
    payload = {
        "model": "gpt-4o", # or whichever OpenAI model you prefer
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that generates Python code."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    # Headers with API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    try:
        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        # Extract the generated Python code
        response_data = response.json()
        generated_text = response_data['choices'][0]['message']['content'].strip()
        
        # Clean up the response to ensure it's valid Python
        # This removes any markdown code blocks if present
        if "```python" in generated_text:
            generated_text = generated_text.split("```python")[1].split("```")[0].strip()
        elif "```" in generated_text:
            generated_text = generated_text.split("```")[1].split("```")[0].strip()
            
        # Convert the string to Python object
        columns = eval(generated_text)
        
        return jsonify({
            'success': True,
            'columns': columns
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/push_columns', methods=['POST'])
def push_columns():
    sheet_id = request.json.get('sheet_id')
    columns = request.json.get('columns')
    
    try:
        # Get the sheet to check existing columns
        sheet = smartsheet_client.Sheets.get_sheet(sheet_id)
        
        # Delete all existing columns
        for column in sheet.columns:
            smartsheet_client.Sheets.delete_column(sheet_id, column.id)
        
        # Add new columns
        new_columns = []
        for column_data in columns:
            # Create column object with SDK 3.0
            column_spec = smartsheet.models.Column({
                'title': column_data['title'],
                'type': column_data['type'],
                'index': 0  # Will be auto-indexed when added
            })
            new_columns.append(column_spec)
        
        # Add all columns at once
        added_columns = smartsheet_client.Sheets.add_columns(sheet_id, new_columns)
        
        return jsonify({
            'success': True,
            'message': f"Successfully updated columns for sheet {sheet.name}"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate_data', methods=['POST'])
def generate_data():
    sheet_id = request.json.get('sheet_id')
    columns = request.json.get('columns')
    user_prompt = request.json.get('data_prompt')
    
    # Convert columns list to a simpler format for the prompt
    column_dict = {col['title']: col['type'] for col in columns}
    
    # OpenAI API URL
    url = "https://api.openai.com/v1/chat/completions"
    
    # Structured prompt for data generation
    prompt = f"""
    You are a Python code generator that creates structured Python dictionaries. Follow these instructions carefully:

    1. Input: You will receive a Python dictionary where the keys represent column names in a Smartsheet.  
    2. Output: You must generate a new Python dictionary that:
       - Contains multiple example rows of data. 
       - Uses the same keys as provided in the input dictionary.
       - Populates each key with realistic example values based on the column name and User Description. 
       - If the key represents a date, must be formatted as YYYY-MM-DD (ISO 8601).
       - If the key represents a CONTACT_LIST, the value must be a valid email address (e.g., "johndoe@example.com").
       - If the key represents a DURATION, must be an integer (e.g., 30).
       - If the key represents Percentages, must be an integer between 0 and 100 (e.g., 75).
       - Outputs only valid Python code—no explanations or extra text.
       - Return a minimum of 10 rows of data, unless otherwise specified. More rows is better, the description asks for 'detailed' - Give 20 rows.

    Column Dictionary:
    {json.dumps(column_dict, indent=4)}

    User Description of Data:
    "{user_prompt}"

    Return a valid Python list of dictionaries only.
    """
    
    # Request payload
    payload = {
        "model": "gpt-4o", # or whichever OpenAI model you prefer
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that generates Python code."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    # Headers with API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    try:
        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        # Extract the generated Python code
        response_data = response.json()
        generated_text = response_data['choices'][0]['message']['content'].strip()
        
        # Clean up the response to ensure it's valid Python
        # This removes any markdown code blocks if present
        if "```python" in generated_text:
            generated_text = generated_text.split("```python")[1].split("```")[0].strip()
        elif "```" in generated_text:
            generated_text = generated_text.split("```")[1].split("```")[0].strip()
            
        # Convert the string to Python object
        rows_data = eval(generated_text)
        
        return jsonify({
            'success': True,
            'data': rows_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/push_data', methods=['POST'])
def push_data():
    sheet_id = request.json.get('sheet_id')
    data = request.json.get('data')
    
    try:
        # Get the sheet to identify columns
        sheet = smartsheet_client.Sheets.get_sheet(sheet_id)
        
        # Create a map of column titles to column ids
        column_map = {col.title: col.id for col in sheet.columns}
        
        # Delete existing rows if any
        if sheet.total_row_count > 0:
            # Get all row ids
            row_ids = [row.id for row in sheet.rows]
            # Delete rows in batches of 100 to avoid API limits
            for i in range(0, len(row_ids), 100):
                batch = row_ids[i:i+100]
                smartsheet_client.Sheets.delete_rows(sheet_id, batch)
        
        # Prepare new rows
        new_rows = []
        for row_data in data:
            cells = []
            for col_title, value in row_data.items():
                if col_title in column_map:
                    cell = smartsheet.models.Cell()
                    cell.column_id = column_map[col_title]
                    
                    # Handle different cell types
                    if isinstance(value, bool):
                        cell.value = value
                    elif value is None:
                        cell.value = ""
                    else:
                        cell.value = str(value)
                    
                    cells.append(cell)
            
            # Create a new row with the cells
            new_row = smartsheet.models.Row()
            new_row.to_bottom = True
            new_row.cells = cells
            new_rows.append(new_row)
        
        # Add rows in batches of 100 to avoid API limits
        results = []
        for i in range(0, len(new_rows), 100):
            batch = new_rows[i:i+100]
            result = smartsheet_client.Sheets.add_rows(sheet_id, batch)
            results.append(result)
        
        return jsonify({
            'success': True,
            'message': f"Successfully added {len(new_rows)} rows to the sheet"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting SheetGenie Flask application...")
    print(f"OpenAI API Key configured: {'Yes' if OPENAI_API_KEY else 'No'}")
    print(f"Smartsheet API Key configured: {'Yes' if SMARTSHEET_API_KEY else 'No'}")
    app.run(debug=True)
