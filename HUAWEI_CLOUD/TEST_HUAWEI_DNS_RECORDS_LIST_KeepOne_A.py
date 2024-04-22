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
    # 设置请求参数
    params = {
        "status": "ACTIVE",
        "type": "A",
        "search_mode": "equal",
        "name": HUAWEI_DNS_TEST_DOMAIN
    }
    url = f"https://dns.myhuaweicloud.com/v2/zones/{zone_id}/recordsets"
    headers = {"Content-Type": "application/json", "X-Auth-Token": XSTOKEN}

    # 发送查询请求
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def delete_record(XSTOKEN, zone_id, recordset_id):
    # 删除指定的DNS记录
    url = f"https://dns.myhuaweicloud.com/v2/zones/{zone_id}/recordsets/{recordset_id}"
    headers = {"Content-Type": "application/json", "X-Auth-Token": XSTOKEN}
    response = requests.delete(url, headers=headers)

    if response.status_code in [200, 202]:
        print(f"Record {recordset_id} deletion requested successfully.")
    else:
        print(f"Failed to delete record {recordset_id}: {response.status_code}, {response.text}")

def main(config_file):
    config = read_config(config_file)
    XSTOKEN = get_XSubjectToken(config)

    if not XSTOKEN:
        print("Failed to obtain token, check credentials.")
        return

    zone_id = config.get('HUAWEI_DNS', 'HUAWEI_DNS_ZONE_ID')
    HUAWEI_DNS_TEST_DOMAIN = config.get('HUAWEI_DNS', 'HUAWEI_DNS_TEST_DOMAIN')
    record_sets = query_record_sets(XSTOKEN, zone_id, HUAWEI_DNS_TEST_DOMAIN)

    if 'recordsets' in record_sets:
        latest_record = max(record_sets['recordsets'], key=lambda x: x['update_at'])
        print(f"Keeping latest record: {latest_record['id']}")

        for record in record_sets['recordsets']:
            if record['id'] != latest_record['id']:
                delete_record(XSTOKEN, zone_id, record['id'])

if __name__ == "__main__":
    config_file = 'NNR.conf'
    main(config_file)
