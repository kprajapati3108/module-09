import boto3
import json
import requests
import hashlib
import datetime
import time

grandtotal = 0
totalPoints = 10
assessmentName = "module-09-assessment"
tag = "module-09"

def currentPoints():
    print(f"Current Points: {grandtotal} out of {totalPoints}.")

clientec2 = boto3.client("ec2")
clientelbv2 = boto3.client("elbv2")
clientasg = boto3.client("autoscaling")

print("*" * 79)
print("Begin tests for Module-09 Assessment...")
print("*" * 79)

print("1. Testing that there is 1 tagged VPC...")
vpcs = clientec2.describe_vpcs(
    Filters=[{"Name": "tag:Name", "Values": [tag]}]
)["Vpcs"]
required = 1
actual = len(vpcs)
print(f"Required: {required}, Actual: {actual}")
if actual == required:
    grandtotal += 1
    print("PASS")
else:
    print("FAIL - Check your aws_vpc tags.")
currentPoints()
print("*" * 79)

print("2. Testing that there is 1 tagged Security Group...")
sgs = clientec2.describe_security_groups(
    Filters=[{"Name": "tag:Name", "Values": [tag]}]
)["SecurityGroups"]
required = 1
actual = len(sgs)
print(f"Required: {required}, Actual: {actual}")
if actual == required:
    grandtotal += 1
    print("PASS")
else:
    print("FAIL - Check your aws_security_group tags.")
currentPoints()
print("*" * 79)

print("3. Testing HTTP 200 from the load balancer...")
lbs = clientelbv2.describe_load_balancers()["LoadBalancers"]
required = 1
actual = len(lbs)
print(f"Required ELBs: {required}, Actual ELBs: {actual}")
if actual != required:
    print("FAIL - You need exactly 1 load balancer.")
else:
    dns = lbs[0]["DNSName"]
    print("Waiting 30 seconds before HTTP check...")
    time.sleep(30)
    try:
        response = requests.get(f"http://{dns}", timeout=10)
        print(f"HTTP status received: {response.status_code}")
        if response.status_code == 200:
            grandtotal += 1
            print("PASS")
        else:
            print("FAIL - Web server did not return HTTP 200.")
    except Exception as e:
        print(f"FAIL - Could not connect to ALB URL: {e}")
currentPoints()
print("*" * 79)

print("4. Testing that there are 3 tagged EC2 instances...")
instances_response = clientec2.describe_instances(
    Filters=[
        {"Name": "tag:Name", "Values": [tag]},
        {"Name": "instance-state-name", "Values": ["pending", "running"]}
    ]
)
instance_count = 0
for reservation in instances_response["Reservations"]:
    instance_count += len(reservation["Instances"])
required = 3
actual = instance_count
print(f"Required: {required}, Actual: {actual}")
if actual == required:
    grandtotal += 1
    print("PASS")
else:
    print("FAIL - Check your Auto Scaling Group desired/min/max values.")
currentPoints()
print("*" * 79)

print("5. Testing that there is 1 tagged Internet Gateway...")
igws = clientec2.describe_internet_gateways(
    Filters=[{"Name": "tag:Name", "Values": [tag]}]
)["InternetGateways"]
required = 1
actual = len(igws)
print(f"Required: {required}, Actual: {actual}")
if actual == required:
    grandtotal += 1
    print("PASS")
else:
    print("FAIL - Check aws_internet_gateway tags.")
currentPoints()
print("*" * 79)

print("6. Testing that there are 3 tagged subnets...")
subnets = clientec2.describe_subnets(
    Filters=[{"Name": "tag:Name", "Values": [tag]}]
)["Subnets"]
required = 3
actual = len(subnets)
print(f"Required: {required}, Actual: {actual}")
if actual == required:
    grandtotal += 1
    print("PASS")
else:
    print("FAIL - Check subnet creation and tags.")
currentPoints()
print("*" * 79)

print("7. Testing that each tagged subnet has a route table association...")
route_tables = clientec2.describe_route_tables(
    Filters=[{"Name": "tag:Name", "Values": [tag]}]
)["RouteTables"]

tagged_subnet_ids = {s["SubnetId"] for s in subnets}
associated_subnet_ids = set()

for rt in route_tables:
    for assoc in rt.get("Associations", []):
        subnet_id = assoc.get("SubnetId")
        if subnet_id in tagged_subnet_ids:
            associated_subnet_ids.add(subnet_id)

required = len(tagged_subnet_ids)
actual = len(associated_subnet_ids)
print(f"Required associated tagged subnets: {required}, Actual: {actual}")
if actual == required and required == 3:
    grandtotal += 1
    print("PASS")
else:
    print("FAIL - Make sure all 3 tagged subnets are associated to the route table.")
currentPoints()
print("*" * 79)

print("8. Testing that there is 1 tagged DHCP options set...")
dhcp_options = clientec2.describe_dhcp_options(
    Filters=[{"Name": "tag:Name", "Values": [tag]}]
)["DhcpOptions"]
required = 1
actual = len(dhcp_options)
print(f"Required: {required}, Actual: {actual}")
if actual == required:
    grandtotal += 1
    print("PASS")
else:
    print("FAIL - Add aws_dhcp_options and associate it with the VPC.")
currentPoints()
print("*" * 79)

print("9. Testing that there is 1 tagged Auto Scaling Group...")
asgs = clientasg.describe_auto_scaling_groups()["AutoScalingGroups"]
tagged_asgs = []
for asg in asgs:
    for t in asg.get("Tags", []):
        if t.get("Key") == "Name" and t.get("Value") == tag:
            tagged_asgs.append(asg)
            break

required = 1
actual = len(tagged_asgs)
print(f"Required: {required}, Actual: {actual}")
if actual == required:
    grandtotal += 1
    print("PASS")
else:
    print("FAIL - Check Auto Scaling Group tags.")
currentPoints()
print("*" * 79)

print("10. Testing that 1 tagged route table is attached to the tagged Internet Gateway...")
required = 1
actual = 0

if len(igws) == 1:
    igw_id = igws[0]["InternetGatewayId"]
    for rt in route_tables:
        for route in rt.get("Routes", []):
            if route.get("GatewayId") == igw_id and route.get("DestinationCidrBlock") == "0.0.0.0/0":
                actual += 1

print(f"Required: {required}, Actual: {actual}")
if actual >= 1:
    grandtotal += 1
    print("PASS")
else:
    print("FAIL - Make sure your tagged route table has default route to the tagged IG.")
currentPoints()
print("*" * 79)

print(f"Your result is: {grandtotal} out of {totalPoints} points.")

with open("module-09-results.txt", "w", encoding="utf-8") as f:
    dt = "{:%Y%m%d%H%M%S}".format(datetime.datetime.now())
    resultToHash = assessmentName + str(grandtotal / totalPoints) + dt
    h = hashlib.new("sha256")
    h.update(resultToHash.encode())

    resultsdict = {
        "Name": assessmentName,
        "gtotal": grandtotal / totalPoints,
        "datetime": dt,
        "sha": h.hexdigest()
    }

    json.dump(resultsdict, f)

print("module-09-results.txt generated successfully.")
