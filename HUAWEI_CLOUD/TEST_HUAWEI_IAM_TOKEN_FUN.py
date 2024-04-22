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

    # 打印返回的响应
    print("Response status code:", response.status_code)
    print("Response headers:", response.headers)
    print("Response body:", response.text)

    # 获取 X-Subject-Token 字段的值
    token = response.headers.get('X-Subject-Token')
    if token:
        return token
    else:
        print("X-Subject-Token not found in response headers.")
        return None

def main():
    # 调用函数获取X-Subject-Token
    XSTOKEN = get_XSubjectToken()
    if XSTOKEN:
        print("X-Subject-Token:", XSTOKEN)

# 如果直接运行此脚本，则执行main函数
if __name__ == "__main__":
    main()
