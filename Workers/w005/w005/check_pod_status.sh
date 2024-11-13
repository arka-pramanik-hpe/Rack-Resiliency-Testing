#!/bin/bash

# Set the node name you want to monitor
NODE_NAME="ncn-w005"

# Set the file to store logs for state changes
LOG_FILE="./pod_state_changes.log"

# Initialize an associative array to keep track of previous states
declare -A pod_states

# Ensure the log file exists
touch "$LOG_FILE"

while true; do
  # Get all DaemonSet, ReplicaSet, and StatefulSet pods on the specified node
  pods=$(kubectl get pods -o json --all-namespaces --field-selector spec.nodeName="$NODE_NAME" | \
         jq -r '.items[] | select((.metadata.ownerReferences[].kind == "DaemonSet") or (.metadata.ownerReferences[].kind == "ReplicaSet") or (.metadata.ownerReferences[].kind == "StatefulSet")) | .metadata.namespace + " " + .metadata.name + " " + .status.phase')

  # Loop through each pod and check for state changes
  while read -r namespace pod_name current_state; do
    pod_id="${namespace}/${pod_name}"

    # If the pod state has changed, log it and update the stored state
    if [[ "${pod_states[$pod_id]}" != "$current_state" ]]; then
      timestamp=$(date "+%Y-%m-%d %H:%M:%S")
      echo "State change detected for pod $pod_name in namespace $namespace on $NODE_NAME: ${pod_states[$pod_id]:-UNKNOWN} -> $current_state at $timestamp"

      # Append the change to the log file
      echo "$timestamp - Pod: $pod_name, Namespace: $namespace, Previous State: ${pod_states[$pod_id]:-UNKNOWN}, Current State: $current_state, Node: $NODE_NAME" >> "$LOG_FILE"

      # Update the state in the array
      pod_states[$pod_id]="$current_state"
    fi
  done <<< "$pods"

  # Pause for a few seconds before checking again
  sleep 60
done

