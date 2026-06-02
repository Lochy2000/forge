# Grant Vault — Startup Script
# Run from the vault/ directory: .\start.ps1

Write-Host ""
Write-Host "Grant Vault"
Write-Host "==========="

# --- Step 1: Check Ollama ---

Write-Host ""
Write-Host "Checking Ollama..."

function Test-OllamaPort {
    try {
        $tcp = [System.Net.Sockets.TcpClient]::new()
        $connect = $tcp.BeginConnect("localhost", 11434, $null, $null)
        $wait = $connect.AsyncWaitHandle.WaitOne(1000)
        if ($wait -and $tcp.Connected) {
            $tcp.Close()
            return $true
        }
        $tcp.Close()
        return $false
    } catch {
        return $false
    }
}

$ollamaReady = Test-OllamaPort

if ($ollamaReady) {
    Write-Host "  Ollama already running."
} else {
    Write-Host "  Starting Ollama..."
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Minimized

    $attempts = 0
    while (-not $ollamaReady -and $attempts -lt 15) {
        Start-Sleep -Seconds 2
        $attempts++
        $ollamaReady = Test-OllamaPort
    }

    if (-not $ollamaReady) {
        Write-Host ""
        Write-Host "ERROR: Ollama did not start. Check that ollama is installed and on your PATH."
        Write-Host "Install from: https://ollama.com"
        exit 1
    }

    Write-Host "  Ollama ready."
}

# --- Step 2: Check embedding model ---

Write-Host ""
Write-Host "Checking embedding model (nomic-embed-text)..."

try {
    $modelsJson = ollama list 2>&1 | Out-String
    if ($modelsJson -match "nomic-embed-text") {
        Write-Host "  nomic-embed-text found."
    } else {
        Write-Host "  Pulling nomic-embed-text..."
        ollama pull nomic-embed-text
    }
} catch {
    Write-Host "  WARNING: Could not verify embedding model. Continuing anyway."
}

# --- Step 3: Check vault has been ingested ---

Write-Host ""
Write-Host "Checking vault..."

$vaultRunning = $false
try {
    $tcp = [System.Net.Sockets.TcpClient]::new()
    $connect = $tcp.BeginConnect("localhost", 8100, $null, $null)
    $wait = $connect.AsyncWaitHandle.WaitOne(1000)
    if ($wait -and $tcp.Connected) { $vaultRunning = $true }
    $tcp.Close()
} catch {}

if ($vaultRunning) {
    Write-Host "  Vault API already running on port 8100."
    Write-Host ""
    Write-Host "Vault is ready."
    Write-Host "  API:  http://localhost:8100"
    Write-Host "  Docs: http://localhost:8100/docs"
    exit 0
}

# --- Step 4: Activate venv ---

Write-Host ""
Write-Host "Activating virtual environment..."

if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host ""
    Write-Host "ERROR: venv not found. Run from the vault/ directory with the venv set up."
    Write-Host "  To create: python -m venv venv"
    Write-Host "  To install: pip install -r requirements.txt"
    exit 1
}

& ".\venv\Scripts\Activate.ps1"
Write-Host "  venv active."

# --- Step 5: Check ChromaDB has data ---

Write-Host ""
Write-Host "Checking document vault..."

if (-not (Test-Path ".\chroma_db")) {
    Write-Host ""
    Write-Host "WARNING: No chroma_db found. The vault is empty."
    Write-Host "  Run: python -m backend.ingest"
    Write-Host "  Then restart this script."
    Write-Host ""
}

# --- Step 6: Start vault API ---

Write-Host ""
Write-Host "Starting vault API on http://localhost:8100..."
Write-Host "  Docs: http://localhost:8100/docs"
Write-Host "  Press Ctrl+C to stop."
Write-Host ""

uvicorn backend.api:app --port 8100
