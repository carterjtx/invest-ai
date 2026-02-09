import { useState } from 'react';
import { useGame } from '../store/GameContext';

export default function TransactionHistory({ userId, onClose }) {
  const { bets, parlays, users, settings } = useGame();
  const user = users.find(u => u.id === userId);
  const [filter, setFilter] = useState('all');

  if (!user) return null;

  // Collect all transactions for this user
  const transactions = [];

  bets.forEach(bet => {
    if (bet.creatorId === userId) {
      transactions.push({
        id: bet.id,
        type: 'bet_created',
        description: bet.description,
        amount: -bet.amount,
        status: bet.status,
        timestamp: bet.createdAt,
        result: bet.resolution ? (bet.resolution.winnerId === userId ? 'won' : 'lost') : null,
        payout: bet.resolution?.winnerId === userId ? bet.resolution.payout : 0,
      });
    }
    if (bet.acceptorId === userId) {
      transactions.push({
        id: bet.id + '_accept',
        type: 'bet_accepted',
        description: bet.description,
        amount: -bet.amount,
        status: bet.status,
        timestamp: bet.createdAt,
        result: bet.resolution ? (bet.resolution.winnerId === userId ? 'won' : 'lost') : null,
        payout: bet.resolution?.winnerId === userId ? bet.resolution.payout : 0,
      });
    }
    if (bet.status === 'cancelled' && bet.creatorId === userId) {
      transactions.push({
        id: bet.id + '_refund',
        type: 'refund',
        description: `Refund: ${bet.description}`,
        amount: bet.amount,
        status: 'refunded',
        timestamp: bet.createdAt,
      });
    }
  });

  parlays.forEach(parlay => {
    if (parlay.creatorId === userId) {
      transactions.push({
        id: parlay.id,
        type: 'parlay',
        description: `Parlay (${parlay.bets.length} legs)`,
        amount: -parlay.totalWager,
        status: parlay.status,
        timestamp: parlay.createdAt,
        result: parlay.status === 'won' ? 'won' : parlay.status === 'lost' ? 'lost' : null,
        payout: parlay.status === 'won' ? parlay.potentialPayout : 0,
      });
    }
  });

  const filtered = transactions
    .filter(t => {
      if (filter === 'won') return t.result === 'won';
      if (filter === 'lost') return t.result === 'lost';
      if (filter === 'pending') return t.status === 'open' || t.status === 'active';
      return true;
    })
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

  const exportHistory = () => {
    const csv = ['Date,Type,Description,Amount,Result,Payout']
      .concat(filtered.map(t =>
        `${new Date(t.timestamp).toLocaleString()},${t.type},${t.description.replace(/,/g, ';')},${t.amount},${t.result || 'pending'},${t.payout || 0}`
      ))
      .join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${user.name}_betting_history.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-surface-light border border-white/10 rounded-2xl p-6 w-full max-w-lg max-h-[85vh] flex flex-col" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold">Transaction History — {user.name}</h3>
          <button onClick={onClose} className="text-white/40 hover:text-white text-2xl cursor-pointer">&times;</button>
        </div>

        {/* Summary */}
        <div className="grid grid-cols-3 gap-2 mb-4">
          <div className="bg-surface rounded-lg p-2 text-center">
            <div className="text-sm font-bold">{transactions.length}</div>
            <div className="text-xs text-white/40">Total Bets</div>
          </div>
          <div className="bg-surface rounded-lg p-2 text-center">
            <div className="text-sm font-bold text-success">${user.totalWon.toFixed(0)}</div>
            <div className="text-xs text-white/40">Won</div>
          </div>
          <div className="bg-surface rounded-lg p-2 text-center">
            <div className="text-sm font-bold text-accent">${user.totalWagered.toFixed(0)}</div>
            <div className="text-xs text-white/40">Wagered</div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex gap-1">
            {['all', 'won', 'lost', 'pending'].map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-2 py-1 rounded text-xs font-bold capitalize cursor-pointer ${
                  filter === f ? 'bg-accent text-white' : 'bg-white/10 text-white/40'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
          <button
            onClick={exportHistory}
            className="bg-white/10 hover:bg-white/20 text-xs px-3 py-1 rounded-lg cursor-pointer"
            title="Export as CSV"
          >
            📥 Export
          </button>
        </div>

        {/* Transaction list */}
        <div className="flex-1 overflow-y-auto space-y-1">
          {filtered.map(t => (
            <div key={t.id} className="flex items-center gap-3 bg-surface/50 rounded-lg p-2 text-sm">
              <span className={`w-8 h-8 rounded-full flex items-center justify-center text-lg ${
                t.result === 'won' ? 'bg-success/20' :
                t.result === 'lost' ? 'bg-danger/20' :
                t.type === 'refund' ? 'bg-white/10' :
                'bg-warning/20'
              }`}>
                {t.result === 'won' ? '✅' : t.result === 'lost' ? '❌' : t.type === 'refund' ? '↩️' : '⏳'}
              </span>
              <div className="flex-1 min-w-0">
                <div className="text-xs truncate">{t.description}</div>
                <div className="text-xs text-white/30">
                  {new Date(t.timestamp).toLocaleTimeString()}
                </div>
              </div>
              <div className="text-right">
                <div className={`text-sm font-bold ${t.amount > 0 ? 'text-success' : 'text-danger'}`}>
                  {t.amount > 0 ? '+' : ''}{t.amount.toFixed(0)}
                </div>
                {t.payout > 0 && (
                  <div className="text-xs text-success">+${t.payout.toFixed(0)}</div>
                )}
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="text-center py-8 text-white/30 text-sm">No transactions yet</div>
          )}
        </div>
      </div>
    </div>
  );
}
