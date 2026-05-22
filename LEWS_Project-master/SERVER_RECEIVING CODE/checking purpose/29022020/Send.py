import smtplib

# Import the email modules we'll need
from email.message import EmailMessage

# Open the plain text file whose name is in textfile for reading.
def send_msg(sender,receiver,message):
  msg = EmailMessage()
  msg.set_content(message)

  msg['Subject'] = "LANDSLIDE PREDICTION"
  msg['From'] = sender
  msg['To'] = receiver

# Send the message via our own SMTP server.

  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.starttls()
  #server.login("lews.sailab@gmail.com",'Root@123')
  #server.send_message(msg)
  #server.quit()
  
#send_msg('lews.sailab@gmail.com','ankit28sharma@gmail.com','OK')  
