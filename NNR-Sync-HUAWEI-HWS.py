import requests
import json

# 配置信息硬编码
CONFIG = {
    "NNR_API": {
        "nnr_api_url": "https://nnr.moe/api/servers",
        "nnr_api_token": "xx-xx-xx-xx",
    },
    "DOMAIN_MAP": {
        "803d0da0-1606-48df-914d-34cd235d8206": "nnrsync-sh-jp-iepl",
        "7fc17ab8-cf06-4a5e-8e9b-4bb4a1f91ded": "nnrsync-sz-hk-iepl",
        "50045ba2-29c9-408c-86b5-976042645f52": "nnrsync-gz-hk-iepl-01",
        "6cf4a639-f0dd-42d3-81d7-f47e426264f6": "nnrsync-gz-hk-iepl-02",
        "0428c217-b76f-40f0-b9df-b5fef7be0a34": "nnrsync-sh-jp",
        "049d691a-c65c-4e86-a79b-e32509851add": "nnrsync-sh-hk",
        "82ebf39a-b624-463d-a4da-3d644a4749a9": "nnrsync-gz-hk",
        "2fd3ffd3-1bdb-424c-a9d8-487236698c29": "nnrsync-ah-jp-cu",
        "f339f3e7-5520-4268-8ca7-b0dcde7a402d": "nnrsync-ah-hk-cu",
        "c3b76a74-74d1-4077-af40-4f95d2e93f43": "nnrsync-ah-jp-cm",
        "3f6c3f59-67e5-48fb-9e61-e34e1db95227": "nnrsync-ah-hk-cm",
        "DOMAIN_ROOT": "huawei-ddns.com",
    },
    "HUAWEI_API": {
        "huawei_iam_accountname": "hwXXX",
        "huawei_iam_username": "iamname",
        "huawei_iam_password": "iampassword",
        "huawei_iam_project": "ap-southeast-3",
    },
    "HUAWEI_DNS": {
        "huawei_dns_zone_id": "xxx",
        "huawei_dns_test_domain": "test.huawei-ddns.com",
    },
}
# 获取华为云身份验证的Token
def get_XSubjectToken():
    config = CONFIG['HUAWEI_API']
    data = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "domain": {"name": config['HUAWEI_IAM_AccountName']},
                        "name": config['HUAWEI_IAM_UserName'],
                        "password": config['HUAWEI_IAM_Password']
                    }
                }
            },
            "scope": {
                "project": {
                    "name": config['HUAWEI_IAM_Project']
                }
            }
        }
    }

    url = "https://iam.myhuaweicloud.com/v3/auth/tokens"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.headers.get('X-Subject-Token')

# 从NNR API获取数据
def fetch_nnr_data():
    nnr_url = CONFIG['NNR_API']['NNR_API_URL']
    nnr_token = CONFIG['NNR_API']['NNR_API_TOKEN']
    headers = {"content-type": "application/json", "token": nnr_token}
    response = requests.post(nnr_url, headers=headers)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print("Failed to fetch data from NNR API:", response.status_code)
        return None

# 创建DNS记录
def create_dns_records():
    XSTOKEN = get_XSubjectToken()
    if not XSTOKEN:
        print("Failed to obtain token, check credentials.")
        return

    zone_id = CONFIG['HUAWEI_DNS']['HUAWEI_DNS_ZONE_ID']
    domain_root = CONFIG['DOMAIN_MAP']['DOMAIN_ROOT']
    domain_mappings = {key: value for key, value in CONFIG['DOMAIN_MAP'].items() if key != 'DOMAIN_ROOT'}
    all_records_to_delete = []

    for entry in fetch_nnr_data():
        sid = entry['sid']
        hosts = entry['host'].split(',')
        if sid in domain_mappings:
            domain_name = f"{domain_mappings[sid]}.{domain_root}"
            create_dns_record(zone_id, XSTOKEN, domain_name, hosts)

            # 处理带序号的域名（多IP地址的情况）
            suffixed_domain_names = []
            if len(hosts) > 1:
                for index, host in enumerate(hosts, start=1):
                    suffixed_domain_name = f"{domain_mappings[sid]}-{str(index).zfill(2)}.{domain_root}"
                    suffixed_domain_names.append(suffixed_domain_name)
                    create_dns_record(zone_id, XSTOKEN, suffixed_domain_name, [host])

            # 清理旧的DNS记录
            domains_to_manage = [domain_name] + suffixed_domain_names
            for domain_to_manage in domains_to_manage:
                existing_records = query_record_sets(XSTOKEN, zone_id, domain_to_manage)
                record_ids = [rec['id'] for rec in existing_records]
                latest_record_id = max(existing_records, key=lambda x: x['updated_at'])['id']
                records_to_delete = [rid for rid in record_ids if rid != latest_record_id]
                all_records_to_delete.extend(records_to_delete)

    if all_records_to_delete:
        batch_delete_record_sets(XSTOKEN, zone_id, all_records_to_delete)

# 查询DNS记录集
def query_record_sets(XSTOKEN, zone_id, domain_name):
    url = f"https://dns.myhuaweicloud.com/v2.1/zones/{zone_id}/recordsets"
    headers = {"Content-Type": "application/json", "X-Auth-Token": XSTOKEN}
    params = {"type": "A", "search_mode": "equal", "name": domain_name + '.'}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['recordsets']
    else:
        print(f"Failed to query records for {domain_name}: {response.status_code}")
        return []

# 创建单个DNS记录
def create_dns_record(zone_id, XSTOKEN, domain_name, record_values, ttl=10):
    url = f"https://dns.myhuaweicloud.com/v2.1/zones/{zone_id}/recordsets"
    data = {
        "name": domain_name + ".",
        "type": "A",
        "ttl": ttl,
        "records": record_values
    }
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": XSTOKEN
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 202:
        print(f"Record created successfully for {domain_name}: {response.json()}")
    else:
        print(f"Failed to create record for {domain_name}: {response.status_code}, {response.text}")

# 批量删除DNS记录
def batch_delete_record_sets(XSTOKEN, zone_id, record_ids):
    url = f"https://dns.myhuaweicloud.com/v2.1/zones/{zone_id}/recordsets"
    headers = {"Content-Type": "application/json", "X-Auth-Token": XSTOKEN}
    for i in range(0, len(record_ids), 100):
        batch_ids = record_ids[i:i+100]
        data = {"recordset_ids": batch_ids}
        response = requests.delete(url, headers=headers, json=data)
        if response.status_code in [200, 202, 204]:
            print(f"Successfully deleted record IDs: {', '.join(batch_ids)}")
        else:
            print(f"Failed to delete records: {response.status_code}, {response.text}")

# 主函数
def main():
    create_dns_records()

def handler(event, context):
    main()

if __name__ == "__main__":
    main()
