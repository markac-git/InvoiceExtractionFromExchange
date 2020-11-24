import imaplib
import email

user = 'virksomhedX@outlook.dk'
password = 'vamXat-rowsub-2zibqa'
imap_url = 'Outlook.office365.com'

connection = imaplib.IMAP4_SSL(imap_url)
connection.login(user, password)

