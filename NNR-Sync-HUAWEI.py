import requests
import json
import configparser
import argparse

def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def get_XSubjectToken(config):
    # 从配置文件中获取IAM账户信息以及项目信息
    IAM_AccountName = config.get('HUAWEI_API', 'HUAWEI_IAM_AccountName')
    IAM_UserName = config.get('HUAWEI_API', 'HUAWEI_IAM_UserName')
    IAM_Password = config.get('HUAWEI_API', 'HUAWEI_IAM_Password')
    IAM_Project_ID = config.get('HUAWEI_API', 'HUAWEI_IAM_Project')

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
                "project": {"name": IAM_Project_ID}
            }
        }
    }

    url = "https://iam.myhuaweicloud.com/v3/auth/tokens"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.headers.get('X-Subject-Token')

def create_dns_record(zone_id, X_Auth_Token, record_name, record_values, ttl=300):
    url = f"https://dns.myhuaweicloud.com/v2.1/zones/{zone_id}/recordsets"
    data = {
        "name": record_name + ".",
        "type": "A",
        "ttl": ttl,
        "records": record_values.split(',')
    }
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": X_Auth_Token
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 202:
        print(f"Record created successfully for {record_name}: {response.json()}")
    else:
        print(f"Failed to create record for {record_name}: {response.status_code}, {response.text}")

def setup_argparse():
    parser = argparse.ArgumentParser(description="Manage DNS records based on NNR API data")
    parser.add_argument('-c', '--config', type=str, default='NNR.conf', help='Path to configuration file')
    return parser.parse_args()

def main():
    args = setup_argparse()
    config = read_config(args.config)

    # Load API configuration and domain mappings
    nnr_url, nnr_token = config['NNR_API']['NNR_API_URL'], config['NNR_API']['NNR_API_TOKEN']
    domain_root = config['DOMAIN_MAP']['DOMIAN_ROOT']
    domain_mappings = {key: value for key, value in config['DOMAIN_MAP'].items() if key != 'DOMIAN_ROOT'}

    # Prepare headers for NNR API
    headers = {"content-type": "application/json", "token": nnr_token}

    # Request NNR API
    response = requests.post(nnr_url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch data from NNR API:", response.status_code)
        return

    # Get token for Huawei Cloud DNS operations
    XSTOKEN = get_XSubjectToken(config)
    if not XSTOKEN:
        print("Failed to obtain Huawei Cloud token.")
        return

    zone_id = config.get('HUAWEI_DNS', 'HUAWEI_DNS_ZONE_ID')
    data = response.json()['data']

    # Process each entry from NNR API response
    for entry in data:
        sid = entry['sid']
        hosts = entry['host']
        if sid in domain_mappings:
            domain_name = domain_mappings[sid] + '.' + domain_root
            create_dns_record(zone_id, XSTOKEN, domain_name, hosts)

if __name__ == "__main__":
    main()
