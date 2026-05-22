import smtplib

# Import the email modules we'll need
from email.message import EmailMessage

# Open the plain text file whose name is in textfile for reading.
with open("Mail.py") as fp:
    # Create a text/plain message
    msg = EmailMessage()
    msg.set_content(fp.read())

# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = "LANDSLIDE PREDIUCTION"
msg['From'] = "lews.sailab@gmail.com"
msg['To'] = "ankit28sharma@gmail.com"

# Send the message via our own SMTP server.

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login("lews.sailab@gmail.com",'Root@123')
server.send_message(msg)
server.quit()
