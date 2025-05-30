provider "azurerm" {
  features {}
  subscription_id = "ba024c33-bcd0-4304-9f29-3bbcce04f297"
}

# 1. Resource Group
resource "azurerm_resource_group" "main" {
  name     = "myResourceGroup"
  location = "West Europe"
  

}

# 2. App Service Plan
resource "azurerm_service_plan" "main" {
  name                = "myAppServicePlan"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = "B1"
}

# 3. Web App (Linux with Python)
resource "azurerm_linux_web_app" "backend" {
  name                = "webapp-urlshortener"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    always_on = false
    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    "WEBSITE_RUN_FROM_PACKAGE" = "1"
  }
}

# 4. Cosmos DB Account (SQL API)
resource "azurerm_cosmosdb_account" "main" {
  name                = "cosmosdbaccountanandu"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }

  capabilities {
    name = "EnableServerless"
  }

  tags = {
    environment = "dev"
    test = "Anandu "
  }
}

# 5. Cosmos DB SQL Database
resource "azurerm_cosmosdb_sql_database" "main" {
  name                = "urlshortenerdb"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
}

resource "azurerm_cosmosdb_sql_container" "main" {
  name                = "urls"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_sql_database.main.name
  partition_key_paths = ["/id"]

  indexing_policy {
    indexing_mode = "consistent"
  }
}

# Triggering Jenkins CI/CD test


