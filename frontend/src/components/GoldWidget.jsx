/**
 * GoldWidget.jsx
 * 
 * Dashboard widget displaying total aggregated gold across all synced characters
 * and a summary of the connected Battle.net account status.
 */
import React from 'react';
import { RefreshCw, Shield } from 'lucide-react';

const GoldWidget = ({ characters = [], loading, onLogin }) => {
    // Calculate totals
    const totalGold = characters.reduce((acc, char) => acc + (char.gold || 0), 0);

    return (
        <div className="bg-surface border border-white/5 rounded-2xl p-6 flex flex-col justify-between">
            <div className="flex justify-between items-start mb-6">
                <div>
                    <h3 className="text-secondary text-sm font-medium uppercase tracking-wider mb-1">Total Wealth</h3>
                    <div className="text-3xl font-bold text-white tracking-tight">{(totalGold / 10000).toLocaleString('de-DE')} <span className="text-yellow-500">g</span></div>
                    <div className="text-sm text-secondary/50 mt-1">
                        {characters.length > 0 ? `Across ${characters.length} characters` : 'No data'}
                    </div>
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
