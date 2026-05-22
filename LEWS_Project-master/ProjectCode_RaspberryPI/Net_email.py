import smtplib
 
#Email Variables
SMTP_SERVER = 'smtp.gmail.com' #Email Server (don't change!)
SMTP_PORT = 587 #Server Port (don't change!)
GMAIL_USERNAME = 'lews.sailab@gmail.com' #change this to match your gmail account
GMAIL_PASSWORD = 'Root@123'  #change this to match your gmail password
 
class Emailer:
    def sendmail(self, recipient, subject, content):
         
        #Create Headers
        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient,
                   "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)
 
        #Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()
 
        #Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
 
        #Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
        session.quit()
 
#Emailer().sendmail('mrinfinitythepro@gmail.com','Bond','James Bond')












'''import smtplib, ssl

port = 587  # For starttls
smtp_server = "smtp.gmail.com"
sender_email = "lews.sailab@gmail.com"
receiver_email = "ankit28sharma@gmail.com"
password = "Root@123"
message = """\
Subject: Hi there This message is sent from Python."""

context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)'''
