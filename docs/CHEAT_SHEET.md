# 🎯 CHEAT SHEET — Une page, à imprimer ou consulter

## **PITCH (30 sec)**
*"devkit orchestre GitHub CLI, Claude, Gemini, Git via subprocess. Composabilité pure. 4 couches architecture."*

---

## **6 SOUS-COMMANDES**
```
devkit doctor       → Diagnostic toolchain
devkit gh          → GitHub (issues, PRs)
devkit ai          → AI (review, commit, ask)
devkit workflow    → Multi-tools orchestration
devkit config      → ~/.devkit/config.json
devkit cache       → Disque local cache
```

---

## **ARCHITECTURE 4 COUCHES**
```
CLI (Typer root app)
  ↓
Commands (logique métier)
  ↓
Utils (subprocess wrappers)
  ↓
External tools (gh, claude, gemini, git)
```

---

## **TECHNOLOGIES**
- Python 3.10+
- Typer (CLI framework)
- Rich (tables, styling)
- subprocess (external tools)
- pytest (27 tests)
- JSON (config + cache)

---

## **COMMANDES DE DÉMO (15 MIN)**

| Acte | Commande | Timing |
|------|----------|--------|
| 1 | `devkit doctor` | 1:30 |
| 2 | `devkit gh issues --repo cli/cli --limit 5` | 2:30 |
| 2 | `devkit gh pr-summary 8000 --repo cli/cli` | |
| 3 | `devkit ai review 8000 --repo cli/cli` | 3:00 |
| 3 | `devkit ai commit` | |
| 3 | `devkit ai ask "..."` | |
| 4 | `devkit workflow feature-start awesome --repo cli/cli` | 2:00 |
| 4 | `devkit workflow daily-digest --repo cli/cli` | |
| 5 | `devkit config show` | 1:30 |
| 5 | `devkit cache info` | |
| 6 | Open VS Code + `pytest -v` | 4:30 |

---

## **POINTS FORTS**
✅ subprocess vs SDK (zéro dépendance)  
✅ 4 couches architecture (testable)  
✅ Type hints partout  
✅ 27 tests pytest  
✅ Cache IA disque  
✅ Plugins extensibles  
✅ Fallback gracieux  
✅ 100% du brief  

---

## **RÉPONSES RAPIDES**
| Q | R |
|---|---|
| "Pourquoi subprocess?" | "gh authed, zéro SDK, composabilité" |
| "Et si gh manque?" | "doctor le detect, error lisible" |
| "Tests?" | "27 pytest, mocks subprocess" |
| "Cache?" | "Disque local, hash → réponse" |
| "Architecture?" | "4 couches: CLI→Commands→Utils→External" |
| "Windows?" | "Cross-platform, développé sur Windows" |

---

## **AVANT LA DÉMO**
```powershell
devkit doctor          # Doit afficher: git ✓ gh ✓ python ✓ claude ✓
devkit ai ask "test"   # Pré-chauffer cache
git add README.md      # Préparer diff pour ai commit
clear
```

---

## **SI PROBLÈME**
- PR 8000 n'existe? → Cherche autre PR sur github.com/cli/cli/pulls
- gh manque? → Installe via `brew install gh` ou `winget install gh`
- Claude lent? → Normal (10-30 sec), continue explanation pendant ce temps
- Pas [cached]? → OK, réponse s'affiche en direct

---

## **TIMING**
```
0:00-1:30   Intro (doctor)
1:30-4:00   GitHub (issues + pr-summary)
4:00-7:00   AI (review + commit + ask)
7:00-9:00   Workflows (feature-start + daily-digest)
9:00-10:30  Config/Cache
10:30-14:30 Architecture (code + tests)
14:30-15:00 Buffer
```

---

## **À DIRE (mémoriser)**
- "Composabilité — réutiliser plutôt que réinventer"
- "4 couches bien séparées, chacune testable indépendamment"
- "Type hints partout — from __future__ import annotations"
- "27 tests pytest couvrant utils, config, CLI"
- "Cache IA pour accélérer futures runs"
- "Plugins: ~/.devkit/plugins/ extensibilité user"
- "100% du brief couvert"

---

## **À NE PAS DIRE**
❌ "SDK PyGithub" → "gh CLI"  
❌ "Pas de tests" → "27 tests"  
❌ "Non-typé" → "from __future__ import annotations"  
❌ "Custom architecture" → "4 couches patterns reconnus"  
❌ "On stocke les tokens" → "env vars seulement"  

---

## **FICHIERS CLÉS**
- `src/devkit/main.py` → Typer root app
- `src/devkit/commands/` → 6 sub-apps
- `src/devkit/utils/` → Wrappers subprocess
- `tests/` → 27 tests

---

## **DOCUMENTS**
| Document | Quand |
|----------|-------|
| **DEMARRAGE_RAPIDE.md** | Navigation |
| **FICHE_REVISION.md** | Mémorisation |
| **QUICK_REFERENCE.md** | Pendant démo |
| **QA_APPROFONDIE.md** | Questions tech |

---

## **MESSAGE CENTRAL**

> **"devkit orchestre `gh`, Claude, Gemini, Git via subprocess. Aucune réinvention. 4 couches architecture. Type hints. 27 tests. 100% du brief."**

Mémorisez ça → tout le reste suit.

---

## **VOUS ÊTES PRÊT !** 🚀

