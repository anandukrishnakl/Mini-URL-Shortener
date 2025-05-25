output "app_service_url" {
  value = azurerm_linux_web_app.backend.default_hostname
}

output "cosmosdb_account_endpoint" {
  value = azurerm_cosmosdb_account.main.endpoint
}
