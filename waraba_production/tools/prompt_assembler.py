#!/usr/bin/env python3
"""
Prompt Assembler — WARABA-DIRECTOR + JoyAI-Echo

Merges CharacterProfile JSON + shot list into JoyAI-Echo prompts.

Usage:
    python prompt_assembler.py --character characters/leuk_v1.json \
                               --shots episodes/episode_01/shots.json \
                               --output episodes/episode_01/prompts/leuk_prompts.json
"""

import json
import argparse
from typing import Dict, List, Any


def load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_character_description(character: Dict[str, Any]) -> str:
    parts = []
    parts.append(f"{character.get('name', 'Character')}, a {character.get('age_appearance', '')} {character.get('species', '')}.")
    if character.get('physical_description'):
        parts.append(character['physical_description'])
    if character.get('clothing'):
        parts.append(f"Wearing {character['clothing']}.")
    if character.get('distinctive_features'):
        parts.append(character['distinctive_features'])
    if character.get('voice'):
        voice = character['voice']
        parts.append(f"Voice: {voice.get('timbre', '')}.")
        if voice.get('tone'):
            parts.append(f"Tone: {voice['tone']}.")
    if character.get('personality_traits'):
        parts.append(f"Personality: {', '.join(character['personality_traits'])}.")
    return ' '.join(parts)


def assemble_prompts(character: Dict[str, Any], shots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    char_desc = build_character_description(character)
    prompts = []
    for shot in shots:
        prompt = (
            f"Roles & Subjects: {char_desc} "
            f"{shot.get('description', '')} "
            f"Style: {shot.get('style', 'cinematic, realistic lighting')} "
            f"Camera: {shot.get('camera', 'medium shot')} "
            f"Background: {shot.get('background', 'savanna clearing with acacia tree')} "
            f"Audio: {shot.get('audio', 'ambient savanna sounds')}"
        )
        prompts.append({
            "shot_id": shot.get("shot_id"),
            "time": shot.get("time"),
            "duration_sec": shot.get("duration_sec"),
            "prompt": prompt.strip()
        })
    return prompts


def main():
    parser = argparse.ArgumentParser(description="Assemble prompts for JoyAI-Echo")
    parser.add_argument("--character", required=True, help="Path to CharacterProfile JSON")
    parser.add_argument("--shots", required=True, help="Path to shots JSON (episode shots file)")
    parser.add_argument("--output", default="prompts.json", help="Output JSON file")
    args = parser.parse_args()

    character = load_json(args.character)
    shots_data = load_json(args.shots)
    shots = shots_data.get("shots", shots_data)

    prompts = assemble_prompts(character, shots)

    output = {
        "episode_id": shots_data.get("episode_id"),
        "character_id": character.get("character_id"),
        "total_shots": len(prompts),
        "prompts": prompts
    }

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(prompts)} prompts → {args.output}")


if __name__ == "__main__":
    main()
