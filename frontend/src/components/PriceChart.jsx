import React from 'react';
import { AreaChart, Area, ResponsiveContainer, YAxis, XAxis, Tooltip } from 'recharts';

const PriceChart = ({ data, selectedRange, onRangeChange, color = "#00ced1", currencySymbol = "g" }) => {
    // Determine tick interval based on range (approximate number of ticks)
    // This is handled by recharts somewhat automatically but we can hint it

    return (
        <div className="h-full w-full">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id={`colorPrice-${color}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={color} stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <XAxis
                        dataKey={selectedRange === '24h' ? 'formattedTime' : 'formattedDate'}
                        domain={['dataMin', 'dataMax']}
                        type="category"
                        stroke="#ffffff33"
                        tick={{ fill: '#ffffff66', fontSize: 10 }}
                        tickLine={false}
                        axisLine={false}
                        minTickGap={60}
                    />
                    <YAxis
                        domain={['auto', 'auto']}
                        stroke="#ffffff33"
                        tick={{ fill: '#ffffff66', fontSize: 10 }}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(value) => {
                            if (value >= 10000) return `${(value / 1000).toFixed(0)}k`;
                            if (value >= 1000) return `${(value / 1000).toFixed(1)}k`;
                            return value.toFixed(0);
                        }}
                        width={35}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1a1b1e', borderColor: '#ffffff1a', borderRadius: '8px', color: '#fff' }}
                        itemStyle={{ color: color }}
                        formatter={(value) => [`${value.toLocaleString('de-DE')}${currencySymbol}`, 'Price']}
                        labelStyle={{ color: '#ffffff99', marginBottom: '4px' }}
                    />
                    <Area
                        type="monotone"
                        dataKey="price"
                        stroke={color}
                        fillOpacity={1}
                        fill={`url(#colorPrice-${color})`}
                        strokeWidth={2}
                        isAnimationActive={false}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};

export default PriceChart;
