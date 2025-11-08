"""
Debate Logger
Persistent storage for debate transcripts and logs.
Supports SQLite for local storage, PostgreSQL for production.
"""

import logging
import sqlite3
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class DebateLogger:
    """
    Logs debate rounds to persistent storage.
    
    Schema:
    - debate_sessions: Metadata about each debate
    - debate_logs: Individual messages/rounds
    """
    
    def __init__(self, db_path: str = "debates.db"):
        """
        Initialize debate logger.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._initialize_database()
        logger.info(f"Initialized DebateLogger with database: {db_path}")
    
    def _initialize_database(self) -> None:
        """Create database schema if not exists."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()
            
            # Create debate_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS debate_sessions (
                    debate_id TEXT PRIMARY KEY,
                    stock_symbol TEXT NOT NULL,
                    start_time DATETIME,
                    end_time DATETIME,
                    num_rounds INTEGER,
                    final_decision TEXT,
                    confidence FLOAT,
                    status TEXT,  -- 'active', 'paused', 'completed', 'terminated'
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create debate_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS debate_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    debate_id TEXT NOT NULL,
                    round_num INTEGER,
                    agent_name TEXT,
                    message_content TEXT,
                    message_type TEXT,  -- 'analysis', 'rebuttal', 'override', 'vote', 'judge_vote'
                    timestamp DATETIME,
                    agent_role TEXT,  -- 'analyst', 'moderator', 'judge', 'human'
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(debate_id) REFERENCES debate_sessions(debate_id)
                )
            """)
            
            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_debate_id 
                ON debate_logs(debate_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_round_num 
                ON debate_logs(debate_id, round_num)
            """)
            
            self.connection.commit()
            logger.info("Database schema initialized successfully")
        
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def start_session(
        self,
        debate_id: str,
        stock_symbol: str,
        num_rounds: int,
    ) -> bool:
        """
        Start a new debate session.
        
        Args:
            debate_id: Unique debate identifier
            stock_symbol: Stock being debated
            num_rounds: Number of rounds
            
        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO debate_sessions 
                (debate_id, stock_symbol, start_time, num_rounds, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                debate_id,
                stock_symbol,
                datetime.utcnow(),
                num_rounds,
                "active"
            ))
            
            self.connection.commit()
            logger.info(f"Started session: {debate_id} ({stock_symbol})")
            return True
        
        except sqlite3.Error as e:
            logger.error(f"Error starting session: {e}")
            return False
    
    def log_message(
        self,
        debate_id: str,
        agent_name: str,
        message_content: str,
        round_num: int,
        message_type: str = "analysis",
        agent_role: str = "analyst",
    ) -> bool:
        """
        Log a debate message.
        
        Args:
            debate_id: Associated debate session
            agent_name: Name of speaking agent
            message_content: The message text
            round_num: Round number
            message_type: Type of message
            agent_role: Role of agent (analyst, moderator, judge, human)
            
        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO debate_logs
                (debate_id, agent_name, message_content, round_num, 
                 message_type, agent_role, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                debate_id,
                agent_name,
                message_content,
                round_num,
                message_type,
                agent_role,
                datetime.utcnow(),
            ))
            
            self.connection.commit()
            return True
        
        except sqlite3.Error as e:
            logger.error(f"Error logging message: {e}")
            return False
    
    def end_session(
        self,
        debate_id: str,
        final_decision: str,
        confidence: float,
    ) -> bool:
        """
        End a debate session.
        
        Args:
            debate_id: Debate to end
            final_decision: Final verdict (BUY/HOLD/SELL)
            confidence: Confidence level (0-100)
            
        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                UPDATE debate_sessions
                SET end_time = ?, status = ?, 
                    final_decision = ?, confidence = ?
                WHERE debate_id = ?
            """, (
                datetime.utcnow(),
                "completed",
                final_decision,
                confidence,
                debate_id,
            ))
            
            self.connection.commit()
            logger.info(f"Ended session: {debate_id}")
            return True
        
        except sqlite3.Error as e:
            logger.error(f"Error ending session: {e}")
            return False
    
    def get_session_logs(self, debate_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all logs for a debate session.
        
        Args:
            debate_id: Debate to retrieve
            
        Returns:
            List of message dictionaries
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT agent_name, round_num, message_type, 
                       message_content, timestamp, agent_role
                FROM debate_logs
                WHERE debate_id = ?
                ORDER BY round_num, timestamp
            """, (debate_id,))
            
            rows = cursor.fetchall()
            
            logs = []
            for row in rows:
                logs.append({
                    "agent": row[0],
                    "round": row[1],
                    "type": row[2],
                    "content": row[3],
                    "timestamp": row[4],
                    "role": row[5],
                })
            
            return logs
        
        except sqlite3.Error as e:
            logger.error(f"Error retrieving logs: {e}")
            return []
    
    def get_session_metadata(self, debate_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata for a debate session.
        
        Args:
            debate_id: Debate to retrieve
            
        Returns:
            Session metadata dictionary or None
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT debate_id, stock_symbol, start_time, end_time,
                       num_rounds, final_decision, confidence, status
                FROM debate_sessions
                WHERE debate_id = ?
            """, (debate_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "debate_id": row[0],
                    "stock_symbol": row[1],
                    "start_time": row[2],
                    "end_time": row[3],
                    "num_rounds": row[4],
                    "final_decision": row[5],
                    "confidence": row[6],
                    "status": row[7],
                }
            
            return None
        
        except sqlite3.Error as e:
            logger.error(f"Error retrieving metadata: {e}")
            return None
    
    def list_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent debate sessions.
        
        Args:
            limit: Number of sessions to retrieve
            
        Returns:
            List of session metadata
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT debate_id, stock_symbol, start_time, end_time,
                       num_rounds, final_decision, confidence, status
                FROM debate_sessions
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            
            sessions = []
            for row in rows:
                sessions.append({
                    "debate_id": row[0],
                    "stock_symbol": row[1],
                    "start_time": row[2],
                    "end_time": row[3],
                    "num_rounds": row[4],
                    "final_decision": row[5],
                    "confidence": row[6],
                    "status": row[7],
                })
            
            return sessions
        
        except sqlite3.Error as e:
            logger.error(f"Error listing sessions: {e}")
            return []
    
    def export_session_json(
        self,
        debate_id: str,
        output_path: Optional[str] = None,
    ) -> Optional[str]:
        """
        Export debate session as JSON.
        
        Args:
            debate_id: Debate to export
            output_path: Optional path to save JSON
            
        Returns:
            JSON string or filepath
        """
        try:
            metadata = self.get_session_metadata(debate_id)
            logs = self.get_session_logs(debate_id)
            
            if not metadata:
                logger.error(f"Session not found: {debate_id}")
                return None
            
            export_data = {
                "metadata": metadata,
                "logs": logs,
                "exported_at": datetime.utcnow().isoformat(),
            }
            
            json_str = json.dumps(export_data, indent=2, default=str)
            
            if output_path:
                Path(output_path).write_text(json_str)
                logger.info(f"Exported session to: {output_path}")
                return output_path
            
            return json_str
        
        except Exception as e:
            logger.error(f"Error exporting session: {e}")
            return None
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")


def create_debate_logger(db_path: str = "debates.db") -> DebateLogger:
    """Factory function to create DebateLogger."""
    return DebateLogger(db_path)
