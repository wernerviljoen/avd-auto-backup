#!/usr/bin/env bash

# Get the directory of the current shell script
script_dir=$(pwd)

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
cp reset_fabric.yml "../${customer_name}/playbooks/reset_fabric.yml"

# Change directory to the customer directory
cd "../$customer_name" || { echo "Failed to change directory to '../$customer_name'"; exit 1; }

# Execute the Ansible playbook command
ansible-playbook playbooks/reset_fabric.yml -i "${customer_name}_inventory/inventory.yml"

# Remove the directory one level back
cd ..

rm -rf "$customer_name"

# Optional: Print a confirmation message
echo "Directory $customer_name has been removed."

cd "$script_dir"

# Reset the dashboards
echo "Running avd-dashboard-set.py with automated inputs..."
#sudo ./avd-dashboard-set.exp
./avd-dashboard-set.exp

# Remove all .exp and .txt files in the current directory
rm *.exp
rm *.txt

clear