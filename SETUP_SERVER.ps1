$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " YouCube Backend - Public Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

function Find-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return "py"
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return "python"
    }
    return $null
}

$PythonCmd = Find-Python
if (-not $PythonCmd) {
    Write-Host "[ERROR] Python was not found." -ForegroundColor Red
    Write-Host "Install Python 3.11 or 3.12 from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "During install, enable 'Add Python to PATH'." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[1/6] Creating Python virtual environment..."
    if ($PythonCmd -eq "py") {
        & py -3 -m venv .venv
    } else {
        & python -m venv .venv
    }
}

$Py = Join-Path $Root ".venv\Scripts\python.exe"

Write-Host "[2/6] Updating Python package tools..."
& $Py -m pip install --upgrade pip setuptools wheel

Write-Host "[3/6] Installing backend dependencies..."
& $Py -m pip install -r requirements.txt

New-Item -ItemType Directory -Force tools | Out-Null

if (-not (Test-Path "tools\sanjuuni.exe")) {
    Write-Host "[4/6] Downloading Sanjuuni..."
    try {
        $headers = @{ "User-Agent" = "YouCubeBackendSetup" }
        $rel = Invoke-RestMethod `
            -Headers $headers `
            "https://api.github.com/repos/MCJack123/sanjuuni/releases/latest"

        $asset = $rel.assets |
            Where-Object { $_.name -match "(?i)(win|windows|x64).*\.zip$" } |
            Select-Object -First 1

        if (-not $asset) {
            $asset = $rel.assets |
                Where-Object { $_.name -match "(?i)\.zip$" } |
                Select-Object -First 1
        }

        if ($asset) {
            $zip = Join-Path $env:TEMP $asset.name
            $tmp = Join-Path $env:TEMP "youcube_sanjuuni_unpack"

            Invoke-WebRequest $asset.browser_download_url -OutFile $zip

            if (Test-Path $tmp) {
                Remove-Item $tmp -Recurse -Force
            }

            Expand-Archive $zip $tmp -Force

            $exe = Get-ChildItem $tmp -Recurse -Filter "sanjuuni.exe" |
                Select-Object -First 1

            if ($exe) {
                Copy-Item $exe.FullName "tools\sanjuuni.exe" -Force
                Get-ChildItem $exe.DirectoryName -Filter "*.dll" |
                    ForEach-Object {
                        Copy-Item $_.FullName "tools\$($_.Name)" -Force
                    }
                Write-Host "      Sanjuuni installed." -ForegroundColor Green
            } else {
                Write-Host "      Sanjuuni executable was not found in the release archive." -ForegroundColor Yellow
            }
        } else {
            Write-Host "      No suitable Sanjuuni Windows ZIP was found." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "      Automatic Sanjuuni download failed: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "[4/6] Sanjuuni already installed."
}

Write-Host "[5/6] Checking FFmpeg..."
if (Test-Path "tools\ffmpeg.exe") {
    Write-Host "      Local FFmpeg found." -ForegroundColor Green
} elseif (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Host "      System FFmpeg found." -ForegroundColor Green
} else {
    Write-Host "      FFmpeg was not found." -ForegroundColor Yellow
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        $answer = Read-Host "Install FFmpeg with winget now? (Y/N)"
        if ($answer -match "^(y|yes)$") {
            winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
        }
    } else {
        Write-Host "      Install FFmpeg manually and place ffmpeg.exe in the tools folder," -ForegroundColor Yellow
        Write-Host "      or add FFmpeg to your Windows PATH." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[6/6] Building YouCubeServer.exe..." -ForegroundColor Cyan

try {
    & $Py -m pip install --upgrade pyinstaller

    if (Test-Path "build") {
        Remove-Item "build" -Recurse -Force -ErrorAction SilentlyContinue
    }

    if (Test-Path "dist") {
        Remove-Item "dist" -Recurse -Force -ErrorAction SilentlyContinue
    }

    if (Test-Path "YouCubeServer.spec") {
        Remove-Item "YouCubeServer.spec" -Force -ErrorAction SilentlyContinue
    }

    & $Py -m PyInstaller `
        --noconfirm `
        --clean `
        --onefile `
        --windowed `
        --name YouCubeServer `
        YouCubeServerGUI.py

    if (Test-Path "dist\YouCubeServer.exe") {
        Copy-Item "dist\YouCubeServer.exe" "YouCubeServer.exe" -Force

        # Remove build-only folders from the finished installation.
        Remove-Item "build" -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item "dist" -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item "YouCubeServer.spec" -Force -ErrorAction SilentlyContinue

        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host " Setup complete!" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Normal use:" -ForegroundColor Cyan
        Write-Host "    Double-click YouCubeServer.exe" -ForegroundColor White
        Write-Host ""
        Write-Host "START_SERVER.bat is only a fallback." -ForegroundColor DarkGray
    } else {
        Write-Host ""
        Write-Host "[WARNING] Setup succeeded, but the EXE build did not produce YouCubeServer.exe." -ForegroundColor Yellow
        Write-Host "You can still use START_SERVER.bat, or run BUILD_GUI_EXE.bat later." -ForegroundColor Yellow
    }
}
catch {
    Write-Host ""
    Write-Host "[WARNING] EXE build failed: $_" -ForegroundColor Yellow
    Write-Host "The backend is installed. Use START_SERVER.bat as a fallback." -ForegroundColor Yellow
}
