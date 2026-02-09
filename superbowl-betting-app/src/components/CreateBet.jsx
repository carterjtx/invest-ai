import { useState } from 'react';
import { useGame } from '../store/GameContext';
import { playBetSound } from '../utils/sounds';

const BET_TEMPLATES = [
  { category: 'score', label: 'Final Score Prediction', desc: '{team} wins by {points}+ points', icon: '🏆' },
  { category: 'touchdown', label: 'Next Touchdown', desc: '{team} scores the next touchdown', icon: '🏈' },
  { category: 'mvp', label: 'MVP Prediction', desc: '{player} wins Super Bowl MVP', icon: '⭐' },
  { category: 'quarter', label: 'Quarter Winner', desc: '{team} leads after Q{quarter}', icon: '⏰' },
  { category: 'prop', label: 'Over/Under Yards', desc: 'Total game yards over/under {yards}', icon: '📊' },
  { category: 'prop', label: 'Total Points', desc: 'Total points over/under {points}', icon: '🎯' },
  { category: 'prop', label: 'First Turnover', desc: '{team} commits the first turnover', icon: '🔄' },
  { category: 'fun', label: 'Coin Toss Winner', desc: '{team} wins the coin toss', icon: '🪙' },
  { category: 'fun', label: 'Longest Play', desc: 'Longest play of the game is {yards}+ yards', icon: '🏃' },
  { category: 'fun', label: 'Penalty Count', desc: 'Total penalties over/under {count}', icon: '🟡' },
];

const EXPIRY_OPTIONS = [
  { label: '5 minutes', value: 5 },
  { label: '15 minutes', value: 15 },
  { label: '30 minutes', value: 30 },
  { label: 'End of quarter', value: 'quarter' },
  { label: 'Halftime', value: 'halftime' },
  { label: 'End of game', value: 'game' },
  { label: 'No expiry', value: null },
];

export default function CreateBet({ onClose }) {
  const { currentUser, gameState, dispatch, settings } = useGame();
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState(10);
  const [odds, setOdds] = useState(1);
  const [expiry, setExpiry] = useState(null);
  const [showTemplates, setShowTemplates] = useState(true);

  if (!currentUser) return null;

  const canBet = currentUser.balance >= settings.minBet && !settings.isPaused && currentUser.balance > 0;

  const applyTemplate = (template) => {
    let desc = template.desc;
    const team = gameState.possession === 'home' ? gameState.homeTeam.name : gameState.awayTeam.name;
    desc = desc.replace('{team}', team)
      .replace('{points}', '7')
      .replace('{player}', 'Mahomes')
      .replace('{quarter}', String(gameState.quarter))
      .replace('{yards}', '300')
      .replace('{count}', '10');
    setDescription(desc);
    setShowTemplates(false);
  };

  const handleSubmit = () => {
    if (!description.trim() || amount < settings.minBet || amount > currentUser.balance) return;

    let expiresAt = null;
    if (typeof expiry === 'number') {
      expiresAt = new Date(Date.now() + expiry * 60000).toISOString();
    }

    dispatch({
      type: 'CREATE_BET',
      payload: {
        creatorId: currentUser.id,
        description: description.trim(),
        amount,
        odds,
        expiresAt,
        expirationType: typeof expiry === 'string' ? expiry : 'time',
      }
    });

    if (settings.soundEnabled) playBetSound();
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-surface-light border border-white/10 rounded-2xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold">Create a Bet</h3>
          <button onClick={onClose} className="text-white/40 hover:text-white text-2xl cursor-pointer">&times;</button>
        </div>

        {!canBet && (
          <div className="bg-danger/20 border border-danger/30 rounded-lg p-3 mb-4 text-sm text-danger">
            {settings.isPaused ? 'Betting is currently paused by the host.' :
             currentUser.balance <= 0 ? 'You have no funds to bet.' :
             `Minimum bet is $${settings.minBet}.`}
          </div>
        )}

        {/* Templates */}
        {showTemplates && (
          <div className="mb-4">
            <h4 className="text-sm text-white/60 mb-2">Quick Templates</h4>
            <div className="grid grid-cols-2 gap-2">
              {BET_TEMPLATES.map((t, i) => (
                <button
                  key={i}
                  onClick={() => applyTemplate(t)}
                  className="bg-surface hover:bg-surface-card border border-white/5 rounded-lg p-2 text-left transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-1.5">
                    <span>{t.icon}</span>
                    <span className="text-xs font-semibold">{t.label}</span>
                  </div>
                </button>
              ))}
            </div>
            <button
              onClick={() => setShowTemplates(false)}
              className="text-accent text-xs mt-2 hover:underline cursor-pointer"
            >
              Write custom bet instead
            </button>
          </div>
        )}

        <div className="space-y-4">
          {/* Description */}
          <div>
            <label className="text-sm text-white/60 block mb-1">Bet Description</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="e.g., Chiefs score the next touchdown"
              className="w-full bg-surface border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-accent resize-none h-20"
            />
          </div>

          {/* Amount */}
          <div>
            <label className="text-sm text-white/60 block mb-1">
              Wager Amount (Balance: ${currentUser.balance.toFixed(0)})
            </label>
            <div className="flex items-center gap-2">
              <input
                type="range"
                min={settings.minBet}
                max={currentUser.balance}
                step={5}
                value={amount}
                onChange={e => setAmount(Number(e.target.value))}
                className="flex-1"
              />
              <div className="flex items-center bg-surface border border-white/10 rounded-lg px-3 py-1.5">
                <span className="text-white/40 mr-1">$</span>
                <input
                  type="number"
                  value={amount}
                  onChange={e => setAmount(Math.min(currentUser.balance, Math.max(settings.minBet, Number(e.target.value))))}
                  className="w-16 bg-transparent text-white font-bold focus:outline-none"
                />
              </div>
            </div>
            <div className="flex gap-1 mt-2">
              {[10, 25, 50, 100].filter(v => v <= currentUser.balance).map(v => (
                <button
                  key={v}
                  onClick={() => setAmount(v)}
                  className={`px-3 py-1 rounded text-xs font-bold transition-colors cursor-pointer ${
                    amount === v ? 'bg-accent text-white' : 'bg-white/10 hover:bg-white/20'
                  }`}
                >
                  ${v}
                </button>
              ))}
              <button
                onClick={() => setAmount(currentUser.balance)}
                className="px-3 py-1 rounded text-xs font-bold bg-danger/20 text-danger hover:bg-danger/30 cursor-pointer"
              >
                ALL IN
              </button>
            </div>
          </div>

          {/* Odds */}
          <div>
            <label className="text-sm text-white/60 block mb-1">Payout Multiplier</label>
            <div className="flex gap-1">
              {[1, 1.5, 2, 3, 5].map(o => (
                <button
                  key={o}
                  onClick={() => setOdds(o)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-bold cursor-pointer transition-colors ${
                    odds === o ? 'bg-gold text-black' : 'bg-white/10 hover:bg-white/20'
                  }`}
                >
                  {o}x
                </button>
              ))}
            </div>
            <div className="text-xs text-white/40 mt-1">
              Potential payout: <span className="text-success font-bold">${(amount * odds * 2).toFixed(0)}</span> (winner takes all)
            </div>
          </div>

          {/* Expiry */}
          <div>
            <label className="text-sm text-white/60 block mb-1">Expires</label>
            <div className="flex flex-wrap gap-1">
              {EXPIRY_OPTIONS.map((opt) => (
                <button
                  key={opt.label}
                  onClick={() => setExpiry(opt.value)}
                  className={`px-3 py-1 rounded text-xs font-bold cursor-pointer transition-colors ${
                    expiry === opt.value ? 'bg-accent text-white' : 'bg-white/10 hover:bg-white/20'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Submit */}
          <button
            onClick={handleSubmit}
            disabled={!canBet || !description.trim() || amount < settings.minBet}
            className="w-full bg-gradient-to-r from-accent to-[#ff6b6b] hover:from-[#ff6b6b] hover:to-accent disabled:opacity-30 disabled:cursor-not-allowed text-white font-bold py-3 rounded-xl text-lg transition-all cursor-pointer"
          >
            Post Bet — ${amount}
          </button>
        </div>
      </div>
    </div>
  );
}
