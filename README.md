# 🤖 Chatbox AI — Multilingual Hybrid Chatbot

A chatbot that combines fast local retrieval with LLM-powered fallback, so it can answer both predefined questions instantly and truly open-ended questions in any language.

**Live demo:** *(add your Streamlit app link here)*

## How it works

This isn't a single-technique chatbot — it's a layered pipeline:

## Why this architecture

Most beginner chatbots pick one extreme: pure rule-based (doesn't scale) or a thin LLM API wrapper (no custom logic). This project routes intelligently — cheap, fast, local matching handles known questions instantly; the LLM is only called when genuinely needed. That's closer to how real production chat systems are designed.

## Tech stack

- **Retrieval:** scikit-learn (`TfidfVectorizer`, `cosine_similarity`)
- **Text preprocessing:** NLTK `PorterStemmer`, custom stopword filtering
- **Language support:** `langdetect`, `deep-translator`
- **LLM fallback:** Groq API (Llama 3.3 70B)
- **Web interface:** Streamlit
- **Deployment:** Streamlit Community Cloud

## Project evolution

This repo shows the full build progression, kept intentionally as separate files:

| File | What it demonstrates |
|---|---|
| `chatbox_v1` | Rule-based if-else matching |
| `chatbox_v2` | Dictionary-based lookup |
| `chatbox_v3`–`v4` | TF-IDF + cosine similarity retrieval |
| `chatbox_v5` | Added stemming for word-form matching |
| `chatbox_v6` | Added multilingual translation support |
| `chatbox_v7` | Added Groq LLM fallback for open-domain questions |
| `app.py` | Streamlit web interface |

## Run it locally

```bash
git clone https://github.com/Ajaybalu004/chatbox.git
cd chatbox
pip install -r requirements.txt
```

Create a `.env` file with your Groq API key:

Run the web app:
```bash
streamlit run app.py
```

## Known limitations

- LLM responses reflect the model's training cutoff — may be outdated for current events
- Language detection can be unreliable on very short inputs (under ~15 characters)
- Translation quality depends on Google Translate's API

## Author

Built by Ajay — AI/ML Engineering graduate.
