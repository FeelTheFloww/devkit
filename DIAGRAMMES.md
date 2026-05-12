# 📊 DIAGRAMMES — Architecture visuelle

## 1. Architecture 4 couches

```
┌─────────────────────────────────────────────────┐
│         CLI ENTRY (main.py)                     │
│  devkit doctor | gh | ai | workflow | config   │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│      COMMANDS (logique métier)                  │
│  commands/github.py                             │
│  commands/ai.py                                 │
│  commands/workflow.py                           │
│  commands/config_cmd.py                         │
│  commands/cache_cmd.py                          │
│  commands/doctor.py                             │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│      UTILS (wrappers + helpers)                 │
│  utils/shell.py        ← subprocess runner     │
│  utils/gh.py           ← gh CLI wrapper        │
│  utils/ai_runner.py    ← Claude/Gemini runner  │
│  utils/cache.py        ← Disque local          │
│  utils/check.py        ← Détection outils      │
│  utils/display.py      ← Rich rendering        │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│    OUTILS EXTERNES (subprocess calls)           │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐       │
│  │  gh  │  │ git  │  │claude│  │gemini│       │
│  └──────┘  └──────┘  └──────┘  └──────┘       │
│         (processus externes)                    │
└─────────────────────────────────────────────────┘
```

---

## 2. Flow d'une commande (exemple: `devkit gh issues`)

```
$ devkit gh issues --repo cli/cli --limit 5
          │
          ▼
    main.py (Typer)
          │
          ▼
    commands/github.py (fonction @app.command())
          │
          ▼
    utils/gh.py.issues()
          │
          ▼
    utils/shell.py.run_command(['gh', 'issue', 'list', '--json', ...])
          │
          ▼
    subprocess.run(...)  ← lance `gh` processus
          │
          ▼
    gh stdout: '[{"number": 1, "title": "Bug"}, ...]'
          │
          ▼
    json.loads()  ← parse JSON
          │
          ▼
    utils/display.py.render_table()  ← Rich table
          │
          ▼
    affichage: [numéro | titre | state | labels | assignee]
```

---

## 3. Flow AI + Cache (exemple: `devkit ai ask`)

```
$ devkit ai ask "explain async"
          │
          ▼
    main.py → commands/ai.py → ask()
          │
          ▼
    utils/ai_runner.py.ask_claude(prompt)
          │
          ▼
    utils/cache.py.get_cached(hash(prompt))
          │
     ┌────┴───────┐
     │             │
  EN CACHE      PAS EN CACHE
     │             │
     ▼             ▼
 retourne   subprocess.run(['claude', ...])
   réponse         │
                   ▼
              cache.set(hash(prompt), réponse)
                   │
                   ▼
              retourne réponse
     │             │
     └─────┬───────┘
           │
           ▼
    utils/display.py.print_response()
           │
           ▼
    affichage: réponse (+ "[cached]" si EN CACHE)
```

---

## 4. Workflow: `devkit workflow feature-start`

```
$ devkit workflow feature-start awesome-feature --repo cli/cli
          │
          ▼
    commands/workflow.py.feature_start()
          │
          ├─→ ÉTAPE 1: git checkout -b feature-awesome-feature
          │           (subprocess.run(['git', 'checkout', ...]))
          │
          ├─→ ÉTAPE 2: git push -u origin
          │           (subprocess.run(['git', 'push', ...]))
          │
          ├─→ ÉTAPE 3: gh pr create --draft
          │           (via utils/gh.py)
          │
          ├─→ ÉTAPE 4: Claude génère plan
          │           (via utils/ai_runner.py)
          │
          └─→ RÉSULTAT: Branche créée, PR ouverte, plan affiché
```

---

## 5. Orchestration d'outils (composabilité)

```
DEVKIT réutilise:

┌─────────┐
│  git    │ ← Versionning
└────┬────┘
     │
┌────▼───────────────────────────────┐
│  DEVKIT (orchestrateur)            │
│  ┌────────────────────────────┐   │
│  │ Typer CLI                  │   │
│  │ Commands (logique métier)  │   │
│  │ Utils (wrappers)           │   │
│  └────────────────────────────┘   │
└────┬──────────┬────────┬──────────┘
     │          │        │
┌────▼───┐  ┌───▼────┐ ┌─▼──────────┐
│   gh   │  │ Claude │ │  Gemini    │
│ GitHub │  │   AI   │ │    AI      │
└────────┘  └────────┘ └────────────┘

CHAQUE OUTIL = spécialiste dans son domaine
DEVKIT = orchestrateur qui les fait travailler ensemble
```

---

## 6. Arborescence fichiers (clé)

```
src/devkit/
├── main.py
│   └─ Typer root app
│      └─ app.add_typer(github.app, name='gh')
│      └─ app.add_typer(ai.app, name='ai')
│      └─ app.add_typer(workflow.app, name='workflow')
│      └─ app.add_typer(config_cmd.app, name='config')
│      └─ app.add_typer(cache_cmd.app, name='cache')
│      └─ app.command('doctor')(doctor.doctor)
│
├── commands/
│   ├── github.py      ← devkit gh *
│   ├── ai.py          ← devkit ai *
│   ├── workflow.py    ← devkit workflow *
│   ├── config_cmd.py  ← devkit config *
│   ├── cache_cmd.py   ← devkit cache *
│   └── doctor.py      ← devkit doctor
│
├── utils/
│   ├── shell.py       ← subprocess.run() wrapper
│   ├── gh.py          ← Wrappers `gh` CLI
│   ├── ai_runner.py   ← Wrappers `claude`/`gemini`
│   ├── cache.py       ← Disque local
│   ├── check.py       ← Détecte outils
│   └── display.py     ← Rich tables/panels
│
├── config.py          ← ~/.devkit/config.json
└── plugins.py         ← ~/.devkit/plugins/ discovery
```

---

## 7. Flux de dépendances (direction)

```
CLI ──► Commands ──► Utils ──► External tools
 ↓        │          │
 │        └─────────►│
 │                   │
 └──────────────────►│

Règle: chaque couche dépend des couches INFÉRIEURES
        jamais des couches SUPÉRIEURES

✅ Commands importe Utils     ← OK
❌ Utils importe Commands     ← INTERDIT
✅ Utils importe subprocess   ← OK
❌ subprocess importe Utils   ← N/A (externe)
```

---

## 8. Cycle de vie d'une requête IA (détaillé)

```
1. USER: "devkit ai ask 'what is async'"
          │
2.        ▼
          parse args (question="what is async")
          │
3.        ▼
          compute cache_key = SHA256(question)
          │
4.        ▼
          check ~/.devkit/cache/{cache_key}.json
          │
          ┌──────────────────┬──────────────────┐
          │                  │                  │
5a. EXISTS         5b. NOT EXISTS      5c. CORRUPT
    │                  │                  │
    ▼                  ▼                  ▼
  load JSON      subprocess(['claude'])  logging error
    │                  │                  │
    ▼                  ▼                  ▼
  cache_hit        run Claude          fallback to
  [cached]         get response        subprocess call
    │                  │                  │
    └──────┬───────────┤──────────────────┘
           │           │
6.         ▼           ▼
           save to ~/.devkit/cache/{cache_key}.json
           │
7.         ▼
           return response
           │
8.         ▼
           display via Rich
           │
9.         ▼
           user sees answer (+ "[cached]" si cas 5a)
```

---

## 9. Technologies utilisées (stacke)

```
┌─────────────────────────────────────┐
│  PYTHON 3.10+                       │
│  (Langage principal)                │
├─────────────────────────────────────┤
│  TYPER                              │
│  (Framework CLI, type hints)        │
├─────────────────────────────────────┤
│  RICH                               │
│  (Tables, panels, styling)          │
├─────────────────────────────────────┤
│  subprocess                         │
│  (Lancer gh, claude, git, etc)     │
├─────────────────────────────────────┤
│  JSON                               │
│  (Config + cache)                   │
├─────────────────────────────────────┤
│  pathlib                            │
│  (Cross-platform file paths)        │
├─────────────────────────────────────┤
│  pytest                             │
│  (Tests unitaires, 27 tests)        │
└─────────────────────────────────────┘
```

---

## 10. Démo timing (15 min)

```
0:00 ──────────────────────────────────────────────── 15:00
│                                                       │
│ 0:00        1:30        3:00        6:00       9:30  │ 14:00 15:00
│  ├─ INTRO ─┤ GITHUB ───┤ AI ───────┤ WORKFLOW  ─────┤ BUFFER
│  │  doctor │ issues    │ review    │ feature-start │
│  │         │ pr-summary│ commit    │ daily-digest  │
│  │         │           │ ask       │               │
│  │         │           │           │               │
│  └─────────┴───────────┴───────────┴───────────────┘

ACTE 1: Introduction (1:30)
  - Pitch du projet
  - `devkit` → liste commandes
  - `devkit doctor` → diagnostic

ACTE 2: GitHub (2:30)
  - `devkit gh issues`
  - `devkit gh pr-summary`

ACTE 3: AI (3:00)
  - `devkit ai review`
  - `devkit ai commit`
  - `devkit ai ask` (cached)

ACTE 4: Workflows (3:00)
  - `devkit workflow feature-start`
  - `devkit workflow daily-digest`

ACTE 5: Config + Cache (1:30)
  - `devkit config show/set`
  - `devkit cache info/clear`

ACTE 6: Architecture (4:30)
  - Code tour (VS Code)
  - `pytest -v`
```

---

## 11. Quoi faire si ... (troubleshooting)

```
Si gh n'existe pas
  └─→ devkit doctor affiche ROUGE
      └─→ utilisateur installe via `brew install gh` ou `winget install gh`

Si claude n'existe pas
  └─→ devkit doctor affiche ROUGE
      └─→ fallback à gemini (si installé)
      └─→ sinon: error lisible

Si cache corrompu
  └─→ JSON parse fail
      └─→ logging.warning
      └─→ fallback subprocess call
      └─→ regenerate cache

Si PR number invalide (cli/cli)
  └─→ `gh pr view` retourne error
      └─→ catch CalledProcessError
      └─→ print error lisible
      └─→ exit(1)
```

---

## 12. Concepts clés: "Composabilité"

```
MAUVAISE APPROCHE (réinvention):
┌──────────────────────┐
│ devkit (tout dedans) │
│ ├─ GitHub API client │
│ ├─ Auth gestion      │
│ ├─ PR parsing        │
│ ├─ Claude client     │
│ ├─ Claude parsing    │
│ ├─ Git integration   │
│ └─ ...               │
└──────────────────────┘
→ Lourd, fragile, à maintenir

BONNE APPROCHE (composabilité) ✅:
┌─────────────────────────────────────┐
│ devkit (orchestrateur)              │
│ ├─ orchestrate gh (déjà smart)     │
│ ├─ orchestrate claude (déjà smart)  │
│ ├─ orchestrate git (déjà smart)     │
│ └─ mettre à disposition les résultats
└─────────────────────────────────────┘
    │         │         │
    ▼         ▼         ▼
   gh       claude      git
(spécialistes)

→ Léger, maintenable, extensible
```

