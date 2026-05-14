#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# comfyui-lora-dataset-tools — full install script
# Usage:  bash install.sh /path/to/ComfyUI
#         bash install.sh          (auto-detects ~/ComfyUI)
# ─────────────────────────────────────────────────────────────────────────────

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

# ── Helper: clone or skip if dir already exists (any source — git or CM) ─────
clone_or_skip() {
  local url="$1"
  local dir="$2"
  local label="$3"
  # Also accept an optional alternate dir name (e.g. ComfyUI Manager uses different casing)
  local altdir="${4:-}"

  if [ -d "$dir" ] || { [ -n "$altdir" ] && [ -d "$altdir" ]; }; then
    local found="$dir"
    [ -d "$dir" ] || found="$altdir"
    if [ -d "$found/.git" ]; then
      echo "  ♻️  $label — already installed, pulling…"
      git -C "$found" pull --ff-only --quiet 2>/dev/null || echo "  ⚠️  pull skipped (detached/no remote)"
    else
      echo "  ✅  $label — already installed (no git, skipping pull)"
    fi
  else
    echo "  ⬇️  $label…"
    git clone --depth 1 "$url" "$dir" --quiet && echo "  ✅  $label — done" \
      || echo "  ⚠️  $label — clone failed (check internet / permissions)"
  fi
}

# ── 1. Custom nodes ──────────────────────────────────────────────────────────
echo "📦  Installing custom nodes…"

clone_or_skip \
  "https://github.com/LordTaylor/comfyui-lora-dataset-tools.git" \
  "$NODES/comfyui-lora-dataset-tools" \
  "comfyui-lora-dataset-tools"

# IPAdapter Plus — ComfyUI Manager may install as comfyui_ipadapter_plus (lowercase)
clone_or_skip \
  "https://github.com/cubiq/ComfyUI_IPAdapter_plus.git" \
  "$NODES/ComfyUI_IPAdapter_plus" \
  "ComfyUI_IPAdapter_plus (cubiq)" \
  "$NODES/comfyui_ipadapter_plus"

# Florence2 — ComfyUI Manager may install as comfyui-florence2
clone_or_skip \
  "https://github.com/kilic-ai/comfyui-florence2.git" \
  "$NODES/comfyui-florence2" \
  "comfyui-florence2 (kilic-ai)"

# Custom Scripts (ShowText|pysssss)
clone_or_skip \
  "https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git" \
  "$NODES/ComfyUI-Custom-Scripts" \
  "ComfyUI-Custom-Scripts (ShowText)" \
  "$NODES/comfyui-custom-scripts"

echo ""

# ── 2. Model downloads ───────────────────────────────────────────────────────
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
    curl -L --progress-bar -o "$dest" "$url" \
      && echo "  ✅  $label — done" \
      || echo "  ❌  $label — download failed"
  fi
}

download_if_missing \
  "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors" \
  "$IPA_DIR/ip-adapter-plus_sdxl_vit-h.safetensors" \
  "ip-adapter-plus_sdxl_vit-h (PLUS)"

download_if_missing \
  "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus-face_sdxl_vit-h.safetensors" \
  "$IPA_DIR/ip-adapter-plus-face_sdxl_vit-h.safetensors" \
  "ip-adapter-plus-face_sdxl_vit-h (PLUS FACE)"

download_if_missing \
  "https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors" \
  "$CLIP_DIR/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors" \
  "CLIP-ViT-H-14 (clip_vision)"

# Florence-2-base via huggingface_hub
if [ -d "$LLM_DIR" ]; then
  echo "  ✅  Florence-2-base — already present"
else
  echo "  ⬇️  Downloading Florence-2-base from HuggingFace…"
  pip install -q huggingface_hub 2>/dev/null || true
  python3 - <<PYEOF
from huggingface_hub import snapshot_download
snapshot_download(
    'microsoft/Florence-2-base',
    local_dir='$LLM_DIR',
    ignore_patterns=['*.msgpack', '*.h5', 'flax_*']
)
print('  ✅  Florence-2-base — done')
PYEOF
fi

echo ""
echo "─────────────────────────────────────────────────────────────────────────────"
echo "✅  Installation complete!"
echo ""
echo "⚠️  Still needed — download manually from CivitAI:"
echo "    Checkpoint: bridgeToonsMix_v80.safetensors"
echo "    → https://civitai.com/models/168673"
echo "    Place in:  $MODELS/checkpoints/"
echo ""
echo "▶️  Restart ComfyUI, then load:"
echo "    custom_nodes/comfyui-lora-dataset-tools/example_workflows/21_char_lora_dataset.json"
echo "─────────────────────────────────────────────────────────────────────────────"
