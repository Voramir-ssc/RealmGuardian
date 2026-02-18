import React, { useState, useEffect } from 'react';
import { Plus, X, Search, TrendingUp, TrendingDown, Package } from 'lucide-react';

const WatchlistWidget = () => {
    const [items, setItems] = useState([]);
    const [newItemId, setNewItemId] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    const fetchItems = async () => {
        try {
            const res = await fetch(`${apiUrl}/api/items`);
            if (res.ok) {
                const data = await res.json();
                setItems(data);
            }
        } catch (err) {
            console.error("Failed to fetch watchlist", err);
        }
    };

    useEffect(() => {
        fetchItems();
        const interval = setInterval(fetchItems, 60000);
        return () => clearInterval(interval);
    }, []);

    const handleAddItem = async (e) => {
        e.preventDefault();
        if (!newItemId) return;

        setLoading(true);
        setError(null);

        try {
            const res = await fetch(`${apiUrl}/api/items`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_id: parseInt(newItemId) })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Failed to add item');
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
        try {
            await fetch(`${apiUrl}/api/items/${itemId}`, { method: 'DELETE' });
            fetchItems();
        } catch (err) {
            console.error("Failed to delete item", err);
        }
    };

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
                        <div key={item.id} className="flex items-center justify-between bg-black/20 border border-white/5 rounded-xl p-3 hover:border-white/10 transition-colors group">
                            <div className="flex items-center gap-3">
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
                                    <div className="text-xs text-secondary/50">ID: {item.item_id}</div>
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
                                    className="text-secondary/50 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100 p-2"
                                >
                                    <X size={16} />
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default WatchlistWidget;
