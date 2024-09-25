# Resource explorer set 
# python3 avd-dashboard-set.py --server www.cv-staging.corp.arista.io --token-file avd-cvaas_token
# pip3 install --upgrade cloudvision
# pip3 install requests
# pip3 install grpcio 


#!/usr/bin/python

import argparse
import grpc
import json
import arista.dashboard.v1
from google.protobuf.json_format import Parse

import os

# Change the working directory to one level up
os.chdir("..")

# The rest of your script
print("Running from directory:", os.getcwd())


RPC_TIMEOUT = 30  # in seconds

# Prompt for customer name and DC number
cust_name = input("What is the customer name? ")



def main(args):
    # Read the FABRIC Markdown file
    fabric_markdown = None  # Initialize fabric_markdown to None

    # Read the Fabric Markdown file
    try:
        with open(f'{cust_name}/{cust_name}_inventory/documentation/{cust_name}_FABRIC/{cust_name}_FABRIC-documentation.md', 'r') as fmd:
            fabric_markdown = fmd.read()
    except FileNotFoundError:
        print("Fabric Markdown file not found.")
        fabric_markdown = "Fabric documentation not generated yet. Run AVD playbook"
    except Exception as e:
        print(f"Error reading Markdown file: {e}")
        return

    # Read the ANTA Markdown file
    anta_markdown = None  # Initialize fabric_markdown to None

    # Read the ANTA Markdown file
    try:
        with open(f'{cust_name}/{cust_name}_inventory/reports/{cust_name}_FABRIC-state.md', 'r') as fmd:
            anta_markdown = fmd.read()
    except FileNotFoundError:
        print("ANTA Markdown file not found.")
        anta_markdown = "ANTA Tests not ran yet. Run AVD playbook"
    except Exception as e:
        print(f"Error reading Markdown file: {e}")
        return


    # Read the token file
    try:
        with open(args.token_file.name, 'r') as tf:
            token = tf.read().strip()
    except Exception as e:
        print(f"Error reading token file: {e}")
        return

    # Create the channel using the self-signed cert if provided
    try:
        if args.cert_file:
            cert = args.cert_file.read()
            channelCreds = grpc.ssl_channel_credentials(root_certificates=cert)
        else:
            channelCreds = grpc.ssl_channel_credentials()
    except Exception as e:
        print(f"Error reading certificate file: {e}")
        return

    # Create the header object for the token
    callCreds = grpc.access_token_call_credentials(token)
    connCreds = grpc.composite_channel_credentials(channelCreds, callCreds)

    # Define the JSON data structure with the embedded Markdown content
    json_data_works = {
        "value": {
            "name": "Deployment Documentation",
            "description": "Documentation on Fabric deployment",
            "key": {
                "dashboardId": "db0d8ce5-cd4d-4bf4-b27a-2cbcddef37d7"
            },
            "widgets": {
                "values": [
                    {
                        "id": "9fc65a6b-0eea-41c3-af7f-ad52ad31c4a6",
                        "name": "",
                        "type": "topology-widget",
                        "location": "main",
                        "parent": "",
                        "position": {
                            "x": 0,
                            "y": 0
                        },
                        "dimensions": {
                            "width": 24,
                            "height": 19
                        }
                    },
                    {
                        "id": "f7128321-914b-4b72-b1c5-e484108cdb5f",
                        "name": "",
                        "type": "security-exposure-widget",
                        "location": "main",
                        "inputs": json.dumps({
                            "complianceView": "ALL_COMPLIANCE_COUNTS",
                            "selectedCustomTags": [],
                            "tags": ""
                        }),  # Serialize the inputs field to a JSON string    
                        "parent": "",
                        "position": {
                            "x": 0,
                            "y": 19
                        },
                        "dimensions": {
                            "width": 24,
                            "height": 78
                        }
                    },                                          
                    {
                        "id": "45d8b8b6-71d1-4a05-a529-087e4d5eec1a",
                        "name": "Documentation",
                        "type": "tabs-widget",
                        "location": "main",
                        "parent": "",
                        "position": {
                            "x": 0,
                            "y": 0
                        },
                        "dimensions": {
                            "width": 24,
                            "height": 19
                        }
                    },
                    {
                        "id": "8aa3e295-429b-4a2a-b29b-e01f4619437b",
                        "name": "Post Deployment Tests",
                        "type": "text-widget",
                        "inputs": json.dumps({
                            "textContent": anta_markdown,
                            "verticalAlignment": 0
                        }),  # Serialize the inputs field to a JSON string
                        "location": "main",
                        "parent": "45d8b8b6-71d1-4a05-a529-087e4d5eec1a",                        
                        "position": {
                            "x": 0,
                            "y": 0
                        },
                        "dimensions": {
                            "width": 24,
                            "height": 19
                        }
                    },                                                       
                    {
                        "id": "6951471d-1417-4840-8112-ec36652052b7",
                        "name": "Fabric Addressing",
                        "type": "text-widget",
                        "inputs": json.dumps({
                            "textContent": fabric_markdown,
                            "verticalAlignment": 0
                        }),  # Serialize the inputs field to a JSON string
                        "location": "main",
                        "parent": "45d8b8b6-71d1-4a05-a529-087e4d5eec1a",                        
                        "position": {
                            "x": 0,
                            "y": 0
                        },
                        "dimensions": {
                            "width": 24,
                            "height": 19
                        }
                    }                                         
                ]
            }
        }
    }


    json_data_testing = {
        "value": {
            "name": "Deployment Documentation",
            "description": "Documentation on Fabric deployment",
            "key": {
                "dashboardId": "db0d8ce5-cd4d-4bf4-b27a-2cbcddef37d7"
            },
            "widgets": {
                "values": [
                    {
                        "id": "9fc65a6b-0eea-41c3-af7f-ad52ad31c4a6",
                        "name": "",
                        "type": "topology-widget",
                        "location": "main",
                        "parent": "",
                        "position": {
                            "x": 0,
                            "y": 0
                        },
                        "dimensions": {
                            "width": 24,
                            "height": 19
                        }
                    },
                    {
                        "id": "f7128321-914b-4b72-b1c5-e484108cdb5f",
                        "name": "",
                        "type": "security-exposure-widget",
                        "location": "main",
                        "inputs": json.dumps({
                            "complianceView": "ALL_COMPLIANCE_COUNTS",
                            "selectedCustomTags": [],
                            "tags": ""
                        }),  # Serialize the inputs field to a JSON string    
                        "parent": "",
                        "position": {
                            "x": 0,
                            "y": 19
                        },
                        "dimensions": {
                            "width": 24,
                            "height": 78
                        }
                    },                                          
                    {
                        "id": "45d8b8b6-71d1-4a05-a529-087e4d5eec1a",
                        "name": "Documentation",
                        "type": "tabs-widget",
                        "location": "main",
                        "parent": "",
                        "position": {
                            "x": 0,
                            "y": 0
                        },
                        "dimensions": {
                            "width": 24,
                            "height": 19
                        }
                    },
                    {
                        "id": "8aa3e295-429b-4a2a-b29b-e01f4619437b",
                        "name": "Post Deployment Tests",
                        "type": "text-widget",
                        "inputs": json.dumps({
                            "textContent": anta_markdown,
                            "verticalAlignment": 0
                        }),  # Serialize the inputs field to a JSON string
                        "location": "main",
                        "parent": "45d8b8b6-71d1-4a05-a529-087e4d5eec1a",                        
                        "position": {
                            "x": 0,
                            "y": 0
                        },
                        "dimensions": {
                            "width": 24,
                            "height": 19
                        }
                    },                                                       
                    {
                        "id": "6951471d-1417-4840-8112-ec36652052b7",
                        "name": "Fabric Addressing",
                        "type": "text-widget",
                        "inputs": json.dumps({
                            "textContent": fabric_markdown,
                            "verticalAlignment": 0
                        }),  # Serialize the inputs field to a JSON string
                        "location": "main",
                        "parent": "45d8b8b6-71d1-4a05-a529-087e4d5eec1a",                        
                        "position": {
                            "x": 0,
                            "y": 0
                        },
                        "dimensions": {
                            "width": 24,
                            "height": 19
                        }
                    }                                         
                ]
            }
        }
    }


    json_request = json.dumps(json_data_testing)
    req = Parse(json_request, arista.dashboard.v1.services.DashboardConfigSetRequest(), ignore_unknown_fields=False)

    # Initialize a connection to the server using our connection settings (auth + TLS)
    try:
        with grpc.secure_channel(args.server, connCreds) as channel:
            tag_stub = arista.dashboard.v1.services.DashboardConfigServiceStub(channel)
            response = tag_stub.Set(req, timeout=RPC_TIMEOUT)
            print(f"Response: {response}")
    except grpc.RpcError as e:
        print(f"gRPC error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--server',
        required=True,
        help="CloudVision server to connect to in <host>:<port> format")
    parser.add_argument("--token-file", required=True,
                        type=argparse.FileType('r'), help="File with access token")
    parser.add_argument("--cert-file", type=argparse.FileType('rb'),
                        help="Certificate to use as root CA (optional, for secure connections)")
    args = parser.parse_args()
    main(args)