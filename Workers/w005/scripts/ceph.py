import json
import subprocess
import re

positions = '{"x3000":["ncn-m001","ncn-w001","ncn-w004","ncn-w007","ncn-s001"],"x3001":["ncn-m002","ncn-w002","ncn-w006","ncn-s003","ncn-s004"],"x3002":["ncn-m003","ncn-w003","ncn-w009","ncn-s005","ncn-s002"]}'
positions_dict = json.loads(positions)


for racknum, (rack, nodes) in enumerate(positions_dict.items()):
    racknum = "rack" + str(racknum+1)
    print("Rack number is ", racknum)
    
    command1 = "ceph osd crush add-bucket "+racknum+" rack"
    print(command1)
    result = subprocess.run(command1, capture_output=True, text=True)
    print('Result for add-bucket command', result.returncode)
    print('Output for add-bucket command', result.stdout)
    
    command2 = "ceph osd crush move "+racknum+" root=default"
    print(command2)
    result = subprocess.run(command2, capture_output=True, text=True)
    print('Result for crush move command', result.returncode)
    print('Output for crush move command', result.stdout)
    
    print(nodes)
    for node in nodes:
        print(node)
        if re.match(r"^.*ncn-s00[0-9]$", node):
            print("Node is storage node")
            command3="ceph osd crush move "+node+" rack="+racknum
            print(command3)
            #result = subprocess.run(command3, capture_output=True, text=True)
            #print('Result for crush move command', result.returncode)
            #print('Output for crush move command', result.stdout)

command4="ceph osd crush rule create-replicated replicated_rule_with_rack_failure_domain default rack"
result = subprocess.run(command4, capture_output=True, text=True)
print('Result for rule creation command', result.returncode)
print('Output for rule creation command', result.stdout)

command5="ceph osd pool ls"
result = subprocess.run(command5, capture_output=True, text=True)
print('Result for rule creation command', result.returncode)
ceph_pools=result.stdout
print('Output for rule creation command', ceph_pools)
for pool in ceph_pools:
    print(pool)
    command6="ceph osd pool set "+pool+" crush_rule replicated_rule_with_rack_failure_domain"
    print(command6)
    #result = subprocess.run(command6, capture_output=True, text=True)
    #print('Result for pool setting with rule command', result.returncode)
    #print('Output for pool setting with rule command', result.stdout)
