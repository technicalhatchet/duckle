from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from duckle_parser import BankStatementParser
from database_handler import DatabaseHandler
import pdfplumber
import tempfile

app = Flask(__name__, static_folder='react-build')
CORS(app)  # Enable CORS for all routes

# Initialize the parser and database handler
parser = BankStatementParser()
db_handler = DatabaseHandler()

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.pdf'):
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
            file.save(temp.name)
            pdf_path = temp.name
        
        try:
            # Extract text from PDF
            with pdfplumber.open(pdf_path) as pdf:
                all_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            
            if not all_text.strip():
                # If no text found, attempt OCR
                all_text = parser.perform_ocr_on_pdf(pdf_path)
            
            # Parse the text
            transactions = parser.parse_bank_statement_with_year(all_text)
            
            # Insert transactions into the database
            for transaction in transactions:
                db_handler.insert_transaction(transaction)
            
            # Clean up the temporary file
            os.unlink(pdf_path)
            
            return jsonify({
                'message': f'Successfully parsed {len(transactions)} transactions',
                'transactions': [
                    {
                        'date': t[0],
                        'withdrawal_or_deposit': t[1],
                        'transaction_type': t[2],
                        'details': t[3],
                        'amount': t[4],
                        'balance': t[5],
                        'category': t[6],
                        'subcategory': t[7]
                    } for t in transactions
                ]
            })
        
        except Exception as e:
            # Clean up in case of error
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    transactions = db_handler.fetch_all_transactions()
    return jsonify([
        {
            'id': t[0],
            'date': t[1],
            'withdrawal_or_deposit': t[2],
            'transaction_type': t[3],
            'details': t[4],
            'amount': t[5],
            'balance': t[6],
            'category': t[7],
            'subcategory': t[8]
        } for t in transactions
    ])

@app.route('/api/categories', methods=['GET'])
def get_categories():
    from gui import CATEGORY_RULES  # Import here to avoid circular imports
    return jsonify(list(CATEGORY_RULES.keys()))

@app.route('/api/set-category', methods=['POST'])
def set_category():
    data = request.json
    if not data or 'transaction_id' not in data or 'category' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    transaction_id = data['transaction_id']
    category = data['category']
    subcategory = data.get('subcategory', category)
    
    # For subcategory handling
    if " -> " in category:
        main_category, subcategory = category.split(" -> ")
    else:
        main_category = category
    
    try:
        db_handler.update_transaction_category(transaction_id, main_category, subcategory)
        return jsonify({'message': 'Category updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add-category', methods=['POST'])
def add_category():
    data = request.json
    if not data or 'category' not in data:
        return jsonify({'error': 'Missing category name'}), 400
    
    new_category = data['category'].strip()
    
    # Update CATEGORY_RULES (needs file modification for persistence)
    from gui import CATEGORY_RULES
    if new_category and new_category not in CATEGORY_RULES:
        CATEGORY_RULES[new_category] = []
        # Save updated categories to a JSON file for persistence
        with open('categories.json', 'w') as f:
            json.dump(CATEGORY_RULES, f)
        return jsonify({'message': f'Category {new_category} added successfully'})
    else:
        return jsonify({'error': 'Category already exists or is empty'}), 400

@app.route('/api/export', methods=['GET'])
def export_data():
    import pandas as pd
    
    transactions = db_handler.fetch_all_transactions()
    if not transactions:
        return jsonify({'error': 'No data to export'}), 404
    
    columns = ['ID', 'Date', 'Withdrawal/Deposit', 'Transaction Type', 
               'Details', 'Amount', 'Balance', 'Category', 'Subcategory']
    
    df = pd.DataFrame(transactions, columns=columns)
    
    # Save to a temporary CSV file
    temp_csv = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    df.to_csv(temp_csv.name, index=False)
    temp_csv.close()
    
    # Return the CSV file
    response = send_from_directory(os.path.dirname(temp_csv.name),
                                  os.path.basename(temp_csv.name),
                                  as_attachment=True,
                                  download_name='transactions.csv')
    
    # Schedule the temporary file for deletion after response is sent
    @response.call_on_close
    def remove_file():
        if os.path.exists(temp_csv.name):
            os.unlink(temp_csv.name)
    
    return response

# Serve React app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)