import { useGame } from '../store/GameContext';

export default function GameStats() {
  const { gameState } = useGame();
  const { homeStats, awayStats, homeTeam, awayTeam } = gameState;

  const StatBar = ({ label, away, home }) => {
    const total = away + home || 1;
    const awayPct = (away / total) * 100;
    return (
      <div className="mb-2">
        <div className="flex justify-between text-xs text-white/60 mb-0.5">
          <span>{away}</span>
          <span className="text-white/30">{label}</span>
          <span>{home}</span>
        </div>
        <div className="flex h-2 rounded-full overflow-hidden bg-white/10">
          <div className="rounded-l-full" style={{ width: `${awayPct}%`, backgroundColor: awayTeam.secondaryColor }} />
          <div className="rounded-r-full flex-1" style={{ backgroundColor: homeTeam.secondaryColor }} />
        </div>
      </div>
    );
  };

  return (
    <div className="bg-surface-card/50 border border-white/10 rounded-xl p-4">
      <h4 className="text-sm font-bold text-white/60 mb-3 flex items-center gap-2">
        📊 Game Stats
      </h4>
      <div className="flex justify-between text-xs font-bold mb-3">
        <span style={{ color: awayTeam.secondaryColor }}>{awayTeam.abbr}</span>
        <span style={{ color: homeTeam.secondaryColor }}>{homeTeam.abbr}</span>
      </div>
      <StatBar label="Total Yards" away={awayStats.totalYards} home={homeStats.totalYards} />
      <StatBar label="Passing" away={awayStats.passingYards} home={homeStats.passingYards} />
      <StatBar label="Rushing" away={awayStats.rushingYards} home={homeStats.rushingYards} />
      <StatBar label="First Downs" away={awayStats.firstDowns} home={homeStats.firstDowns} />
      <StatBar label="Turnovers" away={awayStats.turnovers} home={homeStats.turnovers} />
    </div>
  );
}
