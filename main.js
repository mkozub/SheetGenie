// Define COLUMN_TYPES in the global scope
const COLUMN_TYPES = [
    "TEXT_NUMBER",
    "DATE",
    "DATETIME",
    "CONTACT_LIST",
    "CHECKBOX",
    "PICKLIST",
    "DURATION",
    "ABSTRACT_DATETIME"
];

// Declare verifySheet function in the global scope
function verifySheet() {
    console.log("verifySheet function called");
    const sheetId = document.getElementById('sheetId').value.trim();
    if (!sheetId) {
        showMessage('verifyResult', 'Please enter a Sheet ID', 'error');
        return;
    }
    
    showLoader('verifyLoader');
    clearMessage('verifyResult');
    
    try {
        console.log("Sending verification request for sheet ID:", sheetId);
        fetch('/verify_sheet', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sheet_id: sheetId })
        })
        .then(response => {
            console.log("Response received:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("Response data:", data);
            
            if (data.success) {
                showMessage('verifyResult', `✅ Sheet verified: "${data.sheet_name}"`, 'success');
                document.getElementById('step2').style.display = 'block';
                window.currentSheetId = sheetId;
            } else {
                showMessage('verifyResult', `❌ Error: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            console.error("Error in verify sheet:", error);
            showMessage('verifyResult', `❌ Error: ${error.message}`, 'error');
        })
        .finally(() => {
            hideLoader('verifyLoader');
        });
    } catch (error) {
        console.error("Exception in verify sheet:", error);
        showMessage('verifyResult', `❌ Error: ${error.message}`, 'error');
        hideLoader('verifyLoader');
    }
}

// Utility functions
function showLoader(id) {
    document.getElementById(id).style.display = 'inline-block';
}

function hideLoader(id) {
    document.getElementById(id).style.display = 'none';
}

function showMessage(id, message, type) {
    const element = document.getElementById(id);
    element.textContent = message;
    element.className = `result-box ${type}`;
    element.style.display = 'block';
}

function clearMessage(id) {
    const element = document.getElementById(id);
    element.textContent = '';
    element.style.display = 'none';
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM content loaded - initializing event listeners");
    
    // Global variables to store state
    window.currentSheetId = null;
    window.currentColumns = [];
    window.currentData = [];
    
    // ----- EVENT LISTENERS -----
    
    // Step 1: Verify Sheet
    const verifyBtn = document.getElementById('verifyBtn');
    console.log("Verify button element:", verifyBtn);
    if (verifyBtn) {
        verifyBtn.addEventListener('click', function(e) {
            console.log("Verify button clicked!");
            e.preventDefault();
            verifySheet();
        });
    } else {
        console.error("Verify button not found in the DOM");
    }
    
    // Step 2: Generate Columns
    const generateColumnsBtn = document.getElementById('generateColumnsBtn');
    if (generateColumnsBtn) {
        generateColumnsBtn.addEventListener('click', generateColumns);
    }
    
    // Step 3: Column Actions
    const addColumnBtn = document.getElementById('addColumnBtn');
    if (addColumnBtn) {
        addColumnBtn.addEventListener('click', addEmptyColumn);
    }
    
    // Keeping the event listener for regenerateColumnsBtn even though the button is commented out in HTML
    const regenerateColumnsBtn = document.getElementById('regenerateColumnsBtn');
    if (regenerateColumnsBtn) {
        regenerateColumnsBtn.addEventListener('click', () => {
            document.getElementById('step2').style.display = 'block';
            document.getElementById('step3').style.display = 'none';
        });
    }
    
    const pushColumnsBtn = document.getElementById('pushColumnsBtn');
    if (pushColumnsBtn) {
        pushColumnsBtn.addEventListener('click', pushColumns);
    }
    
    // Step 4: Generate Data
    const generateDataBtn = document.getElementById('generateDataBtn');
    if (generateDataBtn) {
        generateDataBtn.addEventListener('click', generateData);
    }
    
    // Step 5: Data Actions
    // Keeping the event listener for regenerateDataBtn even though the button is commented out in HTML
    const regenerateDataBtn = document.getElementById('regenerateDataBtn');
    if (regenerateDataBtn) {
        regenerateDataBtn.addEventListener('click', () => {
            document.getElementById('step4').style.display = 'block';
            document.getElementById('step5').style.display = 'none';
        });
    }
    
    const pushDataBtn = document.getElementById('pushDataBtn');
    if (pushDataBtn) {
        pushDataBtn.addEventListener('click', pushData);
    }
});

// Generate column suggestions based on sheet purpose
function generateColumns() {
    console.log("generateColumns function called");
    const sheetPurpose = document.getElementById('sheetPurpose').value.trim();
    if (!sheetPurpose) {
        showMessage('verifyResult', 'Please enter a sheet purpose', 'error');
        return;
    }
    
    showLoader('columnsLoader');
    clearMessage('verifyResult');
    
    console.log("Sending generate columns request with purpose:", sheetPurpose);
    fetch('/generate_columns', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ sheet_purpose: sheetPurpose })
    })
    .then(response => {
        console.log("Response received:", response.status);
        return response.json();
    })
    .then(data => {
        console.log("Response data:", data);
        if (data.success) {
            window.currentColumns = data.columns;
            console.log("Rendering columns table with:", window.currentColumns);
            renderColumnsTable(window.currentColumns);
            document.getElementById('step3').style.display = 'block';
        } else {
            showMessage('verifyResult', `❌ Error: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error("Error in generate columns:", error);
        showMessage('verifyResult', `❌ Error: ${error.message}`, 'error');
    })
    .finally(() => {
        hideLoader('columnsLoader');
    });
}

// Push columns to Smartsheet
function pushColumns() {
    // First update currentColumns from the table
    updateColumnsFromTable();
    
    if (window.currentColumns.length === 0) {
        showMessage('pushColumnsResult', 'No columns to push', 'error');
        return;
    }
    
    showLoader('pushColumnsLoader');
    clearMessage('pushColumnsResult');
    
    fetch('/push_columns', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            sheet_id: window.currentSheetId,
            columns: window.currentColumns
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('pushColumnsResult', `✅ ${data.message}`, 'success');
            document.getElementById('step4').style.display = 'block';
        } else {
            showMessage('pushColumnsResult', `❌ Error: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        showMessage('pushColumnsResult', `❌ Error: ${error.message}`, 'error');
    })
    .finally(() => {
        hideLoader('pushColumnsLoader');
    });
}

// Generate sample data based on columns and user prompt
function generateData() {
    const dataPrompt = document.getElementById('dataPrompt').value.trim();
    if (!dataPrompt) {
        showMessage('pushColumnsResult', 'Please enter a data description', 'error');
        return;
    }
    
    showLoader('dataLoader');
    clearMessage('pushColumnsResult');
    
    fetch('/generate_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            sheet_id: window.currentSheetId,
            columns: window.currentColumns,
            data_prompt: dataPrompt
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.currentData = data.data;
            renderDataPreview(window.currentData);
            document.getElementById('step5').style.display = 'block';
        } else {
            showMessage('pushColumnsResult', `❌ Error: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        showMessage('pushColumnsResult', `❌ Error: ${error.message}`, 'error');
    })
    .finally(() => {
        hideLoader('dataLoader');
    });
}

// Push generated data to Smartsheet
function pushData() {
    if (window.currentData.length === 0) {
        showMessage('pushDataResult', 'No data to push', 'error');
        return;
    }
    
    showLoader('pushDataLoader');
    clearMessage('pushDataResult');
    
    fetch('/push_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            sheet_id: window.currentSheetId,
            data: window.currentData
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('pushDataResult', `✅ ${data.message}`, 'success');
        } else {
            showMessage('pushDataResult', `❌ Error: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        showMessage('pushDataResult', `❌ Error: ${error.message}`, 'error');
    })
    .finally(() => {
        hideLoader('pushDataLoader');
    });
}

// Render the columns table
function renderColumnsTable(columns) {
    const tableBody = document.getElementById('columnsTableBody');
    tableBody.innerHTML = '';
    
    columns.forEach((column, index) => {
        const row = document.createElement('tr');
        
        // Title cell (input)
        const titleCell = document.createElement('td');
        const titleInput = document.createElement('input');
        titleInput.type = 'text';
        titleInput.value = column.title;
        titleInput.className = 'column-title';
        titleCell.appendChild(titleInput);
        
        // Type cell (dropdown)
        const typeCell = document.createElement('td');
        const typeSelect = document.createElement('select');
        typeSelect.className = 'column-type';
        
        COLUMN_TYPES.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            if (type === column.type) {
                option.selected = true;
            }
            typeSelect.appendChild(option);
        });
        
        typeCell.appendChild(typeSelect);
        
        // Actions cell
        const actionsCell = document.createElement('td');
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn-delete';
        deleteBtn.textContent = '✕';
        deleteBtn.onclick = () => {
            tableBody.removeChild(row);
        };
        
        actionsCell.appendChild(deleteBtn);
        
        // Append cells to row
        row.appendChild(titleCell);
        row.appendChild(typeCell);
        row.appendChild(actionsCell);
        
        // Append row to table
        tableBody.appendChild(row);
    });
}

// Add an empty column to the table
function addEmptyColumn() {
    const tableBody = document.getElementById('columnsTableBody');
    const row = document.createElement('tr');
    
    // Title cell (input)
    const titleCell = document.createElement('td');
    const titleInput = document.createElement('input');
    titleInput.type = 'text';
    titleInput.value = '';
    titleInput.className = 'column-title';
    titleInput.placeholder = 'Enter column name';
    titleCell.appendChild(titleInput);
    
    // Type cell (dropdown)
    const typeCell = document.createElement('td');
    const typeSelect = document.createElement('select');
    typeSelect.className = 'column-type';
    
    COLUMN_TYPES.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        if (type === 'TEXT_NUMBER') {
            option.selected = true;
        }
        typeSelect.appendChild(option);
    });
    
    typeCell.appendChild(typeSelect);
    
    // Actions cell
    const actionsCell = document.createElement('td');
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'btn-delete';
    deleteBtn.textContent = '✕';
    deleteBtn.onclick = () => {
        tableBody.removeChild(row);
    };
    
    actionsCell.appendChild(deleteBtn);
    
    // Append cells to row
    row.appendChild(titleCell);
    row.appendChild(typeCell);
    row.appendChild(actionsCell);
    
    // Append row to table
    tableBody.appendChild(row);
}

// Update currentColumns from the table
function updateColumnsFromTable() {
    const tableRows = document.querySelectorAll('#columnsTableBody tr');
    window.currentColumns = Array.from(tableRows).map(row => {
        return {
            title: row.querySelector('.column-title').value,
            type: row.querySelector('.column-type').value
        };
    });
}

// Render the data preview table
function renderDataPreview(data) {
    if (data.length === 0) return;
    
    // Get table elements
    const tableHead = document.getElementById('dataPreviewHead');
    const tableBody = document.getElementById('dataPreviewBody');
    
    // Clear previous content
    tableHead.innerHTML = '';
    tableBody.innerHTML = '';
    
    // Create header row
    const headerRow = document.createElement('tr');
    Object.keys(data[0]).forEach(key => {
        const th = document.createElement('th');
        th.textContent = key;
        headerRow.appendChild(th);
    });
    tableHead.appendChild(headerRow);
    
    // Create data rows (only first 3)
    const previewData = data.slice(0, 3);
    previewData.forEach(rowData => {
        const row = document.createElement('tr');
        Object.values(rowData).forEach(value => {
            const td = document.createElement('td');
            td.textContent = value;
            row.appendChild(td);
        });
        tableBody.appendChild(row);
    });
    
    // Update row count display
    document.getElementById('totalRowCount').textContent = data.length;
}