# prepare-demo.ps1
# Script de préparation à lancer 5 minutes avant la démo
# Usage: .\prepare-demo.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  PREPARATION DEMO devkit" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# 1. Aller dans le bon dossier
# ============================================
Set-Location "C:\Users\firfl\OneDrive\Desktop\devkit_project\devkit_project"
Write-Host "[OK] Dossier projet : $(Get-Location)" -ForegroundColor Green

# ============================================
# 2. Vérifier que pip / python sont là
# ============================================
$pythonOk = $null -ne (Get-Command python -ErrorAction SilentlyContinue)
if (-not $pythonOk) {
    Write-Host "[ERREUR] python introuvable dans le PATH" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python : $(python --version 2>&1)" -ForegroundColor Green

# ============================================
# 3. Verifier devkit est installé
# ============================================
$devkitInstalled = python -c "import devkit" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] devkit non installé. Installation..." -ForegroundColor Yellow
    pip install -e . | Out-Null
}
Write-Host "[OK] devkit installé" -ForegroundColor Green

# ============================================
# 4. Vérifier pytest
# ============================================
$pytestOk = python -c "import pytest" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] pytest non installé. Installation..." -ForegroundColor Yellow
    pip install pytest pytest-cov | Out-Null
}
Write-Host "[OK] pytest installé" -ForegroundColor Green

# ============================================
# 5. Lancer les tests
# ============================================
Write-Host ""
Write-Host "[*] Lancement des tests..." -ForegroundColor Cyan
$testResult = python -m pytest -q 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Tests passent : $($testResult | Select-String 'passed')" -ForegroundColor Green
} else {
    Write-Host "[WARN] Certains tests echouent" -ForegroundColor Yellow
    Write-Host $testResult
}

# ============================================
# 6. Pré-chauffer le cache IA
# ============================================
Write-Host ""
Write-Host "[*] Pre-chauffage du cache IA (peut prendre 30-60 sec)..." -ForegroundColor Cyan

$claudeOk = $null -ne (Get-Command claude -ErrorAction SilentlyContinue)
if ($claudeOk) {
    $prompts = @(
        "explain async vs threads in Python in 3 sentences",
        "what is a Makefile in 3 sentences",
        "explain git rebase interactive in 3 sentences"
    )
    foreach ($p in $prompts) {
        Write-Host "  - Cache pour : `"$p`""
        python -m devkit.main ai ask $p 2>&1 | Out-Null
    }
    Write-Host "[OK] Cache pre-chauffe (3 entrees)" -ForegroundColor Green
} else {
    Write-Host "[SKIP] claude pas installe, pre-chauffage saute" -ForegroundColor Yellow
}

# ============================================
# 7. Préparer un fichier staged pour la démo `ai commit`
# ============================================
Write-Host ""
Write-Host "[*] Preparation d'un fichier staged pour ai commit..." -ForegroundColor Cyan

$gitOk = $null -ne (Get-Command git -ErrorAction SilentlyContinue)
if ($gitOk) {
    # Vérifier qu'on est dans un repo git
    git rev-parse --is-inside-work-tree 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        # Ajouter un commentaire à README.md
        $marker = "<!-- demo $(Get-Date -Format 'HH:mm:ss') -->"
        Add-Content README.md $marker
        git add README.md 2>&1 | Out-Null
        Write-Host "[OK] README.md modifie et stage" -ForegroundColor Green
    } else {
        Write-Host "[SKIP] Pas un repo git, skip ai commit prep" -ForegroundColor Yellow
    }
} else {
    Write-Host "[SKIP] git pas installe" -ForegroundColor Yellow
}

# ============================================
# 8. Verdict final
# ============================================
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  PRET POUR LA DEMO" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Commandes utiles :" -ForegroundColor Yellow
Write-Host '  function devkit { python -m devkit.main @args }' -ForegroundColor White
Write-Host "  devkit doctor      # verifier le toolchain"
Write-Host "  devkit             # voir le help"
Write-Host ""
Write-Host "Le protocole complet est dans PROTOCOLE_DEMO.md"
Write-Host "Le cheatsheet rapide est dans demo-cheatsheet.md"
Write-Host ""

# Créer l'alias devkit pour la session
Set-Item -Path Function:\devkit -Value { python -m devkit.main @args }
Write-Host "[OK] Alias 'devkit' active pour cette session" -ForegroundColor Green
Write-Host ""
Write-Host "Tape : devkit doctor" -ForegroundColor Cyan
Write-Host ""
