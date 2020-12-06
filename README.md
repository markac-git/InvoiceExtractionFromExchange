# InvoiceExtractionFromExchange
Application for automating the process of extracting key values from an invoice send to a mailbox


exchangeConnection:
The application is connected with the exchange account virksomhedX@outlook.dk. There's currently one unread email for testing. 
The program runs through all unread messages and marks them as read. If the email contains a pdf (along with other rules), 
the attachment is downloaded to the attachment directory, which currently:

attachment_dir = '/Users/markcederborg/PycharmProjects/InvoiceExtractionExchange/AttachmentDirectory/NewInvoices'
(replace with your own path)

extractPDF:
When an invoice is downloaded, the extractPDF file can be run. This program extracts necessary information regarding 
the invoice to store these in a dictionary (keys and values) along with a backlog check (comparing with price estimations
of a service/product). The idea is to add the information directly to a database that provides the information to our website.
The update function (moving invoice from new_invoices to treated_invoices) is currently out commented due to testing.

