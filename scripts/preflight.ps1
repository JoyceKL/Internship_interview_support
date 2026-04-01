$ErrorActionPreference = 'Stop'

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-Error '[FAIL] Docker chưa được cài hoặc không có trong PATH'
}
Write-Host '[OK] Docker command available'

try {
  docker info | Out-Null
  Write-Host '[OK] Docker daemon is running'
} catch {
  Write-Error '[FAIL] Docker daemon chưa chạy'
}

if (-not (Test-Path .env)) {
  Write-Error '[FAIL] Thiếu file .env (hãy copy từ .env.example)'
}
Write-Host '[OK] .env exists'

$required = @('SECRET_KEY','DATABASE_URL','OPENAI_MODEL','CV_UPLOAD_DIR','JD_UPLOAD_DIR','EXPORTS_DIR')
$envContent = Get-Content .env -Raw
foreach ($key in $required) {
  if ($envContent -notmatch "(?m)^$key=") {
    Write-Error "[FAIL] Thiếu biến $key trong .env"
  }
}
Write-Host '[OK] Required env keys exist'

New-Item -ItemType Directory -Force data/uploads/cv | Out-Null
New-Item -ItemType Directory -Force data/uploads/jd | Out-Null
New-Item -ItemType Directory -Force data/exports | Out-Null
Write-Host '[OK] data directories ready'

try {
  $dbUp = docker compose ps db 2>$null
  if ($dbUp -match 'Up') {
    Write-Host '[OK] DB container is up'
  } else {
    Write-Host '[WARN] DB container chưa chạy (hãy chạy: docker compose up -d)'
  }
} catch {
  Write-Host '[WARN] Chưa kiểm tra được trạng thái docker compose db'
}
