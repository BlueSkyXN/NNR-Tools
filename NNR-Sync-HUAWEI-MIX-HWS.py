import requests
import json
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置信息硬编码
CONFIG = {
    "NNR_API": {
        "NNR_API_URL": "https://nnr.moe/api/servers",
        "NNR_API_TOKEN": "xx-xx-xx-xx",
    },
    "DOMAIN_MAP": {
        "803D0DA0-1606-48DF-914D-34CD235D8206": "nnrsync-sh-jp-iepl",
        "7FC17AB8-CF06-4A5E-8E9B-4BB4A1F91DED": "nnrsync-sz-hk-iepl",
        "50045BA2-29C9-408C-86B5-976042645F52": "nnrsync-gz-hk-iepl-01",
        "6CF4A639-F0DD-42D3-81D7-F47E426264F6": "nnrsync-gz-hk-iepl-02",
        "0428C217-B76F-40F0-B9DF-B5FEF7BE0A34": "nnrsync-sh-jp",
        "049D691A-C65C-4E86-A79B-E32509851ADD": "nnrsync-sh-hk",
        "82EBF39A-B624-463D-A4DA-3D644A4749A9": "nnrsync-gz-hk",
        "2FD3FFD3-1BDB-424C-A9D8-487236698C29": "nnrsync-ah-jp-cu",
        "F339F3E7-5520-4268-8CA7-B0DCDE7A402D": "nnrsync-ah-hk-cu",
        "C3B76A74-74D1-4077-AF40-4F95D2E93F43": "nnrsync-ah-jp-cm",
        "3F6C3F59-67E5-48FB-9E61-E34E1DB95227": "nnrsync-ah-hk-cm",
        "DOMAIN_ROOT": "huawei-ddns.com",
    },
    "HUAWEI_API": {
        "HUAWEI_IAM_AccountName": "hwXXX",
        "HUAWEI_IAM_UserName": "iamname",
        "HUAWEI_IAM_Password": "iampassword",
        "HUAWEI_IAM_Project": "ap-southeast-3",
    },
    "HUAWEI_DNS": {
        "HUAWEI_DNS_ZONE_ID": "xxx",
        "HUAWEI_DNS_TEST_DOMAIN": "test.huawei-ddns.com",
    },
}

# 获取华为云身份验证的Token
def get_XSubjectToken(config):
    IAM_AccountName = config['HUAWEI_API']['HUAWEI_IAM_ACCOUNTNAME']
    IAM_UserName = config['HUAWEI_API']['HUAWEI_IAM_USERNAME']
    IAM_Password = config['HUAWEI_API']['HUAWEI_IAM_PASSWORD']
    IAM_Project_ID = config['HUAWEI_API']['HUAWEI_IAM_PROJECT']

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
                "project": {
                    "name": IAM_Project_ID
                }
            }
        }
    }

    url = "https://iam.myhuaweicloud.com/v3/auth/tokens"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    if response.status_code == 201:
        print("Token obtained successfully")
        return response.headers.get('X-Subject-Token')
    else:
        print(f"Failed to obtain token: {response.status_code}, {response.text}")
        return None

# 从NNR API获取数据
def fetch_nnr_data(nnr_url, nnr_token):
    headers = {"content-type": "application/json", "token": nnr_token}
    response = requests.post(nnr_url, headers=headers)
    if response.status_code == 200:
        print("NNR data fetched successfully")
        return response.json()['data']
    else:
        print(f"Failed to fetch data from NNR API: {response.status_code}, {response.text}")
        return None

# 并发创建DNS记录的任务
def create_dns_record_task(zone_id, XSTOKEN, domain_name, record_values, record_type):
    create_dns_record(zone_id, XSTOKEN, domain_name, record_values, record_type=record_type)

# 创建DNS记录
def create_dns_records(config, nnr_data):
    XSTOKEN = get_XSubjectToken(config)
    if not XSTOKEN:
        print("Failed to obtain token, check credentials.")
        return

    zone_id = config['HUAWEI_DNS']['HUAWEI_DNS_ZONE_ID']
    domain_root = config['DOMAIN_MAP']['DOMAIN_ROOT']
    domain_mappings = {key: value for key, value in config['DOMAIN_MAP'].items() if key != 'DOMAIN_ROOT'}
    all_records_to_delete = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_domain = {}
        for entry in nnr_data:
            sid = entry['sid']
            hosts = entry['host'].split(',')
            if sid in domain_mappings:
                domain_name = f"{domain_mappings[sid]}.{domain_root}"
                domain_name_v4 = f"{domain_mappings[sid]}-v4.{domain_root}"
                domain_name_v6 = f"{domain_mappings[sid]}-v6.{domain_root}"
                ipv4_hosts = [host for host in hosts if is_ipv4(host)]
                ipv6_hosts = [host for host in hosts if is_ipv6(host)]

                if ipv4_hosts:
                    future_to_domain[executor.submit(create_dns_record_task, zone_id, XSTOKEN, domain_name, ipv4_hosts, "A")] = domain_name
                    future_to_domain[executor.submit(create_dns_record_task, zone_id, XSTOKEN, domain_name_v4, ipv4_hosts, "A")] = domain_name_v4
                if ipv6_hosts:
                    future_to_domain[executor.submit(create_dns_record_task, zone_id, XSTOKEN, domain_name, ipv6_hosts, "AAAA")] = domain_name
                    future_to_domain[executor.submit(create_dns_record_task, zone_id, XSTOKEN, domain_name_v6, ipv6_hosts, "AAAA")] = domain_name_v6

                # 处理带序号的域名（多IP地址的情况）
                for index, host in enumerate(hosts, start=1):
                    suffixed_domain_name = f"{domain_mappings[sid]}-{str(index).zfill(2)}.{domain_root}"
                    if is_ipv4(host):
                        future_to_domain[executor.submit(create_dns_record_task, zone_id, XSTOKEN, suffixed_domain_name, [host], "A")] = suffixed_domain_name
                    elif is_ipv6(host):
                        future_to_domain[executor.submit(create_dns_record_task, zone_id, XSTOKEN, suffixed_domain_name, [host], "AAAA")] = suffixed_domain_name

                # 清理旧的DNS记录
                domains_to_manage = [domain_name, domain_name_v4, domain_name_v6] + [f"{domain_mappings[sid]}-{str(index).zfill(2)}.{domain_root}" for index in range(1, len(hosts)+1)]
                for domain_to_manage in domains_to_manage:
                    existing_records = query_record_sets(XSTOKEN, zone_id, domain_to_manage)
                    records_to_delete = identify_records_to_delete(existing_records)
                    all_records_to_delete.extend(records_to_delete)

        for future in as_completed(future_to_domain):
            domain_name = future_to_domain[future]
            try:
                future.result()
                print(f"Successfully created DNS record for {domain_name}")
            except Exception as exc:
                print(f"Failed to create DNS record for {domain_name} generated an exception: {exc}")

    if all_records_to_delete:
        batch_delete_record_sets(XSTOKEN, zone_id, all_records_to_delete)

# 判断是否为IPv4地址
def is_ipv4(address):
    try:
        return type(ipaddress.ip_address(address)) is ipaddress.IPv4Address
    except ValueError:
        return False

# 判断是否为IPv6地址
def is_ipv6(address):
    try:
        return type(ipaddress.ip_address(address)) is ipaddress.IPv6Address
    except ValueError:
        return False

# 查询DNS记录集
def query_record_sets(XSTOKEN, zone_id, domain_name):
    record_types = ["A", "AAAA"]
    all_records = []
    for record_type in record_types:
        url = f"https://dns.myhuaweicloud.com/v2.1/zones/{zone_id}/recordsets"
        headers = {"Content-Type": "application/json", "X-Auth-Token": XSTOKEN}
        params = {"type": record_type, "search_mode": "equal", "name": domain_name + '.'}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            all_records.extend(response.json()['recordsets'])
        else:
            print(f"Failed to query {record_type} records for {domain_name}: {response.status_code}")
    return all_records

# 识别要删除的记录
def identify_records_to_delete(existing_records):
    records_to_delete = []
    records_by_type = {"A": [], "AAAA": []}
    for record in existing_records:
        records_by_type[record['type']].append(record)
    for record_type, records in records_by_type.items():
        if records:
            latest_record = max(records, key=lambda x: x['updated_at'])
            records_to_delete.extend([record['id'] for record in records if record['id'] != latest_record['id']])
    return records_to_delete

# 创建单个DNS记录
def create_dns_record(zone_id, XSTOKEN, domain_name, record_values, record_type="A", ttl=10):
    url = f"https://dns.myhuaweicloud.com/v2.1/zones/{zone_id}/recordsets"
    data = {
        "name": domain_name + ".",
        "type": record_type,
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
    config = CONFIG
    nnr_url, nnr_token = config['NNR_API']['NNR_API_URL'], config['NNR_API']['NNR_API_TOKEN']
    nnr_data = fetch_nnr_data(nnr_url, nnr_token)
    if nnr_data:
        create_dns_records(config, nnr_data)

# 云函数入口
def handler(event, context):
    main()
