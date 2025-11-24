/**
 * UI组件基类和具体实现
 */

import { IUIComponent, EventManager, AppConfig, DateUtils } from './core';

// ================================
// 基础组件类
// ================================

/**
 * 基础UI组件类
 */
class BaseComponent extends IUIComponent {
    constructor(container, options = {}) {
        super();
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        this.options = options;
        this.eventManager = new EventManager();
        this.isRendered = false;
        this.children = [];
    }
    
    render() {
        if (!this.container) {
            throw new Error('容器元素未找到');
        }
        
        this.beforeRender();
        this.doRender();
        this.afterRender();
        this.isRendered = true;
    }
    
    doRender() {
        // 子类实现具体渲染逻辑
    }
    
    beforeRender() {
        // 渲染前的钩子
    }
    
    afterRender() {
        // 渲染后的钩子
        this.bindEvents();
    }
    
    update(data) {
        this.data = data;
        if (this.isRendered) {
            this.render();
        }
    }
    
    destroy() {
        this.children.forEach(child => child.destroy());
        this.children = [];
        this.eventManager = null;
        this.isRendered = false;
    }
    
    on(event, callback) {
        this.eventManager.on(event, callback);
    }
    
    off(event, callback) {
        this.eventManager.off(event, callback);
    }
    
    emit(event, data) {
        this.eventManager.emit(event, data);
    }
    
    createElement(tag, className = '', innerHTML = '') {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (innerHTML) element.innerHTML = innerHTML;
        return element;
    }
    
    bindEvents() {
        // 子类实现事件绑定
    }
}

// ================================
// 情感分析组件
// ================================

/**
 * 情感分析输入组件
 */
class SentimentInputComponent extends BaseComponent {
    constructor(container, options = {}) {
        super(container, options);
        this.placeholder = options.placeholder || '请输入要分析的情感文本...';
        this.maxLength = options.maxLength || 5000;
    }
    
    doRender() {
        this.container.innerHTML = `
            <div class="sentiment-input-container">
                <div class="input-header">
                    <h3>情感分析</h3>
                    <span class="char-count">0/${this.maxLength}</span>
                </div>
                <textarea 
                    class="sentiment-textarea" 
                    placeholder="${this.placeholder}"
                    maxlength="${this.maxLength}"
                    rows="4"
                ></textarea>
                <div class="input-actions">
                    <button class="analyze-btn" disabled>
                        <span class="btn-text">分析情感</span>
                        <span class="btn-loading" style="display: none;">分析中...</span>
                    </button>
                    <button class="clear-btn">清空</button>
                </div>
            </div>
        `;
        
        this.textarea = this.container.querySelector('.sentiment-textarea');
        this.analyzeBtn = this.container.querySelector('.analyze-btn');
        this.clearBtn = this.container.querySelector('.clear-btn');
        this.charCount = this.container.querySelector('.char-count');
        this.btnText = this.container.querySelector('.btn-text');
        this.btnLoading = this.container.querySelector('.btn-loading');
    }
    
    bindEvents() {
        // 字符计数
        this.textarea.addEventListener('input', (e) => {
            const length = e.target.value.length;
            this.charCount.textContent = `${length}/${this.maxLength}`;
            this.analyzeBtn.disabled = length === 0;
            this.emit('input-change', e.target.value);
        });
        
        // 分析按钮
        this.analyzeBtn.addEventListener('click', () => {
            const text = this.textarea.value.trim();
            if (text) {
                this.setLoading(true);
                this.emit('analyze', text);
            }
        });
        
        // 清空按钮
        this.clearBtn.addEventListener('click', () => {
            this.textarea.value = '';
            this.charCount.textContent = `0/${this.maxLength}`;
            this.analyzeBtn.disabled = true;
            this.emit('clear');
        });
        
        // 回车分析（Ctrl+Enter）
        this.textarea.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                const text = this.textarea.value.trim();
                if (text) {
                    this.setLoading(true);
                    this.emit('analyze', text);
                }
            }
        });
    }
    
    setLoading(loading) {
        this.analyzeBtn.disabled = loading;
        if (loading) {
            this.btnText.style.display = 'none';
            this.btnLoading.style.display = 'inline';
        } else {
            this.btnText.style.display = 'inline';
            this.btnLoading.style.display = 'none';
        }
    }
    
    getText() {
        return this.textarea.value.trim();
    }
    
    clear() {
        this.textarea.value = '';
        this.charCount.textContent = `0/${this.maxLength}`;
        this.analyzeBtn.disabled = true;
    }
}

/**
 * 情感分析结果组件
 */
class SentimentResultComponent extends BaseComponent {
    constructor(container, options = {}) {
        super(container, options);
        this.result = null;
    }
    
    doRender() {
        this.container.innerHTML = `
            <div class="sentiment-result-container" style="display: none;">
                <div class="result-header">
                    <h3>分析结果</h3>
                    <span class="result-time"></span>
                </div>
                
                <div class="sentiment-overview">
                    <div class="sentiment-badge">
                        <span class="sentiment-label"></span>
                        <span class="confidence-badge"></span>
                    </div>
                    <div class="intensity-bar">
                        <span class="intensity-label">情感强度</span>
                        <div class="intensity-progress">
                            <div class="intensity-fill"></div>
                        </div>
                        <span class="intensity-percentage"></span>
                    </div>
                </div>
                
                <div class="emotions-section">
                    <h4>情绪分析</h4>
                    <div class="emotions-list"></div>
                </div>
                
                <div class="analysis-section">
                    <h4>详细分析</h4>
                    <p class="analysis-text"></p>
                </div>
                
                <div class="causes-section">
                    <h4>情感原因</h4>
                    <p class="causes-text"></p>
                </div>
                
                <div class="suggestions-section">
                    <h4>改善建议</h4>
                    <ul class="suggestions-list"></ul>
                </div>
            </div>
        `;
        
        this.resultContainer = this.container.querySelector('.sentiment-result-container');
        this.sentimentLabel = this.container.querySelector('.sentiment-label');
        this.confidenceBadge = this.container.querySelector('.confidence-badge');
        this.intensityFill = this.container.querySelector('.intensity-fill');
        this.intensityPercentage = this.container.querySelector('.intensity-percentage');
        this.emotionsList = this.container.querySelector('.emotions-list');
        this.analysisText = this.container.querySelector('.analysis-text');
        this.causesText = this.container.querySelector('.causes-text');
        this.suggestionsList = this.container.querySelector('.suggestions-list');
        this.resultTime = this.container.querySelector('.result-time');
    }
    
    update(result) {
        this.result = result;
        if (!result) {
            this.resultContainer.style.display = 'none';
            return;
        }
        
        this.resultContainer.style.display = 'block';
        this.renderResult();
    }
    
    renderResult() {
        if (!this.result) return;
        
        // 情感分类
        this.sentimentLabel.textContent = this.result.getSentimentLabel();
        this.sentimentLabel.className = `sentiment-label sentiment-${this.result.sentiment}`;
        
        // 置信度
        this.confidenceBadge.textContent = `置信度 ${this.result.getConfidencePercentage()}%`;
        
        // 情感强度
        const intensityPercent = this.result.getIntensityPercentage();
        this.intensityFill.style.width = `${intensityPercent}%`;
        this.intensityPercentage.textContent = `${intensityPercent}%`;
        
        // 情绪列表
        this.renderEmotions();
        
        // 分析文本
        this.analysisText.textContent = this.result.analysis;
        
        // 情感原因
        this.causesText.textContent = this.result.causes;
        
        // 建议
        this.renderSuggestions();
        
        // 时间
        this.resultTime.textContent = DateUtils.formatRelativeTime(this.result.timestamp);
    }
    
    renderEmotions() {
        this.emotionsList.innerHTML = '';
        
        this.result.emotions.forEach(emotion => {
            const emotionItem = this.createElement('div', 'emotion-item');
            emotionItem.innerHTML = `
                <span class="emotion-name">${emotion.name}</span>
                <div class="emotion-bar">
                    <div class="emotion-fill" style="width: ${emotion.getIntensityPercentage()}%"></div>
                </div>
                <span class="emotion-intensity">${emotion.getIntensityPercentage()}%</span>
            `;
            this.emotionsList.appendChild(emotionItem);
        });
    }
    
    renderSuggestions() {
        this.suggestionsList.innerHTML = '';
        
        // 将建议文本按句分割
        const suggestions = this.result.suggestions.split(/[。！？]/).filter(s => s.trim());
        
        suggestions.forEach(suggestion => {
            if (suggestion.trim()) {
                const li = this.createElement('li', 'suggestion-item', suggestion.trim() + '。');
                this.suggestionsList.appendChild(li);
            }
        });
    }
}

// ================================
// 历史记录组件
// ================================

/**
 * 历史记录列表组件
 */
class HistoryListComponent extends BaseComponent {
    constructor(container, options = {}) {
        super(container, options);
        this.history = [];
        this.maxItems = options.maxItems || 50;
    }
    
    doRender() {
        this.container.innerHTML = `
            <div class="history-container">
                <div class="history-header">
                    <h3>历史记录</h3>
                    <div class="history-controls">
                        <select class="filter-select">
                            <option value="all">全部</option>
                            <option value="positive">积极</option>
                            <option value="negative">消极</option>
                            <option value="neutral">中性</option>
                        </select>
                        <button class="refresh-btn">刷新</button>
                        <button class="clear-btn">清空</button>
                    </div>
                </div>
                <div class="history-list"></div>
                <div class="history-empty" style="display: none;">
                    <p>暂无历史记录</p>
                </div>
            </div>
        `;
        
        this.historyList = this.container.querySelector('.history-list');
        this.emptyState = this.container.querySelector('.history-empty');
        this.filterSelect = this.container.querySelector('.filter-select');
        this.refreshBtn = this.container.querySelector('.refresh-btn');
        this.clearBtn = this.container.querySelector('.clear-btn');
    }
    
    bindEvents() {
        // 过滤器变化
        this.filterSelect.addEventListener('change', () => {
            this.renderHistory();
        });
        
        // 刷新按钮
        this.refreshBtn.addEventListener('click', () => {
            this.emit('refresh');
        });
        
        // 清空按钮
        this.clearBtn.addEventListener('click', () => {
            if (confirm('确定要清空所有历史记录吗？')) {
                this.emit('clear');
            }
        });
    }
    
    update(history) {
        this.history = history || [];
        this.renderHistory();
    }
    
    renderHistory() {
        const filter = this.filterSelect.value;
        let filteredHistory = this.history;
        
        if (filter !== 'all') {
            filteredHistory = this.history.filter(item => item.sentiment === filter);
        }
        
        this.historyList.innerHTML = '';
        
        if (filteredHistory.length === 0) {
            this.emptyState.style.display = 'block';
            return;
        }
        
        this.emptyState.style.display = 'none';
        
        filteredHistory.slice(0, this.maxItems).forEach(item => {
            const historyItem = this.createHistoryItem(item);
            this.historyList.appendChild(historyItem);
        });
    }
    
    createHistoryItem(item) {
        const itemElement = this.createElement('div', 'history-item');
        itemElement.innerHTML = `
            <div class="history-item-header">
                <span class="history-sentiment sentiment-${item.sentiment}">${item.getSentimentLabel()}</span>
                <span class="history-time">${DateUtils.formatRelativeTime(item.timestamp)}</span>
            </div>
            <div class="history-text">${this.truncateText(item.text, 100)}</div>
            <div class="history-actions">
                <button class="view-btn">查看详情</button>
                <button class="analyze-again-btn">重新分析</button>
            </div>
        `;
        
        // 查看详情
        itemElement.querySelector('.view-btn').addEventListener('click', () => {
            this.emit('view-detail', item);
        });
        
        // 重新分析
        itemElement.querySelector('.analyze-again-btn').addEventListener('click', () => {
            this.emit('analyze-again', item.text);
        });
        
        return itemElement;
    }
    
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
}

// ================================
// 统计图表组件
// ================================

/**
 * 统计图表组件
 */
class StatisticsChartComponent extends BaseComponent {
    constructor(container, options = {}) {
        super(container, options);
        this.statistics = null;
        this.charts = {};
    }
    
    doRender() {
        this.container.innerHTML = `
            <div class="statistics-container">
                <div class="statistics-header">
                    <h3>数据统计</h3>
                    <select class="period-select">
                        <option value="7">最近7天</option>
                        <option value="30" selected>最近30天</option>
                        <option value="90">最近90天</option>
                    </select>
                </div>
                
                <div class="statistics-overview">
                    <div class="stat-card">
                        <div class="stat-number">0</div>
                        <div class="stat-label">总记录数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">0%</div>
                        <div class="stat-label">积极情绪</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">0%</div>
                        <div class="stat-label">消极情绪</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">0.0</div>
                        <div class="stat-label">平均强度</div>
                    </div>
                </div>
                
                <div class="charts-grid">
                    <div class="chart-container">
                        <h4>情感分布</h4>
                        <canvas id="sentiment-pie-chart"></canvas>
                    </div>
                    <div class="chart-container">
                        <h4>情感趋势</h4>
                        <canvas id="sentiment-trend-chart"></canvas>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h4>情绪标签云</h4>
                    <div class="emotion-cloud"></div>
                </div>
            </div>
        `;
        
        this.periodSelect = this.container.querySelector('.period-select');
        this.statNumbers = this.container.querySelectorAll('.stat-number');
        this.emotionCloud = this.container.querySelector('.emotion-cloud');
    }
    
    bindEvents() {
        this.periodSelect.addEventListener('change', () => {
            const days = parseInt(this.periodSelect.value);
            this.emit('period-change', days);
        });
    }
    
    update(statistics) {
        this.statistics = statistics;
        if (statistics) {
            this.renderStatistics();
        }
    }
    
    renderStatistics() {
        if (!this.statistics) return;
        
        // 更新统计卡片
        this.updateStatCards();
        
        // 更新图表
        this.updateCharts();
        
        // 更新情绪云
        this.updateEmotionCloud();
    }
    
    updateStatCards() {
        const distribution = this.statistics.getSentimentDistribution();
        
        this.statNumbers[0].textContent = this.statistics.totalRecords;
        this.statNumbers[1].textContent = `${distribution.positive}%`;
        this.statNumbers[2].textContent = `${distribution.negative}%`;
        this.statNumbers[3].textContent = this.statistics.averageIntensity.toFixed(2);
    }
    
    updateCharts() {
        // 这里应该集成Chart.js或其他图表库
        // 为了简化，这里只提供占位符
        console.log('更新图表:', this.statistics);
    }
    
    updateEmotionCloud() {
        this.emotionCloud.innerHTML = '';
        
        this.statistics.mostCommonEmotions.forEach(emotion => {
            const emotionTag = this.createElement('span', 'emotion-tag', emotion.name);
            const size = Math.max(0.8, Math.min(2, emotion.count / 10));
            emotionTag.style.fontSize = `${size}rem`;
            emotionTag.style.opacity = Math.max(0.5, emotion.average_intensity);
            this.emotionCloud.appendChild(emotionTag);
        });
    }
    
    destroy() {
        // 销毁图表实例
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        super.destroy();
    }
}

export {
    BaseComponent,
    SentimentInputComponent,
    SentimentResultComponent,
    HistoryListComponent,
    StatisticsChartComponent
};