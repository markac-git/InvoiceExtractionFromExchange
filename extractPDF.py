import collections
import pdfplumber
import os
import shutil
import csv
import requests
import pandas as pd
from openpyxl import load_workbook


#   TEST - First Step
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


def extract_data(invoice):
    invoice_data = collections.defaultdict(list)  # creating dictionary for invoice data
    with pdfplumber.open(invoice) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
    # TEST print(text)
    for row in text.split('\n'):  # splitting new line
        # print(row)
        if row.startswith('Name:'):
            name = row.replace('Name: ', '')
            invoice_data['name'].append(name)
        if row.__contains__('INVOICE_ID'):
            invoice_id = row.split()[-1]
        if row.startswith('TOTAL'):
            total = row.split()[-1]
        if row.startswith('#'):
            service = row.split()[1]
            cost = row.split()[-2]
            if estimation_check(service, cost):
                print('Price approved')
                invoice_data['service'].append(service+' Price Approved')
            else:
                print('Price not approved')
                invoice_data['service'].append(service + ' Price NOT Approved')
    invoice_data['id'].append(invoice_id)
    invoice_data['total'].append(total)
    # for posting form containing invoice data on website
    r = requests.post('https://httpbin.org/post', invoice_data)
    print(r.json())



def estimation_check(item, cost):
    approved = False
    with open('estimations.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for line in csv_reader:
            if item == line['Item']:
                estimation = line['Estimation']
                diff = get_change(float(cost), float(estimation))
                if diff < 20:
                    approved = True
                else:
                    approved = False
        return approved


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
    extract_data(invoice)

#   update()  # deletes array and files in invoice directory
