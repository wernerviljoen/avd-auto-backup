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

# Read the inputs from the file
inputs=$(cat format_expect_input.txt)

# Extract the customer name and number of DCs
customer_name=$(echo "$inputs" | grep 'customer_name' | cut -d'=' -f2)
number_of_dcs=$(echo "$inputs" | grep 'number_of_dcs' | cut -d'=' -f2)

# Initialize the expect script content
expect_script=$(cat << EOF
#!/usr/bin/expect -f

set timeout -1

spawn python3 00_avd_gen.py

expect "What is the customer’s name?" {
    send "$customer_name\r"
}

expect "How many data center’s have they got?" { 
    send "$number_of_dcs\r" 
}
EOF
)

# Loop through the number of DCs and add expect statements
for (( dc=1; dc<=$number_of_dcs; dc++ )); do
    spines=$(echo "$inputs" | grep "spines_dc${dc}" | cut -d'=' -f2)
    leafs=$(echo "$inputs" | grep "leafs_dc${dc}" | cut -d'=' -f2)
    ip_pool=$(echo "$inputs" | grep "ip_pool_dc${dc}" | cut -d'=' -f2)

    expect_script+="
    expect \"How many SPINES are in ${customer_name}_DC${dc}? \" { send \"$spines\r\" }
    expect \"How many LEAF-PAIRS are in ${customer_name}_DC${dc}? \" { send \"$leafs\r\" }
    expect \"What is the Management IP Pool in CIDR format for DC${dc} \" { send \"$ip_pool\r\" }
    "
done

expect_script+="
puts \"Script execution completed\"
expect eof
"

# Write the expect script to a file
echo "$expect_script" > 00_avd_gen.exp

#_____________
# Make the expect script executable
chmod +x 00_avd_gen.exp

echo "Expect script generated successfully."

# Run the Expect script
echo "Running 00_avd_gen.py with automated inputs..."
sudo ./00_avd_gen.exp

# Create and write the second Expect script for the dashboard
cat << EOF > avd-dashboard-set.exp
#!/usr/bin/expect -f

set timeout -1
cd ..
cd avd-auto-backup

# Start the Python script
spawn python3 avd-dashboard-set.py --server www.cv-staging.corp.arista.io --token-file avd-cvaas_token

expect "What is the customer’s name?" {
    send "$customer_name\r"
}

expect eof
EOF

# Make the second Expect script executable
chmod +x avd-dashboard-set.exp

echo "All tasks completed successfully."