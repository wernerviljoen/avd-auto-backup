#!/usr/bin/env bash

# Function to log and execute commands
execute_command() {
    echo "Executing: $1"
    if ! eval "$1"; then
        echo "Error executing: $1"
        exit 1
    fi
    echo "Finished: $1"
}

# Set the customer name
customer_name="WERNER"

# Create customer_name.txt file
touch customer_name.txt
echo "$customer_name" > customer_name.txt

# Create and write the Expect script
cat << EOF > avd-gen.exp
#!/usr/bin/expect -f

set timeout -1

# Start the Python script
spawn python3 avd-gen.py

# Automatically respond with the predefined customer name
expect "What is the customer name? " {
    send "$customer_name\r"
}

# Handle other prompts with predefined values
expect "How many DC’s have they got? " { send "2\r" }
expect "How many SPINES for ${customer_name}_DC1? " { send "4\r" }
expect "How many LEAF pairs for ${customer_name}_DC1? " { send "3\r" }
expect "Enter the Management IP Pool in the format IP_address/Subnet_mask: " { send "192.168.1.0/24\r" }
expect "How many SPINES for ${customer_name}_DC2? " { send "4\r" }
expect "How many LEAF pairs for ${customer_name}_DC2? " { send "3\r" }
expect "Enter the Management IP Pool in the format IP_address/Subnet_mask: " { send "192.168.2.0/24\r" }

puts "Script execution completed"
expect eof
EOF

# Make the Expect script executable
chmod +x avd-gen.exp

echo "Expect script generated successfully."


# Run the Expect script
echo "Running avd-gen.py with automated inputs..."
sudo ./avd-gen.exp

cd ..

# Read the customer name from the temporary file
customer_name=$(cat avd-auto-backup/customer_name.txt)
sudo chown -R $(whoami) "$customer_name"

# Run the Ansible playbook
echo "Running Ansible playbook build_fabric.yml..."
cd "$customer_name" || { echo "Error: Directory '$customer_name' does not exist"; exit 1; }
execute_command "ansible-playbook playbooks/build_fabric.yml -vvv -i ${customer_name}_inventory/inventory.yml"

# Create and write the second Expect script
cat << EOF > avd-dashboard-set.exp
#!/usr/bin/expect -f

set timeout -1
cd ..
cd avd-auto-backup

# Start the Python script
spawn python3 avd-dashboard-set.py --server www.cv-staging.corp.arista.io --token-file avd-cvaas_token

expect "What is the customer name? " {
    send "$customer_name\r"
}

expect eof
EOF

# Make the second Expect script executable
chmod +x avd-dashboard-set.exp

# Run the second Expect script
echo "Running avd-dashboard-set.py with automated inputs..."
sudo ./avd-dashboard-set.exp

echo "All tasks completed successfully."