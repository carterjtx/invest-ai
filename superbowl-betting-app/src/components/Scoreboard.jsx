import { useGame } from '../store/GameContext';

export default function Scoreboard() {
  const { gameState, resumeHalftime, currentUser } = useGame();
  const g = gameState;
  const isHost = currentUser?.isHost;

  return (
    <div className="bg-gradient-to-r from-[#002244] via-[#1a1a3e] to-[#004C54] rounded-2xl p-4 shadow-2xl border border-white/10">
      {/* Live indicator */}
      <div className="flex justify-center items-center gap-2 mb-3">
        {g.isLive && !g.isGameOver && (
          <span className="flex items-center gap-1.5 bg-red-600/80 px-3 py-0.5 rounded-full text-xs font-bold tracking-wider">
            <span className="w-2 h-2 bg-white rounded-full animate-pulse-live"></span>
            LIVE
          </span>
        )}
        {g.isGameOver && (
          <span className="bg-yellow-500/80 px-3 py-0.5 rounded-full text-xs font-bold text-black">FINAL</span>
        )}
        {g.isHalftime && (
          <span className="bg-orange-500/80 px-3 py-0.5 rounded-full text-xs font-bold text-black">HALFTIME</span>
        )}
        <span className="text-white/60 text-xs">SUPER BOWL LXI</span>
      </div>

      {/* Score */}
      <div className="flex items-center justify-center gap-4 md:gap-8">
        {/* Away team */}
        <div className="text-center flex-1">
          <div className="text-3xl mb-1">{g.awayTeam.logo}</div>
          <div className="text-lg font-bold" style={{ color: g.awayTeam.secondaryColor }}>{g.awayTeam.abbr}</div>
          <div className="text-xs text-white/50">{g.awayTeam.name}</div>
        </div>

        {/* Scores */}
        <div className="flex items-center gap-3 md:gap-6">
          <div className="text-5xl md:text-6xl font-black tabular-nums" style={{ color: g.awayTeam.secondaryColor }}>
            {g.awayScore}
          </div>
          <div className="text-center">
            <div className="text-2xl text-white/30 font-light">—</div>
            <div className="text-sm font-bold text-white/80">
              {g.isHalftime ? 'HALF' : g.isGameOver ? 'FINAL' : g.quarter <= 4 ? `Q${g.quarter}` : 'OT'}
            </div>
            {!g.isGameOver && !g.isHalftime && (
              <div className="text-xs text-white/60 tabular-nums">{g.timeRemaining}</div>
            )}
          </div>
          <div className="text-5xl md:text-6xl font-black tabular-nums" style={{ color: g.homeTeam.secondaryColor }}>
            {g.homeScore}
          </div>
        </div>

        {/* Home team */}
        <div className="text-center flex-1">
          <div className="text-3xl mb-1">{g.homeTeam.logo}</div>
          <div className="text-lg font-bold" style={{ color: g.homeTeam.secondaryColor }}>{g.homeTeam.abbr}</div>
          <div className="text-xs text-white/50">{g.homeTeam.name}</div>
        </div>
      </div>

      {/* Game info bar */}
      {!g.isGameOver && !g.isHalftime && (
        <div className="flex justify-center gap-4 mt-3 text-xs text-white/50">
          <span>
            <span className="text-white/30">POSS:</span>{' '}
            <span className="font-bold" style={{ color: g.possession === 'home' ? g.homeTeam.secondaryColor : g.awayTeam.secondaryColor }}>
              {g.possession === 'home' ? g.homeTeam.abbr : g.awayTeam.abbr}
            </span>
          </span>
          <span>{g.down > 0 && `${g.down}${['st','nd','rd','th'][Math.min(g.down-1,3)]} & ${g.yardsToGo}`}</span>
          <span>TO: {g.awayTeam.abbr} {g.awayTimeouts} | {g.homeTeam.abbr} {g.homeTimeouts}</span>
        </div>
      )}

      {/* Halftime resume button */}
      {g.isHalftime && isHost && (
        <div className="text-center mt-3">
          <button
            onClick={resumeHalftime}
            className="bg-orange-500 hover:bg-orange-600 text-black font-bold px-6 py-2 rounded-lg text-sm transition-colors cursor-pointer"
          >
            Resume 2nd Half
          </button>
        </div>
      )}

      {/* Play-by-play ticker */}
      <div className="mt-3 border-t border-white/10 pt-2 max-h-32 overflow-y-auto">
        {g.plays.slice(0, 8).map((play) => (
          <div
            key={play.id}
            className={`text-xs py-1 px-2 rounded mb-0.5 ${
              play.isHighlight ? 'bg-yellow-500/10 text-yellow-300 font-semibold' : 'text-white/60'
            }`}
          >
            <span className="text-white/30 mr-2">Q{play.quarter} {play.time}</span>
            {play.text}
          </div>
        ))}
        {g.plays.length === 0 && (
          <div className="text-xs text-white/30 text-center py-2">Waiting for game to start...</div>
        )}
      </div>
    </div>
  );
}
