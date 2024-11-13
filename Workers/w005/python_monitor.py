import json
import os
import time
from datetime import datetime
from subprocess import check_output

# Directory to store logs and JSON files
LOG_DIR = "./pod_state_logs"
LOG_FILE = os.path.join(LOG_DIR, "pod_state_changes.log")
JSON_FILE_TIMESTAMP_FIRST = os.path.join(LOG_DIR, "pod_state_changes_timestamp_first.json")
JSON_FILE_NODE_FIRST = os.path.join(LOG_DIR, "pod_state_changes_node_first.json")
JSON_FILE_NODE_NAMESPACE_TIMESTAMP = os.path.join(LOG_DIR, "pod_state_changes_node_namespace_timestamp.json")

# Dictionary to store current and previous pod states
pod_states = {}

# Initialize empty dictionaries to hold JSON data for all three structures
json_data_timestamp_first = {}
json_data_node_first = {}
json_data_node_namespace_timestamp = {}

# Function to log changes to file
def log_changes(namespace, log_entries):
    if not log_entries:
        return
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"Namespace: {namespace}\n")
        for entry in log_entries:
            log_file.write(entry)

def update_json_timestamp_first(timestamp, node_name, namespace, pod_name, previous_state, current_state, controller_type, controller_name, pod_age):
    """Update the JSON structure with the state change details in timestamp first order."""
    if timestamp not in json_data_timestamp_first:
        json_data_timestamp_first[timestamp] = {}

    if node_name not in json_data_timestamp_first[timestamp]:
        json_data_timestamp_first[timestamp][node_name] = {}

    if namespace not in json_data_timestamp_first[timestamp][node_name]:
        json_data_timestamp_first[timestamp][node_name][namespace] = {}

    # Store pod state change, controller, and pod age in the JSON structure
    json_data_timestamp_first[timestamp][node_name][namespace][pod_name] = {
        "Previous State": previous_state,
        "Current State": current_state,
        "Controller": {
            "Type": controller_type,
            "Name": controller_name
        },
        "Pod Age": pod_age
    }

    # Write JSON data to file
    with open(JSON_FILE_TIMESTAMP_FIRST, "w") as json_file:
        json.dump(json_data_timestamp_first, json_file, indent=4)

def update_json_node_first(timestamp, node_name, namespace, pod_name, previous_state, current_state, controller_type, controller_name, pod_age):
    """Update the JSON structure with the state change details in node first order."""
    if node_name not in json_data_node_first:
        json_data_node_first[node_name] = {}

    if timestamp not in json_data_node_first[node_name]:
        json_data_node_first[node_name][timestamp] = {}

    if namespace not in json_data_node_first[node_name][timestamp]:
        json_data_node_first[node_name][timestamp][namespace] = {}

    # Store pod state change, controller, and pod age in the JSON structure
    json_data_node_first[node_name][timestamp][namespace] = {
        pod_name: {
            "Previous State": previous_state,
            "Current State": current_state,
            "Controller": {
                "Type": controller_type,
                "Name": controller_name
            },
            "Pod Age": pod_age
        }
    }

    # Write JSON data to file
    with open(JSON_FILE_NODE_FIRST, "w") as json_file:
        json.dump(json_data_node_first, json_file, indent=4)

def update_json_node_namespace_timestamp(timestamp, node_name, namespace, pod_name, previous_state, current_state, controller_type, controller_name, pod_age):
    """Update the JSON structure with the state change details in Node -> Namespace -> Timestamp order."""
    if node_name not in json_data_node_namespace_timestamp:
        json_data_node_namespace_timestamp[node_name] = {}

    if namespace not in json_data_node_namespace_timestamp[node_name]:
        json_data_node_namespace_timestamp[node_name][namespace] = {}

    if timestamp not in json_data_node_namespace_timestamp[node_name][namespace]:
        json_data_node_namespace_timestamp[node_name][namespace][timestamp] = {}

    # Store pod state change, controller, and pod age in the JSON structure
    json_data_node_namespace_timestamp[node_name][namespace][timestamp][pod_name] = {
        "Previous State": previous_state,
        "Current State": current_state,
        "Controller": {
            "Type": controller_type,
            "Name": controller_name
        },
        "Pod Age": pod_age
    }

    # Write JSON data to file
    with open(JSON_FILE_NODE_NAMESPACE_TIMESTAMP, "w") as json_file:
        json.dump(json_data_node_namespace_timestamp, json_file, indent=4)

def get_pod_data():
    """Get pod information from kubectl and parse it as JSON."""
    try:
        # Retrieve all DaemonSet, ReplicaSet, and StatefulSet pods
        pods_data = check_output(
            "kubectl get pods -o json --all-namespaces", shell=True
        )
        pods_json = json.loads(pods_data)
        return pods_json.get("items", [])
    except Exception as e:
        print(f"Error fetching pod data: {e}")
        return []

def calculate_pod_age(creation_timestamp):
    """Calculate the age of the pod based on its creation timestamp."""
    try:
        # Parse creation timestamp to datetime
        creation_time = datetime.strptime(creation_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        current_time = datetime.utcnow()
        age = current_time - creation_time
        # Return age in a human-readable format (days, hours, minutes)
        days = age.days
        hours, remainder = divmod(age.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m"
    except Exception as e:
        return "Unknown"

def main():
    # Ensure the log directory exists
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    while True:
        # Dictionary to store logs grouped by namespace
        grouped_logs = {}

        # Get the current pod data
        pods = get_pod_data()

        for pod in pods:
            try:
                # Extract relevant pod details
                namespace = pod.get("metadata", {}).get("namespace", "unknown")
                pod_name = pod.get("metadata", {}).get("name", "unknown")
                current_state = pod.get("status", {}).get("phase", "unknown")
                node_name = pod.get("spec", {}).get("nodeName", "unknown")
                creation_timestamp = pod.get("metadata", {}).get("creationTimestamp", "unknown")
                deletion_timestamp = pod.get("metadata", {}).get("deletionTimestamp", "")
                owner_references = pod.get("metadata", {}).get("ownerReferences", [])

                # Calculate pod age
                pod_age = calculate_pod_age(creation_timestamp) if creation_timestamp != "unknown" else "Unknown"

                # Extract the controller type and name (e.g., ReplicaSet, DaemonSet, StatefulSet)
                controller_type = "Unknown"
                controller_name = "Unknown"
                if owner_references:
                    controller_type = owner_references[0].get("kind", "Unknown")
                    controller_name = owner_references[0].get("name", "Unknown")

                # Determine the correct state: if deletionTimestamp is present, it's Terminating
                if deletion_timestamp:
                    current_state = "Terminating"

                # Create a unique pod identifier
                pod_id = f"{namespace}/{pod_name}"

                # Retrieve the previous state from the dictionary
                previous_state = pod_states.get(pod_id, "UNKNOWN")

                # If the state has changed, log the change
                if previous_state != current_state:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_entry = (
                        f"  - Pod: {pod_name}\n"
                        f"    Node: {node_name}\n"
                        f"    Previous State: {previous_state}\n"
                        f"    Current State: {current_state}\n"
                        f"    Controller: {controller_type}/{controller_name}\n"
                        f"    Pod Age: {pod_age}\n"
                        f"    Timestamp: {timestamp}\n\n"
                    )

                    # Add log entry to the namespace group
                    if namespace not in grouped_logs:
                        grouped_logs[namespace] = []
                    grouped_logs[namespace].append(log_entry)

                    # Update all three JSON files with the change, controller info, and pod age
                    update_json_timestamp_first(timestamp, node_name, namespace, pod_name, previous_state, current_state, controller_type, controller_name, pod_age)
                    update_json_node_first(timestamp, node_name, namespace, pod_name, previous_state, current_state, controller_type, controller_name, pod_age)
                    update_json_node_namespace_timestamp(timestamp, node_name, namespace, pod_name, previous_state, current_state, controller_type, controller_name, pod_age)

                    # Update the state in the dictionary
                    pod_states[pod_id] = current_state

            except Exception as e:
                print(f"Error processing pod: {e}")

        # Write the grouped logs to the file, each namespace grouped together
        if grouped_logs:
            for ns, logs in grouped_logs.items():
                log_changes(ns, logs)

        # Pause for a few seconds before checking again
        time.sleep(10)

if __name__ == "__main__":
    main()

