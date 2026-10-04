import React from "react";

function getDaysLeft(deadline) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(deadline);
  target.setHours(0, 0, 0, 0);
  return Math.ceil((target - today) / (1000 * 60 * 60 * 24));
}

function getPriority(daysLeft) {
  if (daysLeft < 0) return { label: "Expired", color: "text-white/30", bar: "bg-white/10", ring: "border-white/10", dot: "bg-white/20", pct: 100 };
  if (daysLeft <= 14) return { label: "Critical", color: "text-red-400", bar: "bg-red-500", ring: "border-red-500/40", dot: "bg-red-400", pct: 95 };
  if (daysLeft <= 30) return { label: "High", color: "text-orange-400", bar: "bg-orange-500", ring: "border-orange-500/40", dot: "bg-orange-400", pct: 70 };
  if (daysLeft <= 60) return { label: "Medium", color: "text-yellow-400", bar: "bg-yellow-500", ring: "border-yellow-500/40", dot: "bg-yellow-400", pct: 40 };
  return { label: "Low", color: "text-emerald-400", bar: "bg-emerald-500", ring: "border-emerald-500/40", dot: "bg-emerald-400", pct: 15 };
}

export default function UpcomingDeadlines({ universities = [] }) {
  const sorted = [...universities]
    .map((u) => ({ ...u, daysLeft: getDaysLeft(u.deadline) }))
    .sort((a, b) => a.daysLeft - b.daysLeft);

  const next = sorted.find((u) => u.daysLeft >= 0);

  return (
    <div className="w-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white">Upcoming Deadlines</h2>
          <p className="text-white/40 text-sm mt-0.5">Stay ahead of your applications</p>
        </div>
        <span className="text-[10px] font-black uppercase tracking-widest text-white/30 bg-white/5 px-3 py-1.5 rounded-lg border border-white/10">
          {sorted.filter((u) => u.daysLeft >= 0).length} Active
        </span>
      </div>

      {/* Countdown hero — nearest deadline */}
      {next && (
        <div className={`mb-6 rounded-2xl p-5 border ${getPriority(next.daysLeft).ring} bg-white/5 relative overflow-hidden`}>
          <div className="absolute inset-0 opacity-5">
            <div className={`absolute -right-8 -top-8 w-40 h-40 rounded-full ${getPriority(next.daysLeft).bar} blur-3xl`} />
          </div>
          <p className="text-[10px] font-black uppercase tracking-widest text-white/30 mb-2">Next Deadline</p>
          <div className="flex items-end justify-between">
            <div>
              <p className="text-white font-bold text-lg leading-tight">{next.name}</p>
              <p className="text-white/40 text-xs mt-1">{next.deadline}</p>
            </div>
            <div className="text-right">
              <p className={`text-4xl font-black tabular-nums ${getPriority(next.daysLeft).color}`}>
                {next.daysLeft}
              </p>
              <p className="text-white/30 text-xs font-semibold uppercase tracking-wider">days left</p>
            </div>
          </div>
          {/* progress bar */}
          <div className="mt-4 h-1 rounded-full bg-white/10 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${getPriority(next.daysLeft).bar}`}
              style={{ width: `${getPriority(next.daysLeft).pct}%` }}
            />
          </div>
        </div>
      )}

      {/* All deadlines list */}
      <div className="space-y-2">
        {sorted.map((u) => {
          const p = getPriority(u.daysLeft);
          const isExpired = u.daysLeft < 0;
          return (
            <div
              key={u.id}
              className={`flex items-center gap-4 px-4 py-3 rounded-xl border transition-all
                ${isExpired
                  ? "border-white/5 bg-white/[0.02] opacity-40"
                  : "border-white/10 bg-white/5 hover:bg-white/[0.08] hover:border-white/20"
                }`}
            >
              {/* dot */}
              <span className={`w-2 h-2 rounded-full shrink-0 ${p.dot}`} />

              {/* name */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-white truncate">{u.name}</p>
                <p className="text-[11px] text-white/30">{u.deadline}</p>
              </div>

              {/* days */}
              <div className="text-right shrink-0">
                <p className={`text-sm font-black tabular-nums ${p.color}`}>
                  {isExpired ? "Expired" : `${u.daysLeft}d`}
                </p>
                <p className={`text-[10px] font-bold uppercase tracking-wider ${p.color} opacity-70`}>
                  {p.label}
                </p>
              </div>

              {/* mini bar */}
              {!isExpired && (
                <div className="w-12 h-1 rounded-full bg-white/10 overflow-hidden shrink-0">
                  <div
                    className={`h-full rounded-full ${p.bar}`}
                    style={{ width: `${p.pct}%` }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-5 flex flex-wrap gap-3 pt-4 border-t border-white/5">
        {[
          { label: "Critical", color: "bg-red-400", sub: "≤14 days" },
          { label: "High", color: "bg-orange-400", sub: "≤30 days" },
          { label: "Medium", color: "bg-yellow-400", sub: "≤60 days" },
          { label: "Low", color: "bg-emerald-400", sub: "60+ days" },
        ].map((l) => (
          <div key={l.label} className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${l.color}`} />
            <span className="text-[11px] text-white/30">
              <span className="text-white/50 font-semibold">{l.label}</span> {l.sub}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}