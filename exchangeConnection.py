import imaplib, email

user = 'virksomhedX@outlook.dk'
password = 'vamXat-rowsub-2zibqa'
imap_url = 'Outlook.office365.com'

connection = imaplib.IMAP4_SSL(imap_url)
connection.login(user, password)

#  TEST  print(connection.list())

connection.select('Inbox')


def search(key, value, connection):
    result, data = connection.search(None, key, '"()"'.format(value))
    return data


print(search('FROM', 'no-reply@microsoft.com', connection))
