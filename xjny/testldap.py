import ldap




# LDAP服务器地址
ldap_server = "ldap://172.28.1.254"

# 绑定用户和密码
bind_dn = "cn=administrator,dc=xworld,dc=com"
bind_password = "xinshijie@2023"

# bind_dn = "cn=readonly,dc=xworld,dc=com"
# bind_password = "Admin@123"

# 创建LDAP连接
ldap_conn = ldap.initialize(ldap_server)

# 进行身份验证
ldap_conn.simple_bind_s(bind_dn, bind_password)

# LDAP查询
base_dn = "ou=Users,dc=xworld,dc=com"
filter_str = "(objectClass=person)"
attributes = ["cn", "sn", "mail"]

result = ldap_conn.search_s(base_dn, ldap.SCOPE_SUBTREE, filter_str, attributes)

# 打印查询结果
for dn, entry in result:
    print(f"DN: {dn}")
    print(f"Entry: {entry}")

# 关闭LDAP连接
ldap_conn.unbind()