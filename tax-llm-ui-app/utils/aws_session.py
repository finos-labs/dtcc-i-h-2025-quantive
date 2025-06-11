import boto3
import os

def get_boto3_resource(service, region_name="us-west-2"):
    session = boto3.Session(region_name=region_name)
    return session.resource(service)

def get_boto3_client(service, region_name="us-east-1"):
    session = boto3.Session(region_name=region_name)
    return session.client(service)