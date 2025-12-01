# Contract Intelligence - Azure Deployment with azd

Complete guide for deploying Contract Intelligence to Azure Container Apps using Azure Developer CLI (azd).

## Table of Contents
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Reusing Existing Resources](#reusing-existing-resources)
- [Azure AD Authentication](#azure-ad-authentication)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)

## Architecture

### Deployed Resources

```
┌─────────────────────────────────────────────────────────────┐
│                     Azure Container Apps                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Contract Intelligence (Backend + Frontend)             │ │
│  │  - FastAPI backend (port 8000)                          │ │
│  │  - React frontend (static files)                        │ │
│  │  - GraphRAG data/output (baked into image)             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌────────────────┐  ┌──────────────┐  ┌──────────────┐
│ Azure OpenAI   │  │ PostgreSQL   │  │ Container    │
│ - gpt-4o       │  │ - Apache AGE │  │ Registry     │
│ - embeddings   │  │ - pgvector   │  │              │
└────────────────┘  └──────────────┘  └──────────────┘
```

**Services:**
- **Container App**: FastAPI + React frontend (single container)
- **PostgreSQL Flexible Server**: Contract data, graph database (Apache AGE)
- **Azure OpenAI**: LLM and embedding models
- **Container Registry**: Docker image storage
- **Log Analytics**: Application monitoring
- **Managed Identity**: Secure authentication to Azure services

## Prerequisites

### Required Tools
| Tool | Version | Installation |
|------|---------|--------------|
| Azure CLI | 2.50+ | https://aka.ms/azure-cli |
| Azure Developer CLI | 1.0+ | https://aka.ms/azd-install |
| Docker Desktop | 24.0+ | https://www.docker.com/products/docker-desktop |
| PowerShell | 7.0+ | https://github.com/PowerShell/PowerShell |

### Azure Requirements
- Active Azure subscription
- Owner or Contributor role
- Sufficient quotas for:
  - Azure OpenAI (2 deployments: chat + embeddings)
  - PostgreSQL Flexible Server (1 instance)
  - Container Apps (1 environment + 1 app)

## Quick Start

### Option 1: Deploy Everything (New Resources)

```powershell
# 1. Clone and navigate to project
cd c:\testing\graph\contract_intelligence

# 2. Login to Azure
azd auth login
az login

# 3. Initialize azd environment
azd init

# When prompted:
# Environment name: ci-dev
# Location: eastus2

# 4. Set PostgreSQL password (required for new database)
azd env set POSTGRES_ADMIN_PASSWORD "YourSecureP@ssw0rd123" --secret

# 5. Deploy everything (infrastructure + code)
azd up

# 6. Access your application
# URL will be displayed at the end: https://ci-xxxxx-app.xxx.azurecontainerapps.io
```

### Option 2: Deploy with Existing Resources

If you already have Azure OpenAI and/or PostgreSQL from another project, you can reuse them:

```powershell
# Initialize
azd init

# Set existing OpenAI:
azd env set EXISTING_OPENAI_ENDPOINT "https://eastus2oai.openai.azure.com/"
azd env set EXISTING_OPENAI_DEPLOYMENT_NAME "gpt-5.1"
azd env set EXISTING_OPENAI_EMBEDDING_DEPLOYMENT_NAME "text-embedding-3-small"

# Set existing PostgreSQL
azd env set EXISTING_POSTGRES_HOST "ci-ci-dev-pgflex.postgres.database.azure.com"
azd env set EXISTING_POSTGRES_DATABASE "cipgraph"
azd env set EXISTING_POSTGRES_USER "pgadmin"
azd env set EXISTING_POSTGRES_PASSWORD "YourPassword" --secret

# Deploy (will skip provisioning OpenAI and PostgreSQL)
azd up
```

## Reusing Existing Resources

### Reuse Existing Azure OpenAI

To avoid creating a new Azure OpenAI account (saves cost and quota):

```powershell
# Get existing OpenAI endpoint (example from Azure Portal or other deployment)
$openaiEndpoint = "https://your-openai.openai.azure.com/"
$chatDeployment = "gpt-4o"  # or "gpt-4", "gpt-35-turbo"
$embeddingDeployment = "text-embedding-3-small"

# Set in azd environment
azd env set EXISTING_OPENAI_ENDPOINT $openaiEndpoint
azd env set EXISTING_OPENAI_DEPLOYMENT_NAME $chatDeployment
azd env set EXISTING_OPENAI_EMBEDDING_DEPLOYMENT_NAME $embeddingDeployment
```

**Important:** The managed identity will be granted "Cognitive Services OpenAI User" role on the existing OpenAI account.

### Reuse Existing PostgreSQL

To connect to an existing PostgreSQL database:

```powershell
# Set existing PostgreSQL connection details
azd env set EXISTING_POSTGRES_HOST "your-server.postgres.database.azure.com"
azd env set EXISTING_POSTGRES_DATABASE "cipgraph"
azd env set EXISTING_POSTGRES_USER "pgadmin"
azd env set EXISTING_POSTGRES_PASSWORD "YourPassword" --secret
```

**Requirements:**
- Database must have extensions: `vector`, `pg_trgm`, `hstore`, `citext`, `age`
- Firewall must allow Azure services (IP: 0.0.0.0)
- Database should already contain contract data (run ingestion scripts)

### Check What Will Be Created

Before deploying, review the deployment plan:

```powershell
# Preview changes
azd provision --preview

# This shows:
# ✓ Resources that will be CREATED (new)
# ✓ Resources that will be SKIPPED (existing)
```

## Azure AD Authentication

The deployment automatically reuses Azure AD app registrations from the OpenAIWorkshop project (if available).

### Using Existing AAD Apps (Recommended)

The `preprovision.ps1` script automatically detects and reuses AAD configuration from `~/.azure/agenticaiworkshop/.env`:

```
AAD_FRONTEND_CLIENT_ID="0c2fc3b7-df66-4844-b3f4-80963ea92a0f"
AAD_TENANT_ID="0fbe7234-45ea-498b-b7e4-1a8b2d3be4d9"
AAD_API_APP_ID="48599190-c265-4c7b-8df1-b6d993fca800"
AAD_API_AUDIENCE="api://48599190-c265-4c7b-8df1-b6d993fca800"
```

**No additional setup required!** The preprovision hook handles this automatically.

### Manual AAD Configuration

If you don't have OpenAIWorkshop deployed, set AAD values manually:

```powershell
azd env set AAD_FRONTEND_CLIENT_ID "your-client-id"
azd env set AAD_TENANT_ID "your-tenant-id"
azd env set AAD_API_APP_ID "your-api-app-id"
azd env set AAD_API_AUDIENCE "api://your-api-app-id"
```

### Disable Authentication (Development Only)

For development/testing without AAD:

```powershell
azd env set DISABLE_AUTH "true"
```

## Advanced Configuration

### Environment Variables Reference

All environment variables can be set in `.azure/<env-name>/.env` or via `azd env set`:

#### Reusing Resources
| Variable | Description | Example |
|----------|-------------|---------|
| `EXISTING_OPENAI_ENDPOINT` | Azure OpenAI endpoint | `https://my-openai.openai.azure.com/` |
| `EXISTING_OPENAI_DEPLOYMENT_NAME` | Chat model deployment | `gpt-4o` |
| `EXISTING_OPENAI_EMBEDDING_DEPLOYMENT_NAME` | Embedding deployment | `text-embedding-3-small` |
| `EXISTING_POSTGRES_HOST` | PostgreSQL server FQDN | `my-server.postgres.database.azure.com` |
| `EXISTING_POSTGRES_DATABASE` | Database name | `cipgraph` |
| `EXISTING_POSTGRES_USER` | Admin username | `pgadmin` |
| `EXISTING_POSTGRES_PASSWORD` | Admin password | (secure value) |

#### New Resources
| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_ADMIN_PASSWORD` | Password for NEW PostgreSQL | (required) |
| `POSTGRES_DATABASE_NAME` | Database name | `cipgraph` |

#### Authentication
| Variable | Description | Default |
|----------|-------------|---------|
| `AAD_FRONTEND_CLIENT_ID` | Frontend SPA client ID | (from OpenAIWorkshop) |
| `AAD_TENANT_ID` | Azure AD tenant ID | (from OpenAIWorkshop) |
| `AAD_API_APP_ID` | Backend API app ID | (from OpenAIWorkshop) |
| `AAD_API_AUDIENCE` | API audience URI | (from OpenAIWorkshop) |
| `DISABLE_AUTH` | Disable AAD auth | `false` |

### Deployment Stages

```powershell
# Stage 1: Provision infrastructure only
azd provision

# Stage 2: Build and deploy code only
azd deploy

# Or do both in one command
azd up
```

### Update Deployment

```powershell
# Update infrastructure (Bicep changes)
azd provision

# Update application code (rebuild Docker image)
azd deploy

# Update environment variables without rebuild
azd env set MY_VAR "new-value"
azd deploy --no-build  # Refresh container with new env vars
```

### Monitor Application

```powershell
# Stream logs
azd logs --follow

# View specific service logs
az containerapp logs show \
  --name $(azd env get-value APPLICATION_NAME) \
  --resource-group $(azd env get-value AZURE_RESOURCE_GROUP) \
  --follow

# Check application health
curl $(azd env get-value APPLICATION_URL)/health
```

### Scale Configuration

Edit `infra/modules/application.bicep` to adjust scaling:

```bicep
scale: {
  minReplicas: 1      // Minimum instances
  maxReplicas: 10     // Maximum instances
  rules: [
    {
      name: 'http-scaling'
      http: {
        metadata: {
          concurrentRequests: '50'  // Scale trigger
        }
      }
    }
  ]
}
```

Then redeploy:
```powershell
azd provision
```

## Troubleshooting

### Issue: PostgreSQL Connection Timeout

**Symptom:** Container App can't connect to PostgreSQL

**Solution:**
```powershell
# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group $(azd env get-value AZURE_RESOURCE_GROUP) \
  --name $(azd env get-value POSTGRES_HOST | cut -d'.' -f1)

# Add rule for Azure services (should already exist)
az postgres flexible-server firewall-rule create \
  --resource-group $(azd env get-value AZURE_RESOURCE_GROUP) \
  --name $(azd env get-value POSTGRES_HOST | cut -d'.' -f1) \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### Issue: OpenAI 404 Error

**Symptom:** GraphRAG queries fail with "Resource not found"

**Solution:** Ensure deployment names match exactly:
```powershell
# Check actual deployment names in Azure Portal
# Update environment variables
azd env set EXISTING_OPENAI_DEPLOYMENT_NAME "gpt-4o"  # exact name
azd deploy
```

### Issue: Docker Build Fails

**Symptom:** `azd deploy` fails during Docker build

**Solution:**
```powershell
# Ensure Docker is running
docker version

# Test build locally
docker build -t test-ci .

# Check disk space
docker system df
docker system prune -a  # Clean up if needed
```

### Issue: Frontend Not Loading

**Symptom:** Application URL shows 404 or empty page

**Solution:**
```powershell
# Rebuild frontend and redeploy
cd frontend
npm install
npm run build

cd ..
azd deploy
```

### Issue: Authentication Fails

**Symptom:** "JWT validation failed" errors

**Solution:**
```powershell
# Verify AAD configuration
azd env get-value AAD_API_AUDIENCE
azd env get-value AAD_FRONTEND_CLIENT_ID

# Ensure redirect URIs are configured in Azure AD
# Should include: https://<your-app>.azurecontainerapps.io

# Disable auth temporarily for testing
azd env set DISABLE_AUTH "true"
azd deploy
```

### Get All Environment Variables

```powershell
# List all environment variables
azd env get-values

# Get specific value
azd env get-value APPLICATION_URL
```

### Clean Up and Redeploy

```powershell
# Delete all resources
azd down --force --purge

# Start fresh
azd up
```

## Cost Optimization

### Estimated Monthly Costs (Pay-as-you-go)

| Resource | Configuration | Est. Cost/Month |
|----------|--------------|-----------------|
| Container Apps | 1 instance, 2 vCPU, 4GB RAM | ~$60 |
| PostgreSQL Flexible | Standard_D2ds_v4, 256GB | ~$150 |
| Azure OpenAI | 50K chat tokens, 100K embeddings | ~$5 |
| Container Registry | Basic tier, <10GB | ~$5 |
| Log Analytics | 5GB ingestion | ~$12 |
| **TOTAL** | | **~$232/month** |

### Cost Savings Tips

1. **Reuse existing OpenAI** - Saves ~$5/month + avoids quota limits
2. **Reuse existing PostgreSQL** - Saves ~$150/month
3. **Scale down dev environments** - Set minReplicas: 0 when not in use
4. **Use B-series PostgreSQL** - For dev/test: ~$30/month
5. **Delete when not needed** - `azd down` removes all resources

## Next Steps

After successful deployment:

1. **Initialize Database** (if using NEW PostgreSQL):
   ```powershell
   python scripts/run_ingestion.py
   ```

2. **Index GraphRAG Data** (if not already indexed):
   ```powershell
   graphrag index --root graphrag_config
   ```

3. **Test the Application**:
   ```powershell
   # Get application URL
   $appUrl = azd env get-value APPLICATION_URL
   
   # Test health endpoint
   curl "$appUrl/health"
   
   # Open in browser
   Start-Process $appUrl
   ```

4. **Configure Custom Domain** (optional):
   ```powershell
   az containerapp hostname add \
     --name $(azd env get-value APPLICATION_NAME) \
     --resource-group $(azd env get-value AZURE_RESOURCE_GROUP) \
     --hostname yourdomain.com
   ```

## Support

For issues or questions:
- **Azure Developer CLI**: https://aka.ms/azd
- **Container Apps**: https://aka.ms/container-apps
- **Azure OpenAI**: https://aka.ms/azure-openai
