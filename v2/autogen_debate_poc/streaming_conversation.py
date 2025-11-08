"""
Streaming conversation components for real-time debate rendering
"""
import streamlit as st
import time
import asyncio
from typing import Dict, Any, List, Callable, Optional
import threading
from datetime import datetime

class StreamingConversation:
    """Handles streaming conversation display with real-time message rendering."""
    
    def __init__(self):
        self.conversation_container = None
        self.message_count = 0
        self.is_streaming = False
        
    def initialize_streaming_ui(self):
        """Initialize the streaming conversation UI components."""
        
        # Custom CSS for streaming chat
        st.markdown("""
        <style>
        .streaming-chat-container {
            max-height: 600px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
            border-radius: 15px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background-size: 200% 200%;
            animation: gradientShift 10s ease infinite;
            margin-bottom: 20px;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .streaming-message {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 15px;
            position: relative;
            max-width: 85%;
            word-wrap: break-word;
            animation: slideIn 0.3s ease-out;
            opacity: 0;
            animation-fill-mode: forwards;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes typing {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        
        .typing-indicator {
            display: inline-block;
            animation: typing 1s infinite;
        }
        
        .technical-stream {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .fundamental-stream {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            margin-right: auto;
            text-align: left;
        }
        
        .sentiment-stream {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            margin-right: auto;
            text-align: left;
        }
        
        .moderator-stream {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            color: #333;
            margin: 0 auto;
            text-align: center;
            max-width: 90%;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .judge-stream {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: #333;
            margin: 0 auto;
            text-align: center;
            max-width: 70%;
            font-size: 0.9em;
            border: 2px solid #ffd700;
        }
        
        .speaker-badge {
            font-weight: bold;
            font-size: 0.85em;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .message-text {
            font-size: 1em;
            line-height: 1.5;
            margin-bottom: 8px;
        }
        
        .message-timestamp {
            font-size: 0.7em;
            opacity: 0.7;
            font-style: italic;
        }
        
        .debate-status {
            text-align: center;
            padding: 15px;
            background-color: rgba(255,255,255,0.1);
            border-radius: 10px;
            margin-bottom: 20px;
            color: white;
            font-weight: bold;
        }
        
        .typing-indicator-container {
            padding: 10px 15px;
            background-color: rgba(255,255,255,0.1);
            border-radius: 15px;
            margin: 10px auto;
            max-width: 200px;
            text-align: center;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Initialize conversation container
        st.markdown('<div class="streaming-chat-container" id="chat-container">', unsafe_allow_html=True)
        self.conversation_container = st.empty()
        
        return self.conversation_container
    
    def show_typing_indicator(self, speaker: str, container: st.container) -> None:
        """Show typing indicator for the current speaker."""
        speaker_emoji = self._get_speaker_emoji(speaker)
        
        with container:
            st.markdown(f"""
            <div class="typing-indicator-container">
                {speaker_emoji} {speaker} is typing<span class="typing-indicator">...</span>
            </div>
            """, unsafe_allow_html=True)
    
    def stream_message(
        self, 
        message: Dict[str, Any], 
        container: st.container,
        typing_delay: float = 2.0,
        chunk_delay: float = 0.05
    ) -> None:
        """Stream a message with typing effect."""
        
        speaker = message.get('speaker', 'Unknown')
        content = message.get('message', '')
        role = message.get('role', '')
        timestamp = message.get('timestamp', datetime.now().isoformat())
        
        # Show typing indicator
        if typing_delay > 0:
            self.show_typing_indicator(speaker, container)
            time.sleep(typing_delay)
        
        # Clear typing indicator and start streaming message
        message_class = self._get_message_class(speaker)
        speaker_emoji = self._get_speaker_emoji(speaker)
        
        # Stream content word by word
        words = content.split()
        streamed_content = ""
        
        for i, word in enumerate(words):
            streamed_content += word + " "
            
            with container:
                st.markdown(f"""
                <div class="streaming-message {message_class}" style="animation-delay: 0.1s;">
                    <div class="speaker-badge">
                        {speaker_emoji} <strong>{speaker}</strong>
                        <small>({role})</small>
                    </div>
                    <div class="message-text">{streamed_content}<span class="typing-indicator">|</span></div>
                    <div class="message-timestamp">{self._format_timestamp(timestamp)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            time.sleep(chunk_delay)
        
        # Final message without cursor
        with container:
            st.markdown(f"""
            <div class="streaming-message {message_class}">
                <div class="speaker-badge">
                    {speaker_emoji} <strong>{speaker}</strong>
                    <small>({role})</small>
                </div>
                <div class="message-text">{content}</div>
                <div class="message-timestamp">{self._format_timestamp(timestamp)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        self.message_count += 1
    
    def show_debate_status(self, status: str, container: st.container) -> None:
        """Show debate status update."""
        with container:
            st.markdown(f"""
            <div class="debate-status">
                🎯 {status}
            </div>
            """, unsafe_allow_html=True)
    
    def show_round_header(self, round_info: str, container: st.container) -> None:
        """Show round header with animation."""
        with container:
            st.markdown(f"""
            <div class="debate-status" style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #333;">
                🔥 {round_info}
            </div>
            """, unsafe_allow_html=True)
    
    def _get_message_class(self, speaker: str) -> str:
        """Get CSS class based on speaker."""
        speaker_lower = speaker.lower()
        if 'technical' in speaker_lower:
            return 'technical-stream'
        elif 'fundamental' in speaker_lower:
            return 'fundamental-stream'
        elif 'sentiment' in speaker_lower:
            return 'sentiment-stream'
        elif 'judge' in speaker_lower:
            return 'judge-stream'
        else:  # moderator
            return 'moderator-stream'
    
    def _get_speaker_emoji(self, speaker: str) -> str:
        """Get emoji for speaker."""
        speaker_lower = speaker.lower()
        emojis = {
            'technical': '📈',
            'fundamental': '📊', 
            'sentiment': '📰',
            'moderator': '⚖️',
            'judge': '👨‍⚖️'
        }
        
        for key, emoji in emojis.items():
            if key in speaker_lower:
                return emoji
        return '🗣️'
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Format timestamp for display."""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%H:%M:%S')
        except:
            return timestamp[-8:-3] if len(timestamp) > 8 else ''


class StreamingDebateManager:
    """Manages the streaming debate flow with real-time updates."""
    
    def __init__(self, update_callback: Optional[Callable] = None):
        self.streaming_ui = StreamingConversation()
        self.conversation_history = []
        self.current_round = 0
        self.is_active = False
        self.update_callback = update_callback
        
    def start_streaming_debate(self, container):
        """Initialize and start the streaming debate interface."""
        self.is_active = True
        self.conversation_container = container
        
        # Initialize streaming UI
        self.streaming_ui.initialize_streaming_ui()
        
        # Show initial status
        self.streaming_ui.show_debate_status(
            "🚀 Initializing Vietnamese Stock Market Debate...", 
            container
        )
        
        return True
    
    def stream_message_to_ui(
        self, 
        message: Dict[str, Any], 
        typing_delay: float = 1.5,
        chunk_delay: float = 0.03
    ) -> None:
        """Stream a single message to the UI."""
        if not self.is_active or not self.conversation_container:
            return
            
        # Add to conversation history
        self.conversation_history.append(message)
        
        # Stream to UI
        self.streaming_ui.stream_message(
            message, 
            self.conversation_container,
            typing_delay=typing_delay,
            chunk_delay=chunk_delay
        )
        
        # Callback for updates
        if self.update_callback:
            self.update_callback(message)
    
    def show_round_transition(self, round_info: str) -> None:
        """Show round transition with animation."""
        if not self.is_active or not self.conversation_container:
            return
            
        self.current_round += 1
        self.streaming_ui.show_round_header(round_info, self.conversation_container)
        time.sleep(1)  # Brief pause for transition
    
    def show_status_update(self, status: str) -> None:
        """Show status update."""
        if not self.is_active or not self.conversation_container:
            return
            
        self.streaming_ui.show_debate_status(status, self.conversation_container)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get current conversation history."""
        return self.conversation_history.copy()
    
    def stop_streaming(self) -> None:
        """Stop the streaming debate."""
        self.is_active = False
        if self.conversation_container:
            self.streaming_ui.show_debate_status(
                "✅ Debate Complete! Judges are evaluating...", 
                self.conversation_container
            )


# Streamlit components for integration
def create_streaming_debate_ui():
    """Create the streaming debate UI components."""
    
    # Initialize session state
    if 'streaming_manager' not in st.session_state:
        st.session_state.streaming_manager = StreamingDebateManager()
    
    if 'debate_active' not in st.session_state:
        st.session_state.debate_active = False
    
    # Create main container
    debate_container = st.container()
    
    with debate_container:
        st.header("🎬 Live Debate Stream")
        
        # Control buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("▶️ Start Streaming", disabled=st.session_state.debate_active):
                st.session_state.debate_active = True
                st.session_state.streaming_manager.start_streaming_debate(st.empty())
                st.rerun()
        
        with col2:
            if st.button("⏹️ Stop Streaming", disabled=not st.session_state.debate_active):
                st.session_state.debate_active = False
                st.session_state.streaming_manager.stop_streaming()
                st.rerun()
        
        with col3:
            if st.session_state.debate_active:
                st.success("🔴 LIVE - Debate in Progress")
            else:
                st.info("⚪ Ready to Stream")
    
    return st.session_state.streaming_manager, debate_container