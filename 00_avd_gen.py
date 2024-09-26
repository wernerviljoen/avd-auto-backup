import yaml
import ipaddress
import os
from collections import OrderedDict

# Change the working directory to one level up
os.chdir("..")

# The rest of your script
print("Running from directory:", os.getcwd())

# Function to get a valid numerical input
def get_numeric_input(prompt):
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Please enter a valid numerical value.")

# Function to get a valid IP address and subnet
def get_ip_pool():
    while True:
        try:
            ip_pool = ipaddress.IPv4Network(input(f"What is the Management IP Pool in CIDR format for DC{dc_number}? "), strict=False)
            return ip_pool
        except ValueError:
            print("Please enter a valid IP address and subnet.")

# Function to create customer directory structure
def create_customer_directory(cust_name):
    try:
        # Create the main directory with the customer name
        cust_directory = os.path.join(os.getcwd(), cust_name)
        os.makedirs(cust_directory, exist_ok=True)

        # Create the cust_name_inventory directory
        inventory_directory = os.path.join(cust_directory, f"{cust_name}_inventory")
        os.makedirs(inventory_directory, exist_ok=True)

        # Create the playbooks directory
        playbooks_directory = os.path.join(cust_directory, "playbooks")
        os.makedirs(playbooks_directory, exist_ok=True)

        # Create sub-directories under cust_name_inventory
        subdirectories = ['group_vars', 'documentation', 'reports', 'intended']
        for subdir in subdirectories:
            subdir_path = os.path.join(inventory_directory, subdir)
            os.makedirs(subdir_path, exist_ok=True)

        # Ensure group_vars directory exists before creating subdirectories
        group_vars_directory = os.path.join(inventory_directory, 'group_vars')
        if not os.path.exists(group_vars_directory):
            raise Exception(f"Directory {group_vars_directory} does not exist.")

        # Create additional directories under group_vars
        group_vars_subdirs = ['cv_servers', 'CVAAS']
        for subdir in group_vars_subdirs:
            subdir_path = os.path.join(group_vars_directory, subdir)
            os.makedirs(subdir_path, exist_ok=True)
            print(f"Created directory: {subdir_path}")

        print(f"Directories created successfully for customer: {cust_name}")
    except Exception as e:
        print(f"Error creating directories: {e}")

# Prompt for customer name
cust_name = input("What is the customer’s name? ")

if __name__ == "__main__":
    # Call the function to create directories
    create_customer_directory(cust_name)

    # Prompt for the number of DCs
    dc_number = get_numeric_input("How many data center’s have they got? ")

    # Initialize the inventory data structure
    inventory_data = {
        'all': {
            'children': {}
        }
    }

    # Initialize studio_data to aggregate data for all DCs
    studio_data_aggregate = {
        'path': [],
        'inputs': {
            'dataCenters': []
        }
    }

ansible_cfg_data = f"""
[defaults]
interpreter_python = /Library/Frameworks/Python.framework/Versions/3.11/bin/python3
inventory = ./{cust_name}_inventory/inventory.yml
roles_path = ~/.ansible/collections/ansible_collections/arista/cvp/roles
collections_path = ~/.ansible/collections/ansible_collections
jinja2_extensions = jinja2.ext.loopcontrols,jinja2.ext.do
duplicate_dict_key = error
[persistent_connection]
connect_timeout = 120
command_timeout = 120
"""
# Write the data to ansible.cfg
with open(f'{cust_name}/ansible.cfg', 'w') as cfg_file:
    cfg_file.write(ansible_cfg_data)

build_playbook_data = f"""
- name: GENERATE CONFIG AND DOCUMENTATION
  hosts: {cust_name}_FABRIC
  connection: local
  gather_facts: false
  collections:
    - arista.avd
  vars:
    fabric_dir_name: "{{{{fabric_name}}}}"
    execute_tasks: false
  tasks:

    - name: GENERATE INTENDED VARIABLES
      import_role:
        name: eos_designs

    - name: GENERATE INTENDED CONFIG AND DOCUMENTATION
      import_role:
        name: eos_cli_config_gen
"""
with open(f'{cust_name}/playbooks/build_fabric.yml', 'w') as yaml_file:
    yaml_file.write(build_playbook_data)

deploy_playbook_data = f"""
- name: DEPLOY CONFIGURATION TO DEVICES VIA CLOUDVISION
  #hosts: cv_servers
  hosts: cvaas
  connection: local
  gather_facts: false
  collections:
    - arista.avd
  tasks:
    - name: PROVISION CVP WITH AVD CONFIGURATION
      import_role:
        name: eos_config_deploy_cvp
      vars:
        container_root: '{cust_name}_FABRIC'
        configlets_prefix: 'AVD'
        state: present
        execute_tasks: true
        
"""
with open(f'{cust_name}/playbooks/deploy_fabric.yml', 'w') as yaml_file:
    yaml_file.write(deploy_playbook_data)

validate_playbook_data = f"""
- name: VALIDATE STATES ON EOS DEVICES USING ANTA
  hosts: {cust_name}_FABRIC
  gather_facts: false
  tasks:
    - name: VALIDATE STATES ON EOS DEVICES
      ansible.builtin.import_role:
        name: arista.avd.eos_validate_state
      vars:
        # To enable ANTA
        # use_anta: false
        # To save catalogs
        save_catalog: true
"""
with open(f'{cust_name}/playbooks/validate_fabric.yml', 'w') as yaml_file:
    yaml_file.write(validate_playbook_data)

all_fabric_playbook = f"""
---
{build_playbook_data.strip('---')}
{deploy_playbook_data.strip('---')}
{validate_playbook_data.strip('---')}
"""

with open(f'{cust_name}/playbooks/all_fabric.yml', 'w') as yaml_file:
    yaml_file.write(all_fabric_playbook)


CVAAS_data = """
ansible_host: www.cv-staging.corp.arista.io
ansible_user: cvaas
# Good until Jan 1, 2026 10:48:08 <update to expiration date of token that was generated in CVaaS>
# It is advised to use Ansible Vault for storing the `ansible_password`.
ansible_password: eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJkaWQiOjQ2ODc5OTAsImRzbiI6ImFuc2libGUiLCJkc3QiOiJhY2NvdW50IiwiZXhwIjoxNzY3MjU3Mjg4LCJpYXQiOjE3MDU0ODEyOTIsIm9naSI6NDQzOTk5Nywib2duIjoid3YtbGFiIiwic2lkIjoiYzFmZGZhMjdlMjE1ZmQ4MTg5MWIxY2FmZjM3MjA1NjEzNDZiNDk3NmM5MjgwNmQ2YjE1NDg2ZjBlYTcwNzg3Yy1KeEp3QkI3ei00ZjdtbW1lNER4alczWU5hSExXQmZwZ2NhRWFqUmhuIn0.3zu_bZ88nWTcodmV7-VCWJo8F7BJuqbgYyGibXE2aZ_pnB6ogeWMTmgHAeC1WaT7DHBEdKWe8sEbtwUQ5ugzQQ
ansible_connection: httpapi
ansible_network_os: eos
ansible_httpapi_use_ssl: True
ansible_httpapi_validate_certs: True
ansible_httpapi_port: 443
"""
with open(f'{cust_name}/{cust_name}_inventory/group_vars/CVAAS/cvaas_auth.yml', 'w') as yaml_file:
    yaml_file.write(CVAAS_data)

dc_content ={}

# Initialize the YAML structure
initial_topo_data = {
'CVP_DEVICES_INIT': [],  # Initialize as a list to store device dictionaries
    'CVP_CONTAINERS_INIT': {
        'Tenant': {
            'configlets': [f'{cust_name}-INFRA']
        },
        'STAGING': {
            'parentContainerName': 'Tenant',
            'configlets': [f'{cust_name}-INFRA-STAGING']
        }
    },
    'CVP_CONTAINERS_DELETE': {
        'Leaf': {
            'parentContainerName': 'Tenant'
        },
        'Spine': {
            'parentContainerName': 'Tenant'
        }
    }
}

# Process each DC
for dc_count in range(1, dc_number + 1):
    dc_name = f'{cust_name}_DC{dc_count}'
    #dc_fabric = f'{dc_name}
    # Populate initial_topo_data for each DC
#    initial_topo_data['CVP_CONTAINERS_INIT']['Tenant']['configlets'].append(f'{cust_name}-INFRA')
#    initial_topo_data['CVP_CONTAINERS_INIT']['STAGING']['configlets'].append(f'{cust_name}-INFRA-STAGING')    

    # Prompt for SPINES and LEAF Pairs
    spines_count = get_numeric_input(f"How many SPINES are in {dc_name}? ")
    leaf_pairs_count = get_numeric_input(f"How many LEAF-PAIRS are in {dc_name}? ")

    # Prompt for Management IP Pool
    management_ip_pool = get_ip_pool()

#####################################

######################################  
    # Build the inventory structure for the current DC
    inv_data = {
        'children': {
            f'{cust_name}_FABRIC': {
                'children': {
                    f'{dc_name}': {
                        'children': {
                            f'{dc_name}_SPINES': {
                                'vars': {'type': 'spine'},
                                'hosts': {}
                            },
                            f'{dc_name}_LEAFS': {
                                'vars': {'type': 'l3leaf'},
                                'hosts': {}
                                ##'children': {}
                            }
                        }
                    }
                }
            },
            'TENANTS_NETWORKS': {
                'children': {
                    f'{dc_name}_LEAFS': {}
                }
            },
            'CONECTED_ENDPOINTS': {
                'children': {
                    f'{dc_name}_LEAFS': {}
                }
            },    
            'CVAAS': {
                'hosts': {
                    'cvaas': {}
                }   
            }
        }
    }
    inventory_data['all']['children'].setdefault(f'{cust_name}_FABRIC', {'children': {}})
    inventory_data['all']['children'][f'{cust_name}_FABRIC']['children'][f'{dc_name}'] = inv_data['children'][f'{cust_name}_FABRIC']['children'][f'{dc_name}']
    inventory_data['all']['children']['TENANTS_NETWORKS'] = inv_data['children']['TENANTS_NETWORKS']
    inventory_data['all']['children']['CONECTED_ENDPOINTS'] = inv_data['children']['CONECTED_ENDPOINTS']
    inventory_data['all']['children']['CVAAS'] = inv_data['children']['CVAAS']    
######################################

    # Define loopback_ipv4_pool dynamically based on dc_count
    leaf_loopback_ipv4_pool = ipaddress.IPv4Network(f'172.{15 + dc_count}.0.0/25')
    spine_loopback_ipv4_pool = ipaddress.IPv4Network(f'172.{15 + dc_count}.0.128/25')
    vtep_loopback_ipv4_pool = ipaddress.IPv4Network(f'172.{15 + dc_count}.1.0/24')
    uplink_ipv4_pool = ipaddress.IPv4Network(f'172.{15 + dc_count}.200.0/24') 
    mlag_peer_l3_vlan: 4094    #Added to use same VLAN for iBGP
    mlag_peer_ipv4_pool = ipaddress.IPv4Network(f'169.254.0.0/31')
    mgmt_gateway = str(management_ip_pool.broadcast_address - 1)

######################################
    dc_data = {
    'mgmt_gateway': str(mgmt_gateway),
    'spine': {
        'defaults': {
            'platform': 'default',
            #'downlink_interfaces': ['Ethernet1/1', 'Ethernet2/1', 'Ethernet3/1', 'Ethernet4/1', 'Ethernet5/1', 'Ethernet6/1'],
            'loopback_ipv4_pool': str(spine_loopback_ipv4_pool),
            'bgp_defaults': [
                'distance bgp 20 200 200',
                'graceful-restart restart-time 300',
                'graceful-restart'
            ]
        },
        'nodes': [{}]
    },
    'l3leaf': {
        'defaults': {
            'platform': 'default',
            'loopback_ipv4_pool': str(leaf_loopback_ipv4_pool),
            'loopback_ipv4_offset': 2,
            'vtep_loopback_ipv4_pool': str(vtep_loopback_ipv4_pool),
            'uplink_ipv4_pool': str(uplink_ipv4_pool),
            'mlag_peer_ipv4_pool': str(mlag_peer_ipv4_pool),
            'mlag_peer_l3_ipv4_pool': str(leaf_loopback_ipv4_pool),
            'mlag_peer_l3_vlan': '4094', #Added to use same VLAN for iBGP
            #'mlag_interfaces': ['Ethernet55/1', 'Ethernet56/1'],
            #'uplink_interfaces': ['Ethernet49/1', 'Ethernet50/1', 'Ethernet51/1', 'Ethernet52/1'],
            'virtual_router_mac_address': '00:1c:73:00:00:99',
            'mlag_port_channel_id': '2000',
            'spanning_tree_priority': 4096,
            'spanning_tree_mode': 'mstp',
            'bgp_defaults': [
                'distance bgp 20 200 200',
                'graceful-restart restart-time 300',
                'graceful-restart'
            ]
        },
        'node_groups': []
    #},
    #'l2leaf': {
    #    'defaults': {
    #        'platform': 'vEOS-lab',
    #        'spanning_tree_mode': 'mstp'
    #    },
    #    'node_groups': [
    #        {
    #            'group': 'DC1_L2_LEAF1',
    #            'uplink_switches': ['dc1-leaf1a', 'dc1-leaf1b'],
    #            'nodes': [
    #                {
    #                    'name': 'dc1-leaf1c',
    #                    'id': 1,
    #                    'mgmt_ip': '172.16.1.151/24',
    #                    'uplink_switch_interfaces': ['Ethernet8', 'Ethernet8']
    #                }
    #            ]
    #        },
    #        {
    #            'group': 'DC1_L2_LEAF2',
    #            'uplink_switches': ['dc1-leaf2a', 'dc1-leaf2b'],
    #            'nodes': [
    #                {
    #                    'name': 'dc1-leaf2c',
    #                    'id': 2,
    #                    'mgmt_ip': '172.16.1.152/24',
    #                    'uplink_switch_interfaces': ['Ethernet8', 'Ethernet8']
    #                }
    #            ]
    #        }
    #    ]
    }
    }
######################################    

    l2_leafs_data = {'type': 'l2leaf'}
    l3_leafs_data = {'type': 'l3leaf'}
    spines_data = {'type': 'spine'}

    # Initialize spine nodes as a list
    dc_data['spine']['nodes'] = []
    spine_bgp_asn = int('65' + str(dc_count) + '00')
    # Initialize a list to store spine names for the current DC
    spine_names = []

    # Populate SPINES hosts with ansible_host values from the Management IP Pool
    for spine_count in range(1, spines_count + 1):
        ansible_host = str(management_ip_pool.network_address + spine_count)
        #node_name = f'{dc_name}_SPINE-{spine_count}'
        node_name = f'{cust_name}-DC{dc_count}-SPINE-{spine_count}'
        #PHY#
        #downlink_interfaces = [f'Ethernet{leaf_count}/1' for leaf_count in range(1, leaf_pairs_count * 2 + 1)]
        #VEOS#
        #downlink_interfaces = [f'Ethernet{leaf_count}' for leaf_count in range(1, leaf_pairs_count * 2 + 1)]
        # Add the spine name to the list
        spine_names.append(node_name)
        inv_data['children'][f'{cust_name}_FABRIC']['children'][f'{dc_name}']['children'][f'{dc_name}_SPINES']['hosts'][f'{cust_name}-DC{dc_count}-SPINE-{spine_count}'] = {'ansible_host': ansible_host}
        # Create an OrderedDict for the device entry
        # Create a standard dict for the device entry with fields in the desired order
        device_entry = {
            'fqdn': node_name,
            'parentContainerName': 'STAGING',
            'configlets': [f'BaseIPv4_{node_name}']
        }      
        # Append the dict to the CVP_DEVICES_INIT list
        initial_topo_data['CVP_DEVICES_INIT'].append(device_entry)

        # Add the node to dc_data['spine']['nodes']
        dc_data['spine']['nodes'].append({
            'name': node_name,
            'id': spine_count,
            'mgmt_ip': f"{ansible_host}/{management_ip_pool.prefixlen}"#,
            #'downlink_interfaces': downlink_interfaces
    })
    # Add the node group to dc_data['spine']['nodes']
    dc_data['spine']['defaults']['bgp_as'] = spine_bgp_asn
    # Assign the spine_names list to uplink_switches in dc_data['l3leaf']['defaults']
    dc_data['l3leaf']['defaults']['uplink_switches'] = spine_names
    
    #####
    # Populate LEAFS hosts with ansible_host values from the Management IP Pool
    #for group_count in range(1, (leaf_pairs_count // 2) + 1):
    for group_count in range(1, leaf_pairs_count + 1):
        # Define group name
        group_name = f'{dc_name}_L3_LEAF{group_count}'
        leaf_bgp_asn = int('65' + str(dc_count) + str(group_count).zfill(2))

        # Initialize nodes for the group
        group_nodes = []

        # Define pod key for each group
        pod_key = f'pod{group_count}'

        # Ensure pod_key exists in inv_data structure
        ###inv_data['children'][f'{cust_name}_FABRIC']['children'][f'{dc_name}']['children'][f'{dc_name}_LEAFS'] = {'hosts': {}}
        ##if pod_key not in inv_data['children'][f'{cust_name}_FABRIC']['children'][f'{dc_name}']['children'][f'{dc_name}_LEAFS']['children']:
        ##    inv_data['children'][f'{cust_name}_FABRIC']['children'][f'{dc_name}']['children'][f'{dc_name}_LEAFS']['children'][pod_key] = {'hosts': {}}

        for leaf_count in range(1, 3):
            # Determine the pod letter based on leaf_count
            pod_letter = chr(64 + leaf_count)
            ansible_host = str(management_ip_pool.network_address + spines_count + (group_count - 1) * 2 + leaf_count)
            #node_name = f'{dc_name}_LEAF-{group_count}{pod_letter}'
            node_name = f'{cust_name}-DC{dc_count}-LEAF-{group_count}{pod_letter}'
            # Repeat 'Ethernet1' interface as many times as there are spines
            # for vEOS Correct
            uplink_switch_interfaces = [f'Ethernet{(group_count - 1) * 2 + leaf_count}'] * spines_count
            uplink_interfaces = [f'Ethernet{0 + spine}' for spine in range(1, spines_count + 1)]
            # for Physical
            #uplink_switch_interfaces = [f'Ethernet{48 + spine}/1' for spine in range(1, spines_count + 1)]


            # Add the leaf node to the inventory
            ##inv_data['children'][f'{cust_name}_FABRIC']['children'][f'{dc_name}']['children'][f'{dc_name}_LEAFS']['children'][pod_key]['hosts'][node_name] = {'ansible_host': ansible_host}
            inv_data['children'][f'{cust_name}_FABRIC']['children'][f'{dc_name}']['children'][f'{dc_name}_LEAFS']['hosts'][node_name] = {'ansible_host': ansible_host}
            device_entry = {
                'fqdn': node_name,
                'parentContainerName': 'STAGING',
                'configlets': [f'BaseIPv4_{node_name}']
            }
            
            # Append the dict to the CVP_DEVICES_INIT list
            initial_topo_data['CVP_DEVICES_INIT'].append(device_entry)

            # Add the leaf node to the current group
            group_nodes.append({
                'name': node_name,
                'id': (group_count - 1) * 2 + leaf_count,
                'mgmt_ip': f"{ansible_host}/{management_ip_pool.prefixlen}",
                'uplink_switch_interfaces': uplink_switch_interfaces
            })

        # Insert the node group at the beginning of the list
        dc_data['l3leaf']['node_groups'].insert(0, {
            'group': group_name,
            'bgp_as': leaf_bgp_asn,
            'nodes': group_nodes
        })
        dc_data['l3leaf']['defaults']['uplink_interfaces'] = uplink_interfaces
#    # Populate CVP_DEVICES_INIT for each node in the current DC
#    for node in dc_data['spine']['nodes'] + dc_data['l3leaf']['node_groups']:
#        initial_topo_data['CVP_DEVICES_INIT'].append({
#            'fqdn': {node_name},
#            'parentContainerName': 'STAGING',
#            'configlets': [f'BaseIPv4_{node_name}']
#        })

################
        # Define studio_data for the current DC
        studio_data = {
            'path': [],
            'inputs': {
                'dataCenters': [
                    {
                        'inputs': {
                            'dataCenter': {
                                'fabricSettings': {},
                                'platformSettingsResolver': [],
                                'pods': [
                                    {
                                        'inputs': {
                                            'pod': {
                                                'LeafDomains': [
                                                    {
                                                        'inputs': {
                                                            'l3LeafDomain': {
                                                                'l3LeafMlag': True
                                                            }
                                                        },
                                                        'tags': {
                                                            'query': 'Leaf-Domain:1'
                                                        }
                                                    },
                                                    {
                                                        'inputs': {
                                                            'l3LeafDomain': {
                                                                'l3LeafMlag': True
                                                            }
                                                        },
                                                        'tags': {
                                                            'query': 'Leaf-Domain:2'
                                                        }
                                                    },
                                                    {
                                                        'inputs': {
                                                            'l3LeafDomain': {
                                                                'l3LeafMlag': True
                                                            }
                                                        },
                                                        'tags': {
                                                            'query': 'Leaf-Domain:3'
                                                        }
                                                    }                                                                                                        
                                                ],
                                                'commonBGPConfig': {
                                                    'evpnEnabled': True,
                                                    'evpnMulticast': False,
                                                    'evpnRtMembership': False,
                                                    'leafAsnRange': f'65{dc_count}01-65{dc_count * 100 + 32}',
                                                    'leafLoopback0Subnet': str(leaf_loopback_ipv4_pool),
                                                    'leafLoopback0SubnetV6': f'2024:{15 + dc_count}:16::/64',
                                                    'spineAsn': f'65{dc_count}00',
                                                    'spineBGPDynamicNeighbors': False,
                                                    'spineLoopback0Subnet': str(spine_loopback_ipv4_pool),
                                                    'spineLoopback0SubnetV6': f'2024:{15 + dc_count}:16::/64',
                                                },
                                                'commonMlagConfig': {
                                                    'lacpMode': 'active',
                                                    'mlagPeerLinkSubnet': '169.254.0.0/31',
                                                    'mlagPortChannelId': 2000,
                                                    'mlagSubnetMask': 31,
                                                    'mlagVlan': 4094,
                                                    'virtualRouterMacAddress': '00:1c:73:00:00:99'
                                                },
                                                'l2LeafDomains': [],
                                                'maximums': {},
                                                'ospfConfiguration': {},
                                                'overlayDetails': {
                                                    'leafLoopback1Subnet': str(vtep_loopback_ipv4_pool),
                                                    'leafLoopback1SubnetV6': f'2024:{15 + dc_count}:16:1::/64',
                                                    'vVtepAddress': f'172.{15 + dc_count}.1.254/32',
                                                    'vxlanOverlay': True
                                                },
                                                'spanningTreeMode': None,
                                                'underlayRouting': {}
                                            }
                                        },
                                        'tags': {
                                            'query': f'DC-Pod:{dc_name}_POD1'
                                        }
                                    }
                                ],
                                'superSpinePlanes': []
                            }
                        },
                        'tags': {
                            'query': f'DC:{dc_name}'
                        }
                    }
                ]
            }
        }
###########################

        # Append the current DC's studio_data to the aggregate data
        studio_data_aggregate['inputs']['dataCenters'].append(studio_data['inputs']['dataCenters'][0])

    # Write the consolidated inventory YAML file
    with open(f'{cust_name}/{cust_name}_inventory/inventory.yml', 'w', encoding='utf-8') as yaml_file:
        yaml.dump(inventory_data, yaml_file, default_flow_style=False, allow_unicode=True)
        print(f"Consolidated inventory written to inventory.yml")

    # Write the aggregated studio_data to a single YAML file
    with open(f'{cust_name}/{cust_name}_inventory/{cust_name}_studio_import.yaml', 'w', encoding='utf-8') as yaml_file:
        yaml.dump(studio_data_aggregate, yaml_file, default_flow_style=False, allow_unicode=True)
        print(f"Aggregated studio_data written to dc_name_studio_import.yaml")
    
##########################
     # Write the data to dcX.yml
    with open(f'{cust_name}/{cust_name}_inventory/group_vars/{dc_name}.yml', 'w', encoding='utf-8') as yaml_file:
        yaml.dump(dc_data, yaml_file, default_flow_style=False, allow_unicode=True)

         # Write the data to SPINES.yml
    with open(f'{cust_name}/{cust_name}_inventory/group_vars/{dc_name}_SPINES.yml', 'w', encoding='utf-8') as yaml_file:
        yaml.dump(spines_data, yaml_file, default_flow_style=False, allow_unicode=True)

     # Write the data to L2_LEAFS.yml
    with open(f'{cust_name}/{cust_name}_inventory/group_vars/{dc_name}_L2_LEAFS.yml', 'w', encoding='utf-8') as yaml_file:
        yaml.dump(l2_leafs_data, yaml_file, default_flow_style=False, allow_unicode=True)

     # Write the data to L3_LEAFS.yml
    with open(f'{cust_name}/{cust_name}_inventory/group_vars/{dc_name}_L3_LEAFS.yml', 'w', encoding='utf-8') as yaml_file:
        yaml.dump(l3_leafs_data, yaml_file, default_flow_style=False, allow_unicode=True)                                      
    
# Write the data to inventory.yml
with open(f'{cust_name}/{cust_name}_inventory/inventory.yml', 'w', encoding='utf-8') as yaml_file:
    yaml_file.write(yaml.dump(inventory_data, default_flow_style=False, allow_unicode=True))

# Write the consolidated initial_topo YAML file
with open(f'{cust_name}/{cust_name}_inventory/group_vars/cv_servers/initial_topology.yml', 'w', encoding='utf-8') as yaml_file:
    yaml.dump(initial_topo_data, yaml_file, default_flow_style=False, allow_unicode=True)
    print(f"Consolidated initial_topology written to initial_topology.yml")    

######################################
fabric_data = {
    "ansible_connection": "ansible.netcommon.httpapi",
    "ansible_network_os": "arista.eos.eos",
    "ansible_user": "cvpadmin",
    "ansible_password": "@rista123!",
    "ansible_become": True,
    "ansible_become_method": "enable",
    "ansible_httpapi_use_ssl": True,
    "ansible_httpapi_validate_certs": False,
    "fabric_name": f"{cust_name}_FABRIC",
    "fabric_ip_addressing": {
        "mlag": {
            "algorithm": "same_subnet"
        }
    },
    "underlay_routing_protocol": "ebgp",
    "overlay_routing_protocol": "ebgp",
    "local_users": [
        {
            "name": "ansible",
            "privilege": 15,
            "role": "network-admin",
            "sha512_password": "$6$7u4j1rkb3VELgcZE$EJt2Qff8kd/TapRoci0XaIZsL4tFzgq1YZBLD9c6f/knXzvcYY0NcMKndZeCv0T268knGKhOEwZAxqKjlMm920"
        },
        {
            "name": "admin",
            "privilege": 15,
            "role": "network-admin",
            "no_password": True
        }
    ],
    "bgp_update_wait_install": False,  # For vEOS to install EVPN Loopback
    "bgp_peer_groups": {
        "evpn_overlay_peers": {"password": "Q4fqtbqcZ7oQuKfuWtNGRQ=="},
        "ipv4_underlay_peers": {"password": "7x4B4rnJhZB438m9+BrBfQ=="},
        "mlag_ipv4_underlay_peer": {"password": "4b21pAdCvWeAqpcKDFMdWw=="}
    },
    "p2p_uplinks_mtu": 9214,
    "default_interfaces": [
        #{
        #    "types": ["spine"],
        #    "platforms": ["default"],
        #    "downlink_interfaces": ["Ethernet1/1", "Ethernet2/1", "Ethernet3/1", "Ethernet4/1"]
        #},
        {
            "types": ["l3leaf"],
            "platforms": ["default"],
        #    "uplink_interfaces": ["Ethernet49/1", "Ethetrnet50/1", "Ethernet51/1", "Ethetrnet52/1"],
            #PHY#
            #"mlag_interfaces": ["Ethernet55/1", "Ethernet56/1"]#,
            #VEOS#
            "mlag_interfaces": ["Ethernet5"]#,
#           "downlink_interfaces": ["Ethernet1", "Ethernet1"]
        }#,
#        {
#            "types": ["l2leaf"],
#            "platforms": ["default"],
#            "uplink_interfaces": ["Ethernet1", "Ethernet2"]
#        }
    ]#,
#    "l3_edge": {
#        "p2p_links_ip_pools": [
#            {
#                "name": "DCI_IP_pool",
#                "ipv4_pool": "10.10.100.0/24"
#            }
#        ],
#        "p2p_links_profiles": [
#            {
#                "name": "DCI_profile",
#                "ip_pool": "DCI_IP_pool",
#                "as": [65116, 65216],
#                "include_in_underlay_protocol": True
#            }
#        ],
#        "p2p_links": [
#            {
#                "id": 1,
#                "nodes": ["PAI-BORDER-1A", "DR-BORDER-1A"],
#                "interfaces": ["Ethernet48", "Ethernet48"],
#                "profile": "DCI_profile"
#            },
#            {
#                "id": 2,
#                "nodes": ["PAI-BORDER-1B", "DR-BORDER-1B"],
#                "interfaces": ["Ethernet48", "Ethernet48"],
#                "profile": "DCI_profile"
#            }
#        ]
#    }
}

####################################

# Write the data to CUSTOMER_FABRIC.yml
with open(f'{cust_name}/{cust_name}_inventory/group_vars/{cust_name}_FABRIC.yml', 'w') as yaml_file:
    yaml.dump(fabric_data, yaml_file, default_flow_style=False)

 # Write the data to TENANT_NETWORKS.yml
#with open(f'{cust_name}/{cust_name}_inventory/group_vars/{cust_name}_TENANTS_NETWORKS.yml', 'w') as yaml_file:
#    yaml.dump('# to be done', yaml_file, default_flow_style=False)

# Write the data to CONECTED_ENDPOINTS.yml
#with open(f'{cust_name}/{cust_name}_inventory/group_vars/{cust_name}_CONECTED_ENDPOINTS.yml', 'w') as yaml_file:
#    yaml.dump('# to be done', yaml_file, default_flow_style=False)   


print("New customer files have succesfully been generated.")