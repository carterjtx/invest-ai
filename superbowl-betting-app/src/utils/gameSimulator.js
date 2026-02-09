// Simulates a live Super Bowl game without any external API
// Generates realistic play-by-play data that advances over real time

const TEAMS = {
  home: { name: 'Chiefs', abbr: 'KC', color: '#E31837', secondaryColor: '#FFB81C', logo: '🏈' },
  away: { name: 'Eagles', abbr: 'PHI', color: '#004C54', secondaryColor: '#A5ACAF', logo: '🦅' }
};

const PLAY_TYPES = [
  { type: 'run', weight: 30, desc: (team, player) => `${player} rushes for {yards} yards` },
  { type: 'pass_complete', weight: 30, desc: (team, player) => `${player} complete pass for {yards} yards` },
  { type: 'pass_incomplete', weight: 12, desc: (team, player) => `${player} pass incomplete` },
  { type: 'sack', weight: 5, desc: (team, player) => `${player} sacked for a loss of {yards} yards` },
  { type: 'penalty', weight: 8, desc: (team, player) => `Penalty on ${team}: {penalty}, {yards} yards` },
  { type: 'punt', weight: 8, desc: () => `Punt` },
  { type: 'field_goal_attempt', weight: 4, desc: (team, player) => `${player} attempts a {yards}-yard field goal` },
  { type: 'touchdown', weight: 3, desc: (team, player) => `TOUCHDOWN ${team}! ${player} scores!` },
];

const KC_PLAYERS = ['Mahomes', 'Kelce', 'Worthy', 'Edwards-Helaire', 'Rice', 'Pacheco', 'Butker'];
const PHI_PLAYERS = ['Hurts', 'Brown', 'Smith', 'Barkley', 'Goedert', 'Elliott', 'Gainwell'];
const PENALTIES = ['Holding', 'False Start', 'Pass Interference', 'Offsides', 'Illegal Formation', 'Delay of Game'];

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function pickWeighted(items) {
  const totalWeight = items.reduce((sum, item) => sum + item.weight, 0);
  let rand = Math.random() * totalWeight;
  for (const item of items) {
    rand -= item.weight;
    if (rand <= 0) return item;
  }
  return items[items.length - 1];
}

export function createInitialGameState() {
  return {
    homeTeam: TEAMS.home,
    awayTeam: TEAMS.away,
    homeScore: 0,
    awayScore: 0,
    quarter: 1,
    timeRemaining: '15:00',
    timeSeconds: 900,
    possession: Math.random() > 0.5 ? 'home' : 'away',
    down: 1,
    yardsToGo: 10,
    ballPosition: 25,
    homeTimeouts: 3,
    awayTimeouts: 3,
    plays: [],
    isLive: true,
    isHalftime: false,
    isGameOver: false,
    lastUpdated: new Date().toISOString(),
    gameStartTime: Date.now(),
    homeStats: { totalYards: 0, passingYards: 0, rushingYards: 0, turnovers: 0, firstDowns: 0 },
    awayStats: { totalYards: 0, passingYards: 0, rushingYards: 0, turnovers: 0, firstDowns: 0 },
  };
}

export function simulateTick(state) {
  if (state.isGameOver || state.isHalftime) return { ...state };

  const newState = JSON.parse(JSON.stringify(state));

  // Advance clock
  const clockDrain = randomInt(15, 45);
  newState.timeSeconds = Math.max(0, newState.timeSeconds - clockDrain);
  const mins = Math.floor(newState.timeSeconds / 60);
  const secs = newState.timeSeconds % 60;
  newState.timeRemaining = `${mins}:${secs.toString().padStart(2, '0')}`;

  // Check quarter end
  if (newState.timeSeconds <= 0) {
    if (newState.quarter === 2) {
      newState.isHalftime = true;
      newState.quarter = 2;
      newState.timeRemaining = 'HALF';
      newState.plays.unshift({
        id: Date.now(),
        text: '⏱️ HALFTIME',
        time: 'HALF',
        quarter: 2,
        isHighlight: true
      });
      newState.lastUpdated = new Date().toISOString();
      return newState;
    } else if (newState.quarter === 4) {
      if (newState.homeScore === newState.awayScore) {
        // Overtime
        newState.quarter = 5;
        newState.timeSeconds = 600;
        newState.timeRemaining = '10:00';
      } else {
        newState.isGameOver = true;
        newState.isLive = false;
        newState.timeRemaining = 'FINAL';
        const winner = newState.homeScore > newState.awayScore ? newState.homeTeam.name : newState.awayTeam.name;
        newState.plays.unshift({
          id: Date.now(),
          text: `🏆 GAME OVER! ${winner} win!`,
          time: 'FINAL',
          quarter: 4,
          isHighlight: true
        });
        newState.lastUpdated = new Date().toISOString();
        return newState;
      }
    } else {
      newState.quarter += 1;
      newState.timeSeconds = 900;
      newState.timeRemaining = '15:00';
      newState.plays.unshift({
        id: Date.now(),
        text: `📢 Start of Quarter ${newState.quarter}`,
        time: '15:00',
        quarter: newState.quarter,
        isHighlight: true
      });
    }
  }

  // Generate play
  const possTeam = newState.possession === 'home' ? newState.homeTeam : newState.awayTeam;
  const players = newState.possession === 'home' ? KC_PLAYERS : PHI_PLAYERS;
  const stats = newState.possession === 'home' ? newState.homeStats : newState.awayStats;
  const player = players[randomInt(0, players.length - 1)];
  const play = pickWeighted(PLAY_TYPES);

  let playText = '';
  let yards = 0;

  switch (play.type) {
    case 'run':
      yards = randomInt(-2, 15);
      playText = `${player} rushes for ${yards} yards`;
      stats.rushingYards += Math.max(0, yards);
      stats.totalYards += Math.max(0, yards);
      newState.ballPosition += yards;
      newState.yardsToGo -= yards;
      break;
    case 'pass_complete':
      yards = randomInt(3, 35);
      playText = `${player} complete pass for ${yards} yards`;
      stats.passingYards += yards;
      stats.totalYards += yards;
      newState.ballPosition += yards;
      newState.yardsToGo -= yards;
      break;
    case 'pass_incomplete':
      playText = `${player} pass incomplete`;
      break;
    case 'sack':
      yards = randomInt(3, 10);
      playText = `${player} sacked for a loss of ${yards} yards`;
      newState.ballPosition -= yards;
      newState.yardsToGo += yards;
      break;
    case 'penalty':
      yards = randomInt(5, 15);
      const penalty = PENALTIES[randomInt(0, PENALTIES.length - 1)];
      playText = `⚠️ Penalty on ${possTeam.name}: ${penalty}, ${yards} yards`;
      break;
    case 'punt':
      playText = `${possTeam.name} punt`;
      newState.possession = newState.possession === 'home' ? 'away' : 'home';
      newState.ballPosition = randomInt(20, 35);
      newState.down = 1;
      newState.yardsToGo = 10;
      break;
    case 'field_goal_attempt': {
      const fgDist = Math.max(20, 100 - newState.ballPosition + 17);
      const made = Math.random() > (fgDist > 50 ? 0.6 : 0.2);
      if (made) {
        playText = `✅ ${player} ${fgDist}-yard FIELD GOAL is GOOD!`;
        if (newState.possession === 'home') newState.homeScore += 3;
        else newState.awayScore += 3;
      } else {
        playText = `❌ ${player} ${fgDist}-yard field goal attempt NO GOOD`;
      }
      newState.possession = newState.possession === 'home' ? 'away' : 'home';
      newState.ballPosition = randomInt(20, 30);
      newState.down = 1;
      newState.yardsToGo = 10;
      break;
    }
    case 'touchdown': {
      const tdType = Math.random() > 0.5 ? 'pass' : 'rush';
      yards = randomInt(1, 65);
      playText = `🏈 TOUCHDOWN ${possTeam.name}! ${player} ${tdType === 'pass' ? 'receiving' : 'rushing'} TD for ${yards} yards!`;
      if (newState.possession === 'home') newState.homeScore += 7; // Assume PAT good
      else newState.awayScore += 7;
      stats.totalYards += yards;
      if (tdType === 'pass') stats.passingYards += yards;
      else stats.rushingYards += yards;

      // Kickoff
      newState.possession = newState.possession === 'home' ? 'away' : 'home';
      newState.ballPosition = randomInt(20, 30);
      newState.down = 1;
      newState.yardsToGo = 10;
      break;
    }
  }

  // Handle downs
  if (!['punt', 'field_goal_attempt', 'touchdown'].includes(play.type)) {
    if (newState.yardsToGo <= 0) {
      newState.down = 1;
      newState.yardsToGo = 10;
      stats.firstDowns += 1;
      if (newState.ballPosition >= 100) {
        // Crossed goal line
        playText += ' → TOUCHDOWN!';
        if (newState.possession === 'home') newState.homeScore += 7;
        else newState.awayScore += 7;
        newState.possession = newState.possession === 'home' ? 'away' : 'home';
        newState.ballPosition = randomInt(20, 30);
      }
    } else {
      newState.down += 1;
      if (newState.down > 4) {
        // Turnover on downs
        playText += ' → Turnover on downs!';
        newState.possession = newState.possession === 'home' ? 'away' : 'home';
        newState.down = 1;
        newState.yardsToGo = 10;
        stats.turnovers += 1;
      }
    }
  }

  // Clamp ball position
  newState.ballPosition = Math.max(1, Math.min(99, newState.ballPosition));

  if (playText) {
    newState.plays.unshift({
      id: Date.now() + Math.random(),
      text: playText,
      time: newState.timeRemaining,
      quarter: newState.quarter,
      team: possTeam.abbr,
      isHighlight: ['touchdown', 'field_goal_attempt'].includes(play.type)
    });
  }

  // Keep only last 50 plays
  if (newState.plays.length > 50) {
    newState.plays = newState.plays.slice(0, 50);
  }

  newState.lastUpdated = new Date().toISOString();
  return newState;
}

export function resumeFromHalftime(state) {
  return {
    ...state,
    isHalftime: false,
    quarter: 3,
    timeSeconds: 900,
    timeRemaining: '15:00',
    possession: state.possession === 'home' ? 'away' : 'home',
    homeTimeouts: 3,
    awayTimeouts: 3,
    plays: [{
      id: Date.now(),
      text: '📢 Start of the 2nd Half!',
      time: '15:00',
      quarter: 3,
      isHighlight: true
    }, ...state.plays]
  };
}
