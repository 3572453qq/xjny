#coding=utf-8
# from ldap3 import *


from ldap3 import Server, Connection, SUBTREE, ALL_ATTRIBUTES

# 替换以下信息为您的AD服务器信息
ad_server = '172.28.1.254'
# ad_user = 'Administrator'
# ad_password = 'xinshijie@2023'
ad_user = 'readony'
ad_password = 'Abc_12345'
base_dn = 'DC=xworld,DC=com'

# 设置AD服务器和连接
server = Server(ad_server, use_ssl=False)
conn = Connection(server, user=ad_user, password=ad_password, auto_bind=True)
print(conn.result)
if not conn.result:
    print("LDAP error:", conn.result)
    # print("Additional info:", conn.result.get("description"))

# 设置查询参数
search_filter = '(&(objectClass=user)(sAMAccountName=*))'  # 您可以根据需要更改搜索过滤器
attributes = [ALL_ATTRIBUTES]  # 获取所有属性，您可以根据需要指定特定的属性

# 执行查询
conn.search(search_base=base_dn, search_filter=search_filter, search_scope=SUBTREE, attributes=attributes)

# 处理查询结果
for entry in conn.entries:
    print("DN:", entry.entry_dn)
    print("Username:", entry.sAMAccountName.value)
    # print("First Name:", entry.givenName.value)
    # print("Last Name:", entry.sn.value)
    # print("Email:", entry.mail.value)
    print("---------------------")

# 关闭连接
conn.unbind()



# if __name__ == '__main__':

#     #连接ad服务器
#     admin = "administrator"
#     adminpwd = "xinshijie@2023"
#     server_ip = '172.28.1.254'
#     print('server ip is:',server_ip)
#     s = Server(server_ip, get_info=ALL, use_ssl=False)
#     c = Connection(s, user=admin, password=adminpwd, auto_bind=True)
#     base='OU=Users,DC=xworld,DC=com,DC=cn'
#     print('connecting ad server',c.result)

    
#     c.unbind()