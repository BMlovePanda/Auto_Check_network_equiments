#-*-coding:utf-8-*-
#程序名:AutoCheck_Net.py
#作者:zhangrui@xz.chinamobile.com
#自动巡检网络设备脚本
import telnetlib
import time
import re
import fileinput
import os
import zipfile
import smtplib  
import sys 
import socket
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText  
from email.mime.application import MIMEApplication
#import pdb
#--------------------------------------------------------
LogDir = 'D:\\AutoCheck_Net\\log'   
LogDirMailToday = time.strftime('%Y%m%d')#以日期创建目录
#UserName = 'xz4a_admin'#设备信息
#PassWord = 'tE!b@t5m'
#SuperPass = 's@n!eCa0'
NetworkAddr_FILE = 'D:\\AutoCheck_Net\\etc\\Network_Addr.ini'
CMDFile_HW = 'D:\\AutoCheck_Net\\etc\\CMD_HW.ini'
CMDFile_CISCO = 'D:\\AutoCheck_Net\\etc\\CMD_Cisco.ini'
Password_File = 'D:\\AutoCheck_Net\\etc\\password.ini'
SMTP_Sever = 'smtp.139.com'
Mail_List_File = 'D:\\AutoCheck_Net\\etc\\Mail_list.ini'
ZipFileDir = LogDir + '\\' + LogDirMailToday
ZIPFILE = LogDirMailToday + '.zip'
#--------------------------------------------------------
#def Read_Pass(UserName,PassWord,SuperPass,Mail_User,Mail_Pwd):
def Read_Pass():
    f = file(Password_File,'rb')
    content = f.read()
    f.close
    UserName = re.findall("UserName.*=(.*)",content)
    UserName = "".join(UserName).strip()
    PassWord = re.findall("PassWord.*=(.*)",content)
    PassWord = "".join(PassWord).strip()
    SuperPass = re.findall("SuperPass.*=(.*)",content)
    SuperPass = "".join(SuperPass).strip()
    Mail_User = re.findall("Mail_User.*=(.*)",content)
    Mail_User = "".join(Mail_User).strip()
    Mail_Pwd = re.findall("Mail_Pwd.*=(.*)",content)
    Mail_Pwd = "".join(Mail_Pwd).strip()
    return(UserName,PassWord,SuperPass,Mail_User,Mail_Pwd)
#---------------------设备巡检部分-----------------------
#def Auto_Check(UserName,PassWord,SuperPass,NetworkAddr_FILE,CMDFile_HW,CMDFile_CISCO):
def Auto_Check():
    success_count = 0
    failed_count = 0
    if not os.path.exists(LogDir + '\\' + LogDirMailToday):
        os.mkdir(LogDir + '\\' + LogDirMailToday) 
    os.chdir(LogDir + '\\' + LogDirMailToday)
    NetworkAddr = fileinput.input(NetworkAddr_FILE)
    for Host in NetworkAddr:#连接设备
        try:
            content = ""
            tn = telnetlib.Telnet(Host.strip(),timeout = 3)
            DeviceType = tn.expect([],timeout=0.5)[2].decode().strip()
            tn.set_debuglevel(2)    
            tn.read_until("Username:",1) 
            tn.write(UserName.encode() + "\n")
            tn.read_until("Password:",1)
            tn.write(PassWord.encode() + "\n")
            tn.write(5*b'\n')
            #pdb.set_trace()
            if (DeviceType.upper().find('Huawei'.upper()) != -1 or DeviceType.upper().find('H3C'.upper()) != -1):#华为或者华三设备
                CMDFile = file(CMDFile_HW)#命令列表
                DeviceType = 'HW'
                #DeviceFlag = ']'
                tn.write('super'.encode()+ '\n')
                tn.write(SuperPass.encode() + "\n")      
            else:#思科设备
                CMDFile = file(CMDFile_CISCO)#命令列表
                DeviceType = 'Cisco'
                #DeviceFlag = '#'
                tn.write('enable'.encode()+ '\n')
                tn.write(SuperPass.encode() + "\n")
            for cmd in CMDFile: #输入列表的命令
                tn.write(cmd.strip().encode())
                tn.write(2*b'\n')
                telreply = tn.expect([],timeout=5)[2].decode().strip()#输出日志 
                content = content + telreply
            DeviceName = re.search('[A-Z].*(?=[#|>])',content).group() + '_' + DeviceType
            LogFile = DeviceName + '.txt'
            log = open(LogFile,'a')#写入日志
            DeviceType = ""
            log.write(content)
            log.close()
            CMDFile.close()   
            success_count = success_count + 1            
        except Exception,Error_Message:#登陆失败
            Log_Error_File =  Host.strip() + '_failed.txt' 
            log = open(Log_Error_File,'w')
            Error_Log = 'ERROR:' + Host.strip() + ',' + str(Error_Message)
            log.write(Error_Log)
            log.close()
            failed_count = failed_count + 1
    return (success_count,failed_count)
#---------------------附件压缩部分------------------------
def Zip_File(): 
    os.chdir(LogDir)
    LogZip = zipfile.ZipFile(ZIPFILE,'w',zipfile.ZIP_DEFLATED)#压缩日志
    for filenames in os.walk(ZipFileDir):
        for filename in filenames[-1]:
            LogZip.write(os.path.join(LogDirMailToday + '\\' + filename))
            os.remove(LogDirMailToday + '\\' + filename)#压缩完成后删除文件，以便后续删除原始目录
    LogZip.close()
    #------------------------------------------------------------
    os.removedirs(LogDirMailToday)#压缩成功后，删除原始目录
    return ZIPFILE


#---------------------邮件发送部分-------------------------
#2017.4.28 增加SSL加密功能
#2017.5.2 增加中文邮件支持
#def Send_Mail(Mail_User,Mail_Pwd,SMTP_Sever,Mail_List_File,success_count,failed_count,ZIPFILE):   
def Send_Mail(success_count,failed_count):
    Mail_List = file(Mail_List_File)#邮件地址列表
    Mail_To   = []
    for list in Mail_List:#读取邮件列表文件
        Mail_To.extend(list.strip().split(','))
    Mail_List.close()
    msg = MIMEMultipart() 
    reload(sys)
    sys.setdefaultencoding('utf-8')
    Subject = '网络设备巡检-' + LogDirMailToday
    Content = '巡检成功: ' + str(success_count)  + ' 巡检失败: ' + str(failed_count)
    msg["Subject"] = unicode(Subject) #邮件标题
    msg["From"]    = Mail_User  
    msg["To"]      = ",".join(Mail_To)     
    msgContent = MIMEText(Content ,'html','utf-8')  #邮件内容
    msgContent["Accept-Language"]="zh-CN"
    msgContent["Accept-Charset"]="ISO-8859-1,utf-8"  
    msg.attach(msgContent)
    attachment = MIMEApplication(open(ZIPFILE,'rb').read())  #邮件附件
    attachment.add_header('Content-Disposition', 'attachment', filename=ZIPFILE)  
    msg.attach(attachment)  
    s = smtplib.SMTP_SSL(SMTP_Sever,'465')  
    s.ehlo()  
    s.login(Mail_User, Mail_Pwd)
    s.sendmail(Mail_User, Mail_To, msg.as_string())#发送邮件  
    s.close()
#--------------------------------------------------------------------------
if __name__ == "__main__":
    (UserName,PassWord,SuperPass,Mail_User,Mail_Pwd)=Read_Pass()
    (success_count,failed_count) = Auto_Check()
    Zip_File()
    Send_Mail(success_count,failed_count)