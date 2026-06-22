# Deploy SentinelAI to Zoho Catalyst
# Prerequisites: Zoho Catalyst CLI installed and configured
param(
    [string]$Action = "deploy"
)

$PROJECT_DIR = "D:\Projects\SentinelAI"
$CATALYST_PROJECT_ID = "43547000000013050"

function Deploy-Functions {
    Write-Host "Deploying Catalyst functions..." -ForegroundColor Cyan
    $functions = @("generate-pdf", "export-report", "process-voice", "sentinel_utils")
    foreach ($fn in $functions) {
        $path = Join-Path $PROJECT_DIR "functions\$fn"
        if (Test-Path $path) {
            Write-Host "  Deploying $fn..." -ForegroundColor Yellow
            Push-Location $path
            & catalyst function:deploy
            Pop-Location
        }
    }
}

function Deploy-Backend {
    Write-Host "Deploying backend to AppSail..." -ForegroundColor Cyan
    Push-Location (Join-Path $PROJECT_DIR "backend")
    & catalyst app:sail:deploy
    Pop-Location
}

function Deploy-Frontend {
    Write-Host "Building and deploying frontend to AppSail..." -ForegroundColor Cyan
    Push-Location (Join-Path $PROJECT_DIR "frontend")
    Write-Host "  Building..." -ForegroundColor Yellow
    npm run build
    Write-Host "  Deploying to AppSail..." -ForegroundColor Yellow
    & catalyst app:sail:deploy
    Pop-Location
}

switch ($Action) {
    "functions" { Deploy-Functions }
    "backend" { Deploy-Backend }
    "frontend" { Deploy-Frontend }
    "all" {
        Deploy-Functions
        Deploy-Backend
        Deploy-Frontend
    }
    default {
        Write-Host @"
Usage: .\deploy-catalyst.ps1 [action]
Actions:
  functions   Deploy all Catalyst functions
  backend     Deploy backend to AppSail
  frontend    Deploy frontend to AppSail
  all         Deploy everything
"@ -ForegroundColor Green
    }
}
