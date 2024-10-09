import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fpdf import FPDF
import pandas as pd

class InvoicePDF(FPDF):
    def header(self):
        # Invoice title
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, 'INVOICE', ln=True, align='R')

    def company_details(self):
        # Company details (these remain static)
        self.set_font('Arial', '', 12)
        self.cell(100, 10, 'PATEL BROTHER\'S INTERNATIONAL COURIER', ln=True)
        self.cell(100, 10, '25, Ashirwad Society,', ln=True)
        self.cell(100, 10, 'Old Padra Road, Vadodara, Akota,', ln=True)
        self.cell(100, 10, 'Gujarat - 390020', ln=True)
        self.cell(100, 10, 'GSTIN - 24BBFPP0580H1ZR', ln=True)
        self.cell(100, 10, 'Contact Person - Pate Nishaben S', ln=True)

    def bill_to(self, customer_name):
        # Bill to section (dynamic)
        self.ln(10)
        self.set_font('Arial', 'B', 12)
        self.cell(100, 10, 'Bill To', ln=True)
        self.set_font('Arial', '', 12)
        self.cell(100, 10, customer_name, ln=True)

    def ship_to(self, shipping_address):
        # Ship to section (dynamic)
        self.ln(5)
        self.set_font('Arial', 'B', 12)
        self.cell(100, 10, 'Ship To', ln=True)
        self.set_font('Arial', '', 12)
        self.cell(100, 10, shipping_address, ln=True)

    def invoice_details(self, invoice_number, date, balance_due):
        # Invoice date and balance due (dynamic)
        self.set_y(45)
        self.set_x(-70)
        self.cell(0, 10, f'Invoice #: {invoice_number}', ln=True)
        self.cell(0, 10, f'Date: {date}', ln=True)
        self.cell(0, 10, f'Balance Due: ₹{balance_due}', ln=True)

    def add_item_table(self, items):
        # Adding table header
        self.ln(20)
        self.set_font('Arial', 'B', 12)
        self.cell(60, 10, 'ITEM', 1)
        self.cell(30, 10, 'QUANTITY', 1)
        self.cell(40, 10, 'RATE', 1)
        self.cell(40, 10, 'AMOUNT', 1)
        self.ln()

        # Add table rows (dynamic)
        self.set_font('Arial', '', 12)
        for item in items:
            self.cell(60, 10, item['description'], 1)
            self.cell(30, 10, str(item['quantity']), 1)
            self.cell(40, 10, f"₹{item['rate']:.2f}", 1)
            self.cell(40, 10, f"₹{item['amount']:.2f}", 1)
            self.ln()

    def add_totals(self, subtotal, tax_rate, total):
        # Adding subtotal, tax, and total (dynamic)
        self.ln(10)
        self.set_font('Arial', 'B', 12)
        self.cell(130, 10, 'Subtotal', 0)
        self.cell(40, 10, f"₹{subtotal:.2f}", 0, ln=True)

        self.cell(130, 10, f"Tax ({tax_rate*100}%)", 0)
        self.cell(40, 10, f"₹{subtotal * tax_rate:.2f}", 0, ln=True)

        self.cell(130, 10, 'Total', 0)
        self.cell(40, 10, f"₹{total:.2f}", 0, ln=True)


# Set up the Google Sheets API credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('your-credentials-file.json', scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open("InvoiceData").sheet1

# Get all data in the sheet
data = sheet.get_all_records()

# Iterate through each row and generate an invoice for each customer
for row in data:
    pdf = InvoicePDF()
    pdf.add_page()

    # Static company details
    pdf.company_details()

    # Dynamic invoice data from the Google Sheet
    pdf.bill_to(row['Bill To'])
    pdf.ship_to(row['Ship To'])
    pdf.invoice_details(row['Invoice Number'], row['Date'], row['Total Price'])

    # Dynamic item table
    items = [
        {'description': row['Description'], 'quantity': 1, 'rate': row['Price'], 'amount': row['Price']}
    ]
    pdf.add_item_table(items)

    # Totals
    subtotal = row['Price']
    gst = row['GST']
    total = row['Total Price']
    pdf.add_totals(subtotal, gst, total)

    # Save the PDF
    pdf_filename = f"invoice_{row['Invoice Number']}.pdf"
    pdf.output(pdf_filename)
