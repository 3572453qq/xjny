#coding=utf-8
from ldap3 import *




if __name__ == '__main__':

    #连接ad服务器
    admin = "administrator"
    adminpwd = "xinshijie@2023"
    server_ip = '172.28.1.254'
    print('server ip is:',server_ip)
    s = Server(server_ip, get_info=ALL, use_ssl=False)
    c = Connection(s, user=admin, password=adminpwd, auto_bind=True)
    base='OU=Users,DC=xworld,DC=com,DC=cn'
    print('connecting ad server',c.result)

    
    c.unbind()