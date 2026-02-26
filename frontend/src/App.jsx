/**
 * App.jsx
 * 
 * Main application component for RealmGuardian.
 * Orchestrates API communication for WoW tokens and user characters, manages
 * the global active tab state, and incorporates an automatic background polling
 * mechanism to refresh the UI seamlessly after a successful Battle.net login.
 * 
 * [2026-02-25T14:15:00] STATUS: WORKING (v.0.5.2)
 * - OAuth Redirect logic verified
 * - Polling waits correctly up to 90s for character background sync to finish
 * - CharacterList properly parses and renders equipment JSON and item level
 * - CharacterList properly parses and renders profession JSON and skill points
 * - Removed deprecated playtime rendering
 * DO NOT BREAK THIS BASE FUNCTIONALITY.
 */
import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import TokenWidget from './components/TokenWidget';
import GoldWidget from './components/GoldWidget';
import WatchlistWidget from './components/WatchlistWidget';
import GoldChartWidget from './components/GoldChartWidget';
import CraftingWidget from './components/CraftingWidget';

import CharacterList from './components/CharacterList';
import Settings from './components/Settings';

function App() {
  const [tokenData, setTokenData] = useState(null);
  const [tokenHistory, setTokenHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [range, setRange] = useState('24h');

  // Character Data State
  const [characterData, setCharacterData] = useState(null);
  const [accountGoldHistory, setAccountGoldHistory] = useState([]);
  const [charLoading, setCharLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isSyncing, setIsSyncing] = useState(false);

  // Use relative path for API, handled by Vite proxy in dev (or Nginx in prod)
  // This allows remote access (e.g. from 100.x.x.x) to work, as the browser talks to Vite, 
  // and Vite talks to the local backend.
  const getApiUrl = () => '';

  const fetchTokenData = React.useCallback(async () => {
    try {
      const apiUrl = getApiUrl();
      const latestRes = await fetch(`${apiUrl}/api/token/latest`);
      const latest = await latestRes.json();
      const historyRes = await fetch(`${apiUrl}/api/token/history?range=${range}`);
      const history = await historyRes.json();

      setTokenData(latest);
      setTokenHistory(history);
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch data", error);
      setError(error.message);
      setLoading(false);
    }
  }, [range]);

  const fetchCharacterData = React.useCallback(async () => {
    setCharLoading(true);
    try {
      const apiUrl = getApiUrl();
      const res = await fetch(`${apiUrl}/api/user/characters`);
      if (res.ok) {
        const json = await res.json();
        setCharacterData(json);
      } else {
        setCharacterData(null);
      }
    } catch (e) {
      console.error("Failed to fetch characters", e);
      setCharacterData(null);
    } finally {
      setCharLoading(false);
    }
  }, []);

  const fetchAccountGoldHistory = React.useCallback(async () => {
    try {
      const apiUrl = getApiUrl();
      const res = await fetch(`${apiUrl}/api/user/gold-history`);
      if (res.ok) {
        const json = await res.json();
        setAccountGoldHistory(json.history || []);
      }
    } catch (e) {
      console.error("Failed to fetch gold history", e);
    }
  }, []);

  const handleLogin = () => {
    console.log("LOGIN BUTTON CLICKED. Redirecting...", activeTab);
    // Force absolute URL to ensure we hit the backend and not the frontend router
    // This allows login to work on localhost even if the proxy is misconfigured
    window.location.href = `http://localhost:8000/api/auth/login?tab=${activeTab}`;
  };

  useEffect(() => {
    fetchTokenData();
    fetchCharacterData();
    fetchAccountGoldHistory();
  }, [fetchTokenData, fetchCharacterData, fetchAccountGoldHistory]);

  useEffect(() => {
    const interval = setInterval(fetchTokenData, 60000);
    return () => clearInterval(interval);
  }, [fetchTokenData]);

  useEffect(() => {
    // Check for connected param to trigger immediate refresh
    const params = new URLSearchParams(window.location.search);
    if (params.get('connected')) {
      const tab = params.get('tab');
      if (tab) {
        setActiveTab(tab);
      }
      // Clean URL
      window.history.replaceState({}, document.title, "/");
      setIsSyncing(true);
      fetchCharacterData();
    }
  }, [fetchCharacterData]);

  // Polling mechanism for background sync
  useEffect(() => {
    let pollInterval;
    let timeoutId;

    if (isSyncing) {
      // Poll every 3 seconds
      pollInterval = setInterval(() => {
        fetchCharacterData();
        fetchAccountGoldHistory();
      }, 3000);

      // Stop polling after 90 seconds to ensure all characters are fetched
      timeoutId = setTimeout(() => {
        setIsSyncing(false);
      }, 90000);
    }

    return () => {
      clearInterval(pollInterval);
      clearTimeout(timeoutId);
    };
  }, [isSyncing, fetchCharacterData, fetchAccountGoldHistory]);

  // Sync state will stop naturally after 90s, no early bailout.

  const characters = characterData?.characters || [];

  return (
    <Layout activeTab={activeTab} onTabChange={setActiveTab}>
      {error && (
        <div className="bg-red-500/10 border border-red-500/50 text-red-500 p-4 rounded-xl mb-6">
          Error loading data: {error}. Check if Backend is running at {import.meta.env.VITE_API_URL || 'localhost:8000'}
        </div>
      )}

      {activeTab === 'dashboard' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Token Card */}
          {loading ? (
            <div className="animate-pulse bg-surface h-48 rounded-2xl border border-white/5"></div>
          ) : (
            <TokenWidget
              currentPrice={tokenData?.price || 0}
              lastUpdated={tokenData?.last_updated || 0}
              formatted={tokenData?.formatted || "0g"}
              history={tokenHistory}
              selectedRange={range}
              onRangeChange={setRange}
            />
          )}

          {/* Account / Gold Card */}
          <GoldWidget
            characters={characters}
            loading={charLoading}
          />

          {/* Gold History Card */}
          <GoldChartWidget
            history={accountGoldHistory}
            loading={charLoading}
          />

          <div className="md:col-span-2 lg:col-span-3">
            <WatchlistWidget apiUrl={getApiUrl()} />
          </div>
        </div>
      )}

      {activeTab === 'characters' && (
        <CharacterList
          characters={characters}
          loading={charLoading}
          onLogin={handleLogin}
        />
      )}

      {activeTab === 'crafting' && (
        <CraftingWidget apiUrl={getApiUrl()} />
      )}

      {activeTab === 'settings' && (
        <Settings
          onLogin={handleLogin}
          characters={characters}
          loading={charLoading || isSyncing}
        />
      )}
    </Layout>
  );
}

export default App;
