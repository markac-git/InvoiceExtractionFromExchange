import time
import InvoiceExtraction
import RetrieveEmails
import mysql.connector.errors
import imaplib


def search_mailbox():
    RetrieveEmails.read_inbox()


def treat_invoice():
    InvoiceExtraction.main()


def run():
    search_mailbox()
    treat_invoice()


def init():
    RetrieveEmails.init()
    InvoiceExtraction.init()


def error_handling(error):
    print(error)
    print('Waiting for reestablishing ...')
    time.sleep(15)
    main()


def main():
    try:
        init()
        while not error_handling():
            run()
            time.sleep(5)
    except imaplib.IMAP4_SSL.error as e:
        error_handling(e)
    except mysql.connector.errors as e:
        error_handling(e)
    except ConnectionRefusedError as e:
        error_handling(e)


if __name__ == '__main__':
    main()
