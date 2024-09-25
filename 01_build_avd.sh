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

# Copy TENANT and HOST variables OR alternatively use CloudVision Studios
cp CONNECTED_ENDPOINTS.yml "../${customer_name}/${customer_name}_inventory/group_vars/CONNECTED_ENDPOINTS.yml"
cp TENANTS_NETWORKS.yml "../${customer_name}/${customer_name}_inventory/group_vars/TENANTS_NETWORKS.yml"

# Change directory to the customer directory
cd "../$customer_name" || { echo "Failed to change directory to '../$customer_name'"; exit 1; }

# Execute the Ansible playbook command
ansible-playbook playbooks/build_fabric.yml -i "${customer_name}_inventory/inventory.yml"

echo "All tasks completed successfully."
