import { useState } from 'react';
import { useGame } from '../store/GameContext';

export default function UserProfile({ userId, onClose }) {
  const { users, bets, getTitle, AVATARS, dispatch, settings } = useGame();
  const user = users.find(u => u.id === userId);
  const [editAvatar, setEditAvatar] = useState(false);

  if (!user) return null;

  const { title, icon } = getTitle(user);
  const totalBets = user.wins + user.losses;
  const winPct = totalBets > 0 ? Math.round((user.wins / totalBets) * 100) : 0;
  const profit = user.balance - settings.startingBalance;
  const userBets = bets.filter(b => b.creatorId === userId || b.acceptorId === userId);
  const activeBets = userBets.filter(b => ['open', 'active'].includes(b.status));
  const resolvedBets = userBets.filter(b => b.status === 'resolved');

  // Simple balance history chart
  const history = user.balanceHistory || [settings.startingBalance];
  const maxBal = Math.max(...history, settings.startingBalance + 1);
  const minBal = Math.min(...history, 0);
  const range = maxBal - minBal || 1;
  const chartWidth = 280;
  const chartHeight = 80;
  const points = history.map((val, i) => {
    const x = (i / Math.max(history.length - 1, 1)) * chartWidth;
    const y = chartHeight - ((val - minBal) / range) * chartHeight;
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-surface-light border border-white/10 rounded-2xl p-6 w-full max-w-md" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-3">
            <button onClick={() => setEditAvatar(!editAvatar)} className="text-4xl cursor-pointer hover:scale-110 transition-transform" title="Change avatar">
              {user.avatar}
            </button>
            <div>
              <h3 className="text-xl font-bold">{user.name}</h3>
              <div className="text-sm text-white/50">{icon} {title}</div>
            </div>
          </div>
          <button onClick={onClose} className="text-white/40 hover:text-white text-2xl cursor-pointer">&times;</button>
        </div>

        {editAvatar && (
          <div className="grid grid-cols-10 gap-1 mb-4 p-2 bg-surface rounded-lg border border-white/10">
            {AVATARS.map(a => (
              <button
                key={a}
                onClick={() => { dispatch({ type: 'UPDATE_USER_AVATAR', payload: { userId, avatar: a } }); setEditAvatar(false); }}
                className={`text-xl p-1 rounded cursor-pointer hover:bg-white/10 ${user.avatar === a ? 'bg-accent/30' : ''}`}
              >
                {a}
              </button>
            ))}
          </div>
        )}

        {/* Stats grid */}
        <div className="grid grid-cols-3 gap-2 mb-4">
          <div className="bg-surface rounded-lg p-3 text-center">
            <div className="text-2xl font-black text-accent">${user.balance.toFixed(0)}</div>
            <div className="text-xs text-white/40">Balance</div>
          </div>
          <div className="bg-surface rounded-lg p-3 text-center">
            <div className={`text-2xl font-black ${profit >= 0 ? 'text-success' : 'text-danger'}`}>
              {profit >= 0 ? '+' : ''}{profit.toFixed(0)}
            </div>
            <div className="text-xs text-white/40">Profit/Loss</div>
          </div>
          <div className="bg-surface rounded-lg p-3 text-center">
            <div className="text-2xl font-black text-gold">${user.biggestWin.toFixed(0)}</div>
            <div className="text-xs text-white/40">Biggest Win</div>
          </div>
        </div>

        <div className="grid grid-cols-4 gap-2 mb-4">
          <div className="bg-surface rounded-lg p-2 text-center">
            <div className="text-lg font-bold">{user.wins}</div>
            <div className="text-xs text-success">Wins</div>
          </div>
          <div className="bg-surface rounded-lg p-2 text-center">
            <div className="text-lg font-bold">{user.losses}</div>
            <div className="text-xs text-danger">Losses</div>
          </div>
          <div className="bg-surface rounded-lg p-2 text-center">
            <div className="text-lg font-bold">{winPct}%</div>
            <div className="text-xs text-white/40">Win Rate</div>
          </div>
          <div className="bg-surface rounded-lg p-2 text-center">
            <div className="text-lg font-bold">${user.totalWagered.toFixed(0)}</div>
            <div className="text-xs text-white/40">Wagered</div>
          </div>
        </div>

        {/* Balance history chart */}
        <div className="bg-surface rounded-lg p-3 mb-4">
          <div className="text-xs text-white/40 mb-2">Balance History</div>
          <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-20">
            {/* Starting line */}
            <line
              x1="0"
              y1={chartHeight - ((settings.startingBalance - minBal) / range) * chartHeight}
              x2={chartWidth}
              y2={chartHeight - ((settings.startingBalance - minBal) / range) * chartHeight}
              stroke="rgba(255,255,255,0.1)"
              strokeDasharray="4"
            />
            <polyline
              fill="none"
              stroke={profit >= 0 ? '#22C55E' : '#EF4444'}
              strokeWidth="2"
              points={points}
            />
          </svg>
        </div>

        {/* Active bets */}
        {activeBets.length > 0 && (
          <div className="mb-4">
            <div className="text-xs text-white/40 mb-1">Active Bets ({activeBets.length})</div>
            {activeBets.slice(0, 3).map(b => (
              <div key={b.id} className="text-xs bg-surface rounded p-2 mb-1 text-white/60">
                {b.description} — ${b.amount}
              </div>
            ))}
          </div>
        )}

        {/* Badges */}
        <div className="flex flex-wrap gap-1">
          {user.bailoutUsed && (
            <span className="bg-danger/20 text-danger text-xs px-2 py-0.5 rounded-full">💔 Used Bailout</span>
          )}
          {user.wins >= 5 && user.losses === 0 && (
            <span className="bg-gold/20 text-gold text-xs px-2 py-0.5 rounded-full">⭐ Perfect Record</span>
          )}
          {user.streak >= 3 && (
            <span className="bg-success/20 text-success text-xs px-2 py-0.5 rounded-full">🔥 {user.streak} Win Streak</span>
          )}
          {user.biggestWin >= 100 && (
            <span className="bg-gold/20 text-gold text-xs px-2 py-0.5 rounded-full">💰 Big Winner</span>
          )}
          {user.isHost && (
            <span className="bg-accent/20 text-accent text-xs px-2 py-0.5 rounded-full">🎮 Host</span>
          )}
        </div>
      </div>
    </div>
  );
}
