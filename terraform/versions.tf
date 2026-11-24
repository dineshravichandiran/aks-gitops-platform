terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  # Remote state in an Azure Storage account.
  # The details live in backend.hcl, which scripts/bootstrap-state.sh creates.
  backend "azurerm" {}
}

# The subscription is read from the ARM_SUBSCRIPTION_ID environment variable.
provider "azurerm" {
  features {}
}
