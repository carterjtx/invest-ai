import { useEffect, useState } from 'react';
import { useGame } from '../store/GameContext';
import { playBankruptSound } from '../utils/sounds';

export default function BankruptcyModal() {
  const { currentUser, dispatch, settings } = useGame();
  const [show, setShow] = useState(false);
  const [animating, setAnimating] = useState(false);

  useEffect(() => {
    if (currentUser && currentUser.balance <= 0 && !show) {
      setShow(true);
      setAnimating(true);
      if (settings.soundEnabled) playBankruptSound();
      setTimeout(() => setAnimating(false), 2000);
    } else if (currentUser && currentUser.balance > 0) {
      setShow(false);
    }
  }, [currentUser?.balance]);

  if (!show || !currentUser) return null;

  const canBailout = !currentUser.bailoutUsed;

  const handleBailout = () => {
    dispatch({ type: 'BAILOUT', payload: currentUser.id });
    setShow(false);
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
      <div className={`bg-surface-light border-2 border-danger rounded-2xl p-8 max-w-sm mx-4 text-center ${animating ? 'bankrupt-flash animate-shake' : ''}`}>
        <div className="text-6xl mb-4">💸</div>
        <h2 className="text-3xl font-black text-danger mb-2">BANKRUPT!</h2>
        <p className="text-white/60 mb-6">
          {currentUser.name}, you've lost all your money!
        </p>

        {canBailout ? (
          <>
            <p className="text-sm text-white/40 mb-4">
              You have ONE bailout available. Take ${settings.bailoutAmount} to get back in the game?
            </p>
            <div className="flex gap-2">
              <button
                onClick={handleBailout}
                className="flex-1 bg-success hover:bg-success/80 text-white font-bold py-3 rounded-xl text-lg transition-colors cursor-pointer animate-glow"
              >
                💰 Take ${settings.bailoutAmount} Bailout
              </button>
            </div>
            <button
              onClick={() => setShow(false)}
              className="w-full mt-2 text-white/30 text-xs hover:text-white/50 cursor-pointer"
            >
              No thanks, I'll spectate
            </button>
          </>
        ) : (
          <>
            <p className="text-sm text-danger/60 mb-4">
              You've already used your bailout. You're out of the game!
              <br />Ask the host for a manual bailout.
            </p>
            <button
              onClick={() => setShow(false)}
              className="w-full bg-white/10 hover:bg-white/20 text-white py-2 rounded-lg cursor-pointer"
            >
              Spectate Mode
            </button>
          </>
        )}
      </div>
    </div>
  );
}
