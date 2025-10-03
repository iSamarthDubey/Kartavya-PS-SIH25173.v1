# PowerShell script to install and configure Filebeat and Metricbeat for log collection

param(
    [string]$ElasticHost = "localhost",
    [int]$ElasticPort = 9200,
    [string]$InstallPath = "C:\elastic-beats"
)

Write-Host "Starting Elastic Beats installation..." -ForegroundColor Green

# Create installation directory
if (!(Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force
    Write-Host "Created directory: $InstallPath" -ForegroundColor Yellow
}

# Download URLs (update these to current stable versions as needed)
# Check https://www.elastic.co/downloads/beats for latest version numbers
$ElasticVersion = "8.15.3"  # Update this to current stable version
$FilebeatUrl = "https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-$ElasticVersion-windows-x86_64.zip"
$MetricbeatUrl = "https://artifacts.elastic.co/downloads/beats/metricbeat/metricbeat-$ElasticVersion-windows-x86_64.zip"

# Function to download and extract beats
function Install-Beat {
    param(
        [string]$BeatName,
        [string]$DownloadUrl,
        [string]$InstallDir
    )
    
    Write-Host "Installing $BeatName..." -ForegroundColor Yellow
    
    $ZipPath = Join-Path $InstallDir "$BeatName.zip"
    $ExtractPath = Join-Path $InstallDir $BeatName
    
    try {
        # Download
        Write-Host "Downloading $BeatName..."
        Invoke-WebRequest -Uri $DownloadUrl -OutFile $ZipPath
        
        # Extract
        Write-Host "Extracting $BeatName..."
        Expand-Archive -Path $ZipPath -DestinationPath $ExtractPath -Force
        
        # Move files to beat directory
        $ExtractedFolder = Get-ChildItem $ExtractPath | Where-Object { $_.PSIsContainer } | Select-Object -First 1
        if ($ExtractedFolder) {
            $FinalPath = Join-Path $InstallDir $BeatName
            if (Test-Path $FinalPath) {
                Remove-Item $FinalPath -Recurse -Force
            }
            Move-Item $ExtractedFolder.FullName $FinalPath
            Remove-Item $ExtractPath -Recurse -Force
        }
        
        # Clean up zip file
        Remove-Item $ZipPath -Force
        
        Write-Host "$BeatName installed successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to install $BeatName: $($_.Exception.Message)"
        return $false
    }
}

# Install Filebeat
$FilebeatInstalled = Install-Beat -BeatName "filebeat" -DownloadUrl $FilebeatUrl -InstallDir $InstallPath

# Install Metricbeat
$MetricbeatInstalled = Install-Beat -BeatName "metricbeat" -DownloadUrl $MetricbeatUrl -InstallDir $InstallPath

# Configure Filebeat
if ($FilebeatInstalled) {
    Write-Host "Configuring Filebeat..." -ForegroundColor Yellow
    
    $FilebeatConfig = @"
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - C:\Windows\System32\winevt\Logs\Security.evtx
    - C:\Windows\System32\winevt\Logs\System.evtx
    - C:\Windows\System32\winevt\Logs\Application.evtx
  fields:
    source: windows_events
  fields_under_root: true

- type: winlogbeat
  event_logs:
    - name: Security
      level: info
    - name: System
      level: warning
    - name: Application
      level: error

output.elasticsearch:
  hosts: ["$($ElasticHost):$($ElasticPort)"]
  index: "security-logs-%{+yyyy.MM.dd}"

setup.template.name: "security-logs"
setup.template.pattern: "security-logs-*"

logging.level: info
logging.to_files: true
logging.files:
  path: $InstallPath\filebeat\logs
  name: filebeat
  keepfiles: 7
  rotateeverybytes: 10485760
"@

    $FilebeatConfigPath = Join-Path $InstallPath "filebeat\filebeat.yml"
    $FilebeatConfig | Out-File -FilePath $FilebeatConfigPath -Encoding UTF8
    Write-Host "Filebeat configuration saved to: $FilebeatConfigPath" -ForegroundColor Green
}

# Configure Metricbeat
if ($MetricbeatInstalled) {
    Write-Host "Configuring Metricbeat..." -ForegroundColor Yellow
    
    $MetricbeatConfig = @"
metricbeat.config.modules:
  path: \${path.config}/modules.d/*.yml
  reload.enabled: false

metricbeat.modules:
- module: system
  metricsets:
    - cpu
    - load
    - memory
    - network
    - process
    - process_summary
    - socket_summary
  enabled: true
  period: 10s
  processes: ['.*']

- module: windows
  metricsets:
    - perfmon
    - service
  enabled: true
  period: 10s

output.elasticsearch:
  hosts: ["$($ElasticHost):$($ElasticPort)"]
  index: "metrics-%{+yyyy.MM.dd}"

setup.template.name: "metrics"
setup.template.pattern: "metrics-*"

logging.level: info
logging.to_files: true
logging.files:
  path: $InstallPath\metricbeat\logs
  name: metricbeat
  keepfiles: 7
  rotateeverybytes: 10485760
"@

    $MetricbeatConfigPath = Join-Path $InstallPath "metricbeat\metricbeat.yml"
    $MetricbeatConfig | Out-File -FilePath $MetricbeatConfigPath -Encoding UTF8
    Write-Host "Metricbeat configuration saved to: $MetricbeatConfigPath" -ForegroundColor Green
}

# Create start scripts
$StartScriptContent = @"
@echo off
echo Starting Elastic Beats...

cd /d "$InstallPath\filebeat"
start "Filebeat" filebeat.exe -c filebeat.yml

cd /d "$InstallPath\metricbeat" 
start "Metricbeat" metricbeat.exe -c metricbeat.yml

echo Beats started successfully!
pause
"@

$StartScriptPath = Join-Path $InstallPath "start_beats.bat"
$StartScriptContent | Out-File -FilePath $StartScriptPath -Encoding ASCII

# Create stop scripts
$StopScriptContent = @"
@echo off
echo Stopping Elastic Beats...

taskkill /f /im filebeat.exe 2>nul
taskkill /f /im metricbeat.exe 2>nul

echo Beats stopped!
pause
"@

$StopScriptPath = Join-Path $InstallPath "stop_beats.bat"
$StopScriptContent | Out-File -FilePath $StopScriptPath -Encoding ASCII

Write-Host "`nInstallation Summary:" -ForegroundColor Cyan
Write-Host "- Installation Path: $InstallPath" -ForegroundColor White
Write-Host "- Elasticsearch Host: $ElasticHost:$ElasticPort" -ForegroundColor White
Write-Host "- Start Beats: $StartScriptPath" -ForegroundColor White
Write-Host "- Stop Beats: $StopScriptPath" -ForegroundColor White

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "1. Ensure Elasticsearch is running on $ElasticHost:$ElasticPort" -ForegroundColor Yellow
Write-Host "2. Run $StartScriptPath to start log collection" -ForegroundColor Yellow
Write-Host "3. Check logs in Elasticsearch using Kibana or the SIEM Assistant" -ForegroundColor Yellow

Write-Host "`nElastic Beats installation completed!" -ForegroundColor Green