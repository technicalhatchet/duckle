import pdfplumber

pdf_path = "Redactednew.pdf"  # Update with correct path

with pdfplumber.open(pdf_path) as pdf:
    full_text = ""
    for page in pdf.pages:
        full_text += page.extract_text() + "\n\n"

print(full_text[:9000])  # Print first 9000 characters to inspect structure