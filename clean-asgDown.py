import json
import boto3    
import logging

module = 'ASG Scale Down Cleaner Lambda'

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.info('%s started.', module)

#Set Default Region & Account ID- Overridden by Lambda context
REGION = 'us-east-2'
ACCOUNT_ID = '12234567890'
LOCAL=True

def isProtected(asg):
    protected = False
    try:
        tags = asg['Tags']
        for tag in tags:
            if tag['Key'] == 'protected':
                if tag['Value'] == 'true':
                    protected = True
    except Exception as e:
        logger.warning('Volume %s has no tags defined.', asg['AutoScalingGroupName'])
        return protected

    return protected


def scaleDown():
    if LOCAL:
        session = boto3.session.Session(profile_name='sandbox')
    else:
        session = boto3.session.Session()
    
    #Needs driven by parameter store in SSM witin a different function
    ssm = session.client('ssm', region_name=REGION)
    parameterRoot = '/mysandbox/'

    autoscaling = session.client('autoscaling', region_name=REGION)
    groups =  autoscaling.describe_auto_scaling_groups();
    
    count=0
    for asg in groups['AutoScalingGroups']:
        if isProtected(asg):
            logger.info('Auto-Scaling Group: %s protected from deletion by %s', asg['AutoScalingGroupName'], module)
        else:
            logger.info('Scaling down the Auto-Scaling Group: %s', asg['AutoScalingGroupName'])
            asgName = asg['AutoScalingGroupName']
            desiredCapacity = asg['DesiredCapacity']
            minSize = asg['MinSize']
            
            #Make sure address minmimum less than equal to desired
            parameterKey = parameterRoot + asgName + '/DesiredCapacity'
            ssm.put_parameter(
                Name=parameterKey,
                Description='Original Desired Capacity Prior to Scale Down',
                Value=str(desiredCapacity),
                Type='String',
                Overwrite=True)
                
            response = autoscaling.set_desired_capacity(
                AutoScalingGroupName=asgName,
                DesiredCapacity=minSize,
                HonorCooldown=False)
            count+=1

    logger.info('%s completed. %i Auto-Scaling Groups were updated.', module, count)


def lambda_handler(event, context):
    global REGION
    REGION=context.invoked_function_arn.split(':')[3]
    
    global ACCOUNT_ID
    ACCOUNT_ID=context.invoked_function_arn.split(":")[4]
    
    global LOCAL
    LOCAL=False
    
    scaleDown()

scaleDown()