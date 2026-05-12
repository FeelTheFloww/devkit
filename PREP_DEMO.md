# 🎯 GUIDE PRATIQUE — Préparation + Présentation

## ✅ CHECKLIST PRÉ-DÉMO (À FAIRE 15 MIN AVANT)

### Environnement
- [ ] Ouvre Windows Terminal en plein écran (police 14-16pt)
- [ ] Place-toi dans: `cd C:\Users\firfl\OneDrive\Desktop\devkit_project\devkit_project`
- [ ] Crée alias: `function devkit { python -m devkit.main @args }`

### Tests du toolchain
```powershell
devkit doctor
# Doit afficher: git ✓, gh ✓, python ✓, claude ✓
# Si Gemini manque, c'est OK (on montrera le fallback)
```

### Pré-chauffage du cache IA
Pose ces questions MAINTENANT pour que les réponses s'affichent `(cached)` pendant la démo :
```powershell
devkit ai ask "explain async vs threads in Python"
devkit ai ask "what is a Makefile in 3 sentences"
devkit ai ask "what is the GitHub CLI in 3 sentences"
```

### Préparer un diff pour `devkit ai commit`
```powershell
# Ajoute du contenu à README
"# Demo $(Get-Date -Format HH:mm)" | Add-Content README.md
git add README.md

# Vérifie qu'il y a du diff
git diff --staged
```

### Clear et test final
```powershell
clear
devkit       # Affiche le welcome panel
```

---

## 🎬 TIMING DE DÉMO — 15 MIN CHRONO

```
[00:00-00:30]  Acte 1. INTRO + DOCTOR
                - Pitch du projet (30 sec)
                - `devkit` → montre les 6 sous-commandes
                - `devkit doctor` → diagnostic

[00:30-03:00]  Acte 2. GITHUB (2:30)
                - `devkit gh issues --repo cli/cli --limit 5`
                  Montre table Rich + dit "subprocess + gh --json + parsing"
                - `devkit gh pr-summary 8000 --repo cli/cli`
                  Montre panneau PR + tables

[03:00-06:00]  Acte 3. AI (3:00)
                - `devkit ai review 8000 --repo cli/cli`
                  Claude review la PR
                - `devkit ai commit`
                  Génère message semantic commit
                - `devkit ai ask "what is GitHub CLI in 3 sentences"`
                  Q&A cached (pré-chauffée)

[06:00-08:00]  Acte 4. WORKFLOWS (2:00)
                - `devkit workflow feature-start awesome-feature --repo cli/cli`
                  Montre orchestration (branche + PR draft + plan IA)
                - `devkit workflow daily-digest`
                  Dashboard (PRs + issues + CI)

[08:00-09:30]  Acte 5. CONFIG + CACHE (1:30)
                - `devkit config show` → affiche ~/.devkit/config.json
                - `devkit config set ai_tool gemini` → modifie
                - `devkit cache info` → taille du cache
                - `devkit cache clear` → vide

[09:30-14:00]  Acte 6. ARCHITECTURE (4:30)
                - Ouvre VS Code
                - Montre src/devkit/main.py (Typer app)
                - Montre commands/github.py (une commande exemple)
                - Montre utils/shell.py (wrapper subprocess)
                - Montre utils/gh.py (appel gh + parsing)
                - Dit: "4 couches, bien séparées, testables."
                - Lance pytest : `pytest -v`
                - Montre 27 tests ✓

[14:00-15:00]  BUFFER
                - Q&A rapides en réserve
                - Redémo rapide d'une commande si problème
```

---

## 🚨 TROUBLESHOOTING LIVE

### Problème: `devkit doctor` affiche un outil au rouge
**Solution:** C'est prévisible (ex: Gemini peut manquer). Tu dis: *"Cet outil manque, mais `devkit` n'en a pas besoin pour cette démo. Claude suffit. Si quelqu'un en a besoin, `gh` le propose à l'installation."*

### Problème: Numéro de PR 8000 n'existe plus dans cli/cli
**Solution:** Avant la démo, va sur https://github.com/cli/cli/pulls, note un numéro de PR ouvert récent (ex: 7500, 7600), mémorise-le.

### Problème: Cache IA absent
**Solution:** Les réponses s'affichent juste en direct (pas `(cached)` au début). C'est moins spectaculaire mais ça marche. Dit: *"La réponse s'affiche en direct — on peut aussi la mettre en cache pour accélerer future runs."*

### Problème: `devkit ai commit` manque un diff staged
**Solution:** Avant de la commande, fais:
```powershell
echo "# demo $(date)" >> README.md
git add README.md
git diff --staged
# Puis devkit ai commit
```

### Problème: Terminal trop petit/texte illisible
**Solution:** Zoom terminal `Ctrl+-` / `Ctrl++` ou change la police dans Windows Terminal settings.

---

## 📝 NOTES PENDANT LA DÉMO

### Points forts à mémoriser
1. **"subprocess plutôt que SDK"** — `gh` est déjà sur la machine, zéro tokens
2. **"Composabilité"** — réutiliser vs réinventer (c'est le brief)
3. **"Architecture 4 couches"** — chacune testable indépendamment
4. **"Type hints"** — `from __future__ import annotations` partout
5. **"27 tests"** — couverture utils, config, CLI

### Si on te demande sur le brief
Dis: *"Le brief exige: discovery, commands + JSON, ≥3 IA, workflow, error handling, code quality, documentation. Tout est couvert — je peux vous montrer la checklist après."*

---

## ❓ RÉPONSES PIÉGÉES POSSIBLES

### Q: "Vous stockez les tokens GitHub où ?"
**R:** *"Pas stockés par devkit — `gh` les gère. `gh auth status` montre que je suis authentifié. devkit ne les manipule jamais."*

### Q: "Et si quelqu'un a un autre repo GitHub private ?"
**R:** *"Il remplace `--repo cli/cli` par son repo. Si privé, `gh` doit être authentifié (standard GitHub). devkit ne change rien à l'auth."*

### Q: "Les réponses IA sont-elles loggées ?"
**R:** *"Écrits juste en cache disque local. Pas de serveur, pas d'upload. Les tokens Claude/Gemini restent en env var."*

### Q: "Vous avez mesuré les perfs ?"
**R:** *"Pas le scope du brief. Mais chaque commande est ~ aussi rapide que son outil sous-jacent (`gh` ou Claude). Le cache accélère réutilisations."*

### Q: "Windows/Mac/Linux ?"
**R:** *"Python 3.10+ portable — devrait marcher partout. J'ai développé sur Windows. subprocess appels sont portables."*

---

## 🎓 TERMES CLÉS — Pour paraître expert

- **Typer** : Framework CLI Python. Type hints natifs → `--help` auto-généré.
- **Rich** : Rendering tables, panels, couleurs. Rend les données belle.
- **subprocess.run()** : Lancer `gh`, `claude`, `git` comme processus externes.
- **gh --json** : GitHub CLI en mode JSON. On parse ça → Python dict → Rich table.
- **~/.devkit/config.json** : Configuration persistante (ai_tool, default_repo, etc.)
- **~/.devkit/cache/** : Cache IA disque. Hash de la question → réponse.
- **Fallback** : Si Gemini manque mais Claude marche, utiliser Claude.
- **Composabilité** : Réutiliser outils existants plutôt que réinventer.
- **Plugins** : Code utilisateur (~/.devkit/plugins/) auto-chargé au startup.

---

## 🎬 SCRIPT COURT (5 MIN MAX)

Si tu dois faire une présentation ultra-courte:

```
devkit doctor
# "Diagnostic du toolchain. Les outils que j'orchestre."

devkit gh issues --repo cli/cli --limit 3
# "Liste d'issues depuis GitHub. Table Rich."

devkit ai ask "what is the GitHub CLI"
# "Q&A IA. Claude répond. Réponse en cache si re-demandée."

devkit workflow feature-start test --repo cli/cli
# "Workflow: crée branche + PR draft + plan IA. Composabilité."
```

Puis: *"Architecture: 4 couches, type hints, 27 tests. Questions ?"*

---

## 📊 SCRIPT LONG (15 MIN MAX)

Voir le PROTOCOLE_DEMO.md (déjà fourni) + SYNTHESE_PRESENTATION.md.

---

## 🎯 ERREURS À NE PAS FAIRE

❌ Dire "on utilise l'SDK PyGithub" → ❌ Non, on utilise `gh` CLI via subprocess  
❌ Dire "pas de tests" → ❌ Si, 27 tests pytest  
❌ Dire "architecture maison" → ❌ Non, 4 couches + patterns reconnus  
❌ Dire "ça marche que sur mon PC" → ❌ Non, Python 3.10+ portable  
❌ Montrer du code non-typé → ✅ Tout est typé (`from __future__ import annotations`)  

---

## 📞 DANS LE DOUTE...

**Reviens toujours au core message :**

> *"devkit orchestre `gh`, Claude, Gemini, Git via `subprocess`. Aucune réinvention. 4 couches architecture, type hints, tests. Répondre au brief Modern CLI."*

**Si on t'interrompt:** *"Bonne question. Laisse-moi te montrer ça." → saute à la section pertinente.*

