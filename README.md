# Auto Generate L3LS DC variables for Arista Validated Designs

## Introduction

Arista Validated Designs (AVD) is a powerful tool for automating, documenting, and testing network environments using Arista equipment. AVD leverages industry best practices and provides a framework for network engineers to design, deploy, and validate data center networks efficiently.

While AVD offers comprehensive documentation and examples, creating the necessary variable files can be time-consuming and requires expertise in YAML and Ansible. This project aims to simplify the process by automatically generating variable files based on minimal user input, enabling rapid deployment of proof-of-concept or test environments for 1 to 10+ data centers.

The key advantages of using AVD include:
- Ensuring best practice configurations
- Automatic documentation generation
- Detailed post-deployment testing framework

This tool offers three ways to run the workflow:
- Manually execute the scripts
- Use an Apple Shortcut (included, may require modification for file locations)
- Utilize Siri with voice prompts

## Components

### 00_avd_gen.py

This is the heart of the project. It is simply a Python script that asks the following:
- What is the customer’s name?
- How many data centers have they got?

It then iterates through the last two questions based on the answer of the question "How many data centers have they got?":
- How many SPINES are in CUSTOMER_DC#?
- How many LEAF-PAIRS are in CUSTOMER_DC#?
- What is the Management IP Pool in CIDR format in DC#?

Based on the input it generates all the files required for # of DCs for CUSTOMER one folder up from the script directory. This includes:
```
<CUSTOMER> -- a New directory for the customer name.
├── <CUSTOMER>_inventory -- The directory for all inventory files.
│   ├── <CUSTOMER>_studio_import.yaml -- a CloudVision Studio input that file that be used with the CloudVision "L3 Leaf-Spine Fabric" studio instead of the AVD build playbook.
│   ├── documentation -- AVD will generate the build documentation here. Think of it as a Low-Level Design of the network. 
│   │   ├── <CUSTOMER>_FABRIC -- Documentation for the FABRIC.
│   │   └── devices -- Documentation for each device.
│   ├── group_vars -- Ansible Group Variables for AVD.
│   │   ├── CVAAS
│   │   │   └── cvaas_auth.yml  -- Details of CVaaS. This might require some variables specific to your deployment.
│   │   ├── <CUSTOMER>_DC<NUMBER> .yml -- Generated from user input and JSON inputs inside the script. Details such as underlay protocol.
│   │   ├── <CUSTOMER>_DC<NUMBER> _L2_LEAFS.yml -- Generated from user input and JSON inputs inside the script. Not much input here.
│   │   ├── <CUSTOMER>_DC<NUMBER> _L3_LEAFS.yml -- Generated from user input and JSON inputs inside the script. Not much input here.
│   │   ├── <CUSTOMER>_DC<NUMBER> _SPINES.yml -- Generated from user input and JSON inputs inside the script. Details such as LEAF Pairs, SPINES, Addressing, ASN numbers and interface maps.
│   │   ├── <CUSTOMER>_FABRIC.yml - Generated from user input and JSON inputs inside the script. Details such as Underlay and Overlay protocol.
│   │   └── cv_servers
│   │       └── initial_topology.yml -- Initial container structure and configlet assignment for staging. It would require the Configlet e.g. <CUSTOMER>_INFRA to exist on CVP to be assigned.
│   ├── intended -- All generated config from AVD will go here.
│   ├── inventory.yml -- The Ansible inventory file for all the devices. 
│   └── reports -- All Arista Network Test Automation (ANTA) results are stored here.
│       └── test_results
├── ansible.cfg -- The Ansible config file. Here you can point it to the inventory file as well. 
└── playbooks -- All AVD playbooks.
    ├── all_fabric.yml -- A playbook to build the configs and documentation, deploy it to CVaaS and do the ANTA tests all in one.
    ├── build_fabric.yml -- A playbook to build the configs and documentation.
    ├── deploy_fabric.yml -- A playbook to deploy it to CVaaS.
    └── validate_fabric.yml -- A playbook to run the ANTA tests against the devices.
```
### 00_avd_gen.sh
This is the same script as 00_avd_gen.py but with the variables filled using the Apple Shortcut or SIRI voice inputs.

### 01_build_avd.sh
A shell script to run the build_fabric.yml playbook. For this to work you should first generate the customer directory using either the 00_avd_gen.py script or the DEMO AVD(Apple Shortcut) > Generate function.

### 02_deploy_avd.sh
A shell script to run the deploy_fabric.yml playbook. Additionally, we use PyAVD to upload the FABRIC documentation into a CloudVision Dashboard.  For this to work you should first generate the customer directory using either the 00_avd_gen.py script or the DEMO AVD(Apple Shortcut) > Generate function and then the Build menu option or the 01_build_avd.sh shell script.

### deployment doc dashboard.json
A prerequisite is to upload the dashboard into CloudVision. Go into CloudVision> Dashboards> Import and select the "deployment doc dashboard.json" file. You will see a new dashboard called Deployment Documentation with a TAB for Post Deployment Tests and Fabric Addressing.

### 03_validate_avd.sh
A shell script to run the AVD validation playbook using ANTA. Additionally, we use PyAVD to upload the ANTA Test report into a CloudVision Dashboard. A prerequisite is to upload the dashboard into CloudVision. Go into CloudVision > Dashboards >Import and select the "deployment doc dashboard.json" file. You will see a new dashboard called Deployment Documentation with a TAB for Post Deployment Tests and Fabric Addressing. For this to work you should first deploy the fabric using the Deploy option from the DEMO AVD(Apple Shortcut) > Deploy Function or the 02_deploy_avd.sh shell script. 

### 04_all_avd.sh
A shell script to run the AVD all_fabric.yml playbook that Builds, Deploys and Validates the deployment in one step. For this to work you should first generate the customer directory using either the 00_avd_gen.py script or the DEMO AVD(Apple Shortcut) > Generate function.

### 05_reset_avd.sh
A shell script to delete the generated files and reset the devices to a prior state. It will also remove the generated directory and reset the "Deployment Documentation" dashboard.

### reset_fabric.yml
A playbook to restore the devices to a pre-deployment state. This gets copied to the <CUSTOMER> Playbooks directory with the 05_reset_avd.sh shell script. You can also manually copy it.

### CONNECTED_ENDPOINTS.yml
A YML file for AVD to specify how hosts connect to the fabric. 

### TENANTS_NETWORKS.yml
A YML file for AVD to specify EVPN tenants to be deployed for the fabric. An alternative is to import "Inputs_EVPN Services.yaml" into the "EVPN Services" studio or manually running the studio.

### DEMO AVD QUIET.shortcut
Import this into the Apple Shortcuts to use as a manual shortcut or use SIRI and voice prompts. This shortcut does not include additional voiceovers. Best for quick AVD deployments or demos where you do all the talking.

### DEMO AVD.shortcut
Import this into the Apple Shortcuts to use as a manual shortcut or use SIRI and voice prompts. This shortcut includes additional voiceovers. Best for AVD demos with SIRI speaking

### format_expect.py
This revises the generated output from user inputs using SIRI or Apple shortcuts and formats it into a file that can be used for the expected input. It will also look for inputs accidentally captured as words instead of numbers in IP Addressing e.g. 192.168.one.0/24.

### avd-cvaas_token 
An authentication token to be used by avd-dashboard-set.py. This token needs to be generated and replaced with YOUR custom token. To generate the token go to CloudVision-as-a-Service>Settings>Service Accounts. Create a service account called ansible, as network admin and copy the generated token. Paste the token into this file and save.

### avd-dashboard-set.py
This is used with the avd-cvaas_token to upload the deployment documentation and ANTA report into the "Deployment Documentation" dashboard.                      
## Instructions using Apple Shortcut
# Pre-requisites
- CloudVision-as-service.
- Visual Studio Code and Python 3.
- AVD installed - (https://avd.sh/en/stable/).
- "avd-auto-backup" folder is cloned to a directory where you are going to run your AVDs.
- An Apple MAC with the shortcuts app if using Shortcuts.
- Update the Apple Script inputs to point to the correct directory e.g. keystroke "cd ~/Documents/scripts/arista-ansible/avd-auto-backup" & return -- Change directory.

## Assumptions

## Steps
- Say "Hey Siri, Demo AVD" or "Hey Siri, Demo AVD QUIET"
- Say Generate when prompted to select one.
- Say Build when prompted to select one.
- Say Deploy when prompted to select one.
- Say Build when prompted to select one.
- Say Validate when prompted to select one.
- Say Exit Validate when prompted to select one.

## TODO
-  Link to the Demo recording.
-  Maybe a "make" file.
-  Fix some actions in Apple Script e.g. play music or tell Alexa to play music.
-  Apple Shortcut shell script does not work due to permissions therefore AppleScript is used to run a shell script. It would be nice to just run the shell script from inside the shortcut.
-  Adjust timings for the "Wait" Action.
-  Document 00_avd_gen.sh in more detail.
