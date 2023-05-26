import boto3
import json

priceList = []
#retrieve price list
def getPriceList():
    global priceList
    pricing = boto3.client('pricing')
    response = pricing.get_products( ServiceCode='AmazonSecurityLake')
    priceList = response['PriceList']
    while "NextToken" in response:
        response = pricing.get_products(ServiceCode='AmazonSecurityLake', NextToken=response["NextToken"])
        priceList.extend(response['PriceList'])

#gets the price per unit (GB) for the usage_type, except for other log types, as those are tier priced
def getPrice(usage_type):
    if ("other" in usage_type.lower()):
        raise Exception ("Other log types are calculated using different function as they are tier priced.")
    usage_type = usage_type.lower()
    if("free" in usage_type):
        usage_type = usage_type.replace("free","paid")
    price_per_unit = 0
    for pr in priceList:
        p=json.loads(pr)
        if usage_type == p["product"]["attributes"]["usagetype"].lower() and "OnDemand" in p["terms"]:
            #this is required to access the deeply nested price wiht some unknown keys
            price_per_unit = float(list(list(p['terms']['OnDemand'].values())[0]["priceDimensions"].values())[0]["pricePerUnit"]["USD"])
    return price_per_unit        

#helper sorting function
def getBeginRange(priceDimension):
    return float(priceDimension['beginRange'])

#gets the total cost for the other log types, as those are tier priced
def getPriceOther(usage_type, usage_projection):
    if ("other" not in usage_type.lower()):
        raise Exception ("This function should be used for calculatin the Other log types, as they are tier priced.")
    usage_type = usage_type.lower()
    if("free" in usage_type):
        usage_type = usage_type.replace("free","paid")
    for pr in priceList:
        p=json.loads(pr)
        if usage_type == p["product"]["attributes"]["usagetype"].lower() and "OnDemand" in p["terms"]:
            priceDimensions = list(list(p['terms']['OnDemand'].values())[0]["priceDimensions"].values())

    #The bands list reads as first 10240 at 0.25c, next 20480 at 0.15 ... so on as tiered pricing for Other logs
    #The Order is important for the calculation, so we are sorting the bands.
    #bands = [(10240, 0.25), (20480, 0.15), (20480, 0.075), (inf, 0.005)]
    bands = []
    priceDimensions.sort(key=getBeginRange)
    for d in priceDimensions:
        bands.append(((float(d['endRange']) - float(d['beginRange'])), float(d['pricePerUnit']['USD'])))

    remaining_gb = usage_projection
    current_band_idx = 0
    total_cost = 0

    while remaining_gb > 0:
        band_max_gb, band_cost = bands[current_band_idx]

        if band_max_gb is None:
            band_billable_gb = remaining_gb
        else:
            band_billable_gb = min(remaining_gb, band_max_gb)

        total_cost += band_billable_gb * band_cost
        current_band_idx += 1
        remaining_gb -= band_billable_gb
        
    return total_cost