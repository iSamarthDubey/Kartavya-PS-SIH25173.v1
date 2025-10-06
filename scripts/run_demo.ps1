param(
    [int]$BackendPort = 8100,
    [string]$BackendHost = "0.0.0.0",
    [string]$FrontendHost = "localhost",
    [int]$FrontendPort = 8501,
    [string]$DemoUsername,
    [string]$DemoPassword,
    [string]$AdminPassword,
    [switch]$SkipTests,
    [switch]$NoFrontend
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")

Push-Location $repoRoot

if (-not $DemoUsername) {
    $DemoUsername = $env:ASSISTANT_DEMO_USERNAME
}
if (-not $DemoUsername) {
    $DemoUsername = "admin"
}

if (-not $DemoPassword) {
    $DemoPassword = $env:ASSISTANT_DEMO_PASSWORD
}
if (-not $DemoPassword) {
    $DemoPassword = "Admin!2025"
}

if ($AdminPassword) {
    $env:ASSISTANT_ADMIN_PASSWORD = $AdminPassword
}

$env:ASSISTANT_DEMO_USER = $DemoUsername
$env:ASSISTANT_DEMO_USERNAME = $DemoUsername
$env:ASSISTANT_DEMO_PASSWORD = $DemoPassword

$backendProcess = $null
$frontendProcess = $null

try {
    if (-not $SkipTests) {
        Write-Host "Running preflight tests (tests/run_complete_tests.py)..." -ForegroundColor Cyan
        python tests/run_complete_tests.py
        if ($LASTEXITCODE -ne 0) {
            throw "Test suite failed. Resolve the failures or re-run with -SkipTests."
        }
    }

    $env:ASSISTANT_HOST = $BackendHost
    $env:ASSISTANT_PORT = $BackendPort.ToString()

    $backendUrlHost = $FrontendHost
    if (-not $backendUrlHost -or $backendUrlHost -eq "0.0.0.0") {
        $backendUrlHost = "localhost"
    }
    $env:ASSISTANT_BACKEND_URL = "http://$backendUrlHost:$BackendPort"

    Write-Host "Starting backend with uvicorn on $BackendHost:$BackendPort..." -ForegroundColor Cyan
    $backendArgs = @(
        "-m", "uvicorn", "assistant.main:app",
        "--host", $BackendHost,
        "--port", $BackendPort.ToString()
    )
    $backendProcess = Start-Process -FilePath "python" -ArgumentList $backendArgs -PassThru -NoNewWindow -WorkingDirectory $repoRoot

    $maxAttempts = 30
    $ready = $false
    for ($attempt = 0; $attempt -lt $maxAttempts; $attempt++) {
        if ($backendProcess.HasExited) {
            throw "Backend process exited early with code $($backendProcess.ExitCode). Check backend.log for details."
        }

        $listening = Test-NetConnection -ComputerName "localhost" -Port $BackendPort -InformationLevel Quiet
        if ($listening) {
            $ready = $true
            break
        }
        Start-Sleep -Seconds 1
    }

    if (-not $ready) {
        throw "Backend did not become ready on port $BackendPort within $maxAttempts seconds."
    }

    if (-not $NoFrontend) {
        Write-Host "Launching Streamlit UI on $FrontendHost:$FrontendPort..." -ForegroundColor Cyan
        $frontendArgs = @(
            "-m", "streamlit", "run", "ui_dashboard/streamlit_app.py",
            "--server.port", $FrontendPort.ToString(),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        )

        if ($FrontendHost -ne "localhost") {
            $frontendArgs += @("--server.address", $FrontendHost)
        }

        $frontendProcess = Start-Process -FilePath "python" -ArgumentList $frontendArgs -PassThru -NoNewWindow -WorkingDirectory $repoRoot
    }

    Write-Host "" # Blank line
    Write-Host "Demo environment is running:" -ForegroundColor Green
    Write-Host ("  Backend API   : http://{0}:{1}/assistant/ask" -f $backendUrlHost, $BackendPort)
    if (-not $NoFrontend) {
        Write-Host ("  Streamlit UI : http://{0}:{1}" -f $FrontendHost, $FrontendPort)
    }
    Write-Host ("  Demo user      : {0}" -f $DemoUsername)
    Write-Host "Press Enter to stop both services..."
    [void][System.Console]::ReadLine()
}
finally {
    if ($frontendProcess -and -not $frontendProcess.HasExited) {
        Write-Host "Stopping Streamlit UI..." -ForegroundColor Yellow
        Stop-Process -Id $frontendProcess.Id -Force
    }

    if ($backendProcess -and -not $backendProcess.HasExited) {
        Write-Host "Stopping backend..." -ForegroundColor Yellow
        Stop-Process -Id $backendProcess.Id -Force
    }

    Pop-Location
}
