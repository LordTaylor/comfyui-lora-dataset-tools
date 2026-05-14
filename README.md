# comfyui-lora-dataset-tools

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![ComfyUI](https://img.shields.io/badge/ComfyUI-SDXL-blueviolet)
![Version](https://img.shields.io/badge/version-0.1.0-green)

Streamlined LoRA dataset generation for ComfyUI — **two nodes that replace 5+ manual configuration steps.**

Before this package you had to edit a base description node, a trigger word in the wildcard node, two separate output folder fields, maintain external `.txt` wildcard files, and then run a post-processing Python script after every generation. Now you edit **one node** (`LoRADatasetConfig`) and everything else wires up automatically. The caption sidecar `.txt` file is written atomically alongside each PNG — no post-processing script needed.

---

## Quick Start

1. Install the package (see [Installation](#installation)).
2. Open an example workflow from `example_workflows/`.
3. Edit **only** the `🎛️ LoRA Dataset Config` node: set your `trigger_word`, `output_name`, and `description`.
4. Set `seed` to **Randomize** for variety across runs.
5. Queue the prompt. Paired `.png` + `.txt` files land in `ComfyUI/output/lora_dataset/<name>/`.

---

## Nodes

### 🎛️ LoRA Dataset Config (`LoRADatasetConfig`)

The single configuration node. **You only ever edit this node.** All other nodes in the workflow are pre-wired and never need touching.

Built-in wildcard lists cover shot types, poses, expressions, locations, lighting, and atmosphere — no external `.txt` files required. The variety is seeded so results are reproducible when you need them and random when you don't.

#### Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `trigger_word` | STRING | `char_trigger` | Unique LoRA trigger word. Used in training captions and prepended to the varied prompt. |
| `output_name` | STRING | `my_character` | Output folder and filename prefix. Use `snake_case`; spaces are converted automatically. |
| `description` | STRING | `adult woman, cel-shaded…` | Base description of your subject. Do **not** include the trigger word here — it is added automatically. |
| `dataset_type` | ENUM | `character` | `character` · `outfit` · `location` · `object`. Controls wildcard selection and output resolution. |
| `seed` | INT | `0` | Set to **Randomize** in the widget for a different prompt composition every run. |

#### Outputs

| Name | Type | Description |
|------|------|-------------|
| `trigger` | STRING | Trigger word, trimmed. Connect to `LoRACaptionSaver.trigger_word`. |
| `varied_prompt` | STRING | `trigger, <random shot/pose/expression/location/lighting>`. Wire to your positive prompt. |
| `base_description` | STRING | The description field verbatim. Use as a stable secondary prompt or for IPAdapter conditioning. |
| `output_prefix` | STRING | `lora_dataset/<name>/<name>`. Connect to `LoRACaptionSaver.filename_prefix`. |
| `latent_width` | INT | `1216` for `location`, `1024` for all others. Wire to your Empty Latent Image node. |
| `latent_height` | INT | `832` for `location`, `1024` for all others. Wire to your Empty Latent Image node. |

#### Resolution by dataset type

| `dataset_type` | Width | Height | Notes |
|----------------|-------|--------|-------|
| `character` | 1024 | 1024 | Full IPAdapter face chain in example workflow |
| `outfit` | 1024 | 1024 | Single IPAdapter PLUS in example workflow |
| `location` | 1216 | 832 | Landscape ratio, no people |
| `object` | 1024 | 1024 | Isolated subject |

#### Built-in wildcard categories

The wildcards are baked into `wildcards.py` — no `.txt` files to maintain.

| Category | Used for |
|----------|----------|
| `char_shot` | Camera framing (full body, bust, close-up, etc.) |
| `char_pose` | Body language and stance |
| `char_expression` | Facial expression |
| `location` | Background environment |
| `lighting` | Lighting style |
| `outfit_shot` | Outfit-specific framings |
| `outfit_activity` | Activity showing outfit in motion |
| `obj_angle` | Viewing angle for locations/objects |
| `time_of_day` | Daylight condition |
| `atmosphere` | Mood and weather |

---

### 💾 LoRA Caption Saver (`LoRACaptionSaver`)

Saves each generated image as a PNG and writes a matching `.txt` caption file in the same atomic operation. Replaces the combination of `SaveImage` + `SaveText|pysssss` + a separate post-processing script.

#### Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `images` | IMAGE | Yes | Image tensor from your KSampler/VAE Decode pipeline. |
| `caption` | STRING | Yes | Caption string from `Florence2Run` (or any STRING node). Force-input — must be connected. |
| `filename_prefix` | STRING | Yes | Output path prefix. Connect to `LoRADatasetConfig.output_prefix` for automatic naming, or type `lora_dataset/<name>/<name>` manually. |
| `trigger_word` | STRING | No | Connect to `LoRADatasetConfig.trigger`. Prepended to the caption in the `.txt` file. |

#### Outputs

| Name | Type | Description |
|------|------|-------------|
| `image` | IMAGE | Pass-through of the input image. Chain to a preview node if desired. |
| `caption` | STRING | Final caption string as written to the `.txt` file (`trigger_word, <Florence2 caption>`). |

#### Caption file format

```
my_character, The image shows a woman standing confidently in a forest clearing...
```

If no `trigger_word` is connected the caption is written as-is without a prefix.

---

## Workflow Guide

### Step-by-step

1. **Open an example workflow** matching your subject type (character / outfit / location-object).
2. **Edit `🎛️ LoRA Dataset Config`** — the only node you need to change:
   - `trigger_word`: your unique activation token (e.g. `jane_doe_v1`)
   - `output_name`: short snake_case name (e.g. `jane_doe`)
   - `description`: visual description of your subject without the trigger word
   - `dataset_type`: pick the type that matches your subject
   - `seed`: set to **Randomize** for maximum variety across the dataset
3. **Load reference images** into the `LoadImage` node(s) (face reference for character/outfit, style reference for others).
4. **Queue the prompt** (Ctrl+Enter). ComfyUI will generate the image, auto-caption it with Florence2, and save the pair.
5. **Repeat** — queue 20–50 times with seed on Randomize. All pairs accumulate in `ComfyUI/output/lora_dataset/<name>/`.

> The dataset folder is ready for training immediately after generation — no post-processing, no script to run.

---

## Example Workflows

All example workflows are in the `example_workflows/` directory.

| File | Type | Description |
|------|------|-------------|
| `21_char_lora_dataset.json` | Character | 3-stage IPAdapter face identity chain for strong character consistency |
| `22_outfit_lora_dataset.json` | Outfit | Single IPAdapter PLUS for style and outfit consistency |
| `23_loc_obj_lora_dataset.json` | Location / Object | Landscape ratio (1216×832), no IPAdapter, environment focus |

To use: in ComfyUI open the workflow browser, drag-and-drop the `.json` file, or use **Load** from the menu.

---

## Output Format

Generated files are saved under `ComfyUI/output/`:

```
ComfyUI/output/lora_dataset/
└── my_character/
    ├── my_character_00001_.png
    ├── my_character_00001_.txt
    ├── my_character_00002_.png
    ├── my_character_00002_.txt
    ├── my_character_00003_.png
    ├── my_character_00003_.txt
    └── ...
```

Each `.txt` file contains a single line:

```
my_character, The image shows a woman in a full body shot, standing confidently with hands on hips, in a forest clearing, soft natural daylight
```

The PNG files embed the full ComfyUI workflow metadata (prompt, nodes) in their EXIF data.

---

## Training Preparation

The output folder is structured exactly as kohya_ss and SimpleTuner expect — each image paired with a same-name `.txt` caption file.

### kohya_ss

Point your dataset directory to `ComfyUI/output/lora_dataset/<name>/`. The `.txt` sidecar files are picked up automatically as captions.

### SimpleTuner

Use the same directory as your `instance_data_dir`. Set `caption_strategy: textfile` in your dataset config — SimpleTuner will read the `.txt` files alongside each image.

### Recommended dataset sizes

| Type | Images |
|------|--------|
| Character | 20–50 |
| Outfit | 15–30 |
| Location | 15–25 |
| Object | 15–30 |

---

## Requirements

- **ComfyUI** (SDXL)
- **comfyui-florence2** — for auto-captioning via `Florence2Run`
- **ComfyUI IPAdapter Plus** — for face/style consistency in character and outfit workflows
- No additional Python packages — all wildcard logic is self-contained in `wildcards.py`

---

## Installation

### Manual (recommended)

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/LordTaylor/comfyui-lora-dataset-tools.git
```

Restart ComfyUI. The two nodes appear under the **LoRA Dataset Tools** category.

### ComfyUI Manager

Search for **LoRA Dataset Tools** in the Manager node browser and click Install. (Available once the package is published to the registry.)

---

## License

MIT — see [LICENSE](LICENSE).
