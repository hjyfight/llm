import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title, 
  Tooltip, 
  Legend,
  ArcElement
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { Heart, TrendingUp, BarChart3, Activity, AlertCircle, CheckCircle } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [text, setText] = useState('');
  const [userId, setUserId] = useState('default_user');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [assessment, setAssessment] = useState(null);
  const [activeTab, setActiveTab] = useState('analyze');
  const [error, setError] = useState(null);

  useEffect(() => {
    if (activeTab === 'history') {
      fetchHistory();
    } else if (activeTab === 'stats') {
      fetchStats();
    } else if (activeTab === 'assessment') {
      fetchAssessment();
    }
  }, [activeTab]);

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/sentiment/history/${userId}`);
      setHistory(response.data);
    } catch (err) {
      console.error('获取历史失败:', err);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/sentiment/stats/${userId}`);
      setStats(response.data);
    } catch (err) {
      console.error('获取统计失败:', err);
    }
  };

  const fetchAssessment = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health/assessment/${userId}`);
      setAssessment(response.data);
    } catch (err) {
      console.error('获取评估失败:', err);
    }
  };

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError('请输入要分析的文本');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/sentiment/analyze`, {
        text: text,
        user_id: userId
      });
      setResult(response.data);
      setText('');
    } catch (err) {
      setError(err.response?.data?.detail || '分析失败，请检查后端服务是否启动');
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '#28a745';
      case 'negative': return '#dc3545';
      default: return '#17a2b8';
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'low': return '#28a745';
      case 'medium': return '#ffc107';
      case 'high': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
  };

  const renderAnalyzeTab = () => (
    <>
      <div className="card">
        <h2>💭 情感分析</h2>
        <div className="input-section">
          <label>输入你的文本（日记、想法、心情等）：</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="例如：今天的工作压力很大，感觉有点焦虑和疲惫。虽然完成了任务，但总觉得不够好..."
          />
        </div>
        <button 
          className="button" 
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading ? '分析中...' : '开始分析'}
        </button>

        {error && (
          <div className="error-message">
            <AlertCircle size={20} style={{ verticalAlign: 'middle', marginRight: '8px' }} />
            {error}
          </div>
        )}

        {result && (
          <div className="result-section">
            <h3 style={{ marginBottom: '15px', color: '#333' }}>分析结果</h3>
            
            <div style={{ marginBottom: '15px' }}>
              <strong>情感分类：</strong>
              <span className={`sentiment-badge sentiment-${result.sentiment}`}>
                {result.sentiment === 'positive' ? '积极' : 
                 result.sentiment === 'negative' ? '消极' : '中性'}
              </span>
              <span style={{ color: '#666', fontSize: '0.9rem' }}>
                (置信度: {(result.confidence * 100).toFixed(1)}%)
              </span>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <strong>情感强度：</strong>
              <div style={{ 
                width: '100%', 
                height: '20px', 
                background: '#e0e0e0', 
                borderRadius: '10px',
                overflow: 'hidden',
                marginTop: '8px'
              }}>
                <div style={{
                  width: `${result.intensity * 100}%`,
                  height: '100%',
                  background: getSentimentColor(result.sentiment),
                  transition: 'width 0.5s'
                }} />
              </div>
              <span style={{ fontSize: '0.9rem', color: '#666' }}>
                {(result.intensity * 100).toFixed(1)}%
              </span>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <strong>识别的情绪：</strong>
              <div className="emotions-list">
                {result.emotions.map((emotion, index) => (
                  <div key={index} className="emotion-tag">
                    {emotion.name}
                    <div className="intensity-bar">
                      <div 
                        className="intensity-fill" 
                        style={{ width: `${emotion.intensity * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <strong>详细分析：</strong>
              <div className="analysis-text">{result.analysis}</div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <strong>可能的原因：</strong>
              <div className="analysis-text">{result.causes}</div>
            </div>

            <div>
              <strong>个性化建议：</strong>
              <div className="suggestions-box">{result.suggestions}</div>
            </div>
          </div>
        )}
      </div>
    </>
  );

  const renderHistoryTab = () => (
    <div className="card">
      <h2>📝 情感历史</h2>
      {history.length === 0 ? (
        <div className="empty-state">
          <Activity size={48} />
          <p>还没有历史记录</p>
        </div>
      ) : (
        <div className="history-list">
          {history.map((item) => (
            <div key={item.id} className="history-item">
              <div className="history-date">{formatDate(item.created_at)}</div>
              <div className="history-text">{item.text}</div>
              <div>
                <span className={`sentiment-badge sentiment-${item.sentiment}`}>
                  {item.sentiment === 'positive' ? '积极' : 
                   item.sentiment === 'negative' ? '消极' : '中性'}
                </span>
                {JSON.parse(item.emotions).slice(0, 3).map((emotion, idx) => (
                  <span key={idx} style={{ 
                    marginLeft: '8px', 
                    fontSize: '0.85rem', 
                    color: '#666' 
                  }}>
                    {emotion.name}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderStatsTab = () => {
    if (!stats) return <div className="card"><div className="loading">加载中...</div></div>;

    const sentimentData = {
      labels: ['积极', '中性', '消极'],
      datasets: [{
        data: [stats.positive_count, stats.neutral_count, stats.negative_count],
        backgroundColor: ['#28a745', '#17a2b8', '#dc3545'],
      }]
    };

    const trendData = {
      labels: stats.trends.map(t => t.date),
      datasets: [{
        label: '情感得分',
        data: stats.trends.map(t => t.sentiment_score),
        borderColor: '#667eea',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        tension: 0.4,
        fill: true,
      }]
    };

    return (
      <div className="card">
        <h2>📊 情感统计</h2>
        
        <div className="stats-grid">
          <div className="stat-box">
            <div className="stat-value">{stats.total_records}</div>
            <div className="stat-label">总记录数</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{(stats.average_intensity * 100).toFixed(0)}%</div>
            <div className="stat-label">平均情感强度</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{stats.positive_count}</div>
            <div className="stat-label">积极情感</div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{stats.negative_count}</div>
            <div className="stat-label">消极情感</div>
          </div>
        </div>

        <div className="chart-container">
          <h3 style={{ marginBottom: '15px', color: '#333' }}>情感分布</h3>
          <div style={{ maxWidth: '300px', margin: '0 auto' }}>
            <Doughnut data={sentimentData} />
          </div>
        </div>

        {stats.trends.length > 0 && (
          <div className="chart-container">
            <h3 style={{ marginBottom: '15px', color: '#333' }}>情感趋势</h3>
            <Line data={trendData} options={{
              responsive: true,
              plugins: {
                legend: { display: false }
              },
              scales: {
                y: {
                  min: -1,
                  max: 1,
                  ticks: {
                    callback: function(value) {
                      if (value === 1) return '积极';
                      if (value === 0) return '中性';
                      if (value === -1) return '消极';
                      return value;
                    }
                  }
                }
              }
            }} />
          </div>
        )}

        <div style={{ marginTop: '20px' }}>
          <h3 style={{ marginBottom: '15px', color: '#333' }}>最常见的情绪</h3>
          <div className="emotions-list">
            {stats.most_common_emotions.map((emotion, index) => (
              <div key={index} className="emotion-tag">
                {emotion.name}
                <div className="intensity-bar">
                  <div 
                    className="intensity-fill" 
                    style={{ width: `${emotion.intensity * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderAssessmentTab = () => {
    if (!assessment) return <div className="card"><div className="loading">加载中...</div></div>;

    return (
      <div className="card">
        <h2>🏥 心理健康评估</h2>
        
        <div className="assessment-card">
          <div style={{ textAlign: 'center', marginBottom: '30px' }}>
            <div style={{ 
              fontSize: '4rem', 
              fontWeight: '700', 
              color: getRiskColor(assessment.risk_level),
              marginBottom: '10px'
            }}>
              {assessment.overall_score}
            </div>
            <div style={{ fontSize: '1.2rem', color: '#666' }}>
              总体健康得分
              <span className={`risk-badge risk-${assessment.risk_level}`}>
                {assessment.risk_level === 'low' ? '低风险' : 
                 assessment.risk_level === 'medium' ? '中等风险' : '高风险'}
              </span>
            </div>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ marginBottom: '10px', color: '#333' }}>
              <AlertCircle size={20} style={{ verticalAlign: 'middle', marginRight: '8px' }} />
              主要关注点
            </h3>
            <ul className="concerns-list">
              {assessment.key_concerns.map((concern, index) => (
                <li key={index}>{concern}</li>
              ))}
            </ul>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ marginBottom: '10px', color: '#333' }}>
              <CheckCircle size={20} style={{ verticalAlign: 'middle', marginRight: '8px' }} />
              改善建议
            </h3>
            <ul className="recommendations-list">
              {assessment.recommendations.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </div>

          <div>
            <h3 style={{ marginBottom: '10px', color: '#333' }}>详细分析</h3>
            <div className="analysis-text" style={{ lineHeight: '1.8' }}>
              {assessment.detailed_analysis}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="app">
      <div className="container">
        <div className="header">
          <h1>
            <Heart size={40} style={{ verticalAlign: 'middle', marginRight: '10px' }} />
            智能情感分析与心理健康辅助系统
          </h1>
          <p>基于大语言模型的多维度情感分析平台</p>
        </div>

        <div className="tab-container">
          <div className="tabs">
            <button 
              className={`tab ${activeTab === 'analyze' ? 'active' : ''}`}
              onClick={() => setActiveTab('analyze')}
            >
              💭 情感分析
            </button>
            <button 
              className={`tab ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              📝 历史记录
            </button>
            <button 
              className={`tab ${activeTab === 'stats' ? 'active' : ''}`}
              onClick={() => setActiveTab('stats')}
            >
              📊 统计分析
            </button>
            <button 
              className={`tab ${activeTab === 'assessment' ? 'active' : ''}`}
              onClick={() => setActiveTab('assessment')}
            >
              🏥 健康评估
            </button>
          </div>
        </div>

        <div className="main-content" style={{ gridTemplateColumns: '1fr' }}>
          {activeTab === 'analyze' && renderAnalyzeTab()}
          {activeTab === 'history' && renderHistoryTab()}
          {activeTab === 'stats' && renderStatsTab()}
          {activeTab === 'assessment' && renderAssessmentTab()}
        </div>

        <div style={{ 
          textAlign: 'center', 
          color: 'white', 
          marginTop: '40px', 
          opacity: '0.8',
          fontSize: '0.9rem'
        }}>
          <p>💡 本系统仅供参考，不能替代专业心理咨询。如需帮助请联系专业机构。</p>
          <p style={{ marginTop: '10px' }}>
            全国心理援助热线：<strong>400-161-9995</strong>
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
