#!/bin/bash

# Directory to save the output files
OUTPUT_DIR="./kubectl_logs"

# Create the directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Infinite loop to run the command every minute
while true; do
    # Get the current timestamp
    TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

    # Filename with the timestamp
    FILENAME="${OUTPUT_DIR}/kubectl_podlayout_w002_${TIMESTAMP}.log"

    # Run the command and add a timestamp to the output, then save it to the file
    {
        echo "Timestamp: $(date +"%Y-%m-%d %H:%M:%S")"
        kubectl get all -A -o wide | grep w002
    } > "$FILENAME"

    echo "Output saved to $FILENAME"

    # Wait for 60 seconds before the next iteration
    sleep 300
done

