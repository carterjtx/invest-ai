import { useState } from 'react';
import { useGame } from '../store/GameContext';
import { playBetSound, playWinSound, playLoseSound } from '../utils/sounds';

function TimeRemaining({ expiresAt }) {
  const [now, setNow] = useState(Date.now());

  // Update every second
  useState(() => {
    const interval = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(interval);
  });

  if (!expiresAt) return <span className="text-white/30">No expiry</span>;

  const diff = new Date(expiresAt).getTime() - now;
  if (diff <= 0) return <span className="text-danger font-bold">Expired</span>;

  const mins = Math.floor(diff / 60000);
  const secs = Math.floor((diff % 60000) / 1000);
  const isUrgent = diff < 60000;

  return (
    <span className={`tabular-nums ${isUrgent ? 'text-danger font-bold animate-pulse' : 'text-warning'}`}>
      {mins}:{secs.toString().padStart(2, '0')}
    </span>
  );
}

export default function BetFeed() {
  const { bets, users, currentUser, dispatch, settings } = useGame();
  const [filter, setFilter] = useState('all'); // all, open, active, resolved
  const [sort, setSort] = useState('newest');
  const [resolveModal, setResolveModal] = useState(null);

  const getUserName = (id) => users.find(u => u.id === id)?.name || 'Unknown';
  const getUserAvatar = (id) => users.find(u => u.id === id)?.avatar || '👤';

  const filteredBets = bets
    .filter(b => {
      if (filter === 'open') return b.status === 'open';
      if (filter === 'active') return b.status === 'active';
      if (filter === 'resolved') return ['resolved', 'expired', 'cancelled'].includes(b.status);
      return true;
    })
    .sort((a, b) => {
      if (sort === 'newest') return new Date(b.createdAt) - new Date(a.createdAt);
      if (sort === 'amount') return b.amount - a.amount;
      if (sort === 'ending') {
        if (!a.expiresAt) return 1;
        if (!b.expiresAt) return -1;
        return new Date(a.expiresAt) - new Date(b.expiresAt);
      }
      return 0;
    });

  const handleAccept = (betId) => {
    const bet = bets.find(b => b.id === betId);
    if (!currentUser || currentUser.id === bet.creatorId || currentUser.balance < bet.amount) return;
    dispatch({ type: 'ACCEPT_BET', payload: { betId, userId: currentUser.id } });
    if (settings.soundEnabled) playBetSound();
    dispatch({
      type: 'ADD_NOTIFICATION',
      payload: {
        id: Date.now().toString(),
        userId: bet.creatorId,
        text: `${currentUser.name} accepted your bet: "${bet.description}"`,
        type: 'accepted',
        read: false,
        createdAt: new Date().toISOString(),
      }
    });
  };

  const handleResolve = (betId, winnerId) => {
    dispatch({ type: 'RESOLVE_BET', payload: { betId, winnerId } });
    if (settings.soundEnabled) {
      if (winnerId === currentUser?.id) playWinSound();
      else playLoseSound();
    }
    setResolveModal(null);
  };

  const statusColors = {
    open: 'border-success/50 bg-success/5',
    active: 'border-warning/50 bg-warning/5',
    resolved: 'border-white/10 bg-white/5',
    expired: 'border-white/10 bg-white/3',
    cancelled: 'border-white/10 bg-white/3',
  };

  const statusBadge = {
    open: <span className="bg-success/20 text-success text-xs px-2 py-0.5 rounded-full font-bold">OPEN</span>,
    active: <span className="bg-warning/20 text-warning text-xs px-2 py-0.5 rounded-full font-bold">ACTIVE</span>,
    resolved: <span className="bg-white/10 text-white/60 text-xs px-2 py-0.5 rounded-full font-bold">RESOLVED</span>,
    expired: <span className="bg-white/10 text-white/40 text-xs px-2 py-0.5 rounded-full font-bold">EXPIRED</span>,
    cancelled: <span className="bg-white/10 text-white/40 text-xs px-2 py-0.5 rounded-full font-bold">CANCELLED</span>,
  };

  return (
    <div>
      {/* Filters */}
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <div className="flex gap-1">
          {['all', 'open', 'active', 'resolved'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-lg text-xs font-bold capitalize cursor-pointer transition-colors ${
                filter === f ? 'bg-accent text-white' : 'bg-white/10 hover:bg-white/20 text-white/60'
              }`}
            >
              {f} {f !== 'all' && `(${bets.filter(b => f === 'resolved' ? ['resolved','expired','cancelled'].includes(b.status) : b.status === f).length})`}
            </button>
          ))}
        </div>
        <select
          value={sort}
          onChange={e => setSort(e.target.value)}
          className="bg-surface border border-white/10 rounded-lg px-2 py-1 text-xs text-white/60"
        >
          <option value="newest">Newest</option>
          <option value="amount">Highest Wager</option>
          <option value="ending">Ending Soon</option>
        </select>
      </div>

      {/* Bet cards */}
      <div className="space-y-2 max-h-[60vh] overflow-y-auto pr-1">
        {filteredBets.length === 0 && (
          <div className="text-center py-8 text-white/30">
            <div className="text-4xl mb-2">🏈</div>
            <div>No bets yet. Create one!</div>
          </div>
        )}
        {filteredBets.map(bet => (
          <div
            key={bet.id}
            className={`border rounded-xl p-3 card-hover ${statusColors[bet.status]}`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg">{getUserAvatar(bet.creatorId)}</span>
                  <span className="text-sm font-bold">{getUserName(bet.creatorId)}</span>
                  {statusBadge[bet.status]}
                </div>
                <p className="text-sm text-white/90 font-medium mb-1">{bet.description}</p>
                <div className="flex items-center gap-3 text-xs text-white/40">
                  <span className="text-accent font-bold">${bet.amount}</span>
                  {bet.odds > 1 && <span className="text-gold">{bet.odds}x odds</span>}
                  {bet.gameSnapshot && (
                    <span>Score: {bet.gameSnapshot.awayScore}-{bet.gameSnapshot.homeScore}</span>
                  )}
                  <TimeRemaining expiresAt={bet.expiresAt} />
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex flex-col gap-1">
                {bet.status === 'open' && currentUser && currentUser.id !== bet.creatorId && currentUser.balance >= bet.amount && (
                  <button
                    onClick={() => handleAccept(bet.id)}
                    className="bg-success hover:bg-success/80 text-white text-xs font-bold px-3 py-1.5 rounded-lg cursor-pointer transition-colors"
                  >
                    Take Bet
                  </button>
                )}
                {bet.status === 'open' && currentUser?.id === bet.creatorId && (
                  <button
                    onClick={() => dispatch({ type: 'CANCEL_BET', payload: bet.id })}
                    className="bg-white/10 hover:bg-white/20 text-white/60 text-xs px-3 py-1.5 rounded-lg cursor-pointer"
                  >
                    Cancel
                  </button>
                )}
                {bet.status === 'active' && (currentUser?.id === bet.creatorId || currentUser?.isHost) && (
                  <button
                    onClick={() => setResolveModal(bet)}
                    className="bg-gold/80 hover:bg-gold text-black text-xs font-bold px-3 py-1.5 rounded-lg cursor-pointer"
                  >
                    Resolve
                  </button>
                )}
              </div>
            </div>

            {/* Acceptor info */}
            {bet.acceptorId && (
              <div className="mt-2 pt-2 border-t border-white/5 flex items-center gap-2 text-xs text-white/50">
                <span>vs</span>
                <span className="text-lg">{getUserAvatar(bet.acceptorId)}</span>
                <span className="font-bold">{getUserName(bet.acceptorId)}</span>
              </div>
            )}

            {/* Resolution info */}
            {bet.resolution && (
              <div className="mt-2 pt-2 border-t border-white/5 text-xs">
                <span className="text-success font-bold">
                  🏆 {getUserName(bet.resolution.winnerId)} won ${bet.resolution.payout.toFixed(0)}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Resolve modal */}
      {resolveModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50" onClick={() => setResolveModal(null)}>
          <div className="bg-surface-light border border-white/10 rounded-2xl p-6 w-full max-w-sm mx-4" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-2">Resolve Bet</h3>
            <p className="text-sm text-white/60 mb-4">"{resolveModal.description}"</p>
            <p className="text-xs text-white/40 mb-4">Select the winner:</p>
            <div className="space-y-2">
              <button
                onClick={() => handleResolve(resolveModal.id, resolveModal.creatorId)}
                className="w-full flex items-center gap-2 bg-surface hover:bg-success/20 border border-white/10 rounded-lg p-3 cursor-pointer transition-colors"
              >
                <span className="text-xl">{getUserAvatar(resolveModal.creatorId)}</span>
                <span className="font-bold">{getUserName(resolveModal.creatorId)}</span>
                <span className="text-xs text-white/40">(creator)</span>
              </button>
              <button
                onClick={() => handleResolve(resolveModal.id, resolveModal.acceptorId)}
                className="w-full flex items-center gap-2 bg-surface hover:bg-success/20 border border-white/10 rounded-lg p-3 cursor-pointer transition-colors"
              >
                <span className="text-xl">{getUserAvatar(resolveModal.acceptorId)}</span>
                <span className="font-bold">{getUserName(resolveModal.acceptorId)}</span>
                <span className="text-xs text-white/40">(acceptor)</span>
              </button>
            </div>
            <button
              onClick={() => setResolveModal(null)}
              className="w-full mt-3 bg-white/10 hover:bg-white/20 py-2 rounded-lg text-sm cursor-pointer"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
