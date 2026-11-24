resource "azurerm_resource_group" "this" {
  name     = "rg-${var.prefix}"
  location = var.location
  tags     = var.tags
}

resource "azurerm_kubernetes_cluster" "this" {
  name                = "${var.prefix}-aks"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  dns_prefix          = "${var.prefix}-aks"

  # Free tier: no charge for the control plane, you only pay for the nodes.
  sku_tier = "Free"

  # kubernetes_version is not set on purpose, so AKS picks its default supported version.

  default_node_pool {
    name                        = "system"
    vm_size                     = var.vm_size
    node_count                  = var.node_count
    os_disk_size_gb             = 64
    temporary_name_for_rotation = "systemtmp"
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin      = "azure"
    network_plugin_mode = "overlay"
  }

  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  tags = var.tags
}
