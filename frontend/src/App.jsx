import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import TokenWidget from './components/TokenWidget';
import WatchlistWidget from './components/WatchlistWidget';

function App() {
  const [tokenData, setTokenData] = useState(null);
  const [tokenHistory, setTokenHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [range, setRange] = useState('24h');

  const fetchTokenData = async () => {
    try {
      let apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

      // If we are on the same machine, try localhost first if the IP fails, or just default to localhost for now to fix the immediate issue.
      // Actually, let's just force localhost for this test if the user is on the server.
      // But better: try-catch the fetch.

      let latestRes;
      try {
        latestRes = await fetch(`${apiUrl}/api/token/latest`);
      } catch (e) {
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
  };

  useEffect(() => {
    fetchTokenData();
  }, [range]); // Re-fetch when range changes

  useEffect(() => {
    const interval = setInterval(fetchTokenData, 60000); // Poll every minute
    return () => clearInterval(interval);
  }, [range]);

  return (
    <Layout>
      {error && (
        <div className="bg-red-500/10 border border-red-500/50 text-red-500 p-4 rounded-xl mb-6">
          Error loading data: {error}. Check if Backend is running at {import.meta.env.VITE_API_URL || 'localhost:8000'}
        </div>
      )}
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

        {/* Placeholder for Watchlist */}
        <div className="bg-surface border border-white/5 rounded-2xl p-6 md:col-span-2">
          <h3 className="text-secondary text-sm font-medium uppercase tracking-wider mb-4">Market Watchlist</h3>
          <div className="flex flex-col items-center justify-center h-32 text-secondary/50 border-2 border-dashed border-white/5 rounded-xl">
            <span>No items tracked yet</span>
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default App;
