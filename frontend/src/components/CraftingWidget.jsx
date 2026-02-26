import React, { useState, useEffect } from 'react';
import { Search, Loader2, Plus, Trash2, ArrowRight, TrendingUp, TrendingDown } from 'lucide-react';

export default function CraftingWidget({ apiUrl }) {
    const [recipes, setRecipes] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetchRecipes();
    }, [apiUrl]);

    const fetchRecipes = async () => {
        try {
            const res = await fetch(`${apiUrl}/api/recipes`);
            const data = await res.json();
            setRecipes(data);
        } catch (error) {
            console.error("Failed to fetch recipes", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!searchQuery.trim()) return;

        setIsSearching(true);
        try {
            const res = await fetch(`${apiUrl}/api/recipes/search?query=${encodeURIComponent(searchQuery)}`);
            const data = await res.json();
            setSearchResults(data);
        } catch (error) {
            console.error("Search failed", error);
        } finally {
            setIsSearching(false);
        }
    };

    const addRecipe = async (recipeId) => {
        try {
            setIsLoading(true);
            const res = await fetch(`${apiUrl}/api/recipes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ recipe_id: recipeId })
            });
            if (res.ok) {
                setSearchQuery('');
                setSearchResults([]);
                await fetchRecipes();
            } else {
                const err = await res.json();
                alert(`Error: ${err.detail}`);
                setIsLoading(false);
            }
        } catch (error) {
            console.error("Failed to add recipe", error);
            setIsLoading(false);
        }
    };

    const deleteRecipe = async (id) => {
        try {
            setIsLoading(true);
            const res = await fetch(`${apiUrl}/api/recipes/${id}`, {
                method: 'DELETE'
            });
            if (res.ok) {
                await fetchRecipes();
            } else {
                setIsLoading(false);
            }
        } catch (error) {
            console.error("Failed to delete recipe", error);
            setIsLoading(false);
        }
    };

    const formatGold = (copper) => {
        if (!copper) return "0g";
        const gold = Math.floor(copper / 10000);
        return `${gold.toLocaleString()}g`;
    };

    return (
        <div className="bg-surface rounded-2xl border border-white/5 overflow-hidden flex flex-col h-full">
            <div className="p-6 border-b border-white/5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-xl font-bold font-display tracking-tight text-white mb-1">Crafting Profit Calculator</h2>
                    <p className="text-sm text-white/50">Track margins based on live AH prices.</p>
                </div>

                {/* Search Bar */}
                <form onSubmit={handleSearch} className="flex gap-2 w-full md:w-auto relative">
                    <div className="relative flex-1 md:w-64">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
                        <input
                            type="text"
                            placeholder="Search recipe..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-white/40 focus:outline-none focus:border-brand-primary/50 focus:ring-1 focus:ring-brand-primary/50 transition-all"
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={isSearching}
                        className="bg-brand-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-brand-primary/90 transition-colors disabled:opacity-50 flexitems-center justify-center gap-2"
                    >
                        {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Search'}
                    </button>

                    {/* Search Dropdown */}
                    {searchResults.length > 0 && (
                        <div className="absolute top-full left-0 right-0 mt-2 bg-surface border border-white/10 rounded-xl shadow-2xl z-50 max-h-64 overflow-y-auto">
                            {searchResults.map((res) => (
                                <div key={res.id} className="flex items-center justify-between p-3 hover:bg-white/5 transition-colors border-b border-white/5 last:border-0">
                                    <span className="text-sm font-medium text-white/90">{res.name}</span>
                                    <button
                                        type="button"
                                        onClick={() => addRecipe(res.id)}
                                        className="p-1.5 hover:bg-brand-primary/20 text-brand-primary rounded-lg transition-colors"
                                        title="Add Recipe"
                                    >
                                        <Plus className="w-4 h-4" />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </form>
            </div>

            <div className="p-6 flex-1 overflow-auto">
                {isLoading ? (
                    <div className="h-48 flex items-center justify-center">
                        <Loader2 className="w-8 h-8 text-brand-primary animate-spin" />
                    </div>
                ) : recipes.length === 0 ? (
                    <div className="h-48 flex flex-col items-center justify-center text-white/40">
                        <TrendingUp className="w-12 h-12 mb-3 opacity-50" />
                        <p className="text-sm">No recipes tracked yet.</p>
                        <p className="text-xs mt-1">Search via the Blizzard API above to add one.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                        {recipes.map(recipe => (
                            <div key={recipe.id} className="bg-white/5 rounded-xl border border-white/10 overflow-hidden flex flex-col group relative">
                                <button
                                    onClick={() => deleteRecipe(recipe.id)}
                                    className="absolute top-3 right-3 p-1.5 bg-black/40 hover:bg-red-500/20 text-white/40 hover:text-red-400 rounded-lg transition-colors z-10 opacity-0 group-hover:opacity-100 disabled:opacity-50"
                                    disabled={isLoading}
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>

                                {/* Header (Crafted Item) */}
                                <div className="p-4 bg-gradient-to-br from-white/5 to-transparent border-b border-white/5 flex items-center gap-3">
                                    {recipe.icon_url ? (
                                        <img src={recipe.icon_url} alt="" className="w-10 h-10 rounded-lg border border-white/10" />
                                    ) : (
                                        <div className="w-10 h-10 rounded-lg bg-white/10 border border-white/10 flex items-center justify-center">
                                            <span className="text-xs text-white/40">?</span>
                                        </div>
                                    )}
                                    <div>
                                        <h3 className="font-semibold text-white/90 text-sm leading-tight group-hover:text-brand-primary transition-colors pr-6">
                                            {recipe.name}
                                        </h3>
                                        <div className="flex items-center gap-1.5 mt-1">
                                            <span className="text-xs font-medium text-brand-primary">{formatGold(recipe.target_price)}</span>
                                            <span className="text-[10px] text-white/40 uppercase tracking-wide px-1.5 py-0.5 rounded-sm bg-white/5 border border-white/10">Yield: {recipe.crafted_quantity}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Reagents */}
                                <div className="p-4 flex-1">
                                    <h4 className="text-[10px] items-center gap-1 text-white/50 uppercase tracking-widest font-semibold mb-3 flex">
                                        Reagents <ArrowRight className="w-3 h-3" />
                                    </h4>
                                    <div className="space-y-2">
                                        {recipe.reagents.map(reg => (
                                            <div key={reg.item_id} className="flex justify-between items-center text-xs">
                                                <span className="text-white/70 truncate mr-2" title={reg.name}>
                                                    {reg.quantity}x {reg.name}
                                                </span>
                                                <span className="text-white/50 shrink-0 tabular-nums">
                                                    {formatGold(reg.total_price)}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Profit Footer */}
                                <div className="p-4 border-t border-white/5 bg-black/20 flex justify-between items-center">
                                    <div className="flex flex-col">
                                        <span className="text-[10px] text-white/40 uppercase tracking-widest font-semibold">Total Cost</span>
                                        <span className="text-sm font-medium text-white/70">{formatGold(recipe.total_cost)}</span>
                                    </div>
                                    <div className="flex flex-col items-end">
                                        <span className="text-[10px] text-white/40 uppercase tracking-widest font-semibold">Margin</span>
                                        <div className={`flex items-center gap-1 text-lg font-bold ${recipe.profit > 0 ? 'text-green-400' : 'text-red-400'}`}>
                                            {recipe.profit > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                                            {formatGold(recipe.profit)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
