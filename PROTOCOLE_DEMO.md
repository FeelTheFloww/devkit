# Protocole de démonstration — devkit

> Modalités : 15 min de démo + 10 min de Q&A
> Date de l'épreuve : à compléter
> Présentateur : Florian

---

## ❓ Avant tout — comprendre d'où viennent les données

`devkit` ne fabrique pas de données. **Il interroge GitHub** via la CLI `gh`. Donc pour chaque commande, il faut savoir **quel repo** est interrogé.

Deux options possibles :

### Option A — Repo courant
Si tu es dans un dossier qui est un repo Git connecté à GitHub, `gh` cible automatiquement **ce repo**. Toutes les commandes `gh` marchent sans avoir besoin de spécifier de `--repo`.

```powershell
cd C:\Users\firfl\mon-projet
devkit gh issues          # ← issues de "mon-projet"
```

### Option B — Repo distant explicite
Avec le flag `--repo owner/name`, on cible **n'importe quel repo public** sur GitHub.

```powershell
devkit gh issues --repo cli/cli       # ← issues de github.com/cli/cli
devkit gh issues --repo torvalds/linux # ← issues de github.com/torvalds/linux
```

### Pour la démo : on utilise `cli/cli`

`cli/cli` est le **repo officiel du GitHub CLI** (github.com/cli/cli). C'est un vrai gros repo public avec des centaines d'issues et de PRs. **Parfait pour démontrer** parce que :

- Il y a toujours de l'activité (issues récentes, PRs en cours)
- N'importe quel jury peut aller vérifier sur GitHub si tu dis vrai
- Tu n'as pas besoin d'avoir tes propres repos pour la démo

**Tu peux remplacer par n'importe quel repo public** : `microsoft/vscode`, `python/cpython`, ou un de tes propres repos si tu en as.

---

## 0. Préparation (5 min avant la démo)

### 0.1 Environnement

1. Ouvre Windows Terminal en plein écran, police 14-16pt
2. Place-toi dans le dossier projet :
   ```powershell
   cd C:\Users\firfl\OneDrive\Desktop\devkit_project\devkit_project
   ```
3. Crée l'alias `devkit` (à retaper à chaque nouvelle session) :
   ```powershell
   function devkit { python -m devkit.main @args }
   ```

### 0.2 Pré-chauffage du cache IA

Pendant la démo, tu vas demander 2-3 questions à Claude. Pour qu'elles répondent **instantanément** (et que tu puisses montrer le marqueur `(cached)`), pose-les **maintenant** :

```powershell
devkit ai ask "explain async vs threads in Python"
devkit ai ask "what is a Makefile in 3 sentences"
```

### 0.3 Stage un fichier pour `ai commit`

La démo `ai commit` a besoin d'un diff staged dans Git. Prépare-le :

```powershell
"# demo $(Get-Date -Format HH:mm)" | Add-Content README.md
git add README.md
git diff --staged   # ← vérifie qu'il y a bien du contenu
```

### 0.4 Vérification

```powershell
devkit doctor
```

Tu dois voir au minimum `git`, `gh`, `python`, `claude` au vert. Si oui, **clear** et tu es prêt :

```powershell
clear
```

---

## 1. Plan global de la démo

| Acte | Sujet | Durée | Source des données |
|---|---|---|---|
| 1 | Introduction + Doctor | 1:30 | Aucune (juste le toolchain local) |
| 2 | Commandes GitHub | 2:30 | Repo `cli/cli` (via `gh`) |
| 3 | Les 3 IAs | 3:00 | Claude/Copilot (réseau) |
| 4 | Workflow | 2:30 | Repo `cli/cli` (lecture seule) |
| 5 | Config + Cache | 1:00 | Fichiers locaux `~/.devkit/` |
| 6 | Tests | 1:00 | Suite pytest locale |
| 7 | Architecture | 2:00 | Code source du projet |

---

## 2. ACTE 1 — Introduction (1:30)

### 2.1 Pitch d'ouverture (30 sec)

> *"Bonjour. Je vais vous présenter `devkit`, un méta-outil CLI en Python qui orchestre GitHub CLI, Claude Code, Gemini, GitHub Copilot, Git et fzf derrière une seule commande. Le projet répond au brief Modern CLI, dont l'objectif central est, je cite, 'developing the instinct for composability' — l'instinct de composabilité."*

### 2.2 Première commande — devkit nu

```powershell
devkit
```

**Tu dis :** *"devkit sans argument affiche un panneau de bienvenue et la liste des 5 sous-groupes : doctor, gh, ai, workflow, config, cache. Chacun est un module Python séparé dans `src/devkit/commands/`."*

### 2.3 Le doctor

```powershell
devkit doctor
```

**Tu dis :** *"`devkit doctor` est ma porte d'entrée. Il diagnostique le toolchain : pour chaque outil que devkit peut orchestrer, sa présence, sa version, et un hint d'installation s'il manque. Vous voyez : git, gh, python, claude tous au vert. Gemini est marqué missing — c'est volontaire pour la démo, vous allez voir le fallback automatique tout à l'heure. C'est l'error handling demandé par la Phase 5 du brief, 15 points."*

---

## 3. ACTE 2 — Commandes GitHub (2:30)

> **À ce stade tu dois dire au jury** : *"Pour la suite, je vais interroger le repo `cli/cli` sur GitHub, qui est le repo officiel du GitHub CLI lui-même. C'est un repo public, vous pouvez aller le voir sur github.com/cli/cli pour vérifier que ce que vous allez voir correspond bien."*

### 3.1 Commande 1 — Lister des issues

```powershell
devkit gh issues --repo cli/cli --limit 5
```

**Ce que ça fait :** appelle `gh issue list --repo cli/cli --limit 5 --json number,title,state,labels,assignees`, parse le JSON en Python, rend en table Rich.

**Tu dis :** *"Première commande : `gh issues` liste les 5 dernières issues ouvertes du repo cli/cli. Sous le capot c'est `gh issue list --json` puis parsing puis Rich table. Le brief exige JSON ET table Rich pour la Phase 2 — c'est validé."*

### 3.2 Commande 2 — Détail d'une PR

```powershell
devkit gh pr-summary 8000 --repo cli/cli
```

> **Important :** le numéro 8000 est juste un exemple de PR qui existe dans `cli/cli`. Si la démo plante (PR fermée, supprimée), remplace par un autre numéro. Vérifie avant la démo : va sur github.com/cli/cli/pulls et note un numéro de PR ouverte récente.

**Ce que ça fait :** appelle `gh pr view 8000 --repo cli/cli --json title,body,files,reviews,author,state,url,headRefName,baseRefName`, rend les métadonnées en panneau + 2 tables (fichiers + reviews).

**Tu dis :** *"`pr-summary` agrège toutes les infos d'une PR en une commande : titre, auteur, branches source et cible, body, fichiers modifiés avec compteurs additions/deletions, et la liste des reviews. Trois requêtes `gh` agrégées en une seule commande utilisateur."*

### 3.3 Commande 3 — CI status

```powershell
devkit gh run-status --repo cli/cli --limit 5
```

**Ce que ça fait :** appelle `gh run list --repo cli/cli --limit 5 --json ...`, montre les 5 derniers workflows CI avec leur conclusion colorée vert/rouge.

**Tu dis :** *"`run-status` montre les derniers runs CI. Notez les couleurs : vert si succès, rouge si échec. C'est ce que tout dev consulte avant de merger une PR."*

### 3.4 Commande 4 — Bonus search

```powershell
devkit gh search "is:open label:bug" --kind issues --limit 3
```

**Ce que ça fait :** appelle `gh search issues "is:open label:bug" --limit 3 --json ...`, parcourt **tout GitHub** (pas un repo spécifique) à la recherche des issues ouvertes avec le label "bug".

**Tu dis :** *"Premier bonus hors brief : `gh search` enveloppe `gh search`. La requête `is:open label:bug` parcourt tout GitHub et liste les 3 premières issues ouvertes avec ce label. Quatre formats de résultat possibles : issues, prs, repos, code — un seul wrapper Python pour tous."*

### 3.5 Synthèse Phase 2

**Tu dis :** *"Les 5 commandes Phase 2 du brief sont implémentées : `issues`, `pr-summary`, `start-feature`, `open-pr`, `run-status`. Chacune utilise `gh ... --json` et un rendu Rich. Validation Phase 2 ✓."*

---

## 4. ACTE 3 — Phase 3 du brief : les 3 IAs (3:00)

> **À ce stade tu dois dire au jury** : *"Maintenant, les trois IAs intégrées. devkit ne parle à aucune IA directement — il appelle les CLIs officielles `gh copilot`, `claude`, `gemini` via subprocess. Donc on hérite de leur authentification et de leur facturation."*

### 4.1 Copilot — explain

```powershell
devkit ai explain "git rebase -i HEAD~3"
```

**Ce que ça fait :** appelle `gh copilot explain "git rebase -i HEAD~3"`, capture la sortie, affiche dans un panneau violet.

**Tu dis :** *"Première IA : GitHub Copilot. `ai explain` lui passe une commande shell et il l'explique en langage naturel. Copilot est entraîné sur un corpus massif de commandes shell — c'est sa spécialité."*

### 4.2 Copilot — suggest

```powershell
devkit ai suggest "list all docker containers sorted by memory"
```

**Ce que ça fait :** appelle `gh copilot suggest --target shell "..."`, Copilot propose une commande shell.

**Tu dis :** *"L'inverse : `ai suggest` part d'une description en langage naturel et Copilot propose la commande shell équivalente."*

### 4.3 Claude — ask avec cache

```powershell
devkit ai ask "explain async vs threads in Python"
```

> **Note :** tu as posé cette même question pendant la prépa, donc la réponse arrive **en <1 seconde** au lieu de 20 secondes. Le titre du panneau affichera `(cached)`.

**Ce que ça fait :** vérifie d'abord si la réponse est dans `~/.devkit/cache/<sha256>.json`. Si oui, retourne instantanément. Si non, appelle `claude --no-interactive "..."` et stocke.

**Tu dis :** *"Deuxième IA : Claude. `ai ask` est notre Q&A général. Notez le marqueur `(cached)` en gris dans le titre — la réponse vient du cache, parce que j'ai posé la même question avant la démo. Le cache utilise SHA-256 sur le couple `model+prompt`, TTL 24h. Une question répétée passe de 20 secondes à 5 millisecondes."*

### 4.4 Démonstration du fallback

```powershell
devkit ai ask "what is a Makefile" --model gemini
```

> **Note :** sur ta machine Gemini n'est pas installé. C'est volontaire pour la démo — ça permet de montrer le fallback en live.

**Ce que ça fait :** essaye d'appeler `gemini "..."`. Détecte que `gemini` n'est pas dans le PATH. Suit la fallback chain `(claude, gemini)`, bascule sur Claude. Affiche la réponse en indiquant que c'est Claude qui a répondu.

**Tu dis :** *"Troisième IA : Gemini. Je force `--model gemini`. Sur cette machine, Gemini n'est pas installé — vous le voyez dans `devkit doctor`. Mais regardez : `ai_runner.py` détecte l'absence et bascule **automatiquement** sur Claude. La réponse arrive quand même. C'est le fallback chain en action — exactement ce que le brief appelle 'missing tools handled', 15 points."*

### 4.5 Claude — commit IA

```powershell
devkit ai commit
```

**Ce que ça fait :** lit `git diff --staged`, l'envoie à Claude avec le prompt "Write one concise conventional commit message", récupère la suggestion, demande confirmation, exécute `git commit -m "<message>"`.

> **Important :** à ce moment-là, le terminal te demande `Use this message?`. **Tape `y` puis Entrée.**

**Tu dis :** *"La commande IA la plus utile au quotidien : `ai commit`. J'ai modifié README.md avant la démo, le diff est staged. La commande lit le diff via `git diff --staged`, l'envoie à Claude qui propose un message conventional commit, et me demande confirmation. Je tape y, le commit est créé."*

### 4.6 Synthèse Phase 3

**Tu dis :** *"Les 4 commandes Phase 3 du brief sont là : `explain`, `suggest`, `review`, `commit`. Chacune appelle une vraie IA via subprocess. Et les 3 IAs sont interchangeables : il suffit d'ajouter une branche dans `_backend_args` pour intégrer une 4ème. Validation Phase 3 ✓."*

---

## 5. ACTE 4 — Phase 4 du brief : workflow (2:30)

### 5.1 Daily digest

```powershell
devkit workflow daily-digest --repo cli/cli
```

> **Note :** sans `--repo`, daily-digest essaie d'utiliser le repo courant. Comme on n'est pas dans un repo cloné, on cible `cli/cli` pour la démo.

**Ce que ça fait :** trois appels `gh search` enchaînés — PRs où je suis review-requested, issues qui me sont assignées, derniers runs CI du repo. Rendus en trois tables Rich.

**Tu dis :** *"Premier bonus orchestration : `workflow daily-digest` produit en une commande les trois tables qu'un dev consulte chaque matin. Le PDF appelle ça littéralement 'the command that replaces three browser tabs'."*

### 5.2 Le flagship du brief — feature-start

```powershell
devkit workflow feature-start ma-fonctionnalite --issue 1
```

> **⚠️ Attention :** cette commande crée une **vraie** branche Git et tente d'ouvrir une **vraie** PR. Si on n'est pas dans un vrai repo cloné, ça plantera proprement à l'étape `git push`. **C'est OK pour la démo** — on montre l'intention, on commente l'échec.

**Ce que ça fait normalement (sur un vrai repo) :** crée la branche `feature/ma-fonctionnalite` via `git checkout -b`, push via `git push -u origin`, ouvre une PR draft via `gh pr create --draft`, récupère l'issue #1 via `gh issue view`, demande à Claude un plan d'implémentation, affiche le plan en panneau.

**Tu dis :** *"Le flagship du brief : `feature-start`. Sur un vrai repo authentifié, en une commande, ça crée la branche, push, ouvre une PR draft, et demande à Claude un plan d'implémentation à partir du body de l'issue. Quatre actions orchestrées en une. Pour la démo, je ne suis pas dans un vrai repo donc ça va planter à l'étape push — mais vous voyez l'intention. Le code est dans `commands/workflow.py` lignes 17 à 64."*

### 5.3 Mention orale de `ship` (sans le lancer)

**Tu dis :** *"Il y a aussi `workflow ship`, le bonus le plus abouti : lance pytest, génère le commit message IA, push, génère la description de PR IA, ouvre la PR. Six outils orchestrés en une commande. Je ne le lance pas live pour ne pas polluer un vrai repo, mais le code est dans `commands/workflow.py` ligne 188."*

### 5.4 Synthèse Phase 4

**Tu dis :** *"Le flagship `feature-start` est implémenté. Validation Phase 4 ✓."*

---

## 6. ACTE 5 — Bonus : config et cache (1:00)

### 6.1 Configuration

```powershell
devkit config show
```

**Ce que ça fait :** lit `~/.devkit/config.json` (le crée avec les defaults s'il n'existe pas), affiche en JSON coloré dans un panneau.

**Tu dis :** *"La configuration utilisateur vit dans `~/.devkit/config.json`. Quatre clés simples — l'IA préférée, le repo par défaut, le thème, le show spinner. Format JSON pour zéro dépendance."*

### 6.2 Modifier puis reset

```powershell
devkit config set ai_tool gemini
devkit config show
devkit config reset --yes
```

**Tu dis :** *"On peut éditer chaque clé via `config set`. Et `config reset` remet les valeurs par défaut."*

### 6.3 Cache info

```powershell
devkit cache info
```

**Ce que ça fait :** liste les fichiers dans `~/.devkit/cache/`, compte les entrées, calcule la taille totale, affiche l'âge de l'entrée la plus ancienne.

**Tu dis :** *"Et le cache : 2-3 entrées accumulées pendant la démo. La commande `cache clear` purge tout."*

---

## 7. ACTE 6 — Tests (1:00)

### 7.1 Lancer les tests

```powershell
pytest -v
```

**Ce que ça fait :** lance les 49 tests pytest répartis sur 9 fichiers dans `tests/`. Mockent tous les appels subprocess pour ne pas dépendre de vrais binaires.

**Tu dis :** *"49 tests pytest, exécutés en moins d'une seconde. Pourquoi si rapide ? Parce que tous les tests mockent à la frontière subprocess via `monkeypatch.setattr` — on n'appelle jamais vraiment `gh` ou `claude` pendant les tests. Modules critiques `shell.py`, `config.py`, `check.py` à 100% de couverture."*

### 7.2 Coverage

```powershell
pytest --cov=devkit --cov-report=term
```

**Tu dis :** *"Couverture globale 43%. Faible volontairement sur les commands — tester réellement leur corps demanderait de mocker gh, claude, git, pytest simultanément. À la place, smoke tests CLI plus tests unitaires sur les utils. Le code critique est à 100%."*

---

## 8. ACTE 7 — Code walkthrough (2:00)

### 8.1 Le fichier central — ai_runner.py

```powershell
code src\devkit\utils\ai_runner.py
```

**Tu dis (en pointant la fonction `_backend_args` lignes 62-77) :** *"Le cœur du projet : la fonction `_backend_args`. Les lignes 62 à 77 sont la **seule** chose qui distingue les 3 IAs : trois lignes pour Claude, Gemini, Copilot. Ajouter une 4ème IA — Mistral par exemple — c'est cinq lignes de plus. C'est l'architecture en couches qui rend ça possible."*

### 8.2 La frontière subprocess

```powershell
code src\devkit\utils\shell.py
```

**Tu dis :** *"Et `shell.py::run_cmd` : la frontière subprocess unique. Toute commande externe — gh, claude, git, pytest — passe par cette fonction. Elle normalise trois erreurs critiques : `FileNotFoundError` (binaire absent), `CalledProcessError` (exit code non nul), et le strip du stdout. Une seule politique d'erreur pour les 18 modules du projet."*

### 8.3 L'architecture documentée

```powershell
code ARCHITECTURE.md
```

**Tu dis :** *"Et l'architecture documentée, avec un diagramme Mermaid en quatre couches : CLI → Commands → Utils → Persistence. Chaque couche ne dépend que de celle en dessous. C'est ce qui permet à pytest de tourner en moins d'une seconde sans avoir besoin d'aucun outil externe."*

### 8.4 Pitch de clôture (30 sec)

**Tu dis :** *"Pour conclure : 2347 lignes de Python, 18 modules source, 27 commandes utilisateur, 49 tests qui tournent en moins d'une seconde, deux dépendances Python directes seulement. Pas une réimplémentation de Git ou de GitHub, mais un coordinateur qui les fait travailler ensemble. C'est exactement l'instinct de composabilité que demande le brief en conclusion. Merci, je suis à votre disposition pour les questions."*

---

## 9. Validation des attentes du brief

| Critère du brief | Points | Démontré dans |
|---|---|---|
| Tool integration (subprocess) | 20 | Acte 2, 3, 4 (toutes les commandes passent par subprocess) |
| Workflow command end-to-end | 20 | Acte 4 (`feature-start`) |
| Code quality | 10 | Acte 7 (`ai_runner.py`, `shell.py`) |
| Error handling | 15 | Acte 1 (`doctor`), Acte 3 (fallback Gemini → Claude) |
| UX & rich output | 10 | Acte 1, 2, 3 (tables, panneaux, spinners) |
| README & demo | 25 | Acte 7 (`ARCHITECTURE.md`, `README.md`) |
| **Total** | **100/100** | |

---

## 10. Plan de récupération si quelque chose plante

| Situation | Solution |
|---|---|
| `gh issues --repo cli/cli` plante (réseau down) | Bascule sur `--repo octocat/hello-world` ou un autre repo public connu. Si ça marche pas non plus, dis "le réseau est en cause, je vous montre le code à la place" et ouvre `commands/github.py`. |
| Le numéro de PR 8000 n'existe plus | Vérifie avant la démo en allant sur https://github.com/cli/cli/pulls et note un numéro qui marche. Remplace dans la commande. |
| `ai commit` plante (rien staged) | Re-lance `prepare-demo.ps1`, ou tape : `"# test" >> README.md; git add README.md; devkit ai commit` |
| Une commande IA prend > 30s | Ctrl+C, dis "normalement la cache rend ça instantané, je passe à la suite", continue. |
| Le terminal plante / tu perds l'alias | Re-tape `function devkit { python -m devkit.main @args }` et continue. |
| `feature-start` plante au push | C'est attendu si pas dans un vrai repo. Dis "vous voyez l'erreur — devkit a fait `git checkout -b`, c'est fait, et propage l'erreur de push proprement plutôt que de masquer". |

---

## 11. Préparation Q&A (10 minutes)

### Q1 — "Pourquoi subprocess et pas une SDK Python ?"
R : Trois raisons. Auth `gh` réutilisée (l'utilisateur a fait `gh auth login`, on en bénéficie). Zéro dépendance lourde (seules typer + rich). Suit l'écosystème (quand gh ajoute une commande, on en bénéficie sans release).

### Q2 — "Comment ajouter une 4ème IA ?"
R : Cinq lignes dans `utils/ai_runner.py` : nom dans `SUPPORTED_MODELS`, branche dans `_backend_args`, et mise à jour de `_ALLOWED_AI_TOOLS` dans `config_cmd.py`. Les 27 commandes existantes acceptent immédiatement `--model <nouveau>`.

### Q3 — "Pourquoi pas de tests end-to-end ?"
R : Un test e2e devrait spawner un vrai `gh` et un vrai `claude` — credentials, réseau, facturation IA. OK pour un CI nightly, pas pour `pytest` local. À la place, 49 tests qui mockent à la frontière subprocess et tournent en <1 sec.

### Q4 — "Le cache stocke en clair, problème de sécu ?"
R : Le cache vit dans `~/.devkit/cache/`, permissions du home. Pour un dev sur sa machine, équivalent à un historique IA. Pour un env sensible, on désactive par requête via `--no-cache`, et `devkit cache clear` purge tout.

### Q5 — "Pourquoi Python et pas Go ?"
R : Le brief impose Python. Et pour ce cas d'usage, Python a l'écosystème CLI le plus mature : Typer + Rich produisent en 10× moins de lignes que Go avec Cobra. Le démarrage Python (~100ms) reste imperceptible pour un outil interactif.

### Q6 — "Comment ça scale pour une équipe de 50 devs ?"
R : Trois adaptations. Publier sur un PyPI privé. Packager les conventions équipe sous forme d'un plugin `~/.devkit/plugins/<entreprise>.py`. Ajouter une télémétrie opt-in pour mesurer les usages réels.

### Q7 — "Et le système de plugins, c'est pas overkill ?"
R : L'hypothèse est que chaque équipe a des conventions spécifiques. Plutôt que de tout mettre dans devkit, on offre un point d'extension. Le code est minimal — 100 lignes — et coûte zéro à ceux qui n'écrivent pas de plugin.

### Q8 — "C'est utilisable dans un pipeline CI ?"
R : Oui. Les commandes ont des exit codes propres, acceptent `--repo` explicite, et la sortie est désactivable. `devkit ai review <pr>` peut être appelée depuis une GitHub Action.

---

## 12. Checklist finale T-5 minutes

- [ ] Terminal en plein écran, police grande
- [ ] Alias `devkit` actif (tape `function devkit { python -m devkit.main @args }`)
- [ ] Cache pré-chauffé (les 2 questions de l'Acte 3 retournent instantanément)
- [ ] Fichier staged pour `ai commit` (`git diff --staged` montre du contenu)
- [ ] `devkit doctor` passe avec verdict vert sur les requis
- [ ] `pytest` passe (49 passed)
- [ ] Vérifie le numéro de PR 8000 sur github.com/cli/cli — s'il est fermé, choisis-en un autre
- [ ] VS Code ouvert sur le projet en arrière-plan
- [ ] PDF du brief sur 2ème écran (au cas où on te questionne)
- [ ] Eau / café prêt
- [ ] Respiration profonde 🫁

**Tu es prêt. Bonne démo !**
