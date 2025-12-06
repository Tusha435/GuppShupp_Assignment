import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';   // ✅ use App_with_auth, not App
import { disableConsoleInProduction, preventCredentialLogging } from './utils/security';

// Enable security features
disableConsoleInProduction();
preventCredentialLogging();

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
