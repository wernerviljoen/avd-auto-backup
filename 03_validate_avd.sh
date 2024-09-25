#!/usr/bin/env bash

# Read the inputs from the file
inputs=$(cat format_expect_input.txt)

# Extract the customer name
customer_name=$(echo "$inputs" | grep 'customer_name' | cut -d'=' -f2)

# Print extracted customer name for debugging
echo "Extracted customer name: '$customer_name'"

# Check if the customer directory exists one level up
if [ ! -d "../$customer_name" ]; then
    echo "Error: Directory '../$customer_name' does not exist"
    exit 1
fi

# Change ownership of the directory to the current user
sudo chown -R "$(whoami)" "../$customer_name"

# Change directory to the customer directory
cd "../$customer_name" || { echo "Failed to change directory to '../$customer_name'"; exit 1; }

# Execute the Ansible playbook command
ansible-playbook playbooks/validate_fabric.yml -i "${customer_name}_inventory/inventory.yml"

# Update the dashboards after ANTA Test
echo "Running avd-dashboard-set.py with automated inputs..."
sudo ./avd-dashboard-set.exp

echo "All tasks completed successfully."