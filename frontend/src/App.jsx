import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import TokenWidget from './components/TokenWidget';
import GoldWidget from './components/GoldWidget';
import WatchlistWidget from './components/WatchlistWidget';

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
  const [charLoading, setCharLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');

  // Helper to ensure we use the same API URL logic
  const getApiUrl = () => import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchTokenData = React.useCallback(async () => {
    try {
      let apiUrl = getApiUrl();
      let latestRes;
      try {
        latestRes = await fetch(`${apiUrl}/api/token/latest`);
      } catch {
        console.warn("Main API URL failed, trying localhost...");
        apiUrl = 'http://localhost:8000';
        latestRes = await fetch(`${apiUrl}/api/token/latest`);
      }

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

  const handleLogin = () => {
    const url = getApiUrl();
    console.log("Redirecting to:", `${url}/api/auth/login`);
    window.location.href = `${url}/api/auth/login`;
  };

  useEffect(() => {
    fetchTokenData();
    fetchCharacterData();
  }, [fetchTokenData, fetchCharacterData]);

  useEffect(() => {
    const interval = setInterval(fetchTokenData, 60000);
    return () => clearInterval(interval);
  }, [fetchTokenData]);

  useEffect(() => {
    // Check for connected param to trigger immediate refresh
    const params = new URLSearchParams(window.location.search);
    if (params.get('connected')) {
      // Clean URL
      window.history.replaceState({}, document.title, "/");
      fetchCharacterData();
    }
  }, [fetchCharacterData]);

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

          <WatchlistWidget apiUrl={import.meta.env.VITE_API_URL || 'http://localhost:8000'} />
        </div>
      )}

      {activeTab === 'characters' && (
        <CharacterList
          characters={characters}
          loading={charLoading}
          onLogin={handleLogin}
        />
      )}

      {activeTab === 'settings' && (
        <Settings
          onLogin={handleLogin}
          characters={characters}
          loading={charLoading}
        />
      )}
    </Layout>
  );
}

export default App;
