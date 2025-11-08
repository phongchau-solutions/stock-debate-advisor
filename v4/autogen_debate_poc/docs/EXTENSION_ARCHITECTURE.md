# 🚀 Streamlit + Teams + HiL Extension Architecture

**Extending v4 with Interactive UI, Autogen Teams, and Human-in-the-Loop**

---

## 📋 Component Overview

### 1. Human-in-the-Loop Integration (HiL)
**File:** `agents/human_proxy_agent.py`
- UserProxyAgent with Streamlit callback hooks
- Supports: Start/Pause/Stop/Override commands from UI
- Queues user decisions for agent consumption

### 2. Judge Team Implementation
**File:** `services/judge_team.py`
- 3-member financial expert consensus voting
- Independent verdicts from each member
- Aggregation logic to combine votes
- Weighted confidence scoring

### 3. Tool Enhancement
**Files:** `agents/{fundamental,technical,sentiment}_agent.py` (refactored)
- Registered tools using `.register_tool()` pattern
- AssistantAgent compatible
- Data sources: Vietcap, VnEconomy, WSJ APIs

### 4. Moderator Enhancement
**File:** `agents/moderator_agent.py` (enhanced)
- Dynamic turn order control
- Support for ≥5 rounds
- Speaking time balance
- Debate flow management

### 5. Debate Logger
**File:** `services/debate_logger.py`
- SQLite persistence layer
- Schema: (timestamp, speaker, content, round, debate_id)
- Replay capability

### 6. Enhanced Streamlit App
**File:** `app.py` (replaces streamlit_demo.py)
- Real-time message streaming
- Control buttons (Start/Pause/Stop/Override)
- Human input panel
- Team voting visualization

---

## 🔄 Data Flow

```
User Input (Streamlit UI)
    ↓
[Human Proxy Agent] ← Start/Pause/Stop/Override commands
    ↓
[Moderator Agent] ← Controls turn order & round flow
    ↓
[3 Specialist Agents] ← Each produces analysis
    ↓
[Judge Team] ← Aggregates verdicts
    ↓
[Debate Logger] → SQLite persistence
    ↓
Display Results (Streamlit UI)
```

---

## 🎯 Expected Workflow

```
1. User opens Streamlit
2. Select stock symbol & time range
3. Click "Start Debate"
   │
   ├→ Initialize ModeratorAgent
   ├→ Initialize 3 Analyst Agents
   ├→ Initialize JudgeTeam
   └→ Initialize HiL UserProxyAgent
4. Round-by-round execution:
   ├→ Moderator decides turn order
   ├→ Agents speak in order
   ├→ Messages stream to UI in real-time
   └→ User can pause/stop/override anytime
5. After final round:
   ├→ Judge Team votes independently
   ├→ Aggregates decision
   └→ Displays structured result
6. Option to save/replay debate
```

---

## 🛠️ Implementation Phases

### Phase 1: Foundation (Core Extensions)
- [ ] Create human_proxy_agent.py
- [ ] Create judge_team.py
- [ ] Enhance moderator_agent.py
- [ ] Create debate_logger.py

### Phase 2: Integration
- [ ] Refactor agents as tools
- [ ] Update orchestrator for Teams compatibility
- [ ] Add HiL event handlers

### Phase 3: UI Enhancement
- [ ] Upgrade app.py to Streamlit 1.29+
- [ ] Add real-time streaming
- [ ] Add control buttons
- [ ] Add team visualization

### Phase 4: Polish & Deploy
- [ ] Integration tests
- [ ] Documentation
- [ ] Deployment guides
- [ ] Example workflows

---

## 📦 Dependencies (New)

```
autogen-teams>=0.2.0          # Autogen Teams API
streamlit>=1.29.0             # Already have
sqlite3                       # Built-in
pydantic>=2.0.0               # Data validation
asyncio                       # Async support
```

---

## 🔗 Integration Points

### With Existing Services
- ✅ GeminiService (unchanged)
- ✅ DataService (unchanged)
- ✅ DebateOrchestrator (extends)

### With New Components
- HiL ← Streamlit UI (callbacks)
- JudgeTeam ← Agents (verdicts)
- ModeratorAgent ← HiL (flow control)
- DebateLogger ← Orchestrator (persistence)

---

## 📚 Example Usage (New)

```python
# Create debate with Teams
orchestrator = DebateOrchestrator(
    llm_service=gemini_service,
    enable_teams=True,           # NEW
    enable_hil=True,             # NEW
    hil_callback=streamlit_callback  # NEW
)

# Run with HiL support
result = orchestrator.run_debate(
    stock_symbol="VCB",
    stock_data=data,
    num_rounds=3,
    allow_override=True  # NEW
)

# Access team voting
print(result.team_votes)      # NEW
print(result.aggregated_decision)  # NEW
```

---

## 🎨 UI Enhancements

### Main Tab Layout
```
┌─────────────────────────────────────────┐
│  🎯 Debate Control Panel               │
├─────────────────────────────────────────┤
│ [Start] [Pause] [Stop] [Override ▼]   │
│ Stock: [VCB    ] Rounds: [3] Period: 6mo
├─────────────────────────────────────────┤
│  💬 Live Debate Stream                  │
├─────────────────────────────────────────┤
│ Round 1:                                │
│ ┌─────────────────────────────────────┐ │
│ │ 🔵 Fundamental: [message...]        │ │
│ │ 🟠 Technical: [message...]          │ │
│ │ 🟢 Sentiment: [message...]          │ │
│ └─────────────────────────────────────┘ │
│ Round 2: ...                            │
├─────────────────────────────────────────┤
│  🎖️ Judge Team Voting                   │
│ ┌─────────────────────────────────────┐ │
│ │ Judge 1: BUY (87%)                  │ │
│ │ Judge 2: BUY (82%)                  │ │
│ │ Judge 3: HOLD (65%)                 │ │
│ │ Aggregated: BUY (78%)               │ │
│ └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ 👤 Human Override:                      │
│ [Input prompt...]                       │
│ [Send Override]                         │
└─────────────────────────────────────────┘
```

---

## 🔐 Human-in-the-Loop Commands

| Command | Effect | Example |
|---------|--------|---------|
| **Start** | Begin debate | Click "Start Debate" |
| **Pause** | Halt at end of round | "Pause after Round 2" |
| **Stop** | Terminate debate | "Stop & Finalize" |
| **Override** | Inject custom stance | "Analyst says SELL due to..." |
| **Vote** | Cast human vote | "I vote BUY" |

---

## 📊 Logging Schema (SQLite)

```sql
CREATE TABLE debate_logs (
    id INTEGER PRIMARY KEY,
    debate_id TEXT NOT NULL,
    round_num INTEGER,
    agent_name TEXT,
    message_content TEXT,
    timestamp DATETIME,
    message_type TEXT,  -- 'analysis'|'rebuttal'|'judge_vote'|'human_override'
    FOREIGN KEY(debate_id) REFERENCES debates(id)
);

CREATE TABLE debate_sessions (
    id TEXT PRIMARY KEY,  -- debate_id
    stock_symbol TEXT,
    start_time DATETIME,
    end_time DATETIME,
    final_decision TEXT,
    confidence FLOAT
);
```

---

## 🚀 Deployment Notes

- **Streamlit**: `streamlit run app.py --server.port=8501`
- **Teams API**: Requires `autogen-teams>=0.2.0`
- **HiL Callbacks**: Async event handling via Streamlit session state
- **Database**: SQLite (local) or PostgreSQL (production)

---

## ✅ Success Criteria

- ✅ Streamlit UI displays live debate stream
- ✅ Human can start/pause/stop debate from UI
- ✅ Human can override agent opinions
- ✅ Judge Team produces independent votes
- ✅ Aggregation combines votes correctly
- ✅ All messages logged to SQLite
- ✅ Replay debate from logs
- ✅ <2s latency for message display

---

**Next:** Implement each component according to phases above.

