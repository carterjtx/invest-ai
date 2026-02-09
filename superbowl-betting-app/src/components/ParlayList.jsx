import { useGame } from '../store/GameContext';

export default function ParlayList() {
  const { parlays, users, currentUser, dispatch, settings } = useGame();

  const getUserName = (id) => users.find(u => u.id === id)?.name || 'Unknown';
  const getUserAvatar = (id) => users.find(u => u.id === id)?.avatar || '👤';

  if (parlays.length === 0) return null;

  const handleResolveLeg = (parlayId, betId, won) => {
    dispatch({ type: 'RESOLVE_PARLAY_LEG', payload: { parlayId, betId, won } });
  };

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-bold text-white/60 flex items-center gap-1">
        🎲 Parlays ({parlays.length})
      </h4>
      {parlays.map(parlay => (
        <div
          key={parlay.id}
          className={`border rounded-xl p-3 ${
            parlay.status === 'won' ? 'border-success/50 bg-success/5' :
            parlay.status === 'lost' ? 'border-danger/50 bg-danger/5' :
            'border-gold/30 bg-gold/5'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="text-lg">{getUserAvatar(parlay.creatorId)}</span>
              <span className="text-sm font-bold">{getUserName(parlay.creatorId)}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                parlay.status === 'won' ? 'bg-success/20 text-success' :
                parlay.status === 'lost' ? 'bg-danger/20 text-danger' :
                'bg-gold/20 text-gold'
              }`}>
                {parlay.status === 'won' ? 'WON' : parlay.status === 'lost' ? 'LOST' : 'ACTIVE'}
              </span>
            </div>
            <div className="text-right">
              <div className="text-xs text-white/40">Wager: <span className="text-accent font-bold">${parlay.totalWager}</span></div>
              <div className="text-xs text-gold font-bold">{parlay.multiplier.toFixed(1)}x → ${parlay.potentialPayout.toFixed(0)}</div>
            </div>
          </div>

          {/* Legs */}
          <div className="space-y-1">
            {parlay.bets.map((bet, idx) => (
              <div key={bet.id} className="flex items-center gap-2 text-xs">
                <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${
                  bet.won === true ? 'bg-success text-white' :
                  bet.won === false ? 'bg-danger text-white' :
                  'bg-white/10 text-white/40'
                }`}>
                  {bet.won === true ? '✓' : bet.won === false ? '✗' : idx + 1}
                </span>
                <span className={`flex-1 ${bet.won === false ? 'line-through text-white/30' : 'text-white/70'}`}>
                  {bet.description}
                </span>
                {parlay.status === 'active' && !bet.resolved && (currentUser?.id === parlay.creatorId || currentUser?.isHost) && (
                  <div className="flex gap-1">
                    <button
                      onClick={() => handleResolveLeg(parlay.id, bet.id, true)}
                      className="bg-success/20 hover:bg-success/40 text-success px-2 py-0.5 rounded text-xs cursor-pointer"
                    >
                      Won
                    </button>
                    <button
                      onClick={() => handleResolveLeg(parlay.id, bet.id, false)}
                      className="bg-danger/20 hover:bg-danger/40 text-danger px-2 py-0.5 rounded text-xs cursor-pointer"
                    >
                      Lost
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
