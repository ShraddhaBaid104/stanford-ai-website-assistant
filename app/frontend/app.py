"""
Stanford AI Website Assistant
Production Streamlit Frontend

Author: Shraddha Nahata
"""

import uuid
import streamlit as st

from api import (
    stream_answer,
    get_citations,
)
from config import PAGE_TITLE

# -------------------------------------------------------
# Page Configuration
# -------------------------------------------------------

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🎓",
    layout="wide",
)

# -------------------------------------------------------
# Session State
# -------------------------------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------

with st.sidebar:

    st.title("🎓 Stanford AI")

    st.caption("Production RAG Assistant")

    st.divider()

    if st.button("🆕 New Chat", use_container_width=True):

        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    if st.button("🗑 Clear Conversation", use_container_width=True):

        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.subheader("💡 Suggested Questions")

    suggestions = [
        "What is Stanford University?",
        "How do I apply to Stanford?",
        "What courses does Stanford offer?",
        "Tell me about Stanford research.",
        "What is Stanford known for?",
    ]

    for q in suggestions:

        if st.button(q, use_container_width=True):
            st.session_state["suggested_question"] = q

    st.divider()

    st.subheader("📊 Conversation")

    user_messages = sum(
        1
        for m in st.session_state.messages
        if m["role"] == "user"
    )

    assistant_messages = sum(
        1
        for m in st.session_state.messages
        if m["role"] == "assistant"
    )

    st.metric("Questions", user_messages)
    st.metric("Responses", assistant_messages)

    st.caption("Session ID")

    st.code(
        st.session_state.session_id[:8],
        language=None,
    )

# -------------------------------------------------------
# Header
# -------------------------------------------------------

st.title("🎓 Stanford AI Website Assistant")

st.caption(
    "Ask questions about Stanford University using a production RAG pipeline."
)

st.divider()

# -------------------------------------------------------
# Suggested Question
# -------------------------------------------------------

if "suggested_question" in st.session_state:

    prompt = st.session_state.pop("suggested_question")

else:

    prompt = None

# -------------------------------------------------------
# Display Previous Messages
# -------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            citations = message.get("citations", [])

            if citations:

                with st.expander("📚 Sources", expanded=False):

                    for citation in citations:

                        st.markdown(
                            f"**{citation['title']}**"
                        )

                        st.markdown(
                            citation["url"]
                        )

                        if citation.get("score") is not None:

                            st.caption(
                                f"Score: {citation['score']:.3f}"
                            )

                        st.divider()

# -------------------------------------------------------
# Chat Input
# -------------------------------------------------------

user_input = st.chat_input(
    "Ask a question about Stanford..."
)

if user_input:
    prompt = user_input

# -------------------------------------------------------
# Send Question
# -------------------------------------------------------

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        placeholder = st.empty()

        try:

            answer = ""

            for chunk in stream_answer(
                    st.session_state.session_id,
                    prompt,
            ):
                answer += chunk
                placeholder.markdown(answer + "▌")

            placeholder.markdown(answer)

            metadata = get_citations(
                st.session_state.session_id,
            )

            citations = metadata.get(
                "citations",
                [],
            )

            if citations:

                st.divider()

                with st.expander(
                        "📚 Sources",
                        expanded=False,
                ):

                    for citation in citations:

                        st.markdown(
                            f"**{citation['title']}**"
                        )

                        st.markdown(
                            citation["url"]
                        )

                        if citation.get("score") is not None:
                            st.caption(
                                f"Relevance: {citation['score']:.3f}"
                            )
        except Exception as exc:

            answer = (
                "❌ Unable to contact the backend.\n\n"
                f"{exc}"
            )

            citations = []

            placeholder.error(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "citations": citations,
        }
    )

# -------------------------------------------------------
# Footer
# -------------------------------------------------------

st.divider()

st.caption(
    "Stanford AI Website Assistant • Production RAG • FastAPI • LangChain • OpenAI • ChromaDB • Redis"
)