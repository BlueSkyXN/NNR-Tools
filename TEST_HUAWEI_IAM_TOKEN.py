import requests
import json
import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read('NNR.conf')

# 从配置文件中获取IAM用户名、密码和所属账号名
IAM_AccountName = config.get('HUAWEI_API', 'HUAWEI_IAM_AccountName')
IAM_UserName = config.get('HUAWEI_API', 'HUAWEI_IAM_UserName')
IAM_Password = config.get('HUAWEI_API', 'HUAWEI_IAM_Password')

# 构建POST请求的JSON数据
data = {
    "auth": {
        "identity": {
            "methods": ["password"],
            "password": {
                "user": {
                    "domain": {"name": IAM_AccountName},
                    "name": IAM_UserName,
                    "password": IAM_Password
                }
            }
        },
        "scope": {
            "domain": {"name": IAM_AccountName}
        }
    }
}

# 发送POST请求
url = "https://iam.myhuaweicloud.com/v3/auth/tokens"
headers = {"Content-Type": "application/json"}
response = requests.post(url, data=json.dumps(data), headers=headers)

# 打印返回的响应
print("Response status code:", response.status_code)
print("Response headers:", response.headers)
print("Response body:", response.text)

# 保存 X-Subject-Token 字段的值到文件中
token = response.headers.get('X-Subject-Token')
if token:
    with open('HUAWEI_CLOUD_TOKEN.txt', 'w') as file:
        file.write(token)
        print("Token saved to HUAWEI_CLOUD_TOKEN.txt")
else:
    print("X-Subject-Token not found in response headers.")
