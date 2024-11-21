#!/bin/bash

# Define the output file where pod details will be saved
output_file="non_running_pod_details.txt"

# Function to get pod details
get_non_running_pod_details() {
  kubectl get pods --all-namespaces -o=json | \
  jq -r '.items[] | select(.status.phase != "Running") | 
         "\(.metadata.namespace) \(.metadata.name) \(.status.hostIP) \(.status.phase) \(.status.startTime)"'
}

# Function to create a header
create_header() {
  echo -e "Namespace\t\tPod Name\t\t\tNode Name\t\t\tState\t\t\tState Timestamp"
  echo -e "---------------------------------------------------------------------------------------------------------------"
}

# Monitor pods indefinitely and save details to the file, replacing previous content
while true; do
  # Get the list of non-running pods
  pod_details=$(get_non_running_pod_details)

  # If there are any non-running pods, overwrite the output file with the latest pod details
  if [[ -n "$pod_details" ]]; then
    # Write header and pod details in a formatted way
    {
      create_header
      echo "$pod_details" | while IFS= read -r line; do
        # Split the line into separate variables for better formatting
        namespace=$(echo "$line" | awk '{print $1}')
        pod_name=$(echo "$line" | awk '{print $2}')
        node_name=$(echo "$line" | awk '{print $3}')
        state=$(echo "$line" | awk '{print $4}')
        state_timestamp=$(echo "$line" | awk '{print $5}')

        # Format each pod's details for better readability and ensure proper column alignment
        printf "%-20s %-30s %-30s %-15s %-25s\n" "$namespace" "$pod_name" "$node_name" "$state" "$state_timestamp"
      done
    } > "$output_file"

    echo "Non-running pod details updated in $output_file"
  fi

  # Sleep for 30 seconds before checking again
  sleep 30
done
 
