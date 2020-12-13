import os
import shutil
from configparser import ConfigParser
import mysql.connector
import pdfplumber
import SendMail

new_invoices_dir = None
treated_invoices_dir = None
db_connection, mydb, mycursor = False, None, None
config = None


def init():
    global new_invoices_dir
    global treated_invoices_dir
    global config
    """ Configuration 
    Reading information from config.ini in order to hide information
    as .gitignore contains "/config.ini"""
    config = ConfigParser()
    config.read('config.ini')
    new_invoices_dir = config['Directories']['new_invoices_dir']
    treated_invoices_dir = config['Directories']['treated_invoices_dir']
    connect_db()


def connect_db():
    global db_connection
    global mydb
    global mycursor
    print('Connecting database...')
    mydb = mysql.connector.connect(
        host=config['Database']['host'],
        user=config['Database']['user'],
        password=config['Database']['password'],
        database=config['Database']['database']
    )
    if mydb:
        print('Database Connection Established.')
        mycursor = mydb.cursor()  # for executing commands


def main():
    if db_connection:
        invoices = check_for_new_invoices()  # returns array of invoices
        for invoice in invoices:
            completed, invoice_data = extract_data(invoice)
            if completed:
                add_invoice(invoice_data)
            else:  # Probably due to wrong input data as connection is already established
                print('Extraction Failure')
                from_address = invoice.split()[-2].replace('<', '').replace('>', '')
                # Due to above theory
                SendMail.send_email(from_address)


def check_for_new_invoices():
    """
    Generates the file names in a directory tree by walking the tree
    either top-down or bottom-up. For each directory in the tree rooted
    at directory top (including top itself), it yields a 3-tuple
    (dirpath, dirnames, filenames). Appending array if file is .pdf
    """
    invoices = []  # array of invoices
    for dirpath, subdirs, files in os.walk(new_invoices_dir):  # tuple
        for f in files:
            if f.endswith(".pdf"):
                invoices.append(
                    os.path.join(dirpath, f))  # To get a full path - names in the lists contain no path components.
    return invoices


def update(invoices):
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
                add_service(service, cost)
            else:
                approved = False
                add_service(service, 999999)  # adding service to estimations with cost --> inf if false
            services_data.append({'Description': service, 'Hours': hours, 'Cost': cost, 'Approved': approved})
            invoice_data['Approved'] = approved

    for v in invoice_data.values():
        v = v.__str__()
        if v.__contains__('_') or v.__contains__(':') or v.__contains__('.'):
            extraction_completed = False
        else:
            extraction_completed = True


    # pushing array into dictionary to access data of every service (e.g. (l: 140+))
    invoice_data['Service(s)'] = services_data

    return extraction_completed, invoice_data  # returning tuple

    """
    if extraction_completed:
        print('Data extracted')
        return invoice_data
    else:
        return False
    """


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
            if diff <= 20:
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


def add_service(service, cost):
    """ Adding service to estimations section in db with price --> INF
    :param cost:
    :param service: item """
    query = "INSERT INTO estimations (item, price) VALUES (%s, %s);"
    values = (service, int(cost))
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
    print('Invoice added')
