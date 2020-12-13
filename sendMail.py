import smtplib
from configparser import ConfigParser
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(to_address, message):
    if not message:  # default
        message = 'Sorry for the inconvenience but we are experiencing ' \
                  'some issues extracting your invoice<br>due to our new ' \
                  'system. Please visit: <a href="#">instructions</a> in ' \
                  'order to mail us a valid invoice to <br> receive your ' \
                  'payment sooner.'
    """Configuration"""
    config = ConfigParser()
    config.read('config.ini')
    user = config['Gmail']['user']
    password = config['Gmail']['password']
    host = config['Gmail']['SMTP_server']
    port = config['Gmail']['SMTP_port']
    logo = config['Logo']['logo']

    """
    The approach is to create a message root structure and attaching parts within.
    """
    msg = MIMEMultipart('related')
    msg['Subject'] = "Sorry for the inconvenience..."
    msg['From'] = user
    msg['To'] = to_address

    # Creating the body of the message
    msgAlternative = MIMEMultipart('alternative')
    msg.attach(msgAlternative)
    text = MIMEText('<html><head></head><body>'
                    '<h>Hi!</h><br>'
                    '<p>%s' % message + '<br><br>'
                    + 'Kind regards<br>Main Office - VirksomhedX'
                      '</p></body></html>', 'html', 'utf-8')
    # _maintype as the Content-Type major type (e.g. text or image)
    # and _params is a parameter key/value dictionary
    msgAlternative.attach(text)
    with open(logo, 'rb') as l:  # closes automatically
        msgImage = MIMEImage(l.read())

    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image1>')
    msg.attach(msgImage)

    try:
        with smtplib.SMTP_SSL(host, port) as server:
            server.ehlo()
            server.login(user, password)
            server.sendmail(user, to_address, msg.as_string())
            server.close()
            print('Email sent!')
    except:
        print('Something went wrong...')
