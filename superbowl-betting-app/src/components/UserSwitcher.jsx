import { useState } from 'react';
import { useGame } from '../store/GameContext';

export default function UserSwitcher() {
  const { users, currentUser, dispatch, AVATARS } = useGame();
  const [showAddUser, setShowAddUser] = useState(false);
  const [newName, setNewName] = useState('');
  const [newAvatar, setNewAvatar] = useState(AVATARS[0]);
  const [newPin, setNewPin] = useState('');
  const [pinPrompt, setPinPrompt] = useState(null);
  const [pinInput, setPinInput] = useState('');

  const handleSwitch = (userId) => {
    const user = users.find(u => u.id === userId);
    if (user?.pin) {
      setPinPrompt(userId);
      setPinInput('');
    } else {
      dispatch({ type: 'SWITCH_USER', payload: userId });
    }
  };

  const verifyPin = () => {
    const user = users.find(u => u.id === pinPrompt);
    if (user && user.pin === pinInput) {
      dispatch({ type: 'SWITCH_USER', payload: pinPrompt });
      setPinPrompt(null);
      setPinInput('');
    } else {
      alert('Incorrect PIN');
    }
  };

  const addUser = () => {
    if (!newName.trim()) return;
    dispatch({ type: 'ADD_USER', payload: { name: newName.trim(), avatar: newAvatar, pin: newPin } });
    setNewName('');
    setNewPin('');
    setShowAddUser(false);
  };

  return (
    <div className="relative">
      <div className="flex items-center gap-2 flex-wrap">
        {/* Current user display */}
        {currentUser && (
          <div className="flex items-center gap-2 bg-surface-card/80 px-3 py-1.5 rounded-xl border border-white/10">
            <span className="text-xl">{currentUser.avatar}</span>
            <span className="font-bold text-sm">{currentUser.name}</span>
            <span className="text-accent font-bold text-sm">${currentUser.balance.toFixed(0)}</span>
          </div>
        )}

        {/* Quick switch buttons */}
        <div className="flex gap-1">
          {users.filter(u => u.id !== currentUser?.id).map(u => (
            <button
              key={u.id}
              onClick={() => handleSwitch(u.id)}
              className="flex items-center gap-1 bg-surface/80 hover:bg-surface-card px-2 py-1 rounded-lg text-xs transition-colors border border-white/5 cursor-pointer"
              title={`Switch to ${u.name}`}
            >
              <span>{u.avatar}</span>
              <span className="hidden md:inline">{u.name}</span>
            </button>
          ))}
        </div>

        {/* Add user button */}
        <button
          onClick={() => setShowAddUser(true)}
          className="bg-success/20 hover:bg-success/30 text-success px-3 py-1.5 rounded-lg text-sm font-bold transition-colors cursor-pointer"
        >
          + Add Player
        </button>
      </div>

      {/* Add user modal */}
      {showAddUser && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50" onClick={() => setShowAddUser(false)}>
          <div className="bg-surface-light border border-white/10 rounded-2xl p-6 w-full max-w-md mx-4" onClick={e => e.stopPropagation()}>
            <h3 className="text-xl font-bold mb-4">Add Player</h3>
            <div className="space-y-4">
              <div>
                <label className="text-sm text-white/60 block mb-1">Name</label>
                <input
                  type="text"
                  value={newName}
                  onChange={e => setNewName(e.target.value)}
                  placeholder="Enter player name"
                  className="w-full bg-surface border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-accent"
                  autoFocus
                  onKeyDown={e => e.key === 'Enter' && addUser()}
                />
              </div>
              <div>
                <label className="text-sm text-white/60 block mb-1">Avatar</label>
                <div className="grid grid-cols-10 gap-1">
                  {AVATARS.map(a => (
                    <button
                      key={a}
                      onClick={() => setNewAvatar(a)}
                      className={`text-xl p-1 rounded-lg cursor-pointer transition-all ${
                        newAvatar === a ? 'bg-accent/30 ring-2 ring-accent scale-110' : 'hover:bg-white/10'
                      }`}
                    >
                      {a}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="text-sm text-white/60 block mb-1">PIN (optional, for privacy)</label>
                <input
                  type="password"
                  value={newPin}
                  onChange={e => setNewPin(e.target.value)}
                  placeholder="4-digit PIN"
                  maxLength={4}
                  className="w-full bg-surface border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-accent"
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={addUser}
                  className="flex-1 bg-success hover:bg-success/80 text-white font-bold py-2 rounded-lg transition-colors cursor-pointer"
                >
                  Add Player
                </button>
                <button
                  onClick={() => setShowAddUser(false)}
                  className="flex-1 bg-white/10 hover:bg-white/20 text-white py-2 rounded-lg transition-colors cursor-pointer"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* PIN prompt modal */}
      {pinPrompt && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-surface-light border border-white/10 rounded-2xl p-6 w-full max-w-sm mx-4">
            <h3 className="text-xl font-bold mb-4">Enter PIN</h3>
            <input
              type="password"
              value={pinInput}
              onChange={e => setPinInput(e.target.value)}
              placeholder="Enter 4-digit PIN"
              maxLength={4}
              className="w-full bg-surface border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-accent mb-4"
              autoFocus
              onKeyDown={e => e.key === 'Enter' && verifyPin()}
            />
            <div className="flex gap-2">
              <button onClick={verifyPin} className="flex-1 bg-accent hover:bg-accent/80 text-white font-bold py-2 rounded-lg cursor-pointer">
                Unlock
              </button>
              <button onClick={() => setPinPrompt(null)} className="flex-1 bg-white/10 hover:bg-white/20 py-2 rounded-lg cursor-pointer">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
