# 📌 QUICK REFERENCE — À AVOIR OUVERT PENDANT LA DÉMO

## COMMANDES À EXÉCUTER (copier-coller)

### 1. INTRO (1:30)
```powershell
devkit

# 👉 Montre les 6 sous-commandes

devkit doctor

# 👉 Affiche: git ✓, gh ✓, python ✓, claude ✓
```

### 2. GITHUB (2:30)
```powershell
devkit gh issues --repo cli/cli --limit 5

# 👉 Table Rich avec 5 dernières issues

devkit gh pr-summary 8000 --repo cli/cli

# 👉 Détail de la PR 8000
```

### 3. AI (3:00)
```powershell
devkit ai review 8000 --repo cli/cli

# 👉 Claude review la PR (peut prendre 10-20 sec)

devkit ai commit

# 👉 Génère message de commit (doit avoir un diff staged!)
# Si erreur: git add README.md ; echo "test" >> README.md ; git add README.md

devkit ai ask "what is the GitHub CLI in 3 sentences"

# 👉 Réponse Claude (rapide si [cached])
```

### 4. WORKFLOW (2:00)
```powershell
devkit workflow feature-start awesome --repo cli/cli

# 👉 Crée branche + PR + plan IA (prend ~20 sec)

devkit workflow daily-digest --repo cli/cli

# 👉 Dashboard (PRs + issues + CI)
```

### 5. CONFIG/CACHE (1:30)
```powershell
devkit config show

# 👉 Affiche ~/.devkit/config.json

devkit config set ai_tool gemini

# 👉 Change le config

devkit cache info

# 👉 Taille du cache

devkit cache clear

# 👉 Vide le cache
```

### 6. ARCHITECTURE (4:30)
```powershell
# Ouvre VS Code
code .

# Montre fichiers clés:
# - src/devkit/main.py          (Typer root app)
# - src/devkit/commands/github.py (example commande)
# - src/devkit/utils/shell.py    (subprocess wrapper)
# - src/devkit/utils/gh.py       (gh CLI wrapper)

# Lance tests
pytest -v

# 👉 Affiche 27 tests ✓
```

---

## CE QU'IL FAUT DIRE À CHAQUE ÉTAPE

| Étape | Commande | À dire |
|-------|----------|--------|
| **INTRO** | `devkit` | "6 sous-commandes: doctor, gh, ai, workflow, config, cache" |
| | `doctor` | "Diagnostic du toolchain. git ✓, gh ✓, python ✓, claude ✓" |
| **GH 1** | `gh issues` | "subprocess + `gh issue list --json` + parsing + Rich table" |
| **GH 2** | `gh pr-summary` | "Détail d'une PR: titre, body, fichiers, reviews" |
| **AI 1** | `ai review` | "Claude lit la PR et génère un avis technique" |
| **AI 2** | `ai commit` | "Génère message semantic commit (feat: X, fix: Y)" |
| **AI 3** | `ai ask` | "Q&A one-shot. Réponse en cache si pré-chauffée" |
| **WFLOW 1** | `workflow feature-start` | "Orchestration: crée branche + PR draft + plan IA" |
| **WFLOW 2** | `workflow daily-digest` | "Dashboard quotidien: PRs + issues + CI status" |
| **CONFIG** | `config show` | "Configuration persistante: ~/.devkit/config.json" |
| **CACHE** | `cache info` | "Réponses IA en disque local, accélère futures runs" |
| **ARCH** | Code + tests | "4 couches: CLI → Commands → Utils → External tools. 27 tests" |

---

## RÉPONSES RAPIDES (Si question pendant démo)

| Question | Réponse rapide | Pour plus: Voir fichier |
|----------|---|---|
| "Pourquoi subprocess ?" | "gh déjà authed, zéro SDK, composabilité" | QA_APPROFONDIE.md |
| "Et si gh manque ?" | "doctor le detect, error lisible" | PREP_DEMO.md → TROUBLESHOOTING |
| "Tests ?" | "27 pytest. Mocks subprocess." | QA_APPROFONDIE.md → TYPE HINTS |
| "Cache ?" | "Disque local. Hash question → réponse." | QA_APPROFONDIE.md → AI & CACHE |
| "Architecture ?" | "4 couches: CLI → Commands → Utils → External" | SYNTHESE_PRESENTATION.md |
| "Windows ?" | "Cross-platform. Développé sur Windows." | QA_APPROFONDIE.md → WINDOWS |

---

## SHORTCUTS UTILES

```powershell
# Si tu veux redémo une commande
devkit gh issues --repo cli/cli --limit 3

# Si cache pas chauffé
devkit ai ask "Python is great because"

# Si tu veux réinitialiser config
devkit config reset

# Si cache plein
devkit cache clear

# Si terminal lent
clear
```

---

## TIMING (garde-le à l'œil)

```
[00:00]  Intro
[01:30]  GitHub
[04:00]  AI
[07:00]  Workflows
[09:00]  Config/Cache
[10:30]  Architecture
[14:30]  Buffer + questions
[15:00]  END
```

---

## CHECKLISTS MINI

### Avant de lancer
- [ ] Terminal plein écran
- [ ] `devkit doctor` → OK
- [ ] Diff staged (README.md)
- [ ] Cache chauffé (optionnel)

### Pendant la démo
- [ ] Copie/colle les commandes
- [ ] Attends les résultats (20-30 sec par commande IA)
- [ ] Lis le texte à dire pendant ce temps
- [ ] Si problème: regarde TROUBLESHOOTING

### Après chaque commande
- [ ] Laisser 5-10 sec à l'utilisateur de lire l'output
- [ ] Puis continuer à la suite

---

## CAS D'URGENCE

**PR 8000 n'existe plus?**  
→ Cherche un autre numéro sur github.com/cli/cli/pulls

**Claude prend trop longtemps (>30 sec)?**  
→ Dit: "Claude réfléchit... pendant ce temps..." + continue explication

**`git add README.md` manqué?**  
→ `git status` pour voir, puis `git add README.md`

**Cache pas [cached]?**  
→ C'est OK, réponse s'affiche juste en direct

**Terminal crash?**  
→ Relance terminal, relis commands depuis ici

---

## POINTS FORTS À RÉPÉTER

- ✅ "Composabilité — réutiliser plutôt que réinventer"
- ✅ "4 couches architecture — testable indépendamment"
- ✅ "Type hints partout — from __future__ import annotations"
- ✅ "27 tests pytest — couverture utils + config + CLI"
- ✅ "Cache IA — accélère runs futures"
- ✅ "Plugins — ~/.devkit/plugins/ extensibilité"
- ✅ "Fallback — Gemini manque → Claude OK"
- ✅ "100% du brief" — discovery, commands, IA, workflow, error handling, code quality, docs

---

## ERREURS À ÉVITER

❌ Dire "SDK PyGithub" → "gh CLI via subprocess"  
❌ Dire "pas de tests" → "27 tests pytest"  
❌ Dire "code non-typé" → "from __future__ import annotations"  
❌ Dire "ça marche que sur mon PC" → "cross-platform"  
❌ Oublier de faire `git add` avant `ai commit` → faire avant!  

---

## OUTPUT ATTENDU (DEBUG)

Si tu vois ça, c'est bon:

```
✅ devkit                    → 6 sous-commandes
✅ devkit doctor            → git ✓ gh ✓ python ✓ claude ✓
✅ devkit gh issues         → Table Rich [numéro | titre | state | labels | assignee]
✅ devkit gh pr-summary     → Panneau PR + fichiers + reviews
✅ devkit ai review         → Texte Claude (peut être long)
✅ devkit ai commit         → Message semantic commit
✅ devkit ai ask            → Réponse Claude (rapide ou [cached])
✅ devkit workflow start    → "Created branch / Opened PR draft / Generating plan"
✅ devkit workflow digest   → Table dashboard
✅ devkit config show       → {"ai_tool": "claude", ...}
✅ devkit cache info        → "X items, Y MB"
✅ pytest -v                → 27 passed
```

---

## SI TU DOIS IMPROVISER

**Structure classique de réponse:**

> *"C'est une excellente question. Le brief nous demande [contexte]. Notre approche: [notre solution]. Ça c'est exactement ce qu'on fait ici [pointer le code/la démo]. Cette question soulève [le détail], c'est un bon point pour la production."*

---

## NOTES RAPIDES APRÈS CHAQUE ACTE

```
[ ] INTRO — doctor OK? (Y/N)
[ ] GITHUB — tables affichées? (Y/N)
[ ] AI — Claude rapide? (Y/N)
[ ] WORKFLOW — branche créée? (Y/N)
[ ] CONFIG/CACHE — fichiers modifiés? (Y/N)
[ ] ARCH — pytest passé? (Y/N)
[ ] QUESTIONS — répondu OK? (Y/N)
```

---

## MAINTENANT

Ouvre ce fichier en split-screen pendant la démo.

Copie-colle les commandes → attends résultats → lis le texte à dire → continue.

Tu as 15 min. Vas-y ! 🚀

