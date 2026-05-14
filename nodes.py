"""
comfyui-lora-dataset-tools — nodes
Two nodes for streamlined LoRA dataset generation:

  LoRADatasetConfig  — single config node (trigger, description, variety)
  LoRACaptionSaver   — atomic PNG + .txt caption saver
"""

import os
import json
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo

import folder_paths
from .wildcards import get_variety_prompt, get_latent_size


# ──────────────────────────────────────────────────────────────────────────────
# Node 1 — LoRADatasetConfig
# ──────────────────────────────────────────────────────────────────────────────

class LoRADatasetConfig:
    """
    Single configuration node for LoRA dataset generation.

    User edits ONLY this node — trigger word, description, output name,
    and dataset type.  All other nodes are wired up and never need touching.

    Outputs:
        0  trigger          STRING  — trigger word alone
        1  varied_prompt    STRING  — trigger + random shot/pose/location/…
        2  base_description STRING  — character / outfit / scene description
        3  output_prefix    STRING  — lora_dataset/{name}/{name}
        4  latent_width     INT     — recommended latent width
        5  latent_height    INT     — recommended latent height
    """

    DATASET_TYPES = ["character", "outfit", "location", "object"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trigger_word": (
                    "STRING",
                    {
                        "default": "char_trigger",
                        "multiline": False,
                        "tooltip": "Unique trigger word for your LoRA. Use it in training captions.",
                    },
                ),
                "output_name": (
                    "STRING",
                    {
                        "default": "my_character",
                        "multiline": False,
                        "tooltip": "Output folder and filename prefix. Keep it short and snake_case.",
                    },
                ),
                "description": (
                    "STRING",
                    {
                        "default": (
                            "adult woman, cel-shaded, flat colors, "
                            "animated series character, bridge toons style"
                        ),
                        "multiline": True,
                        "tooltip": (
                            "Base description of your character / outfit / location. "
                            "Do NOT include trigger word here — it is added automatically."
                        ),
                    },
                ),
                "dataset_type": (
                    cls.DATASET_TYPES,
                    {
                        "tooltip": (
                            "character → full IPAdapter face chain, 1024×1024  |  "
                            "outfit → style IPA only  |  "
                            "location → 1216×832 landscape, no people  |  "
                            "object → 1024×1024, isolated"
                        )
                    },
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "tooltip": "Set to 'randomize' in the widget for variety per run.",
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "INT", "INT")
    RETURN_NAMES = (
        "trigger",
        "varied_prompt",
        "base_description",
        "output_prefix",
        "latent_width",
        "latent_height",
    )
    FUNCTION = "generate_config"
    CATEGORY = "LoRA Dataset Tools"
    DESCRIPTION = (
        "Central config node for LoRA dataset generation. "
        "Edit ONLY this node — everything else wires up automatically."
    )

    def generate_config(
        self,
        trigger_word: str,
        output_name: str,
        description: str,
        dataset_type: str,
        seed: int,
    ):
        trigger = trigger_word.strip()
        name = output_name.strip().replace(" ", "_")

        varied_prompt = f"{trigger}, {get_variety_prompt(dataset_type, seed)}"
        output_prefix = f"lora_dataset/{name}/{name}"
        w, h = get_latent_size(dataset_type)

        return (trigger, varied_prompt, description.strip(), output_prefix, w, h)


# ──────────────────────────────────────────────────────────────────────────────
# Node 2 — LoRACaptionSaver
# ──────────────────────────────────────────────────────────────────────────────

class LoRACaptionSaver:
    """
    Saves image as PNG AND a matching .txt caption file atomically.

    Replaces:  SaveImage  +  SaveText|pysssss  +  lora_dataset_post_caption.py

    Each run produces a pair:
        lora_dataset/char_NAME/char_NAME_00001_.png
        lora_dataset/char_NAME/char_NAME_00001_.txt   ← trigger_word, <caption>

    The .txt files are immediately ready for kohya_ss / SimpleTuner training.
    """

    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "caption": (
                    "STRING",
                    {
                        "forceInput": True,
                        "multiline": True,
                        "tooltip": "Caption from Florence2Run (or any STRING).",
                    },
                ),
                "filename_prefix": (
                    "STRING",
                    {
                        "default": "lora_dataset/char_NAME/char_NAME",
                        "tooltip": (
                            "Connect to LoRADatasetConfig.output_prefix for auto-naming, "
                            "or type manually: lora_dataset/<name>/<name>"
                        ),
                    },
                ),
            },
            "optional": {
                "trigger_word": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": (
                            "Connect to LoRADatasetConfig.trigger. "
                            "Prepended to caption in the .txt file."
                        ),
                    },
                ),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "caption")
    FUNCTION = "save_with_caption"
    CATEGORY = "LoRA Dataset Tools"
    OUTPUT_NODE = True
    DESCRIPTION = (
        "Saves image as PNG and a matching .txt caption sidecar atomically. "
        "Replaces SaveImage + SaveText|pysssss. No post-processing script needed."
    )

    def save_with_caption(
        self,
        images,
        caption: str,
        filename_prefix: str = "lora_dataset/output/output",
        trigger_word: str = "",
        prompt=None,
        extra_pnginfo=None,
    ):
        tw = trigger_word.strip()
        full_caption = f"{tw}, {caption.strip()}" if tw else caption.strip()

        full_output_folder, filename, counter, subfolder, _ = (
            folder_paths.get_save_image_path(
                filename_prefix,
                self.output_dir,
                images[0].shape[1],
                images[0].shape[0],
            )
        )

        results = []
        for batch_number, image in enumerate(images):
            # ── build image ──────────────────────────────────────────────
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            # ── PNG metadata ─────────────────────────────────────────────
            metadata = PngInfo()
            try:
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for k, v in extra_pnginfo.items():
                        metadata.add_text(k, json.dumps(v))
            except Exception:
                pass  # metadata is nice-to-have, not critical

            # ── filenames ────────────────────────────────────────────────
            fn = filename.replace("%batch_num%", str(batch_number))
            base = f"{fn}_{counter:05}_"
            png_path = os.path.join(full_output_folder, base + ".png")
            txt_path = os.path.join(full_output_folder, base + ".txt")

            # ── atomic save ──────────────────────────────────────────────
            img.save(png_path, pnginfo=metadata, compress_level=self.compress_level)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(full_caption)

            results.append(
                {"filename": base + ".png", "subfolder": subfolder, "type": self.type}
            )
            counter += 1

        return {"ui": {"images": results}, "result": (images, full_caption)}


# ──────────────────────────────────────────────────────────────────────────────
# Registration
# ──────────────────────────────────────────────────────────────────────────────

NODE_CLASS_MAPPINGS = {
    "LoRADatasetConfig": LoRADatasetConfig,
    "LoRACaptionSaver": LoRACaptionSaver,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoRADatasetConfig": "🎛️ LoRA Dataset Config",
    "LoRACaptionSaver": "💾 LoRA Caption Saver",
}
