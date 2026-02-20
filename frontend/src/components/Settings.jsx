/**
 * Settings.jsx
 * 
 * Renders the Battle.net integration controls and application settings.
 * Displays connection status and handles manual/automatic sync triggers.
 */
import React from 'react';
import { Shield, RefreshCw, LogOut } from 'lucide-react';

const Settings = ({ onLogin, characters, loading }) => {
    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <div className="bg-surface border border-white/5 rounded-2xl p-6">
                <h2 className="text-xl font-medium text-white mb-4 flex items-center gap-2">
                    <Shield size={20} className="text-primary" />
                    Battle.net Integration
                </h2>

                <div className="bg-surface-dark border border-white/5 rounded-xl p-4 mb-6">
                    <div className="flex justify-between items-center">
                        <div>
                            <p className="text-white font-medium">Connection Status</p>
                            <p className="text-sm text-secondary mt-1">
                                {characters.length > 0
                                    ? `Connected (${characters.length} characters synced)`
                                    : 'Not connected'}
                            </p>
                        </div>
                        <div className={`w-3 h-3 rounded-full ${characters.length > 0 ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.4)]' : 'bg-red-500'}`} />
                    </div>
                </div>

                <div className="flex flex-col gap-3">
                    <button
                        onClick={onLogin}
                        disabled={loading}
                        className="w-full bg-[#148eff] hover:bg-[#0074e0] text-white px-4 py-3 rounded-xl font-medium transition-all shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading && characters.length === 0 ? (
                            <>
                                <RefreshCw size={18} className="animate-spin" />
                                Syncing from Battle.net...
                            </>
                        ) : characters.length > 0 ? (
                            <>
                                <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
                                {loading ? "Syncing..." : "Sync Data from Battle.net"}
                            </>
                        ) : (
                            <>
                                <Shield size={18} />
                                Connect Battle.net Account
                            </>
                        )}
                    </button>

                    {characters.length > 0 && (
                        <p className="text-center text-xs text-secondary/50 mt-2">
                            Last sync: Just now (Auto-syncs every minute)
                        </p>
                    )}
                </div>
            </div>

            <div className="bg-surface border border-white/5 rounded-2xl p-6 opacity-50 pointer-events-none grayscale">
                <h2 className="text-xl font-medium text-white mb-4">Application Settings</h2>
                <div className="space-y-4">
                    <div className="flex justify-between items-center p-3 bg-surface-dark rounded-lg border border-white/5">
                        <span className="text-secondary">Dark Mode</span>
                        <div className="w-10 h-5 bg-primary/20 rounded-full relative"><div className="absolute right-1 top-1 w-3 h-3 bg-primary rounded-full" /></div>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-surface-dark rounded-lg border border-white/5">
                        <span className="text-secondary">Notifications</span>
                        <div className="w-10 h-5 bg-white/10 rounded-full relative"><div className="absolute left-1 top-1 w-3 h-3 bg-white/50 rounded-full" /></div>
                    </div>
                </div>
                <p className="text-center text-xs text-secondary/30 mt-4">Coming Soon</p>
            </div>
        </div>
    );
};

export default Settings;
