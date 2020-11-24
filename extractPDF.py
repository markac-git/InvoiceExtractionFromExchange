import requests
import pdfplumber


def download_file(url):
    local_filename = url.split('/')[-1]  # splitting from last slash
    with requests.get(url) as r:  # using requests library for accessing url
        with open(local_filename, 'wb') as f:
            f.write(r.content)
        return local_filename


invoice_url = 'http://www.k-billing.com/example_invoices/professionalblue_example.pdf'
invoice = download_file(invoice_url)

with pdfplumber.open(invoice) as pdf:
    page = pdf.pages[0]
    text = page.extract_text()

# TEST print(text)

for row in text.split('\n'):  # splitting new line
    if row.startswith('Balance Due'):
        balance = row.split()[-1]  # last row from end

        print(balance)
