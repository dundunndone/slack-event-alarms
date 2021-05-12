import boto3
import json
import datetime
import os
import requests 
from botocore.exceptions import ClientError

#Counts the number of errors per event name
def countErrors(errors):
    unique = []
    for error in errors:
        if error not in unique:
            unique.append(error)
    errorCount = {}
    for value in unique: 
        num = errors.count(value)
        if num >= 3: #number of errors threshold
            errorCount[value] = num 
            return errorCount
            
def lambda_handler(event, context):
    aliases = json.loads(os.environ['accountAliases'])
    time = datetime.datetime.today() - datetime.timedelta(minutes=15)
    bucket_name = os.environ['EVENTS_LOGS_BUCKET']
    region = boto3.Session().region_name
    s3 = boto3.client('s3')
    prefix = 'eventlogs/' #Current bucket structure "eventlogs/accountid/region/yyyy-mm-dd/" For each event ID a separate .json file is created
    accountObjects = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')
    for accounts in accountObjects['CommonPrefixes']:
        account = accounts['Prefix'].split("/")[1]
        regionObjects = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix + account + '/', Delimiter='/')
        for regions in regionObjects['CommonPrefixes']:
            errors = []
            region = regions['Prefix'].split("/")[2]
            dayObjects = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix + account + '/' + region + '/', Delimiter='/')
            for days in dayObjects['CommonPrefixes']: 
                day = days['Prefix'].split("/")[3]
                if str(datetime.date.today()) == day:
                    errors =[]
                    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix + account + '/' + region + '/' + day + '/')
                    for object in objects['Contents']:
                        try: 
                            file = s3.get_object(Bucket=bucket_name, Key=object['Key'], IfModifiedSince=time)
                        except: 
                            file = ""
                        if file != "":
                            Event = json.loads(file['Body'].read().decode('utf-8'))
                            if "errorCode" in Event['detail'].keys():
                                eventName = Event['detail']['eventName']
                                errors.append("{}".format(eventName))
                    
            allErrors = countErrors(errors)
            if allErrors: 
                awsPartition = os.environ['awsPartition']
                #Lists slack channels to AWS accounts
                slackChannels = json.loads(os.environ['SLACK_CHANNELS'])
                #Checks for accountID in var keys
                if account in aliases.keys():
                    if aliases[account] in slackChannels.keys(): 
                        slackChannel = slackChannels[aliases[account]]
                    else: 
                        slackChannel = ""
                    if slackChannel:
                            errorString = ""
                            for key in allErrors: 
                                errorString += '\n*EventName*: _{}_\n*Error Count*: `{}`\n*Error Msg*: ```{}```'.format(key, allErrors[key], errorMsg) 
                            #print("Errors detected from: " + account + "/" + region)
                            slack_message  = {
                                "attachments": [
                                    {
                                        "color": "#FF0000",                                      
                                        "pretext": f"Recent errors from: (*{aliases[account]}*) ",
                                        "title": f"Region: <https://console.{awsPartition}.amazon.com/cloudtrail/home?region={region}|{region}>",
                                        "text": f"{errorString}"
                                    }
                                ]
                            }
                            req = requests.post(slackChannel, data=json.dumps(slack_message))
                            #print(f'Slack Response: {req}')    
    return