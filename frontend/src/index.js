import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import sentimentApp from './SentimentAnalysisApp';

async function initializeApp() {
  try {
    await sentimentApp.initialize();
    console.log('面向对象应用初始化完成');
  } catch (error) {
    console.error('应用初始化失败:', error);
  }
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

initializeApp();

if (typeof window !== 'undefined') {
  window.app = sentimentApp;
}
