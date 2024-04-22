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
    if token:
        return token
    else:
        print("X-Subject-Token not found in response headers.")
        return None

def update_record_set(XSTOKEN, zone_id, recordset_id, name, record_values, ttl=None, description=None):
    url = f"https://dns.myhuaweicloud.com/v2/zones/{zone_id}/recordsets/{recordset_id}"
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": XSTOKEN
    }
    
    data = {
        "name": name,
        "type": "A",
        "records": record_values
    }
    
    if ttl is not None:
        data["ttl"] = ttl
    
    if description is not None:
        data["description"] = description
    
    response = requests.put(url, headers=headers, data=json.dumps(data))
    
    if response.status_code in [200, 202]:
        print(f"Record set update requested successfully. Status code: {response.status_code}", response.json())
    else:
        print(f"Failed to update record set: {response.status_code}, {response.text}")

def main(config_file):
    config = read_config(config_file)
    XSTOKEN = get_XSubjectToken(config)
    
    if not XSTOKEN:
        print("Failed to obtain token, check credentials.")
        return
    
    zone_id = config.get('HUAWEI_DNS', 'HUAWEI_DNS_ZONE_ID')
    recordset_id = "ff8080828ef2300b018f041993a407f4"  # Use the actual recordset ID
    record_name = config.get('HUAWEI_DNS', 'HUAWEI_DNS_TEST_DOMAIN')
    record_values = ["1.1.1.1", "2.2.2.2"]  # Example IP addresses
    
    update_record_set(XSTOKEN, zone_id, recordset_id, record_name, record_values, ttl=3600, description="Updated description")

if __name__ == "__main__":
    config_file = 'NNR.conf'
    main(config_file)
