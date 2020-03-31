import os
import json
import boto3    
import datetime
import logging
from _datetime import timezone

module = 'Snapshot Cleaner Lambda'

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.info('%s started.', module)

#Set Default Region & Account ID- Overridden by Lambda context
REGION = 'us-east-2'
ACCOUNT_ID = '12234567890'
LOCAL=True


def isProtected(snapshot):
    protected = False
    try:
        tags = snapshot.tags
        for tag in tags:
            if tag['Key'] == 'protected':
                if tag['Value'] == 'true':
                    protected = True
    except Exception as e:
        logger.warning('Snapshot %s has no tags defined.', snapshot.snapshot_id)
        return protected

    return protected

def deleteSnapshots():
    if LOCAL:
        session = boto3.session.Session(profile_name='sandbox')
    else:
        session = boto3.session.Session()

    now_utc = datetime.datetime.now(timezone.utc)
    retentionDatetime = now_utc - datetime.timedelta(minutes=5)

    ec2 = session.resource('ec2', region_name=REGION)

    filters = [
        {
            'Name': 'owner-id',
            'Values': [ACCOUNT_ID]
        }
    ]
    snapshots = ec2.snapshots.filter(Filters=filters)
    
    count=0
    for snapshot in snapshots:
        if isProtected(snapshot):
            logger.info('Snapshot: %s protected from deletion by %s', snapshot.snapshot_id, module)
        else:
            if snapshot.start_time < retentionDatetime:
                snapshot.delete()
                logger.info('Snapshot: %s deleted by %s', snapshot.snapshot_id, module)
                count+=1
            else:
                logger.info('Snapshot: %s within retention period', snapshot.snapshot_id)
    
    logger.info('%s completed. %i snapshots were deleted.', module, count)

def lambda_handler(event, context):
    global REGION
    REGION=context.invoked_function_arn.split(':')[3]
    
    global ACCOUNT_ID
    ACCOUNT_ID=context.invoked_function_arn.split(":")[4]
    print(ACCOUNT_ID)
    
    global LOCAL
    LOCAL=False
    
    deleteSnapshots()

deleteSnapshots()