import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ImagePanel from './components/ImagePanel';
import MetricsCards from './components/MetricsCards';
import InsightsPanel from './components/InsightsPanel';
import './styles.css';

function App() {
    const generateQuarters = () => {
        const quarters = [];
        const currentYear = new Date().getFullYear();

        for (let year = 2015; year <= currentYear; year++) {
            for (let q = 1; q <= 4; q++) {
                const quarterDate = new Date(year, (q - 1) * 3, 1);
                if (quarterDate <= new Date()) {
                    quarters.push(`${year}-Q${q}`);
                }
            }
        }

        return quarters.reverse();
    };

    const [quarters] = useState(generateQuarters());
    const [beforeQuarter, setBeforeQuarter] = useState('');
    const [afterQuarter, setAfterQuarter] = useState('');
    const [beforeDate, setBeforeDate] = useState('');
    const [afterDate, setAfterDate] = useState('');
    const [beforeDates, setBeforeDates] = useState([]);
    const [afterDates, setAfterDates] = useState([]);
    const [loadingBeforeDates, setLoadingBeforeDates] = useState(false);
    const [loadingAfterDates, setLoadingAfterDates] = useState(false);
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState('');
    const [error, setError] = useState('');
    const [results, setResults] = useState(null);

    // MAGIC VERIFICATION BUTTON - Uses known cached dates to bypass connection issues
    const runVerificationTest = async () => {
        // Known valid cached dates
        const testDateBefore = '2022-05-06';
        const testDateAfter = '2024-11-26';

        // Update UI
        setBeforeDate(testDateBefore);
        setAfterDate(testDateAfter);
        setLoading(true);
        setStatus('Running verification with verified local data...');
        setError('');
        setResults(null);
        setProgress(0);

        try {
            console.log('Starting verification job...');
            const response = await axios.post('/api/analyze', {
                date_before: testDateBefore,
                date_after: testDateAfter
            });

            const jobId = response.data.job_id;
            console.log('Verification job ID:', jobId);

            // Start polling (same logic as handleAnalyze)
            const pollInterval = setInterval(async () => {
                try {
                    const statusResponse = await axios.get(`/api/status/${jobId}`);
                    const data = statusResponse.data;
                    setStatus(data.status);
                    setProgress(data.progress || 0);

                    if (data.status === 'completed') {
                        clearInterval(pollInterval);
                        const resultsResponse = await axios.get(`/api/results/${jobId}`);
                        setResults(resultsResponse.data);
                        setLoading(false);
                        setStatus('Verification Complete!');
                    } else if (data.status === 'failed') {
                        clearInterval(pollInterval);
                        setError(data.error || 'Verification failed');
                        setLoading(false);
                    }
                } catch (err) {
                    clearInterval(pollInterval);
                    setError('Error checking status');
                    setLoading(false);
                }
            }, 2000);

        } catch (err) {
            console.error('Verification error:', err);
            setError(err.response?.data?.error || 'Verification failed');
            setLoading(false);
        }
    };

    const fetchDatesForQuarter = async (quarter, setDates, setLoadingDates) => {
        try {
            setLoadingDates(true);
            const response = await axios.get(`/api/available-dates?quarter=${quarter}`);

            if (response.data.success) {
                setDates(response.data.dates);
            } else {
                setError(`Failed to load dates for ${quarter}`);
            }
        } catch (err) {
            console.error('Error fetching dates:', err);
            setError(`Failed to load dates for ${quarter}`);
        } finally {
            setLoadingDates(false);
        }
    };

    useEffect(() => {
        if (beforeQuarter) {
            setBeforeDate('');
            fetchDatesForQuarter(beforeQuarter, setBeforeDates, setLoadingBeforeDates);
        }
    }, [beforeQuarter]);

    useEffect(() => {
        if (afterQuarter) {
            setAfterDate('');
            fetchDatesForQuarter(afterQuarter, setAfterDates, setLoadingAfterDates);
        }
    }, [afterQuarter]);

    const handleAnalyze = async () => {
        if (!beforeDate || !afterDate) {
            setError('Please select both before and after dates');
            return;
        }

        setLoading(true);
        setProgress(0);
        setError('');
        setResults(null);
        setStatus('Starting analysis...');

        try {
            const response = await axios.post('/api/analyze', {
                date_before: beforeDate,
                date_after: afterDate
            });

            const jobId = response.data.job_id;
            console.log('Analysis started, job ID:', jobId);

            const pollInterval = setInterval(async () => {
                try {
                    const statusResponse = await axios.get(`/api/status/${jobId}`);
                    const data = statusResponse.data;

                    console.log('Status update:', data);
                    setStatus(data.status);
                    setProgress(data.progress || 0);

                    if (data.status === 'completed') {
                        clearInterval(pollInterval);
                        setProgress(100);

                        console.log('Analysis completed, fetching results...');
                        const resultsResponse = await axios.get(`/api/results/${jobId}`);
                        console.log('Results received:', resultsResponse.data);

                        setResults(resultsResponse.data);
                        setLoading(false);
                        setStatus('Analysis complete!');
                    } else if (data.status === 'failed') {
                        clearInterval(pollInterval);
                        setError(data.error || 'Analysis failed');
                        setLoading(false);
                    }
                } catch (err) {
                    clearInterval(pollInterval);
                    console.error('Status check error:', err);
                    setError('Error checking status');
                    setLoading(false);
                }
            }, 2000);

        } catch (err) {
            console.error('Analysis error:', err);
            setError(err.response?.data?.error || 'Failed to start analysis');
            setLoading(false);
        }
    };

    return (
        <div className="app">
            <header className="header">
                <div className="logo">🌲 GeoSentinel Forest Watch</div>
                <p className="subtitle">AI-Powered Deforestation Detection using Sentinel-2 Satellite Imagery</p>
            </header>

            <div className="container">
                <div className="input-section">
                    <div className="date-selector-grid">
                        <div className="date-group">
                            <label>BEFORE QUARTER</label>
                            <select
                                value={beforeQuarter}
                                onChange={(e) => setBeforeQuarter(e.target.value)}
                                disabled={loading}
                                className="quarter-select"
                            >
                                <option value="">Select quarter...</option>
                                {quarters.map((q) => (
                                    <option key={`before-q-${q}`} value={q}>{q}</option>
                                ))}
                            </select>
                        </div>

                        <div className="date-group">
                            <label>BEFORE DATE</label>
                            {loadingBeforeDates ? (
                                <div className="loading-dates">Loading...</div>
                            ) : (
                                <select
                                    value={beforeDate}
                                    onChange={(e) => setBeforeDate(e.target.value)}
                                    disabled={loading || !beforeQuarter}
                                    className="date-select"
                                >
                                    <option value="">Select date...</option>
                                    {beforeDates.map((item) => (
                                        <option key={`before-${item.date}`} value={item.date}>
                                            {item.date} ({item.cloud_cover}% cloud)
                                        </option>
                                    ))}
                                </select>
                            )}
                        </div>

                        <div className="date-group">
                            <label>AFTER QUARTER</label>
                            <select
                                value={afterQuarter}
                                onChange={(e) => setAfterQuarter(e.target.value)}
                                disabled={loading}
                                className="quarter-select"
                            >
                                <option value="">Select quarter...</option>
                                {quarters.map((q) => (
                                    <option key={`after-q-${q}`} value={q}>{q}</option>
                                ))}
                            </select>
                        </div>

                        <div className="date-group">
                            <label>AFTER DATE</label>
                            {loadingAfterDates ? (
                                <div className="loading-dates">Loading...</div>
                            ) : (
                                <select
                                    value={afterDate}
                                    onChange={(e) => setAfterDate(e.target.value)}
                                    disabled={loading || !afterQuarter}
                                    className="date-select"
                                >
                                    <option value="">Select date...</option>
                                    {afterDates.map((item) => (
                                        <option key={`after-${item.date}`} value={item.date}>
                                            {item.date} ({item.cloud_cover}% cloud)
                                        </option>
                                    ))}
                                </select>
                            )}
                        </div>

                        <button
                            className="analyze-btn"
                            onClick={handleAnalyze}
                            disabled={loading || !beforeDate || !afterDate}
                        >
                            {loading ? '⏳ ANALYZING...' : '🔍 ANALYZE DEFORESTATION'}
                        </button>
                    </div>

                    {/* TEST BUTTON FOR MOCK DATA */}
                    <div style={{ marginTop: '20px', textAlign: 'center' }}>
                        <button
                            onClick={runVerificationTest}
                            style={{
                                padding: '12px 24px',
                                background: '#2ecc71',  /* Green for success */
                                border: 'none',
                                borderRadius: '8px',
                                color: 'white',
                                fontWeight: 'bold',
                                cursor: 'pointer',
                                fontSize: '1.1em'
                            }}
                        >
                            🚀 RUN VERIFICATION TEST (LOCAL DATA)
                        </button>
                    </div>

                    {error && <div className="error">❌ {error}</div>}

                    {loading && (
                        <div className="status-container">
                            <div className="status">⚙️ {status}</div>
                            <div className="progress-bar">
                                <div className="progress-fill" style={{ width: `${progress}%` }}>
                                    <span className="progress-text">{progress}%</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {results && (
                    <div className="results-section fade-in">
                        <ImagePanel
                            images={results.images}
                            dates={results.dates}
                        />

                        {results.metrics && <MetricsCards metrics={results.metrics} />}

                        {results.explanation && <InsightsPanel explanation={results.explanation} />}
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
