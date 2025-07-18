import boto3
import logging
import os
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REGION = 'ap-south-1'
BUCKET_NAME = 'my-test-bucket-' + datetime.now().strftime('%Y%m%d%H%M%S%f')
SAMPLE_FILE = 'sample.txt'
SAMPLE_CONTENT = b'Hello, S3!'
UPDATED_CONTENT = b'Hello, Updated S3!'
KEY = 'documents/sample.txt'
SUPPORTED_EXT = ['.pdf', '.jpeg', '.mpeg', '.doc', '.txt']
SAMPLE_FILES = ("C:\\Users\\sonak\\OneDrive\\Desktop\\AWS  S3")

try:
    s3 = boto3.client('s3', region_name=REGION)
    logger.info("Boto3 initialized.")
except (NoCredentialsError, ClientError) as e:
    logger.error(f"Init error: {e}")
    raise

def create_bucket(name):
    try:
        s3.create_bucket(Bucket=name, CreateBucketConfiguration={'LocationConstraint': REGION})
        s3.put_bucket_versioning(Bucket=name, VersioningConfiguration={'Status': 'Enabled'})
        logger.info(f"Bucket '{name}' created (versioned).")
    except ClientError as e:
        logger.error(f"Create bucket error: {e}")
        raise

def upload_file(bucket, path, key):
    try:
        with open(path, 'rb') as f:
            s3.upload_fileobj(f, bucket, key)
        logger.info(f"Uploaded '{path}' to '{key}'.")
    except (FileNotFoundError, ClientError) as e:
        logger.error(f"Upload error: {e}")
        raise

def list_objects(bucket):
    try:
        resp = s3.list_objects_v2(Bucket=bucket)
        objs = [obj['Key'] for obj in resp.get('Contents', [])]
        logger.info(f"Objects: {objs}")
        return objs
    except ClientError as e:
        logger.error(f"List error: {e}")
        raise

def update_file(bucket, key, content):
    try:
        s3.put_object(Bucket=bucket, Key=key, Body=content)
        logger.info(f"Updated '{key}'.")
    except ClientError as e:
        logger.error(f"Update error: {e}")
        raise

def delete_file(bucket, key):
    try:
        s3.delete_object(Bucket=bucket, Key=key)
        logger.info(f"Deleted '{key}'.")
    except ClientError as e:
        logger.error(f"Delete error: {e}")
        raise

def create_and_move_files(bucket, prefix='pictures/', files=None):
    try:
        s3.put_object(Bucket=bucket, Key=prefix)
        logger.info(f"Folder '{prefix}' created.")
        today = datetime.now().strftime('%Y-%m-%d')
        dated = f"{prefix}{today}/"
        s3.put_object(Bucket=bucket, Key=dated)
        for path in files or []:
            ext = os.path.splitext(path)[1].lower()
            if ext in SUPPORTED_EXT:
                key = os.path.basename(path)
                new_key = dated + key
                upload_file(bucket, path, new_key)
                logger.info(f"Moved '{key}' to '{new_key}'.")
            else:
                logger.warning(f"Unsupported: {path}")
    except ClientError as e:
        logger.error(f"Folder/move error: {e}")
        raise

def main():
    try:
        create_bucket(BUCKET_NAME)
        with open(SAMPLE_FILE, 'wb') as f:
            f.write(SAMPLE_CONTENT)
        upload_file(BUCKET_NAME, SAMPLE_FILE, KEY)
        list_objects(BUCKET_NAME)
        update_file(BUCKET_NAME, KEY, UPDATED_CONTENT)
        delete_file(BUCKET_NAME, KEY)
        create_and_move_files(BUCKET_NAME, files=SAMPLE_FILES)
        list_objects(BUCKET_NAME)
    except Exception as e:
        logger.error(f"Main error: {e}")
    finally:
        try:
            s3.delete_bucket(Bucket=BUCKET_NAME)
            logger.info("Bucket deleted.")
        except ClientError:
            pass

if __name__ == "__main__":
    main()