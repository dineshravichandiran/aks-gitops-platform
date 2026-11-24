#!/usr/bin/env bash
# Destroys the cluster. Pass --state to also delete the Terraform state storage.
set -euo pipefail

cd "$(dirname "$0")/../terraform"

terraform destroy -auto-approve

if [ "${1:-}" = "--state" ]; then
  az group delete --name rg-gitops-tfstate --yes --no-wait
  rm -f backend.hcl
  echo "State resource group is being deleted."
fi

echo "Check the Azure portal for any leftover resource groups."
