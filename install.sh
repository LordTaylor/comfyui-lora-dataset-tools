#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# comfyui-lora-dataset-tools — full install script
# Usage:  bash install.sh /path/to/ComfyUI
#         bash install.sh          (auto-detects ~/ComfyUI or ../.. from custom_nodes)
# ─────────────────────────────────────────────────────────────────────────────
set -e

# ── Find ComfyUI root ────────────────────────────────────────────────────────
if [ -n "$1" ]; then
  COMFY="$1"
elif [ -d "$HOME/ComfyUI" ]; then
  COMFY="$HOME/ComfyUI"
elif [ -d "../../ComfyUI" ]; then
  COMFY="$(realpath ../../ComfyUI)"
else
  echo "❌  Could not find ComfyUI. Pass the path as an argument:"
  echo "    bash install.sh /path/to/ComfyUI"
  exit 1
fi

NODES="$COMFY/custom_nodes"
MODELS="$COMFY/models"

echo "🔧  ComfyUI root : $COMFY"
echo "🔧  custom_nodes : $NODES"
echo ""

# ── Helper ───────────────────────────────────────────────────────────────────
clone_or_pull() {
  local url="$1" dir="$2" label="$3"
  if [ -d "$dir/.git" ]; then
    echo "  ♻️  $label — already installed, pulling…"
    git -C "$dir" pull --ff-only --quiet
  else
    echo "  ⬇️  $label…"
    git clone --depth 1 "$url" "$dir" --quiet
  fi
}

# ── 1. Custom nodes ──────────────────────────────────────────────────────────
echo "📦  Installing custom nodes…"

clone_or_pull \
  "https://github.com/LordTaylor/comfyui-lora-dataset-tools.git" \
  "$NODES/comfyui-lora-dataset-tools" \
  "comfyui-lora-dataset-tools"

clone_or_pull \
  "https://github.com/cubiq/ComfyUI_IPAdapter_plus.git" \
  "$NODES/ComfyUI_IPAdapter_plus" \
  "ComfyUI_IPAdapter_plus (cubiq)"

clone_or_pull \
  "https://github.com/kilic-ai/comfyui-florence2.git" \
  "$NODES/comfyui-florence2" \
  "comfyui-florence2 (kilic-ai)"

clone_or_pull \
  "https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git" \
  "$NODES/ComfyUI-Custom-Scripts" \
  "ComfyUI-Custom-Scripts (ShowText)"

echo ""

# ── 2. Model download helpers ────────────────────────────────────────────────
echo "📥  Checking models…"

IPA_DIR="$MODELS/ipadapter"
CLIP_DIR="$MODELS/clip_vision"
LLM_DIR="$MODELS/LLM/Florence-2-base"

mkdir -p "$IPA_DIR" "$CLIP_DIR"

download_if_missing() {
  local url="$1" dest="$2" label="$3"
  if [ -f "$dest" ]; then
    echo "  ✅  $label — already present"
  else
    echo "  ⬇️  Downloading $label…"
    curl -L --progress-bar -o "$dest" "$url"
    echo "  ✅  $label — done"
  fi
}

# IPAdapter PLUS (SDXL)
download_if_missing \
  "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors" \
  "$IPA_DIR/ip-adapter-plus_sdxl_vit-h.safetensors" \
  "ip-adapter-plus_sdxl_vit-h.safetensors"

# IPAdapter PLUS FACE (SDXL)
download_if_missing \
  "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus-face_sdxl_vit-h.safetensors" \
  "$IPA_DIR/ip-adapter-plus-face_sdxl_vit-h.safetensors" \
  "ip-adapter-plus-face_sdxl_vit-h.safetensors"

# CLIP Vision ViT-H
download_if_missing \
  "https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors" \
  "$CLIP_DIR/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors" \
  "CLIP-ViT-H-14 (for IPAdapter)"

# Florence-2-base via HuggingFace
if [ -d "$LLM_DIR" ]; then
  echo "  ✅  Florence-2-base — already present"
else
  echo "  ⬇️  Downloading Florence-2-base from HuggingFace…"
  pip install -q huggingface_hub 2>/dev/null || true
  python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('microsoft/Florence-2-base', local_dir='$LLM_DIR', ignore_patterns=['*.msgpack','*.h5','flax_*'])
print('Florence-2-base downloaded.')
"
  echo "  ✅  Florence-2-base — done"
fi

echo ""
echo "─────────────────────────────────────────────────────────────────────────────"
echo "✅  Installation complete!"
echo ""
echo "⚠️  Still needed (download from CivitAI):"
echo "    Checkpoint: bridgeToonsMix_v80.safetensors"
echo "    → https://civitai.com/models/168673"
echo "    Place in: $MODELS/checkpoints/"
echo ""
echo "▶️  Restart ComfyUI, then open example_workflows/21_char_lora_dataset.json"
echo "─────────────────────────────────────────────────────────────────────────────"
