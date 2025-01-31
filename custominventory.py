#!/usr/bin/python3
#!/usr/bin/env python

import boto3
import argparse
import json

def get_instances():
    """Fetches all EC2 instances."""
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()

    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance)

    return instances

def parse_instances(instances):
    """Parse instances into Ansible inventory format."""
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

        if public_ip:
            inventory['all']['hosts'].append(instance_id)
            inventory['_meta']['hostvars'][instance_id] = {
                'ansible_host': public_ip,
                'private_ip': instance.get('PrivateIpAddress'),
                'instance_type': instance.get('InstanceType'),
                'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            }

            # Add grouping by tag
            for tag in instance.get('Tags', []):
                key = tag['Key']
                value = tag['Value']
                group_name = f'tag_{key}_{value}'

                if group_name not in inventory:
                    inventory[group_name] = {'hosts': []}

                inventory[group_name]['hosts'].append(instance_id)

    return inventory

def main():
    parser = argparse.ArgumentParser(description="Ansible Dynamic Inventory Script for AWS EC2")
    parser.add_argument('--list', action='store_true', help='List instances')
    parser.add_argument('--host', help='Get variables for a specific host')
    args = parser.parse_args()

    instances = get_instances()
    inventory = parse_instances(instances)

    if args.list:
        print(json.dumps(inventory, indent=2))
    elif args.host:
        print(json.dumps(inventory['_meta']['hostvars'].get(args.host, {}), indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

