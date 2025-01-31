#!/usr/bin/env python

import boto3
import argparse
import json
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def get_ec2_instances():
    """Fetches all EC2 instances using boto3."""
    try:
        ec2 = boto3.client('ec2', region_name='us-west-2')  # Specify your region
        response = ec2.describe_instances()

        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append(instance)

        return instances

    except NoCredentialsError:
        print("AWS credentials not found. Please configure your AWS credentials.")
        exit(1)
    except PartialCredentialsError:
        print("Incomplete AWS credentials. Please check your AWS configuration.")
        exit(1)

def parse_instances(instances):
    """
    Parse EC2 instance data into Ansible inventory format.
    
    Returns:
        dict: Ansible inventory format.
    """
    inventory = {
        'all': {
            'hosts': [],
            'vars': {}
        },
        '_meta': {
            'hostvars': {}
        }
    }

    for instance in instances:
        instance_id = instance['InstanceId']
        public_ip = instance.get('PublicIpAddress')

        # Skip instances that do not have a public IP address
        if not public_ip:
            continue

        # Add the instance to the list of all hosts
        inventory['all']['hosts'].append(instance_id)
        
        # Add host variables
        inventory['_meta']['hostvars'][instance_id] = {
            'ansible_host': public_ip,
            'private_ip': instance.get('PrivateIpAddress'),
            'instance_type': instance.get('InstanceType'),
            'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        }

        # Grouping by tags
        for tag in instance.get('Tags', []):
            key = tag['Key']
            value = tag['Value']
            group_name = f'tag_{key}_{value}'

            if group_name not in inventory:
                inventory[group_name] = {'hosts': []}

            inventory[group_name]['hosts'].append(instance_id)

        # Group by instance type
        instance_type = instance.get('InstanceType')
        if instance_type:
            group_name = f'instance_type_{instance_type}'
            if group_name not in inventory:
                inventory[group_name] = {'hosts': []}
            inventory[group_name]['hosts'].append(instance_id)

        # Group by availability zone
        availability_zone = instance['Placement']['AvailabilityZone']
        if availability_zone:
            group_name = f'zone_{availability_zone}'
            if group_name not in inventory:
                inventory[group_name] = {'hosts': []}
            inventory[group_name]['hosts'].append(instance_id)

    return inventory

def main():
    """
    Main function to execute the dynamic inventory script.
    """
    parser = argparse.ArgumentParser(description="Ansible Dynamic Inventory Script for AWS EC2")
    parser.add_argument('--list', action='store_true', help='List all instances in inventory')
    parser.add_argument('--host', help='Get detailed information for a specific host')
    args = parser.parse_args()

    instances = get_ec2_instances()
    inventory = parse_instances(instances)

    if args.list:
        print(json.dumps(inventory, indent=2))
    elif args.host:
        print(json.dumps(inventory['_meta']['hostvars'].get(args.host, {}), indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

