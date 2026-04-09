import streamlit as st
import time
from create_api import deploy_code
from history_manager import load_history, delete_from_history, clear_all_history

# -------------------------------------------------------
# PAGE CONFIG — must be the very first Streamlit command
# -------------------------------------------------------
st.set_page_config(
    page_title="ZenLegacy API Marketplace",
    page_icon="⚡",
    layout="wide",                  # use full browser width
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------
# CUSTOM CSS — makes it look professional
# -------------------------------------------------------
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0f1117;
        color: #e0e0e0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2e3140;
    }

    /* Big title */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #7c6afe, #5eead4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Status step cards */
    .step-card {
        background: #1e2130;
        border: 1px solid #2e3140;
        border-radius: 10px;
        padding: 12px 18px;
        margin: 6px 0;
        font-size: 0.9rem;
    }

    .step-active {
        border-left: 3px solid #7c6afe;
        color: #c4b5fd;
    }

    .step-done {
        border-left: 3px solid #5eead4;
        color: #5eead4;
    }

    .step-waiting {
        color: #555;
    }

    /* API result card */
    .result-card {
        background: #1e2130;
        border: 1px solid #2e3140;
        border-radius: 12px;
        padding: 20px;
        margin-top: 1rem;
    }

    /* URL display box */
    .url-box {
        background: #12151f;
        border: 1px solid #3d4260;
        border-radius: 8px;
        padding: 12px 16px;
        font-family: monospace;
        font-size: 0.95rem;
        color: #7c6afe;
        margin: 6px 0;
    }

    /* History card */
    .history-card {
        background: #1a1d27;
        border: 1px solid #2e3140;
        border-radius: 10px;
        padding: 14px 16px;
        margin: 8px 0;
    }

    .history-prompt {
        font-weight: 600;
        font-size: 0.95rem;
        color: #c4b5fd;
    }

    .history-time {
        font-size: 0.78rem;
        color: #666;
        margin-top: 3px;
    }

    /* Badge */
    .badge-success {
        background: #0d2e1f;
        color: #5eead4;
        border: 1px solid #5eead4;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .badge-fail {
        background: #2e0d0d;
        color: #f87171;
        border: 1px solid #f87171;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* Hide default Streamlit menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------
# SIDEBAR — History of all generated APIs
# -------------------------------------------------------
with st.sidebar:
    st.markdown("## 📚 API History")
    st.markdown("Every API you generate is saved here.")
    st.divider()

    history = load_history()

    if not history:
        st.markdown('<p style="color:#555; font-size:0.9rem;">No APIs generated yet.<br>Go generate your first one!</p>', unsafe_allow_html=True)
    else:
        # Show newest first
        for entry in reversed(history):
            with st.expander(f"#{entry['id']} — {entry['prompt'][:35]}..."):
                st.markdown(f'<div class="history-time">🕐 {entry["timestamp"]}</div>', unsafe_allow_html=True)
                st.markdown(f'**Prompt:** {entry["prompt"]}')
                st.code(entry["code"], language="python")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔁 Re-deploy", key=f"redeploy_{entry['id']}"):
                        # Save the prompt to session so main area picks it up
                        st.session_state["redeploy_prompt"] = entry["prompt"]
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{entry['id']}"):
                        delete_from_history(entry["id"])
                        st.rerun()

        st.divider()
        if st.button("🧹 Clear All History", use_container_width=True):
            clear_all_history()
            st.rerun()

    st.divider()
    st.markdown('<p style="color:#444; font-size:0.78rem;">ZenLegacy API Marketplace<br>Powered by Llama3 + FastAPI</p>', unsafe_allow_html=True)


# -------------------------------------------------------
# MAIN AREA
# -------------------------------------------------------
st.markdown('<div class="main-title">⚡ ZenLegacy API Marketplace</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Describe an API in plain English. Get working Python code in seconds.</div>', unsafe_allow_html=True)

# PORT SETTING
port = st.number_input(
    "API Port",
    min_value=1024,
    max_value=65535,
    value=8000,
    help="The port your API will run on. Default is 8000."
)

# PROMPT INPUT
# If user clicked "Re-deploy" from history, pre-fill the input
default_prompt = st.session_state.get("redeploy_prompt", "API to store and retrieve employee data with name, role and salary")
if "redeploy_prompt" in st.session_state:
    del st.session_state["redeploy_prompt"]  # clear it after use

prompt = st.text_area(
    "📝 Describe your API",
    value=default_prompt,
    height=100,
    placeholder="e.g. API to manage a book library with title, author, and genre",
    help="Be specific! The more detail you give, the better the generated code."
)

# EXAMPLE PROMPTS — clickable shortcuts
st.markdown("**Quick examples:**")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("👤 User login API"):
        prompt = "API for user registration and login with username, email and password"
with col2:
    if st.button("📦 Product inventory API"):
        prompt = "API to manage product inventory with name, price, quantity and category"
with col3:
    if st.button("📝 Todo list API"):
        prompt = "API for a todo list app with tasks that have title, description and completed status"

st.divider()

# DEPLOY BUTTON
deploy_clicked = st.button("🚀 Deploy API", type="primary", use_container_width=True)

# -------------------------------------------------------
# DEPLOY LOGIC
# -------------------------------------------------------
if deploy_clicked:
    if not prompt.strip():
        st.error("⚠️ Please enter a description for your API first.")
    else:
        # Show animated status steps
        st.markdown("### 🔄 Generating your API...")

        status_box = st.empty()

        def show_status(step: int):
            steps = [
                ("🧠 Thinking about your requirements...", "active", "waiting", "waiting"),
                ("✍️ Writing Python code...",             "done",   "active",  "waiting"),
                ("💾 Saving and starting server...",      "done",   "done",    "active"),
            ]
            labels = ["Understanding prompt", "Writing code", "Deploying"]
            icons  = ["🧠", "✍️", "🚀"]

            html = ""
            for i, label in enumerate(labels):
                if i < step:
                    css = "step-card step-done"
                    icon = "✅"
                elif i == step:
                    css = "step-card step-active"
                    icon = icons[i]
                else:
                    css = "step-card step-waiting"
                    icon = "⏳"
                html += f'<div class="{css}">{icon} {label}</div>'

            status_box.markdown(html, unsafe_allow_html=True)

        show_status(0)
        time.sleep(0.8)
        show_status(1)

        # Actually generate the code (this is the slow AI step)
        result = deploy_code(user_prompt=prompt, port=int(port))

        show_status(2)
        time.sleep(0.5)

        # -------------------------------------------------------
        # SHOW RESULTS
        # -------------------------------------------------------
        if result["success"]:
            status_box.empty()
            st.success("✅ API deployed successfully!")

            # URLs
            st.markdown("### 🌐 Your API is live at:")
            local_url = f"http://127.0.0.1:{result['port']}"
            docs_url  = f"http://127.0.0.1:{result['port']}/docs"
            network_url = f"http://{result['ip']}:{result['port']}"

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="url-box">🏠 Local &nbsp;&nbsp;&nbsp; <a href="{local_url}" target="_blank">{local_url}</a></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="url-box">📖 Swagger <a href="{docs_url}" target="_blank">{docs_url}/docs</a></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="url-box">🌐 Network &nbsp;<a href="{network_url}" target="_blank">{network_url}</a></div>', unsafe_allow_html=True)
                st.info("Share the Network URL with others on your WiFi to let them test your API!")

            # Generated code display
            st.markdown("### 📄 Generated Code")
            st.markdown("This is the Python code the AI wrote for you. It's already saved to `main.py` and running.")
            st.code(result["code"], language="python")

            col_copy, col_download = st.columns(2)
            with col_download:
                st.download_button(
                    label="⬇️ Download main.py",
                    data=result["code"],
                    file_name="main.py",
                    mime="text/plain",
                    use_container_width=True
                )

            # How to use guide
            with st.expander("📖 How to test your API"):
                st.markdown(f"""
**Option 1 — Swagger UI (easiest)**
1. Open this link: [{docs_url}]({docs_url})
2. Click any endpoint (like POST /items/)
3. Click "Try it out"
4. Fill in the fields
5. Click "Execute"
6. See the response below

**Option 2 — From Python**
```python
import requests

# Create a new item
response = requests.post("{local_url}/items/", json={{
    "title": "My first item",
    "description": "Testing my API"
}})
print(response.json())

# Get all items
response = requests.get("{local_url}/items/")
print(response.json())
```

**Option 3 — From terminal (curl)**
```bash
# Create
curl -X POST "{local_url}/items/" -H "Content-Type: application/json" -d '{{"title":"Hello","description":"World"}}'

# Read all
curl "{local_url}/items/"
```
                """)

        else:
            # Something went wrong
            status_box.empty()
            st.error("❌ Something went wrong. See details below.")
            with st.expander("🔍 Error details"):
                st.code(result["error"])
            st.markdown("""
**Common fixes:**
- Make sure **Ollama is running**: open a terminal and type `ollama serve`
- Make sure **Llama3 is downloaded**: type `ollama pull llama3`
- Make sure the **port is not in use**: try changing the port number above
            """)
