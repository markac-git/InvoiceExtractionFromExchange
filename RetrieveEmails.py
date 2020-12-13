import email
import imaplib
import os
from configparser import ConfigParser
import SendMail

mail = None
attachment_dir = None


def init():
    global attachment_dir
    global mail
    """Configuration"""
    config = ConfigParser()
    config.read('config.ini')
    attachment_dir = config['Directories']['new_invoices_dir']
    user = config['Gmail']['user']
    password = config['Gmail']['password']
    host = config['Gmail']['host']
    port = config['Gmail']['port']
    while not mail:
        mail = connection(user, password, host, port)  # calling function for establishing connection
    print('Mail connection established')


def connection(address, password, host, port):
    """
    Connects to Outlook
    :returns: mail connection
    """
    print('Connecting to ' + host + "...")
    mail = imaplib.IMAP4_SSL(host, port)  # port for connecting
    mail.login(address, password)
    return mail


def read_inbox():
    mail.select('Inbox')
    # Returned data is a tuple
    # - we're only interested in data, so a placeholder is placed
    _, data = mail.search(None, '(UNSEEN)')  # search for unread emails
    inbox_item_list = data[0].split()  # list of references to emails
    if not inbox_item_list:
        print('No unread emails')
    for item in inbox_item_list:
        # Returned data are tuples of message part envelope and data
        # The latter type of payload is indicated as multipart/* or message/rfc822
        _, email_data = mail.fetch(item, '(RFC822)')  # returns email in byte form
        string_email = email_data[0][1].decode("utf-8")  # extracting
        email_message = email.message_from_string(string_email)  # converting to object
        if get_invoices(email_message):
            print('Invoice collected')
        else:
            sender_email = email_message['From']
            SendMail.send_email(sender_email)  # sends default mail
        mail.uid('STORE', item, '+FLAGS', '\\SEEN')  # marking email as read


def get_invoices(msg):
    sender_email = msg['From']
    print(sender_email)
    for part in msg.walk():  # iterates through email object
        if part.get_content_maintype() == 'multipart':
            continue  # skipping to next iteration of msg.walk()
        if part.get_content_disposition() is None:
            continue
        file_name = part.get_filename()
        if not file_name.endswith('.pdf'):
            continue
        if bool(file_name):
            file_path = os.path.join(attachment_dir, sender_email + '_' + file_name)
            with open(file_path, 'wb') as f:  # wb = wide binary
                f.write(part.get_payload(decode=True))
