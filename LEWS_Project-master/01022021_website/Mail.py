import yagmail
'''receiver = "ankit28sharma@gmail.com"
body = "Hello there from Yagmail"
filename = "document.pdf"

yag = yagmail.SMTP("lews.sailab@gmail.com")
yag.send(
    to=receiver,
    subject="Yagmail test with attachment",
    contents=body, 
    attachments=filename,
)
print('MAIL HAS BEEN SENT')  #Root@123'''


print('HI')
# connect to smtp server.
yag_smtp_connection = yagmail.SMTP( user="lews.sailab@gmail.com", password="Root@123", host='smtp.gmail.com')
# email subject
subject = 'Hello from richard'
# email content with attached file path.
contents = ['Hello tom this is richard speaking']
# send the email
yag_smtp_connection.send('ankit28sharma@gmail.com', subject, contents)
