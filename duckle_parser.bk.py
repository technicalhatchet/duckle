import re
import pdfplumber

def extract_text_from_pdf(pdf_path):
    """Extracts raw text from a bank statement PDF."""
    raw_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            raw_text += page.extract_text() + "\n"  # Extract text from each page
    return raw_text

def parse_transactions(raw_text):
    """
    Parses bank transactions from raw text and returns a structured list.

    Handles:
    - Multi-line transaction descriptions.
    - Correctly assigns withdrawals and deposits.
    - Extracts the balance accurately.
    """

    # Refined regex pattern for transaction extraction
    transaction_pattern = re.compile(
        r"(?P<date>\w{3} \d{1,2})\s+"  # Match date (e.g., "Jan 2")
        r"(?P<type>Withdrawal|Deposit|ACH|Card purchase|POS|Home banking Transfer.*?)\s+"  # Match transaction type
        r"(?P<description>.*?)\s+"  # Match transaction description (multi-line enabled)
        r"(?P<amount>-?\d{1,3}(?:,\d{3})*\.\d{2})\s+"  # Match transaction amount
        r"(?P<balance>\d{1,3}(?:,\d{3})*\.\d{2})",  # Match balance
        re.DOTALL  # Enables handling multi-line descriptions
    )

    transactions = []  # List to store structured transactions
    matches = transaction_pattern.finditer(raw_text)

    for match in matches:
        transaction_data = match.groupdict()

        # Append structured transaction
        transactions.append({
            "date": transaction_data["date"],
            "type": transaction_data["type"],
            "description": " ".join(transaction_data["description"].split()),  # Clean extra spaces/newlines
            "amount": float(transaction_data["amount"].replace(",", "")),  # Convert amount to float
            "balance": float(transaction_data["balance"].replace(",", "")),  # Convert balance to float
        })

    return transactions

def process_pdf(pdf_path):
    """
    Extracts text from the PDF, parses transactions, and returns structured data.
    """
    raw_text = extract_text_from_pdf(pdf_path)
    transactions = parse_transactions(raw_text)
    return transactions