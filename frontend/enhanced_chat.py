"""
Streamlit GUI for Cohere Chat API with Wikipedia Integration.

This module provides an interactive web-based chat interface using Streamlit
that connects to the Cohere Chat API backend with Wikipedia integration and
PostgreSQL chat history storage.

Features:
    - Interactive chat interface with real-time messaging
    - Wikipedia integration toggle for enhanced responses
    - Complete chat history viewer with PostgreSQL backend
    - API status monitoring and health checks
    - Configurable parameters (max tokens, temperature)
    - Pre-built example queries for quick testing
    - Responsive design with sidebar controls

Components:
    - Chat Interface: Real-time conversation with AI
    - Settings Panel: Configure API parameters and Wikipedia usage
    - History Manager: View and manage chat history from database
    - API Monitor: Real-time status of backend services
    - Quick Examples: Pre-built queries for testing

API Integration:
    Connects to FastAPI backend at http://localhost:8000
    - POST /api/v1/chat: Send chat messages
    - GET /api/v1/chat/history: Retrieve chat history
    - DELETE /api/v1/chat/history: Clear chat history
    - GET /api/v1/health: Check API and database status

Dependencies:
    - Streamlit: Web app framework
    - Requests: HTTP client for API calls
    - Pandas: Data manipulation for history display

Usage:
    Run with: streamlit run streamlit_app_enhanced.py --server.port 8501
    Access at: http://localhost:8501

Author: Cohere THA Project
Created: September 2025
."""

import streamlit as st
import requests
import pandas as pd
import logging
import os

# Configure logging for Streamlit app
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('streamlit_enhanced.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Log Streamlit app startup
logger.info("Starting Streamlit Enhanced Chat App")

# Page configuration
st.set_page_config(
    page_title="Cohere Chat with Wikipedia", page_icon="🤖", layout="wide"
)

# API Configuration
# Use environment variable for Docker, fallback to localhost for local development
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def call_chat_api(query, max_tokens=300, temperature=0.7, use_wikipedia=True):
    """Call the enhanced chat API."""
    logger.info(f"Calling chat API with query: '{query[:50]}...', wikipedia: {use_wikipedia}")
    url = f"{API_BASE_URL}/api/v1/chat"
    payload = {
        "query": query,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "use_wikipedia": use_wikipedia,
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            logger.info("Chat API call successful")
            return response.json()
        else:
            logger.error(f"Chat API error: {response.status_code} - {response.text}")
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to chat API")
        st.error(
            "Cannot connect to the API. Please ensure the Docker container is running."
        )
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def get_chat_history():
    """Get chat history from API."""
    logger.info("Fetching chat history")
    url = f"{API_BASE_URL}/api/v1/chat/history"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException:
        return None


def clear_chat_history():
    """Clear chat history."""
    logger.info("Clearing chat history via API")
    url = f"{API_BASE_URL}/api/v1/chat/history"
    try:
        response = requests.delete(url, timeout=10)
        success = response.status_code == 200
        if success:
            logger.info("Chat history cleared successfully")
        else:
            logger.warning(f"Failed to clear chat history: {response.status_code}")
        return success
    except requests.RequestException as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        return False


# Main App
def main():
    """Run the main Streamlit application with chat interface."""
    logger.info("Starting main Streamlit application")
    st.title("🤖 Cohere Chat with Wikipedia Integration")
    st.markdown("---")

    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")

        # API Configuration
        max_tokens = st.slider("Max Tokens", 50, 1000, 300)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        use_wikipedia = st.checkbox("Use Wikipedia Tool", value=True)

        st.markdown("---")

        # Chat History Management
        st.header("📚 Chat History")
        if st.button("📜 View Full History"):
            st.session_state.show_history = True

        if st.button("🗑️ Clear History"):
            if clear_chat_history():
                st.success("History cleared!")
                st.rerun()
            else:
                st.error("Failed to clear history")

        st.markdown("---")

        # API Status
        st.header("🔗 API Status")
        try:
            health_response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=5)
            if health_response.status_code == 200:
                health_data = health_response.json()
                st.success("✅ API Online")
                st.json(health_data)
            else:
                st.error("❌ API Offline")
        except requests.RequestException:
            st.error("❌ API Offline")

    # Main chat interface
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("💬 Chat Interface")

        # Initialize session state
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    if message.get("wikipedia_sources"):
                        st.markdown("**📖 Wikipedia Sources:**")
                        for source in message["wikipedia_sources"]:
                            st.markdown(f"- [{source}]({source})")

    with col2:
        st.header("🎯 Quick Examples")

        example_queries = [
            "Who was the second person to walk on the moon?",
            "What is quantum computing?",
            "Tell me about the history of artificial intelligence",
            "How many planets are in the solar system?",
            "What is the capital of France?",
            "Explain machine learning in simple terms",
        ]

        st.markdown("**Click on any example to try it:**")
        for query in example_queries:
            if st.button(query, key=f"example_{hash(query)}"):
                # Set the query and trigger a response
                st.session_state.messages.append({"role": "user", "content": query})

                # Get response
                response_data = call_chat_api(
                    query,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    use_wikipedia=use_wikipedia,
                )

                if response_data:
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": response_data["response"],
                            "wikipedia_sources": response_data.get(
                                "wikipedia_sources", []
                            ),
                        }
                    )
                    st.rerun()

    # Chat input outside columns to avoid Streamlit limitations
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get response from API
        response_data = call_chat_api(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            use_wikipedia=use_wikipedia,
        )

        if response_data:
            # Add assistant message to session state
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response_data["response"],
                    "wikipedia_sources": response_data.get("wikipedia_sources", []),
                }
            )
            st.rerun()
        else:
            st.error("Failed to get response from API")

    # Chat History Display
    if st.session_state.get("show_history", False):
        st.markdown("---")
        st.header("📚 Complete Chat History")

        history_data = get_chat_history()
        if history_data and history_data["history"]:
            st.write(f"**Total Conversations: {history_data['total_conversations']}**")

            # Convert to DataFrame for better display
            df_data = []
            for item in history_data["history"]:
                df_data.append(
                    {
                        "ID": item["id"],
                        "Query": (
                            item["query"][:100] + "..."
                            if len(item["query"]) > 100
                            else item["query"]
                        ),
                        "Response": (
                            item["response"][:150] + "..."
                            if len(item["response"]) > 150
                            else item["response"]
                        ),
                        "Wikipedia Sources": len(item["wikipedia_sources"]),
                        "Timestamp": item["timestamp"],
                    }
                )

            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)

            # Detailed view
            st.subheader("Detailed History")
            for item in reversed(history_data["history"]):  # Show most recent first
                with st.expander(
                    f"Conversation {item['id']} - {item['timestamp'][:19]}"
                ):
                    st.markdown(f"**Query:** {item['query']}")
                    st.markdown(f"**Response:** {item['response']}")
                    if item["wikipedia_sources"]:
                        st.markdown("**Wikipedia Sources:**")
                        for source in item["wikipedia_sources"]:
                            st.markdown(f"- [{source}]({source})")
        else:
            st.info("No chat history available.")

        if st.button("❌ Close History"):
            st.session_state.show_history = False
            st.rerun()


if __name__ == "__main__":
    main()
