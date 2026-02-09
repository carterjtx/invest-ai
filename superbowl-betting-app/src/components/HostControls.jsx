import { useState } from 'react';
import { useGame } from '../store/GameContext';

export default function HostControls() {
  const { currentUser, users, settings, dispatch, saveGame, gameState } = useGame();
  const [showPanel, setShowPanel] = useState(false);
  const [confirmReset, setConfirmReset] = useState(false);
  const [manualHome, setManualHome] = useState(gameState.homeScore);
  const [manualAway, setManualAway] = useState(gameState.awayScore);
  const [settingsPanel, setSettingsPanel] = useState(false);
  const [localSettings, setLocalSettings] = useState(settings);

  if (!currentUser?.isHost) return null;

  const handleReset = () => {
    if (confirmReset) {
      dispatch({ type: 'RESET_GAME' });
      setConfirmReset(false);
      setShowPanel(false);
    } else {
      setConfirmReset(true);
    }
  };

  const handleManualScore = () => {
    dispatch({ type: 'MANUAL_SCORE_UPDATE', payload: { homeScore: manualHome, awayScore: manualAway } });
  };

  const applySettings = () => {
    dispatch({ type: 'UPDATE_SETTINGS', payload: localSettings });
    setSettingsPanel(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowPanel(!showPanel)}
        className="bg-accent/20 hover:bg-accent/30 text-accent px-3 py-1.5 rounded-xl border border-accent/30 cursor-pointer transition-colors text-sm font-bold"
      >
        🎮 Host
      </button>

      {showPanel && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => { setShowPanel(false); setConfirmReset(false); }} />
          <div className="absolute right-0 top-full mt-2 w-72 bg-surface-light border border-white/10 rounded-xl shadow-2xl z-50 p-4">
            <h4 className="font-bold text-sm mb-3">Host Controls</h4>

            <div className="space-y-2">
              {/* Pause */}
              <button
                onClick={() => dispatch({ type: 'TOGGLE_PAUSE' })}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm cursor-pointer transition-colors ${
                  settings.isPaused ? 'bg-success/20 text-success' : 'bg-warning/20 text-warning'
                }`}
              >
                {settings.isPaused ? '▶️ Resume Betting' : '⏸️ Pause Betting'}
              </button>

              {/* Save */}
              <button
                onClick={() => { saveGame(); alert('Game saved!'); }}
                className="w-full text-left px-3 py-2 rounded-lg text-sm bg-white/10 hover:bg-white/20 cursor-pointer"
              >
                💾 Save Game
              </button>

              {/* Settings */}
              <button
                onClick={() => setSettingsPanel(!settingsPanel)}
                className="w-full text-left px-3 py-2 rounded-lg text-sm bg-white/10 hover:bg-white/20 cursor-pointer"
              >
                ⚙️ Game Settings
              </button>

              {settingsPanel && (
                <div className="bg-surface rounded-lg p-3 space-y-2">
                  <div>
                    <label className="text-xs text-white/40">Starting Balance ($)</label>
                    <input
                      type="number"
                      value={localSettings.startingBalance}
                      onChange={e => setLocalSettings({ ...localSettings, startingBalance: Number(e.target.value) })}
                      className="w-full bg-surface-light border border-white/10 rounded px-2 py-1 text-sm text-white"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-white/40">Min Bet ($)</label>
                    <input
                      type="number"
                      value={localSettings.minBet}
                      onChange={e => setLocalSettings({ ...localSettings, minBet: Number(e.target.value) })}
                      className="w-full bg-surface-light border border-white/10 rounded px-2 py-1 text-sm text-white"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-white/40">Bailout Amount ($)</label>
                    <input
                      type="number"
                      value={localSettings.bailoutAmount}
                      onChange={e => setLocalSettings({ ...localSettings, bailoutAmount: Number(e.target.value) })}
                      className="w-full bg-surface-light border border-white/10 rounded px-2 py-1 text-sm text-white"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-white/40">Game Speed (ms per play)</label>
                    <input
                      type="number"
                      value={localSettings.gameSpeed}
                      onChange={e => setLocalSettings({ ...localSettings, gameSpeed: Number(e.target.value) })}
                      min={2000}
                      max={30000}
                      step={1000}
                      className="w-full bg-surface-light border border-white/10 rounded px-2 py-1 text-sm text-white"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={localSettings.soundEnabled}
                      onChange={e => setLocalSettings({ ...localSettings, soundEnabled: e.target.checked })}
                      className="rounded"
                    />
                    <label className="text-xs text-white/60">Sound Effects</label>
                  </div>
                  <button
                    onClick={applySettings}
                    className="w-full bg-accent/80 hover:bg-accent text-white py-1.5 rounded text-xs font-bold cursor-pointer"
                  >
                    Apply Settings
                  </button>
                </div>
              )}

              {/* Manual score */}
              <div className="border-t border-white/10 pt-2">
                <div className="text-xs text-white/40 mb-1">Manual Score Override</div>
                <div className="flex items-center gap-2">
                  <div className="text-center">
                    <div className="text-xs text-white/30">{gameState.awayTeam.abbr}</div>
                    <input
                      type="number"
                      value={manualAway}
                      onChange={e => setManualAway(Number(e.target.value))}
                      className="w-14 bg-surface border border-white/10 rounded px-1 py-0.5 text-center text-sm text-white"
                    />
                  </div>
                  <span className="text-white/30">-</span>
                  <div className="text-center">
                    <div className="text-xs text-white/30">{gameState.homeTeam.abbr}</div>
                    <input
                      type="number"
                      value={manualHome}
                      onChange={e => setManualHome(Number(e.target.value))}
                      className="w-14 bg-surface border border-white/10 rounded px-1 py-0.5 text-center text-sm text-white"
                    />
                  </div>
                  <button
                    onClick={handleManualScore}
                    className="bg-white/10 hover:bg-white/20 px-2 py-1 rounded text-xs cursor-pointer"
                  >
                    Set
                  </button>
                </div>
              </div>

              {/* Grant bailout */}
              <div className="border-t border-white/10 pt-2">
                <div className="text-xs text-white/40 mb-1">Grant Bailout</div>
                <div className="space-y-1">
                  {users.filter(u => u.balance === 0 || u.balance < settings.minBet).map(u => (
                    <button
                      key={u.id}
                      onClick={() => dispatch({ type: 'ADMIN_BAILOUT', payload: u.id })}
                      className="w-full flex items-center gap-2 bg-surface hover:bg-success/10 rounded p-1.5 text-xs cursor-pointer"
                    >
                      <span>{u.avatar}</span>
                      <span>{u.name}</span>
                      <span className="text-white/30">${u.balance}</span>
                    </button>
                  ))}
                  {users.filter(u => u.balance === 0 || u.balance < settings.minBet).length === 0 && (
                    <div className="text-xs text-white/30">No players need bailout</div>
                  )}
                </div>
              </div>

              {/* Remove user */}
              <div className="border-t border-white/10 pt-2">
                <div className="text-xs text-white/40 mb-1">Remove Player</div>
                <div className="space-y-1">
                  {users.filter(u => !u.isHost).map(u => (
                    <button
                      key={u.id}
                      onClick={() => { if (confirm(`Remove ${u.name}?`)) dispatch({ type: 'REMOVE_USER', payload: u.id }); }}
                      className="w-full flex items-center gap-2 bg-surface hover:bg-danger/10 rounded p-1.5 text-xs cursor-pointer"
                    >
                      <span>{u.avatar}</span>
                      <span>{u.name}</span>
                      <span className="text-danger/60">✕</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Reset */}
              <button
                onClick={handleReset}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm cursor-pointer transition-colors ${
                  confirmReset ? 'bg-danger text-white font-bold' : 'bg-danger/20 text-danger'
                }`}
              >
                {confirmReset ? '⚠️ CONFIRM RESET? Click again' : '🔄 Reset All (New Game)'}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
