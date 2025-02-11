provider "azurerm" {
  features {}
  subscription_id = "55f0b9a1-fc98-42f9-8e54-a0a2eb57ea80"
}

resource "azurerm_resource_group" "example" {
  name     = "devopsProject1"
  location = "East US"
}

resource "azurerm_kubernetes_cluster" "example" {
  name                = "ask-devops-project"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  dns_prefix          = "ask-devops-project"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_DS2_v2"
  }

  identity {
    type = "SystemAssigned"
  }
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.example.kube_config_raw
  sensitive = true
}