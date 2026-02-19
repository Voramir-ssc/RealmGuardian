import React from 'react';
import { RefreshCw, Shield } from 'lucide-react';

const GoldWidget = ({ characters = [], loading, onLogin }) => {
    // Calculate totals
    const totalGold = characters.reduce((acc, char) => acc + (char.gold || 0), 0);
    const totalPlaytimeSeconds = characters.reduce((acc, char) => acc + (char.played_time || 0), 0);

    const formatPlaytime = (seconds) => {
        if (!seconds) return "N/A";
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        return `${days}d ${hours}h`;
    };

    return (
        <div className="bg-surface border border-white/5 rounded-2xl p-6 md:col-span-2 flex flex-col justify-between">
            <div className="flex justify-between items-start mb-6">
                <div>
                    <h3 className="text-secondary text-sm font-medium uppercase tracking-wider mb-1">Total Wealth</h3>
                    <div className="text-3xl font-bold text-white tracking-tight">{(totalGold / 10000).toLocaleString('de-DE')} <span className="text-yellow-500">g</span></div>
                    <div className="text-sm text-secondary/50 mt-1">
                        {characters.length > 0 ? `Across ${characters.length} characters` : 'No data'}
                    </div>
                </div>
                <div className="text-right">
                    <h3 className="text-secondary text-xs font-medium uppercase tracking-wider mb-1">Account Playtime</h3>
                    <div className="text-xl font-bold text-white tracking-tight">{formatPlaytime(totalPlaytimeSeconds)}</div>
                </div>
            </div>

            <div className="mt-4 border-t border-white/5 pt-4">
                <div className="flex items-center gap-2 text-xs text-secondary/50">
                    <Shield size={12} />
                    <span>Battle.net Connected</span>
                </div>
            </div>
        </div>
    );
};

export default GoldWidget;
