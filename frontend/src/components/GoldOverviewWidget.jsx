/**
 * GoldOverviewWidget.jsx
 * 
 * Dashboard widget displaying total aggregated gold across all synced characters
 * and a summary of the connected Battle.net account status, including a sparkline/chart
 * for historical price trends similar to the TokenWidget.
 */
import React from 'react';
import { Shield, Coins } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const GoldOverviewWidget = ({ characters = [], history = [], loading }) => {
    // Calculate totals
    const totalGold = characters.reduce((acc, char) => acc + (char.gold || 0), 0);

    // Format data for Recharts
    const chartData = history.map(entry => {
        const date = new Date(entry.timestamp);
        return {
            date: date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' }),
            fullDate: date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }),
            gold: Math.floor(entry.total_gold / 10000) // Convert copper to gold
        };
    });

    const safeHistory = Array.isArray(history) ? history : [];

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-surface/90 border border-white/10 rounded-lg p-3 shadow-xl backdrop-blur-md">
                    <p className="text-secondary text-xs mb-1">{payload[0].payload.fullDate}</p>
                    <p className="font-bold text-white">
                        {payload[0].value.toLocaleString('de-DE')} <span className="text-yellow-500 font-normal">g</span>
                    </p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="bg-surface border border-white/5 rounded-2xl p-6 relative overflow-hidden group hover:border-yellow-500/30 transition-all duration-300 flex flex-col justify-between">
            <div className="flex justify-between items-start mb-4 relative z-10">
                <div>
                    <h3 className="text-secondary text-sm font-medium uppercase tracking-wider mb-1">Gesamtvermögen</h3>
                    <div className="flex items-baseline gap-2 mt-1">
                        <span className="text-3xl font-bold text-white tracking-tight">{(totalGold / 10000).toLocaleString('de-DE')}</span>
                        <span className="text-yellow-500 text-sm font-medium">Gold</span>
                    </div>
                    <div className="text-sm text-secondary/50 mt-1">
                        {characters.length > 0 ? `Auf ${characters.length} Charakteren` : 'Keine Daten'}
                    </div>
                </div>
            </div>

            <div className="h-32 w-full mt-auto opacity-75 group-hover:opacity-100 transition-opacity duration-500 relative z-10">
                {loading && history.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-secondary/50 text-xs">
                        Verlauf wird geladen...
                    </div>
                ) : history.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-secondary/50 text-xs">
                        Noch keine historischen Daten verfügbar.
                    </div>
                ) : (
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                            <defs>
                                <linearGradient id="goldGradientArea" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#eab308" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#eab308" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                            <XAxis
                                dataKey="date"
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10 }}
                                dy={10}
                                minTickGap={20}
                            />
                            <YAxis
                                hide={true}
                                domain={['dataMin - 15000', 'dataMax + 15000']}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Area
                                type="monotone"
                                dataKey="gold"
                                stroke="#eab308"
                                strokeWidth={2}
                                fillOpacity={1}
                                fill="url(#goldGradientArea)"
                                animationDuration={1000}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                )}
            </div>

            <div className="mt-4 pt-4 border-t border-white/5 relative z-10 flex justify-between items-center">
                <div className="flex items-center gap-2 text-xs text-secondary/50">
                    <Shield size={12} />
                    <span>Battle.net Verbunden</span>
                </div>
                <div className="text-[10px] text-secondary/30 uppercase tracking-widest font-semibold">
                    Vermögensverlauf
                </div>
            </div>

            <div className="absolute top-0 right-0 p-3 opacity-5 pointer-events-none">
                <Coins size={120} />
            </div>
        </div>
    );
};

export default GoldOverviewWidget;
