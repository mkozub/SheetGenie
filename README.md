# SheetGenie

SheetGenie is an automation tool that combines the power of Smartsheet and OpenAI to automatically create and populate sheets with AI-generated data.

## Description

SheetGenie helps you quickly set up structured Smartsheet sheets with appropriate columns and sample data. It:
1. Clears an existing Smartsheet
2. Uses AI to generate appropriate column structures based on the sheet type you need
3. Creates those columns in Smartsheet
4. Generates realistic sample data based on your description
5. Populates the sheet with the generated data

## Requirements

- Python 3.7 or higher
- `smartsheet-python-sdk`
- `openai`

## Installation

```bash
pip install smartsheet-python-sdk openai
```

## Environment Variables

You'll need to set the following environment variables:

- `OPENAI_API_KEY` - Your OpenAI API key
- `SMARTSHEET_API_KEY` - Your Smartsheet API key

## Usage

1. Run the script:
   ```bash
   python app.py
   ```

2. Enter your Smartsheet ID when prompted

3. Confirm that you want to clear the sheet (this will delete all existing data!)

4. Enter the type of sheet you want (e.g., "project management", "inventory tracking", "event planning")

5. Describe what kind of data you want to fill the sheet with

## Warning

**This tool will delete all existing data in the specified sheet.** Make sure you have backups if needed.
