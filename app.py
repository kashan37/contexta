import streamlit as st
from src.chat_engine import ChatEngine
import tempfile
from pathlib import Path
import time

favicon_path = Path("assets/favicon.png")
page_icon = str(favicon_path) if favicon_path.exists() else "📄"

st.set_page_config(
    page_title="Document Chat - AI Assistant",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- Load CSS ----------
css_file = Path("assets/style.css")
if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- Session State ----------
if "engine" not in st.session_state:
    st.session_state.engine = ChatEngine()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "document_loaded" not in st.session_state:
    st.session_state.document_loaded = False

if "file_name" not in st.session_state:
    st.session_state.file_name = None

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

# ---------- Header ----------
st.markdown("""
<div class="header-container">
    <div class="header-content">
        <div class="logo-section">
            <span class="logo-icon">✦</span>
            <span class="logo-text">Document Chat</span>
        </div>
        <div class="header-badge">
            <span class="badge-dot"></span>
            AI Powered
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- Info Banner (persistent, compact — replaces the old giant hero) ----------
if st.session_state.document_loaded:
    banner_icon = "✅"
    banner_text = f"<b>{st.session_state.file_name}</b>  is loaded — ask anything below, answers are grounded only in this document."
else:
    banner_icon = "📄"
    banner_text = "Upload a PDF on the left, then ask anything about it — instant, grounded answers only from your document."

st.markdown(f"""
<div class="info-banner">
    <span class="info-banner-icon">{banner_icon}</span>
    <span class="info-banner-text">{banner_text}</span>
</div>
""", unsafe_allow_html=True)

# ---------- Main Layout ----------
col_left, col_right = st.columns([1, 2.5], gap="large")

# ---------- SIDEBAR / LEFT PANEL ----------
with col_left:
    st.markdown("""
    <div class="panel-card">
        <div class="panel-header">
            <span class="panel-icon">📄</span>
            <span class="panel-title">Document</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload Area
    uploaded_file = st.file_uploader(
        "",
        type=["pdf"],
        label_visibility="collapsed",
        key="pdf_uploader"
    )
    
    if uploaded_file:
        if st.session_state.file_name != uploaded_file.name:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                temp_path = tmp.name
            
            with st.spinner(""):
                progress_bar = st.progress(0, text="Processing document...")
                pages = st.session_state.engine.load_document(temp_path)
                progress_bar.progress(100, text="Complete!")
                time.sleep(0.3)
                progress_bar.empty()
            
            st.session_state.document_loaded = True
            st.session_state.file_name = uploaded_file.name
            st.session_state.messages = []
            st.session_state.chat_started = False
            st.rerun()
    
    # Document Info
    if st.session_state.document_loaded:
        st.markdown(f"""
        <div class="doc-info">
            <div class="doc-info-item">
                <span class="doc-info-label">Status</span>
                <span class="doc-info-value active">● Ready</span>
            </div>
            <div class="doc-info-item">
                <span class="doc-info-label">File</span>
                <span class="doc-info-value">{st.session_state.file_name}</span>
            </div>
            <div class="doc-info-item">
                <span class="doc-info-label">Messages</span>
                <span class="doc-info-value">{len(st.session_state.messages)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Actions
    st.markdown("""
    <div class="panel-header" style="margin-top: 24px;">
        <span class="panel-icon">⚡</span>
        <span class="panel-title">Actions</span>
    </div>
    """, unsafe_allow_html=True)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🗑️ Clear", use_container_width=True, key="clear_btn"):
            st.session_state.messages = []
            st.session_state.chat_started = False
            st.session_state.engine.history = []
            st.rerun()
    
    with col_btn2:
        if st.button("🔄 New", use_container_width=True, key="new_doc_btn"):
            st.session_state.document_loaded = False
            st.session_state.file_name = None
            st.session_state.messages = []
            st.session_state.chat_started = False
            st.session_state.engine.history = []
            st.rerun()
    
    # Tips
    if st.session_state.document_loaded:
        st.markdown("""
        <div class="tips-section">
            <div class="tips-header">
                <span class="tips-icon">💡</span>
                <span class="tips-title">Tips</span>
            </div>
            <div class="tip-item-mini">
                <span>Ask specific questions</span>
            </div>
            <div class="tip-item-mini">
                <span>Request summaries</span>
            </div>
            <div class="tip-item-mini">
                <span>Find key information</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="panel-footer">
        <div class="footer-item">
            <span class="footer-icon">🔒</span>
            <span>Secure</span>
        </div>
        <div class="footer-item">
            <span class="footer-icon">⚡</span>
            <span>Fast</span>
        </div>
        <div class="footer-item">
            <span class="footer-icon">🤖</span>
            <span>AI</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------- MAIN CHAT AREA ----------
with col_right:
    if st.session_state.document_loaded:
        # Chat Header
        st.markdown(f"""
        <div class="chat-header">
            <div class="chat-header-left">
                <span class="chat-status-dot"></span>
                <span class="chat-status-text">Ready to chat</span>
                <span class="memory-badge" title="I remember the last few messages, so follow-ups work">🧠 Remembers context</span>
            </div>
            <div class="chat-header-right">
                <span class="chat-message-count">{len(st.session_state.messages)} messages</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat Container with fixed height and auto-scroll
        st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
        
        suggestion_clicked = None
        
        if not st.session_state.messages:
            # Welcome message when document is loaded but no chat yet
            st.markdown("""
            <div class="chat-welcome">
                <div class="chat-welcome-icon">👋</div>
                <h3>Start asking questions</h3>
                <p>Ask me anything about your document. I'll help you find the information you need.</p>
            </div>
            """, unsafe_allow_html=True)
            
            sugg_col1, sugg_col2, sugg_col3 = st.columns(3)
            suggestions = [
                (sugg_col1, "📝", "Summarize this document"),
                (sugg_col2, "🔍", "What are the key points?"),
                (sugg_col3, "📊", "Explain the main concepts"),
            ]
            for col, icon, text in suggestions:
                with col:
                    if st.button(f"{icon} {text}", key=f"suggestion_{text}", use_container_width=True):
                        suggestion_clicked = text
        else:
            # Messages
            for role, content in st.session_state.messages:
                with st.chat_message(role):
                    st.markdown(content)

            # Quick follow-up chips — only after the latest answer, nudging people
            # toward the fact that follow-ups actually work now
            if st.session_state.messages[-1][0] == "assistant":
                followup_col1, followup_col2, followup_col3 = st.columns(3)
                followups = [
                    (followup_col1, "🔍", "Tell me more about that"),
                    (followup_col2, "✨", "Simplify that"),
                    (followup_col3, "💡", "Give me an example"),
                ]
                for col, icon, text in followups:
                    with col:
                        if st.button(f"{icon} {text}", key=f"followup_{text}_{len(st.session_state.messages)}", use_container_width=True):
                            suggestion_clicked = text
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat Input - Always visible at bottom
        st.markdown('<div class="chat-input-wrapper">', unsafe_allow_html=True)
        typed_prompt = st.chat_input("Ask a question about your document...", key="chat_input")
        st.markdown('</div>', unsafe_allow_html=True)
        
        prompt = suggestion_clicked or typed_prompt
        
        if prompt:
            st.session_state.messages.append(("user", prompt))
            st.session_state.chat_started = True
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.spinner(""):
                answer = st.session_state.engine.ask(prompt)
            
            st.session_state.messages.append(("assistant", answer))
            st.rerun()
    else:
        # Show upload prompt in chat area
        st.markdown("""
        <div class="upload-prompt">
            <div class="upload-prompt-icon">📤</div>
            <h3>Upload a Document to Get Started</h3>
            <p>Use the panel on the left to upload a PDF file.</p>
            <div class="upload-prompt-steps">
                <div class="step">
                    <span class="step-number">1</span>
                    <span>Click "Upload" or drag & drop a PDF</span>
                </div>
                <div class="step">
                    <span class="step-number">2</span>
                    <span>Wait for processing (usually a few seconds)</span>
                </div>
                <div class="step">
                    <span class="step-number">3</span>
                    <span>Start asking questions about your document</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)