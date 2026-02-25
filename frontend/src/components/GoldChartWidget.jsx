import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const GoldChartWidget = ({ history = [], loading }) => {
    // Format data for Recharts
    const chartData = history.map(entry => {
        const date = new Date(entry.timestamp);
        return {
            date: date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' }),
            fullDate: date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }),
            gold: Math.floor(entry.total_gold / 10000) // Convert copper to gold
        };
    });

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
        <div className="bg-surface border border-white/5 rounded-2xl p-6 flex flex-col justify-between h-full">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-secondary text-sm font-medium uppercase tracking-wider mb-1">Wealth History</h3>
                    <p className="text-xs text-secondary/50">Tracking across all characters</p>
                </div>
            </div>

            <div className="h-24 w-full mt-auto">
                {loading && history.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-secondary/50">
                        Loading history...
                    </div>
                ) : history.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-secondary/50">
                        No historical data available yet.
                    </div>
                ) : (
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                            <defs>
                                <linearGradient id="goldGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#eab308" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#eab308" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                            <XAxis
                                dataKey="date"
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 12 }}
                                dy={10}
                            />
                            <YAxis
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 12 }}
                                tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
                                dx={-10}
                                domain={['dataMin - 15000', 'dataMax + 15000']}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Area
                                type="monotone"
                                dataKey="gold"
                                stroke="#eab308"
                                strokeWidth={2}
                                fillOpacity={1}
                                fill="url(#goldGradient)"
                                animationDuration={1000}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                )}
            </div>
        </div>
    );
};

export default GoldChartWidget;
