import requests
import json
import socket
import ipaddress
from datetime import datetime

# 配置信息硬编码
CONFIG = {

}

# 获取华为云身份验证的Token
def get_XSubjectToken(config):
    IAM_AccountName = config['HUAWEI_API']['huawei_iam_accountname']
    IAM_UserName = config['HUAWEI_API']['huawei_iam_username']
    IAM_Password = config['HUAWEI_API']['huawei_iam_password']
    IAM_Project_ID = config['HUAWEI_API']['huawei_iam_project']

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

# 检查 TCP 连通性
def check_tcp_connectivity(host, port, retries=3, timeout=1):
    for attempt in range(retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.close()
            return True
        except socket.error:
            continue
    return False

# 获取 DNS 记录
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

# 创建单个 DNS 记录
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

# 批量删除 DNS 记录
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

# 判断是否为 IPv4 地址
def is_ipv4(address):
    try:
        return type(ipaddress.ip_address(address)) is ipaddress.IPv4Address
    except ValueError:
        return False

# 判断是否为 IPv6 地址
def is_ipv6(address):
    try:
        return type(ipaddress.ip_address(address)) is ipaddress.IPv6Address
    except ValueError:
        return False

# 主函数
def main():
    config = CONFIG
    domain_root = config['DOMAIN_MAP']['domain_root']
    domain_port_map = config['DOMAIN_PORT_MAP']

    XSTOKEN = get_XSubjectToken(config)
    if not XSTOKEN:
        print("Failed to obtain token, check credentials.")
        return

    zone_id = config['HUAWEI_DNS']['huawei_dns_zone_id']

    for full_domain, prefix in domain_port_map.items():
        domain, port = full_domain.split(':')
        port = int(port)
        domain_name_v4 = f"{domain}"
        print(f"Checking domain: {domain_name_v4} with port {port}")

        records = query_record_sets(XSTOKEN, zone_id, domain_name_v4)
        valid_ips = []

        for record in records:
            for ip in record['records']:
                if check_tcp_connectivity(ip, port, retries=2, timeout=1):
                    valid_ips.append(ip)

        if valid_ips:
            target_domain = f"{prefix}.{domain_root}"
            create_dns_record(zone_id, XSTOKEN, target_domain, valid_ips, record_type="A")

            existing_records = query_record_sets(XSTOKEN, zone_id, target_domain)
            records_to_delete = identify_old_records(existing_records)
            if records_to_delete:
                batch_delete_record_sets(XSTOKEN, zone_id, records_to_delete)
        else:
            print(f"No valid IPs found for {domain_name_v4}, keeping existing records.")

# 识别要删除的记录，保留最新的记录
def identify_old_records(records):
    latest_record = max(records, key=lambda x: datetime.strptime(x['created_at'], "%Y-%m-%dT%H:%M:%S.%f"))
    return [record['id'] for record in records if record['id'] != latest_record['id']]

# 云函数入口
def handler(event, context):
    main()

if __name__ == "__main__":
    main()
