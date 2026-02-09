// Simple sound effects using Web Audio API - no external files needed
const audioCtx = typeof window !== 'undefined' ? new (window.AudioContext || window.webkitAudioContext)() : null;

function playTone(frequency, duration, type = 'sine', volume = 0.3) {
  if (!audioCtx) return;
  try {
    audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = type;
    osc.frequency.value = frequency;
    gain.gain.value = volume;
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + duration);
  } catch {}
}

export function playWinSound() {
  playTone(523, 0.15, 'sine');
  setTimeout(() => playTone(659, 0.15, 'sine'), 150);
  setTimeout(() => playTone(784, 0.3, 'sine'), 300);
}

export function playLoseSound() {
  playTone(400, 0.2, 'sawtooth', 0.15);
  setTimeout(() => playTone(300, 0.3, 'sawtooth', 0.15), 200);
}

export function playBetSound() {
  playTone(880, 0.1, 'sine', 0.2);
}

export function playNotificationSound() {
  playTone(660, 0.1, 'sine', 0.15);
  setTimeout(() => playTone(880, 0.1, 'sine', 0.15), 100);
}

export function playBankruptSound() {
  for (let i = 0; i < 5; i++) {
    setTimeout(() => playTone(200 - i * 30, 0.2, 'square', 0.15), i * 200);
  }
}

export function playTouchdownSound() {
  const notes = [523, 659, 784, 1047];
  notes.forEach((n, i) => setTimeout(() => playTone(n, 0.2, 'sine', 0.2), i * 100));
}
