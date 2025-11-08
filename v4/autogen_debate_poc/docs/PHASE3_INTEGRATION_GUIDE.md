# Phase 3 Integration Guide - System Architecture Update

## 🎯 What's New

Phase 3 adds **persistence** and **HiL state management** to the v4 debate system:

```
Before (Phase 2):
[Agent Debate] → [Judge Decision] → (Lost if app closes)

After (Phase 3):
[Agent Debate] ─→ [DebateLogger] ─→ SQLite Database
     ↓                                      ↓
[ModeratorAgent] (HiL Controls)      [Debate Replay]
     ↓
[Judge Decision] → [Stored + Searchable]
```

---

## 🔧 Component Integration Map

### 1. **DebateLogger** ↔ **ModeratorAgent**

**During Debate:**
```python
moderator = ModeratorAgent(llm_service, max_rounds=5)
logger = DebateLogger("debates.db")

# Start
logger.start_session("debate_001", "AAPL", 5)

# Each round
for round in range(1, 6):
    # Get fair speaker
    speaker = moderator.get_next_speaker(["Fundamental", "Technical", "Sentiment"])
    
    # Debate happens...
    message = agent.debate_round()
    
    # Log it
    logger.log_message("debate_001", speaker, message.content, 
                      round_num=round, message_type="analysis")
    
    # Check status
    status = moderator.get_debate_status()
    if not status['can_continue']:
        break

# End
logger.end_session("debate_001", "BUY", 0.85)
```

**After Debate:**
```python
# Retrieve history
logs = logger.get_session_logs("debate_001")  # All messages
metadata = logger.get_session_metadata("debate_001")  # Session info

# Export
json_file = logger.export_session_json("debate_001", "output.json")
```

---

### 2. **HumanProxyAgent** ↔ **ModeratorAgent**

**HiL Flow:**
```python
from agents.human_proxy_agent import HumanProxyAgent, HumanCommand
from agents.moderator_agent import ModeratorAgent

human_agent = HumanProxyAgent()
moderator = ModeratorAgent(llm_service)

# User clicks "Pause" button in Streamlit
human_agent.submit_command(HumanCommand.PAUSE)

# Command processing
if command == HumanCommand.PAUSE:
    moderator.pause_debate("User paused for review")
    status = moderator.get_debate_status()  # Send to Streamlit

# User clicks "Resume"
human_agent.submit_command(HumanCommand.CONTINUE)
moderator.resume_debate()

# User overrides decision
human_agent.submit_command(HumanCommand.OVERRIDE, decision="HOLD")
```

---

### 3. **JudgeTeam** ↔ **DebateLogger**

**Judge Context:**
```python
from services.judge_team.py import JudgeTeam
from services.debate_logger import DebateLogger

logger = DebateLogger("debates.db")
judge_team = JudgeTeam(llm_service)

# Get debate context
debate_logs = logger.get_session_logs("debate_001")

# Judges review full transcript
vote = judge_team.judge_fundamental_analysis(
    stock_symbol="AAPL",
    arguments=debate_logs,  # Full context
)

# Teams vote on final decision
final_decision = judge_team.aggregate_votes([vote1, vote2, vote3])
```

---

## 📊 Data Flow Example: Complete Debate Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. INITIATE DEBATE                                              │
├─────────────────────────────────────────────────────────────────┤
│ ModeratorAgent.__init__(llm_service, max_rounds=5)             │
│ DebateLogger.start_session("debate_001", "AAPL", 5)            │
│ HumanProxyAgent.get_status()  [for Streamlit]                  │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. ROUND 1 (Speaker fairness via ModeratorAgent)               │
├─────────────────────────────────────────────────────────────────┤
│ speaker = moderator.get_next_speaker(agents)                   │
│ message = fundamental_agent.analyze(...)                        │
│ logger.log_message(..., message, round_num=1)                  │
│ [Repeat for Technical, Sentiment]                              │
│ moderator_synthesis = moderator.manage_round(...)              │
│ logger.log_message(..., synthesis, round_num=1, role="moderator")
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. ROUND 2-4 (Normal debate flow)                              │
├─────────────────────────────────────────────────────────────────┤
│ Same as Round 1 (fair speaker selection, logging)              │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. HUMAN INTERVENTION (HiL via HumanProxyAgent)                │
├─────────────────────────────────────────────────────────────────┤
│ User clicks "Pause" in Streamlit                               │
│ → HumanProxyAgent.submit_command(PAUSE)                        │
│ → ModeratorAgent.pause_debate("User paused")                   │
│ → status = moderator.get_debate_status()                       │
│ → Logger continues accepting logs for this "paused" round      │
│                                                                 │
│ User reviews arguments from DebateLogger.get_session_logs()   │
│ User clicks "Resume"                                            │
│ → moderator.resume_debate()                                    │
│ → Debate continues                                             │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. ROUND 5 COMPLETE (Max rounds reached)                       │
├─────────────────────────────────────────────────────────────────┤
│ After round 5:                                                  │
│ can_continue = moderator.can_continue_debate()  # False        │
│ → Debate auto-stops                                            │
│ logger.end_session(..., "BUY", 0.85)                           │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. JUDGE REVIEW (JudgeTeam uses DebateLogger)                  │
├─────────────────────────────────────────────────────────────────┤
│ judge_team = JudgeTeam(llm_service)                            │
│ logs = logger.get_session_logs("debate_001")                   │
│ metadata = logger.get_session_metadata("debate_001")           │
│                                                                 │
│ # Judges analyze with full context                             │
│ vote1 = judge_team.judge_fundamental_analysis(logs)            │
│ vote2 = judge_team.judge_technical_analysis(logs)              │
│ vote3 = judge_team.judge_sentiment_analysis(logs)              │
│                                                                 │
│ final = judge_team.aggregate_votes([vote1, vote2, vote3])     │
│ → Returns AggregatedDecision with reasoning                    │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. EXPORT & ARCHIVE (DebateLogger persistence)                 │
├─────────────────────────────────────────────────────────────────┤
│ json_data = logger.export_session_json("debate_001")           │
│ → Contains: metadata, full logs, judges' votes, final decision │
│                                                                 │
│ File: debates.db                                               │
│ ├── debate_sessions table (1 row for debate_001)              │
│ └── debate_logs table (20+ rows for all messages)             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔗 Method Call Chains

### A. Standard Debate Flow (No Interruption)

```python
# Initialize
logger.start_session("debate_001", "AAPL", 5)
moderator = ModeratorAgent(llm_service, max_rounds=5)

# For each round
for round_num in range(1, 6):
    # Round processing
    message = moderator.manage_round(round_num, arg1, arg2, arg3)
    logger.log_message("debate_001", "Moderator", message.content, round_num)
    
    # Check continuation
    if not moderator.can_continue_debate():
        break

# End
logger.end_session("debate_001", final_decision, confidence)
```

### B. HiL-Interrupted Flow

```python
# Initialize
logger.start_session("debate_001", "AAPL", 5)
moderator = ModeratorAgent(llm_service, max_rounds=5)

# Round 1-2: Normal
for round_num in range(1, 3):
    message = moderator.manage_round(round_num, arg1, arg2, arg3)
    logger.log_message("debate_001", "Moderator", message.content, round_num)

# User pauses (HiL trigger)
human.submit_command(HumanCommand.PAUSE)
moderator.pause_debate("User review")

# User reviews logs
logs = logger.get_session_logs("debate_001")
status = moderator.get_debate_status()

# User decides to continue
human.submit_command(HumanCommand.CONTINUE)
moderator.resume_debate()

# Rounds 3-5 continue
for round_num in range(3, 6):
    if not moderator.can_continue_debate():
        break
    message = moderator.manage_round(round_num, arg1, arg2, arg3)
    logger.log_message("debate_001", "Moderator", message.content, round_num)

# End
logger.end_session("debate_001", final_decision, confidence)
```

---

## 📝 Quick API Reference

### ModeratorAgent State Management
```python
moderator.pause_debate(reason="User review")          # → {"status": "paused", ...}
moderator.resume_debate()                              # → {"status": "resumed"}
moderator.stop_debate(reason="Decision made")          # → {"status": "stopped"}
moderator.can_continue_debate()                        # → bool
moderator.get_debate_status()                          # → Dict with full status
moderator.get_next_speaker(["Fund", "Tech", "Sent"])  # → "Fund" (fair selection)
```

### DebateLogger CRUD
```python
logger.start_session(debate_id, stock, num_rounds)     # Create
logger.log_message(debate_id, agent, content, round)   # Create
logger.get_session_logs(debate_id)                      # Read (messages)
logger.get_session_metadata(debate_id)                  # Read (metadata)
logger.end_session(debate_id, decision, confidence)     # Update
logger.export_session_json(debate_id, path)             # Export
logger.list_sessions(limit=10)                          # List all
```

### HumanProxyAgent Commands
```python
human.submit_command(HumanCommand.START)                # Start debate
human.submit_command(HumanCommand.PAUSE)                # Pause
human.submit_command(HumanCommand.CONTINUE)             # Resume
human.submit_command(HumanCommand.STOP)                 # End
human.submit_command(HumanCommand.OVERRIDE, "BUY")      # Override decision
human.submit_command(HumanCommand.VOTE, "HOLD")         # Cast vote
```

### JudgeTeam Voting
```python
vote1 = judge_team.judge_fundamental_analysis(...)
vote2 = judge_team.judge_technical_analysis(...)
vote3 = judge_team.judge_sentiment_analysis(...)
final = judge_team.aggregate_votes([vote1, vote2, vote3])
```

---

## 🗄️ Database Schema Summary

```sql
-- Debate Sessions (1 per debate)
debate_sessions:
  - debate_id (PK, TEXT)
  - stock_symbol (TEXT)
  - start_time (DATETIME)
  - end_time (DATETIME)
  - num_rounds (INTEGER)
  - final_decision (TEXT: BUY/HOLD/SELL)
  - confidence (FLOAT: 0-1)
  - status (TEXT: active/paused/completed/terminated)

-- Debate Logs (multiple per debate)
debate_logs:
  - id (PK, INTEGER)
  - debate_id (FK → debate_sessions)
  - round_num (INTEGER)
  - agent_name (TEXT)
  - message_content (TEXT)
  - message_type (TEXT: analysis/rebuttal/override/vote/judge_vote)
  - timestamp (DATETIME)
  - agent_role (TEXT: analyst/moderator/judge/human)

-- Indexes
  - debate_id (for fast session lookup)
  - (debate_id, round_num) (for round-specific queries)
```

---

## ✅ Integration Checklist

- ✅ ModeratorAgent controls debate rounds
- ✅ DebateLogger persists all messages
- ✅ HumanProxyAgent triggers pause/resume/stop
- ✅ JudgeTeam accesses full debate context
- ✅ Status API for Streamlit dashboard
- ✅ Fair speaker selection
- ✅ Database schema optimized for queries
- ✅ Export to JSON format

---

## 🚀 Next: Phase 4 UI Enhancement

When ready, upgrade `streamlit_demo.py` to:
1. Add HiL control buttons (Pause, Resume, Stop, Override)
2. Real-time message streaming
3. Team voting visualization
4. Debate history browser powered by DebateLogger
