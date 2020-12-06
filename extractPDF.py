import collections
import csv
import os
import shutil
from configparser import ConfigParser
import mysql.connector
import pdfplumber


#   TEST - First Step
#   import requests
#   First step of learning to deal with .pdfs
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


# cutting invoice from directory new_invoices to treated_invoices
def update():
    invoices.clear()
    file_names = os.listdir(new_invoices_dir)
    for file_name in file_names:
        shutil.move(os.path.join(new_invoices_dir, file_name), treated_invoices_dir)


def extract_data(invoice):
    invoice_data = {}  # creating dictionary for invoice data
    services_data = []  # creating array

    with pdfplumber.open(invoice) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
    for row in text.split('\n'):
        if row.lower().__contains__('company name: '):
            invoice_data['Company'] = row.lower().replace('company name: ', '').upper()
        if row.lower().__contains__('date:'):
            date = row.split()[-1]
            if date.__contains__('/' or '-'):
                date = date.replace('/' or '-', '')
            invoice_data['Date'] = date
        if row.lower().startswith('name:'):
            invoice_data['Name'] = row.lower().replace('name:', '').upper()
        if row.lower().__contains__('invoice_id'):
            invoice_data['Invoice_ID'] = row.split()[-1]
        if row.lower().startswith('total' or 'amount'):
            invoice_data['Total'] = row.split()[-1]
        if row.startswith('#'):
            service = row.split()[1].upper()
            cost = row.split()[-2]
            hours = row.split()[2]
            if estimation_check(service, cost):
                approved = True
            else:
                approved = False
                add_service(service)    # adding service to estimations if false
            services_data.append({'Description': service, 'Hours': hours, 'Cost': cost, 'Approved': approved})
            invoice_data['Approved'] = approved
    # pushing array into dictionary to access data of every service (e.g. (l: 140+))
    invoice_data['Service(s)'] = services_data
    return invoice_data


def estimation_check(item, cost):
    """
    Comparing with estimation price in db
    If an estimation exist and diff is smaller that 20 percent
    :return: true/false boolean
    """
    mycursor.execute("SELECT * FROM id15598460_erp.estimations;")
    for row in mycursor:
        if item == row[0]:
            estimation = row[1]
            diff = get_change(float(cost), float(estimation))
            if diff < 20:
                approved = True
            else:
                approved = False
    return approved

    """ FIRST STEP FOR DEALING WITH .csv files    
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
    """


def get_change(current, previous):
    """
    :param current price
    :param previous/estimation price
    :return: change in percentage
    """
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')


def add_service(service):
    """ Adding service to estimations section in db with price > INF
    :param service: item """
    query = "INSERT INTO estimations (item, price) VALUES (%s, %s);"
    values = (service, 99999)
    mycursor.execute(query, values)
    mydb.commit()


def add_invoice(invoice):
    query = "INSERT INTO invoice (invoiceID, company, date, billedTo, total, approved) VALUES (%s, %s, %s, %s, %s, %s);"
    values = (invoice['Invoice_ID'], invoice['Company'], invoice['Date'], invoice['Name'], invoice['Total'], invoice['Approved'])
    mycursor.execute(query, values)
    mydb.commit()

    for s in invoice['Service(s)']:
        query = "INSERT INTO service (name, hours, rate, approved) VALUES (%s, %s, %s, %s);"
        values = (s['Description'], s['Hours'], s['Cost'], s['Approved'])
        mycursor.execute(query, values)
        mydb.commit()

    """TESTING 
    mycursor.execute("SELECT * FROM id15598460_erp.invoice;")
    for x in mycursor:
        print(x)
    """

"""
//Configuration
Reading information from config.ini in order to hide information
as .gitignore contains "/config.ini"  
"""
config = ConfigParser()
config.read('config.ini')
mydb = mysql.connector.connect(
    host=config['Database']['host'],
    user=config['Database']['user'],
    password=config['Database']['password'],
    database=config['Database']['database']
)
mycursor = mydb.cursor()

new_invoices_dir = '/Users/markcederborg/PycharmProjects/InvoiceExtractionExchange/AttachmentDirectory/NewInvoices'
treated_invoices_dir = '/Users/markcederborg/PycharmProjects/InvoiceExtractionExchange/AttachmentDirectory/TreatedInvoices'
invoices = check_for_new_invoices()  # returns array of invoices
for invoice in invoices:
    invoice_data = extract_data(invoice)
    add_invoice(invoice_data)
