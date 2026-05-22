import smtplib
from email.message import EmailMessage


def send_msg(sender, receiver, message):
  """Send an email alert. Safe to call from a worker thread."""
  try:
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = "LANDSLIDE PREDICTION"
    msg['From'] = sender
    msg['To'] = receiver

    # Send the message via SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    #server.login("lews.sailab@gmail.com",'Root@123')
    #server.send_message(msg)
    #server.quit()
  except Exception as e:
    print('Email send failed: %s' % e, flush=True)
