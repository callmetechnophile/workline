import React, { useState, useEffect, useRef } from "react";
import {
  Bell,
  Check,
  CheckSquare,
  MessageSquare,
  ShieldAlert,
  CheckCircle2,
  UserPlus,
  Clock,
  X,
} from "lucide-react";

export interface NotificationItem {
  id: string;
  user_id: string;
  notification_type: "MENTION" | "TASK_ASSIGNED" | "APPROVAL_REQUEST" | "APPROVAL_DECISION" | "TEAM_INVITE" | string;
  title: string;
  message: string;
  related_entity_type?: string;
  related_entity_id?: string;
  read: boolean;
  created_at: string;
}

interface NotificationDropdownProps {
  apiBase: string;
  userId?: string;
}

export const NotificationDropdown: React.FC<NotificationDropdownProps> = ({
  apiBase,
  userId = "current_user",
}) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const fetchNotifications = async () => {
    try {
      const res = await fetch(`${apiBase}/api/notifications?user_id=${encodeURIComponent(userId)}`);
      if (res.ok) {
        const data = await res.json();
        setNotifications(data);
      } else {
        // Fallback sample notifications
        setNotifications([
          {
            id: "notif_001",
            user_id: userId,
            notification_type: "MENTION",
            title: "Lead Engineer mentioned you",
            message: "Hey, check the decoupling capacitors on the 3.3V rail.",
            read: false,
            created_at: new Date(Date.now() - 1800000).toISOString(),
          },
          {
            id: "notif_002",
            user_id: userId,
            notification_type: "APPROVAL_REQUEST",
            title: "New Gate Approval Requested",
            message: "Substitute LM7805 with MP1584 Buck Converter requires your review.",
            read: false,
            created_at: new Date(Date.now() - 7200000).toISOString(),
          },
        ]);
      }
    } catch (err) {
      console.error("Failed to fetch notifications:", err);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 15000); // 15s poll
    return () => clearInterval(interval);
  }, [userId]);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleMarkAsRead = async (notifId: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === notifId ? { ...n, read: true } : n))
    );
    try {
      await fetch(`${apiBase}/api/notifications/${notifId}/read`, { method: "PATCH" });
    } catch (err) {
      console.error("Mark read failed:", err);
    }
  };

  const handleMarkAllRead = async () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    try {
      await fetch(`${apiBase}/api/notifications/mark-all-read`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId }),
      });
    } catch (err) {
      console.error("Mark all read failed:", err);
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case "MENTION":
        return <MessageSquare className="w-3.5 h-3.5 text-cyan-400" />;
      case "TASK_ASSIGNED":
        return <CheckSquare className="w-3.5 h-3.5 text-emerald-400" />;
      case "APPROVAL_REQUEST":
        return <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />;
      case "APPROVAL_DECISION":
        return <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />;
      case "TEAM_INVITE":
        return <UserPlus className="w-3.5 h-3.5 text-pink-400" />;
      default:
        return <Bell className="w-3.5 h-3.5 text-zinc-400" />;
    }
  };

  return (
    <div className="relative inline-block" ref={dropdownRef}>
      {/* Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-lg bg-zinc-900/80 hover:bg-zinc-800 text-zinc-300 hover:text-zinc-100 border border-zinc-800 transition-colors focus:outline-none"
        title="Notifications"
      >
        <Bell className="w-4 h-4" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-cyan-500 px-1 text-[10px] font-bold text-zinc-950 font-mono shadow-md animate-pulse">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-xl bg-zinc-900 border border-zinc-800 shadow-2xl z-50 overflow-hidden text-xs">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-950/60">
            <div className="flex items-center space-x-2">
              <Bell className="w-4 h-4 text-cyan-400" />
              <span className="font-semibold text-zinc-100">Engineering Alerts</span>
              {unreadCount > 0 && (
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/40">
                  {unreadCount} unread
                </span>
              )}
            </div>

            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                className="text-[11px] text-zinc-400 hover:text-cyan-400 font-mono flex items-center gap-1 transition-colors"
              >
                <Check className="w-3 h-3" /> Mark all read
              </button>
            )}
          </div>

          {/* Notifications Scroll List */}
          <div className="max-h-[380px] overflow-y-auto divide-y divide-zinc-800/60">
            {notifications.length > 0 ? (
              notifications.map((n) => (
                <div
                  key={n.id}
                  onClick={() => handleMarkAsRead(n.id)}
                  className={`p-3 transition-colors cursor-pointer flex items-start space-x-3 ${
                    n.read ? "bg-zinc-900/40 hover:bg-zinc-850/50" : "bg-zinc-800/40 hover:bg-zinc-800/60"
                  }`}
                >
                  <div className="p-1.5 rounded bg-zinc-950 border border-zinc-800 mt-0.5 shrink-0">
                    {getIcon(n.notification_type)}
                  </div>

                  <div className="flex-1 min-w-0 space-y-1">
                    <div className="flex items-center justify-between gap-1">
                      <span className={`text-xs truncate ${n.read ? "text-zinc-300 font-normal" : "text-zinc-100 font-semibold"}`}>
                        {n.title}
                      </span>
                      {!n.read && (
                        <span className="w-2 h-2 rounded-full bg-cyan-400 shrink-0" />
                      )}
                    </div>

                    <p className="text-[11px] text-zinc-400 line-clamp-2 leading-relaxed">
                      {n.message}
                    </p>

                    <span className="text-[10px] text-zinc-500 font-mono flex items-center gap-1">
                      <Clock className="w-2.5 h-2.5" />
                      {new Date(n.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-zinc-500 font-mono">
                <span>No alerts or notifications</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
