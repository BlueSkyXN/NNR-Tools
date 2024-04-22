import requests
import json
import configparser
import argparse

def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def get_XSubjectToken(config):
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
                   "project": {
                    "name": IAM_Project_ID
               }
            }
        }
    }

    url = "https://iam.myhuaweicloud.com/v3/auth/tokens"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.headers.get('X-Subject-Token')

def fetch_nnr_data(nnr_url, nnr_token):
    headers = {"content-type": "application/json", "token": nnr_token}
    response = requests.post(nnr_url, headers=headers)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print("Failed to fetch data from NNR API:", response.status_code)
        return None

def create_dns_records(config, nnr_data):
    XSTOKEN = get_XSubjectToken(config)
    if not XSTOKEN:
        print("Failed to obtain token, check credentials.")
        return

    zone_id = config.get('HUAWEI_DNS', 'HUAWEI_DNS_ZONE_ID')
    domain_root = config['DOMAIN_MAP']['DOMIAN_ROOT']
    domain_mappings = {key: value for key, value in config['DOMAIN_MAP'].items() if key != 'DOMIAN_ROOT'}

    for entry in nnr_data:
        sid = entry['sid']
        hosts = entry['host'].split(',')
        if sid in domain_mappings:
            domain_name = f"{domain_mappings[sid]}.{domain_root}"
            create_dns_record(zone_id, XSTOKEN, domain_name, hosts)

def create_dns_record(zone_id, XSTOKEN, domain_name, record_values, ttl=300):
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

def setup_argparse():
    parser = argparse.ArgumentParser(description="Manage DNS records based on NNR API data")
    parser.add_argument('-c', '--config', type=str, default='NNR.conf', help='Path to configuration file')
    return parser.parse_args()

def main():
    args = setup_argparse()
    config = read_config(args.config)

    nnr_url, nnr_token = config['NNR_API']['NNR_API_URL'], config['NNR_API']['NNR_API_TOKEN']
    nnr_data = fetch_nnr_data(nnr_url, nnr_token)
    if nnr_data:
        create_dns_records(config, nnr_data)

if __name__ == "__main__":
    main()
