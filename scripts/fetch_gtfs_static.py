import os
import sys
from datetime import date
import requests
import boto3


def main():
    day = sys.argv[1] if len(sys.argv) > 1 else date.today().strftime('%Y%m%d')
    api_key = os.getenv('TFNSW_API_KEY')
    if not api_key:
        raise RuntimeError('TFNSW_API_KEY not set')

    url = f'https://api.transport.nsw.gov.au/v1/gtfs/schedule/{day}'
    headers = {'Authorization': f'apikey {api_key}'}
    resp = requests.get(url, headers=headers, timeout=60)
    resp.raise_for_status()

    filename = f'gtfs_{day}.zip'
    with open(filename, 'wb') as f:
        f.write(resp.content)

    s3 = boto3.client(
        "s3",
        endpoint_url=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
        aws_access_key_id=os.getenv(
            "MINIO_ROOT_USER", os.getenv("AWS_ACCESS_KEY_ID")
        ),
        aws_secret_access_key=os.getenv(
            "MINIO_ROOT_PASSWORD", os.getenv("AWS_SECRET_ACCESS_KEY")
        ),
        region_name="us-east-1",
    )
    s3.upload_file(filename, 'stp', f'gtfs_static/{day}.zip')
    print(f'Uploaded {filename} to s3://stp/gtfs_static/{day}.zip')


if __name__ == '__main__':
    main()
