import { useState } from 'react';
import { GameProvider, useGame } from './store/GameContext';
import Scoreboard from './components/Scoreboard';
import UserSwitcher from './components/UserSwitcher';
import BetFeed from './components/BetFeed';
import CreateBet from './components/CreateBet';
import ParlayBuilder from './components/ParlayBuilder';
import ParlayList from './components/ParlayList';
import Leaderboard from './components/Leaderboard';
import UserProfile from './components/UserProfile';
import TransactionHistory from './components/TransactionHistory';
import NotificationCenter from './components/NotificationCenter';
import HostControls from './components/HostControls';
import BankruptcyModal from './components/BankruptcyModal';
import GameStats from './components/GameStats';

function AppContent() {
  const { currentUser, users, settings } = useGame();
  const [showCreateBet, setShowCreateBet] = useState(false);
  const [showParlay, setShowParlay] = useState(false);
  const [showProfile, setShowProfile] = useState(null);
  const [showHistory, setShowHistory] = useState(null);
  const [activeTab, setActiveTab] = useState('feed');

  return (
    <div className="min-h-screen max-w-7xl mx-auto px-3 md:px-6 py-4">
      {/* Header */}
      <header className="mb-4">
        <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
          <div className="flex items-center gap-3">
            <h1 className="text-xl md:text-2xl font-black tracking-tight">
              <span className="text-accent">SUPER</span>
              <span className="text-gold">BOWL</span>
              <span className="text-white/60 text-sm ml-2">BET</span>
            </h1>
            {settings.isPaused && (
              <span className="bg-warning/20 text-warning text-xs px-2 py-0.5 rounded-full font-bold animate-pulse">
                PAUSED
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <NotificationCenter />
            <HostControls />
          </div>
        </div>
        <UserSwitcher />
      </header>

      {/* Scoreboard */}
      <div className="mb-4">
        <Scoreboard />
      </div>

      {/* Main layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left column - Main content */}
        <div className="lg:col-span-2">
          {/* Action buttons */}
          {currentUser && (
            <div className="flex gap-2 mb-4 flex-wrap">
              <button
                onClick={() => setShowCreateBet(true)}
                disabled={settings.isPaused || currentUser.balance < settings.minBet}
                className="bg-gradient-to-r from-accent to-[#ff6b6b] hover:from-[#ff6b6b] hover:to-accent disabled:opacity-30 disabled:cursor-not-allowed text-white font-bold px-6 py-2.5 rounded-xl text-sm transition-all cursor-pointer shadow-lg shadow-accent/20"
              >
                + Create Bet
              </button>
              <button
                onClick={() => setShowParlay(true)}
                disabled={settings.isPaused || currentUser.balance < settings.minBet}
                className="bg-gradient-to-r from-gold/80 to-[#FFA500] hover:from-[#FFA500] hover:to-gold disabled:opacity-30 disabled:cursor-not-allowed text-black font-bold px-6 py-2.5 rounded-xl text-sm transition-all cursor-pointer"
              >
                🎲 Build Parlay
              </button>
              <button
                onClick={() => setShowProfile(currentUser.id)}
                className="bg-white/10 hover:bg-white/20 px-4 py-2.5 rounded-xl text-sm cursor-pointer transition-colors"
              >
                👤 My Profile
              </button>
              <button
                onClick={() => setShowHistory(currentUser.id)}
                className="bg-white/10 hover:bg-white/20 px-4 py-2.5 rounded-xl text-sm cursor-pointer transition-colors"
              >
                📋 History
              </button>
            </div>
          )}

          {/* Tabs */}
          <div className="flex gap-1 mb-3 border-b border-white/10 pb-2">
            {[
              { key: 'feed', label: 'Bet Feed', icon: '📢' },
              { key: 'parlays', label: 'Parlays', icon: '🎲' },
              { key: 'stats', label: 'Game Stats', icon: '📊' },
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`px-4 py-2 rounded-lg text-sm font-bold cursor-pointer transition-colors ${
                  activeTab === tab.key
                    ? 'bg-accent/20 text-accent border border-accent/30'
                    : 'text-white/40 hover:text-white/60 hover:bg-white/5'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          {activeTab === 'feed' && <BetFeed />}
          {activeTab === 'parlays' && <ParlayList />}
          {activeTab === 'stats' && <GameStats />}
        </div>

        {/* Right column - Sidebar */}
        <div className="space-y-4">
          <Leaderboard />

          {/* Quick user profiles */}
          <div className="bg-surface-card/50 border border-white/10 rounded-xl p-4">
            <h3 className="text-sm font-bold text-white/60 mb-3">👥 Players</h3>
            <div className="space-y-2">
              {users.map(u => (
                <button
                  key={u.id}
                  onClick={() => setShowProfile(u.id)}
                  className="w-full flex items-center gap-2 bg-surface/50 hover:bg-white/10 rounded-lg p-2 cursor-pointer transition-colors text-left"
                >
                  <span className="text-xl">{u.avatar}</span>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-bold truncate">{u.name}</div>
                    <div className="text-xs text-white/30">
                      {u.wins}W-{u.losses}L
                      {u.isHost && ' · Host'}
                    </div>
                  </div>
                  <span className="text-sm font-bold text-accent">${u.balance.toFixed(0)}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Welcome screen if no users */}
      {users.length === 0 && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-30">
          <div className="text-center max-w-md mx-4">
            <div className="text-6xl mb-4">🏈</div>
            <h2 className="text-3xl font-black mb-2">
              <span className="text-accent">SUPER</span>
              <span className="text-gold">BOWL</span>
              <span className="text-white"> BET</span>
            </h2>
            <p className="text-white/50 mb-6">
              Add players to get started! Everyone starts with ${settings.startingBalance} in fake money.
            </p>
            <p className="text-white/30 text-sm">
              Click "+ Add Player" above to begin
            </p>
          </div>
        </div>
      )}

      {/* Modals */}
      {showCreateBet && <CreateBet onClose={() => setShowCreateBet(false)} />}
      {showParlay && <ParlayBuilder onClose={() => setShowParlay(false)} />}
      {showProfile && <UserProfile userId={showProfile} onClose={() => setShowProfile(null)} />}
      {showHistory && <TransactionHistory userId={showHistory} onClose={() => setShowHistory(null)} />}
      <BankruptcyModal />
    </div>
  );
}

export default function App() {
  return (
    <GameProvider>
      <AppContent />
    </GameProvider>
  );
}
