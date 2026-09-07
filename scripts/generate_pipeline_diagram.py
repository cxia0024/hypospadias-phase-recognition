"""Generate docs/pipeline_diagram.svg — a colour-coded overview of the
Stage 2 phase-recognition pipeline (notebooks/stage2_phase_recognition.ipynb).

Regenerate after changing the notebook's pipeline structure:
    python3 scripts/generate_pipeline_diagram.py
"""

import os

CANVAS_W = 1900

MAIN_X = 460
MAIN_W = 980
LEFT_X = 40
LEFT_W = 380
RIGHT_X = 1480
RIGHT_W = 380

HEADER_H = 44
LINE_H = 25
PAD = 18
CHIP_H = 64
GAP = 34

FONT = "Helvetica, Arial, sans-serif"

svg_parts = []
_clip_counter = [0]


def esc(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def rounded_box(x, y, w, h, fill, stroke, rx=14, dash=None, sw=2):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    svg_parts.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash_attr}/>'
    )


def header_band(x, y, w, h, color, radius=14):
    # header band with rounded top corners only, achieved by overlaying a
    # rounded rect clipped visually with a plain rect covering the bottom.
    _clip_counter[0] += 1
    cid = f"clip-{_clip_counter[0]}"
    svg_parts.append(
        f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" '
        f'height="{h}" rx="{radius}" ry="{radius}"/></clipPath>'
    )
    svg_parts.append(
        f'<g clip-path="url(#{cid})"><rect x="{x}" y="{y}" width="{w}" '
        f'height="{h}" fill="{color}"/></g>'
    )


def text_line(x, y, s, size=17, weight="normal", color="#1f2937", anchor="start", style="normal"):
    svg_parts.append(
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" font-style="{style}" fill="{color}" '
        f'text-anchor="{anchor}">{esc(s)}</text>'
    )


def arrow_v(x, y1, y2, color="#475569", sw=3):
    svg_parts.append(
        f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{sw}" marker-end="url(#arrow)"/>'
    )


def connector(x1, y1, x2, y2, color="#94a3b8", dash="6,5", arrow=True, sw=2.5):
    marker = ' marker-end="url(#arrow-light)"' if arrow else ""
    svg_parts.append(
        f'<path d="M {x1} {y1} L {x2} {y2}" stroke="{color}" stroke-width="{sw}" '
        f'stroke-dasharray="{dash}" fill="none"{marker}/>'
    )


def stage_box(y, title, lines, header_color, body_fill, border_color, extra_h=0, chips=None, chip_note=None):
    n_lines = len(lines)
    h = HEADER_H + PAD * 2 + n_lines * LINE_H + extra_h
    if chips:
        h += CHIP_H + PAD
        if chip_note:
            h += len(chip_note) * LINE_H
    rounded_box(MAIN_X, y, MAIN_W, h, body_fill, border_color, sw=2.5)
    header_band(MAIN_X, y, MAIN_W, HEADER_H, header_color)
    svg_parts.append(
        f'<rect x="{MAIN_X}" y="{y}" width="{MAIN_W}" height="{HEADER_H}" rx="14" ry="14" '
        f'fill="none" stroke="{border_color}" stroke-width="2.5"/>'
    )
    text_line(MAIN_X + 24, y + 30, title, size=19, weight="bold", color="#ffffff")
    ty = y + HEADER_H + PAD + 14
    for line in lines:
        text_line(MAIN_X + 24, ty, line, size=15.5, color="#334155")
        ty += LINE_H
    if chips:
        chip_y = ty - LINE_H + 8
        chip_w = (MAIN_W - 24 * 2 - 16 * (len(chips) - 1)) / len(chips)
        cx = MAIN_X + 24
        for label, dims in chips:
            rounded_box(cx, chip_y, chip_w, CHIP_H, "#ffffff", header_color, rx=10, sw=2)
            text_line(cx + chip_w / 2, chip_y + 26, label, size=14.5, weight="bold",
                      color="#1f2937", anchor="middle")
            text_line(cx + chip_w / 2, chip_y + 47, dims, size=12.5, color="#64748b",
                      anchor="middle")
            cx += chip_w + 16
        ty = chip_y + CHIP_H + PAD + 14
        if chip_note:
            for note in chip_note:
                text_line(MAIN_X + 24, ty, note, size=14, color="#475569", style="italic")
                ty += LINE_H
    return y + h


def context_box(x, y, w, title, lines, color="#64748b"):
    h = HEADER_H - 4 + PAD * 1.6 + len(lines) * LINE_H
    rounded_box(x, y, w, h, "#f8fafc", color, rx=12, dash="7,5", sw=2)
    text_line(x + 18, y + 30, title, size=15.5, weight="bold", color=color)
    ty = y + HEADER_H - 4 + 14
    for line in lines:
        text_line(x + 18, ty, line, size=13.5, color="#475569")
        ty += LINE_H
    return h


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

y = 40

# Title
title_h = 96
text_line(CANVAS_W / 2, y + 38, "Stage 2 — Phase Recognition: Full Pipeline",
          size=30, weight="bold", color="#0f172a", anchor="middle")
text_line(CANVAS_W / 2, y + 68,
          "Distal hypospadias repair videos  ·  7 in-house cases  ·  leave-one-video-out cross-validation",
          size=15.5, color="#64748b", anchor="middle")
y += title_h + 10

# Inputs row
input_h = 62
gap_in = 24
input_w = (MAIN_W - gap_in) / 2
rounded_box(MAIN_X, y, input_w, input_h, "#eef2ff", "#4338ca", sw=2)
text_line(MAIN_X + input_w / 2, y + 27, "Raw Videos", size=16, weight="bold",
          color="#312e81", anchor="middle")
text_line(MAIN_X + input_w / 2, y + 48, "7 in-house recordings, sampled at 2 fps",
          size=12.5, color="#4338ca", anchor="middle")
rounded_box(MAIN_X + input_w + gap_in, y, input_w, input_h, "#eef2ff", "#4338ca", sw=2)
text_line(MAIN_X + input_w + gap_in + input_w / 2, y + 27, "CVAT Annotations",
          size=16, weight="bold", color="#312e81", anchor="middle")
text_line(MAIN_X + input_w + gap_in + input_w / 2, y + 48,
          "Interpolated phase-boundary tracks", size=12.5, color="#4338ca", anchor="middle")
y_inputs_bottom = y + input_h
y += input_h + GAP
arrow_v(MAIN_X + MAIN_W / 2, y_inputs_bottom, y)

# Stage 1: Manifest
s1_top = y
y = stage_box(
    y,
    "1 · Manifest Construction",
    [
        "Parse CVAT interval tracks  →  per-frame phase labels",
        "Overlap check: no frame may carry two phase labels",
        "Sampling: 2 fps base rate + dense resample of segments < 10 frames",
        "Outputs: phase-by-video incidence matrix, frame counts",
    ],
    "#2563eb", "#eff6ff", "#2563eb",
)
arrow_v(MAIN_X + MAIN_W / 2, y, y + GAP)
y += GAP

# Stage 2: Feature extraction
s2_top = y
y = stage_box(
    y,
    "2 · Feature Extraction (frozen backbones)",
    ["Each backbone: own preprocessing, extracted once, cached in frame order (~1.4 GB total)"],
    "#7c3aed", "#f5f3ff", "#7c3aed",
    chips=[
        ("ResNet-50", "2048-d · supervised · GAP"),
        ("DINO v1", "768-d · ViT-B/16 · CLS"),
        ("DINOv2", "768-d · ViT-B/14 · CLS"),
        ("MoCo v3", "2048-d · ResNet-50 · GAP"),
    ],
    chip_note=["+ Stage 1 detector features (9-d: conf / presence / count × hand, needle driver, forceps) — Model D only"],
)
s2_bottom = y
arrow_v(MAIN_X + MAIN_W / 2, y, y + GAP)
y += GAP

# Stage 3: t-SNE
s3_top = y
y = stage_box(
    y,
    "3 · t-SNE Sanity Check",
    [
        "Per backbone, coloured by phase and by video",
        "Early warning, not a metric — a phase invisible here won't be learnable by the GRU",
    ],
    "#0d9488", "#f0fdfa", "#0d9488",
)
s3_bottom = y
arrow_v(MAIN_X + MAIN_W / 2, y, y + GAP)
y += GAP

# Stage 4: Baselines
y = stage_box(
    y,
    "4 · Baselines",
    [
        "Majority class — always predicts the longest phase (frame count)",
        "Per-frame logistic regression on frozen features — no temporal model",
    ],
    "#65a30d", "#f7fee7", "#65a30d",
)
arrow_v(MAIN_X + MAIN_W / 2, y, y + GAP)
y += GAP

# Stage 5: LOOCV + BiGRU sweep
y = stage_box(
    y,
    "5 · Leave-One-Video-Out CV  ·  BiGRU Backbone Sweep",
    [
        "Frozen features → linear projection → single-layer BiGRU → per-frame head",
        "Overlapping windows: size 1024, stride 512 (~8.5 min) — logits averaged at inference",
        "All 4 backbones, identical frames / hyperparameters / folds / seeds",
        "7 folds — scalers, weights, class weights refit per fold on 6 training videos",
    ],
    "#ea580c", "#fff7ed", "#ea580c",
)
arrow_v(MAIN_X + MAIN_W / 2, y, y + GAP)
y += GAP

# Stage 6: Model C vs D
y = stage_box(
    y,
    "6 · Model C  vs.  Model D",
    [
        "Model C — winning backbone → GRU (reference system)",
        "Model D — winning backbone + detector features → GRU",
        "Feature blocks standardised separately; scalers fit per fold before concatenation",
    ],
    "#dc2626", "#fef2f2", "#dc2626",
)
arrow_v(MAIN_X + MAIN_W / 2, y, y + GAP)
y += GAP

# Stage 7: Metrics
y = stage_box(
    y,
    "7 · Metrics",
    [
        "Pooled — macro-F1 (headline), per-phase F1, confusion matrix",
        "Segmental — edit score, F1@IoU, per-video phase timelines",
        "Per-video metrics, computed for the paired comparison below",
    ],
    "#d97706", "#fffbeb", "#d97706",
)
arrow_v(MAIN_X + MAIN_W / 2, y, y + GAP)
y += GAP

# Stage 8: Statistics
y = stage_box(
    y,
    "8 · Statistics",
    [
        "Full per-video table (n = 7) and win counts, Model D vs Model C",
        "Cliff's delta with bootstrap CI — descriptive effect size",
        "Pre-specified Wilcoxon signed-rank, Model C vs D — the sole inferential test",
    ],
    "#c026d3", "#fdf4ff", "#c026d3",
)
arrow_v(MAIN_X + MAIN_W / 2, y, y + GAP)
y += GAP

# Stage 9: Outputs
s9_top = y
y = stage_box(
    y,
    "9 · Outputs",
    [
        "Per-video & pooled results tables, confusion-matrix PNGs, run manifest",
        "Raw per-video logits + fold checkpoints  {run}__{video}.pt  (one model per held-out video)",
        "Per-frame prediction CSV  (video, frame, timestamp, true / predicted phase)",
    ],
    "#1d4ed8", "#eff6ff", "#1d4ed8",
)
s9_bottom = y

# Context boxes ---------------------------------------------------------

stage1_ctx_y = s2_top + 10
stage1_h = context_box(
    LEFT_X, stage1_ctx_y, LEFT_W,
    "Stage 1 (sibling repo)",
    [
        "AVOS YOLOv8 instrument detector",
        "Run over every sampled frame;",
        "no ground-truth validation here —",
        "Model D read as conditional on it.",
    ],
)
connector(LEFT_X + LEFT_W, stage1_ctx_y + stage1_h / 2, MAIN_X, s2_top + 40)

stage3_ctx_y = s3_top - 6
stage3_h = context_box(
    RIGHT_X, stage3_ctx_y, RIGHT_W,
    "→ Stage 3",
    ["Embedding / clustering analysis", "built on these t-SNE projections."],
)
connector(MAIN_X + MAIN_W, s3_top + 30, RIGHT_X, stage3_ctx_y + stage3_h / 2)

stage4_ctx_y = s9_top + 20
stage4_h = context_box(
    RIGHT_X, stage4_ctx_y, RIGHT_W,
    "→ Stage 4",
    [
        "Saliency & segment selection.",
        "Loads the fold checkpoint that",
        "never saw its target video, plus",
        "this stage's phase logits.",
    ],
)
connector(MAIN_X + MAIN_W, s9_top + 60, RIGHT_X, stage4_ctx_y + stage4_h / 2)

# Footer
y_end = max(y, stage4_ctx_y + stage4_h) + 34
text_line(CANVAS_W / 2, y_end,
          "Everything fitted to data (weights, scalers, class weights) is rebuilt inside each fold from that fold's 6 training videos only.",
          size=13.5, color="#94a3b8", anchor="middle", style="italic")
CANVAS_H = int(y_end + 30)

# ---------------------------------------------------------------------------
# Assemble document
# ---------------------------------------------------------------------------

defs = f"""
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#475569"/>
    </marker>
    <marker id="arrow-light" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8"/>
    </marker>
  </defs>
  <rect x="0" y="0" width="{CANVAS_W}" height="{CANVAS_H}" fill="#ffffff"/>
"""

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}" '
    f'width="{CANVAS_W}" height="{CANVAS_H}" font-family="{FONT}">\n'
    f"{defs}\n" + "\n".join(svg_parts) + "\n</svg>\n"
)

out_path = os.path.join(os.path.dirname(__file__), "..", "docs", "pipeline_diagram.svg")
out_path = os.path.normpath(out_path)
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w") as f:
    f.write(svg)

print(f"Wrote {out_path} ({CANVAS_W}x{CANVAS_H})")
