module "naming" {
  source  = "Azure/naming/azurerm"
  prefix = [ var.env ]
  suffix = [ "${var.myname}","${var.location}"  ]

}

resource "azurerm_resource_group" "rg" {
  name     = module.naming.resource_group.name
  location = var.location
}

module "asp_plan" {
  source  = "Azure/avm-res-web-serverfarm/azurerm"
  version = "0.6.0"

  name                = module.naming.app_service_plan.name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku_name            = "F1"
  os_type             = "Linux"
  zone_balancing_enabled      = false
  worker_count         = 1
}

module "web_app" {
  source  = "Azure/avm-res-web-site/azurerm"
  version = "0.17.1"

  name                     = module.naming.app_service.name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  service_plan_resource_id = module.asp_plan.resource_id
  
  os_type                  = "Linux"
  kind                     = "webapp"
  fc1_runtime_name         = "python"
  fc1_runtime_version      = "3.8"
  
  site_config = {
    always_on = false
    use_32_bit_worker       = true
  }
}




# resource "azurerm_service_plan" "name" {
#     name = module.naming.app_service_plan.name
#     location = azurerm_resource_group.rg.location
#     resource_group_name = azurerm_resource_group.rg.name
#     sku_name = "F1"
#     os_type = "Linux"
    
# }

# resource "azurerm_linux_web_app" "name" {
#     name = module.naming.app_service.name
#     location = azurerm_resource_group.rg.location
#     resource_group_name = azurerm_resource_group.rg.name
#     service_plan_id = azurerm_service_plan.name.id
#     site_config {
#         always_on                               = false
#         application_stack {
#             python_version = "3.8"
#         }
#     }
# }

