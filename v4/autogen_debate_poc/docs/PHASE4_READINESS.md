# Phase 4 Readiness Checklist

## 🎯 Phase 4 Goal
Upgrade Streamlit UI with Human-in-the-Loop controls and real-time debate visualization.

---

## ✅ Prerequisites Met (Phase 3 Complete)

### Foundation Components
- ✅ ModeratorAgent with HiL controls (pause/resume/stop)
- ✅ HumanProxyAgent with command queueing
- ✅ DebateLogger with persistent storage
- ✅ JudgeTeam with 3-member voting

### Integration Points Ready
- ✅ `moderator.pause_debate()` → Available
- ✅ `moderator.resume_debate()` → Available
- ✅ `moderator.stop_debate()` → Available
- ✅ `moderator.get_debate_status()` → Available
- ✅ `moderator.get_next_speaker()` → Available
- ✅ `logger.log_message()` → Available
- ✅ `logger.get_session_logs()` → Available
- ✅ `logger.list_sessions()` → Available
- ✅ `human_proxy_agent.submit_command()` → Available
- ✅ `judge_team.aggregate_votes()` → Available

### Data Persistence
- ✅ SQLite database schema (debates.db)
- ✅ All debate messages logged
- ✅ Export to JSON available

---

## 📝 Phase 4 Implementation Tasks

### Task 1: Add HiL Control Panel (~150-200 lines)
**Location:** `streamlit_demo.py` → "Debate Live" tab

**Components to Add:**
```python
# Control buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("⏸ Pause"):
        moderator.pause_debate("User paused for review")
        st.session_state.paused = True

with col2:
    if st.button("▶ Resume"):
        moderator.resume_debate()
        st.session_state.paused = False

with col3:
    if st.button("⏹ Stop"):
        moderator.stop_debate("User ended debate")
        st.session_state.stopped = True

with col4:
    if st.button("✋ Override"):
        st.session_state.show_override = True

# Status display
if st.session_state.paused:
    st.warning("⏸ Debate Paused - Awaiting User Decision")

status = moderator.get_debate_status()
st.info(f"Round {status['current_round']}/{status['max_rounds']}")
```

**Estimated Lines:** 150-200

---

### Task 2: Real-Time Message Streaming (~100-150 lines)
**Location:** `streamlit_demo.py` → "Debate Live" tab

**Components to Add:**
```python
# Streaming area
message_container = st.container()

# Refresh messages from logger
with message_container:
    logs = logger.get_session_logs(debate_id)
    for log in logs:
        # Color by agent role
        if log['role'] == 'analyst':
            st.write(f"🤖 **{log['agent']}** (Round {log['round']})")
        elif log['role'] == 'moderator':
            st.write(f"🎙️ **Moderator**")
        elif log['role'] == 'judge':
            st.write(f"⚖️ **Judge {log['agent']}**")
        elif log['role'] == 'human':
            st.write(f"👤 **Human Decision**")
        
        st.write(f"> {log['content']}")
        st.write(f"__{log['timestamp']}__")
        st.divider()

# Auto-refresh
if st.button("🔄 Refresh Messages"):
    st.rerun()
```

**Estimated Lines:** 100-150

---

### Task 3: Team Voting Visualization (~80-120 lines)
**Location:** `streamlit_demo.py` → "Results" tab (enhance existing)

**Components to Add:**
```python
# Voting panel
st.subheader("🏛️ Judge Team Votes")

# Get judge votes from judge_team
votes = judge_team.aggregate_votes([vote1, vote2, vote3])

# Display as cards
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Fundamental Judge",
        votes.votes[0].decision,
        f"{votes.votes[0].confidence:.0%} confidence"
    )

with col2:
    st.metric(
        "Technical Judge",
        votes.votes[1].decision,
        f"{votes.votes[1].confidence:.0%} confidence"
    )

with col3:
    st.metric(
        "Sentiment Judge",
        votes.votes[2].decision,
        f"{votes.votes[2].confidence:.0%} confidence"
    )

# Final decision
st.info(f"""
**Final Decision:** {votes.final_decision}  
**Confidence:** {votes.confidence:.0%}  
**Unanimity Score:** {votes.unanimity_score:.2f}
""")

# Rationale
with st.expander("📋 Judge Reasoning"):
    for i, vote in enumerate(votes.votes):
        st.write(f"**Judge {i+1}:** {vote.rationale}")
```

**Estimated Lines:** 80-120

---

### Task 4: Debate History Browser (~80-120 lines)
**Location:** `streamlit_demo.py` → New "History" tab

**Components to Add:**
```python
st.title("📚 Debate History")

# List recent debates
sessions = logger.list_sessions(limit=20)

if sessions:
    # Create table view
    data = []
    for session in sessions:
        data.append({
            "ID": session['debate_id'],
            "Stock": session['stock_symbol'],
            "Date": session['start_time'],
            "Rounds": session['num_rounds'],
            "Decision": session['final_decision'],
            "Confidence": f"{session['confidence']:.0%}",
            "Status": session['status']
        })
    
    df = pd.DataFrame(data)
    
    # Display table
    selected_debate = st.dataframe(
        df,
        use_container_width=True,
        key="debates_table"
    )
    
    # Select debate to view
    debate_id = st.selectbox("Select debate to view:", 
                             [s['debate_id'] for s in sessions])
    
    if debate_id:
        # Show full debate logs
        logs = logger.get_session_logs(debate_id)
        st.write(f"**Debate {debate_id}**")
        for log in logs:
            st.write(f"{log['agent']}: {log['content'][:100]}...")
        
        # Export options
        if st.button("📥 Export Full Debate"):
            json_data = logger.export_session_json(debate_id)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"{debate_id}.json"
            )
else:
    st.info("No debates found yet. Start a debate to see history.")
```

**Estimated Lines:** 80-120

---

## 📋 Files to Modify

### Primary
- **streamlit_demo.py** (+400-500 lines)
  - Add HiL control buttons (~150 lines)
  - Add message streaming (~120 lines)
  - Enhance voting display (~100 lines)
  - Add history browser (~100 lines)
  - Update session initialization (~30 lines)

### Secondary (May need minor tweaks)
- **services/debate_orchestrator.py** (Check integration with logger/moderator)
- **config.yaml** (May need debate_logger path)

---

## 🔗 Integration Calls Needed

### In streamlit_demo.py initialization:
```python
# Add imports
from services.debate_logger import DebateLogger
from agents.human_proxy_agent import HumanProxyAgent

# Initialize (in session_state)
if 'logger' not in st.session_state:
    st.session_state.logger = DebateLogger("debates.db")
    
if 'human_proxy' not in st.session_state:
    st.session_state.human_proxy = HumanProxyAgent()
```

### In debate_orchestrator integration:
```python
# Pass logger to orchestrator or call it separately
logger.start_session(debate_id, stock_symbol, num_rounds)

# During debate rounds
logger.log_message(debate_id, agent_name, content, round_num)

# After debate
logger.end_session(debate_id, final_decision, confidence)
```

### HiL button integration:
```python
# When user clicks pause
if st.button("⏸ Pause"):
    st.session_state.human_proxy.submit_command(HumanCommand.PAUSE)
    orchestrator.moderator.pause_debate("User paused")
```

---

## ✅ Phase 4 Success Criteria

- ✅ HiL control panel functional (Pause/Resume/Stop/Override buttons)
- ✅ Real-time message streaming from DebateLogger
- ✅ Team voting visualization with confidence scores
- ✅ Debate history browser with past debates
- ✅ Export functionality preserved and enhanced
- ✅ Database integration (debates.db) transparent to user
- ✅ No breaking changes to existing functionality
- ✅ Streamlit app runs without errors
- ✅ HiL commands properly flow to ModeratorAgent
- ✅ Status updates reflect in UI in real-time

---

## 📦 Deliverables (Phase 4)

1. **Enhanced streamlit_demo.py** (900-1100 lines, up from 625)
2. **Integration documentation** showing HiL data flow
3. **User guide** for new HiL features
4. **Testing checklist** for HiL workflows

---

## 🚀 Ready to Start?

**Prerequisites:** ✅ ALL COMPLETE

You can now proceed with Phase 4 implementation:
1. Start with Task 1 (HiL Control Panel) - Most critical
2. Add Task 2 (Real-Time Streaming)
3. Add Task 3 (Team Voting Viz)
4. Add Task 4 (History Browser)

**Recommendation:** Implement in order 1→2→3→4 to maintain working app at each stage.

---

## 📞 Reference

**Phase 3 Components:**
- `agents/moderator_agent.py` - `pause_debate()`, `resume_debate()`, etc.
- `services/debate_logger.py` - `log_message()`, `get_session_logs()`, etc.
- `agents/human_proxy_agent.py` - `submit_command()`
- `services/judge_team.py` - `aggregate_votes()`

**New in Phase 4:**
- streamlit_demo.py will integrate all of above
- SQLite database created on first run
- 4 new UI tabs/sections for HiL and history

**All APIs documented in:**
- `PHASE3_INTEGRATION_GUIDE.md` - How components connect
- `STATUS_REPORT.md` - Overall system status
- Docstrings in each component

---

**Phase 4 Status:** 🟡 **READY TO START**
