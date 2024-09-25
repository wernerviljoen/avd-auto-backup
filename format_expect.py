import json
import os
import re

# Get the directory of the current shell script
script_dir = os.path.dirname(os.path.realpath(__file__))


# Define the output file path within the same directory as the script
input_file_path = os.path.join(script_dir, 'format_expect_output.txt')

# Dictionary to map words to numbers
words_to_numbers = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9"
}

# Function to convert word numbers to numeric in IP addresses
def convert_ip(ip):
    print(f"Original IP: {ip}")  # Debugging line
    # Replace word numbers with digits using word boundaries
    for word, num in words_to_numbers.items():
        ip = re.sub(r'\b{}\b'.format(word), num, ip)
    print(f"Converted IP: {ip}")  # Debugging line
    return ip

# Function to validate IP address
def is_valid_ip(ip):
    try:
        # Split the IP address from the subnet mask
        ip_addr, subnet_mask = ip.split('/')
        
        # Ensure the subnet mask is an integer between 0 and 32
        subnet_mask = int(subnet_mask)
        if not 0 <= subnet_mask <= 32:
            return False
        
        # Validate the IP address format
        ip_parts = ip_addr.split('.')
        if len(ip_parts) != 4:
            return False
        
        # Ensure each part of the IP address is a number between 0 and 255
        for part in ip_parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                return False
        
        return True
    except (ValueError, IndexError):
        return False

# Read the input data from the file
with open(input_file_path, 'r') as file:
    input_data = file.read()

# Split the input data into lines
lines = input_data.strip().split('\n')

# Initialize a dictionary to store the formatted data
formatted_data = {}

# Process each line with debugging info
for line in lines:
    print(f"Processing line: {line}")  # Debugging line
    try:
        # Attempt to parse the line as JSON
        data = json.loads(line)
        print(f"Parsed JSON data: {data}")  # Debugging line
        # Process each item in the JSON data
        for key, value in data.items():
            if key.startswith("ip_pool_dc"):
                value = convert_ip(value)
                if not is_valid_ip(value):
                    raise ValueError(f"Invalid IP address: {value}")
            formatted_data[key] = value
    except json.JSONDecodeError:
        # If not JSON, treat it as a key-value pair
        key, value = line.split('=')
        print(f"Key: {key}, Value before processing: {value}")  # Debugging line
        # Ensure customer_name is in uppercase
        if key == "customer_name":
            value = value.upper()
        # Convert IP address entries to numbers and validate
        if key.startswith("ip_pool_dc"):
            value = convert_ip(value)
            if not is_valid_ip(value):
                raise ValueError(f"Invalid IP address: {value}")
        formatted_data[key] = value
        print(f"Key: {key}, Value after processing: {value}")  # Debugging line

# Function to extract sorting key
def sort_key(x):
    parts = x.split('_dc')
    prefix = parts[0]
    suffix = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return (prefix, suffix)

# Sort keys to ensure proper order in the output
sorted_keys = sorted(formatted_data.keys(), key=sort_key)

# Generate the output in the desired format
output_lines = []
for key in sorted_keys:
    output_lines.append(f"{key}={formatted_data[key]}")

# Join the output lines
output = '\n'.join(output_lines)

# Define the output file path
output_file_path = os.path.join(script_dir, 'format_expect_input.txt')

# Ensure the directory exists
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

# Write the output to the file
with open(output_file_path, 'w') as file:
    file.write(output)

print(f"Output written to {output_file_path}")