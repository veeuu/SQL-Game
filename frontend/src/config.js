const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS  = API.replace('https://', 'wss://').replace('http://', 'ws://');

export { API, WS };
