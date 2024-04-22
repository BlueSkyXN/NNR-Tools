import requests
import json
import configparser

def get_XSubjectToken(config_file='NNR.conf'):
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(config_file)

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

    # 获取 X-Subject-Token 字段的值
    token = response.headers.get('X-Subject-Token')
    if token:
        return token
    else:
        print("X-Subject-Token not found in response headers.")
        return None

def query_public_zones(XSTOKEN):
    # 构建GET请求的URL
    url = "https://dns.myhuaweicloud.com/v2/zones"

    # 设置请求头部
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": XSTOKEN
    }

    # 发送GET请求
    response = requests.get(url, headers=headers)

    # 返回响应内容
    return response.json()

def main():
    # 获取X-Subject-Token
    XSTOKEN = get_XSubjectToken()

    # 如果没有得到正确的返回值，则从本地文件中读取TOKEN
    if not XSTOKEN:
        with open('HUAWEI_CLOUD_TOKEN.txt', 'r') as file:
            XSTOKEN = file.read().strip()

    # 查询公网Zone列表
    zones = query_public_zones(XSTOKEN)
    print("Public Zones:", zones)

# 如果直接运行此脚本，则执行main函数
if __name__ == "__main__":
    main()
