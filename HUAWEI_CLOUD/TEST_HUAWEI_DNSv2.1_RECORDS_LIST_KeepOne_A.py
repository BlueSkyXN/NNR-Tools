import requests
import json
import configparser

def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def get_XSubjectToken(config):
    IAM_AccountName = config.get('HUAWEI_API', 'HUAWEI_IAM_AccountName')
    IAM_UserName = config.get('HUAWEI_API', 'HUAWEI_IAM_UserName')
    IAM_Password = config.get('HUAWEI_API', 'HUAWEI_IAM_Password')

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

    url = "https://iam.myhuaweicloud.com/v3/auth/tokens"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    token = response.headers.get('X-Subject-Token')
    return token if token else None

def query_record_sets(XSTOKEN, zone_id, HUAWEI_DNS_TEST_DOMAIN):
    params = {"type": "A", "search_mode": "equal", "name": HUAWEI_DNS_TEST_DOMAIN}
    url = f"https://dns.myhuaweicloud.com/v2.1/zones/{zone_id}/recordsets"
    headers = {"Content-Type": "application/json", "X-Auth-Token": XSTOKEN}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def delete_record_sets(XSTOKEN, zone_id, recordset_ids_to_delete):
    data = {"recordset_ids": recordset_ids_to_delete}
    url = f"https://dns.myhuaweicloud.com/v2.1/zones/{zone_id}/recordsets"
    headers = {"Content-Type": "application/json", "X-Auth-Token": XSTOKEN}
    response = requests.delete(url, headers=headers, data=json.dumps(data))

    if response.status_code in [200, 202]:
        deleted_records = json.loads(response.text)
        deleted_ids = [record['id'] for record in deleted_records.get('recordsets', [])]
        print("Records deleted successfully:", deleted_ids)
        not_deleted_ids = [record_id for record_id in recordset_ids_to_delete if record_id not in deleted_ids]
        if not_deleted_ids:
            print("Records not deleted:", not_deleted_ids)
    else:
        print(f"Failed to delete record sets: {response.status_code}, {response.text}")


def main(config_file):
    config = read_config(config_file)
    XSTOKEN = get_XSubjectToken(config)
    if not XSTOKEN:
        print("Failed to obtain token, check credentials.")
        return

    zone_id = config.get('HUAWEI_DNS', 'HUAWEI_DNS_ZONE_ID')
    HUAWEI_DNS_TEST_DOMAIN = config.get('HUAWEI_DNS', 'HUAWEI_DNS_TEST_DOMAIN')
    record_sets = query_record_sets(XSTOKEN, zone_id, HUAWEI_DNS_TEST_DOMAIN)

    all_recordset_ids = [record['id'] for record in record_sets.get('recordsets', [])]
    if not all_recordset_ids:
        print("No record sets found to delete.")
        return

    # 找到最新修改的记录的ID
    latest_record_id = max(record_sets['recordsets'], key=lambda x: x['updated_at'])['id']
    print("Record ID being retained:", latest_record_id)  # 显示保留的记录ID

    # 筛选出除了最新记录之外需要删除的记录ID列表
    recordset_ids_to_delete = [record_id for record_id in all_recordset_ids if record_id != latest_record_id]

    if recordset_ids_to_delete:
        delete_record_sets(XSTOKEN, zone_id, recordset_ids_to_delete)
    else:
        print("No record sets found to delete except the latest one.")


# 如果直接运行此脚本，则执行main函数
if __name__ == "__main__":
    config_file = 'NNR.conf'
    main(config_file)
