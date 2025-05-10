import AsyncStorage from '@react-native-async-storage/async-storage';

// API URL helpers
export const getApiUrl = async () => {
  const url = await AsyncStorage.getItem('apiUrl');
  return url || 'http://default-api-url.com';
};

export const setApiUrl = async (url) => {
  await AsyncStorage.setItem('apiUrl', url);
};

// API functions
export const fetchSymbols = async () => {
  const baseUrl = await getApiUrl();
  const res = await fetch(`${baseUrl}/symbols`);
  return res.json();
};

export const toggleSymbol = async (symbol) => {
  const baseUrl = await getApiUrl();
  const res = await fetch(`${baseUrl}/symbols/${symbol}`, { method: 'PATCH' });
  return res.json();
};

export const deleteSymbol = async (symbol) => {
  const baseUrl = await getApiUrl();
  const res = await fetch(`${baseUrl}/symbols/${symbol}`, { method: 'DELETE' });
  return res.json();
};

export const addSymbol = async (symbol) => {
  const baseUrl = await getApiUrl();
  const res = await fetch(`${baseUrl}/symbols`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(symbol),
  });
  return res.json();
};

export const fetchEquityCurve = async () => {
  const baseUrl = await getApiUrl();
  const res = await fetch(`${baseUrl}/equity_curve`);
  return res.json();
};

export const fetchOpenTrades = async () => {
  const baseUrl = await getApiUrl();
  const res = await fetch(`${baseUrl}/open_trades`);
  return res.json();
};

export const fetchNewsEvents = async (symbol) => {
  const baseUrl = await getApiUrl();
  const res = await fetch(`${baseUrl}/symbols/${symbol}/news`);
  return res.json();
};

export const addNewsEvent = async (symbol, event) => {
  const baseUrl = await getApiUrl();
  const res = await fetch(`${baseUrl}/symbols/${symbol}/news`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(event),
  });
  return res.json();
};

export const deleteNewsEvent = async (symbol, id) => {
  const baseUrl = await getApiUrl();
  const res = await fetch(`${baseUrl}/symbols/${symbol}/news/${id}`, { method: 'DELETE' });
  return res.json();
};
