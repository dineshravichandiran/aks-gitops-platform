variable "prefix" {
  description = "Short name used as a prefix for all resources."
  type        = string
  default     = "gitops"
}

variable "location" {
  description = "Azure region."
  type        = string
  default     = "centralindia"
}

variable "node_count" {
  description = "Number of nodes in the default node pool."
  type        = number
  default     = 2
}

variable "vm_size" {
  description = "VM size for the nodes. Change it if your subscription has no quota for this size in the region."
  type        = string
  default     = "Standard_B2s"
}

variable "tags" {
  description = "Tags added to every resource."
  type        = map(string)
  default = {
    project = "aks-gitops-platform"
    purpose = "learning-lab"
  }
}
