import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from retrieval_engine.rag_engine import load_all_documents, build_vector_store, build_qa_chain

st.set_page_config(
    page_title="Nedbank Banking Compliance Assistant",
    page_icon="🏦",
    layout="wide"
)

# --- Nedbank Colour Scheme ---
# Primary green: #007B40
# Dark green: #005A2B
# Light green: #E8F5EE
# White: #FFFFFF
# Dark text: #1A1A1A
# Gray: #6B7280

st.markdown("""
<style>
    /* Global */
    .main { background-color: #F4F6F5; }
    .block-container { padding-top: 0rem; padding-left: 1rem; padding-right: 1rem; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #005A2B !important;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #007B40 !important;
    }

    /* Portfolio disclaimer */
    .disclaimer-banner {
        background: #FFF8E1;
        border-left: 4px solid #F59E0B;
        border-radius: 4px;
        padding: 10px 16px;
        font-size: 12px;
        color: #92400E;
        margin-bottom: 0px;
    }

    /* Header bar */
    .nedbank-header {
        background: linear-gradient(135deg, #005A2B 0%, #007B40 100%);
        padding: 20px 32px;
        border-radius: 0px;
        margin-bottom: 0px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .nedbank-header h1 {
        color: #ffffff !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    .nedbank-header p {
        color: #A7F3C0 !important;
        font-size: 13px !important;
        margin: 0 !important;
    }

    /* Doc card in sidebar */
    .doc-card {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 8px;
        display: flex;
        align-items: flex-start;
        gap: 10px;
    }
    .doc-name { color: #ffffff !important; font-weight: 600; font-size: 13px; }
    .doc-type { color: #A7F3C0 !important; font-size: 11px; margin-top: 2px; }

    /* Security warning */
    .warning-box {
        background: #E8F5EE;
        border: 1px solid #007B40;
        border-radius: 6px;
        padding: 10px 16px;
        font-size: 12px;
        color: #005A2B;
        margin-bottom: 12px;
    }
    /* Success box */
    .stAlert { border-radius: 6px !important; }

    /* Suggested question buttons */
    .stButton > button {
        background-color: #ffffff !important;
        border: 1px solid #007B40 !important;
        color: #005A2B !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background-color: #007B40 !important;
        color: #ffffff !important;
    }

    /* Chat messages */
    .stChatMessage { border-radius: 10px !important; }

    /* Badge */
    .badge {
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 12px;
        color: #ffffff;
        display: inline-block;
    }

    /* Footer */
    .footer-text { font-size: 12px; color: #6B7280; }

    /* Divider color */
    hr { border-color: #007B40 !important; }
</style>
""", unsafe_allow_html=True)

# --- Document metadata ---
DOCUMENTS = [
    {"name": "Nedbank 2024 Integrated Report", "file": "2024-integrated-report-nedbank.pdf", "type": "Strategy & Governance", "icon": "📊"},
    {"name": "Nedbank 2024 Annual Results", "file": "2024-annual-results-booklet-nedbank.pdf", "type": "Financial Results", "icon": "💰"},
    {"name": "Nedbank 2024 Financial Statements", "file": "2024-annual-financial-statements-nedbank-limited.pdf", "type": "Audited Financials", "icon": "📋"},
    {"name": "POPIA — Protection of Personal Information Act", "file": "Popia-Act.pdf", "type": "Regulatory Compliance", "icon": "🔒"},
    {"name": "BCBS 239 — Banking Data Principles", "file": "bcbs-239.pdf", "type": "Data Governance", "icon": "🏛️"},
    {"name": "Nedbank 2022 Factsheet", "file": "nedbank-factsheet.pdf", "type": "Company Overview & History", "icon": "📑"},
    {"name": "Nedbank Historical Firsts", "file": "nedbank-firsts.pdf", "type": "Corporate History", "icon": "📜"},
]

# --- Load RAG pipeline ---
@st.cache_resource(show_spinner=False)
def initialize_rag(version="v3-nedbank"):
    text = load_all_documents("documents")
    vector_store = build_vector_store(text)
    qa_chain = build_qa_chain(vector_store)
    return qa_chain

# --- Portfolio Disclaimer ---
st.markdown("""
<div class="disclaimer-banner">
<strong>Portfolio Project Disclaimer:</strong> This is an independent portfolio project built by
<strong>Thobani Antony Zondi</strong> to demonstrate RAG and GenAI capabilities using publicly available
Nedbank documents. It is <strong>not an official Nedbank product</strong> and is not affiliated with or
endorsed by Nedbank Group Limited.
</div>
""", unsafe_allow_html=True)

# --- Nedbank-styled Header ---
st.markdown(f"""
<div class="nedbank-header">
    <div style="font-size:48px">🏦</div>
    <div>
        <h1>Nedbank Banking Compliance & Intelligence Assistant</h1>
        <p>Powered by {len(DOCUMENTS)} verified Nedbank documents · POPIA · BCBS 239 · Answers grounded in official documents only</p>
    </div>
    <div style="margin-left:auto">
        <span class="badge">Secure · Document-Grounded</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🏦 Nedbank Assistant")
    st.markdown("---")
    st.markdown("### Loaded Documents")
    st.markdown("")
    for doc in DOCUMENTS:
        st.markdown(f"""
        <div class="doc-card">
            <span style="font-size:20px">{doc['icon']}</span>
            <div>
                <div class="doc-name">{doc['name']}</div>
                <div class="doc-type">{doc['type']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Security Guardrails")
    st.markdown("""
    - Document-grounded answers only
    - No hallucination policy
    - Source citation required
    - No financial advice given
    - POPIA-aware responses
    - No PII exposure
    """)
    st.markdown("---")
    st.markdown("### ℹDisclaimer")
    st.caption("""This assistant provides information from loaded public documents only.
    It does not constitute financial, legal, or regulatory advice.
    Always consult qualified professionals for formal guidance.""")
    st.markdown("---")
    st.caption("Built by Thobani Antony Zondi")
    st.caption("[GitHub](https://github.com/thobanizondi) · [Portfolio](https://datascienceportfol.io/thobanizondi)")

# --- Load pipeline ---
with st.spinner(f"Loading {len(DOCUMENTS)} banking documents and building secure RAG pipeline..."):
    qa_chain = initialize_rag()

st.success(f"{len(DOCUMENTS)} banking documents loaded and verified — answers are document-grounded only")

# --- Security warning ---
st.markdown(f"""
<div class="warning-box">
<strong>Security Notice:</strong> This assistant only answers questions based on the {len(DOCUMENTS)} loaded documents.
Responses do not constitute financial, legal, or regulatory advice.
Always verify with qualified professionals before making compliance or investment decisions.
</div>
""", unsafe_allow_html=True)

# --- Chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Suggested questions ---
suggested = [
    "What are the BCBS 239 data governance principles?",
    "What does POPIA say about personal data processing?",
    "What was Nedbank's headline earnings in 2024?",
    "What is Nedbank's AI and data strategy?",
    "What are the key risks Nedbank faced in 2024?",
    "What does BCBS 239 say about data lineage?",
    "When was Nedbank founded?",
    "What are Nedbank's ESG commitments?",
]

if not st.session_state.messages:
    st.markdown("#### Suggested Compliance Questions")
    cols = st.columns(2)
    for i, q in enumerate(suggested):
        if cols[i % 2].button(q, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": q})
            with st.chat_message("user"):
                st.markdown(q)
            with st.chat_message("assistant"):
                with st.spinner("Searching documents..."):
                    answer = qa_chain(q)
                    st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()

# --- Chat input ---
if prompt := st.chat_input("Ask about banking compliance, POPIA, BCBS 239, or Nedbank reports..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            answer = qa_chain(prompt)
            st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()

# --- Footer ---
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<p class="footer-text">Document-grounded responses only</p>', unsafe_allow_html=True)
with col2:
    st.markdown('<p class="footer-text" style="text-align:center">Built with LangChain · Groq LLaMA3 · FAISS · Streamlit</p>', unsafe_allow_html=True)
with col3:
    st.markdown('<p class="footer-text" style="text-align:right"><a href="https://github.com/thobanizondi">GitHub</a> · <a href="https://datascienceportfol.io/thobanizondi">Portfolio</a></p>', unsafe_allow_html=True)