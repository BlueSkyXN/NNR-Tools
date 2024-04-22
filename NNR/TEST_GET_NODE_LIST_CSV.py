import argparse
import configparser
import requests
import json
import csv

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

def save_to_csv(data, filename='data.csv'):
    """ Save the data to a CSV file. """
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['sid', 'name', 'host'])  # Writing the headers
        for item in data:
            writer.writerow([item['sid'], item['name'], item['host']])  # Writing the data rows

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
        data = response.json().get('data', [])
        if data:
            save_to_csv(data)  # Saving the data to CSV
            print("数据已保存到 CSV 文件中.")
        else:
            print("没有数据可保存.")
    else:
        print("请求失败，HTTP 状态码:", response.status_code)
        print(response.text)

if __name__ == "__main__":
    main()
