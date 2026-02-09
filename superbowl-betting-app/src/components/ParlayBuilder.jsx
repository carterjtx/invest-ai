import { useState } from 'react';
import { useGame } from '../store/GameContext';
import { playBetSound } from '../utils/sounds';

export default function ParlayBuilder({ onClose }) {
  const { currentUser, dispatch, settings } = useGame();
  const [legs, setLegs] = useState(['', '']);
  const [totalWager, setTotalWager] = useState(20);

  if (!currentUser) return null;

  const validLegs = legs.filter(l => l.trim());
  const multiplier = validLegs.length >= 2 ? (Math.pow(2, validLegs.length) - 0.5) : 0;
  const potentialPayout = totalWager * multiplier;

  const addLeg = () => {
    if (legs.length < 5) setLegs([...legs, '']);
  };

  const removeLeg = (idx) => {
    if (legs.length > 2) setLegs(legs.filter((_, i) => i !== idx));
  };

  const updateLeg = (idx, value) => {
    setLegs(legs.map((l, i) => i === idx ? value : l));
  };

  const handleSubmit = () => {
    if (validLegs.length < 2 || totalWager < settings.minBet || totalWager > currentUser.balance) return;
    dispatch({
      type: 'CREATE_PARLAY',
      payload: { userId: currentUser.id, betDescriptions: validLegs, totalWager }
    });
    if (settings.soundEnabled) playBetSound();
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-surface-light border border-white/10 rounded-2xl p-6 w-full max-w-lg" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold flex items-center gap-2">
            <span className="text-2xl">🎲</span> Build a Parlay
          </h3>
          <button onClick={onClose} className="text-white/40 hover:text-white text-2xl cursor-pointer">&times;</button>
        </div>

        <div className="bg-danger/10 border border-danger/30 rounded-lg p-2 mb-4 text-xs text-danger flex items-center gap-2">
          <span className="text-lg">⚠️</span>
          HIGH RISK — All legs must win or you lose everything!
        </div>

        {/* Legs */}
        <div className="space-y-2 mb-4">
          {legs.map((leg, idx) => (
            <div key={idx} className="flex items-center gap-2">
              <span className="text-xs text-white/30 w-6">#{idx + 1}</span>
              <input
                type="text"
                value={leg}
                onChange={e => updateLeg(idx, e.target.value)}
                placeholder={`Bet leg ${idx + 1}...`}
                className="flex-1 bg-surface border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-accent"
              />
              {legs.length > 2 && (
                <button onClick={() => removeLeg(idx)} className="text-danger/60 hover:text-danger cursor-pointer text-lg">&times;</button>
              )}
            </div>
          ))}
          {legs.length < 5 && (
            <button
              onClick={addLeg}
              className="w-full border border-dashed border-white/20 rounded-lg py-2 text-sm text-white/40 hover:text-white/60 hover:border-white/40 cursor-pointer transition-colors"
            >
              + Add Leg ({legs.length}/5)
            </button>
          )}
        </div>

        {/* Wager amount */}
        <div className="mb-4">
          <label className="text-sm text-white/60 block mb-1">Wager (Balance: ${currentUser.balance.toFixed(0)})</label>
          <div className="flex items-center gap-2">
            <input
              type="range"
              min={settings.minBet}
              max={currentUser.balance}
              step={5}
              value={totalWager}
              onChange={e => setTotalWager(Number(e.target.value))}
              className="flex-1"
            />
            <span className="font-bold text-lg text-accent w-16 text-right">${totalWager}</span>
          </div>
        </div>

        {/* Payout info */}
        {validLegs.length >= 2 && (
          <div className="bg-surface rounded-lg p-3 mb-4">
            <div className="flex justify-between text-sm">
              <span className="text-white/60">Legs</span>
              <span className="font-bold">{validLegs.length}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-white/60">Multiplier</span>
              <span className="font-bold text-gold">{multiplier.toFixed(1)}x</span>
            </div>
            <div className="flex justify-between text-sm border-t border-white/10 pt-2 mt-2">
              <span className="text-white/60">Potential Payout</span>
              <span className="font-black text-success text-lg">${potentialPayout.toFixed(0)}</span>
            </div>
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={validLegs.length < 2 || totalWager < settings.minBet || totalWager > currentUser.balance}
          className="w-full bg-gradient-to-r from-gold to-[#FFA500] hover:from-[#FFA500] hover:to-gold disabled:opacity-30 disabled:cursor-not-allowed text-black font-bold py-3 rounded-xl text-lg transition-all cursor-pointer"
        >
          Place Parlay — ${totalWager} for ${potentialPayout.toFixed(0)}
        </button>
      </div>
    </div>
  );
}
