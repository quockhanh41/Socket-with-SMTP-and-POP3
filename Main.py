from distutils.cmd import Command
from function_common import *
import mailsmtp 
import mailpop3 
import base64 
import os 
import shutil 

const_pathmailbox = "D:/Gmail/"
path_mailbox = ""

def content_choose1(list_mail, list_file, subject_mail, content_mail) :
    print("Day la thong tin soan email: (neu khong dien vui long nhan enter de bo qua)")
    
    # nhap thong in to,cc,bcc
    list_mail["to"] = input("To: ").replace(","," ").split()
    list_mail["cc"] = input("CC: ").replace(","," ").split()
    list_mail["bcc"] = input("BCC: ").replace(","," ").split()
    
    # nhap thong subject va content
    subject_mail = input("Subject: ")
    content_mail = input("Content: ")

    # nhap thong tin file 
    if (input("Co gui file (1.co, 2.khong): ") == "1") : 
        n = int(input("So luong file can gui: "))
        for i in range(1,n + 1): 
            print("Cho biet duong dan file thu ",end = "")
            list_file.append(input(f"{i}: ")) 

    return list_mail, list_file, subject_mail, content_mail  

def check_in_list(Listarray, key): 
    for i in Listarray: 
        if i in key: return True 
    return False

def creater_FilterFolder_mail():
    list_folder = []
    Filter = readinfo_json("Filter")
    for i in range(0,len(Filter)):
        folder_path = path_mailbox + Filter[i][list(Filter[i].keys())[1]]
        list_folder.append(Filter[i][list(Filter[i].keys())[1]])
        os.makedirs(folder_path, mode=0o777, exist_ok = True)
        os.makedirs(folder_path + "/Read", mode=0o777, exist_ok = True)
        os.makedirs(folder_path + "/UnRead", mode=0o777, exist_ok = True)
    
    folder_path = path_mailbox + "Inbox"
    list_folder.append("Inbox")
    os.makedirs(folder_path, mode=0o777, exist_ok = True)
    os.makedirs(folder_path + "/Read", mode=0o777, exist_ok = True)
    os.makedirs(folder_path + "/UnRead", mode=0o777, exist_ok = True)

    return list_folder

def mail_in_folder(): 
    Filter = readinfo_json("Filter")
    list_file_in_folder = []
    for i in range(0,len(Filter)):
        folder_path = path_mailbox + Filter[i][list(Filter[i].keys())[1]]
        for i in os.listdir(folder_path + "/Read"): list_file_in_folder.append(i) 
        for i in os.listdir(folder_path + "/UnRead"): list_file_in_folder.append(i) 
    
    folder_path = path_mailbox + "Inbox"
    for i in os.listdir(folder_path + "/Read"): list_file_in_folder.append(i) 
    for i in os.listdir(folder_path + "/UnRead"): list_file_in_folder.append(i)  

    return list_file_in_folder

def Filter_mail(s, list_folder, number_mail, namemail):
    content_file, From, subject, content, list_file = mailpop3.readinfo_mail(s, number_mail) 
    Filter = readinfo_json("Filter")
    if check_in_list(Filter[0]["From"], From): 
        with open(path_mailbox + Filter[0]["From-to"] + "/UnRead/" + namemail, "w") as f: 
            f.write(content_file)
    elif check_in_list(Filter[1]["Subject"], subject): 
            with open(path_mailbox + Filter[1]["Subject-to"] + "/UnRead/" + namemail, "w") as f: 
                 f.write(content_file)
    elif check_in_list(Filter[2]["Content"], content): 
            with open(path_mailbox + Filter[2]["Content-to"] + "/UnRead/" + namemail, "w") as f: 
                 f.write(content_file)
    elif check_in_list(Filter[3]["Spam"], subject) or check_in_list(Filter[3]["Spam"], content): 
            with open(path_mailbox + Filter[3]["Spam-to"] + "/UnRead/" + namemail, "w") as f: 
                 f.write(content_file)
    else:
            with open(path_mailbox + "Inbox/UnRead/" + namemail,"w") as f:
                f.write(content_file)


def downloadFile(File,path):
    filename,file_data=File
    path+=f'\\{filename}'
    #print(file_data.encode())
    with open(path, 'wb') as attachment_file:
        attachment_file.write(base64.b64decode(file_data))

def read_content(file_path): 
    with open(file_path,"r") as f: 
        boundary = readinfo_json("boundary")
        content_file = con = f.read() 
        
        content_to_cc = con[con.find("To") : con.find("From")]
        L = list(content_to_cc)
        for i in range(0,len(L)-1):
            if(L[i]=='\n' and L[i+1]=='\n'):
                L[i]=''
        #L[content_to_cc.find('\n')] = ''
        content_to_cc = "" 
        for i in L: content_to_cc += i

        From = con[con.find("From:") + 6: con.find("Subject") - 2]
        con = con.split(f"{boundary}\n\n")
        tmp = con[1]
        subject_mail = tmp[tmp.find("Subject:") + 9: ]
        subject_mail = subject_mail.split("\n\n")[0]
        con[2] = con[2].split("\n\n")

        content_mail = f"From: {From}" + '\n' + content_to_cc + con[2][2]
    
        list_file = []
        for i in range(3,len(con) - 1):
            New = con[i].split("\n\n")
            cont = ""
            file_name = New[0][New[0].find('name=') + 5: ]
            for i in range(2,len(New)) : cont += New[i]
            list_file.append((file_name,cont)) 
        return content_file, From, subject_mail, content_mail, list_file

def content_choose2(s, number_of_mail, list_namemail, list_folder): 
    print("Day la danh sach cac mail trong folder cua ban: ")
    for i in range(0,len(list_folder)): print(f"{i + 1}. {list_folder[i]}")
    choose = input("Ban muon xem mail trong folder nao: ")
    if (choose == ""): return False 
    choose = int(choose)
    pos = 0
    while (pos == 0):
        list_fileFolder = []
        T = []
        for i in os.listdir(path_mailbox + list_folder[choose - 1] + "/UnRead/"): 
            content_file, From, subject_mail, content_mail, list_file = read_content(path_mailbox + list_folder[choose - 1] + "/UnRead/" + i)
            T.append((path_mailbox + list_folder[choose - 1],"/UnRead/", i))
            list_fileFolder.append([From,subject_mail,content_mail,list_file,False])

        for i in os.listdir(path_mailbox + list_folder[choose - 1] + "/Read/"): 
            content_file, From, subject_mail, content_mail, list_file = read_content(path_mailbox + list_folder[choose - 1] + "/Read/" + i)
            list_fileFolder.append([From,subject_mail,content_mail,list_file,True])
            T.append((path_mailbox + list_folder[choose - 1],"/Read/", i))

        if (len(list_fileFolder) == 0) :
            print("Khong co email trong folder nay!\r\n")
            return True 

        print("\r\nDay la danh sach mail trong " + list_folder[choose - 1] + " folder")
        c = 0
        for i in list_fileFolder:
            From,subject_mail,content_mail,list_file, Readed = i 
            c = c + 1
            print(f"{c}. ",end = "")
            if (Readed == False): print(f"(chua doc) ",end = "")
            print(f"<{From}> <{subject_mail}>")
        
        pos = input("Ban doc mail thu may (nhan enter de thoat ra ngoai): ")
        if (pos == ""): return False # True : xem lai danh sach email trong folder 
        pos = int(pos)
        From, subject, content, list_file, Readed = list_fileFolder[pos - 1]
        print(f"noi dung mail cua mail thu {pos} la: \n{content}")
        if (len(list_file) != 0):
            yn = input("Trong file co attached file, ban co muon save file khong (1.co, 2.khong): ")
            if (yn == "1"):
                path = input("cho biet duong dan muon luu: ")
                for i in list_file: 
                    downloadFile(i, path)
        shutil.move(T[pos - 1][0] + T[pos - 1][1] + T[pos - 1][2],T[pos - 1][0] + "/Read/" + T[pos - 1][2])
        pos = 0

def process_FILTER() :
    pop3_username = readinfo_json("username")
    pop3_username = pop3_username[pop3_username.find('<') + 1: pop3_username.find('>')]
    pop3_password = readinfo_json("password");
    
    global path_mailbox
    path_mailbox = const_pathmailbox + pop3_username + "/";
    
    list_folder = creater_FilterFolder_mail()
    list_mail_in_folder = mail_in_folder()
    
    s, number_of_mail, list_namemail = mailpop3.received_mailserver(pop3_username,pop3_password)
    
    for i in range(0,len(list_namemail)):
        if check_in_list(list_mail_in_folder, list_namemail[i]): continue # neu loc roi thi bo qua 
        Filter_mail(s, list_folder, i + 1, list_namemail[i])

    for i in range(1,number_of_mail + 1): s.send(f"DELE {i}\r\n".encode())
    s.send("QUIT\r\n".encode())
    return s, number_of_mail, list_namemail, list_folder
    

def MENU() :
    print("\r\nVui long chon: ")
    print("1. De gui email")
    print("2. De xem danh sach cac email da nhan")
    print("3. Dang nhap vao tai khoan khac")
    print("4. Thoat")
    choose = input("Ban chon: ")
    if (choose == "4"): return
    if (choose == "1"): 
        list_mail = {"to": [], "cc": [], "bcc": []}
        list_file = []
        subject_mail = content_mail = ""
        list_mail, list_file, subject_mail, content_mail = content_choose1(list_mail, list_file, subject_mail, content_mail)
        if (mailsmtp.client_mail(list_mail,list_file,subject_mail,content_mail) == False): MENU()
    elif choose == "2":
        s, number_of_mail, list_namemail, list_folder = process_FILTER()
        while(content_choose2(s, number_of_mail, list_namemail, list_folder)): continue
    else: LOGIN_account()
    
    MENU()

#################################
#################################
#################################

import subprocess
import json 

def change_json(keyword_changed, value_changed):
    tmp_data = ""
    with open("Data.json","r") as f:
        tmp_data = json.loads(f.read())
        
    tmp_data[keyword_changed] = value_changed 
    with open("Data.json","w") as f:
        json.dump(tmp_data,f,indent=2, ensure_ascii=False)

def LOGIN_account() :
    print("Login")
    username = "<" + input("Username: ") + ">"
    password = input("Password: ")
    change_json("username", username) 
    change_json("password", password) 

if __name__ == "__main__":
    change_json("Exit_program", False)
    LOGIN_account() 

    command = "python autoload.py"
    process1 = subprocess.Popen(["start", "cmd", "/k", command], shell=True)
    MENU() 
    change_json("Exit_program", True)