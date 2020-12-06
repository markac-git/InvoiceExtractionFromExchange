import email
import imaplib
import os
from configparser import ConfigParser

attachment_dir = '/Users/markcederborg/PycharmProjects/InvoiceExtractionExchange/AttachmentDirectory/NewInvoices'

def connection(address, password, host):
    """
    Connects to Outlook
    :param address:
    :param password:
    :param host:
    :return: mail connection
    """
    print('Connecting to ' + host + "...")
    mail = imaplib.IMAP4_SSL(host, 993)
    mail.login(address, password)
    return mail


def read_inbox():

    mail.select('Inbox')
    status, data = mail.search(None, '(UNSEEN)')  # search for unread emails
    inbox_item_list = data[0].split()
    if not inbox_item_list:
        print('No unread emails')
    for item in inbox_item_list:
        result2, email_data = mail.fetch(item, '(RFC822)')  # standard
        raw_email = email_data[0][1].decode("utf-8")
        email_message = email.message_from_string(raw_email)  # converting to object
        get_invoices(email_message)
        mail.uid('STORE', item, '+FLAGS', '\\SEEN')  # marking email as read


def get_invoices(msg):
    for part in msg.walk():  # iterates through email object
        if part.get_content_maintype() == 'multipart':
            continue  # skipping to next iteration of msg.walk()
        if part.get_content_disposition() is None:
            continue
        file_name = part.get_filename()
        if not file_name.endswith('.pdf'):
            continue
        if bool(file_name):
            file_path = os.path.join(attachment_dir, file_name)
            with open(file_path, 'wb') as f:  # wb = wide binary
                f.write(part.get_payload(decode=True))
        print('Invoice collected')


config = ConfigParser()
config.read('config.ini')
user = config['Exchange']['user']
password = config['Exchange']['password']
host = config['Exchange']['host']

mail = connection(user, password, host)  # calling function for establishing connection
read_inbox()
