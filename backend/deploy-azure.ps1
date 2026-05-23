# deploy-azure.ps1
# PowerShell script to deploy Sentexa backend to Azure Container Apps (ACA)

$ErrorActionPreference = "Stop"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "          SENTEXA BACKEND AZURE DEPLOYMENT AUTOMATOR                  " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# Configuration parameters
$resourceGroupName = "rg-sentexa-prod"
$location = "southeastasia"
$deploymentName = "sentexa-infra-deploy"
$envFilePath = ".env"

# 1. Verify Azure CLI is installed
Write-Host "`n[+] Checking Azure CLI installation..." -ForegroundColor Yellow
if (-not (Get-Command "az" -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI ('az') is not installed. Please install it from https://aka.ms/installazurecliwindows and try again."
}
Write-Host "[✓] Azure CLI is installed." -ForegroundColor Green

# 2. Check if logged in to Azure
Write-Host "`n[+] Checking Azure authentication status..." -ForegroundColor Yellow
$account = az account show --query "name" -o tsv 2>$null
if (-not $account) {
    Write-Host "[!] You are not logged in. Initiating Azure login..." -ForegroundColor Cyan
    az login
    $account = az account show --query "name" -o tsv
}
Write-Host "[✓] Logged in to Azure subscription: $account" -ForegroundColor Green

# 3. Read local .env secrets to configure Azure Container App securely
Write-Host "`n[+] Loading secrets from local $envFilePath..." -ForegroundColor Yellow
if (-not (Test-Path $envFilePath)) {
    Write-Error "Local environment file '$envFilePath' not found in backend directory. Please create it first."
}

$secrets = @{}
Get-Content $envFilePath | Where-Object { $_ -match "^[^#\s]+=.+" } | ForEach-Object {
    $parts = $_.Split('=', 2)
    $key = $parts[0].Trim()
    $val = $parts[1].Trim()
    $secrets[$key] = $val
}

# Validate essential keys are present
$essentialKeys = @("DATABASE_URL", "SECRET_KEY", "KAGGLE_USERNAME", "KAGGLE_KEY", "HF_TOKEN", "HF_MODEL")
foreach ($key in $essentialKeys) {
    if (-not $secrets.ContainsKey($key)) {
        Write-Error "Essential variable '$key' is missing from your $envFilePath. Please configure it."
    }
}
Write-Host "[✓] Loaded all environment settings and credentials successfully." -ForegroundColor Green

# 4. Ask user whether to bake ML model into the Docker image
$title = "Machine Learning Optimization"
$message = "Do you want to pre-download and bake the IndoBERT model into the Docker image?`n`n[YES] - (Recommended) Instant container startup, zero cold starts, offline safety. (Image is +450MB larger)`n[NO]  - Dynamic download on startup. Slower boot times, depends on HF Hub at runtime."
$options = [System.Management.Automation.Host.ChoiceDescription[]]@(
    New-Object System.Management.Automation.Host.ChoiceDescription "&Yes", "Pre-download and bake model into image"
    New-Object System.Management.Automation.Host.ChoiceDescription "&No", "Download model at runtime"
)
$result = $host.UI.PromptForChoice($title, $message, $options, 0)
$bakeModel = ($result -eq 0)

# 5. Create Resource Group if it doesn't exist
Write-Host "`n[+] Ensuring Resource Group '$resourceGroupName' exists in '$location'..." -ForegroundColor Yellow
az group create --name $resourceGroupName --location $location --output table

# 6. Deploy Azure Infrastructure (ACR, Log Analytics, ACA Env, Container App with Dummy Config)
Write-Host "`n[+] Deploying Azure infrastructure via Bicep template (deploy.bicep)..." -ForegroundColor Yellow
$bicepOutput = az deployment group create `
    --resource-group $resourceGroupName `
    --name $deploymentName `
    --template-file deploy.bicep `
    --parameters allowedOrigins="https://sentexa.vercel.app,http://localhost:3000" hfModel=$($secrets["HF_MODEL"]) `
    --query "properties.outputs" `
    --output json | ConvertFrom-Json

$acrLoginServer = $bicepOutput.acrLoginServer.value
$acrUsername = $bicepOutput.acrAdminUsername.value
$containerAppFqdn = $bicepOutput.fqdn.value

Write-Host "[✓] Infrastructure successfully provisioned." -ForegroundColor Green
Write-Host "    - ACR: $acrLoginServer" -ForegroundColor Gray
Write-Host "    - FQDN (Initial App URL): https://$containerAppFqdn" -ForegroundColor Gray

# 7. Pre-download model if requested
if ($bakeModel) {
    Write-Host "`n[+] Pre-downloading ML model ($($secrets["HF_MODEL"])) locally for Docker baking..." -ForegroundColor Yellow
    # Set HF_TOKEN locally for the download script
    $env:HF_TOKEN = $secrets["HF_TOKEN"]
    $env:HF_MODEL = $secrets["HF_MODEL"]
    
    python ml/scripts/download_model.py
    
    # Clear local env variables
    $env:HF_TOKEN = $null
    $env:HF_MODEL = $null
}

# 8. Check Docker installation and authenticate with ACR
Write-Host "`n[+] Checking Docker status..." -ForegroundColor Yellow
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "Docker Desktop is not installed or not in PATH. Docker is required to build and push backend images."
}

# Test if Docker daemon is running
$dockerPing = docker ps -q 2>&1
if ($dockerPing -match "error during connect") {
    Write-Error "Docker daemon is not running. Please start Docker Desktop and run this script again."
}
Write-Host "[✓] Docker is running." -ForegroundColor Green

# Fetch ACR password
Write-Host "`n[+] Authenticating with Azure Container Registry..." -ForegroundColor Yellow
$acrPassword = az acr credential show --name $acrUsername --resource-group $resourceGroupName --query "passwords[0].value" -o tsv
docker login --username $acrUsername --password $acrPassword $acrLoginServer

# 9. Build the Docker image
$imageTag = "$acrLoginServer/sentexa-backend:latest"
Write-Host "`n[+] Building Docker image ($imageTag)..." -ForegroundColor Yellow

if ($bakeModel) {
    Write-Host "    --> Baking model into container image..." -ForegroundColor Gray
    docker build `
        --build-arg PRE_DOWNLOAD_MODEL=true `
        --build-arg HF_MODEL=$($secrets["HF_MODEL"]) `
        --build-arg HF_TOKEN=$($secrets["HF_TOKEN"]) `
        -t $imageTag .
} else {
    Write-Host "    --> Skipping model baking (runtime download)..." -ForegroundColor Gray
    docker build -t $imageTag .
}
Write-Host "[✓] Docker image built successfully." -ForegroundColor Green

# 10. Push Docker image to ACR
Write-Host "`n[+] Pushing Docker image to Azure Container Registry..." -ForegroundColor Yellow
docker push $imageTag
Write-Host "[✓] Image successfully pushed to registry." -ForegroundColor Green

# 11. Securely provision actual production secrets to the Container App
Write-Host "`n[+] Securely updating Azure Container App secrets with production values..." -ForegroundColor Yellow
az containerapp secret set `
    --name ca-sentexa-backend `
    --resource-group $resourceGroupName `
    --secrets "database-url=$($secrets["DATABASE_URL"])" "secret-key=$($secrets["SECRET_KEY"])" "kaggle-username=$($secrets["KAGGLE_USERNAME"])" "kaggle-key=$($secrets["KAGGLE_KEY"])" "hf-token=$($secrets["HF_TOKEN"])" `
    --output table

# 12. Deploy the latest image revision to Container App
Write-Host "`n[+] Deploying latest image revision and starting container app..." -ForegroundColor Yellow
az containerapp update `
    --name ca-sentexa-backend `
    --resource-group $resourceGroupName `
    --image $imageTag `
    --output table

Write-Host "`n" + "="*80 -ForegroundColor Green
Write-Host " [✓] CONGRATULATIONS! SENTEXA BACKEND HAS BEEN DEPLOYED SUCCESSFULLY TO AZURE!" -ForegroundColor Green
Write-Host " ="*40 -ForegroundColor Green
Write-Host " Backend Public URL: https://$containerAppFqdn" -ForegroundColor Green
Write-Host " Health Check URL:   https://$containerAppFqdn/api/health" -ForegroundColor Gray
Write-Host " API Docs URL:       https://$containerAppFqdn/docs (Production docs are disabled by default)" -ForegroundColor Gray
Write-Host "="*80 -ForegroundColor Green
