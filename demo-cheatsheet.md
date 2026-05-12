# 📋 Demo Cheatsheet — devkit (à imprimer / garder à côté)

## Setup express (à taper en début de session)

```powershell
cd C:\Users\firfl\OneDrive\Desktop\devkit_project\devkit_project
.\prepare-demo.ps1
function devkit { python -m devkit.main @args }
clear
```

---

## 🎬 ACTE 1 — Doctor (1:30)
```powershell
devkit
devkit doctor
```

## 🎬 ACTE 2 — GitHub (2:30)
```powershell
devkit gh issues --repo cli/cli --limit 5
devkit gh pr-summary 8000 --repo cli/cli
devkit gh run-status --repo cli/cli --limit 5
devkit gh search "is:open label:bug" --kind issues --limit 3
```

## 🎬 ACTE 3 — 3 IAs (3:00)
```powershell
devkit ai explain "git rebase -i HEAD~3"
devkit ai suggest "list all docker containers sorted by memory"
devkit ai ask "explain async vs threads in Python"
devkit ai ask "what is a Makefile" --model gemini
devkit ai commit
```

## 🎬 ACTE 4 — Workflow (2:30)
```powershell
devkit workflow daily-digest
devkit workflow feature-start ma-fonctionnalite --issue 1
# (mentionner workflow ship sans le lancer)
```

## 🎬 ACTE 5 — Config & Cache (1:00)
```powershell
devkit config show
devkit config set ai_tool gemini
devkit config show
devkit config reset --yes
devkit cache info
```

## 🎬 ACTE 6 — Tests (1:00)
```powershell
pytest -v
pytest --cov=devkit --cov-report=term
```

## 🎬 ACTE 7 — Code (2:00)
```powershell
code src\devkit\utils\ai_runner.py
code src\devkit\utils\shell.py
code ARCHITECTURE.md
```

---

## 🚨 Recovery rapide

| Problème | Solution |
|---|---|
| `gh` plante | `devkit doctor` → "le doctor détecte le problème" |
| IA plante | `--model gemini` qui forcera fallback → claude |
| Commande lente | Ctrl+C, passer à la suivante |
| Terminal mort | Nouvelle fenêtre + `function devkit {...}` |

---

## 💬 Pitch d'ouverture (par cœur)

> *"devkit est un méta-outil CLI en Python qui orchestre GitHub CLI, Claude Code, Gemini, GitHub Copilot, Git et fzf derrière une seule commande. Le projet répond au brief Modern CLI, dont l'objectif central est 'developing the instinct for composability' — l'instinct de composabilité."*

## 💬 Pitch de clôture (par cœur)

> *"2347 lignes de Python, 18 modules, 27 commandes, 49 tests qui tournent en <1 seconde, deux dépendances directes. Pas une réimplémentation de Git ou de GitHub, mais un coordinateur qui les fait travailler ensemble. C'est exactement l'instinct de composabilité demandé par le brief."*

---

## 📊 Validation grille (à mentionner)

| Critère | Pts | Acte |
|---|---|---|
| Tool integration | 20 | 2-4 |
| Workflow command | 20 | 4 |
| Code quality | 10 | 7 |
| Error handling | 15 | 1, 3 |
| UX & rich output | 10 | 1-3 |
| README & demo | 25 | 7 |
| **TOTAL** | **100** | |

---

## 🎤 Top 3 questions Q&A

**Q : Pourquoi subprocess et pas SDK ?**
R : Auth gh réutilisée, zéro dépendance lourde, suit l'écosystème.

**Q : 4ème IA ?**
R : 5 lignes dans `ai_runner.py`, c'est tout.

**Q : Pas de tests e2e ?**
R : Credentials + facturation IA + lenteur. Mocks à la frontière subprocess.
