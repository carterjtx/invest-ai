import { createContext, useContext, useReducer, useEffect, useCallback, useRef } from 'react';
import { storage } from '../utils/storage';
import { createInitialGameState, simulateTick, resumeFromHalftime } from '../utils/gameSimulator';
import { v4 as uuidv4 } from 'uuid';

const GameContext = createContext(null);

const DEFAULT_SETTINGS = {
  startingBalance: 200,
  minBet: 5,
  bailoutAmount: 50,
  isPaused: false,
  soundEnabled: true,
  darkMode: true,
  autoSaveInterval: 60000,
  gameSpeed: 8000, // ms between simulated plays
};

const AVATARS = [
  '😎', '🤠', '👻', '🎃', '🦊', '🐺', '🦁', '🐯', '🐻', '🦅',
  '🐉', '🦈', '🐙', '🦄', '🎩', '👑', '💀', '🤖', '👽', '🧙',
  '🥷', '🏈', '⭐', '🔥', '💎', '🎯', '🎪', '🃏', '🎰', '🏆'
];

function getTitle(balance, bailoutUsed, wins, totalBets) {
  if (totalBets >= 5 && wins === totalBets) return { title: 'Perfect Record', icon: '⭐' };
  if (bailoutUsed) return { title: 'Bankruptcy King', icon: '👑💔' };
  if (balance >= 500) return { title: 'Legend', icon: '👑' };
  if (balance >= 300) return { title: 'High Roller', icon: '🎰' };
  if (balance >= 200) return { title: 'Safe Bettor', icon: '🛡️' };
  if (balance >= 100) return { title: 'Casual Gambler', icon: '🎲' };
  if (balance >= 50) return { title: 'On Thin Ice', icon: '⚠️' };
  return { title: 'Degenerate', icon: '💸' };
}

function reducer(state, action) {
  switch (action.type) {
    case 'LOAD_STATE':
      return { ...state, ...action.payload };

    case 'ADD_USER': {
      const existing = state.users.find(u => u.name.toLowerCase() === action.payload.name.toLowerCase());
      if (existing) return state;
      const newUser = {
        id: uuidv4(),
        name: action.payload.name,
        avatar: action.payload.avatar || AVATARS[Math.floor(Math.random() * AVATARS.length)],
        balance: state.settings.startingBalance,
        bailoutUsed: false,
        isHost: state.users.length === 0,
        pin: action.payload.pin || '',
        wins: 0,
        losses: 0,
        totalWagered: 0,
        totalWon: 0,
        biggestWin: 0,
        streak: 0,
        balanceHistory: [state.settings.startingBalance],
        joinedAt: new Date().toISOString(),
      };
      return { ...state, users: [...state.users, newUser], currentUserId: state.currentUserId || newUser.id };
    }

    case 'REMOVE_USER': {
      const users = state.users.filter(u => u.id !== action.payload);
      return {
        ...state,
        users,
        currentUserId: state.currentUserId === action.payload ? (users[0]?.id || null) : state.currentUserId
      };
    }

    case 'SWITCH_USER':
      return { ...state, currentUserId: action.payload };

    case 'VERIFY_PIN':
      return state; // PIN verification handled in component

    case 'UPDATE_GAME':
      return { ...state, gameState: action.payload };

    case 'CREATE_BET': {
      if (state.settings.isPaused) return state;
      const bet = {
        id: uuidv4(),
        creatorId: action.payload.creatorId,
        acceptorId: null,
        description: action.payload.description,
        amount: action.payload.amount,
        odds: action.payload.odds || 1,
        category: action.payload.category || 'custom',
        status: 'open',
        expiresAt: action.payload.expiresAt || null,
        expirationType: action.payload.expirationType || 'time',
        createdAt: new Date().toISOString(),
        gameSnapshot: {
          homeScore: state.gameState.homeScore,
          awayScore: state.gameState.awayScore,
          quarter: state.gameState.quarter,
          time: state.gameState.timeRemaining,
        },
        resolution: null,
        creatorConfirmed: false,
        acceptorConfirmed: false,
        parlayId: null,
      };
      // Deduct from creator
      const users1 = state.users.map(u =>
        u.id === bet.creatorId ? { ...u, balance: u.balance - bet.amount, totalWagered: u.totalWagered + bet.amount } : u
      );
      return { ...state, bets: [bet, ...state.bets], users: users1 };
    }

    case 'ACCEPT_BET': {
      if (state.settings.isPaused) return state;
      const { betId, userId } = action.payload;
      const bets = state.bets.map(b =>
        b.id === betId ? { ...b, acceptorId: userId, status: 'active' } : b
      );
      const bet = bets.find(b => b.id === betId);
      const users2 = state.users.map(u =>
        u.id === userId ? { ...u, balance: u.balance - bet.amount, totalWagered: u.totalWagered + bet.amount } : u
      );
      return { ...state, bets, users: users2 };
    }

    case 'RESOLVE_BET': {
      const { betId, winnerId } = action.payload;
      const bet = state.bets.find(b => b.id === betId);
      if (!bet || bet.status !== 'active') return state;
      const payout = bet.amount * 2 * (bet.odds || 1);
      const loserId = winnerId === bet.creatorId ? bet.acceptorId : bet.creatorId;
      const bets2 = state.bets.map(b =>
        b.id === betId ? { ...b, status: 'resolved', resolution: { winnerId, loserId, payout, resolvedAt: new Date().toISOString() } } : b
      );
      const users3 = state.users.map(u => {
        if (u.id === winnerId) {
          const newBiggest = Math.max(u.biggestWin, payout - bet.amount);
          return {
            ...u,
            balance: u.balance + payout,
            wins: u.wins + 1,
            totalWon: u.totalWon + payout,
            biggestWin: newBiggest,
            streak: u.streak > 0 ? u.streak + 1 : 1,
            balanceHistory: [...u.balanceHistory, u.balance + payout],
          };
        }
        if (u.id === loserId) {
          return {
            ...u,
            losses: u.losses + 1,
            streak: u.streak < 0 ? u.streak - 1 : -1,
            balanceHistory: [...u.balanceHistory, u.balance],
          };
        }
        return u;
      });
      const notifications = [...state.notifications];
      const winner = users3.find(u => u.id === winnerId);
      const loser = users3.find(u => u.id === loserId);
      notifications.unshift({
        id: uuidv4(),
        userId: winnerId,
        text: `You won $${payout.toFixed(0)} on "${bet.description}"!`,
        type: 'win',
        read: false,
        createdAt: new Date().toISOString(),
      });
      notifications.unshift({
        id: uuidv4(),
        userId: loserId,
        text: `You lost on "${bet.description}"`,
        type: 'loss',
        read: false,
        createdAt: new Date().toISOString(),
      });

      return { ...state, bets: bets2, users: users3, notifications };
    }

    case 'CANCEL_BET': {
      const cancelBet = state.bets.find(b => b.id === action.payload);
      if (!cancelBet || cancelBet.status !== 'open') return state;
      const bets3 = state.bets.map(b =>
        b.id === action.payload ? { ...b, status: 'cancelled' } : b
      );
      const users4 = state.users.map(u =>
        u.id === cancelBet.creatorId ? { ...u, balance: u.balance + cancelBet.amount } : u
      );
      return { ...state, bets: bets3, users: users4 };
    }

    case 'EXPIRE_BETS': {
      const now = new Date();
      let updatedBets = [...state.bets];
      let updatedUsers = [...state.users];
      updatedBets = updatedBets.map(b => {
        if (b.status === 'open' && b.expiresAt && new Date(b.expiresAt) <= now) {
          // Refund creator
          updatedUsers = updatedUsers.map(u =>
            u.id === b.creatorId ? { ...u, balance: u.balance + b.amount } : u
          );
          return { ...b, status: 'expired' };
        }
        return b;
      });
      return { ...state, bets: updatedBets, users: updatedUsers };
    }

    case 'CREATE_PARLAY': {
      if (state.settings.isPaused) return state;
      const { userId, betDescriptions, totalWager } = action.payload;
      const parlayId = uuidv4();
      const multiplier = Math.pow(2, betDescriptions.length) - 0.5; // e.g., 3 bets = 7.5x
      const parlay = {
        id: parlayId,
        creatorId: userId,
        bets: betDescriptions.map(desc => ({
          id: uuidv4(),
          description: desc,
          resolved: false,
          won: null,
        })),
        totalWager,
        multiplier,
        potentialPayout: totalWager * multiplier,
        status: 'active',
        createdAt: new Date().toISOString(),
      };
      const users5 = state.users.map(u =>
        u.id === userId ? { ...u, balance: u.balance - totalWager, totalWagered: u.totalWagered + totalWager } : u
      );
      return { ...state, parlays: [parlay, ...state.parlays], users: users5 };
    }

    case 'RESOLVE_PARLAY_LEG': {
      const { parlayId, betId, won } = action.payload;
      const parlays = state.parlays.map(p => {
        if (p.id !== parlayId) return p;
        const updatedBets = p.bets.map(b =>
          b.id === betId ? { ...b, resolved: true, won } : b
        );
        const allResolved = updatedBets.every(b => b.resolved);
        const allWon = updatedBets.every(b => b.won === true);
        const anyLost = updatedBets.some(b => b.won === false);
        let status = p.status;
        if (anyLost) status = 'lost';
        else if (allResolved && allWon) status = 'won';
        return { ...p, bets: updatedBets, status };
      });

      let users6 = [...state.users];
      const parlay = parlays.find(p => p.id === parlayId);
      if (parlay.status === 'won') {
        users6 = users6.map(u =>
          u.id === parlay.creatorId ? {
            ...u,
            balance: u.balance + parlay.potentialPayout,
            wins: u.wins + 1,
            totalWon: u.totalWon + parlay.potentialPayout,
            biggestWin: Math.max(u.biggestWin, parlay.potentialPayout),
            streak: u.streak > 0 ? u.streak + 1 : 1,
          } : u
        );
      } else if (parlay.status === 'lost') {
        users6 = users6.map(u =>
          u.id === parlay.creatorId ? { ...u, losses: u.losses + 1, streak: u.streak < 0 ? u.streak - 1 : -1 } : u
        );
      }

      return { ...state, parlays, users: users6 };
    }

    case 'BAILOUT': {
      const user = state.users.find(u => u.id === action.payload);
      if (!user || user.balance > 0 || user.bailoutUsed) return state;
      const users7 = state.users.map(u =>
        u.id === action.payload ? {
          ...u,
          balance: state.settings.bailoutAmount,
          bailoutUsed: true,
          balanceHistory: [...u.balanceHistory, state.settings.bailoutAmount],
        } : u
      );
      const notifications2 = [...state.notifications, {
        id: uuidv4(),
        userId: action.payload,
        text: `Bailout activated! You received $${state.settings.bailoutAmount}`,
        type: 'bailout',
        read: false,
        createdAt: new Date().toISOString(),
      }];
      return { ...state, users: users7, notifications: notifications2 };
    }

    case 'ADMIN_BAILOUT': {
      const users8 = state.users.map(u =>
        u.id === action.payload ? {
          ...u,
          balance: u.balance + state.settings.bailoutAmount,
          balanceHistory: [...u.balanceHistory, u.balance + state.settings.bailoutAmount],
        } : u
      );
      return { ...state, users: users8 };
    }

    case 'ADD_NOTIFICATION':
      return {
        ...state,
        notifications: [action.payload, ...state.notifications].slice(0, 100)
      };

    case 'MARK_NOTIFICATION_READ':
      return {
        ...state,
        notifications: state.notifications.map(n =>
          n.id === action.payload ? { ...n, read: true } : n
        )
      };

    case 'CLEAR_NOTIFICATIONS':
      return {
        ...state,
        notifications: state.notifications.map(n =>
          n.userId === action.payload ? { ...n, read: true } : n
        )
      };

    case 'UPDATE_SETTINGS':
      return { ...state, settings: { ...state.settings, ...action.payload } };

    case 'TOGGLE_PAUSE':
      return { ...state, settings: { ...state.settings, isPaused: !state.settings.isPaused } };

    case 'RESET_GAME': {
      const resetUsers = state.users.map(u => ({
        ...u,
        balance: state.settings.startingBalance,
        bailoutUsed: false,
        wins: 0,
        losses: 0,
        totalWagered: 0,
        totalWon: 0,
        biggestWin: 0,
        streak: 0,
        balanceHistory: [state.settings.startingBalance],
      }));
      return {
        ...state,
        users: resetUsers,
        bets: [],
        parlays: [],
        notifications: [],
        gameState: createInitialGameState(),
      };
    }

    case 'UPDATE_USER_AVATAR':
      return {
        ...state,
        users: state.users.map(u =>
          u.id === action.payload.userId ? { ...u, avatar: action.payload.avatar } : u
        )
      };

    case 'MANUAL_SCORE_UPDATE':
      return {
        ...state,
        gameState: {
          ...state.gameState,
          homeScore: action.payload.homeScore ?? state.gameState.homeScore,
          awayScore: action.payload.awayScore ?? state.gameState.awayScore,
        }
      };

    default:
      return state;
  }
}

const initialState = {
  users: [],
  currentUserId: null,
  bets: [],
  parlays: [],
  notifications: [],
  gameState: createInitialGameState(),
  settings: DEFAULT_SETTINGS,
};

export function GameProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const gameTimerRef = useRef(null);
  const autoSaveRef = useRef(null);
  const expiryRef = useRef(null);

  // Load saved state on mount
  useEffect(() => {
    const saved = storage.get('game_state');
    if (saved) {
      dispatch({ type: 'LOAD_STATE', payload: { ...saved, gameState: saved.gameState || createInitialGameState() } });
    }
  }, []);

  // Auto-save
  useEffect(() => {
    autoSaveRef.current = setInterval(() => {
      storage.set('game_state', {
        users: state.users,
        currentUserId: state.currentUserId,
        bets: state.bets,
        parlays: state.parlays,
        notifications: state.notifications,
        gameState: state.gameState,
        settings: state.settings,
      });
    }, state.settings.autoSaveInterval);
    return () => clearInterval(autoSaveRef.current);
  }, [state]);

  // Game simulation timer
  useEffect(() => {
    if (!state.gameState.isLive || state.gameState.isHalftime || state.gameState.isGameOver) {
      clearInterval(gameTimerRef.current);
      return;
    }
    gameTimerRef.current = setInterval(() => {
      dispatch({ type: 'UPDATE_GAME', payload: simulateTick(state.gameState) });
    }, state.settings.gameSpeed);
    return () => clearInterval(gameTimerRef.current);
  }, [state.gameState.isLive, state.gameState.isHalftime, state.gameState.isGameOver, state.settings.gameSpeed]);

  // Expire bets periodically
  useEffect(() => {
    expiryRef.current = setInterval(() => {
      dispatch({ type: 'EXPIRE_BETS' });
    }, 10000);
    return () => clearInterval(expiryRef.current);
  }, []);

  const saveGame = useCallback(() => {
    storage.set('game_state', {
      users: state.users,
      currentUserId: state.currentUserId,
      bets: state.bets,
      parlays: state.parlays,
      notifications: state.notifications,
      gameState: state.gameState,
      settings: state.settings,
    });
  }, [state]);

  const currentUser = state.users.find(u => u.id === state.currentUserId) || null;

  const value = {
    ...state,
    currentUser,
    dispatch,
    saveGame,
    getTitle: (user) => getTitle(user.balance, user.bailoutUsed, user.wins, user.wins + user.losses),
    resumeHalftime: () => dispatch({ type: 'UPDATE_GAME', payload: resumeFromHalftime(state.gameState) }),
    AVATARS,
  };

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
}

export function useGame() {
  const ctx = useContext(GameContext);
  if (!ctx) throw new Error('useGame must be used within GameProvider');
  return ctx;
}
