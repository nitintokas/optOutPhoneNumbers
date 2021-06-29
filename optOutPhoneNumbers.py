import json
import csv
import requests
import boto3
import os
import logging
import s3fs
from botocore.exceptions import ClientError

env = {}

log = logging.getLogger()
log.setLevel(logging.INFO)

# S3 bucket info
s3 = s3fs.S3FileSystem(anon=False)

# boto3 initializations
s3_client = boto3.client("s3")
lambda_client = boto3.client("lambda")


def lambda_handler(event, context):
    global env
    print("invoked_function_arn :", context.invoked_function_arn)
    get_env(context.invoked_function_arn)
    print(env)
    bc_pages = get_pages_by_attr("AR_FILE_S3_LOCATION").json()

    for page in bc_pages["pages_list"]:
        print(page["merchant_page"])
        phone_no_list = get_sms_phone_numbers_per_request(page["merchant_page"], "MSG_SENT").json()
        print(len(phone_no_list["data"]))


def get_env(input_arn):
    global env
    if input_arn.endswith("DEV"):
        env = {"host": os.environ["BC_STAG_HOST"], "auth_key": os.environ["BC_STAG_AUTH_HEADER"], "s3_bucket": "sftp-dev.balancecollect.com"}
    elif input_arn.endswith("STAG"):
        env = {"host": os.environ["BC_STAG_HOST"], "auth_key": os.environ["BC_STAG_AUTH_HEADER"], "s3_bucket": "sftp-staging.balancecollect.com"}
    elif input_arn.endswith("PROD"):
        env = {"host": os.environ["BC_HOST"], "auth_key": os.environ["BC_AUTH_HEADER"], "s3_bucket": "sftp.balancecollect.com"}


def get_pages_by_attr(attr_type):
    request_url = env["host"] + "api/pages/attribute/" + attr_type
    return make_request("GET", request_url)


def get_sms_phone_numbers_per_request(merchant_page, status, date=None):
    request_url = env["host"] + "api/sms/numbers/" + merchant_page
    request_data = {"status": status, "dated": date}
    return make_request("POST", request_url, request_data)


def make_request(req_type: str, req_url: str, data: dict = []) -> object:
    my_headers = {'Authorization': "Bearer " + env["auth_key"]}

    if req_type == "GET":
        return requests.get(req_url, headers=my_headers)
    elif req_type == "POST":
        return requests.post(req_url, headers=my_headers, json=data)


def write_to_file(file_name, records):
    # now we will open a file for writing
    data_file = open(file_name+'.csv', 'w')

    # create the csv writer object
    csv_writer = csv.writer(data_file)

    # Counter variable used for writing
    # headers to the CSV file
    count = 0
    # Writing headers of CSV file
    csv_writer.writerow({"Phone Number"})
    count += 1
    for record in records:
        # Writing data of CSV file
        csv_writer.writerow(record.values())

    data_file.close()
