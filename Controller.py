import time


def search_mailbox():
    import RetrieveEmails
    RetrieveEmails.read_inbox()


def treat_invoice():
    import InvoiceExtraction
    InvoiceExtraction.main()


def run():
    search_mailbox()
    treat_invoice()


while True:
    run()
    time.sleep(5)
