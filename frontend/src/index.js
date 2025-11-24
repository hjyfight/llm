import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// 导入新的面向对象应用
import app from './app';

// 初始化面向对象应用
async function initializeApp() {
  try {
    await app.initialize();
    console.log('面向对象应用初始化完成');
  } catch (error) {
    console.error('应用初始化失败:', error);
  }
}

// 渲染React应用
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// 初始化面向对象架构
initializeApp();

// 将应用实例暴露到全局（便于调试）
window.app = app;