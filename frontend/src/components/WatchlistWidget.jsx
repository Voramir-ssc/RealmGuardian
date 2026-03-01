/**
 * WatchlistWidget.jsx
 * 
 * Dashboard widget for tracking user-selected auction house commodities.
 * Allows adding new items via Blizzard ID and displays their current minimum buyout prices.
 */
import React, { useState, useEffect } from 'react';
import { Plus, X, Search, TrendingUp, TrendingDown, Package, ChevronDown, ChevronUp } from 'lucide-react';
import PriceChart from './PriceChart';

const WatchlistWidget = ({ apiUrl: propApiUrl }) => {
    const [items, setItems] = useState([]);
    const [newItemId, setNewItemId] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [expandedItem, setExpandedItem] = useState(null);
    const [itemHistory, setItemHistory] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [historyRange, setHistoryRange] = useState('14d');

    // Dynamic API URL logic similar to App.jsx
    const fetchItems = React.useCallback(async () => {
        let url = propApiUrl;
        try {
            let res;
            try {
                res = await fetch(`${url}/api/items`);
            } catch {
                console.warn("Watchlist fetch failed, trying local network fallback...");
                url = `http://${window.location.hostname}:8000`;
                res = await fetch(`${url}/api/items`);
            }

            if (res.ok) {
                const data = await res.json();
                // Sort by price descending
                const sortedData = data.sort((a, b) => (b.current_price || 0) - (a.current_price || 0));
                setItems(sortedData);
                setError(null);
            } else {
                throw new Error(res.statusText);
            }
        } catch (err) {
            console.error("Failed to fetch watchlist", err);
            setError("Could not load watchlist.");
        }
    }, [propApiUrl]);

    useEffect(() => {
        fetchItems();
        const interval = setInterval(fetchItems, 60000);
        return () => clearInterval(interval);
    }, [fetchItems]);

    const fetchHistory = React.useCallback(async (itemId, range) => {
        setHistoryLoading(true);
        let url = propApiUrl;
        try {
            let res;
            try {
                res = await fetch(`${url}/api/items/${itemId}/history?range=${range}`);
            } catch {
                url = `http://${window.location.hostname}:8000`;
                res = await fetch(`${url}/api/items/${itemId}/history?range=${range}`);
            }

            if (res.ok) {
                const data = await res.json();
                // Map to chart format
                const chartData = data.map(entry => ({
                    price: entry.price / 10000,
                    time: entry.last_updated_timestamp,
                    formattedTime: new Date(entry.last_updated_timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    formattedDate: new Date(entry.last_updated_timestamp * 1000).toLocaleDateString([], { day: '2-digit', month: '2-digit' })
                }));
                setItemHistory(chartData);
            }
        } catch (err) {
            console.error("Failed to fetch item history", err);
        } finally {
            setHistoryLoading(false);
        }
    }, [propApiUrl]);

    const toggleExpand = (itemId) => {
        if (expandedItem === itemId) {
            setExpandedItem(null);
            setItemHistory([]);
        } else {
            setExpandedItem(itemId);
            fetchHistory(itemId, historyRange);
        }
    };

    const handleRangeChange = (range) => {
        setHistoryRange(range);
        if (expandedItem) {
            fetchHistory(expandedItem, range);
        }
    };

    const handleAddItem = async (e) => {
        e.preventDefault();
        if (!newItemId) return;

        setLoading(true);
        setError(null);
        let url = propApiUrl;

        try {
            let res;
            try {
                res = await fetch(`${url}/api/items`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ item_id: parseInt(newItemId) })
                });
            } catch {
                url = `http://${window.location.hostname}:8000`;
                res = await fetch(`${url}/api/items`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ item_id: parseInt(newItemId) })
                });
            }

            if (!res.ok) {
                let errMsg = 'Failed to add item';
                try {
                    const err = await res.json();
                    errMsg = err.detail || errMsg;
                } catch (e) {
                    // Fallback if the response is not valid JSON (e.g. proxy HTML error page)
                    errMsg = 'Server returned an invalid response. Ensure backend is running.';
                }
                throw new Error(errMsg);
            }

            setNewItemId('');
            fetchItems();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteItem = async (itemId) => {
        let url = propApiUrl;
        try {
            await fetch(`${url}/api/items/${itemId}`, { method: 'DELETE' });
            fetchItems();
        } catch (err) {
            try {
                await fetch(`http://${window.location.hostname}:8000/api/items/${itemId}`, { method: 'DELETE' });
                fetchItems();
            } catch {
                console.error("Failed to delete item", err);
            }
        }
    };

    const ranges = [
        { label: '24H', value: '24h' },
        { label: '7D', value: '7d' },
        { label: '14D', value: '14d' },
        { label: '30D', value: '30d' }
    ];

    return (
        <div className="bg-surface border border-white/5 rounded-2xl p-6 md:col-span-2">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-secondary text-sm font-medium uppercase tracking-wider">Commodity Watchlist</h3>
                <span className="text-xs text-secondary/50">Region Wide Prices</span>
            </div>

            {/* Add Item Form */}
            <form onSubmit={handleAddItem} className="flex gap-2 mb-6">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary/50" size={16} />
                    <input
                        type="number"
                        placeholder="Enter WoW Item ID (e.g. 190321)"
                        value={newItemId}
                        onChange={(e) => setNewItemId(e.target.value)}
                        className="w-full bg-black/20 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-accent/50 transition-colors"
                    />
                </div>
                <button
                    type="submit"
                    disabled={loading}
                    className="bg-accent/10 hover:bg-accent/20 text-accent border border-accent/20 rounded-lg px-4 py-2 flex items-center gap-2 transition-all disabled:opacity-50"
                >
                    <Plus size={16} />
                    <span className="text-sm font-medium">track</span>
                </button>
            </form>

            {error && (
                <div className="mb-4 text-xs text-red-400 bg-red-400/10 p-2 rounded border border-red-400/20">
                    {error}
                </div>
            )}

            {/* List */}
            <div className="space-y-3">
                {items.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-32 text-secondary/50 border-2 border-dashed border-white/5 rounded-xl">
                        <Package size={24} className="mb-2 opacity-50" />
                        <span className="text-sm">No items tracked yet</span>
                    </div>
                ) : (
                    items.map(item => (
                        <div key={item.id} className="bg-black/20 border border-white/5 rounded-xl transition-all hover:border-white/10">
                            <div className="flex items-center justify-between p-3">
                                <div className="flex items-center gap-3 flex-1 cursor-pointer" onClick={() => toggleExpand(item.item_id)}>
                                    {item.icon_url ? (
                                        <img src={item.icon_url} alt={item.name} className="w-10 h-10 rounded-lg border border-white/10" />
                                    ) : (
                                        <div className="w-10 h-10 rounded-lg bg-surface border border-white/10 flex items-center justify-center">
                                            <Package size={20} className="text-secondary" />
                                        </div>
                                    )}
                                    <div>
                                        <div className={`font-medium text-sm ${item.quality === 'EPIC' ? 'text-purple-400' : item.quality === 'RARE' ? 'text-blue-400' : 'text-white'}`}>
                                            {item.name}
                                        </div>
                                        <div className="text-xs text-secondary/50 flex items-center gap-2">
                                            ID: {item.item_id}
                                            {expandedItem === item.item_id ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-4">
                                    <div className="text-right">
                                        <div className="font-bold text-white tracking-tight">
                                            {item.current_price ? (item.current_price / 10000).toLocaleString('de-DE') : 0}g
                                        </div>
                                        <div className="text-[10px] text-secondary/50">
                                            {item.last_updated ? new Date(item.last_updated).toLocaleTimeString() : 'No Data'}
                                        </div>
                                    </div>

                                    <button
                                        onClick={() => handleDeleteItem(item.item_id)}
                                        className="text-secondary/50 hover:text-red-400 transition-colors p-2"
                                    >
                                        <X size={16} />
                                    </button>
                                </div>
                            </div>

                            {/* Expanded Graph Area */}
                            {expandedItem === item.item_id && (
                                <div className="border-t border-white/5 p-4 bg-black/40 rounded-b-xl">
                                    <div className="flex justify-between items-center mb-4">
                                        <span className="text-xs text-secondary uppercase tracking-wider font-medium">Price History</span>
                                        <div className="flex gap-1">
                                            {ranges.map(range => (
                                                <button
                                                    key={range.value}
                                                    onClick={() => handleRangeChange(range.value)}
                                                    className={`text-[10px] px-2 py-0.5 rounded transition-colors ${historyRange === range.value
                                                        ? 'bg-accent/20 text-accent font-medium'
                                                        : 'text-secondary hover:text-white hover:bg-white/5'
                                                        }`}
                                                >
                                                    {range.label}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="h-48 w-full">
                                        {historyLoading ? (
                                            <div className="h-full w-full flex items-center justify-center text-secondary/50 text-xs">Loading...</div>
                                        ) : itemHistory.length > 0 ? (
                                            <PriceChart
                                                data={itemHistory}
                                                selectedRange={historyRange}
                                                onRangeChange={() => { }} // Handled by buttons above
                                                color="#a3b3cc" // Different color for items
                                            />
                                        ) : (
                                            <div className="h-full w-full flex items-center justify-center text-secondary/50 text-xs">No history data available</div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default WatchlistWidget;
