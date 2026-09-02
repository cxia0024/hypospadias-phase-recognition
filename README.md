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
