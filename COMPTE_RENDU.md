# Compte rendu de projet — `devkit`

## Modern CLI : Developer Workflow with Modern CLI Tools

---

## 1. Présentation du projet

Le terminal du développeur a beaucoup évolué ces dernières années. À côté de Git et des outils Unix classiques sont apparues plusieurs CLI modernes : `gh` pour GitHub, `claude` et `gemini` pour les IA, `fzf` pour la sélection interactive, `bat` ou `delta` pour la lecture de fichiers et de diffs. Chacune est excellente, mais elles ne savent pas travailler ensemble.

`devkit` est un méta-outil en Python qui résout ce problème. Il ne réimplémente rien : il **orchestre** ces outils derrière une interface unique, simple et cohérente. Quand l'utilisateur tape `devkit workflow ship`, devkit lance les tests, demande à Claude un message de commit, fait `git commit` et `git push`, demande à Claude une description de PR, puis appelle `gh pr create`. Six outils, une seule commande.

Le projet répond au brief « Modern CLI » dont l'objectif central est, selon ses propres mots, *"developing the instinct for composability"*.

---

## 2. Objectifs

Quatre objectifs principaux ont guidé la conception.

D'abord, **comprendre les CLI modernes** et leurs interfaces : ce qu'elles prennent en entrée, ce qu'elles retournent, comment elles peuvent être chaînées via leur sortie JSON.

Ensuite, **construire une couche d'orchestration en Python** qui appelle ces CLIs via le module `subprocess`, avec une gestion d'erreurs robuste (binaire absent, exit code non nul, stderr capturé).

Troisièmement, **intégrer trois IAs** comme des outils programmables, pas comme des chatbots : GitHub Copilot pour les commandes shell, Claude pour les tâches agentiques, Gemini comme alternative et fallback.

Enfin, **fournir une expérience utilisateur soignée** : couleurs et tables Rich pour l'humain, format JSON pour la machine, exit codes propres, messages d'erreur explicites.

Le livrable est un package Python installable via `pip install -e .` qui expose 27 commandes, accompagnées d'une suite de tests pytest et d'une documentation complète.

---

## 3. Architecture

`devkit` est organisé en quatre couches strictes, où chaque couche ne dépend que de la couche immédiatement inférieure. Cette discipline est ce qui permet à la suite de tests de tourner en moins d'une seconde.

```
┌─────────────────────────────────────────────────┐
│ Couche CLI       (main.py)                      │  Assemble les sub-apps Typer
├─────────────────────────────────────────────────┤
│ Couche Commands  (commands/*.py)                │  Logique métier de chaque commande
├─────────────────────────────────────────────────┤
│ Couche Utils     (utils/*.py)                   │  Wrappers subprocess, cache, AI runner
├─────────────────────────────────────────────────┤
│ Couche Persistence (config.py, utils/cache.py)  │  I/O JSON sur disque
└─────────────────────────────────────────────────┘
                       ↓
            Binaires externes (subprocess)
        gh, git, claude, gemini, fzf, pytest
```

Les **commands** déclarent ce que fait chaque commande utilisateur via Typer. Les **utils** contiennent les briques réutilisables : `shell.py` est le wrapper unique autour de `subprocess.run`, `gh.py` spécialise pour GitHub, `ai_runner.py` orchestre les trois backends IA, `cache.py` gère le cache disque des réponses, `check.py` détecte les binaires manquants. La **persistence** se réduit à deux fichiers JSON : `~/.devkit/config.json` pour les préférences utilisateur, `~/.devkit/cache/<sha256>.json` pour les réponses IA mises en cache.

Un module `plugins.py` permet aux utilisateurs d'étendre devkit en déposant simplement des fichiers Python dans `~/.devkit/plugins/` ou `~/.devkit/hooks/` — sans `pip install`.

### 3.1 Exemple de flux complet : `devkit workflow ship`

Pour rendre concrète la notion d'orchestration, voici le flux exact qui se déroule quand l'utilisateur tape `devkit workflow ship`. Cette commande "send-it" enchaîne six outils différents en une seule action.

```
devkit workflow ship
  │
  ├─→ [1] pytest -x --tb=short                 (échec → on s'arrête là)
  │
  ├─→ [2] git diff --staged                    (si vide → git add -u)
  │
  ├─→ [3] Claude (ou Gemini en fallback)
  │       prompt: "Write a conventional commit subject for: <diff>"
  │       réponse: "feat: add rate limiter"
  │
  ├─→ [4] hook pre_commit (optionnel)
  │       → exécute ~/.devkit/hooks/*.py si défini
  │
  ├─→ [5] git commit -m "<message IA>"
  │       git push -u origin <branch>
  │
  ├─→ [6] Claude (ou Gemini)
  │       prompt: "Write a 3-paragraph PR description for: <git log>"
  │       réponse: markdown structuré What/Why/How to test
  │
  ├─→ [7] gh pr create --title ... --body ...
  │
  └─→ [8] hook post_pr_open (optionnel)
          → notif Slack, ticket Jira, etc.
```

Sans devkit, cette séquence demanderait à l'utilisateur huit commandes manuelles, deux changements de contexte (terminal vers navigateur), et la rédaction manuelle du message de commit et de la description de PR. Avec devkit, c'est une seule commande qui dure environ 30 secondes, dont 25 sont les appels IA.

C'est exactement ce que le brief appelle l'instinct de composabilité : voir deux outils CLI et imaginer comment les chaîner.

---

## 4. Choix techniques

**Python + Typer + Rich.** Python pour la rapidité de prototypage et la richesse de l'écosystème CLI. Typer pour déduire les options depuis les annotations de type (3× moins verbeux qu'argparse). Rich pour les tables, panneaux et spinners qui donnent un look professionnel.

**Subprocess plutôt que SDK.** Tous les appels externes passent par `subprocess.run`, jamais par `PyGithub`, `anthropic` ou `google-generativeai`. Trois raisons : on réutilise l'authentification existante (`gh auth login` déjà fait), on garde zéro dépendance lourde (seules `typer` et `rich`), et on suit l'écosystème (quand `gh` ajoute une commande, devkit en bénéficie sans release).

**Trois IAs intégrées.** Le module `utils/ai_runner.py` traite les trois IAs comme des backends interchangeables. Trois lignes dans `_backend_args` font la différence :

```python
if model == "claude":  return ["claude", "--no-interactive", prompt]
if model == "gemini":  return ["gemini", prompt]
if model == "copilot": return ["gh", "copilot", "suggest", "--target", "shell", prompt]
```

Au-dessus, un **système de fallback** : si Claude est cassé ou absent, Gemini est essayé automatiquement. Au-dessus encore, un **cache disque** qui rend instantanées les requêtes répétées (clé SHA-256 du couple model+prompt, TTL 24h).

**Configuration JSON.** Quatre clés (`ai_tool`, `default_repo`, `theme`, `show_spinner`) dans `~/.devkit/config.json`. JSON est dans la stdlib, suffit largement, et la fonction `load_config()` merge toujours par-dessus les défauts, donc ajouter une clé future ne casse jamais une config existante.

### 4.1 Sécurité et confidentialité

Trois points méritent une attention particulière, et chacun a été tranché explicitement.

**Les tokens d'authentification.** `devkit` ne stocke ni ne manipule jamais de token GitHub ou de clé API IA. C'est `gh auth login` qui gère le token GitHub (stockage chiffré dans le keyring système), et c'est `claude` ou `gemini` qui gèrent leurs propres credentials. En déléguant aux outils en place, devkit hérite automatiquement de leur niveau de sécurité, sans introduire une nouvelle surface d'attaque.

**Le cache des réponses IA.** Les fichiers de `~/.devkit/cache/` contiennent en clair les prompts envoyés et les réponses reçues. Le dossier hérite des permissions du home utilisateur (700 par défaut sur Linux/macOS, accès utilisateur sur Windows). Pour un développeur sur sa machine personnelle, c'est l'équivalent d'un historique de conversation IA — pas plus sensible qu'un shell history. Pour un environnement multi-utilisateurs ou sensible, le cache peut être désactivé par requête via `--no-cache`, et purgé via `devkit cache clear`.

**Les plugins utilisateur.** Les fichiers déposés dans `~/.devkit/plugins/` sont du code Python exécuté avec les droits de l'utilisateur. C'est par nature un point d'extension privilégié, donc dangereux : un plugin malveillant a accès à tout ce que l'utilisateur peut faire. La responsabilité est explicitement à l'utilisateur, mentionnée dans la documentation, exactement comme pour les hooks Git ou les extensions de shell.

---

## 5. Cas d'usage concrets

Trois scénarios d'utilisation typiques illustrent la valeur pratique du projet.

**Scénario 1 — Le matin du développeur.** Le développeur arrive le matin, prend son café, et veut savoir ce qui l'attend. Sans devkit : ouvrir GitHub, naviguer dans "Review requests", puis "Issues assigned to me", puis le repo du projet pour voir les CI rouges. Trois onglets de navigateur, deux minutes. Avec devkit : `devkit workflow daily-digest`. Trois tables Rich en une commande, dix secondes. Le PDF appelle exactement ce type de gain *"the command that replaces three browser tabs"*.

**Scénario 2 — Avant un release.** Le développeur s'apprête à taguer une version `v2.0`. Il faut générer le CHANGELOG depuis le dernier tag. Sans devkit : `git log v1.0..HEAD --oneline`, copier dans un fichier, réécrire chaque ligne pour qu'elle soit lisible, regrouper par type (Added/Changed/Fixed). Vingt minutes. Avec devkit : `devkit ai changelog --since v1.0..HEAD`. Trente secondes. Le résultat suit le format Keep a Changelog, prêt à coller dans `CHANGELOG.md`.

**Scénario 3 — Pendant un debug.** Un collègue envoie une commande shell obscure du type `awk 'NR==FNR{a[$1]=$2;next} $1 in a{print $0,a[$1]}'`. Sans devkit : Google, Stack Overflow, lecture de la man page de `awk`. Cinq minutes au mieux. Avec devkit : `devkit ai explain "<commande>"`. Trois secondes, explication structurée dans un panneau coloré.

Ces trois scénarios illustrent les trois axes de valeur du projet : remplacer plusieurs outils par une commande (scénario 1), accélérer une tâche fastidieuse par l'IA (scénario 2), réduire le coût d'une recherche (scénario 3).

---

## 6. Implémentation par phase

### Phase 1 — Discovery

Fichier `discovery.md` qui décrit chaque outil moderne (rôle, observation surprenante, cas d'usage). La commande `devkit doctor` automatise cette phase : elle vérifie présence, version et authentification de chaque outil, et donne les commandes d'installation pour ce qui manque.

### Phase 2 — GitHub CLI

Cinq commandes dans `commands/github.py` : `issues`, `pr-summary`, `start-feature`, `open-pr`, `run-status`. Chacune utilise `gh ... --json` et rend le résultat en table Rich. L'option `-i` sur `issues` ajoute une sélection interactive via `fzf`.

### Phase 3 — AI CLI Tools

Quatre commandes dans `commands/ai.py` : `explain` et `suggest` utilisent Copilot exclusivement (sa spécialité), `review` et `commit` utilisent Claude par défaut (Gemini en alternative). Toutes appellent une vraie IA via subprocess et affichent la réponse dans un panneau Rich avec spinner pendant l'attente.

### Phase 4 — Orchestration

La commande flagship `devkit workflow feature-start <name> --issue N` enchaîne quatre actions : crée la branche `feature/<name>`, push, ouvre une PR draft, demande à l'IA un plan d'implémentation à partir du body de l'issue. Le tout est coordonné par `commands/workflow.py`.

### Phase 5 — Polish

Error handling centralisé dans `utils/check.py` (binaires manquants) et `utils/shell.py` (FileNotFoundError, CalledProcessError convertis en messages explicites). README de 231 lignes avec exemples. Les cinq commandes de la démo finale du brief (`gh issues`, `gh pr-summary`, `workflow feature-start`, `ai commit`, `ai explain`) fonctionnent.

### Fonctionnalités ajoutées au-delà du brief

Pour aller dans le sens de l'instinct de composabilité demandé par le brief : cache disque des réponses IA, fallback automatique multi-IA, système de plugins/hooks, commandes additionnelles (`ai changelog`, `ai test-gen`, `ai ask`, `gh search`, `gh stats`, `workflow daily-digest`, `workflow ship`).

---

## 7. Tests

49 tests pytest répartis sur 9 fichiers, exécutés en moins d'une seconde.

| Module testé | Tests | Couverture |
|---|---|---|
| `utils/shell.py` | 6 | 100% |
| `utils/check.py` | 4 | 100% |
| `config.py` | 5 | 100% |
| `utils/cache.py` | 9 | 92% |
| `plugins.py` | 6 | 95% |
| `utils/ai_runner.py` | 6 | 71% |
| `commands/ai.py` (helpers) | 7 | — |
| CLI smoke tests | 6 | — |

**Choix : tests unitaires plutôt qu'end-to-end.** Un test e2e devrait spawner un vrai `gh` et un vrai `claude`, ce qui demande des credentials et facture l'IA. À la place, chaque test mocke à la frontière `subprocess` via `monkeypatch.setattr`. Les modules critiques (shell, config, check) sont à 100% de couverture ; les modules `commands/*.py` sont à 12-43% par design — leur couverture passe par les smoke tests CLI qui vérifient juste que `--help` répond correctement pour chaque commande.

---

## 8. Difficultés rencontrées et solutions

Quatre problèmes concrets ont émergé pendant le développement et ont chacun guidé une décision de conception.

**Problème 1 — La latence des appels IA.** Un appel à `claude` ou `gemini` prend entre cinq et trente secondes. Pendant une démo ou un développement itératif, attendre quinze secondes à chaque fois qu'on relance la même commande devient intenable. **Solution :** un cache disque (`utils/cache.py`) qui mémorise les réponses indexées par `sha256(model + prompt)` avec un TTL de 24 heures. Une requête répétée passe de quinze secondes à environ cinq millisecondes.

**Problème 2 — L'absence d'une IA chez l'utilisateur.** Tous les utilisateurs n'ont pas installé Claude **et** Gemini **et** l'extension Copilot. Une commande qui échoue avec un message technique du genre `command not found: claude` n'est pas acceptable. **Solution :** une chaîne de fallback automatique dans `utils/ai_runner.py`. Si le backend préféré est absent ou plante, le runner essaye le suivant transparently. L'utilisateur voit dans la sortie quel backend a effectivement répondu via le champ `result.model`.

**Problème 3 — Les limites de longueur de ligne de commande Windows.** Passer un diff complet à `claude` ou `gemini` en argument positionnel échoue silencieusement sur Windows cmd.exe au-delà d'environ 8000 caractères, et même sur les shells POSIX certains diffs très longs produisent des réponses dégradées. **Solution :** une fonction `truncate_prompt(prompt, limit=6000)` qui coupe au seuil et ajoute un marqueur explicite `[truncated N chars]`. La troncature est appliquée systématiquement avant chaque appel.

**Problème 4 — Les sorties non-déterministes des IAs.** Les modèles génératifs ne donnent jamais exactement la même réponse, ce qui rend impossible un test unitaire qui vérifie le contenu exact d'une review IA. **Solution :** ne jamais tester le contenu IA. À la place, mocker le binaire entier via `monkeypatch.setattr(ai_runner, "_call_one", fake)` et tester uniquement la logique d'orchestration (fallback, cache, format de sortie). Cette discipline a permis d'avoir 49 tests fiables qui passent en moins d'une seconde.

Ces quatre problèmes ne sont pas anecdotiques : ils ont littéralement façonné la structure des modules `cache.py`, `ai_runner.py`, et la stratégie de tests entière.

---

## 9. Limites actuelles et perspectives d'évolution

Le projet est fonctionnel et couvre l'intégralité du brief, mais plusieurs axes d'amélioration restent ouverts.

**Pas de streaming des réponses IA.** Actuellement, quand l'utilisateur lance `devkit ai review 42`, il voit un spinner pendant 20 secondes puis la réponse complète d'un coup. Une amélioration consisterait à utiliser le composant `Live` de Rich combiné aux modes streaming de Claude/Gemini pour afficher la réponse token par token. L'expérience perçue serait nettement meilleure même si la latence totale ne change pas.

**Le `daily-digest` est séquentiel.** La commande fait trois appels `gh search` l'un après l'autre, ce qui prend environ 6 secondes. Avec `asyncio.create_subprocess_exec` et `asyncio.gather`, les trois requêtes pourraient être lancées en parallèle pour ramener le temps total à environ 2 secondes.

**Pas d'interface TUI live.** Pour un usage répété, une vraie interface texte à la Textual (refresh toutes les 30 secondes, navigation clavier) serait un cran au-dessus. C'est cependant un projet d'une autre ampleur — il s'agirait plutôt d'une commande `devkit dashboard` séparée.

**Pas d'auto-installation de hooks Git.** Une commande `devkit init-hooks` pourrait installer un hook Git `pre-commit` qui bloque le commit si les tests échouent, et un `pre-push` qui vérifie le formatage du code. Cela rapprocherait devkit d'outils comme `pre-commit.com` mais en restant Python-natif.

**Pas de génération MCP server.** L'écosystème MCP (Model Context Protocol) permet à Claude Desktop ou Cursor d'invoquer des outils externes. Une commande `devkit serve-mcp` qui exposerait toutes les commandes Typer comme des outils MCP rendrait devkit utilisable depuis ces interfaces graphiques. C'est l'évolution la plus ambitieuse de la liste et probablement la plus impactante.

**Pas de télémétrie.** Sans données d'usage réel, le développement futur est piloté par l'intuition. Une télémétrie opt-in qui mesure simplement quelles commandes sont invoquées (sans les arguments) permettrait de prioriser empiriquement.

Toutes ces évolutions sont des extensions de l'architecture existante, pas des refontes. C'est précisément ce qu'une bonne architecture en couches permet.

---

## 10. Démonstration prévue (15 minutes)

La démo se déroule en sept actes calibrés pour le créneau imparti.

1. **La porte d'entrée** (1 min) — `devkit doctor` en premier, le tableau visuel qui impressionne.
2. **Phase 2 — GitHub** (2 min) — `gh issues`, `pr-summary`, `run-status`, `search`, `stats` sur un repo de démo préparé.
3. **Phase 3 — Les 3 IAs** (3 min) — `ai explain` et `ai suggest` (Copilot), puis `ai ask` deux fois pour montrer le cache, puis `ai commit` sur un staged diff.
4. **Phase 4 — Workflow** (2 min) — `workflow daily-digest`, `feature-start --issue`, `ship`.
5. **Bonus — Config & cache** (1 min) — manipulation de `~/.devkit/config.json` et `cache info`.
6. **Tests** (30 sec) — `pytest -v`, les 49 tests qui passent en <1 sec.
7. **Code walkthrough** (2 min) — ouvrir `utils/ai_runner.py` pour montrer les 3 IAs en 3 lignes, puis le diagramme dans `ARCHITECTURE.md`.

Reste 3 minutes de marge pour absorber un incident technique ou des questions intermédiaires.

---

## 11. Préparation Q&A (10 minutes)

Quelques questions probables et leurs réponses préparées :

**« Pourquoi `subprocess` plutôt qu'une SDK Python ? »**
Pour réutiliser l'authentification `gh` existante, garder zéro dépendance lourde, et suivre automatiquement les évolutions de l'écosystème. Le coût (~100ms par appel) est imperceptible pour un outil interactif.

**« Comment ajouter une 4ème IA ? »**
Cinq lignes dans `utils/ai_runner.py` : ajouter le nom dans `SUPPORTED_MODELS`, ajouter une branche dans `_backend_args`, mettre à jour `_ALLOWED_AI_TOOLS`. Toutes les commandes existantes acceptent immédiatement `--model <nouveau>`.

**« Pourquoi pas de tests end-to-end ? »**
Ils auraient demandé des credentials, du réseau et des frais d'API. Les 49 tests unitaires mockent à la frontière subprocess et tournent en <1 sec, ce qui permet de les relancer après chaque modification.

**« Le cache stocke en clair sur disque, problème de sécurité ? »**
Le cache vit dans `~/.devkit/cache/` qui hérite des permissions du home utilisateur. Pour un développeur sur sa machine, équivalent à un historique de conversation IA. Pour un environnement sensible, on désactive avec `--no-cache`.

**« Comment ça s'adapte à une équipe de 50 développeurs ? »**
Trois adaptations : publier sur un PyPI privé, packager les conventions équipe sous forme d'un plugin `~/.devkit/plugins/<entreprise>.py`, et ajouter une télémétrie opt-in pour mesurer les usages réels.

---

## 12. Conclusion

Le projet a été livré dans le respect intégral du cahier des charges : les cinq phases sont implémentées, les cinq commandes de la démo finale fonctionnent, la grille de notation à 100 points est entièrement adressée. En complément, neuf fonctionnalités ont été ajoutées dans l'esprit de la conclusion du brief — l'instinct de composabilité.

En chiffres : 2347 lignes de Python, 18 modules source, 27 commandes utilisateur, 49 tests qui s'exécutent en moins d'une seconde, deux dépendances Python directes seulement.

La leçon centrale du projet : un méta-outil bien conçu n'invente rien, il oriente. `devkit` ne réécrit ni Git, ni GitHub, ni les IAs. Il les met en mouvement ensemble derrière une seule commande utilisateur. C'est exactement ce que le brief appelle l'instinct de composabilité, et c'est ce qui distingue, comme il le dit en conclusion, *"a developer from a craftsperson"*.
