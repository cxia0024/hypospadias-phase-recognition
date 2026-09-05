# hypospadias-phase-recognition

Surgical phase recognition for distal hypospadias repair videos.

## Stage 2 — Phase Recognition

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/cxia0024/hypospadias-phase-recognition/blob/main/notebooks/stage2_phase_recognition.ipynb)

`notebooks/stage2_phase_recognition.ipynb` assigns a surgical phase to every
sampled frame of a distal hypospadias repair video. It is the core technical
contribution of the project: Stage 4 (saliency and segment selection)
depends on this stage's phase logits and phase boundaries.

The notebook builds, in order:

1. **Manifest** — per-frame phase labels from CVAT-annotated boundaries
   (2 fps base rate, with dense resampling of any segment under 10 frames),
   plus the phase-by-video incidence matrix and frame counts.
2. **Features** — four frozen backbones (ResNet-50 supervised, DINO v1
   ViT-B/16, DINOv2 ViT-B/14, MoCo v3 ResNet-50), extracted once and cached
   in frame order, plus the Stage 1 detector features used by Model D.
3. **t-SNE** sanity check per backbone.
4. **Baselines** — majority class, and a per-frame classifier with no
   temporal model.
5. **Backbone sweep** — a single-layer bidirectional GRU on top of each
   backbone, evaluated under leave-one-video-out cross-validation.
6. **Model C vs Model D** — the winning backbone alone vs. the winning
   backbone plus detector features, with pooled metrics, segmental
   metrics (edit score, F1@IoU), and the pre-specified Wilcoxon
   signed-rank comparison.

Run cells top to bottom in Colab; `CONFIG` near the top of the notebook is
the only place that needs paths edited before running against real data
(raw videos, CVAT exports, and the Stage 1 detector cache, all expected
under a single project root on Google Drive).

## Stage 4 — Highlight Reels

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/cxia0024/hypospadias-phase-recognition/blob/main/notebooks/stage4_highlight_reels.ipynb)

`notebooks/stage4_highlight_reels.ipynb` builds short highlight reels from
the full-length videos, using Stage 2's saved artefacts (per-fold GRU
checkpoints, cached visual embeddings, phase logits) and Stage 1's cached
instrument detections. It reuses Stage 2's project root and only adds a
`stage4/` subtree for its own outputs.

All audio is stripped from every video with `ffmpeg -an` before anything
else runs; no audio is read, used, or written at any later stage, and the
final reels carry no audio track.

The notebook builds, in order:

1. **Saliency** — gradient of the winning phase-recognition model's
   predicted-phase logit with respect to each frame's visual embedding,
   computed through the Stage 2 LOOCV fold that held that video out.
   Min-max normalised per video, smoothed, then thresholded (a sweep over
   five candidate thresholds, with one chosen as the operating point) into
   contiguous high-saliency segments.
2. **Reel 1 (saliency only)** — top-N saliency-ranked segments per phase,
   sized to a 2-5 minute (±30s) final playback duration at 2x speed. This
   also fixes the clips-per-phase quota Reels 2 and 3 are asked to match.
3. **Templated captioning** — frame-level captions from predicted phase +
   detected instruments only (no LLM), aggregated into clip-level captions
   either by a fixed sliding window (512s and 32s, 50% overlap — Reel 2's
   saliency-blind candidate pool) or over a saliency segment's own span
   (Reel 3).
4. **Reel 2 (LLM only)** — an LLM (ChatGPT, Claude, or Ollama) selects
   clips from evenly-spaced captioned candidates, with no saliency
   information involved anywhere in the selection.
5. **Reel 3 (combined)** — the same LLM selection, but re-ranking the
   saliency-shortlisted candidate pool from Reel 1 instead of evenly-spaced
   clips.
6. **Assembly** — chronological order, burned-in phase-label overlay,
   uniform 2x speed, no audio, high-quality (lossless by default) encode.
7. **Evaluation** — phase coverage, compression ratio, intra-reel and
   reel-to-video cosine similarity, Spearman alignment with saliency, and
   inter-reel/inter-LLM Jaccard similarity. All descriptive, no
   inferential testing.

`CFG.winning_backbone` (from Stage 2's `backbone_sweep_summary.csv`) and
at least one LLM backend's credentials (`OPENAI_API_KEY`,
`ANTHROPIC_API_KEY`, or a reachable Ollama host) need setting before
running end to end.
