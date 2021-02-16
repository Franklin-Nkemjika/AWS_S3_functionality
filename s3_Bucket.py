import boto3
import logging
import datetime
import botocore
from botocore.exceptions import ClientError


def list_bucket_objects_item():
    """List the objects in an Amazon S3 bucket
        :param bucket_name: string
        :param object name: string
        :return: List of bucket objects. If error, return None.
        """
    s3 = boto3.resource('s3')
    try:
        for bucket in s3.buckets.all():
            # Get a list of all bucket names
            print("Name: {0} ".format(bucket.name))
            for object in bucket.objects.all():
                # Get a list of all the keys names
                print("Object: {}".format(object))
    except ClientError as e:
        # AllAccessDisabled error == bucket not found
        logging.error(e)
        return None
  
   
def create_bucket():
    """Create an S3 bucket in a specified region
    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).
    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-east-1'
    :return: True if bucket created, else False
    """
    # Create bucket
    s3_resource = boto3.resource('s3')
    s3_connection = s3_resource.meta.client
    session = boto3.session.Session()
    current_region = session.region_name
    bucket_name = input("Create unique bucket Name : ")
    try:
        if current_region == 'us-east-1':
            s3_connection.create_bucket(Bucket=bucket_name)
        else:
            s3_connection.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
                'LocationConstraint': current_region})
        s3_client = boto3.client('s3')
        s3_client.put_public_access_block(Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print(bucket_name, current_region)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def put_object(dest_bucket_name, dest_object_name, src_data):
    """Add an object to an Amazon S3 bucket
        The src_data argument must be of type bytes or a string that references
        a file specification.
        :param dest_bucket_name: string
        :param dest_object_name: string
        :param src_data: bytes of data or string reference to file spec
        :return: True if src_data was added to dest_bucket/dest_object, otherwise
        False
        """
    # Construct Body= parameter
    if isinstance(src_data, bytes):
        object_data = src_data
    elif isinstance(src_data, str):
        try:
            object_data = open(src_data, 'rb')
            # possible FileNotFoundError/IOError exception
        except Exception as e:
            logging.error(e)
            return False
    else:
        logging.error('Type of ' + str(type(src_data)) +
                      ' for the argument \'src_data\' is not supported.')
        return False
    # Put the object
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=dest_bucket_name, Key=dest_object_name, Body=object_data)
        print("{0} has been successfully put to bucket {1}".format(object_data,dest_bucket_name))
    except ClientError as e:
        # AllAccessDisabled error == bucket not found
        # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
        logging.error(e)
        return False
    finally:
        if isinstance(src_data, str):
            object_data.close()
    return True


def delete_object_item(bucket_name):
    """Delete an object from an S3 bucket
    :param bucket_name: string
    :param object_name: string
    :return: True if the referenced object was deleted, otherwise False
    """
    s3_client = boto3.client('s3')
    try:
        # delete bucket objects
        object_name = input("Enter Object Name : ")
        s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        print("Object name : {} was deleted".format(object_name))
    except ClientError as e:
        logging.error(e)
        return False
    return True


def delete_bucket():
    """Delete an empty S3 bucket
    If the bucket is not empty, the operation fails.
    :param bucket_name: string
    :return: True if the referenced bucket was deleted, otherwise False
    """
    # Delete the bucket
    s3_client = boto3.client('s3')
    try:
        # Get a list of all bucket names from the response
        s3 = boto3.resource('s3')
        for bucket in s3.buckets.all():
            print("Bucket Name: {}".format(bucket.name))
        bucket_name = input("Enter bucket : ")
        s3_client.delete_bucket(Bucket=bucket_name)
        print("Bucket name : {0} was deleted".format(bucket_name))
    except ClientError as e:
        logging.error(e)
        return False
    return True


def copy_object():
    """Copy an Amazon S3 bucket object
            :param bucket_to_name: string
            :param object_to_name: string
            :param bucket_from_name: string. Must already exist.
            :return: True if object was copied, otherwise False
            """
    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        print("Name: {0} ".format(bucket.name))
        for object in bucket.objects.all():
            print("Object: {}".format(object))
    bucket_from_name = input("Copy from Bucket : ")
    bucket_to_name = input("Copy to Bucket : ")
    file_name = input("Enter file name : ")
    dest_object_name = None
    # Construct source bucket/object parameter
    copy_source = {'Bucket': bucket_from_name, 'Key': file_name}
    if dest_object_name is None:
        dest_object_name = bucket_from_name
    # Copy the object1
    try:
        s3_client = boto3.client('s3')
        s3_client.copy_object(CopySource=copy_source,Bucket=bucket_to_name,Key=file_name)
        print("{0} was successfully copied to bucket {1}".format(file_name,bucket_to_name))
    except ClientError as e:
        logging.error(e)
        return False
    return True


def download_object():
    """Download an object from an S3 bucket
    :param bucket_name: string
    :param object_name: string
    :return: True if the referenced object was downloaded, otherwise False
    """
    bucket_name = input("Bucket Name : ")
    object_name = input("object Name : ")
    key = input("Save file with : ")
    s3 = boto3.resource('s3')
    try:
      s3.Bucket(bucket_name).download_file(object_name, key)
      print("{} was successfully download to ec2 user environment.".format(key))
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

#Main 
def main():
    print("Welcome to AWS s3 application.")
    menu = {"0 : Exit the program.",
            "1 : Display available Buckets.",
            "2 : Create Buckets.",
            "3 : Put Object.",
            "4 : Delete Object",
            "5 : Delete Bucket.",
            "6 : Copies Object.",
            "7 : Download Object.",
            }
    for val in sorted(menu):
        print(val)


main()
while True:
    UserInput = str(input("Select a menu : "))
    if UserInput == "0":
        e = datetime.datetime.now()
        print(e.strftime("%I:%M:%S %p"))
        print(e.strftime("%a, %b %d, %Y"))
        break

    if UserInput == "1":
        list_bucket_objects_item()

    if UserInput == "2":
        create_bucket()

    if UserInput == "3":
        list_bucket_objects_item()
        dest_bucket_name = input("Enter Bucket Name : ")
        dest_object_name = input("Enter object Name : ")
        scr_data = input("File description : ")
        put_object(dest_bucket_name, dest_object_name, scr_data)

    if UserInput == "4":
        list_bucket_objects_item()
        delete_object_item(bucket_name=input("Enter Bucket : "))

    if UserInput == "5":
        delete_bucket()

    if UserInput == "6":
        copy_object()

    if UserInput == "7":
        list_bucket_objects_item()
        download_object()
