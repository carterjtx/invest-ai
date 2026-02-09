import { useState, useEffect } from 'react';
import { useGame } from '../store/GameContext';
import { playNotificationSound } from '../utils/sounds';

export default function NotificationCenter() {
  const { notifications, currentUser, dispatch, settings } = useGame();
  const [showPanel, setShowPanel] = useState(false);
  const [lastCount, setLastCount] = useState(0);

  const myNotifications = notifications.filter(n => n.userId === currentUser?.id);
  const unreadCount = myNotifications.filter(n => !n.read).length;

  // Play sound on new notification
  useEffect(() => {
    if (unreadCount > lastCount && settings.soundEnabled) {
      playNotificationSound();
    }
    setLastCount(unreadCount);
  }, [unreadCount]);

  const clearAll = () => {
    if (currentUser) {
      dispatch({ type: 'CLEAR_NOTIFICATIONS', payload: currentUser.id });
    }
  };

  const typeIcons = {
    win: '🎉',
    loss: '😢',
    accepted: '🤝',
    bailout: '💰',
    expired: '⏰',
  };

  const typeColors = {
    win: 'border-l-success',
    loss: 'border-l-danger',
    accepted: 'border-l-accent',
    bailout: 'border-l-gold',
    expired: 'border-l-white/30',
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowPanel(!showPanel)}
        className="relative bg-surface-card/80 hover:bg-surface-card px-3 py-1.5 rounded-xl border border-white/10 cursor-pointer transition-colors"
      >
        🔔
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-accent text-white text-xs w-5 h-5 rounded-full flex items-center justify-center font-bold animate-bounce-in">
            {unreadCount}
          </span>
        )}
      </button>

      {showPanel && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setShowPanel(false)} />
          <div className="absolute right-0 top-full mt-2 w-80 bg-surface-light border border-white/10 rounded-xl shadow-2xl z-50 max-h-96 flex flex-col">
            <div className="flex items-center justify-between p-3 border-b border-white/10">
              <span className="font-bold text-sm">Notifications</span>
              {unreadCount > 0 && (
                <button onClick={clearAll} className="text-xs text-accent hover:underline cursor-pointer">
                  Mark all read
                </button>
              )}
            </div>
            <div className="flex-1 overflow-y-auto">
              {myNotifications.length === 0 ? (
                <div className="text-center py-8 text-white/30 text-sm">No notifications</div>
              ) : (
                myNotifications.slice(0, 20).map(n => (
                  <div
                    key={n.id}
                    onClick={() => dispatch({ type: 'MARK_NOTIFICATION_READ', payload: n.id })}
                    className={`p-3 border-b border-white/5 border-l-4 cursor-pointer hover:bg-white/5 transition-colors ${
                      typeColors[n.type] || 'border-l-white/10'
                    } ${!n.read ? 'bg-white/5' : ''}`}
                  >
                    <div className="flex items-start gap-2">
                      <span className="text-lg mt-0.5">{typeIcons[n.type] || '📢'}</span>
                      <div>
                        <div className={`text-sm ${!n.read ? 'font-bold' : 'text-white/60'}`}>{n.text}</div>
                        <div className="text-xs text-white/30 mt-0.5">
                          {new Date(n.createdAt).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}

      {/* Toast for latest unread notification */}
      {unreadCount > 0 && myNotifications[0] && !myNotifications[0].read && (
        <div className="fixed top-4 right-4 z-50 animate-slide-in pointer-events-auto">
          <div
            className={`bg-surface-light border border-white/10 rounded-xl p-3 shadow-2xl max-w-sm flex items-start gap-2 cursor-pointer`}
            onClick={() => {
              dispatch({ type: 'MARK_NOTIFICATION_READ', payload: myNotifications[0].id });
            }}
          >
            <span className="text-xl">{typeIcons[myNotifications[0].type] || '📢'}</span>
            <div>
              <div className="text-sm font-bold">{myNotifications[0].text}</div>
              <div className="text-xs text-white/40">Click to dismiss</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
