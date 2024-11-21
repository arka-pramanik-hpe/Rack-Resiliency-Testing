#!/bin/bash

# Define the output file where pod details will be saved
output_file="pod_details.txt"

# Function to get pod details
get_pod_details() {
  kubectl get pods --all-namespaces --field-selector=status.phase=Running -o=json | \
  jq -r '.items[] | select((.metadata.creationTimestamp | fromdateiso8601) > (now - 1200)) | 
         "\(.metadata.namespace) \(.metadata.name) \(.status.hostIP) \(.metadata.creationTimestamp)"'
}

# Function to create a header
create_header() {
  echo -e "Namespace\t\tPod Name\t\t\t\t\tNode Name\t\t\tCreation Timestamp"
  echo -e "-------------------------------------------------------------------------------------------------------------------"
}

# Monitor pods indefinitely and save details to the file, replacing previous content
while true; do
  # Get the list of pods whose age is less than 20 minutes
  pod_details=$(get_pod_details)

  # If there are any new pods, overwrite the output file with the latest pod details
  if [[ -n "$pod_details" ]]; then
    # Write header and pod details in a formatted way
    {
      create_header
      echo "$pod_details" | while IFS= read -r line; do
        # Split the line into separate variables for better formatting
        namespace=$(echo "$line" | awk '{print $1}')
        pod_name=$(echo "$line" | awk '{print $2}')
        node_name=$(echo "$line" | awk '{print $3}')
        creation_timestamp=$(echo "$line" | awk '{print $4}')

        # Format each pod's details for better readability and ensure proper column alignment
        printf "%-20s %-50s %-30s %-25s\n" "$namespace" "$pod_name" "$node_name" "$creation_timestamp"
      done
    } > "$output_file"

    echo "Pod details updated in $output_file"
  fi

  # Sleep for 30 seconds before checking again
  sleep 30
done
