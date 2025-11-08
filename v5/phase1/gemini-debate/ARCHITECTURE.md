# Stock Debate AI - System Architecture

This document outlines the technical architecture of the Stock Debate AI system, which facilitates multi-agent debates for stock analysis using Gemini and AutoGen.

## System Overview

The system implements a multi-agent debate platform where different analyst agents (Fundamental, Technical, and Sentiment) discuss and analyze stocks, moderated by a Moderator agent and evaluated by a Judge agent.

## Component Architecture

```mermaid
graph TB
    subgraph Presentation["Presentation Layer"]
        UI[Streamlit Web Interface]
        Display[Display Manager]
    end

    subgraph Core["Core Layer"]
        DO[Debate Orchestrator]
        SS[State Management]
        Config[Configuration]
    end

    subgraph Analysis["Analysis Tools Layer"]
        FA[Financial Analysis]
        TA[Technical Analysis]
        SA[Sentiment Analysis]
    end

    subgraph Agents["AI Agent Layer"]
        subgraph Analysts
            FAgent[Fundamental Analyst]
            TAgent[Technical Analyst]
            SAgent[Sentiment Analyst]
        end
        MAgent[Moderator]
        JAgent[Judge]
    end

    subgraph Integration["Data Integration Layer"]
        GC[Gemini API Client]
        ZA[ZStock Data Adapter]
        NC[News Crawler]
        Cache[Response Cache]
    end

    subgraph Storage["Data Storage Layer"]
        FS[File System]
        DS[Data Store]
    end

    UI --> Display
    Display --> DO
    DO --> SS
    DO --> Config

    FAgent --> FA
    TAgent --> TA
    SAgent --> SA
    
    FA & TA & SA --> ZA
    SA --> NC

    Analysts & MAgent & JAgent --> GC
    GC --> Cache
    
    ZA & NC --> DS
    DS --> FS
    
    MAgent --> DO
    JAgent --> DO
```

## Sequence Diagram - Debate Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant DO as Debate Orchestrator
    participant DB as Data Layer
    participant MA as Moderator Agent
    participant FA as Fundamental Agent
    participant TA as Technical Agent
    participant SA as Sentiment Agent
    participant JA as Judge Agent

    U->>F: Select Stock
    F->>DO: Initialize Debate
    DO->>DB: Load Stock Data
    DB-->>DO: Data Retrieved

    DO->>MA: Begin Debate
    
    par Round 1 Analysis
        MA->>FA: Request Analysis
        MA->>TA: Request Analysis
        MA->>SA: Request Analysis
        
        FA-->>MA: Financial Report + Action
        TA-->>MA: Technical Report + Action
        SA-->>MA: Sentiment Report + Action
    end

    MA->>DO: Store Round 1
    DO->>F: Update Display

    par Round 2 Critiques
        MA->>FA: Request Critiques
        MA->>TA: Request Critiques
        MA->>SA: Request Critiques

        FA-->>MA: Critique + Action
        TA-->>MA: Critique + Action
        SA-->>MA: Critique + Action
    end

    MA->>DO: Store Round 2
    DO->>F: Update Display

    MA->>JA: Request Final Judgment
    JA-->>MA: Final Decision + Reasoning
    MA->>DO: Store Decision
    DO->>F: Display Results
```

## Flow Chart - Message Processing

```mermaid
flowchart TD
    Start([Start]) --> A[User Selects Stock]
    A --> B{Initialize System}
    B --> C[Load Stock Data]
    C --> D[Initialize Agents & Tools]

    D --> E{Start Debate Round}
    
    E --> F1[Fundamental Agent Analysis]
    E --> F2[Technical Agent Analysis]
    E --> F3[Sentiment Agent Analysis]
    
    F1 & F2 & F3 --> G[Moderator Collects Responses]
    
    G --> H{Check Actions}
    H -- Consensus --> I[Judge Final Evaluation]
    H -- Divergent --> J[Generate Critiques]
    
    J --> K{Round < 3}
    K -- Yes --> E
    K -- No --> I
    
    I --> L[Store Results]
    L --> M[Update Display]
    
    M --> N{New Analysis?}
    N -- Yes --> A
    N -- No --> End([End])
```

## Key Components

### Frontend Layer
- **Streamlit UI**: Handles user interaction and real-time display of debate progress
- **WebSocket Events**: Manages real-time updates and message streaming

### Orchestration Layer
- **Debate Orchestrator**: Coordinates agent interactions and manages debate flow
- **Session State**: Maintains debate context and agent states

### Agent Layer
- **Analyst Agents**: Specialized agents for different analysis types
- **Moderator**: Controls debate flow and ensures productive discussion
- **Judge**: Evaluates arguments and makes final decisions

### Integration Layer
- **Gemini Client**: Handles API communication with Google's Gemini model
- **ZStock Adapter**: Interfaces with stock data sources
- **News Crawler**: Gathers relevant news and sentiment data

### Storage Layer
- **File System**: Stores stock data and debate history
- **Response Cache**: Optimizes performance by caching model responses

## Implementation Details

### Agent Communication
- Asynchronous message passing between agents
- Structured debate format with clear roles
- State management for action tracking

### UI Features
- Real-time message updates
- Action status tracking (BUY/SELL/HOLD)
- Critique linking between messages
- Auto-scrolling message view

### Data Flow
1. User selects stock and timeframe
2. System loads relevant data
3. Agents perform analysis in parallel
4. Moderator manages debate progression
5. Judge evaluates final consensus
6. Results displayed in UI

## Technical Stack
- Python 3.13
- Streamlit
- Google Gemini AI
- AutoGen Framework
- WebSocket Protocol
- File-based Storage

## Development Considerations
- Modular design for easy extension
- Asynchronous processing for responsiveness
- State management for debate tracking
- Error handling and recovery
- Performance optimization through caching