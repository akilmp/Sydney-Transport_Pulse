import os
import sys
from datetime import date
from pathlib import Path

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

    filename = Path(f"gtfs_{day}.zip")
    with filename.open("wb") as f:
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

    bucket = "stp"
    key = f"gtfs_static/{day}.zip"

    try:
        s3.head_bucket(Bucket=bucket)
    except s3.exceptions.ClientError:
        s3.create_bucket(Bucket=bucket)

    s3.upload_file(str(filename), bucket, key)
    print(f"Uploaded {filename} to s3://{bucket}/{key}")
    filename.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
