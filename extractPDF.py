import pdfplumber
import os
import shutil
import csv
import pandas as pd
from openpyxl import load_workbook


#   import requests
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
    invoices = []  # array of invoices
    for dirpath, subdirs, files in os.walk(  # tuple
            new_invoices_dir):  # the path to the directory. dirnames is a list of the names of the subdirectories in dirpath filenames is a list of the names of the non-directory files in dirpath
        for f in files:
            if f.endswith(".pdf"):
                invoices.append(
                    os.path.join(dirpath, f))  # To get a full path - names in the lists contain no path components.
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
            return row.split()[-1].replace('$', '')  # last row from end

    #  if row.startswith('Labor'):
    #     item = row.split()[0]


def estimation_check(item):
    with open('estimations.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for line in csv_reader:
            if item == line['Item']:
                return line['Estimation']
        print('Nothing found')


def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')


new_invoices_dir = '/Users/markcederborg/PycharmProjects/InvoiceExtractionExchange/AttachmentDirectory/NewInvoices'
treated_invoices_dir = '/Users/markcederborg/PycharmProjects/InvoiceExtractionExchange/AttachmentDirectory/TreatedInvoices'
invoices = check_for_new_invoices()  # returns array of invoices
for invoice in invoices:
    balance = search(invoice)
    print(balance)
    item = 'Labor'
    estimation = estimation_check(item)
    change = get_change(float(balance), float(estimation))
    print(change)
    if change < 20:
        print('Approved')
    else:
        print('Please notice the price change')

#   update()  # deletes array and files in invoice directory
