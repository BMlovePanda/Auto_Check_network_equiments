# Auto_Check_network_equiments
通过Python脚本，自动巡检网络设备，并将巡检结果输出到附件，邮件发送。使用的是Python的telnetlib模块以及paramiko模块
etc目录中的内容为示例，可根据情况进行修改。
作者联系方式：代码里有，找不到的话，可以在这里留言。

##配置说明
etc目录

#CMD_Cisco.ini
为思科网络设备的命令列表

#CMD_HW.ini
为华为设备及华三设备的命令列表

#Mail_list.ini
接收邮件人员的邮件列表

#Network_addr.ini
巡检网络设备的IP地址

#password.ini
设备密码，以及邮件发送的账号及密码

2018.10.11日重新修改代码，添加了ssh巡检功能以及优化了程序内容。
