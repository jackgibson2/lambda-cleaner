import os
import json
import boto3

REGION = 'us-east-2'

session = boto3.session.Session(profile_name='sandbox')

#iam = boto3.resource('iam', region_name=REGION)

policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "ec2:DeleteVolume",
            "Resource": "arn:aws:ec2:us-east-2:xxxxx:volume/*"
        },
        {
            "Effect": "Allow",
            "Action": "ec2:DeleteSnapshot",
            "Resource": "arn:aws:ec2:us-east-2:xxxxx:snapshot/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "autoscaling:SetDesiredCapacity",
                "ssm:DescribeParameters",
                "autoscaling:DescribeAutoScalingGroups",
                "ec2:DescribeVolumes",
                "ec2:DescribeSnapshots"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "ssm:GetParameters",
            "Resource": "arn:aws:ssm:us-east-2:xxxxx:parameter/mysandbox/*"
        },
        {
            "Effect": "Allow",
            "Action": "ssm:PutParameter",
            "Resource": "arn:aws:ssm:us-east-2:xxxxx:parameter/mysandbox/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:TerminateInstances",
                "ec2:StopInstances"
            ],
            "Resource": "arn:aws:ec2:us-east-2:xxxxx:instance/*"
        }
    ]
}

parameterRoot = '/AccountCleaner/'
retentionDays = 7

ssm = session.client('ssm', region_name=REGION)
ssm.put_parameter(
    Name=parameterRoot + 'retentionDays',
    Description='Days to retain snapsots',
    Value=str(retentionDays),
    Type='String',
    Overwrite=True)

ssm.put_parameter(
    Name=parameterRoot + 'Enalbed',
    Description='Flag to turn off cleaner lambdas globally',
    Value='True',
    Type='String',
    Overwrite=True)

ssm.put_parameter(
    Name=parameterRoot + 'DryRun',
    Description='Flag to turn dry run on for cleaner lambdas globally',
    Value='False',
    Type='String',
    Overwrite=True)