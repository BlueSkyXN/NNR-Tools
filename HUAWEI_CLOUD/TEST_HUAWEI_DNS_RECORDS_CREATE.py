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
    token = response.headers.get('X-Subject-Token')
    if token:
        #print(token)
        return token
    else:
        print("X-Subject-Token not found in response headers.")
        return None

def create_dns_record(zone_id, X_Auth_Token, record_name, record_values, ttl=1):
    url = f"https://dns.myhuaweicloud.com/v2/zones/{zone_id}/recordsets"
    data = {
        "name": record_name,
        "type": "A",
        "ttl": ttl,
        "records": record_values
    }
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": X_Auth_Token
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 202:
        print("Record created successfully:", response.json())
    else:
        print("Failed to create record:", response.status_code, response.text)

def main(config_file):
    config = read_config(config_file)
    XSTOKEN = get_XSubjectToken(config)
    if not XSTOKEN:
        print("Token acquisition failed, check your credentials.")
        return

    zone_id = config.get('HUAWEI_DNS', 'HUAWEI_DNS_ZONE_ID')
    HUAWEI_DNS_TEST_DOMAIN = config.get('HUAWEI_DNS', 'HUAWEI_DNS_TEST_DOMAIN')
    record_name = HUAWEI_DNS_TEST_DOMAIN
    record_values = ["1.1.1.1", "2.2.2.2"]

    create_dns_record(zone_id, XSTOKEN, record_name, record_values)

if __name__ == "__main__":
    config_file = 'NNR.conf'
    main(config_file)
