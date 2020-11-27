import email
import imaplib
import os

user = 'virksomhedX@outlook.dk'
password = 'vamXat-rowsub-2zibqa'
host = 'Outlook.office365.com'
attachment_dir = '/Users/markcederborg/PycharmProjects/InvoiceExtractionExchange/AttachmentDirectory/NewInvoices'


def connection(address, password, host):
    # Connect to the server
    print('Connecting to ' + host + "...")
    mail = imaplib.IMAP4_SSL(host, 993)
    mail.login(address, password)
    return mail


def read_inbox():
    mail.select('Inbox')  # selecting inbox folder
    status, data = mail.search(None, '(UNSEEN)')
    inbox_item_list = data[0].split()
    if not inbox_item_list:
        print('No unread emails')
    for item in inbox_item_list:
        result2, email_data = mail.fetch(item, '(RFC822)')
        raw_email = email_data[0][1].decode("utf-8")
        email_message = email.message_from_string(raw_email)  # converting to object
        get_invoices(email_message)
        mail.uid('STORE', item, '+FLAGS', '\\SEEN')


def get_invoices(msg):
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue  # skipping to next part in msg.walk()
        if part.get_content_disposition() is None:
            continue  # skipping to next part in msg.walk()
        file_name = part.get_filename()
        if not file_name.endswith('.pdf'):
            continue
        if bool(file_name):
            file_path = os.path.join(attachment_dir, file_name)
            with open(file_path, 'wb') as f:
                f.write(part.get_payload(decode=True))
        print('Invoice collected')


mail = connection(user, password, host)  # calling function for establishing connection
read_inbox()
