/**
 * Atom State Management for Stock Debate Advisor
 * 
 * This file uses Recoil atoms for state management.
 * Can be easily adapted to other state management libraries (Zustand, Jotai, etc.)
 * 
 * Usage:
 * ```tsx
 * import { useRecoilState } from 'recoil';
 * import { debateSessionState, debateResultState } from './atoms';
 * 
 * function Component() {
 *   const [session, setSession] = useRecoilState(debateSessionState);
 *   const [result, setResult] = useRecoilState(debateResultState);
 * }
 * ```
 */

import { atom, selector } from 'recoil';
import { DebateSessionResponse, DebateResultResponse, DebateStatusResponse } from '../api/debate-api';

// ==================== UI State ====================

/**
 * Current tab/view
 */
export const currentTabState = atom<'home' | 'debate' | 'history'>({
  key: 'currentTab',
  default: 'home',
});

/**
 * Loading state
 */
export const isLoadingState = atom<boolean>({
  key: 'isLoading',
  default: false,
});

/**
 * Error message
 */
export const errorMessageState = atom<string | null>({
  key: 'errorMessage',
  default: null,
});

/**
 * Success message
 */
export const successMessageState = atom<string | null>({
  key: 'successMessage',
  default: null,
});

// ==================== Symbol State ====================

/**
 * Available stock symbols
 */
export const availableSymbolsState = atom<string[]>({
  key: 'availableSymbols',
  default: [],
});

/**
 * Currently selected symbol
 */
export const selectedSymbolState = atom<string>({
  key: 'selectedSymbol',
  default: 'MBB',
});

/**
 * Number of debate rounds
 */
export const debateRoundsState = atom<number>({
  key: 'debateRounds',
  default: 3,
});

// ==================== Debate Session State ====================

/**
 * Active debate session
 */
export const debateSessionState = atom<DebateSessionResponse | null>({
  key: 'debateSession',
  default: null,
});

/**
 * Debate session status (for polling)
 */
export const debateStatusState = atom<DebateStatusResponse | null>({
  key: 'debateStatus',
  default: null,
});

/**
 * Debate result
 */
export const debateResultState = atom<DebateResultResponse | null>({
  key: 'debateResult',
  default: null,
});

/**
 * Session history
 */
export const sessionHistoryState = atom<DebateSessionResponse[]>({
  key: 'sessionHistory',
  default: [],
});

// ==================== Selectors (Derived State) ====================

/**
 * Is debate in progress
 */
export const isDebateInProgressSelector = selector<boolean>({
  key: 'isDebateInProgress',
  get: ({ get }) => {
    const session = get(debateSessionState);
    return session?.status === 'pending' || session?.status === 'in_progress';
  },
});

/**
 * Debate progress percentage
 */
export const debateProgressSelector = selector<number>({
  key: 'debateProgress',
  get: ({ get }) => {
    const status = get(debateStatusState);
    return status?.progress ?? 0;
  },
});

/**
 * Current debate recommendation
 */
export const recommendationSelector = selector<string | null>({
  key: 'recommendation',
  get: ({ get }) => {
    const result = get(debateResultState);
    return result?.verdict?.recommendation ?? null;
  },
});

/**
 * Can start new debate
 */
export const canStartDebateSelector = selector<boolean>({
  key: 'canStartDebate',
  get: ({ get }) => {
    const isLoading = get(isLoadingState);
    const inProgress = get(isDebateInProgressSelector);
    return !isLoading && !inProgress;
  },
});

/**
 * Formatted debate summary
 */
export const formattedSummarySelector = selector<string>({
  key: 'formattedSummary',
  get: ({ get }) => {
    const result = get(debateResultState);
    if (!result?.debate_summary) return '';

    // Format the summary - truncate if too long
    const summary = result.debate_summary;
    return summary.length > 500 ? summary.substring(0, 500) + '...' : summary;
  },
});

/**
 * All active sessions
 */
export const activeSessions = atom<Map<string, DebateResultResponse>>({
  key: 'activeSessions',
  default: new Map(),
});

// ==================== Advanced Selectors ====================

/**
 * Debate statistics
 */
export const debateStatsSelector = selector({
  key: 'debateStats',
  get: ({ get }) => {
    const history = get(sessionHistoryState);
    
    const stats = {
      totalDebates: history.length,
      completedDebates: history.filter(s => s.status === 'completed').length,
      failedDebates: history.filter(s => s.status === 'failed').length,
      averageRounds: history.length > 0
        ? Math.round(history.reduce((sum, s) => sum + (s.rounds || 3), 0) / history.length)
        : 0,
    };

    return stats;
  },
});

/**
 * Recommendation distribution
 */
export const recommendationStatsSelector = selector({
  key: 'recommendationStats',
  get: ({ get }) => {
    const history = get(sessionHistoryState);
    
    const stats = {
      buy: 0,
      hold: 0,
      sell: 0,
    };

    // This would need to fetch full results for each session
    // For now, returning empty stats
    return stats;
  },
});

// ==================== Reset Actions ====================

/**
 * Atom to reset all state
 */
export const resetStateAtom = atom({
  key: 'resetState',
  default: 0,
});

/**
 * Helper to reset specific debate state
 */
export function createResetDebateState() {
  return (set: any) => {
    set(debateSessionState, null);
    set(debateStatusState, null);
    set(debateResultState, null);
    set(errorMessageState, null);
    set(isLoadingState, false);
  };
}
