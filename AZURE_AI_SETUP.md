# Azure AI Configuration Guide

## Option 1: Azure OpenAI Service (Recommended)

### Step 1: Create Azure OpenAI Resource
1. Go to Azure Portal (portal.azure.com)
2. Create new resource → AI + Machine Learning → Azure OpenAI
3. Fill in details:
   - Subscription: Your subscription
   - Resource Group: Use existing or create new
   - Region: Choose available region (e.g., East US, West Europe)
   - Name: e.g., "get-skills-openai"
   - Pricing Tier: Standard S0

### Step 2: Deploy a Model
1. Go to your Azure OpenAI resource
2. Click "Go to Azure OpenAI Studio" or use ai.azure.com
3. Go to "Deployments" → "Create new deployment"
4. Choose model: `gpt-35-turbo` or `gpt-4` (if available)
5. Deployment name: e.g., "gpt-35-turbo" (remember this name)

### Step 3: Get Configuration Values
From your Azure OpenAI resource overview page:
- **Endpoint**: e.g., `https://your-resource.openai.azure.com/`
- **API Key**: Go to "Keys and Endpoint" → Copy Key 1

### Step 4: Set Environment Variables

For Local Development:
```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-api-key-here"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-35-turbo"
```

For Azure App Service Deployment:
```bash
az webapp config appsettings set \
  --resource-group your-rg \
  --name your-app \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/" \
    AZURE_OPENAI_API_KEY="your-api-key-here" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-35-turbo"
```

## Option 2: Regular OpenAI (Alternative)

If you prefer to use OpenAI directly:

```bash
export OPENAI_API_KEY="sk-your-openai-key-here"
```

## Benefits of Azure OpenAI vs OpenAI

| Feature | Azure OpenAI | OpenAI Direct |
|---------|--------------|---------------|
| **Data Privacy** | Data stays in Azure region | Data goes to OpenAI servers |
| **Enterprise Features** | RBAC, VNets, Private Endpoints | Limited enterprise features |
| **Billing** | Part of Azure subscription | Separate OpenAI billing |
| **Compliance** | SOC, HIPAA, etc. | Limited compliance options |
| **Model Availability** | Slightly delayed new models | Latest models first |
| **Cost** | Potentially lower for high usage | Pay-per-use |

## Testing Your Configuration

Run the application and upload a document. Check the logs for:
- ✅ "Initialized Azure OpenAI with deployment: gpt-35-turbo"
- ✅ AI extraction working without errors

## Troubleshooting

**Error: "No AI service configured"**
- Check environment variables are set correctly
- Verify Azure OpenAI resource is deployed and running

**Error: "Model not found"**
- Ensure the deployment name matches AZURE_OPENAI_DEPLOYMENT_NAME
- Check the model is deployed in Azure OpenAI Studio

**Error: "Access denied"**
- Verify API key is correct
- Check Azure OpenAI resource permissions