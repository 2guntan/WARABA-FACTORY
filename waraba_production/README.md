# WARABA AI Pipeline

**Système de production vidéo assisté par IA**  
**WARABA-DIRECTOR + JoyAI-Echo**

Un pipeline professionnel pour générer des épisodes vidéo longs (fables animées) avec un fort contrôle narratif, une cohérence de personnages et une direction artistique.

---

## 🎯 Objectif

Créer un système hybride où :
- L’humain garde le contrôle créatif et la direction (via WARABA-DIRECTOR)
- L’IA génère efficacement les vidéos (via JoyAI-Echo)
- Les personnages restent cohérents grâce à un outil dédié

---

## 📁 Structure du projet

```
warabaproduction/
├── README.md
├── docs/
│   └── WARABA-DIRECTOR_JoyAI-Echo_Technical_Specification.md
├── tools/
│   ├── character_definition/
│   │   └── CharacterProfile_Schema.json
│   └── prompt_assembler/
│       ├── prompt_assembler.py
│       └── prompt_assembler_v2_with_episode01.py
├── deployment/
│   └── runpod/
│       ├── runpod_fastapi_skeleton.py
│       ├── Dockerfile
│       └── requirements.txt
├── data/
│   └── episode_01_shots.json
└── archive/
    └── WARABA-DIRECTOR_JoyAI-Echo_Project_Package.zip
```

---

## 🚀 Composants principaux

| Composant                    | Rôle                                      | Technologie          |
|-----------------------------|-------------------------------------------|----------------------|
| **Character Definition**    | Générer des profils personnages structurés | Google Flow + JSON   |
| **Prompt Assembler**        | Transformer storyboard + personnages en prompts JoyAI-Echo | Python               |
| **RunPod Orchestrator**     | API FastAPI pour gérer les générations     | FastAPI + Docker     |
| **JoyAI-Echo**              | Génération vidéo + audio long format       | Sur RunPod (H100)    |
| **WARABA-DIRECTOR**         | Direction artistique et storyboard         | Google Drive         |

---

## 🛠️ Installation & Déploiement (RunPod)

1. Clone ce dépôt
2. Va dans `deployment/runpod/`
3. Build l’image Docker :
   ```bash
   docker build -t waraba-joyai-echo .
   ```
4. Déploie sur RunPod avec le Dockerfile fourni

---

## 📌 Prochaines étapes

- Implémenter l’orchestration complète sur RunPod
- Connecter le Character Tool avec le Prompt Assembler
- Intégrer les vrais shots de l’Episode 01
- Ajouter le support des jobs asynchrones et du stockage des résultats

---

## 📄 Documentation

Consulte le fichier :
- [Technical Specification](docs/WARABA-DIRECTOR_JoyAI-Echo_Technical_Specification.md)

---

**Projet en cours de développement** — Structure et outils de base prêts à être étendus.