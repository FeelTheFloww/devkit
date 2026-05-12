# 📚 GUIDE DE LECTURE — COMMENT SE PRÉPARER

## Pour une préparation en 1 heure

### ⚡ 5 MIN : Lisez FICHE_REVISION.md
**Objectif:** Retenir les points clés pour ne pas être perdu

### 📊 15 MIN : Lisez SYNTHESE_PRESENTATION.md
**Objectif:** Comprendre l'architecture + le pitch + la démo

### 📋 20 MIN : Lisez PROTOCOLE_DEMO.md (sections 0 et 1)
**Objectif:** Savoir comment configurer et lancer la démo

### 🆘 15 MIN : Lisez QA_APPROFONDIE.md (sections architecture + subprocess)
**Objectif:** Comprendre les réponses aux questions techniques

### ✅ 5 MIN : Relisez FICHE_REVISION.md
**Objectif:** Consolider avant de partir

---

## Pour une préparation rapide (15 min avant la démo)

1. **FICHE_REVISION.md** — 5 min
2. **PREP_DEMO.md** — 10 min (checklist + troubleshooting)

---

## Pour chaque section de la démo

### Si tu dois parler d'ARCHITECTURE
- Lis: SYNTHESE_PRESENTATION.md → section 🏗️ ARCHITECTURE
- Lis: ARCHITECTURE.md (original) → sections 1-2
- Mémorise: "4 couches : CLI → Commands → Utils → External"

### Si tu dois parler de COMMANDES GITHUB
- Lis: PROTOCOLE_DEMO.md → section 3 (Acte 2)
- Exécute: `devkit gh issues --repo cli/cli --limit 5`
- Clé: "subprocess + gh --json + parsing + Rich table"

### Si tu dois parler d'IA
- Lis: SYNTHESE_PRESENTATION.md → section 🎯 (Acte 3)
- Lis: QA_APPROFONDIE.md → section "AI & CACHE"
- Exécute: `devkit ai ask "..."`
- Clé: "Claude/Gemini CLI appelés via subprocess"

### Si tu dois parler de WORKFLOWS
- Lis: PROTOCOLE_DEMO.md → section 4 (Acte 4)
- Exécute: `devkit workflow feature-start test --repo cli/cli`
- Clé: "Orchestration multi-outils: git + gh + Claude"

### Si tu dois parler de CONFIG/CACHE
- Lis: SYNTHESE_PRESENTATION.md → section 📂 OÙ TROUVER QUOI
- Exécute: `devkit config show` et `devkit cache info`
- Clé: "JSON disque local, zéro serveur"

### Si tu dois parler de CODE QUALITY
- Lis: QA_APPROFONDIE.md → section "TYPE HINTS & TESTING"
- Exécute: `pytest -v`
- Clé: "27 tests pytest, type hints partout, 4 couches"

---

## Questions & Réponses rapides

### Architecture
**Fichier:** QA_APPROFONDIE.md → section "ARCHITECTURE & DESIGN"

### Typer/CLI
**Fichier:** QA_APPROFONDIE.md → section "TYPER & CLI"

### subprocess & outils externes
**Fichier:** QA_APPROFONDIE.md → section "SUBPROCESS & OUTILS EXTERNES"

### AI & Cache
**Fichier:** QA_APPROFONDIE.md → section "AI & CACHE"

### Type hints & Tests
**Fichier:** QA_APPROFONDIE.md → section "TYPE HINTS & TESTING"

### Plugins & Extensibilité
**Fichier:** QA_APPROFONDIE.md → section "PLUGINS & EXTENSIBILITÉ"

### Brief & Notation
**Fichier:** QA_APPROFONDIE.md → section "BRIEF & GRILLE DE NOTATION"

---

## Fichiers du projet (originaux)

Si tu veux aller plus loin :

| Fichier | Contenu | Quand |
|---------|---------|-------|
| **README.md** | Quick start, commands table | Reference |
| **ARCHITECTURE.md** | Design approfondi, diagrammes | Prépa détaillée |
| **PROTOCOLE_DEMO.md** | Demo step-by-step | Pendant la démo |
| **CHANGELOG.md** | Features par version | Optionnel |
| **COMPTE_RENDU.md** | Notes de projet | Optionnel |
| **pyproject.toml** | Dependencies, build config | Reference |
| **src/devkit/main.py** | Typer app root | See architecture |
| **src/devkit/commands/github.py** | Example commande | Code review |
| **src/devkit/utils/shell.py** | subprocess wrapper | Code review |
| **tests/** | 27 pytest | Pour montrer coverage |

---

## CHECKLIST DE RÉVISION

### Concepts architecturaux
- [ ] Comprendre les 4 couches (CLI → Commands → Utils → External)
- [ ] Savoir pourquoi subprocess plutôt que SDK
- [ ] Connaître les 6 sous-commandes
- [ ] Connaître les techno stack (Typer, Rich, subprocess, pytest)

### Démo pratique
- [ ] Savoir lancer `devkit doctor`
- [ ] Savoir lancer `devkit gh issues --repo cli/cli`
- [ ] Savoir lancer `devkit ai review <numéro_PR>`
- [ ] Savoir lancer `devkit workflow feature-start <nom>`
- [ ] Savoir lancer `pytest -v`

### Q&A
- [ ] Réponse: "Pourquoi subprocess ?"
- [ ] Réponse: "Et si gh manque ?"
- [ ] Réponse: "Comment le cache fonctionne ?"
- [ ] Réponse: "Comment testez vous subprocess ?"
- [ ] Réponse: "Vous couvrez le brief ?"

### Préparation pré-démo
- [ ] Terminal configuré (14-16pt)
- [ ] `devkit doctor` OK
- [ ] Cache pré-chauffé (`devkit ai ask ... × 2`)
- [ ] README.md staged pour `ai commit`

---

## RÉSUMÉ ULTRA-COURT (À DIRE EN 30 SEC)

*"devkit orchestre les outils modernes (GitHub CLI, Claude, Gemini, Git) via subprocess. Zéro SDK, zéro dépendance lourde. Architecture 4 couches : CLI → Commands → Utils → External. Type hints partout, 27 tests pytest, plugins extensibles. C'est de la composabilité pure."*

---

## SI TU N'AS QUE 5 MIN

1. Lis FICHE_REVISION.md
2. Ouvre PREP_DEMO.md → section CHECKLIST
3. Lances les commandes dans "Environnement"
4. Exécutes les commandes de test
5. T'es prêt ✅

---

## SI TU AS 30 MIN

1. Lis SYNTHESE_PRESENTATION.md en entier
2. Lis PROTOCOLE_DEMO.md → section "Plan global de la démo"
3. Exécutes les 6 commandes d'exemple
4. Lis QA_APPROFONDIE.md → première moitié
5. Relire FICHE_REVISION.md

---

## SI TU AS 1H+

1. Lis tous les fichiers de synthèse (ordre: FICHE → SYNTHESE → PROTOCOLE → PREP → QA)
2. Lis ARCHITECTURE.md en entier
3. Ouvre le code source et parcours:
   - src/devkit/main.py
   - src/devkit/commands/github.py
   - src/devkit/utils/shell.py
4. Lance `pytest -v` et lis les tests
5. Exécutes manuellement chaque commande
6. Prépares tes 3 questions pièges possibles

---

## ORDRE DE LECTURE RECOMMANDÉ

```
1. FICHE_REVISION.md                    ← Orientation (5 min)
2. SYNTHESE_PRESENTATION.md             ← Deep dive (20 min)
3. PROTOCOLE_DEMO.md                    ← Practice (15 min)
4. PREP_DEMO.md                         ← Checklist (10 min)
5. QA_APPROFONDIE.md                    ← Master class (30 min)
6. (Optionnel) ARCHITECTURE.md original ← Expert mode (20 min)
7. (Optionnel) Code source              ← Deep expert (30+ min)
```

---

## FICHIERS CRÉÉS POUR VOUS

📄 **SYNTHESE_PRESENTATION.md** — Architecture + pitch + script complet  
📄 **PREP_DEMO.md** — Checklist + timing + troubleshooting  
📄 **QA_APPROFONDIE.md** — Réponses techniques détaillées  
📄 **FICHE_REVISION.md** — Synthèse 5 min  
📄 **GUIDE_DE_LECTURE.md** (ce fichier) — Navigation  

---

## MAINTENANT

✅ Vous avez une feuille de route complète  
✅ Vous connaissez les 15 min de démo  
✅ Vous avez les 10 min de Q&A couverts  
✅ Vous avez les réponses aux questions techniques  
✅ Vous avez une checklist pré-démo  

**C'est parti !** 🚀

