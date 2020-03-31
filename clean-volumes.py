import os
import json
import boto3    
import datetime
import logging

module = 'Volume Cleaner Lambda'

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.info('%s started.', module)

#Set Default Region & Account ID- Overridden by Lambda context
REGION = 'us-east-2'
ACCOUNT_ID = '12234567890'
LOCAL=True

def isProtected(volume):
    protected = False
    try:
        tags = volume.tags
        for tag in tags:
            if tag['Key'] == 'protected':
                if tag['Value'] == 'true':
                    protected = True
    except Exception as e:
        logger.warning('Volume %s has no tags defined.', volume.volume_id)
        return protected

    return protected


def deleteVolumes():
    session = boto3.session.Session(profile_name='sandbox')
    ec2 = session.resource('ec2', region_name='us-east-2')

    filters = [
        {
            'Name': 'status',
            'Values': ['available']
        }
    ]
    volumes = ec2.volumes.filter(Filters=filters)

    count=0
    for volume in volumes:
        if isProtected(volume):
            logger.info('Volume: %s protected from deletion by %s', volume.volume_id, module)
        else: 
            volume.delete()
            logger.info('Volume: %s deleted by %s', volume.volume_id, module)
            count += 1

    logger.info('%s completed. %i volumes were deleted.', module, count)

def lambda_handler(event, context):
    global REGION
    REGION=context.invoked_function_arn.split(':')[3]
    
    global ACCOUNT_ID
    ACCOUNT_ID=context.invoked_function_arn.split(":")[4]
    print(ACCOUNT_ID)
    
    global LOCAL
    LOCAL=False
    deleteVolumes()

deleteVolumes()