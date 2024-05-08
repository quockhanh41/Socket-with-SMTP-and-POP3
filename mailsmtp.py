import base64
import socket
import os
import mimetypes
from function_common import *

def get_content_type(file_path) : 
    mime_type, encoding = mimetypes.guess_type(file_path)
    return mime_type 

def recipient_list_to_message(recipient_email_list):
    message=''
    for recipient_email in recipient_email_list:
        message+=recipient_email+', '
    message=message[0:len(message)-2]
    return message
def send_email_data(client_socket,sender_email, to_email_list, subject, body, attachment_paths, 
                    cc_email_list, bcc_email):
    client_socket.sendall(b'DATA\r\n')
    response = client_socket.recv(1024).decode()
            
            # Construct the email message with attachment
    to_email_message= recipient_list_to_message(to_email_list)
    cc_email_message= recipient_list_to_message(cc_email_list)
    boundary = readinfo_json("boundary")

    email_message = (
        f'Content-Type: multipart/mixed; boundary={boundary}\r\n'
        f'MIME-Version: 1.0\r\n'
        f'To: {to_email_message}\r\n' 
    )
    if(len(cc_email_list) != 0): email_message+=f'Cc: {cc_email_message}\r\n'
    if(bcc_email!=''): email_message+=f'Bcc: {bcc_email}\r\n'
    email_message += (
    f'From: {sender_email}\r\n'
    f'Subject: {subject}\r\n')

    email_message+=(
        f'{boundary}\r\n'
        f'Content-Type: text/plain; charset="utf-8"; format=flowed\r\nContent-Transfer-Encoding: 7bit\r\n'
        f'{body}\r\n'
    )
            # Read attachment file and encode in base64
    for attachment_path in attachment_paths:
        email_message += f'{boundary}\r\n'
        namefile = os.path.basename(attachment_path)
        email_message += f'Content-Type: ' + get_content_type(namefile) + f"; name={namefile}\r\n"
        email_message+= f'Content-Disposition: attachment; filename="{namefile}"\r\n'
        with open(attachment_path, 'rb') as attachment_file:
            attachment_data = base64.b64encode(attachment_file.read()).decode('utf-8')
            
        chunk_size = 1024  # Adjust the chunk size as needed
        cnt_size = 0
        for i in range(0, len(attachment_data), chunk_size):
            chunk = attachment_data[i:i + chunk_size]
            cnt_size += 1024
            if (cnt_size > 3000000):
                print("File",namefile,"vuot qua kich thuc 3MB, yeu cau gui lai")
                return False
            email_message += f'{chunk}\r\n'
            # # Add attachment data to the email message
            # email_message += f'{attachment_data}\r\n\r\n'
            
            # End the email message
    email_message += f'{boundary}\r\n.\r\n'

            # Send the email message
    client_socket.sendall(email_message.encode())
    response = client_socket.recv(1024).decode()

    #if "accepted" in response: print("Da gui mail thanh cong")
    return True and ("accepted" in response)

def send_email_with_attach(sender_email, to_email_list, subject, body, attachment_paths, 
                               smtp_host, smtp_port,cc_email_list,bcc_email_list):
    bool1 = send_email_with_attachment(sender_email, to_email_list, subject, body, attachment_paths, smtp_host, smtp_port,cc_email_list,'')
    bool2 = True
    for bcc in bcc_email_list:
        bool2 = bool2 & send_email_with_attachment(sender_email, to_email_list, subject, body, attachment_paths, smtp_host, smtp_port,cc_email_list,bcc)

    if (bool1 & bool2) == True: print("Da gui mail thanh cong")
    else: print("Gui mail khong thanh cong")

    return bool1 & bool2

def send_email_with_attachment(sender_email, to_email_list, subject, body, attachment_paths, 
                               smtp_host, smtp_port, cc_email_list, bcc_email):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # Connect to the SMTP server
        client_socket.connect((smtp_host, smtp_port))
        response = client_socket.recv(1024).decode()

        # Send EHLO command
        client_socket.sendall(f'EHLO {smtp_host}\r\n'.encode())
        response = client_socket.recv(1024).decode()

        # Send MAIL FROM command
        client_socket.sendall(f'MAIL FROM: <{sender_email}>\r\n'.encode())
        response = client_socket.recv(1024).decode()

        # Send RCPT TO command
        if(bcc_email==''):
            for to_email in to_email_list:  
                client_socket.sendall(f'RCPT TO: <{to_email}>\r\n'.encode())
                response = client_socket.recv(1024).decode()

            for cc_email in cc_email_list:  
                client_socket.sendall(f'RCPT TO: <{cc_email}>\r\n'.encode())
                response = client_socket.recv(1024).decode()
            if not send_email_data(client_socket,sender_email,to_email_list,subject,body,attachment_paths,cc_email_list,'') : return False
        else: 
            client_socket.sendall(f'RCPT TO: <{bcc_email}>\r\n'.encode())
            response = client_socket.recv(1024).decode()
            if not send_email_data(client_socket,sender_email,to_email_list,subject,body,attachment_paths,cc_email_list,bcc_email): return False
        # Send QUIT command
        client_socket.sendall(b'QUIT\r\n')
        response = client_socket.recv(1024).decode()
        return True 

def client_mail(list_mail, list_file, subject_mail, content_mail) : 
    smtp_host = readinfo_json("mailserver")
    smtp_port = readinfo_json("SMTP")
    sender_email = readinfo_json("username") #'nguyenquangkhai2509@gmail.com'
    sender_email = sender_email[sender_email.find('<') + 1: sender_email.find('>')]
    to_email_list = list_mail["to"] # ['nguyenquangkhai2509@gmail.com']
    cc_email_list = list_mail["cc"] # ['cclemon@gmail.com']
    bcc_email_list = list_mail["bcc"] 
    subject = subject_mail # subject = 'Test Email with Attachment'
    body = content_mail; # body = 'This is a test email with an attachment sent from Python.'
    attachment_paths = list_file; #attachment_paths = ["D:\Modem.txt","D:\Socket\cmd.txt"]  
    # Replace with the actual path to your file
    
    return send_email_with_attach(sender_email, to_email_list, subject, body, attachment_paths, 
                               smtp_host, smtp_port,cc_email_list,bcc_email_list)

# # # Set your email server details
# smtp_host = 'localhost'  # Assuming the server is running on the same machine
# smtp_port = 2225  # Use the port your test mail server is using (2225 in your case)

# # # Set email details
# sender_email = 'nguyenquangkhai2509@gmail.com'
# to_email_list = ['nguyenquangkhai2509@gmail.com']
# cc_email_list = []
# bcc_email_list = ['bcc2@gmail.com','thenlonlinh2@gmail.com']
# subject = 'Test Email with Attachment'
# body = 'This is a test email with an attachment sent from Python.'
# attachment_paths = ["D:\Modem.txt","D:\Socket\cmd.txt"]     # Replace with the actual path to your file

# # Call the send_email_with_attachment function
# send_email_with_attachment(sender_email, to_email_list, subject, body, attachment_paths, smtp_host, smtp_port,cc_email_list,'')
# for bcc in bcc_email_list:
#     send_email_with_attachment(sender_email, to_email_list, subject, body, attachment_paths, smtp_host, smtp_port,cc_email_list,bcc)