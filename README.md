# Security Lake bill estimate tool

This tool can be used to estimate the Amazon Security Lake cost for your organization, based on the free trial usage. 
It takes a number of past days of usage and extrapolates the monthly bill based on Security Lake pricing. 

The tool outputs the cost per account and usage type (which include source and region). The output can displayed on screen or exported as a CSV formatted report. This gives you the ability to easily understand the top contributors across accounts, regions and log types, and fine tune your usage.

**_NOTE:_**  This tool estimates the Amazon Security Lake charges only. It does not include the charges for AWS services used and resources set up as part of your security data lake. See pricing for [Amazon S3](https://aws.amazon.com/s3/pricing/), [AWS Glue](https://aws.amazon.com/glue/pricing/), [Amazon EventBridge](https://aws.amazon.com/eventbridge/pricing/), [AWS Lambda](https://aws.amazon.com/lambda/pricing/), [Amazon SQS](https://aws.amazon.com/sqs/pricing/), and [Amazon SNS](https://aws.amazon.com/sns/pricing/). Standard data transfer costs apply for data accessed or aggregated into S3 across Regions.


## Requirements

* The tool requires access to the Organization payer account, as it relies on Cost Explorer billing data.
* Cost Explorer should be enabled and active for at least 24 hours.
* The days argument should be equal or less than the number of days that Security Lake was in enabled and in use in your account, in order to get an accurate estimation.
* The tool requires ```python3``` to be installed and you can install the dependencies ```boto3``` and ```prettytable``` installed via ```pip3 install -r requirements.txt``` 
* The following permissions are required in order to retrieve the Cost Explorer usage and  get the Security Lake pricing:
  ```
  ce:GetCostAndUsage
  pricing:GetProducts
  ```
  A sample policy granting these permissions:
  ```
  {
    "Version": "2012-10-17",
    "Statement": [
        {
          "Sid": "SLBillEstimateTool",
          "Effect": "Allow",
          "Action": [
              "ce:GetCostAndUsage",
              "pricing:GetProducts"
          ],
          "Resource": "*"
        }
    ]
  }
  ```


## Usage

1. Copy the 3 files from the repo into the CloudShell console of your AWS payer account:  ```requirements.txt, slbill.py, slpricing.py``` Alternatively, you can run locally if AWS CLI is configured with credentials that grant access to your AWS payer account. 
2. Install the requirements via: ``` pip3 install -r requirements.txt ```
3. Run the tool with: ```python3 slbill.py [-h] [--days DAYS] [--csv] ```


Syntax:
```
usage: python3 slbill.py [-h] [--days DAYS] [--csv]

Retrieve and display Amazon Security Lake usage

optional arguments:
  -h, --help   show this help message and exit
  --days DAYS  Number of past days of usage for estimation (must be 1 to 365)
  --csv        Export results in a CSV format report
```

Example output:
```
+--------------+---------------------------------+------------+-----------------------+-----------------------+
|   Account    | Usage Type                      | Usage (GB) | Usage Projection (GB) | Cost Projection (USD) |
+--------------+---------------------------------+------------+-----------------------+-----------------------+
| 1234567890AB | APN1-FreeCloudTrailEvents-Bytes |    0.07    |          0.07         |          0.05         |
| 1234567890XY | APN1-FreeNormalization-Bytes    |    0.07    |          0.07         |          0.00         |
| 1234567890AB | APS2-FreeCloudTrailEvents-Bytes |    0.08    |          0.08         |          0.06         |
| 1234567890YZ | APS2-FreeNormalization-Bytes    |    0.08    |          0.08         |          0.00         |
| 1234567890CD | EU-FreeCloudTrailEvents-Bytes   |    0.08    |          0.08         |          0.06         |
| 1234567890CD | EU-FreeNormalization-Bytes      |    0.08    |          0.08         |          0.00         |
| 1234567890AB | EUC1-FreeCloudTrailEvents-Bytes |    0.08    |          0.08         |          0.06         |
| 1234567890AB | EUC1-FreeNormalization-Bytes    |    0.08    |          0.08         |          0.00         |
| 1234567890XY | USE1-FreeCloudTrailEvents-Bytes |    0.49    |          0.49         |          0.37         |
| 1234567890XY | USE1-FreeNormalization-Bytes    |    1.73    |          1.73         |          0.06         |
| 1234567890CD | USE1-FreeOtherLogs-Bytes        |    1.24    |          1.24         |          0.31         |
| 1234567890CD | USE2-FreeCloudTrailEvents-Bytes |    0.07    |          0.07         |          0.05         |
| 1234567890AB | USE2-FreeNormalization-Bytes    |    0.07    |          0.07         |          0.00         |
| 1234567890CD | USW2-FreeCloudTrailEvents-Bytes |    0.09    |          0.09         |          0.07         |
| 1234567890XY | USW2-FreeNormalization-Bytes    |    0.09    |          0.09         |          0.00         |
+--------------+---------------------------------+------------+-----------------------+-----------------------+
Usage timeframe: 2023-04-25 to 2023-05-25
Total monthly estimated Security Lake cost (projected based on usage patterns in the last 30 days) is: 1.09 USD
```

## Official Resources

[Amazon Security Lake Overview](https://aws.amazon.com/security-lake/)

[Amazon Security Lake Pricing](https://aws.amazon.com/security-lake/pricing/)

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.