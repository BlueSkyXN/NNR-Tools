import requests
import json
import configparser

def read_config(config_file):
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def get_XSubjectToken(config):
    # 从配置文件中获取IAM的账户信息
    IAM_AccountName = config.get('HUAWEI_API', 'HUAWEI_IAM_AccountName')
    IAM_UserName = config.get('HUAWEI_API', 'HUAWEI_IAM_UserName')
    IAM_Password = config.get('HUAWEI_API', 'HUAWEI_IAM_Password')

    # 构建身份验证请求的数据
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

    # 发送POST请求获取Token
    url = "https://iam.myhuaweicloud.com/v3/auth/tokens"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    token = response.headers.get('X-Subject-Token')

    if token:
        return token
    else:
        print("X-Subject-Token not found in response headers.")
        return None

def query_record_sets(XSTOKEN, zone_id, HUAWEI_DNS_TEST_DOMAIN):
    # 设置查询参数
    params = {
        "type": "A",
        "search_mode": "equal",
        "name": HUAWEI_DNS_TEST_DOMAIN
    }
    url = f"https://dns.myhuaweicloud.com/v2.1/zones/{zone_id}/recordsets"
    headers = {"Content-Type": "application/json", "X-Auth-Token": XSTOKEN}

    # 发送查询请求
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def delete_record_sets(XSTOKEN, zone_id, recordset_ids):
    # 构建删除请求的数据
    data = {
        "recordset_ids": recordset_ids
    }

    # 发送删除请求
    url = f"https://dns.myhuaweicloud.com/v2.1/zones/{zone_id}/recordsets"
    headers = {"Content-Type": "application/json", "X-Auth-Token": XSTOKEN}
    response = requests.delete(url, headers=headers, data=json.dumps(data))

    # 打印删除结果和被删除的记录ID
    if response.status_code in [200, 202]:
        deleted_records = json.loads(response.text)
        for record in deleted_records.get('recordsets', []):
            print(f"Record {record['id']} deletion successful.")
    else:
        print(f"Failed to delete record sets: {response.status_code}, {response.text}")

def main(config_file):
    # 读取配置文件并获取Token
    config = read_config(config_file)
    XSTOKEN = get_XSubjectToken(config)

    # 如果Token获取失败，则退出
    if not XSTOKEN:
        print("Failed to obtain token, check credentials.")
        return

    # 从配置文件中读取Zone ID 和测试域名
    zone_id = config.get('HUAWEI_DNS', 'HUAWEI_DNS_ZONE_ID')
    HUAWEI_DNS_TEST_DOMAIN = config.get('HUAWEI_DNS', 'HUAWEI_DNS_TEST_DOMAIN')

    # 查询指定域名下的Record Set列表
    record_sets = query_record_sets(XSTOKEN, zone_id, HUAWEI_DNS_TEST_DOMAIN)

    # 提取要删除的Record Set ID列表
    recordset_ids = [record['id'] for record in record_sets.get('recordsets', [])]

    # 删除Record Set
    if recordset_ids:
        delete_record_sets(XSTOKEN, zone_id, recordset_ids)
    else:
        print("No record sets found to delete.")

if __name__ == "__main__":
    config_file = 'NNR.conf'
    main(config_file)
