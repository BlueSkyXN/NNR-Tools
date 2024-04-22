import argparse
import configparser
import requests
import json

def load_config(file_path):
    """ Load API configuration from a file. """
    config = configparser.ConfigParser()
    config.read(file_path)
    return config['NNR_API']['NNR_API_URL'], config['NNR_API']['NNR_API_TOKEN']

def setup_argparse():
    """ Setup command line argument parsing. """
    parser = argparse.ArgumentParser(description="Fetch data from NNR API")
    parser.add_argument('-c', '--config', type=str, default='NNR.conf', help='Path to configuration file')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = setup_argparse()

    # Load configuration
    url, token = load_config(args.config)

    # Headers with your authentication token
    headers = {
        "content-type": "application/json",
        "token": token  # Your API token from configuration file
    }

    # Sending the POST request without proxy
    response = requests.post(url, headers=headers)

    # Checking the response
    if response.status_code == 200:
        data = response.json()
        #print("成功获取节点列表:")
        #print(json.dumps(data, indent=4))
        print(response.text)
    else:
        print("请求失败，HTTP 状态码:", response.status_code)
        print(response.text)

if __name__ == "__main__":
    main()
