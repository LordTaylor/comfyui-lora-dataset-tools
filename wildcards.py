"""
Built-in wildcard lists for LoRA dataset generation.
No external .txt files needed — variety is baked in.
"""

import random as _random

WILDCARDS: dict[str, list[str]] = {
    # ── CHARACTER ──────────────────────────────────────────────────────────
    "char_shot": [
        "full body shot",
        "half body portrait, waist up",
        "close-up face and shoulders",
        "medium shot, thigh up",
        "wide establishing shot, full body",
        "bust portrait",
        "back view full body",
        "three-quarter view full body",
        "action shot full body",
        "sitting pose full body",
        "dynamic low angle full body",
        "overhead angle half body",
    ],
    "char_pose": [
        "standing confidently, hands on hips",
        "sitting on steps, relaxed",
        "walking forward casually",
        "arms crossed, looking forward",
        "leaning against wall",
        "kneeling on one knee",
        "looking over shoulder",
        "reaching forward with one arm",
        "crouching low",
        "running dynamic pose",
        "standing relaxed, weight on one leg",
        "sitting cross-legged",
    ],
    "char_expression": [
        "smiling warmly",
        "serious determined expression",
        "surprised wide eyes",
        "calm neutral expression",
        "gentle soft smile",
        "laughing joyfully",
        "pensive thoughtful look",
        "confident smirk",
        "focused intense gaze",
        "curious raised eyebrow",
    ],
    "location": [
        "forest clearing, lush green",
        "city street at night, neon lights",
        "cozy tavern interior, warm lighting",
        "mountain peak, dramatic sky",
        "ancient library, candlelight",
        "beach at sunset, golden sand",
        "snowy mountain path",
        "busy market square",
        "rooftop with city view",
        "mystical cave with glowing crystals",
        "flower meadow, bright day",
        "stone bridge over river",
        "ancient ruins, overgrown",
        "harbor docks at dusk",
    ],
    "lighting": [
        "soft natural daylight",
        "dramatic rim lighting",
        "warm candlelight glow",
        "cool blue moonlight",
        "overcast diffuse light",
        "golden hour sunlight",
        "dramatic side lighting",
        "soft studio lighting",
        "harsh direct sunlight",
        "backlit silhouette glow",
    ],

    # ── OUTFIT ─────────────────────────────────────────────────────────────
    "outfit_shot": [
        "full body outfit showcase",
        "torso detail view",
        "back view full body",
        "movement shot full body",
        "sitting showing outfit detail",
        "three-quarter full body",
        "close-up fabric detail",
        "profile view full body",
    ],
    "outfit_activity": [
        "walking casually forward",
        "sitting at a wooden table",
        "action dynamic pose",
        "standing relaxed natural",
        "gentle movement, flowing fabric",
        "stretching arms overhead",
        "turning around mid-motion",
        "leaning on a surface",
    ],
    "outfit_background": [
        "simple white background",
        "plain neutral grey background",
        "soft gradient background",
        "minimal indoor room background",
        "clean studio background",
    ],

    # ── LOCATION / OBJECT ──────────────────────────────────────────────────
    "obj_angle": [
        "front view",
        "side profile",
        "three-quarter angle",
        "aerial bird's eye view",
        "close detail shot",
        "wide establishing shot",
        "low angle looking up",
        "slight high angle",
    ],
    "time_of_day": [
        "bright noon sunlight",
        "golden hour afternoon",
        "blue hour twilight dusk",
        "night scene dark sky",
        "early morning mist",
        "dramatic sunset orange sky",
        "overcast grey day",
        "stormy dramatic sky",
    ],
    "atmosphere": [
        "clear sunny peaceful",
        "moody thick fog",
        "dramatic storm clouds gathering",
        "light rain wet surfaces",
        "magical ethereal glow",
        "autumn falling leaves",
        "peaceful serene calm",
        "misty mysterious haze",
    ],
}


def get_variety_prompt(dataset_type: str, seed: int) -> str:
    """Return a varied prompt string based on dataset type and seed."""
    rng = _random.Random(seed)

    def pick(key: str) -> str:
        return rng.choice(WILDCARDS[key])

    if dataset_type == "character":
        parts = [
            pick("char_shot"),
            pick("char_pose"),
            pick("char_expression"),
            pick("location"),
            pick("lighting"),
        ]
    elif dataset_type == "outfit":
        parts = [
            pick("outfit_shot"),
            pick("outfit_activity"),
            pick("outfit_background"),
            pick("lighting"),
            "masterpiece, best quality",
        ]
    elif dataset_type == "location":
        parts = [
            pick("obj_angle"),
            pick("time_of_day"),
            pick("atmosphere"),
            "detailed environment",
            "wide shot",
            "no people",
        ]
    else:  # object
        parts = [
            pick("obj_angle"),
            pick("time_of_day"),
            pick("atmosphere"),
            "isolated object",
            "detailed",
            "white background, studio lighting",
        ]

    return ", ".join(parts)


def get_latent_size(dataset_type: str) -> tuple[int, int]:
    """Return (width, height) for the dataset type."""
    if dataset_type == "location":
        return 1216, 832
    return 1024, 1024
