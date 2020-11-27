import requests
import pdfplumber
import os
import shutil


#   First step for learning to deal with .pdfs
#   invoice_url = 'http://www.k-billing.com/example_invoices/professionalblue_example.pdf'
#   invoice = download_file(invoice_url)
# def download_file(url):
#    local_filename = url.split('/')[-1]  # splitting from last slash
#   with requests.get(url) as r:  # using requests library for accessing url
#      with open(local_filename, 'wb') as f:
#         f.write(r.content)
#    return local_filename

def check_for_new_invoices():
    invoices = []
    for dirpath, subdirs, files in os.walk(new_invoices_dir):
        for f in files:
            if f.endswith(".pdf"):
                invoices.append(os.path.join(dirpath, f))
    return invoices


def update():
    invoices.clear()
    file_names = os.listdir(new_invoices_dir)
    for file_name in file_names:
        shutil.move(os.path.join(new_invoices_dir, file_name), treated_invoices_dir)


def search(invoice):
    with pdfplumber.open(invoice) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
    # TEST print(text)
    for row in text.split('\n'):  # splitting new line
        if row.startswith('Balance Due'):
            balance = row.split()[-1]  # last row from end
            print(balance)


new_invoices_dir = '/Users/markcederborg/PycharmProjects/InvoiceExtractionExchange/AttachmentDirectory/NewInvoices'
treated_invoices_dir = '/Users/markcederborg/PycharmProjects/InvoiceExtractionExchange/AttachmentDirectory/TreatedInvoices'
invoices = check_for_new_invoices()  # returns array of invoices
for invoice in invoices:
    search(invoice)
update()  # deletes array and files in invoice directory
