import { useGame } from '../store/GameContext';

export default function Leaderboard() {
  const { users, getTitle, settings } = useGame();

  const sorted = [...users].sort((a, b) => b.balance - a.balance);

  return (
    <div className="bg-surface-card/50 border border-white/10 rounded-xl p-4">
      <h3 className="text-lg font-bold mb-3 flex items-center gap-2">
        🏆 Leaderboard
      </h3>
      <div className="space-y-2">
        {sorted.map((user, idx) => {
          const profit = user.balance - settings.startingBalance;
          const { title, icon } = getTitle(user);
          const totalBets = user.wins + user.losses;
          const winPct = totalBets > 0 ? Math.round((user.wins / totalBets) * 100) : 0;
          const maxBalance = Math.max(...sorted.map(u => u.balance), 1);
          const barWidth = (user.balance / maxBalance) * 100;

          return (
            <div
              key={user.id}
              className={`relative overflow-hidden rounded-lg p-3 transition-all ${
                idx === 0 ? 'bg-gold/10 border border-gold/30' : 'bg-white/5 border border-white/5'
              }`}
            >
              {/* Background bar */}
              <div
                className="absolute inset-y-0 left-0 opacity-10"
                style={{
                  width: `${barWidth}%`,
                  background: idx === 0 ? '#FFD700' : profit >= 0 ? '#22C55E' : '#EF4444',
                }}
              />
              <div className="relative flex items-center gap-3">
                {/* Rank */}
                <div className={`text-lg font-black w-8 text-center ${
                  idx === 0 ? 'text-gold' : idx === 1 ? 'text-patriots-silver' : idx === 2 ? 'text-[#CD7F32]' : 'text-white/30'
                }`}>
                  {idx === 0 ? '👑' : `#${idx + 1}`}
                </div>

                {/* Avatar & Name */}
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <span className="text-2xl">{user.avatar}</span>
                  <div className="min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="font-bold text-sm truncate">{user.name}</span>
                      {user.bailoutUsed && <span className="text-xs" title="Used bailout">💔</span>}
                    </div>
                    <div className="text-xs text-white/40 flex items-center gap-1">
                      <span>{icon} {title}</span>
                      <span>·</span>
                      <span>{user.wins}W-{user.losses}L</span>
                      {totalBets > 0 && <span>({winPct}%)</span>}
                      {user.streak > 1 && <span className="text-success">🔥{user.streak}</span>}
                      {user.streak < -1 && <span className="text-danger">❄️{Math.abs(user.streak)}</span>}
                    </div>
                  </div>
                </div>

                {/* Balance */}
                <div className="text-right">
                  <div className="font-black text-lg tabular-nums">${user.balance.toFixed(0)}</div>
                  <div className={`text-xs font-bold ${profit >= 0 ? 'text-success' : 'text-danger'}`}>
                    {profit >= 0 ? '+' : ''}{profit.toFixed(0)}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
        {users.length === 0 && (
          <div className="text-center py-4 text-white/30 text-sm">Add players to see the leaderboard</div>
        )}
      </div>
    </div>
  );
}
