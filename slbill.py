import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import argparse
import csv
from prettytable import PrettyTable
import slpricing
import traceback

def main():
    ce_client = boto3.client('ce') 

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Retrieve and display Amazon Security Lake usage')
    parser.add_argument('--days', type=int, default=30, choices=range(1, 366), metavar='',
                        help='Number of past days of usage for estimation (must be 1 to 365)')
    parser.add_argument('--csv', action='store_true',
                        help='Export results in a CSV format report')
    args = parser.parse_args()
    # Get the start and end dates for the given number of days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=args.days)

    # Define the query for Amazon Security Lake usage
    query = {
        "TimePeriod": {
            "Start": start_date.strftime('%Y-%m-%d'),
            "End": end_date.strftime('%Y-%m-%d')
        },
        "Granularity": "DAILY",
        "Metrics": ["UsageQuantity"],
        "GroupBy": [
            {
                "Type": "DIMENSION",
                "Key": "LINKED_ACCOUNT"
            },
            {
                "Type": "DIMENSION",
                "Key": "USAGE_TYPE"
            }
        ],
        "Filter": {
            "Dimensions": {
                "Key": "SERVICE",
                "Values": ["Amazon Security Lake"]
            }
        }
    }

    # Retrieve the usage data for the query
    response = ce_client.get_cost_and_usage(
        TimePeriod=query['TimePeriod'],
        Granularity=query['Granularity'],
        Metrics=query['Metrics'],
        GroupBy=query['GroupBy'],
        Filter=query['Filter']
    )

    # Sum the usage data across the time period and populate a table
    usage_totals = {}
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            account = group['Keys'][0]
            usage_type = group['Keys'][1]
            usage_quantity = float(group['Metrics']['UsageQuantity']['Amount'])
            if (account, usage_type) in usage_totals:
                usage_totals[(account, usage_type)] += usage_quantity
            else:
                usage_totals[(account, usage_type)] = usage_quantity

    #get public prices
    slpricing.getPriceList()
    # Test and validate the calculations
    # The cost for 75000 GB other logs in USW2 region should be $ 8358 USD
    if slpricing.getPriceOther("USW2-PaidOtherLogs-Bytes", 75000) != 8358:
        raise Exception ("Calculations performed by slpricing appear to be incorrect")
    # Create a table and add the usage totals
    total_projected_cost = 0
    table = PrettyTable()
    table.field_names = ['Account', 'Usage Type', 'Usage (GB)', 'Usage Projection (GB)', 'Cost Projection (USD)']
    table.align['Usage Type'] = 'l' # Set left alignment for the Usage Type column
    for (account, usage_type), usage_quantity in usage_totals.items():
        usage_projection = usage_quantity / args.days * 30
        if ("other" in usage_type.lower()):
            cost_projection = slpricing.getPriceOther(usage_type, usage_projection)
        else:
            cost_projection = usage_projection * slpricing.getPrice(usage_type)
        total_projected_cost += cost_projection
        table.add_row([account, usage_type, f"{usage_quantity:.2f}", f"{usage_projection:.2f}", f"{cost_projection:.2f}"])

    # Print or output the table
    if args.csv:
        outputFile = 'security_lake_usage_' + str(datetime.now().timestamp())+ '.csv'
        with open(outputFile, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(table.field_names)
            for row in table._rows:
                writer.writerow(row)
            writer.writerow("")
            writer.writerow(["Usage timeframe: " + str(start_date) + " to " + str(end_date)])
            writer.writerow(["Total monthly estimated Security Lake cost (projected based on usage patterns in the last " + str(args.days) + " days) is: " + f"{total_projected_cost:.2f}" + " USD"])
            print("Detail report exported in: " + outputFile)
    else:
        print(table)

    print("Usage timeframe: " + str(start_date) + " to " + str(end_date))
    print("Total monthly estimated Security Lake cost (projected based on usage patterns in the last " + str(args.days) + " days) is: " + f"{total_projected_cost:.2f}" + " USD")

if __name__ == "__main__":
    try:
        main()
    except ClientError as e:
        if e.response['Error']['Code'] == 'DataUnavailableException':
            print("Data is not available. If you just enabled Cost Explorer, data might not be ingested yet. Please try again in a few hours.")
        else:
            print("There was an unexpected error: %s" % e)
            traceback.print_exc()
    except Exception as e:
        print("There was an unexpected error: %s" % e)
        traceback.print_exc()