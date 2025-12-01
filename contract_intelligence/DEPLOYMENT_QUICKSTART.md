# Azure Deployment Quick Start 🚀

Deploy Contract Intelligence to Azure Container Apps in minutes using Azure Developer CLI (azd).

## ⚡ Quick Deploy (5 minutes)

```powershell
# 1. Login
azd auth login

# 2. Initialize
azd init

# 3. Set PostgreSQL password
azd env set POSTGRES_ADMIN_PASSWORD "YourSecureP@ssw0rd123" --secret

# 4. Deploy everything
azd up
```

## 🎯 Deployment Options

### Option A: Fresh Deployment (New Resources)
Creates everything from scratch: Azure OpenAI, PostgreSQL, Container Apps
```powershell
azd up  # That's it!
```

### Option B: Reuse Existing OpenAI & PostgreSQL
Save money and quota by reusing existing resources:
```powershell
# Set existing OpenAI
azd env set EXISTING_OPENAI_ENDPOINT "https://my-openai.openai.azure.com/"
azd env set EXISTING_OPENAI_DEPLOYMENT_NAME "gpt-4o"
azd env set EXISTING_OPENAI_EMBEDDING_DEPLOYMENT_NAME "text-embedding-3-small"

# Set existing PostgreSQL
azd env set EXISTING_POSTGRES_HOST "my-server.postgres.database.azure.com"
azd env set EXISTING_POSTGRES_DATABASE "cipgraph"
azd env set EXISTING_POSTGRES_USER "pgadmin"
azd env set EXISTING_POSTGRES_PASSWORD "MyPassword" --secret

# Deploy (skips provisioning OpenAI and PostgreSQL)
azd up
```

### Option C: Reuse OpenAIWorkshop Resources
Automatically reuse Azure OpenAI and AAD apps from OpenAIWorkshop:
```powershell
# Copy OpenAIWorkshop OpenAI endpoint
azd env set EXISTING_OPENAI_ENDPOINT "$(az cognitiveservices account show -g rg-agenticaiworkshop -n aiws-*-openai --query properties.endpoint -o tsv)"
azd env set EXISTING_OPENAI_DEPLOYMENT_NAME "gpt-5-chat"
azd env set EXISTING_OPENAI_EMBEDDING_DEPLOYMENT_NAME "text-embedding-ada-002"

# AAD apps are auto-detected from ~/.azure/agenticaiworkshop/.env

# Deploy
azd up
```

## 📋 What Gets Deployed

| Resource | Purpose | Cost/Month | Can Reuse? |
|----------|---------|------------|------------|
| Container App | Backend + Frontend | ~$60 | ✗ |
| PostgreSQL Flexible | Graph database | ~$150 | ✅ |
| Azure OpenAI | LLM + Embeddings | ~$5 | ✅ |
| Container Registry | Docker images | ~$5 | ✗ |
| Log Analytics | Monitoring | ~$12 | ✗ |
| **TOTAL** | | **~$232/month** | |

**Reuse existing OpenAI and PostgreSQL to save ~$155/month!**

## 🔑 Environment Variables Guide

### Required (for NEW PostgreSQL)
```powershell
azd env set POSTGRES_ADMIN_PASSWORD "YourPassword123" --secret
```

### Optional (Reuse Existing Resources)
```powershell
# Existing OpenAI
azd env set EXISTING_OPENAI_ENDPOINT "https://..."
azd env set EXISTING_OPENAI_DEPLOYMENT_NAME "gpt-4o"
azd env set EXISTING_OPENAI_EMBEDDING_DEPLOYMENT_NAME "text-embedding-3-small"

# Existing PostgreSQL
azd env set EXISTING_POSTGRES_HOST "server.postgres.database.azure.com"
azd env set EXISTING_POSTGRES_DATABASE "cipgraph"
azd env set EXISTING_POSTGRES_USER "pgadmin"
azd env set EXISTING_POSTGRES_PASSWORD "password" --secret
```

### Authentication (Auto-configured)
```powershell
# Automatically set by preprovision.ps1 from OpenAIWorkshop
# Or set manually:
azd env set AAD_FRONTEND_CLIENT_ID "..."
azd env set AAD_TENANT_ID "..."
azd env set AAD_API_APP_ID "..."
azd env set AAD_API_AUDIENCE "api://..."

# Disable for development
azd env set DISABLE_AUTH "true"
```

## 🎬 Complete Example

```powershell
# Start from contract_intelligence directory
cd c:\testing\graph\contract_intelligence

# Login to Azure
azd auth login

# Initialize environment
azd init
# Environment name: ci-dev
# Location: eastus2

# Option 1: Fresh deployment with NEW resources
azd env set POSTGRES_ADMIN_PASSWORD "MySecure123!" --secret
azd up

# Option 2: Reuse OpenAIWorkshop OpenAI
$openaiEndpoint = az cognitiveservices account show \
  -g rg-agenticaiworkshop \
  -n $(az cognitiveservices account list -g rg-agenticaiworkshop --query "[?kind=='OpenAI'].name" -o tsv) \
  --query properties.endpoint -o tsv

azd env set EXISTING_OPENAI_ENDPOINT $openaiEndpoint
azd env set EXISTING_OPENAI_DEPLOYMENT_NAME "gpt-5-chat"
azd env set EXISTING_OPENAI_EMBEDDING_DEPLOYMENT_NAME "text-embedding-ada-002"
azd env set POSTGRES_ADMIN_PASSWORD "MySecure123!" --secret
azd up

# Access application
$appUrl = azd env get-value APPLICATION_URL
Start-Process $appUrl
```

## 🔧 Common Commands

```powershell
# Deploy/redeploy
azd up                    # Provision + deploy
azd provision             # Infrastructure only
azd deploy                # Code only

# Monitor
azd logs --follow         # Stream logs
azd monitor               # Open Azure Portal

# Update
azd env set VAR "value"   # Change environment variable
azd deploy                # Redeploy with new config

# Clean up
azd down                  # Delete all resources
azd down --force --purge  # Delete + purge
```

## 📚 Full Documentation

See [DEPLOYMENT.md](./DEPLOYMENT.md) for:
- Detailed architecture
- Troubleshooting guide
- Advanced configuration
- Cost optimization tips
- Custom domain setup

## 🆘 Quick Troubleshooting

**PostgreSQL connection fails**
```powershell
# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group $(azd env get-value AZURE_RESOURCE_GROUP) \
  --name $(azd env get-value POSTGRES_HOST | cut -d'.' -f1)
```

**OpenAI 404 error**
```powershell
# Verify deployment names match exactly
azd env get-value EXISTING_OPENAI_DEPLOYMENT_NAME
# Update if needed
azd env set EXISTING_OPENAI_DEPLOYMENT_NAME "gpt-4o"
azd deploy
```

**Frontend not loading**
```powershell
# Rebuild and redeploy
cd frontend && npm run build && cd ..
azd deploy
```

**View all environment variables**
```powershell
azd env get-values
```

## 🎉 Success Checklist

After deployment:
- [ ] Application URL responds (check `/health`)
- [ ] Frontend loads (React UI)
- [ ] PostgreSQL connects (run a query)
- [ ] GraphRAG works (try a thematic query)
- [ ] Authentication works (if enabled)

## 💡 Tips

1. **Reuse resources** - Set `EXISTING_*` variables to save money
2. **Use existing AAD apps** - Deploy OpenAIWorkshop first, then reuse its AAD configuration
3. **Monitor costs** - Check Azure Portal → Cost Management
4. **Scale to zero** - Set `minReplicas: 0` in dev environments
5. **Delete when not needed** - `azd down` to remove all resources

## 📖 Related Documentation

- [Full Deployment Guide](./DEPLOYMENT.md)
- [Environment Variables](./.env.azure.example)
- [Azure Developer CLI](https://aka.ms/azd)
- [Container Apps](https://aka.ms/container-apps)

---

**Questions?** See [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive documentation.
