# SheetGenie 🧞

SheetGenie is a local Flask web application that helps you quickly generate and populate Smartsheets using OpenAI's API. Define a sheet's purpose, generate relevant column headers, and auto-fill sample data—all through a simple and editable interface.

## Features

- **Sheet Verification**: Connect to existing Smartsheets using a Sheet ID
- **AI-Powered Column Generation**: Get suggested column headers based on your sheet's purpose
- **Customizable Column Schema**: Edit AI-generated columns or add your own
- **Sample Data Generation**: Generate realistic sample data based on column structure
- **Direct Push to Smartsheet**: Update your sheet structure and data with one click

## Requirements

- Python 3.7+
- OpenAI API key
- Smartsheet API access token

## Installation

1. **Clone the repository or download the files**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to a new file named `.env`
   - Add your API keys to the `.env` file:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     SMARTSHEET_API_KEY=your_smartsheet_api_key_here
     ```

## Running the Application

1. **Start the Flask application**
   ```bash
   python app.py
   ```

2. **Open your web browser and navigate to**
   ```
   http://127.0.0.1:5000/
   ```

## Usage

1. **Enter Smartsheet ID**
   - Find your Sheet ID in the Smartsheet URL: `https://app.smartsheet.com/sheets/YOUR_SHEET_ID_HERE`
   - Enter it in the first field and click "Verify Sheet"

2. **Generate Column Headers**
   - Enter the purpose of your sheet (e.g., "Project plan", "Employee tracker")
   - Click "Generate Columns" to get AI-suggested column headers

3. **Review & Edit Columns**
   - Modify column titles and types as needed
   - Add additional columns with the "+ Add Column" button
   - Click "Approve & Push to Sheet" when done

4. **Generate Sample Data**
   - Provide a description of the sample data you need
   - Click "Generate Sample Data"

5. **Review & Push Data**
   - Review the first 3 rows of generated data
   - Click "Push Data to Sheet" to update your Smartsheet

## Troubleshooting

### OpenAI API Issues

- Run the `test_openai.py` script to verify your OpenAI API connection:
  ```bash
  python test_openai.py
  ```
- Check that your API key is correct in the `.env` file
- If you get a rate limit error, wait a few minutes and try again

### Smartsheet API Issues

- Verify your Smartsheet API access token is correct in the `.env` file
- Make sure you have the necessary permissions on the sheet you're trying to modify
- Check that the Sheet ID is correct

### Application Errors

- Look for error messages in the Flask console
- If the application crashes, try restarting it
- Make sure all dependencies are installed correctly

## Extending the Application

- **Support for Additional Column Types**: Add more Smartsheet column types as needed
- **Data Generation Options**: Add controls for the number of rows to generate
- **Template Support**: Save and reuse column configurations
- **Authentication**: Add user login and API key management
- **Containerization**: Package the application as a Docker container

## License

This project is for demonstration purposes and can be freely used and modified.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/) - The web framework used
- [OpenAI API](https://openai.com/api/) - For AI-powered content generation
- [Smartsheet API](https://smartsheet-platform.github.io/api-docs/) - For Smartsheet integration
