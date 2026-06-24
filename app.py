import streamlit as st
import plotly.graph_objects as go

from emotion_engine import (
    text_to_palette,
    analyze_emotions_by_sentence,
    highlight_keywords_html,
    shade_sentences_html,
    EMOTIONS,
    EMOTION_DISPLAY_COLORS,
    transformers_available,
)
from fingerprint import build_fingerprint, fingerprint_svg

REPO_URL = "https://github.com/its-Sadb0y/Narrative-Resonance"


EXAMPLES = {
    "Nostalgia": (
        "The porch swing still creaked the way it had in my childhood, and the "
        "memories came flooding back. I was lost in nostalgia, full of longing for "
        "those bygone summers, wistful for the days my grandmother hummed in the kitchen."
    ),
    "Dread": (
        "Something moved in the dark beyond the door. A cold fear gripped me, and I "
        "was terrified, frozen in dread. My heart pounded with panic as the handle "
        "slowly turned, and a mounting horror told me I was not alone."
    ),
    "Turning": (
        "She laughed with joy at the old photograph, delighted. Then the grief rose "
        "up behind the laugh, and she was mournful, heartbroken that he was gone. She "
        "cried. But the morning was bright and calm, and a small hope remained."
    ),
}

HERO_TEXT = (
    "The letter arrived on a grey morning, and a cold dread rose in her chest. For a "
    "moment she was afraid, certain it carried bad news. But as she read, the fear "
    "softened into something like hope. She remembered this house, and how much she "
    "had loved it once. The warm kitchen, the garden, the long peaceful evenings. She "
    "had been happy here, and perhaps could be again."
)


st.set_page_config(
    page_title="Narrative Resonance",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600&family=Spectral:ital,wght@0,400;0,500;1,400&display=swap');

:root {
  --ink:        #15141B;
  --surface:    #1E1C26;
  --surface-2:  #25222F;
  --line:       rgba(255,255,255,0.08);
  --text:       #ECE8F0;
  --muted:      #9A93A8;
  --gold:       #E6C079;
  --display:    'Fraunces', Georgia, serif;
  --ui:         'Inter', system-ui, sans-serif;
  --prose:      'Spectral', Georgia, serif;
}

/* Canvas */
.stApp { background: var(--ink); color: var(--text); }
.block-container { padding-top: 2.4rem; padding-bottom: 4rem; max-width: 900px; }

/* Strip Streamlit chrome for a clean demo */
#MainMenu, header[data-testid="stHeader"], footer { visibility: hidden; height: 0; }
[data-testid="stToolbar"] { display: none; }

/* ── Wordmark / hero ── */
.nr-mark {
  display: flex; align-items: center; gap: 11px;
  font-family: var(--ui); font-size: 13px; letter-spacing: .22em;
  text-transform: uppercase; color: var(--muted); margin-bottom: 28px;
}
.nr-mark .dot { color: var(--gold); font-size: 15px; }
.nr-hero-title {
  font-family: var(--display); font-weight: 600;
  font-size: clamp(34px, 6vw, 56px); line-height: 1.04;
  letter-spacing: -0.015em; margin: 0 0 14px 0; color: var(--text);
}
.nr-hero-title em { font-style: italic; color: var(--gold); font-weight: 500; }
.nr-hero-sub {
  font-family: var(--prose); font-size: 18px; line-height: 1.6;
  color: var(--muted); max-width: 600px; margin: 0 0 30px 0;
}

/* ── Eyebrow labels on each section ── */
.nr-eyebrow {
  font-family: var(--ui); font-size: 11px; font-weight: 600;
  letter-spacing: .18em; text-transform: uppercase; color: var(--muted);
  margin: 0 0 12px 0; display: flex; align-items: center; gap: 9px;
}
.nr-eyebrow::before {
  content: ""; width: 18px; height: 1px; background: var(--gold); opacity: .7;
}

/* ── Cards ── */
.nr-card {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 16px; padding: 22px 24px; margin-bottom: 18px;
}

/* ── Fingerprint (the signature) ── */
.nr-fp-frame {
  width: 100%; border-radius: 14px; overflow: hidden;
  border: 1px solid var(--line); box-shadow: 0 8px 30px rgba(0,0,0,.35);
}
.nr-fp-caption {
  font-family: var(--ui); font-size: 12px; color: var(--muted);
  margin-top: 10px; display: flex; gap: 14px; flex-wrap: wrap;
}

/* ── Palette ── */
.nr-palette { display: flex; gap: 8px; }
.nr-swatch {
  flex: 1; height: 88px; border-radius: 12px;
  transition: transform .18s ease; cursor: default;
}
.nr-swatch:hover { transform: translateY(-4px); }
.nr-hexrow { display: flex; gap: 8px; margin-top: 8px; }
.nr-hex {
  flex: 1; text-align: center; font-family: var(--ui);
  font-size: 11px; color: var(--muted); letter-spacing: .04em;
}

/* ── Emotion bars ── */
.nr-row { display: flex; align-items: center; gap: 12px; margin-bottom: 9px; }
.nr-row-label { width: 92px; font-family: var(--ui); font-size: 13px; color: var(--text); }
.nr-track { flex: 1; background: rgba(255,255,255,.06); border-radius: 6px; height: 8px; overflow: hidden; }
.nr-fill { height: 8px; border-radius: 6px; }
.nr-pct { width: 38px; text-align: right; font-family: var(--ui); font-size: 12px; color: var(--muted); }

/* ── Dominant chip ── */
.nr-dom { padding: 20px 22px; border-radius: 14px; }
.nr-dom .em { font-family: var(--display); font-size: 30px; font-weight: 600; }
.nr-dom .pct { font-family: var(--ui); font-size: 13px; color: var(--muted); margin-top: 2px; }

/* ── Prose surfaces (shading / keywords) ── */
.nr-prose {
  font-family: var(--prose); font-size: 17px; line-height: 2.0;
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 14px; padding: 20px 24px; color: var(--text);
}

/* ── Sentence breakdown rows ── */
.nr-sent { font-family: var(--prose); font-size: 15px; line-height: 1.5; margin: 9px 0; color: var(--text); }
.nr-badge {
  font-family: var(--ui); font-weight: 600; font-size: 11px;
  padding: 2px 9px; border-radius: 8px; color: #16151D; margin-right: 8px;
}

/* ── Text area ── */
[data-testid="stTextArea"] textarea {
  background: var(--surface) !important; color: var(--text) !important;
  border: 1px solid var(--line) !important; border-radius: 14px !important;
  font-family: var(--prose) !important; font-size: 17px !important; line-height: 1.7 !important;
  padding: 16px 18px !important;
}
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 2px rgba(230,192,121,.22) !important;
}
[data-testid="stTextArea"] textarea::placeholder { color: #6c6678 !important; }

/* ── Buttons: example chips (secondary) + primary CTA ── */
.stButton button {
  font-family: var(--ui) !important; font-size: 13px !important; font-weight: 500 !important;
  border-radius: 999px !important; padding: 5px 16px !important;
  background: transparent !important; color: var(--muted) !important;
  border: 1px solid var(--line) !important; transition: all .15s ease !important;
}
.stButton button:hover {
  color: var(--text) !important; border-color: var(--gold) !important;
}
.stButton button[kind="primary"] {
  background: var(--gold) !important; color: #1A1620 !important;
  border: none !important; font-weight: 600 !important; padding: 6px 22px !important;
}
.stButton button[kind="primary"]:hover { filter: brightness(1.08) !important; }

/* ── Footer ── */
.nr-foot {
  font-family: var(--ui); font-size: 12px; color: var(--muted);
  border-top: 1px solid var(--line); margin-top: 38px; padding-top: 20px;
  display: flex; gap: 18px; flex-wrap: wrap; align-items: center;
}
.nr-foot a { color: var(--gold); text-decoration: none; }
.nr-foot a:hover { text-decoration: underline; }

@media (prefers-reduced-motion: reduce) {
  .nr-swatch, .stButton button { transition: none !important; }
}
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _hero_strip() -> str:
    cols = build_fingerprint(HERO_TEXT, mode="fast", max_columns=110)
    return fingerprint_svg(cols, width=860, height=64) if cols else ""


if "text" not in st.session_state:
    st.session_state.text = ""
if "run" not in st.session_state:
    st.session_state.run = False

def _load_example(passage: str):
    st.session_state.text = passage
    st.session_state.run = True

def _on_generate():
    st.session_state.run = True


with st.sidebar:
    st.markdown("#### Settings")
    has_tf = transformers_available()

    mode_labels = {"fast": "Fast · keyword lexicon"}
    if has_tf:
        mode_labels["balanced"] = "Balanced · local transformer"
    mode_labels["precise"] = "Precise · Claude API"

    default_mode = "balanced" if has_tf else "fast"
    mode = st.selectbox(
        "Analysis mode",
        options=list(mode_labels.keys()),
        format_func=lambda x: mode_labels[x],
        index=list(mode_labels.keys()).index(default_mode),
    )

    if mode == "balanced":
        st.caption("First analysis loads the model (~20–40s), then it's instant.")
    if mode == "precise":
        api_key = st.text_input("Anthropic API key", type="password", placeholder="sk-ant-…")
        if api_key:
            import os; os.environ["ANTHROPIC_API_KEY"] = api_key
        st.caption("Your key is used only for this session.")
    if not has_tf:
        st.caption("Balanced mode is hidden — install torch + transformers to enable it.")

    n_colors = st.slider("Palette size", 3, 8, 5)

    st.markdown("---")
    st.markdown(
        "**How the color is built**\n\n"
        "- **Hue** ← dominant emotion\n"
        "- **Saturation** ← intensity\n"
        "- **Lightness** ← positive / negative balance"
    )


st.markdown(
    '<div class="nr-mark"><span class="dot">◆</span> Narrative Resonance</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<h1 class="nr-hero-title">Every story has a <em>color.</em></h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="nr-hero-sub">Paste a passage of prose and see its emotional shape — '
    'rendered as a palette, an arc across the sentences, and a single-strip '
    'fingerprint of the whole text.</p>',
    unsafe_allow_html=True,
)

hero_svg = _hero_strip()
if hero_svg:
    st.markdown(f'<div class="nr-fp-frame">{hero_svg}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="nr-fp-caption"><span>↑ a live fingerprint — dread easing into hope, '
        'then warmth</span><span>·</span><span>12 emotions, hybrid model + lexicon</span></div>',
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)


st.text_area(
    "Your text",
    key="text",
    placeholder="Paste a paragraph of narrative prose…",
    height=140,
    label_visibility="collapsed",
)

c = st.columns([0.7, 1.1, 1.1, 1.1, 2.2, 1.4])
with c[0]:
    st.markdown(
        "<div style='font-family:Inter;font-size:13px;color:#9A93A8;padding-top:7px;'>Try:</div>",
        unsafe_allow_html=True,
    )
for i, (label, passage) in enumerate(EXAMPLES.items()):
    with c[i + 1]:
        st.button(label, on_click=_load_example, args=(passage,), use_container_width=True)
with c[5]:
    st.button("Read →", type="primary", on_click=_on_generate, use_container_width=True)


def _eyebrow(label: str):
    st.markdown(f'<div class="nr-eyebrow">{label}</div>', unsafe_allow_html=True)

if st.session_state.run and st.session_state.text.strip():
    text_input = st.session_state.text

    with st.spinner("Reading…"):
        result = text_to_palette(text_input, n_colors=n_colors, mode=mode)
        sentence_data = analyze_emotions_by_sentence(text_input, mode=mode)

    emotions = result["emotions"]
    palette = result["palette"]
    dom = result["dominant_emotion"]
    dom_color = EMOTION_DISPLAY_COLORS.get(dom, "#888")

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)


    fp_cols = build_fingerprint(text_input, mode=mode, max_columns=120)
    if fp_cols:
        _eyebrow("Fingerprint")
        fp_svg = fingerprint_svg(fp_cols, width=860, height=86)
        st.markdown(f'<div class="nr-fp-frame">{fp_svg}</div>', unsafe_allow_html=True)
        present, seen = [], set()
        for col in fp_cols:
            if col["dominant"] not in seen and col["intensity"] > 0.05:
                seen.add(col["dominant"]); present.append(col["dominant"])
        legend = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:5px;">'
            f'<span style="width:10px;height:10px;border-radius:3px;'
            f'background:{EMOTION_DISPLAY_COLORS.get(e, "#888")};"></span>{e.capitalize()}</span>'
            for e in present
        )
        st.markdown(f'<div class="nr-fp-caption">{legend}</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)


    _eyebrow("Palette")
    swatches = '<div class="nr-palette">' + "".join(
        f'<div class="nr-swatch" style="background:{col};" title="{col}"></div>' for col in palette
    ) + "</div>"
    hexes = '<div class="nr-hexrow">' + "".join(
        f'<div class="nr-hex">{col}</div>' for col in palette
    ) + "</div>"
    st.markdown(swatches + hexes, unsafe_allow_html=True)
    css_vars = "\n".join(f"  --palette-{i+1}: {col};" for i, col in enumerate(palette))
    with st.expander("Copy as CSS variables"):
        st.code(f":root {{\n{css_vars}\n}}", language="css")
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)


    left, right = st.columns([1.3, 1])
    with left:
        _eyebrow("Breakdown")
        sorted_em = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        bars = ""
        for em, score in sorted_em:
            if score < 0.02:
                continue
            pct = int(score * 100)
            bars += (
                f'<div class="nr-row">'
                f'<span class="nr-row-label">{em.capitalize()}</span>'
                f'<div class="nr-track"><div class="nr-fill" '
                f'style="width:{pct}%;background:{EMOTION_DISPLAY_COLORS.get(em, "#888")};"></div></div>'
                f'<span class="nr-pct">{pct}%</span></div>'
            )
        st.markdown(bars, unsafe_allow_html=True)
    with right:
        _eyebrow("Dominant")
        st.markdown(
            f'<div class="nr-dom" style="background:{dom_color}1f;border-left:3px solid {dom_color};">'
            f'<div class="em" style="color:{dom_color};">{dom.capitalize()}</div>'
            f'<div class="pct">{result["dominant_score"]*100:.0f}% intensity</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)


    _eyebrow("Arc")
    if len(sentence_data) < 2:
        st.markdown(
            '<p class="nr-hero-sub" style="font-size:15px;">Add a few more sentences to '
            'see emotion move across the text.</p>', unsafe_allow_html=True,
        )
    else:
        labels = [f"S{i+1}" for i in range(len(sentence_data))]
        fig = go.Figure()
        for em in EMOTIONS:
            scores = [item["emotions"].get(em, 0) for item in sentence_data]
            if max(scores) <= 0.1:
                continue
            fig.add_trace(go.Scatter(
                x=labels, y=scores, mode="lines+markers", name=em.capitalize(),
                line=dict(width=2, color=EMOTION_DISPLAY_COLORS.get(em, "#888"), shape="spline"),
                marker=dict(size=6),
                hovertemplate="<b>%{x}</b> · %{y:.0%}<extra></extra>",
            ))
        fig.update_layout(
            height=320, margin=dict(l=8, r=8, t=8, b=8), hovermode="x unified",
            yaxis=dict(range=[0, 1], tickformat=".0%", gridcolor="rgba(255,255,255,.05)"),
            xaxis=dict(gridcolor="rgba(255,255,255,.05)"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=-0.2, font=dict(color="#9A93A8")),
            font=dict(family="Inter", size=12, color="#ECE8F0"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with st.expander("Sentence-by-sentence"):
            for i, item in enumerate(sentence_data):
                badge = (
                    f'<span class="nr-badge" style="background:{item["color"]};">'
                    f'{item["dominant"].capitalize()} {item["dominant_score"]*100:.0f}%</span>'
                )
                st.markdown(
                    f'<div class="nr-sent"><b style="color:#9A93A8;font-family:Inter;'
                    f'font-size:12px;">S{i+1}</b> &nbsp;{badge}{item["sentence"]}</div>',
                    unsafe_allow_html=True,
                )
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)


    _eyebrow("Shaded text")
    shaded = shade_sentences_html(text_input, sentence_data)
    st.markdown(f'<div class="nr-prose">{shaded}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)


    _eyebrow("Keywords")
    highlighted = highlight_keywords_html(text_input, sentence_data)
    st.markdown(f'<div class="nr-prose">{highlighted}</div>', unsafe_allow_html=True)

elif st.session_state.run:
    st.markdown(
        '<p class="nr-hero-sub" style="font-size:15px;">Paste a passage above, or tap an '
        'example, then press Read.</p>', unsafe_allow_html=True,
    )


st.markdown(
    f'<div class="nr-foot">'
    f'<span>Narrative Resonance</span><span>·</span>'
    f'<span>12-emotion hybrid engine — local transformer corrected by a weighted lexicon, '
    f'with negation handling</span><span>·</span>'
    f'<a href="{REPO_URL}" target="_blank">Source on GitHub</a>'
    f'</div>',
    unsafe_allow_html=True,
)
