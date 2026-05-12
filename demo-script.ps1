# demo-script.ps1
# Script de démo interactif : appuie sur Entrée entre chaque étape
# Usage: .\demo-script.ps1

Set-Location "C:\Users\firfl\OneDrive\Desktop\devkit_project\devkit_project"
Set-Item -Path Function:\devkit -Value { python -m devkit.main @args }

function Step {
    param([string]$Title, [string]$Cmd, [string]$Comment = "")
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Yellow
    Write-Host "============================================" -ForegroundColor Cyan
    if ($Comment) {
        Write-Host ""
        Write-Host "  $Comment" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "  >> $Cmd" -ForegroundColor White
    Write-Host ""
    Read-Host "  [Entree pour executer]"
    Invoke-Expression $Cmd
    Write-Host ""
    Read-Host "  [Entree pour passer a la suite]"
}

Clear-Host
Write-Host ""
Write-Host "    ____  ___ _ __   ___   " -ForegroundColor Cyan
Write-Host "   /  _ \/ -_) ' _\ / -_)  " -ForegroundColor Cyan
Write-Host "  /__,_/\__/_/\_\/\__/_   " -ForegroundColor Cyan
Write-Host "                            " -ForegroundColor Cyan
Write-Host "  DEMO devkit (15 min)" -ForegroundColor Yellow
Write-Host ""
Read-Host "  Appuie Entree pour commencer"

# ============================================
# ACTE 1 — Doctor
# ============================================
Step "ACTE 1 - Introduction" "devkit" "Le panneau de bienvenue et la liste des sous-groupes"
Step "ACTE 1 - Doctor" "devkit doctor" "Diagnostic complet : git, gh, python, claude tous OK"

# ============================================
# ACTE 2 — GitHub
# ============================================
Step "ACTE 2 - Listing issues" "devkit gh issues --repo cli/cli --limit 5" "gh issue list --json + table Rich"
Step "ACTE 2 - PR summary" "devkit gh pr-summary 8000 --repo cli/cli" "Panneau + 2 tables agreges en une commande"
Step "ACTE 2 - CI status" "devkit gh run-status --repo cli/cli --limit 5" "Derniers runs CI colores vert/rouge"
Step "ACTE 2 - Search (bonus)" "devkit gh search 'is:open label:bug' --kind issues --limit 3" "Bonus : wrapper sur gh search"

# ============================================
# ACTE 3 — Les 3 IAs
# ============================================
Step "ACTE 3 - Copilot explain" "devkit ai explain 'git rebase -i HEAD~3'" "GitHub Copilot - specialise commandes shell"
Step "ACTE 3 - Copilot suggest" "devkit ai suggest 'list all docker containers sorted by memory'" "Langage naturel -> commande shell"
Step "ACTE 3 - Claude (cache)" "devkit ai ask 'explain async vs threads in Python'" "Reponse instantanee si pre-chauffe (cached)"
Step "ACTE 3 - Gemini fallback" "devkit ai ask 'what is a Makefile' --model gemini" "Gemini absent -> fallback automatique vers Claude"

Write-Host ""
Write-Host "  [INFO] Pour ai commit, assure-toi qu'un fichier est staged (git diff --staged)" -ForegroundColor Yellow
Read-Host "  [Entree pour continuer]"

# ============================================
# ACTE 4 — Workflow
# ============================================
Step "ACTE 4 - Daily digest" "devkit workflow daily-digest" "3 tables matinales en une commande (bonus)"

Write-Host ""
Write-Host "  [INFO] feature-start cree une vraie branche. Skip si on n'est pas sur un repo de demo." -ForegroundColor Yellow
Write-Host "  [INFO] Mention orale de workflow ship (sans le lancer pour ne pas creer de PR)"
Read-Host "  [Entree pour continuer]"

# ============================================
# ACTE 5 — Config & Cache
# ============================================
Step "ACTE 5 - Config show" "devkit config show" "~/.devkit/config.json, 4 cles, format JSON"
Step "ACTE 5 - Cache info" "devkit cache info" "Cache rempli pendant la demo"

# ============================================
# ACTE 6 — Tests
# ============================================
Step "ACTE 6 - Tests" "pytest -v" "49 tests, < 1 seconde, mocks subprocess"

# ============================================
# ACTE 7 — Code
# ============================================
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ACTE 7 - Code walkthrough" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Ouvrir dans VS Code :"
Write-Host "  1. src\devkit\utils\ai_runner.py (lignes 62-77, les 3 IAs)"
Write-Host "  2. src\devkit\utils\shell.py (frontiere subprocess)"
Write-Host "  3. ARCHITECTURE.md (diagramme en couches)"
Write-Host ""
Read-Host "  [Entree pour ouvrir ai_runner.py]"
code "src\devkit\utils\ai_runner.py"

Read-Host "  [Entree pour ouvrir shell.py]"
code "src\devkit\utils\shell.py"

Read-Host "  [Entree pour ouvrir ARCHITECTURE.md]"
code "ARCHITECTURE.md"

# ============================================
# Cloture
# ============================================
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  DEMO TERMINEE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Pitch de cloture :"
Write-Host ""
Write-Host '  "2347 lignes de Python, 18 modules, 27 commandes,' -ForegroundColor Cyan
Write-Host '   49 tests qui tournent en <1 seconde, deux dependances' -ForegroundColor Cyan
Write-Host '   directes seulement. Pas une reimplementation de Git' -ForegroundColor Cyan
Write-Host '   ou de GitHub, mais un coordinateur qui les fait' -ForegroundColor Cyan
Write-Host '   travailler ensemble. C est exactement l instinct' -ForegroundColor Cyan
Write-Host '   de composabilite demande par le brief."' -ForegroundColor Cyan
Write-Host ""
Write-Host "  Bonne chance pour les 10 min de Q&A !" -ForegroundColor Yellow
Write-Host ""
