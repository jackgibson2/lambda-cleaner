import json
import boto3    
import logging

module = 'ASG Scale Up Cleaner Lambda'
#Set Default Region & Account ID- Overridden by Lambda context
REGION = 'us-east-2'
ACCOUNT_ID = '12234567890'
LOCAL=True

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.info('%s started.', module)

def scaleUp():
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
        asgName = asg['AutoScalingGroupName']
        parameterKey = parameterRoot + asgName + '/DesiredCapacity'
        desiredCapacity = 1
        try:
            parameter = ssm.get_parameter(Name=parameterKey)
            desiredCapacity = int(parameter['Parameter']['Value'])
        except Exception as e:
            logger.warning('Auto-Scaling Group %s has no defined desired capacity - setting current as the default', asgName)
            ssm.put_parameter(
                Name=parameterKey,
                Description='Original Desired Capacity Prior to Scale Down',
                Value=asg['DesiredCapacity'],
                Type='String',
                Overwrite=True) 
        ##Let's be safe and not touch protected in the future        
        response = autoscaling.set_desired_capacity(
            AutoScalingGroupName=asgName,
            DesiredCapacity=desiredCapacity,
            HonorCooldown=False)
        logger.info('Auto-Scaling Group %s reset to initial desired capacity of %i', asgName, desiredCapacity);
        
        count+=1

    logger.info('%s completed. %i Auto-Scaling Groups were updated.', module, count)
def lambda_handler(event, context):
    global REGION
    REGION=context.invoked_function_arn.split(':')[3]
    
    global ACCOUNT_ID
    ACCOUNT_ID=context.invoked_function_arn.split(":")[4]
    print(ACCOUNT_ID)
    
    global LOCAL
    LOCAL=False

    scaleUp()

scaleUp()