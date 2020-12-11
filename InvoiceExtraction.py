import os
import shutil
import time
from configparser import ConfigParser
import mysql.connector
import pdfplumber
import sendMail


def main():
    if db_connection:
        for invoice in invoices:
            if extract_data(invoice):
                invoice_data = extract_data(invoice)
                try:
                    add_invoice(invoice_data)
                except(ConnectionError):
                    print('Database connection error')
                    return
                else:  # Probably due to wrong input data as connection is already established
                    print('Extraction Failure')
                    from_address = invoice.split()[-2].replace('<', '').replace('>', '')
                    send_error_mail(from_address)  # Due to above theory


def send_error_mail(to_address):
    sendMail.send_email(to_address)


def check_for_new_invoices():
    """
    Generates the file names in a directory tree by walking the tree
    either top-down or bottom-up. For each directory in the tree rooted
    at directory top (including top itself), it yields a 3-tuple
    (dirpath, dirnames, filenames). Appending array if file is .pdf
    """
    invoices = []  # array of invoices
    for dirpath, subdirs, files in os.walk(new_invoices_dir):
        for f in files:
            if f.endswith(".pdf"):
                invoices.append(
                    os.path.join(dirpath, f))  # To get a full path - names in the lists contain no path components.
    return invoices


def update():
    """cutting invoice from directory new_invoices to treated_invoices"""
    invoices.clear()
    file_names = os.listdir(new_invoices_dir)
    for file_name in file_names:
        shutil.move(os.path.join(new_invoices_dir, file_name), treated_invoices_dir)


def extract_data(invoice):
    """
    :param invoice:
    :return: invoice data - array pushed into dictionary
    """
    invoice_data = {}  # creating dictionary for invoice data
    services_data = []
    extraction_completed = False

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
                add_service(service)  # adding service to estimations if false
            services_data.append({'Description': service, 'Hours': hours, 'Cost': cost, 'Approved': approved})
            invoice_data['Approved'] = approved
    # pushing array into dictionary to access data of every service (e.g. (l: 140+))
    invoice_data['Service(s)'] = services_data

    if extraction_completed:
        print('Data extracted')
        return invoice_data
    else:
        return None


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
    """ Adding service to estimations section in db with price --> INF
    :param service: item """
    query = "INSERT INTO estimations (item, price) VALUES (%s, %s);"
    values = (service, 99999)
    mycursor.execute(query, values)
    # mydb.commit()


def add_invoice(invoice):
    """
    Adding invoice data to db
    :param invoice contains all information as
    an array is pushed into a dictionary
    """
    query = "INSERT INTO invoice (invoiceID, company, date, billedTo, total, approved) VALUES (%s, %s, %s, %s, %s, %s);"
    values = (
        invoice['Invoice_ID'], invoice['Company'], invoice['Date'], invoice['Name'], invoice['Total'],
        invoice['Approved'])
    mycursor.execute(query, values)
    # mydb.commit()

    for s in invoice['Service(s)']:
        query = "INSERT INTO service (name, hours, rate, approved) VALUES (%s, %s, %s, %s);"
        values = (s['Description'], s['Hours'], s['Cost'], s['Approved'])
        mycursor.execute(query, values)
        # mydb.commit()


""" Configuration - ONLY RUNS ONCE WHEN IMPORTED
Reading information from config.ini in order to hide information
as .gitignore contains "/config.ini"  
"""

config = ConfigParser()
config.read('config.ini')
db_connection = False
while not db_connection:
    try:
        mydb = mysql.connector.connect(
            host=config['Database']['host'],
            user=config['Database']['user'],
            password=config['Database']['password'],
            database=config['Database']['database']
        )
        mycursor = mydb.cursor()  # for exucuting commands
        if mydb:
            db_connection = True  # breaking while-loop
            print('Database Connection Established.')
    except:
        print('Database Connection Error.')
        time.sleep(5)
        print('Reconnecting Database... ')

new_invoices_dir = config['Directories']['new_invoices_dir']
treated_invoices_dir = config['Directories']['treated_invoices_dir']
invoices = check_for_new_invoices()  # returns array of invoices
