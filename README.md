# Slack Event Alarms [![test](https://github.com/dundunndone/slack-event-alarms/actions/workflows/manual.yml/badge.svg?event=push)](https://github.com/dundunndone/slack-event-alarms/actions/workflows/manual.yml)
Provides Slack notifications on errors from AWS accounts using CloudWatch Event Rules.

## Purpose
This tool is designed to alert teams on event errors from CloudTrail by sending a notification to a Slack channel. Information helps alert teams to misconfigurations and access issues within an account.

## How It Works
Checks custom S3 bucket for events from account. CloudWatch event rule runs every 15 minutes where the Lambda function checks 3 or more events within the last 15 minutes that contain error codes. Function can be customized to support different thresholds or S3 bucket structures.

This tool is designed to work with **[AWS Event Monitor](https://github.com/sdunn15/aws-event-monitor)**. However, Slack Event Alarms can be customized to support existing S3 buckets such as your Primary CloudTrail bucket. 

Within Slack, access the `Incoming Webhooks` app to create new webhooks and determine existing Slack webhooks for your target (Public and Private) channels.

Information below references parameters in the `slack_alarms.yml` template and how to configure them.

* CustomS3BucketName
 - Existing s3 bucket is setup to read events using this structure `"s3://custom-s3-bucket/eventlogs/accountid/region/yyyy-mm-dd/eventid.json"`. For each event ID a separate .json file is created.

* SlackChannels
 -  This entry should be formatted as a directory using this format `{"account-alias":"https://hooks.slack.com/services/"}`. The account alias name in this parameter should be present within the **AccountAliases** parameter below. Optionally, you can send alarms to multiple Slack channels for 1 AWS account. 

* AccountAliases:
 - This entry should be formatted as a directory using this format `{"account-alias":"account-id"}`.  If your events only target 1 AWS account, you should include account alias name and the AWS account ID. If you have a centralized S3 bucket logging CloudTrail events from multiple accounts, you should add all applicable accounts aliases/ID here.

## Deployment

Deploy templates and resources in order.

* `slack_alarms.yml`
  - **Contains**: IAM, Lambda, CloudWatch Event rule
  - **Deploy**: us-east-1 only 
* `slack_alarms.py`
  - **Contains**: Zip file and upload to target "LambdaBucketName"
  - **Deploy**: us-east-1 only 

## Supports

* Supports single and centralized account(s) logging events from CloudTrail to S3. 
* Customizable template to send events /w errors from an AWS account to a public or private Slack channel.
* This function uses python `requests` library to send events to Slack. [Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-path) are used to package the library and upload the `requests.zip` file into Lambda.
