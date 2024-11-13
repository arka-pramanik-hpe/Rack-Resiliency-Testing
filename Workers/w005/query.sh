#!/bin/bash

# List of sealed secrets to check
secrets=(
  "metallb-controller"
  "nexus"
  "cfs-hwsync-agent"
  "cfs-trust"
  "cray-bos-db"
  "cray-cfs-api-db"
  "cray-cfs-batcher"
  "cray-console-data"
  "cray-dhcp-kea"
  "cray-externaldns"
  "cray-ipxe"
  "gitea-vcs"
  "alertmanager-cray-sysmgmt-health-promet-alertmanager-0"
  "prometheus-cray-sysmgmt-health-promet-prometheus-0"
  "cray-vault-configurer"
  "spire-intermediate"
)

# File to search in
file_to_search="singleton.log"  # replace with the actual file if different

# Iterate over the list of secrets
for secret in "${secrets[@]}"; do
  if ! grep -q "$secret" "$file_to_search"; then
    echo "No match found for secret: $secret"
  fi
done
