# Changelog

## [0.1.0] — 2026-05-14

### Added
- `LoRADatasetConfig` — single config node with built-in wildcards (character / outfit / location / object)
- `LoRACaptionSaver` — atomic PNG + .txt caption saver (replaces SaveImage + SaveText + post-processing script)
- Example workflows: `21_char_lora_dataset.json`, `22_outfit_lora_dataset.json`, `23_loc_obj_lora_dataset.json`
- Built-in wildcard library in `wildcards.py` (no external .txt files needed)
