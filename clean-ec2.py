import json
import boto3    
import logging

module = 'EC2 Instance Cleaner Lambda'

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.info('%s started.', module)

#Set Default Region & Account ID- Overridden by Lambda context
REGION = 'us-east-2'
ACCOUNT_ID = '12234567890'
LOCAL=True

def deleteEC2Instances():
    if LOCAL:
        session = boto3.session.Session(profile_name='sandbox')
    else:
        session = boto3.session.Session()

    ec2 = session.resource('ec2', region_name=REGION)

    filters = [
        {
            'Name': 'instance-state-name',
            'Values': ['running']
        }
    ]
    instances =  ec2.instances.filter(Filters=filters)

    count=0
    for instance in instances:
        protected = False
        try:
            for tag in instance.tags:
                if tag["Key"] == 'protected':
                    if tag["Value"] == 'true':
                        logger.info('Instance %s is protected, skipping.', instance.id)
                        protected = True
                if tag["Key"] == 'aws:autoscaling:groupName':
                        logger.info('Instance %s is part of an Auto-Scaling Group, skipping.', instance.id)
                        protected = True
        except Exception as e:
            logger.warning('Instance %s has no tags defined.', instance.id)
            protected = False
                
        if protected == False:
            instance.terminate()
            logger.info('Instance %s terminated by %s.', instance.id, module)
            count += 1

    logger.info('%s completed. %i ec2 instances were terminated.', module, count)

def lambda_handler(event, context):
    global REGION
    REGION=context.invoked_function_arn.split(':')[3]
    
    global ACCOUNT_ID
    ACCOUNT_ID=context.invoked_function_arn.split(":")[4]
    print(ACCOUNT_ID)
    
    global LOCAL
    LOCAL=False

    deleteEC2Instances()

deleteEC2Instances()