import boto3
from botocore.exceptions import ClientError

from openvpn.utils import OpenVPNError


def get_ec2(aws_access_key_id, aws_secret_access_key, region_name):
    return boto3.client(
        'ec2',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
    )


def get_route53(aws_access_key_id, aws_secret_access_key):
    return boto3.client(
        'route53',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )


def ec2_start_instance(ec2, instance_id: str):
    try:
        ec2.start_instances(InstanceIds=[instance_id])
    except ClientError as e:
        raise OpenVPNError('ec2/start: failed') from e


def ec2_stop_instance(ec2, instance_id: str):
    try:
        ec2.stop_instances(InstanceIds=[instance_id])
    except ClientError as e:
        raise OpenVPNError('ec2/stop: failed') from e


def ec2_associate_address(ec2, instance_id: str) -> str:
    try:
        allocation = ec2.allocate_address(Domain='vpc')
    except ClientError as e:
        raise OpenVPNError('ec2/allocation: failed') from e

    try:
        ec2.associate_address(AllocationId=allocation['AllocationId'], InstanceId=instance_id)
    except ClientError as e:
        raise OpenVPNError('ec2/associate: failed') from e

    return allocation['PublicIp']


def ec2_release_address(ec2, instance_id: str) -> str:
    try:
        addresses = ec2.describe_addresses(
            Filters=[{
                'Name': 'instance-id',
                'Values': [instance_id],
            }],
        )['Addresses']
        if len(addresses) != 1:
            raise OpenVPNError('ec2/release: failed; zero or multiple addresses')
        ec2.release_address(AllocationId=addresses[0]['AllocationId'])
    except ClientError as e:
        raise OpenVPNError('ec2/release: failed') from e

    return addresses[0]['PublicIp']


def route53_create(route53, hosted_zone_id: str, domain: str, ip: str):
    try:
        route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [{
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': domain,
                        'Type': 'A',
                        'TTL': 60,
                        'ResourceRecords': [{
                            'Value': ip,
                        }],
                    },
                }],
            },
        )
    except ClientError as e:
        raise OpenVPNError('route53/create: failed') from e


def route53_delete(route53, hosted_zone_id: str, domain: str, ip: str):
    try:
        route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [{
                    'Action': 'DELETE',
                    'ResourceRecordSet': {
                        'Name': domain,
                        'Type': 'A',
                        'TTL': 60,
                        'ResourceRecords': [{
                            'Value': ip,
                        }],
                    },
                }],
            },
        )
    except ClientError as e:
        raise OpenVPNError('route53/delete: failed') from e
