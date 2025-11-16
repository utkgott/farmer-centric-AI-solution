# pages/1_AI_Assistant_openai.py
import streamlit as st
import os
import traceback
import openai

# ---------------- CONFIG ----------------
# Put your OpenAI API key here for local testing:
OPENAI_API_KEY = "your-API"
# Choose OpenAI model (use a smaller/cheaper model for demos)
# Examples: "gpt-4o-mini", "gpt-4o", "gpt-4o-mini-unstable", "gpt-3.5-turbo"
OPENAI_MODEL = "gpt-4o-mini"
# ----------------------------------------

st.set_page_config(page_title="AI Assistant (OpenAI)", page_icon="🤖", layout="centered")
st.title("AI Assistant — (OpenAI fallback for demo)")
st.write("Using OpenAI for inference (uses local OpenAI credits). Replace API key locally before running.")

prompt = st.text_area("Enter your prompt (single-turn):", value="Explain what crop rotation is in simple terms.", height=160)
max_tokens = st.slider("Max tokens (approx response length)", 32, 1024, 256, 32)
temperature = st.slider("Temperature", 0.0, 1.2, 0.7, 0.1)
run = st.button("Generate")

if run:
    if not prompt.strip():
        st.warning("Please enter a prompt.")
        st.stop()

    if OPENAI_API_KEY == "sk_your_openai_key_here" or not OPENAI_API_KEY.strip():
        st.error("OpenAI API key not set. Edit this file and put your key in OPENAI_API_KEY.")
        st.stop()

    openai.api_key = OPENAI_API_KEY
    try:
        with st.spinner("Calling OpenAI..."):
            # Use Chat Completions
            resp = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers in clear, simple English."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            # Extract text
            text = resp["choices"][0]["message"]["content"]
            st.success("✅ Response (OpenAI)")
            st.markdown(text)

            # optional: show usage/cost info
            if "usage" in resp:
                usage = resp["usage"]
                st.caption(f"Tokens — prompt: {usage.get('prompt_tokens')}, completion: {usage.get('completion_tokens')}, total: {usage.get('total_tokens')}")
    except Exception as e:
        st.error("OpenAI API error. See details below.")
        st.write(type(e).__name__, str(e))
        st.expander("Traceback").write(traceback.format_exc())
    except Exception as e:
        st.error("Unexpected error while calling OpenAI.")
        st.write(type(e).__name__, str(e))
        st.expander("Traceback").write(traceback.format_exc())
