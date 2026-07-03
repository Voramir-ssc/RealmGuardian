import React, { useState, useEffect, useRef } from 'react';
import { Search, Loader2, Plus, Trash2, ArrowRight, TrendingUp, TrendingDown, ShoppingCart, ShoppingBag, CheckSquare, Square, Trash } from 'lucide-react';

// Reusable Async Search Component for Items
function ItemSearchAsync({ apiUrl, placeholder, onSelect, className }) {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const wrapperRef = useRef(null);

    useEffect(() => {
        function handleClickOutside(event) {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    useEffect(() => {
        if (!query || query.length < 3) {
            setResults([]);
            setIsOpen(false);
            return;
        }

        const fetchResults = async () => {
            setIsLoading(true);
            try {
                const res = await fetch(`${apiUrl}/api/items/search?q=${encodeURIComponent(query)}`);
                if (res.ok) {
                    const data = await res.json();
                    setResults(data);
                    setIsOpen(true);
                }
            } catch (err) {
                console.error("Search failed", err);
            } finally {
                setIsLoading(false);
            }
        };

        const timeoutId = setTimeout(fetchResults, 500); // 500ms debounce
        return () => clearTimeout(timeoutId);
    }, [query, apiUrl]);

    return (
        <div ref={wrapperRef} className={`relative ${className}`}>
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
                <input
                    type="text"
                    placeholder={placeholder}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onFocus={() => { if (results.length > 0) setIsOpen(true); }}
                    className="w-full bg-white/5 border border-white/10 rounded-lg pl-9 pr-8 py-2 text-sm text-white placeholder-white/40 focus:outline-none focus:border-[#148eff]/50 focus:ring-1 focus:ring-[#148eff]/50 transition-all"
                />
                {isLoading && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                        <Loader2 className="w-4 h-4 text-[#148eff] animate-spin" />
                    </div>
                )}
            </div>

            {isOpen && results.length > 0 && (
                <div className="absolute z-50 w-full mt-1 bg-[#1a1c23] border border-white/10 rounded-lg shadow-xl overflow-hidden max-h-60 overflow-y-auto">
                    {results.map((item) => (
                        <button
                            key={item.id}
                            type="button"
                            onClick={() => {
                                onSelect(item.id);
                                setQuery('');
                                setIsOpen(false);
                            }}
                            className="w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-white/5 transition-colors border-b border-white/5 last:border-0"
                        >
                            {item.icon_url ? (
                                <img src={item.icon_url} alt="" className="w-8 h-8 rounded border border-white/10 object-cover" />
                            ) : (
                                <div className="w-8 h-8 rounded bg-white/10 border border-white/10 flex items-center justify-center">
                                    <span className="text-[10px] text-white/40">?</span>
                                </div>
                            )}
                            <div className="flex-1 min-w-0">
                                <span className="block text-sm text-white/90 truncate">{item.name}</span>
                                <span className="block text-[10px] text-white/40">ID: {item.id}</span>
                            </div>
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}

export default function CraftingWidget({ apiUrl }) {
    const [recipes, setRecipes] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('profit');
    const [sortOrder, setSortOrder] = useState('margin-desc');

    // LocalStorage states for shopping list
    const [plannedQuantities, setPlannedQuantities] = useState(() => {
        const saved = localStorage.getItem('rg_planned_recipes');
        return saved ? JSON.parse(saved) : {};
    });

    const [checkedReagents, setCheckedReagents] = useState(() => {
        const saved = localStorage.getItem('rg_checked_reagents');
        return saved ? JSON.parse(saved) : {};
    });

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

    const handleAddRecipeSelect = async (itemId) => {
        if (!itemId) return;

        try {
            setIsLoading(true);
            const res = await fetch(`${apiUrl}/api/recipes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ crafted_item_id: itemId })
            });
            if (res.ok) {
                await fetchRecipes();
            } else {
                const err = await res.json();
                alert(`Fehler: ${err.detail}`);
                setIsLoading(false);
            }
        } catch (error) {
            console.error("Failed to add recipe", error);
            alert("Netzwerkfehler beim Hinzufügen.");
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
                // Also clean up from shopping list
                updatePlannedQty(id, 0);
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

    // Planned Quantities Helpers
    const updatePlannedQty = (recipeId, qty) => {
        const newQtys = { ...plannedQuantities };
        if (qty <= 0) {
            delete newQtys[recipeId];
        } else {
            newQtys[recipeId] = qty;
        }
        setPlannedQuantities(newQtys);
        localStorage.setItem('rg_planned_recipes', JSON.stringify(newQtys));
    };

    const toggleReagentCheck = (itemId) => {
        const newChecked = { ...checkedReagents };
        newChecked[itemId] = !newChecked[itemId];
        setCheckedReagents(newChecked);
        localStorage.setItem('rg_checked_reagents', JSON.stringify(newChecked));
    };

    const clearShoppingList = () => {
        setPlannedQuantities({});
        setCheckedReagents({});
        localStorage.removeItem('rg_planned_recipes');
        localStorage.removeItem('rg_checked_reagents');
    };

    // Consolidate Shopping List items
    const getConsolidatedReagents = () => {
        const consolidated = {};
        recipes.forEach(recipe => {
            const qty = plannedQuantities[recipe.id] || 0;
            if (qty > 0) {
                recipe.reagents.forEach(reg => {
                    const id = reg.item_id;
                    if (!consolidated[id]) {
                        consolidated[id] = {
                            item_id: id,
                            name: reg.name,
                            quantity: 0,
                            total_price: 0
                        };
                    }
                    consolidated[id].quantity += reg.quantity * qty;
                    // Approximate total price
                    consolidated[id].total_price += (reg.total_price / recipe.crafted_quantity) * qty;
                });
            }
        });
        return Object.values(consolidated);
    };

    const consolidatedList = getConsolidatedReagents();
    const plannedRecipeList = recipes.filter(r => (plannedQuantities[r.id] || 0) > 0);

    const sortedRecipes = [...recipes].sort((a, b) => {
        if (sortOrder === 'margin-desc') {
            return b.profit - a.profit;
        } else if (sortOrder === 'margin-asc') {
            return a.profit - b.profit;
        } else if (sortOrder === 'name-asc') {
            return a.name.localeCompare(b.name);
        }
        return 0;
    });

    return (
        <div className="bg-surface rounded-2xl border border-white/5 overflow-hidden flex flex-col h-full">
            {/* Header */}
            <div className="p-6 border-b border-white/5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-gradient-to-br from-white/[0.01] to-transparent">
                <div>
                    <h2 className="text-xl font-bold font-display tracking-tight text-white mb-1">Handwerks-Profitrechner & Einkaufsliste</h2>
                    <p className="text-sm text-white/50">Marge verfolgen und Materialien planen.</p>
                </div>

                {/* Add Recipe Bar and Sort */}
                {activeTab === 'profit' && (
                    <div className="flex gap-2 w-full md:w-auto relative items-center">
                        <select
                            value={sortOrder}
                            onChange={(e) => setSortOrder(e.target.value)}
                            className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#148eff]/50 transition-colors"
                        >
                            <option value="margin-desc" className="bg-[#1a1c23]">Höchste Marge</option>
                            <option value="margin-asc" className="bg-[#1a1c23]">Niedrigste Marge</option>
                            <option value="name-asc" className="bg-[#1a1c23]">Name (A-Z)</option>
                        </select>
                        <div className="relative flex-1 md:w-72">
                            <ItemSearchAsync
                                apiUrl={apiUrl}
                                placeholder="Rezept / Endprodukt suchen..."
                                onSelect={handleAddRecipeSelect}
                            />
                        </div>
                    </div>
                )}
            </div>

            {/* Tabs */}
            <div className="flex border-b border-white/5 bg-black/20">
                <button
                    onClick={() => setActiveTab('profit')}
                    className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'profit' ? 'border-[#148eff] text-white' : 'border-transparent text-white/40 hover:text-white/70'}`}
                >
                    📈 Gewinnrechner
                </button>
                <button
                    onClick={() => setActiveTab('shopping')}
                    className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'shopping' ? 'border-[#148eff] text-white' : 'border-transparent text-white/40 hover:text-white/70'}`}
                >
                    🛒 Einkaufsliste
                    {plannedRecipeList.length > 0 && (
                        <span className="bg-[#148eff] text-white text-[10px] px-2 py-0.5 rounded-full font-bold">
                            {plannedRecipeList.length}
                        </span>
                    )}
                </button>
            </div>

            {/* Content Body */}
            <div className="p-6 flex-1 overflow-auto">
                {isLoading ? (
                    <div className="h-48 flex items-center justify-center">
                        <Loader2 className="w-8 h-8 text-[#148eff] animate-spin" />
                    </div>
                ) : activeTab === 'profit' ? (
                    /* PROFIT CALCULATOR TAB */
                    recipes.length === 0 ? (
                        <div className="h-48 flex flex-col items-center justify-center text-white/40">
                            <TrendingUp className="w-12 h-12 mb-3 opacity-50" />
                            <p className="text-sm">Noch keine Rezepte verfolgt.</p>
                            <p className="text-xs mt-1">Rezept oder Endprodukt oben suchen, um den Profit zu verfolgen.</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                            {sortedRecipes.map(recipe => (
                                <div key={recipe.id} className="bg-white/5 rounded-xl border border-white/10 overflow-hidden flex flex-col group relative">
                                    <button
                                        onClick={() => deleteRecipe(recipe.id)}
                                        className="absolute top-3 right-3 p-1.5 bg-black/40 hover:bg-red-500/20 text-white/40 hover:text-red-400 rounded-lg transition-colors z-10 disabled:opacity-50"
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
                                            <h3 className="font-semibold text-white/90 text-sm leading-tight group-hover:text-[#148eff] transition-colors pr-6">
                                                {recipe.name}
                                            </h3>
                                            <div className="flex items-center gap-1.5 mt-1">
                                                <span className="text-xs font-medium text-[#148eff]">{formatGold(recipe.target_price)}</span>
                                                <span className="text-[10px] text-white/40 uppercase tracking-wide px-1.5 py-0.5 rounded-sm bg-white/5 border border-white/10">Ausbeute: {recipe.crafted_quantity}</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Reagents */}
                                    <div className="p-4 flex-1 flex flex-col">
                                        <h4 className="text-[10px] items-center gap-1 text-white/50 uppercase tracking-widest font-semibold mb-3 flex">
                                            Reagenzien <ArrowRight className="w-3 h-3" />
                                        </h4>
                                        <div className="space-y-2 flex-1">
                                            {recipe.reagents.map(reg => (
                                                <div key={reg.item_id} className="flex justify-between items-center text-xs group/reg">
                                                    <span className="text-white/70 truncate mr-2" title={reg.name}>
                                                        {reg.quantity}x {reg.name}
                                                    </span>
                                                    <div className="flex items-center gap-2">
                                                        <span className="text-white/50 shrink-0 tabular-nums">
                                                            {formatGold(reg.total_price)}
                                                        </span>
                                                        <button
                                                            onClick={async () => {
                                                                try {
                                                                    const res = await fetch(`${apiUrl}/api/recipes/${recipe.id}/reagents/${reg.item_id}`, { method: 'DELETE' });
                                                                    if (res.ok) fetchRecipes();
                                                                } catch (e) { console.error(e); }
                                                            }}
                                                            className="opacity-0 group-hover/reg:opacity-100 text-red-400 hover:text-red-300 transition-opacity"
                                                            title="Reagenz entfernen"
                                                        >
                                                            <Trash2 className="w-3 h-3" />
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}

                                            {/* Add Reagent Form */}
                                            <div className="mt-3 flex gap-1.5 items-center bg-black/20 p-1.5 rounded-lg border border-white/5">
                                                <input id={`qty-${recipe.id}`} type="number" placeholder="Menge" min="1" defaultValue="1" className="w-16 bg-white/5 border border-white/10 rounded-md px-2 py-1.5 text-xs text-white focus:outline-none" />
                                                <ItemSearchAsync
                                                    apiUrl={apiUrl}
                                                    placeholder="Reagenz suchen..."
                                                    className="flex-1 min-w-0"
                                                    onSelect={async (itemId) => {
                                                        const qtyInput = document.getElementById(`qty-${recipe.id}`);
                                                        const qty = parseInt(qtyInput.value, 10) || 1;

                                                        try {
                                                            const res = await fetch(`${apiUrl}/api/recipes/${recipe.id}/reagents`, {
                                                                method: 'POST',
                                                                headers: { 'Content-Type': 'application/json' },
                                                                body: JSON.stringify({ item_id: itemId, quantity: qty })
                                                            });
                                                            if (res.ok) {
                                                                qtyInput.value = "1";
                                                                fetchRecipes();
                                                            } else {
                                                                const errData = await res.json();
                                                                alert(`Fehler: ${errData.detail || 'Konnte Reagenz nicht hinzufügen.'}`);
                                                            }
                                                        } catch (err) {
                                                            console.error(err);
                                                            alert("Netzwerkfehler beim Hinzufügen.");
                                                        }
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Planned Quantity Selector */}
                                    <div className="px-4 pb-3 pt-2 flex items-center justify-between border-t border-white/5 bg-black/10">
                                        <span className="text-[10px] text-white/50 uppercase tracking-widest font-semibold flex items-center gap-1">
                                            <ShoppingCart className="w-3 h-3 text-[#148eff]" /> Für Einkaufsliste:
                                        </span>
                                        <div className="flex items-center gap-1.5 bg-black/40 rounded border border-white/10 px-1 py-0.5">
                                            <button 
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    updatePlannedQty(recipe.id, Math.max(0, (plannedQuantities[recipe.id] || 0) - 1));
                                                }}
                                                className="text-white/60 hover:text-white text-xs px-1.5 py-0.5 hover:bg-white/5 rounded"
                                            >
                                                -
                                            </button>
                                            <span className="text-xs font-semibold text-white px-1.5 min-w-[20px] text-center">
                                                {plannedQuantities[recipe.id] || 0}
                                            </span>
                                            <button 
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    updatePlannedQty(recipe.id, (plannedQuantities[recipe.id] || 0) + 1);
                                                }}
                                                className="text-white/60 hover:text-white text-xs px-1.5 py-0.5 hover:bg-white/5 rounded"
                                            >
                                                +
                                            </button>
                                        </div>
                                    </div>

                                    {/* Profit Footer */}
                                    <div className="p-4 border-t border-white/5 bg-black/20 flex justify-between items-center">
                                        <div className="flex flex-col">
                                            <span className="text-[10px] text-white/40 uppercase tracking-widest font-semibold">Gesamtkosten</span>
                                            <span className="text-sm font-medium text-white/70">{formatGold(recipe.total_cost)}</span>
                                        </div>
                                        <div className="flex flex-col items-end">
                                            <span className="text-[10px] text-white/40 uppercase tracking-widest font-semibold">Marge</span>
                                            <div className={`flex items-center gap-1 text-lg font-bold ${recipe.profit > 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                {recipe.profit > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                                                {formatGold(recipe.profit)}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )
                ) : (
                    /* SHOPPING LIST TAB */
                    plannedRecipeList.length === 0 ? (
                        <div className="h-48 flex flex-col items-center justify-center text-white/40">
                            <ShoppingCart className="w-12 h-12 mb-3 opacity-50" />
                            <p className="text-sm">Deine Einkaufsliste ist leer.</p>
                            <p className="text-xs mt-1">Gehe zum Gewinnrechner und plane Herstellungs-Mengen für Rezepte ein.</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                            {/* Left: Planned Recipes list */}
                            <div className="lg:col-span-1 space-y-4">
                                <div className="flex justify-between items-center">
                                    <h3 className="text-sm font-semibold uppercase tracking-wider text-white/60">Geplante Rezepte</h3>
                                    <button 
                                        onClick={clearShoppingList}
                                        className="text-xs text-red-400 hover:text-red-300 transition-colors flex items-center gap-1"
                                    >
                                        <Trash className="w-3.5 h-3.5" /> Liste leeren
                                    </button>
                                </div>

                                <div className="space-y-3">
                                    {plannedRecipeList.map(recipe => (
                                        <div key={recipe.id} className="bg-white/5 border border-white/10 rounded-xl p-4 flex justify-between items-center gap-4">
                                            <div className="flex items-center gap-3 truncate">
                                                {recipe.icon_url ? (
                                                    <img src={recipe.icon_url} alt="" className="w-8 h-8 rounded border border-white/10" />
                                                ) : (
                                                    <div className="w-8 h-8 rounded bg-white/10 border border-white/10 flex items-center justify-center">
                                                        <span className="text-[10px] text-white/40">?</span>
                                                    </div>
                                                )}
                                                <div className="truncate">
                                                    <h4 className="text-sm font-medium text-white truncate">{recipe.name}</h4>
                                                    <span className="text-[10px] text-white/40">Ausbeute: {recipe.crafted_quantity} pro Craft</span>
                                                </div>
                                            </div>

                                            {/* Quantity adjustment */}
                                            <div className="flex items-center gap-1.5 bg-black/40 rounded border border-white/10 px-1 py-0.5 shrink-0">
                                                <button 
                                                    onClick={() => updatePlannedQty(recipe.id, Math.max(0, (plannedQuantities[recipe.id] || 0) - 1))}
                                                    className="text-white/60 hover:text-white text-xs px-1.5 py-0.5 hover:bg-white/5 rounded"
                                                >
                                                    -
                                                </button>
                                                <span className="text-xs font-semibold text-white px-1 text-center min-w-[16px]">
                                                    {plannedQuantities[recipe.id]}
                                                </span>
                                                <button 
                                                    onClick={() => updatePlannedQty(recipe.id, (plannedQuantities[recipe.id] || 0) + 1)}
                                                    className="text-white/60 hover:text-white text-xs px-1.5 py-0.5 hover:bg-white/5 rounded"
                                                >
                                                    +
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Right: Consolidated Reagents Checklist */}
                            <div className="lg:col-span-2 space-y-4">
                                <h3 className="text-sm font-semibold uppercase tracking-wider text-white/60">Benötigte Reagenzien (Konsolidiert)</h3>
                                
                                <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                                    <div className="divide-y divide-white/5">
                                        {consolidatedList.map(item => {
                                            const isChecked = !!checkedReagents[item.item_id];
                                            return (
                                                <div 
                                                    key={item.item_id}
                                                    onClick={() => toggleReagentCheck(item.item_id)}
                                                    className={`p-4 flex justify-between items-center gap-4 cursor-pointer transition-colors hover:bg-white/[0.02] ${isChecked ? 'opacity-40 line-through bg-white/[0.01]' : ''}`}
                                                >
                                                    <div className="flex items-center gap-3">
                                                        <button className="text-[#148eff] shrink-0">
                                                            {isChecked ? (
                                                                <CheckSquare className="w-5 h-5" />
                                                            ) : (
                                                                <Square className="w-5 h-5 text-white/20 hover:text-white/40" />
                                                            )}
                                                        </button>
                                                        <span className="text-sm font-medium text-white">{item.quantity}x {item.name}</span>
                                                    </div>
                                                    <span className="text-xs text-white/40 tabular-nums">AH-Schätzung: {formatGold(item.total_price)}</span>
                                                </div>
                                            );
                                        })}
                                    </div>

                                    {/* Summary Footer */}
                                    <div className="p-4 bg-black/20 border-t border-white/5 flex justify-between items-center text-sm font-semibold text-white/80">
                                        <span>Gesamteinkaufswert (ca.):</span>
                                        <span className="text-[#148eff]">
                                            {formatGold(consolidatedList.reduce((sum, item) => sum + (checkedReagents[item.item_id] ? 0 : item.total_price), 0))}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )
                )}
            </div>
        </div>
    );
}
