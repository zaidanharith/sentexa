param (
    [switch]$CI = $false
)

$ErrorActionPreference = "Stop"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "          SENTEXA BACKEND AZURE DEPLOYMENT AUTOMATOR                  " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$resourceGroupName = "Sentexa-RG"
$location = "eastus"
$deploymentName = "sentexa-infra-deploy"
$envFilePath = ".env"

# 1. Verify Azure CLI is installed
Write-Host "`n[+] Checking Azure CLI installation..." -ForegroundColor Yellow
if (-not (Get-Command "az" -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI ('az') is not installed. Please install it from https://aka.ms/installazurecliwindows and try again."
}
Write-Host "[OK] Azure CLI is installed." -ForegroundColor Green

# 2. Check if logged in to Azure (Lewati jika di CI karena GitHub Actions sudah login)
Write-Host "`n[+] Checking Azure authentication status..." -ForegroundColor Yellow
$account = az account show --query "name" -o tsv 2>$null
if (-not $account -and -not $CI) {
    Write-Host "[!] You are not logged in. Initiating Azure login..." -ForegroundColor Cyan
    az login
    $account = az account show --query "name" -o tsv
}
if ($account) { Write-Host "[OK] Logged in to Azure subscription: $account" -ForegroundColor Green }

# 3 dan 4. Setup Secrets & Mode berdasarkan Lingkungan (Lokal vs CI/CD)
$secrets = @{}

if ($CI) {
    Write-Host "`n[+] [CI/CD MODE] Loading secrets from Environment Variables..." -ForegroundColor Yellow
    $secrets["DATABASE_URL"] = $env:DATABASE_URL
    $secrets["SECRET_KEY"] = $env:SECRET_KEY
    $secrets["KAGGLE_USERNAME"] = $env:KAGGLE_USERNAME
    $secrets["KAGGLE_KEY"] = $env:KAGGLE_KEY
    $secrets["HF_TOKEN"] = $env:HF_TOKEN
    $secrets["HF_MODEL"] = $env:HF_MODEL

    $bakeModel = $false
} else {
    Write-Host "`n[+] [LOCAL MODE] Loading secrets from local $envFilePath..." -ForegroundColor Yellow
    if (-not (Test-Path $envFilePath)) {
        Write-Error "Local environment file '$envFilePath' not found."
    }

    Get-Content $envFilePath | Where-Object { $_ -match "^[^#\s]+=.+" } | ForEach-Object {
        $parts = $_.Split('=', 2)
        $secrets[$parts[0].Trim()] = $parts[1].Trim()
    }

    $title = "Machine Learning Optimization"
    $message = "Do you want to pre-download and bake the IndoBERT model into the Docker image?"
    $yesChoice = New-Object System.Management.Automation.Host.ChoiceDescription "Yes", "Pre-download and bake model into image"
    $noChoice = New-Object System.Management.Automation.Host.ChoiceDescription "No", "Download model at runtime"
    $options = [System.Management.Automation.Host.ChoiceDescription[]]($yesChoice, $noChoice)
    $result = $host.UI.PromptForChoice($title, $message, $options, 0)
    $bakeModel = ($result -eq 0)
}

$essentialKeys = @("DATABASE_URL", "SECRET_KEY", "KAGGLE_USERNAME", "KAGGLE_KEY", "HF_TOKEN", "HF_MODEL")
foreach ($key in $essentialKeys) {
    if ([string]::IsNullOrWhiteSpace($secrets[$key])) {
        Write-Error "Essential variable '$key' is missing. Please configure it."
    }
}

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

Write-Host "[OK] Infrastructure successfully provisioned." -ForegroundColor Green
Write-Host "    - ACR: $acrLoginServer" -ForegroundColor Gray
Write-Host "    - FQDN (Initial App URL): https://$containerAppFqdn" -ForegroundColor Gray

# 7. Pre-download model if requested
if ($bakeModel) {
    Write-Host "`n[+] Pre-downloading ML model ($($secrets["HF_MODEL"])) locally for Docker baking..." -ForegroundColor Yellow
    $env:HF_TOKEN = $secrets["HF_TOKEN"]
    $env:HF_MODEL = $secrets["HF_MODEL"]
    
    try {
        python ml/scripts/download_model.py
    } catch {
        Write-Error "Gagal mendownload model secara lokal karena dependensi Python (torch/transformers) belum lengkap. Sediakan library tersebut atau jalankan ulang skrip lalu pilih opsi [NO]."
    }
    
    $env:HF_TOKEN = $null
    $env:HF_MODEL = $null
}

# 8. Check Docker installation and authenticate with ACR
Write-Host "`n[+] Checking Docker status..." -ForegroundColor Yellow
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "Docker Desktop is not installed or not in PATH."
}

$dockerPing = docker ps -q 2>&1
if ($dockerPing -match "error during connect") {
    Write-Error "Docker daemon is not running. Please start Docker Desktop and run this script again."
}
Write-Host "[OK] Docker is running." -ForegroundColor Green

# PENGAMAN: Jika karena alasan tertentu $acrUsername kosong dari output bicep, kita paksa isi dengan registry kamu
if ([string]::IsNullOrEmpty($acrUsername)) {
    $acrUsername = "sentexaregistry"
}

Write-Host "`n[+] Authenticating with Azure Container Registry ($acrUsername)..." -ForegroundColor Yellow
$acrPassword = az acr credential show --name $acrUsername --resource-group $resourceGroupName --query "passwords[0].value" -o tsv
docker login --username $acrUsername --password $acrPassword $acrLoginServer

# 9. Build the Docker image
$imageTag = "$acrLoginServer/sentexa-backend:$env:GITHUB_SHA"
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
Write-Host "[OK] Docker image built successfully." -ForegroundColor Green

# 10. Push Docker image to ACR
Write-Host "`n[+] Pushing Docker image to Azure Container Registry..." -ForegroundColor Yellow
docker push $imageTag
Write-Host "[OK] Image successfully pushed to registry." -ForegroundColor Green

# 11. Securely provision actual production secrets to the Container App
Write-Host "`n[+] Securely updating Azure Container App secrets with production values..." -ForegroundColor Yellow
az containerapp secret set `
    --name sentexa-api `
    --resource-group $resourceGroupName `
    --secrets "database-url=$($secrets["DATABASE_URL"])" "secret-key=$($secrets["SECRET_KEY"])" "kaggle-username=$($secrets["KAGGLE_USERNAME"])" "kaggle-key=$($secrets["KAGGLE_KEY"])" "hf-token=$($secrets["HF_TOKEN"])" `
    --output table

# 12. Deploy the latest image revision to Container App
Write-Host "`n[+] Deploying latest image revision and starting container app..." -ForegroundColor Yellow
az containerapp update `
    --name sentexa-api `
    --resource-group $resourceGroupName `
    --image $imageTag `
    --output table

Write-Host "`n" + "="*80 -ForegroundColor Green
Write-Host " [OK] CONGRATULATIONS! SENTEXA BACKEND HAS BEEN DEPLOYED SUCCESSFULLY TO AZURE!" -ForegroundColor Green
Write-Host " ="*40 -ForegroundColor Green
Write-Host " Backend Public URL: https://$containerAppFqdn" -ForegroundColor Green
Write-Host " Health Check URL:   https://$containerAppFqdn/api/health" -ForegroundColor Gray
Write-Host "="*80 -ForegroundColor Green