#!/usr/bin/env bash
# Creates the storage account that holds the Terraform state and writes
# terraform/backend.hcl. Run it once, after "az login".
set -euo pipefail

LOCATION="${LOCATION:-centralindia}"
STATE_RG="rg-gitops-tfstate"
CONTAINER="tfstate"
BACKEND_FILE="$(dirname "$0")/../terraform/backend.hcl"

if [ -f "$BACKEND_FILE" ]; then
  echo "backend.hcl already exists, nothing to do."
  exit 0
fi

# Storage account names must be globally unique, 3-24 lowercase letters and digits.
STATE_SA="tfstate$(openssl rand -hex 4)"

echo "Creating resource group $STATE_RG in $LOCATION"
az group create --name "$STATE_RG" --location "$LOCATION" --output none

echo "Creating storage account $STATE_SA"
az storage account create \
  --name "$STATE_SA" \
  --resource-group "$STATE_RG" \
  --location "$LOCATION" \
  --sku Standard_LRS \
  --allow-blob-public-access false \
  --min-tls-version TLS1_2 \
  --output none

az storage container create \
  --name "$CONTAINER" \
  --account-name "$STATE_SA" \
  --auth-mode key \
  --output none

cat > "$BACKEND_FILE" <<EOF
resource_group_name  = "$STATE_RG"
storage_account_name = "$STATE_SA"
container_name       = "$CONTAINER"
key                  = "aks-gitops.tfstate"
EOF

echo "Done. Wrote $BACKEND_FILE"
