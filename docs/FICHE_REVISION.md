# ⚡ FICHE DE RÉVISION — 5 MIN AVANT LA DÉMO

## 🎯 LE MESSAGE CENTRAL
> *"devkit orchestre subprocess (gh, Claude, Gemini, Git). Aucune réinvention. Composabilité first."*

---

## 📊 LES 6 SOUS-COMMANDES

| Cmd | Fait | Montre |
|-----|------|--------|
| `doctor` | Teste les outils | git ✓, gh ✓, claude ✓ |
| `gh` | Récup issues/PRs GitHub | Table Rich, parsing JSON |
| `ai` | Appelle Claude/Gemini | Review PR, commit message |
| `workflow` | Orchestre multi-outils | Crée branche + PR + plan IA |
| `config` | Gère ~/.devkit/config.json | show/set/reset |
| `cache` | Disque IA (~/.devkit/cache/) | info/clear |

---

## 🏗️ ARCHITECTURE (15 sec)
```
main.py (Typer root app)
  ↓ add_typer
commands/*.py (logique métier)
  ↓ importe
utils/*.py (subprocess wrappers)
  ↓ appelle
gh, claude, gemini, git (processus externes)
```

**= 4 couches indépendantes, testables**

---

## 🔧 TECHNO STACK

- **Python 3.10+** : Langage
- **Typer** : CLI framework (type hints natifs)
- **Rich** : Tables, panneaux, couleurs
- **subprocess** : Appelle les outils externes
- **pytest (27 tests)** : Validation
- **JSON** : Config + cache

---

## 🎬 DÉMO (15 min)

```
[1:30]  doctor                      # diagnostic
[2:30]  gh issues + pr-summary      # GitHub
[3:00]  ai review + commit + ask    # AI (cached)
[2:00]  workflow feature-start      # Orchestration
[1:30]  config + cache              # Gestion
[4:30]  Architecture + pytest       # Code
```

---

## ❌ À JAMAIS DIRE

- "On utilise PyGithub" ❌ (on utilise gh CLI)
- "Pas de tests" ❌ (27 tests)
- "Non-typé" ❌ (tout typé)
- "Architecture custom" ❌ (4 couches reconnus)
- "On stocke les tokens" ❌ (env vars)

---

## ✅ À TOUJOURS DIRE

- "subprocess vs SDK — zéro dépendance lourde"
- "Composabilité — réutiliser plutôt que réinventer"
- "4 couches bien séparées, testables indépendamment"
- "Type hints partout. 27 tests pytest."
- "Cache IA pour accélérer runs futures"
- "Plugins: extensibilité sans fork"

---

## 🆘 SI TU SÉCHES

> *"Le brief exige composabilité. On orchestre `gh`, Claude, Git par subprocess plutôt que SDK lourds. C'est exact ce qu'on fait ici. Votre question [détail] — bonne observation pour la production, mais pour cette démo ça n'affecte pas le core."*

---

## 📝 DERNIERS CHECKS

- [ ] `devkit doctor` → git ✓, gh ✓, python ✓, claude ✓
- [ ] Cache pré-chauffé (`devkit ai ask ... × 2`)
- [ ] README.md staged (pour `ai commit`)
- [ ] Terminal 14-16pt, plein écran
- [ ] Numéro de PR valide pour cli/cli (ex: 8000)

---

## 💪 POINTS FORTS

1. **Subprocess** — Zéro SDK, zéro tokens perso
2. **4 couches** — CLI → Commands → Utils → External
3. **Type hints** — `from __future__ import annotations` partout
4. **Tests** — 27 pytest couvrant utils, config, CLI
5. **Cache** — Disque local, accélère futures runs
6. **Plugins** — ~/.devkit/plugins/, extensibilité user
7. **Fallback** — Gemini manque → Claude OK
8. **Brief** — 100% couvert (discovery, commands, IA, workflow, error handling, code quality, docs, composabilité)

---

## 🎓 VocabCLÉ

- **Typer** : Framework CLI type-hints
- **Rich** : Rendu terminal (tables, couleurs)
- **subprocess** : Lancer commandes externes
- **Composabilité** : Réutiliser vs réinventer
- **Cache** : Réponses IA disque (~/.devkit/cache/)
- **Fallback** : Plan B si outil A manque
- **Plugins** : Code user (~/.devkit/plugins/) auto-chargé

---

## 📞 Q&A RAPIDES

**Q: "Pourquoi pas SDK ?"**  
R: *"Zéro dépendance, gh déjà authed, composabilité."*

**Q: "Et si gh manque ?"**  
R: *"doctor le detect rouge, error lisible."*

**Q: "Tests ?"**  
R: *"27 pytest, mocks subprocess, couvrent utils + config + CLI."*

**Q: "Cache ?"**  
R: *"Disque local, hash question → réponse. Fallback API si absent."*

**Q: "Plugins ?"**  
R: *"~/.devkit/plugins/*.py auto-importés, extensibilité user."*

**Q: "Windows ?"**  
R: *"Cross-platform. Développé sur Windows. pathlib abstrait les OS."*

---

## ⏱️ TIMING

- `doctor`: 30 sec
- `gh issues + pr-summary`: 2:30
- `ai review + commit + ask`: 3:00  
- `workflow`: 2:00
- `config + cache`: 1:30
- `architecture + tests`: 4:30
- Buffer: 1:00
= **15:00 total**

---

## 🚀 GO !

**Tu as ça :** subprocess + CLI framework + tests + docs.  
**Ils veulent ça:** composabilité.  
**C'est ça qu'on livre.** ✅

