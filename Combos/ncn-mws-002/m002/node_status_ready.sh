#!/bin/bash

# Node name to monitor
NODE_NAME="ncn-m002"

# File to log the timestamp of state changes
LOG_FILE="./node_status_change_R.log"

# Initialize the last state
LAST_STATE="Ready"
echo "Shutdown starts at: $(date)"
echo "Monitoring node $NODE_NAME for state changes (Ready <-> Not Ready)..."

# Infinite loop to check node status
while true; do
    # Get the current state of the node
    CURRENT_STATE=$(kubectl get no "$NODE_NAME" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')

    # Convert status to readable form
    if [[ "$CURRENT_STATE" == "True" ]]; then
        CURRENT_STATE="Ready"
    else
        CURRENT_STATE="Not Ready"
    fi

    # Check if the state has changed
    if [[ "$CURRENT_STATE" != "$LAST_STATE" ]]; then
        # Get the current timestamp
        TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

        # Log the state change with timestamp
        echo "State change detected for $NODE_NAME at $TIMESTAMP: $CURRENT_STATE" | tee -a "$LOG_FILE"

        # Update LAST_STATE to the new state
        LAST_STATE="$CURRENT_STATE"

        # Exit the loop since a state change was detected
        break
    fi

    # Update LAST_STATE for the first iteration
    if [[ -z "$LAST_STATE" ]]; then
        LAST_STATE="$CURRENT_STATE"
    fi

    # Wait for a short period before checking again
    sleep 5
done

echo "Monitoring stopped. State change recorded in $LOG_FILE."
