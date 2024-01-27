# Tech Communit day pulumi program workshop

import pulumi
import pulumi_aws as aws

config = pulumi.Config()

project = pulumi.get_project()
stack = pulumi.get_stack()
resource_prefix = f'{project}-{stack}'


# Get stack References
size = config.require('instance_size')
instance_count = config.require_int('instance_count')
instance_ami = config.require('ami')

# Get the Latest AMI
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["amazon"],
    filters=[aws.ec2.GetAmiFilterArgs(name="name", values=[instance_ami])],
)

#Provision SG
group = aws.ec2.SecurityGroup(
    f'{resource_prefix}-wb-sg',  #use a dynamic resource name based on the current project and stack
    description='Enable HTTP, HTTPS, SSH access',
    ingress=[
        {'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr_blocks': ['0.0.0.0/0']},
        {'protocol': 'tcp', 'from_port': 443, 'to_port': 443, 'cidr_blocks': ['0.0.0.0/0']},
        {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': ['0.0.0.0/0']},
    ],
    egress=[
        {'protocol': '-1', 'from_port': 0, 'to_port': 0, 'cidr_blocks': ['0.0.0.0/0']},
    ])


# Create multiple EC2 instances
instances = []
ips = []
hostnames = []
for i in range(instance_count):
    
    instance = aws.ec2.Instance(f'{resource_prefix}-ec2-server-{i}',
        instance_type=size,  # instance type can be changed based on requirements
        ami=ami.id,
        vpc_security_group_ids=[group.id],
        user_data="""#!/bin/bash
echo "Hello, World!" > index.html
nohup python -m SimpleHTTPServer 80 &""",
        tags={'Name': f'{resource_prefix}-ec2-{i}'})

    instances.append(instance.id)    
    ips.append(instance.public_ip)
    hostnames.append(instance.public_dns)
    
    
    
# Export the IDs and public IPs of the instances
pulumi.export('instance_ids',instances)
pulumi.export('instance_public_ips', ips)
pulumi.export('instance_public_dns',hostnames)
