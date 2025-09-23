# Azure Functions Monthly Analysis

This directory contains the Azure Functions implementation for automated monthly skills analysis.

## Features

- **Timer Trigger**: Automatically runs on the 1st of every month at midnight UTC
- **HTTP Triggers**: Manual execution and dashboard access
- **Secure**: Uses Azure Key Vault for configuration

## Functions

### 1. monthly_skills_analysis_timer
- **Trigger**: Timer (0 0 1 * *)
- **Purpose**: Automated monthly analysis
- **Schedule**: 1st day of every month at midnight UTC

### 2. monthly_analysis_http
- **Trigger**: HTTP
- **Methods**: GET (get latest report), POST (generate new report)
- **Auth**: Function key required

### 3. analysis_dashboard
- **Trigger**: HTTP
- **Purpose**: Simple HTML dashboard
- **Auth**: Anonymous access

## Deployment

1. **Create Function App**:
```bash
az functionapp create \
  --resource-group rg-dev-skills \
  --consumption-plan-location norwayeast \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name monthly-analysis-func-app \
  --storage-account sttedu5upjp2nl6
```

2. **Deploy Functions**:
```bash
cd monthly-analysis-function
func azure functionapp publish monthly-analysis-func-app
```

3. **Configure Settings**:
```bash
az functionapp config appsettings set \
  --name monthly-analysis-func-app \
  --resource-group rg-dev-skills \
  --settings "AZURE_KEYVAULT_URL=https://kv-tedu5upjp2nl6.vault.azure.net/"
```

## Usage

### Automatic Execution
The function automatically runs every month and generates analysis reports.

### Manual Execution
```bash
# Generate new report
curl -X POST "https://monthly-analysis-func-app.azurewebsites.net/api/monthly-analysis" \
  -H "Content-Type: application/json" \
  -d '{"month": "2025-09"}'

# Get latest report
curl "https://monthly-analysis-func-app.azurewebsites.net/api/monthly-analysis"
```

### Dashboard Access
Visit: `https://monthly-analysis-func-app.azurewebsites.net/api/analysis-dashboard`

## Configuration

The function uses the same Key Vault configuration as the main web application:
- Azure OpenAI credentials
- Storage account connection strings
- Application Insights connection string

## Monitoring

Monitor function execution through:
- Azure Portal Function App logs
- Application Insights
- Function execution history