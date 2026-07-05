# Contributing

Contributions are welcome — especially around the color-mapping algorithm, the emotion lexicon, and the model-vs-lexicon calibration.

## Setup

```bash
git clone https://github.com/Hosein-Abdollahi/Narrative-Resonance
cd Narrative-Resonance
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

That covers Fast and Precise modes. For Balanced mode (the local transformer), also `pip install torch transformers`.

## Areas open for contribution

- **Expanding the lexicon** in `emotion_engine.py` (`_LEXICON`) — more words and finer weights per emotion, especially for the lexicon-driven emotions (calm, nostalgia, tenderness, hope, awe, disgust, anxiety).
- **Improving the HSL mapping** in `emotions_to_palette()` — how emotions combine into a harmonized palette is a starting point, not a solved problem.
- **Calibration** — the model-vs-lexicon split and the keyword-overlay coefficients are tuned by hand against the transformer. Better-grounded values (or an evaluation set) would help. See the `_TRANSFORMER_EMOTION_MAP` / `_KEYWORD_OVERLAY` design in `emotion_engine.py`.
- **Reducing `wonder` over-firing on short sentences** — the model's `surprise` label spikes on terse lines; a length gate or dampening factor would sharpen it.
- **Roadmap items** (see README): arc smoothing and a pacing/tension curve, story-shape classification, file ingestion for full manuscripts, character-level arcs.

## Tests

The engine is covered by a regression suite in `test_engine.py` (negation handling, the model-vs-lexicon split, neutral detection, per-emotion calibration). Run it before opening a PR:

```bash
python test_engine.py
```

**Any change to engine behavior should come with a test that pins it.** If you fix or tune an emotion, add a case so it can't silently regress.

## Code style

- Keep `emotion_engine.py` free of any UI / Streamlit imports — it must stay usable as a standalone library.
- New analysis backends follow the `_analyze_with_*` pattern (see `_analyze_with_keywords`, `_analyze_with_transformer`, `_analyze_with_api`) and are wired into `analyze_emotions()`.
- The project is English-only for now; the transformer and lexicon both assume English input.
