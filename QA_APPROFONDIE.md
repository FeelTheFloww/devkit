# 🧠 Q&A APPROFONDIE — Questions techniques probables

## ARCHITECTURE & DESIGN

### Q: "Pourquoi cette architecture en 4 couches ?"
**R:** *"Séparation des responsabilités : CLI (parsing args) → Commands (logique métier) → Utils (orchestration outils) → Persistance (disque/réseau). Chaque couche peut être testée isolément sans Typer. C'est la pyramide de test: tests unitaires sur utils, smoke tests sur CLI."*

### Q: "Vous avez envisagé une autre archi ?"
**R:** *"Oui, monolithique (tout dans une fonction). Ça n'aurait pas échellé avec 6 commandes + plugins. L'architecture 4 couches permet l'extensibilité : ajouter une commande = ajouter un fichier dans commands/, elle se branche auto sur le Typer root app."*

### Q: "Comment vous garantissez que rien n'importe 'vers le haut' (utils → commands) ?"
**R:** *"Code review. Dans le brief, j'aurais pu mettre une règle mypy/pylint, mais c'est manuel. En production réelle, des PRs checks."*

---

## TYPER & CLI

### Q: "Pourquoi Typer plutôt que Click/argparse ?"

| Feature | argparse | Click | **Typer** |
|---------|----------|-------|-----------|
| Verbosité | ✗ Très haut | ~ | ✓ Bas |
| Type hints natifs | ✗ Non | ✗ Non | ✓ Oui |
| Sub-apps composables | ~ (lourd) | ✓ | ✓ |
| Rich integration | ✗ | ✗ | ✓ Built-in |
| Auto-completion | ~ | ✓ | ✓ |
| Pydantic validation | ✗ | ✗ | ✓ (implicit) |

**R:** *"Typer = Click + Pydantic. Une commande est juste une fonction typée Python. Typer génère `--help`, validation, sub-apps. Moins de boilerplate qu'argparse, plus moderne que Click."*

### Q: "Comment ça marche, une sub-app Typer ?"
**R:** *"Chaque module (github.py, ai.py, etc.) a sa propre `app = typer.Typer()`. Dans main.py, on fait `app.add_typer(github.app, name='gh')`. Ça monte la sub-app sous `devkit gh *`. Aucune dépendance circulaire si architecture propre."*

### Q: "Et les commandes dynamiques (plugins) ?"
**R:** *"plugins.py importe les fichiers dans ~/.devkit/plugins/. Chacun peut appeler `register_command(app, ...)` pour s'ajouter. On l'appelle au startup de main.py. C'est extensibilité sans fork."*

---

## SUBPROCESS & OUTILS EXTERNES

### Q: "Vous appelez 'gh' comment exactement ?"
**R:** 
```python
import subprocess
result = subprocess.run(
    ['gh', 'issue', 'list', '--repo', 'cli/cli', '--json', 'number,title,state'],
    capture_output=True,
    text=True,
    check=True
)
data = json.loads(result.stdout)
```
*On lève la requête, on capture stdout (JSON), on parse. check=True → exception si gh échoue.*

### Q: "Et si 'gh' n'est pas installé ?"
**R:** *"subprocess.run() lève FileNotFoundError ou CalledProcessError. On catch ça dans utils/shell.py, on affiche une erreur lisible, et on retourne un code non-zero. devkit doctor détecte aussi l'absence via 'which gh'."*

### Q: "Comment vous gérér les erreurs de subprocess ?"
**R:** 
```python
def run_command(cmd, check=True):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return result
    except FileNotFoundError:
        console.print(f"[red]Error: {cmd[0]} not found. Install it first.[/red]")
        raise typer.Exit(1)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]{cmd[0]} failed with: {e.stderr}[/red]")
        raise typer.Exit(1)
```

### Q: "Pourquoi pas utiliser PyGithub SDK ?"
**R:** 
1. **Authentification** : PyGithub demande un token. `gh` est déjà authentifié sur la machine → zéro config.
2. **Dépendances** : PyGithub = ~50MB. On veut juste Typer + Rich (~1MB).
3. **Composabilité** : Quand GitHub ajoute une fonctionnalité à `gh`, PyGithub doit être mis à jour. Nous, on la réutilise directement.

### Q: "Et si 'gh' ajoute un flag que vous n'aviez pas prévu ?"
**R:** *"L'utilisateur peut passer des flags perso via `--extra-flags "..."` ou on laisse la possibilité de passer au subprocess direct. Ou: l'utilisateur fork et ajoute. C'est très flexible."*

---

## AI & CACHE

### Q: "Comment vous appelez Claude ?"
**R:** 
```python
result = subprocess.run(
    ['claude', '-m', 'claude-3-5-sonnet'],
    input=prompt_text,
    capture_output=True,
    text=True
)
response = result.stdout
```
*`claude` CLI (officielle) lit stdin, traite, output résultat.*

### Q: "Et si Claude n'est pas sur PATH ?"
**R:** *"check.py teste 'which claude'. Si absent, `devkit doctor` le signale rouge. `ai review` lève error. fallback: on essaie Gemini à la place (si installé). Sinon: error."*

### Q: "Comment le cache fonctionne ?"
**R:** 
```python
# cache.py
cache_key = hashlib.sha256(prompt.encode()).hexdigest()
cache_file = Path.home() / ".devkit" / "cache" / f"{cache_key}.json"

if cache_file.exists():
    return json.loads(cache_file.read_text())  # ← réutilise
else:
    response = subprocess.run(['claude', ...], ...)  # ← appelle
    cache_file.write_text(json.dumps({"response": response}))
    return response
```

### Q: "Et si le fichier cache est corrompu ?"
**R:** *"Try/except JSON decode. Si corrompu, on relog l'erreur, on ignore le cache, on réappelle Claude. Cache best-effort: si absent ou bad, on fallback API."*

### Q: "Pourquoi pas un vrai cache type Redis ?"
**R:** *"Brief: CLI local. Pas de serveur. Disque est suffisant pour une machine. Redis = overkill et dépendance externe."*

### Q: "Les réponses IA sont-elles stockées pour toujours ?"
**R:** *"Disque local. `devkit cache clear` vide. L'utilisateur contrôle. Pas d'upload externe. Tokens (ANTHROPIC_API_KEY, GOOGLE_API_KEY) restent en env var — jamais écrit en cache."*

---

## TYPE HINTS & TESTING

### Q: "Vous utilisez des type hints partout ?"
**R:** *"Oui. `from __future__ import annotations` en tête de chaque fichier. Ça permet les type hints avec classes non encore définies. Exemple: une fonction retourne None au lieu de 'Optional[None]'."*

### Q: "Vous lancez mypy ?"
**R:** *"Pas dans le brief, mais c'est bonne pratique. Je l'aurais fait en prod. Pour cette démo: `pytest` suffit."*

### Q: "Combien de tests ? Coverage ?"
**R:** *"27 tests. Coverage ~70% (les tests concernent surtout utils et config, pas tout le CLI est couvert de façon granulaire). Je peux le mesurer avec `pytest --cov=devkit`."*

### Q: "Vous mockez les appels subprocess ?"
**R:** 
```python
# tests/test_shell.py
@patch('subprocess.run')
def test_gh_issues(mock_run):
    mock_run.return_value = MagicMock(
        stdout='[{"number": 1, "title": "Bug"}]'
    )
    result = gh_issues(limit=1)
    assert len(result) == 1
```
*On mock subprocess.run, on vérifie que la commande est appelée correctement.*

---

## CONFIG & PERSISTENCE

### Q: "Où vit la config ?"
**R:** *"~/.devkit/config.json. Format JSON. Champs: ai_tool (claude/gemini), default_repo, theme, show_spinner. load_config() le lit au startup, applique defaults si fichier absent."*

### Q: "Et si l'utilisateur edite le JSON à la main ?"
**R:** *"On parse, ça doit être du JSON valide. Si invalid, on log un warning, on utilise defaults. Robustesse."*

### Q: "Vous versionnez la config ?"
**R:** *"Non. config.json est local, pas en Git. .gitignore l'exclut. Chaque machine a la sienne."*

---

## PLUGINS & EXTENSIBILITÉ

### Q: "Comment ça marche, les plugins ?"
**R:** 
```python
# plugins.py
for plugin_file in (Path.home() / ".devkit" / "plugins").glob("*.py"):
    spec = importlib.util.spec_from_file_location(
        plugin_file.stem, plugin_file
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Module peut avoir appelé register_command(app, ...)
```
*On importe tous les .py du dossier plugins. Chacun peut appeler register_command pour ajouter une commande.*

### Q: "Un utilisateur peut modifier devkit sans fork ?"
**R:** *"Exactement. Ses plugins vivent dans ~/.devkit/plugins/. Il peut ajouter ses commandes, hooks, sans toucher au code de devkit. C'est extensibilité low-friction."*

---

## WORKFLOWS & ORCHESTRATION

### Q: "Workflow feature-start: qu'est-ce qu'il fait exactement ?"
**R:** 
```
1. git checkout -b feature-nom
2. git push -u origin feature-nom
3. gh pr create --draft --title "WIP: feature-nom"
4. devkit ai ask "plan for a feature called 'nom'"
5. Display output
```
*Orchestration multi-outil: git, gh, Claude. Chacun fait sa part.*

### Q: "Et si un outil échoue au milieu ?"
**R:** *"On s'arrête et on affiche l'erreur. L'utilisateur voit exactement où ça a cassé. Pas de rollback automatique — on laisse ça à l'utilisateur (delete la branche manu si besoin)."*

### Q: "Comment vous gérez l'ordre des étapes ?"
**R:** *"Code linéaire dans workflow.py: étape 1 → 2 → 3. Si étape i échoue, exception, on sort. Simple et prévisible. Pas de DAG complexe (overkill pour ce brief)."*

---

## WINDOWS VS LINUX/MAC

### Q: "Ça marche sur Windows ?"
**R:** *"Oui. J'ai développé sur Windows. subprocess est portable. gh, git, Claude CLI existent sur Windows. Seul détail: paths (/ vs \), mais pathlib l'abstraite."*

### Q: "Les chemins absolus genre /home/user/.devkit/ ?"
**R:** *"Je uses Path.home() / ".devkit" / "config.json". pathlib l'abstraite pour chaque OS. Cross-platform."*

---

## PERFORMANCE

### Q: "C'est pas lent, d'appeler subprocess partout ?"
**R:** *"Chaque commande = une requête subprocess. C'est aussi rapide que l'outil sous-jacent. gh peut prendre 500ms, Claude 2-3s. C'est pas lent pour une CLI. Cache accélère réutilisations."*

### Q: "Vous avez mesuré ?"
**R:** *"Pas le scope du brief, mais on peut faire `time devkit gh issues ...` et comparer `time gh issue list ...` — c'est équivalent."*

---

## SÉCURITÉ

### Q: "Les tokens sont safe ?"
**R:** 
- Claude token: `ANTHROPIC_API_KEY` en env var. Jamais écrit en config.
- GitHub: `gh auth` gère ça, devkit n'y touche pas.
- Gemini: `GOOGLE_API_KEY` en env var.
- Cache: fichiers locaux, pas d'upload.

### Q: "Un utilisateur malveillant peut voir les tokens dans le cache ?"
**R:** *"Cache ne contient que les RÉPONSES (texte IA). Les tokens ne passent jamais par le cache — c'est des env vars. Mais oui, un utilisateur local peut lire ~/.devkit/cache/. C'est un système mono-utilisateur (ton PC), c'est acceptable."*

---

## BRIEF & GRILLE DE NOTATION

### Q: "Comment vous adressez chaque phase du brief ?"

| Phase | Critère | Vous |
|-------|---------|------|
| 1 | Analyser 10 CLI modernes | ARCHITECTURE.md + découverte |
| 2 | 6 commands + JSON + Rich table | `gh issues`, `pr-summary`, etc. |
| 3 | ≥3 IA backends | Claude, Gemini, GitHub Copilot (explainer) |
| 4 | ≥1 workflow multi-outils | `feature-start` orchestre git + gh + Claude |
| 5 | Error handling + graceful fallback | `devkit doctor` + fallback Gemini → Claude |
| 6 | Code quality (type hints, tests, structure) | Typer, 27 pytest, 4 couches |
| 7 | Documentation | README + ARCHITECTURE + PROTOCOLE_DEMO |
| 8 | Composabilité (pas de réinvention) | subprocess + `gh --json` partout |

*Vous couvrez 100% du brief.*

---

## QUESTIONS PIÈGES

### Q: "Vous vous connectez à l'API GitHub REST directement ?"
**R:** *"Non. On passe par `gh` CLI qui gère l'API. Avantage: l'user's auth dans `gh` — pas de token manipulation. On retourne --json et on parse."*

### Q: "Vous stockez les réponses IA en base de données ?"
**R:** *"Non. Disque local JSON (~/.devkit/cache/). Pas de serveur, pas de DB. Simple et portable."*

### Q: "Vous loggez les erreurs ?"
**R:** *"Console.print([red]error[/red]) en stderr. Pas de fichier log (hors scope brief). Utilisateur voit l'erreur immédiatement."*

### Q: "Comment vous testez Claude integration sans vraiment l'appeler ?"
**R:** *"Mock subprocess.run. On simule la réponse, on vérifie que le parsing fonctionne. En prod, les tests real sont perso à cause de tokens."*

---

## NE PAS DIRE...

❌ *"On utilise PyGithub"* → `gh` CLI, pas SDK  
❌ *"Pas de tests"* → 27 tests pytest  
❌ *"Code non-typé"* → Tout typé (from __future__ import annotations)  
❌ *"Architecture maison innovante"* → Non, patterns reconnus (4 couches)  
❌ *"On stocke les tokens"* → Non, env vars + gh auth  
❌ *"Ça marche que sur Linux"* → Cross-platform (Windows tested)  
❌ *"On n'adresse pas le brief"* → Oui, 100% couvert  

---

## À DIRE...

✅ *"subprocess plutôt que SDK — zéro dépendance, réutilisation d'outils existants"*  
✅ *"Composabilité: outils réutilisés vs réinventés"*  
✅ *"4 couches architecture: CLI → Commands → Utils → Persistence"*  
✅ *"Type hints partout, 27 tests, code propre"*  
✅ *"Plugins: extensibilité user sans fork"*  
✅ *"Cache IA: accélère runs futures"*  
✅ *"Erreur handling + graceful fallback"*  

---

## RÉPONSE PAR DÉFAUT (Si tu séches)

> *"C'est une excellente question. Le brief nous demande de montrer l'instinct de composabilité — réutiliser `gh`, Claude, Gemini, Git via subprocess plutôt que réinventer avec des SDK. Ça c'est exactement ce qu'on fait ici. La question soulève [le détail spécifique] — c'est un bon point pour la prod, mais pour cette démo ça n'affecte pas le core."*

