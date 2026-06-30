# WARABA AI Pipeline

**Pipeline de production vidéo IA pour fables animées**  
WARABA-DIRECTOR + JoyAI-Echo sur RunPod

---

## Structure

```
waraba_production/
├── characters/
│   ├── schema/CharacterProfile_Schema.json   ← JSON Schema des profils
│   ├── leuk_v1.json                          ← à créer
│   └── gainde_v1.json                        ← à créer
├── episodes/
│   └── episode_01/
│       ├── shots.json                        ← storyboard complet
│       └── prompts/                          ← output du prompt assembler
├── tools/
│   ├── prompt_assembler.py                   ← CLI : character + shots → prompts
│   └── api_server.py                         ← FastAPI RunPod orchestrator
├── deployment/
│   └── Dockerfile                            ← image CUDA 12.8 + JoyAI-Echo
├── docs/
│   └── WARABA-DIRECTOR_JoyAI-Echo_Technical_Specification.md
└── archive/                                  ← fichiers de référence archivés
```

---

## Composants

| Composant | Rôle | État |
|-----------|------|------|
| `characters/schema/` | Définition JSON des personnages | ✅ |
| `characters/*.json` | Profils réels (Leuk, Gaïndé…) | ⚠️ à créer |
| `episodes/episode_01/shots.json` | Storyboard Episode 01 (7/19 shots) | ⚠️ incomplet |
| `tools/prompt_assembler.py` | Assemble prompts JoyAI-Echo | ✅ |
| `tools/api_server.py` | FastAPI orchestrateur RunPod | ⚠️ skeleton |
| `deployment/Dockerfile` | Image GPU CUDA 12.8 | ⚠️ JoyAI-Echo non pinned |

---

## Usage — Prompt Assembler

```bash
python tools/prompt_assembler.py \
  --character characters/leuk_v1.json \
  --shots episodes/episode_01/shots.json \
  --output episodes/episode_01/prompts/leuk_prompts.json
```

---

## Prochaines étapes

1. Créer `characters/leuk_v1.json` et `gainde_v1.json`
2. Compléter `episodes/episode_01/shots.json` (shots SH003–SH018 manquants)
3. Intégrer JoyAI-Echo dans `tools/api_server.py` (`process_generation`)
4. Remplacer stockage mémoire par Redis ou fichiers sur Network Volume
5. Pinner version JoyAI-Echo dans Dockerfile

---

Doc complète → [docs/WARABA-DIRECTOR_JoyAI-Echo_Technical_Specification.md](docs/WARABA-DIRECTOR_JoyAI-Echo_Technical_Specification.md)
