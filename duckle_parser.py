import re
import pytesseract
from PIL import Image
import tempfile
import pdfplumber

class BankStatementParser:
    def __init__(self):
        self.categorization_rules = {
            "Income": ["Payroll", "Deposit", "Best Buy Stores"],
            "Grocery": ["Walmart", "Kroger", "Dollar-General", "Aldi", "Meijer"],
            "Entertainment": ["Netflix", "Spotify", "GameStop", "Doordash", "McDonalds"],
            "Debt": ["Credit Card", "Loan Payment", "Discover", "Best Egg", "Merrick Bank"],
            "Utilities": ["Columbia Gas", "Electric", "Water", "Verizon", "AT&T"],
            "Mortgage": ["Home Mtg", "Mortgage"],
            "Insurance": ["State Farm", "Geico", "Progressive"],
            "Home": ["The Home Depot", "Lowe's", "Menards"],
            "Gas": ["Speedway", "Circle K", "Shell", "BP"]
        }

    def categorize_transaction(self, details, amount):
        """Assign a category and subcategory based on transaction details."""
        for category, keywords in self.categorization_rules.items():
            for keyword in keywords:
                if keyword.lower() in details.lower():
                    subcategory = ""

                    # Special case: Gas transactions under $30 → Snacks, over $30 → Gas
                    if category == "Gas" and float(amount) < 30:
                        subcategory = "Snacks"
                    elif category == "Gas":
                        subcategory = "Gas"

                    return category, subcategory if subcategory else category

        return "Uncategorized", "Other"

    def parse_bank_statement_with_year(self, text):
        if not text:
            print("ERROR: No text provided for parsing!")
            return []

        transactions = []
        print("Starting Parsing...")

        # Initial text cleaning
        cleaned_text = re.sub(r'[^\x00-\x7F]+', '', text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        cleaned_text = re.sub(r'Page:\s*\d+\s*of\s*\d+', '', cleaned_text)

        # First, look for multiline transactions with reference numbers and join them
        multiline_pattern = r'(\d{2}/\d{2}|[A-Za-z]{3} \d{1,2})\s+((?:Card Purchase|POS|ACH|Transfer|ATM)?\s+.+?)\n(\d+)\n(-?[\d,]+\.\d{2})\s+([\d,]+\.\d{2})'

        # Replace multiline transactions with single line format
        cleaned_text = re.sub(multiline_pattern, r'\1 \2 \3 \4 \5', cleaned_text)

        print("DEBUG: Cleaned Text After Joining Multiline Transactions:")
        print(cleaned_text[:9000])  # Print first 9000 characters for debugging

        # Transaction pattern with optional withdrawal/deposit
        transaction_pattern = (
            r'(\d{2}/\d{2}|[A-Za-z]{3} \d{1,2})\s+'  # Date format
            r'(?:\b(Withdrawal|Deposit)\b\s+)?'  # Optional Withdrawal/Deposit
            r'(?:(Card Purchase|Card purchase|POS|ACH|Transfer|ATM)?\s+)?'  # Optional Transaction Type
            r'(.+?)\s+'  # Details until amount
            r'(-?[\d,]+\.\d{2})\s+'  # Amount (supports negative and comma-separated)
            r'([\d,]+\.\d{2})'  # Balance (supports comma-separated)
        )

        matches = list(re.finditer(transaction_pattern, cleaned_text))
        if not matches:
            print("WARNING: No transactions matched!")
            return []

        for i, match in enumerate(matches):
            raw_date, withdrawal_or_deposit, transaction_type, details, amount, balance = match.groups()

            # Check if details contain a reference number and format it nicely
            ref_match = re.search(r'(Ref:\d+)', details)
            if ref_match:
                ref_number = ref_match.group(1)
                details = details.replace(ref_number, f" - {ref_number}")

            # Infer Withdrawal or Deposit if missing
            if not withdrawal_or_deposit:
                withdrawal_or_deposit = "Withdrawal" if "-" in amount else "Deposit"

            # Convert date format
            if '/' in raw_date:
                month, day = raw_date.split('/')
            else:
                month_names = {
                    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
                }
                month_abbr, day = raw_date.split()
                month = month_names.get(month_abbr, "00")

            full_date = f"2025-{month}-{day.zfill(2)}"

            # Clean amount for processing
            amount_clean = amount.replace('-', '').replace(',', '')

            # Step 6: Capture multi-line additional details
            start_pos = match.end()  # Start looking after this transaction
            next_transaction_match = re.search(
                r'(?:[A-Za-z]{3}\s+\d{1,2}|\d{2}/\d{2})',  # Look for next date
                cleaned_text[start_pos:]
            )

            if next_transaction_match:
                # Extract everything between this transaction and the next
                additional_details_text = cleaned_text[start_pos:start_pos + next_transaction_match.start()].strip()
            else:
                # No next transaction, take everything until the end of text
                additional_details_text = cleaned_text[start_pos:].strip()

            # Append additional details to the main details field
            if additional_details_text:
                details = details.strip() + " " + additional_details_text

            category, subcategory = self.categorize_transaction(details, amount_clean)

            transaction_entry = (
                full_date,
                withdrawal_or_deposit,
                transaction_type if transaction_type else "Other",
                details.strip(),
                float(amount_clean),
                float(balance.replace(',', '')),
                category,
                subcategory
            )

            transactions.append(transaction_entry)

        print(f"FINAL DEBUG: Total Parsed Transactions: {len(transactions)}")
        return transactions

    def perform_ocr_on_pdf(self, pdf_file_path):
        """Performs OCR on a PDF file if text-based parsing fails."""
        try:
            with pdfplumber.open(pdf_file_path) as pdf:
                all_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    # Convert the page to an image
                    with tempfile.NamedTemporaryFile(suffix=".png") as temp_img:
                        image = page.to_image()
                        image.save(temp_img.name)

                        # Perform OCR
                        ocr_text = pytesseract.image_to_string(Image.open(temp_img.name), config="--psm 6")
                        all_text += ocr_text + "\n"
                    if page_text:
                        all_text += page_text + "\n\n"  # Ensure line breaks

            return all_text
        except Exception as e:
            print(f"OCR Error: {str(e)}")
            return ""