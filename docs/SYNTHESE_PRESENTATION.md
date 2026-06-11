# 📋 SYNTHÈSE DE PRÉSENTATION — devkit
## Démo 15 min + Q&A 10 min

---

## 🎯 LE PITCH EN 30 SECONDES

> *"Bonjour. Je vais vous présenter **devkit**, un méta-outil CLI écrit en Python qui orchestre les outils modernes du développeur (GitHub CLI, Claude, Gemini, Git, GitHub Copilot) derrière une seule interface unifiée. L'objectif central : **développer l'instinct de composabilité** — réutiliser ce qui existe déjà plutôt que de réinventer la roue."*

---

## 🏗️ ARCHITECTURE — LES 4 POINTS CLÉS

### 1️⃣ Architecture en 3 couches + configuration
```
       CLI (Typer)
            ↓
    Commands (logique métier)
            ↓
    Utils (wrappers subprocess)
            ↓
    Outils externes (gh, claude, gemini, git, fzf)
```

| Couche | Fichiers | Rôle |
|--------|----------|------|
| **CLI** | `main.py` | Point d'entrée Typer ; assemble les 6 sous-commandes. |
| **Commands** | `commands/*.py` | Logique métier : `github.py`, `ai.py`, `workflow.py`, `config_cmd.py`, `cache_cmd.py`, `doctor.py` |
| **Utils** | `utils/*.py` | Wrappers `subprocess` : `gh.py`, `ai_runner.py`, `cache.py`, `shell.py`, `check.py`, `display.py` |
| **Config** | `config.py`, `plugins.py` | Persistance JSON + découverte de plugins |

**Règle critique :** une couche ne dépend QUE des couches inférieures. Aucun `utils/*.py` n'importe `commands/*.py`. → **Testable sans Typer.**

### 2️⃣ Les 6 sous-commandes principales
```
devkit
  ├── doctor          # Diagnostic du toolchain
  ├── gh              # GitHub CLI (issues, PRs, workflows)
  ├── ai              # AI tools (explain, review, commit, etc.)
  ├── workflow        # Orchestration multi-outils
  ├── config          # Gestion ~/.devkit/config.json
  └── cache           # Cache IA (disk + fallback)
```

### 3️⃣ Technologies & pourquoi

| Tech | Où | Pourquoi |
|------|-----|---------|
| **Python 3.10+** | Tout | Langage principal |
| **Typer** | `main.py`, `commands/` | Framework CLI avec type hints natifs ; génère `--help` en Rich |
| **Rich** | `utils/display.py` | Rendus tables/panneaux ; `--help` colorisé |
| **subprocess** | `utils/shell.py`, `utils/gh.py`, `utils/ai_runner.py` | Réutilise les CLI externes (gh, claude, gemini, git) |
| **JSON** | `config.py`, retours de `gh --json` | Persistance config + parsing données GitHub |
| **pytest** | `tests/` | 27 tests pour utils, config, CLI (smoke tests) |
| **setuptools** | `pyproject.toml` | Build ; crée le script `devkit` |

### 4️⃣ Choix architectural #1 : subprocess vs SDK Python

❌ **PAS** de `PyGithub`, `anthropic`, `google-generativeai` (les SDK Python officiels)

✅ **OUI** : `subprocess` pour appeler `gh`, `claude`, `gemini`, `git`

**Pourquoi :** 
- `gh` est déjà authentifié sur la machine → zéro gestion de tokens
- Aucune dépendance lourde → `pip install devkit` installe juste `typer` et `rich`
- Suit l'écosystème → quand GitHub ajoute une commande, devkit en bénéficie immédiatement
- **Composabilité** : on réutilise des outils battlefield-tested au lieu de réinventer

---

## 📂 OÙ TROUVER QUOI

### Structure des fichiers
```
src/devkit/
├── main.py                    ← Point d'entrée CLI (Typer root app)
├── config.py                  ← ~/.devkit/config.json (ai_tool, default_repo)
├── plugins.py                 ← Auto-discovery ~/.devkit/plugins/
├── commands/
│   ├── github.py              ← devkit gh (issues, pr-summary, etc.)
│   ├── ai.py                  ← devkit ai (review, commit, explain, etc.)
│   ├── workflow.py            ← devkit workflow (feature-start, daily-digest)
│   ├── config_cmd.py          ← devkit config (show, set, reset, path)
│   ├── cache_cmd.py           ← devkit cache (info, clear)
│   ├── doctor.py              ← devkit doctor (diagnostic)
│   └── __init__.py
└── utils/
    ├── shell.py               ← subprocess.run() wrapper + error handling
    ├── gh.py                  ← Wrappers pour `gh issue list`, `gh pr view`, etc.
    ├── ai_runner.py           ← Appelle claude/gemini ; gère fallback
    ├── cache.py               ← Disque (~/.devkit/cache/) + cache_key
    ├── check.py               ← Teste la présence des outils (git, gh, python, claude)
    ├── display.py             ← console Rich, helpers de rendu
    └── __init__.py
```

### Où trouver un concept clé ?

| Concept | Fichier | Détail |
|---------|---------|--------|
| **Typer setup** | `main.py` L10-24 | `app.add_typer(...)` pour assembler les sous-commandes |
| **Une commande exemple** | `commands/github.py` | Fonction Typer + docstring = CLI auto-générée |
| **Appeler un outil externe** | `utils/shell.py` | `subprocess.run()` + error handling |
| **Récupérer une issue GitHub** | `utils/gh.py` | `gh issue list --json` + `json.loads()` + table Rich |
| **Config utilisateur** | `config.py` | `~/.devkit/config.json` ; défauts si fichier absent |
| **Cache IA** | `utils/cache.py` | Disque `~/.devkit/cache/` ; fallback si manquant |
| **Détection outils** | `utils/check.py` | `which git`, `gh version`, etc. |
| **Plugins user** | `plugins.py` | Importe `~/.devkit/plugins/*.py` automatiquement |

---

## 🎬 SCRIPT DE DÉMO — 15 MIN CHRONO

### Acte 1 : Intro + Doctor (2 min)
```bash
devkit
# 👉 Montre: liste des 6 sous-commandes + description

devkit doctor
# 👉 Montre: git ✓, gh ✓, python ✓, claude ✓
# À dire: "C'est mon diagnostic du toolchain. 
#          devkit sait orchestrer ces outils, je peux donc continuer."
```

### Acte 2 : GitHub (3 min)
```bash
devkit gh issues --repo cli/cli --limit 5
# 👉 Table Rich: numéro | titre | state | labels | assignee
# À dire: "Première commande: liste des 5 dernières issues du repo cli/cli.
#          Sous le capot: `gh issue list --json`, parsing, Rich table."

devkit gh pr-summary 8000 --repo cli/cli
# 👉 Panneau PR + table fichiers + table reviews
# À dire: "Deuxième commande: détail d'une PR. On voit titre, body, fichiers modifiés, reviews."
```

### Acte 3 : AI (3 min)
```bash
devkit ai review 8000 --repo cli/cli
# 👉 Exécute `claude` ; affiche avis humain sur la PR
# À dire: "Troisième acte: AI review. Claude lit la PR et génère un avis technique.
#          Le code reuse le cache si même PR."

devkit ai commit
# 👉 Suppose `git add` + diff staged → Claude génère message conventionnel
# À dire: "Quatrième: génère un message de commit semantic (feat: add X, fix: Y)."

devkit ai ask "what is the GitHub CLI in 3 sentences"
# 👉 Affiche réponse Claude (potentiellement (cached) si pré-chauffée)
# À dire: "Cinquième: Q&A one-shot. La réponse est en cache → instantané."
```

### Acte 4 : Workflows (2 min)
```bash
devkit workflow feature-start awesome-feature --repo cli/cli
# 👉 Crée branche, pousse, ouvre PR draft, demande à Claude : "plan for this feature"
# À dire: "Workflow complet: crée branche + PR + plan IA en une commande."

devkit workflow daily-digest --repo cli/cli
# 👉 Affiche PRs assignées à moi (reader) + issues + CI status en dashboard
# À dire: "Dashboard quotidien: ce qui vous attend le matin."
```

### Acte 5 : Config + Cache (2 min)
```bash
devkit config show
# 👉 Affiche ~/.devkit/config.json : ai_tool=claude, default_repo=...

devkit config set ai_tool gemini
# 👉 Modifie le JSON

devkit cache info
# 👉 Combien de réponses en cache ? Taille disque ?

devkit cache clear
# 👉 Vide le cache
```

### Acte 6 : Architecture code (3 min)
```bash
# Ouvre VS Code, montre la structure:
# 
# src/devkit/main.py
#   ↳ Typer app avec 6 sous-commandes
# 
# src/devkit/commands/github.py
#   ↳ Fonction @app.command() par commande
# 
# src/devkit/utils/shell.py
#   ↳ Wrapper subprocess + error handling
# 
# src/devkit/utils/gh.py
#   ↳ `subprocess.run(['gh', 'issue', 'list', '--json', ...])`
#   ↳ `json.loads()` → parser → Rich table

# À dire: "Architecture : commandes → utils → subprocess.
#         Chaque couche isolée, testable."
```

---

## ❓ RÉPONSES ANTICIPÉES — Q&A 10 MIN

### Q: "Pourquoi pas utiliser directement PyGithub ou anthropic ?"
**R:** *"Trois raisons : (1) `gh` est déjà authentifié sur ma machine — zéro gestion de tokens, (2) Zéro dépendances lourdes — `pip install devkit` installe juste Typer et Rich, (3) Composabilité — quand GitHub ajoute une commande, devkit en bénéficie sans code change. C'est la philosophie du brief."*

### Q: "Et si `gh` ou `claude` n'est pas installé ?"
**R:** *"`devkit doctor` le detect et vous propose une installation. Si une commande le demande et l'outil manque, on retourne une erreur lisible. Exemple: si Gemini manque mais que Claude marche, on bascule à Claude (fallback)."*

### Q: "Vous testez comment les appels subprocess ?"
**R:** *"Mocks pytest : je mock `subprocess.run()` en `tests/test_shell.py`, je simule des réponses `gh`. Pas de vraies API calls pendant les tests."*

### Q: "Comment votre cache fonctionne ?"
**R:** *"Hash de la question → disque `~/.devkit/cache/`. Si même question, on réutilise. Si le fichier est corrompu ou absent, fallback API directe. C'est un cache best-effort."*

### Q: "Et les plugins utilisateur ?"
**R:** *"Fichiers `.py` dans `~/.devkit/plugins/`. Importés auto au startup. Chacun peut ajouter ses propres commandes — l'extensibilité."*

### Q: "Quel IDE utilisé pour coder ?"
**R:** *"VS Code. L'extension Pylance pour type-checking. pytest pour tester."*

### Q: "Dépendances runtime ?"
**R:** *"Juste `typer` et `rich` (déclarées dans `pyproject.toml`). Pas de `PyGithub`, pas de `anthropic`."*

### Q: "Pourquoi Typer plutôt que argparse ?"
**R:** *"Typer = Click + type hints natifs. Commande = fonction typée. Elle génère auto `--help`, validation, completion. C'est plus Pythonique."*

### Q: "Et pour le déploiement en production ?"
**R:** *"Pas de serveur — c'est un CLI. `pip install devkit` chez chaque dev, c'est tout. Pas de frais infrastructure."*

### Q: "Comment vous appelez les IA ?"
**R:** *"subprocess : `claude` ou `gemini` (les CLIs officielles). Chacune peut récupérer sa propre config (tokens). On passe le texte en stdin, on récupère la réponse en stdout."*

### Q: "Combien de tests ?"
**R:** *"27 tests pytest. Couvrent utils, config round-trip, CLI smoke tests. Lancem avec `pytest`."*

---

## 📊 COUVERTURE DU BRIEF

Le projet répond à la grille de notation suivante :

| Phase | Critère | Implémenté |
|-------|---------|-----------|
| **1. Discovery** | Analyser 10 CLI modernes | ✅ ARCHITECTURE.md |
| **2. Commands + JSON** | 6 commands × `gh --json` + Rich | ✅ `gh issues`, `pr-summary`, etc. |
| **3. IA Integration** | ≥3 IA backends (Claude, Gemini, Copilot) | ✅ `ai review`, `ai commit`, etc. |
| **4. Workflows** | ≥1 workflow multi-outils orchestré | ✅ `workflow feature-start`, `daily-digest` |
| **5. Error Handling** | `devkit doctor` + graceful fallback | ✅ `require_tools()` + fallback Gemini→Claude |
| **6. Code Quality** | Type hints + tests + structure | ✅ 27 tests, type hints partout, 4 couches |
| **7. Documentation** | README + ARCHITECTURE + inline | ✅ README.md, ARCHITECTURE.md, PROTOCOLE_DEMO.md |
| **8. Composability** | Chaque outil réutilisé vs réinventé | ✅ subprocess + `gh --json` + plugins |

---

## 🔧 COMMANDES UTILES PENDANT PRÉP

```bash
# Installer devkit en mode dev
pip install -e .

# Vérifier l'install
devkit doctor

# Lancer les tests
pytest -v

# Vérifier la couverture
pytest --cov=devkit

# Faire une démo locale (sans repo distant)
devkit ai ask "What is Python?"

# Pré-chauffer le cache (à faire avant démo)
devkit ai ask "explain async vs threads in Python"
devkit ai ask "what is a Makefile in 3 sentences"

# Préparer un diff pour `ai commit`
echo "# demo $(date)" >> README.md
git add README.md
devkit ai commit
```

---

## 💡 POINTS FORTS À SOULIGNER

1. **Composabilité** : `subprocess` → réutilise `gh`, `claude`, `gemini`, `git`. Pas de SDK.
2. **Architecture claire** : 4 couches bien séparées, chacune testable indépendamment.
3. **Type hints** : Python 3.10+ `from __future__ import annotations` partout.
4. **Erreur handling** : `devkit doctor` + fallback gracieux (Gemini manque → Claude).
5. **Configuration** : `~/.devkit/config.json` persistant + defaults.
6. **Cache** : Réponses IA en disque, accélère future runs.
7. **Plugins** : `~/.devkit/plugins/` auto-montées, extensibilité.
8. **Tests** : 27 tests pytest couvrant utils, config, CLI.

---

## 🎓 TERMINOLOGIE CLÉS

- **Typer** : Framework CLI Python avec type hints natifs
- **Rich** : Rendering tables, panels, couleurs terminal
- **subprocess** : Lancer des outils externes (gh, claude, git)
- **JSON** : Format données (GitHub API, config, cache)
- **Plugins** : Code utilisateur importé auto (~/.devkit/plugins/)
- **Cache** : Réponses IA sauvegardées disque pour réutilisation
- **Fallback** : Gemini manque → utiliser Claude à la place
- **Composabilité** : Réutiliser outils existants vs les réinventer

