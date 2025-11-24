/**
 * 前端面向对象架构设计
 * 智能情感分析与心理健康辅助系统
 */

// ================================
// 数据传输对象 (DTOs)
// ================================

/**
 * 情感数据类
 */
class EmotionData {
    constructor(name, intensity) {
        this.name = name;
        this.intensity = intensity;
        
        // 验证
        if (intensity < 0 || intensity > 1) {
            throw new Error('情感强度必须在0-1之间');
        }
    }
    
    getIntensityPercentage() {
        return Math.round(this.intensity * 100);
    }
}

/**
 * 情感分析结果类
 */
class SentimentAnalysisResult {
    constructor(data) {
        this.id = data.id;
        this.userId = data.user_id;
        this.text = data.text;
        this.sentiment = data.sentiment;
        this.confidence = data.confidence;
        this.emotions = data.emotions.map(e => new EmotionData(e.name, e.intensity));
        this.intensity = data.intensity;
        this.analysis = data.analysis;
        this.causes = data.causes;
        this.suggestions = data.suggestions;
        this.timestamp = new Date(data.created_at);
    }
    
    getSentimentLabel() {
        const labels = {
            'positive': '积极',
            'negative': '消极',
            'neutral': '中性'
        };
        return labels[this.sentiment] || '未知';
    }
    
    getConfidencePercentage() {
        return Math.round(this.confidence * 100);
    }
    
    getIntensityPercentage() {
        return Math.round(this.intensity * 100);
    }
    
    getPrimaryEmotion() {
        if (this.emotions.length === 0) return null;
        return this.emotions.reduce((prev, current) => 
            prev.intensity > current.intensity ? prev : current
        );
    }
}

/**
 * 健康评分类
 */
class HealthScore {
    constructor(data) {
        this.overallScore = data.overall_score;
        this.riskLevel = data.risk_level;
        this.keyConcerns = data.key_concerns;
        this.recommendations = data.recommendations;
        this.detailedAnalysis = data.detailed_analysis;
    }
    
    getRiskLevelLabel() {
        const labels = {
            'low': '低风险',
            'medium': '中风险',
            'high': '高风险'
        };
        return labels[this.riskLevel] || '未知';
    }
    
    getScoreColor() {
        if (this.overallScore >= 70) return '#10b981'; // green
        if (this.overallScore >= 40) return '#f59e0b'; // yellow
        return '#ef4444'; // red
    }
}

/**
 * 用户统计数据类
 */
class UserStatistics {
    constructor(data) {
        this.totalRecords = data.total_records;
        this.positiveCount = data.positive_count;
        this.negativeCount = data.negative_count;
        this.neutralCount = data.neutral_count;
        this.averageIntensity = data.average_intensity;
        this.mostCommonEmotions = data.most_common_emotions || [];
        this.dailyTrends = data.daily_trends || [];
    }
    
    getSentimentDistribution() {
        const total = this.totalRecords;
        return {
            positive: total > 0 ? (this.positiveCount / total * 100).toFixed(1) : 0,
            negative: total > 0 ? (this.negativeCount / total * 100).toFixed(1) : 0,
            neutral: total > 0 ? (this.neutralCount / total * 100).toFixed(1) : 0
        };
    }
}

// ================================
// 抽象接口定义
// ================================

/**
 * API服务接口
 */
class IApiService {
    async analyzeSentiment(text, userId = 'default_user') {
        throw new Error('Method must be implemented');
    }
    
    async getUserHistory(userId, limit = 100) {
        throw new Error('Method must be implemented');
    }
    
    async getUserStatistics(userId, days = 30) {
        throw new Error('Method must be implemented');
    }
    
    async getHealthAssessment(userId, days = 30) {
        throw new Error('Method must be implemented');
    }
}

/**
 * 数据管理接口
 */
class IDataManager {
    saveAnalysis(result) {
        throw new Error('Method must be implemented');
    }
    
    getHistory(userId) {
        throw new Error('Method must be implemented');
    }
    
    getStatistics(userId) {
        throw new Error('Method must be implemented');
    }
    
    clearCache() {
        throw new Error('Method must be implemented');
    }
}

/**
 * UI组件接口
 */
class IUIComponent {
    render() {
        throw new Error('Method must be implemented');
    }
    
    update(data) {
        throw new Error('Method must be implemented');
    }
    
    destroy() {
        throw new Error('Method must be implemented');
    }
}

// ================================
// API服务实现
// ================================

/**
 * HTTP API服务实现
 */
class HttpApiService extends IApiService {
    constructor(baseUrl = 'http://localhost:8000') {
        super();
        this.baseUrl = baseUrl;
        this.timeout = 30000; // 30秒超时
    }
    
    async analyzeSentiment(text, userId = 'default_user') {
        try {
            const response = await this._request('/api/sentiment/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    user_id: userId
                })
            });
            
            return new SentimentAnalysisResult(response);
        } catch (error) {
            console.error('情感分析失败:', error);
            throw error;
        }
    }
    
    async getUserHistory(userId, limit = 100) {
        try {
            const response = await this._request(`/api/sentiment/history/${userId}?limit=${limit}`);
            return response.map(item => new SentimentAnalysisResult(item));
        } catch (error) {
            console.error('获取历史记录失败:', error);
            throw error;
        }
    }
    
    async getUserStatistics(userId, days = 30) {
        try {
            const response = await this._request(`/api/sentiment/stats/${userId}?days=${days}`);
            return new UserStatistics(response);
        } catch (error) {
            console.error('获取统计数据失败:', error);
            throw error;
        }
    }
    
    async getHealthAssessment(userId, days = 30) {
        try {
            const response = await this._request(`/api/health/assessment/${userId}?days=${days}`);
            return new HealthScore(response);
        } catch (error) {
            console.error('获取健康评估失败:', error);
            throw error;
        }
    }
    
    async _request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        // 添加默认选项
        const defaultOptions = {
            timeout: this.timeout,
            headers: {
                'Accept': 'application/json',
            }
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        // 创建超时控制器
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        finalOptions.signal = controller.signal;
        
        try {
            const response = await fetch(url, finalOptions);
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }
}

/**
 * 带缓存的API服务装饰器
 */
class CachedApiService extends IApiService {
    constructor(apiService) {
        super();
        this.apiService = apiService;
        this.cache = new Map();
        this.cacheTTL = 5 * 60 * 1000; // 5分钟缓存
    }
    
    async analyzeSentiment(text, userId = 'default_user') {
        // 情感分析不使用缓存，因为每次都应该是实时的
        return await this.apiService.analyzeSentiment(text, userId);
    }
    
    async getUserHistory(userId, limit = 100) {
        const cacheKey = `history_${userId}_${limit}`;
        const cached = this._getFromCache(cacheKey);
        if (cached) return cached;
        
        const result = await this.apiService.getUserHistory(userId, limit);
        this._setCache(cacheKey, result);
        return result;
    }
    
    async getUserStatistics(userId, days = 30) {
        const cacheKey = `stats_${userId}_${days}`;
        const cached = this._getFromCache(cacheKey);
        if (cached) return cached;
        
        const result = await this.apiService.getUserStatistics(userId, days);
        this._setCache(cacheKey, result);
        return result;
    }
    
    async getHealthAssessment(userId, days = 30) {
        const cacheKey = `health_${userId}_${days}`;
        const cached = this._getFromCache(cacheKey);
        if (cached) return cached;
        
        const result = await this.apiService.getHealthAssessment(userId, days);
        this._setCache(cacheKey, result);
        return result;
    }
    
    _getFromCache(key) {
        const item = this.cache.get(key);
        if (item && Date.now() - item.timestamp < this.cacheTTL) {
            return item.data;
        }
        if (item) {
            this.cache.delete(key);
        }
        return null;
    }
    
    _setCache(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
        
        // 限制缓存大小
        if (this.cache.size > 100) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
    }
    
    clearCache() {
        this.cache.clear();
    }
}

// ================================
// 数据管理器实现
// ================================

/**
 * 本地存储数据管理器
 */
class LocalDataManager extends IDataManager {
    constructor() {
        super();
        this.storageKey = 'sentiment_analysis_data';
        this.loadData();
    }
    
    saveAnalysis(result) {
        if (!this.data.analyses) {
            this.data.analyses = [];
        }
        
        // 添加到开头
        this.data.analyses.unshift(result);
        
        // 限制存储数量
        if (this.data.analyses.length > 1000) {
            this.data.analyses = this.data.analyses.slice(0, 1000);
        }
        
        this.saveData();
    }
    
    getHistory(userId) {
        if (!this.data.analyses) return [];
        return this.data.analyses.filter(item => item.userId === userId);
    }
    
    getStatistics(userId) {
        const userHistory = this.getHistory(userId);
        // 这里可以实现简单的统计计算
        return {
            totalCount: userHistory.length,
            recentCount: userHistory.filter(item => 
                Date.now() - item.timestamp.getTime() < 7 * 24 * 60 * 60 * 1000
            ).length
        };
    }
    
    clearCache() {
        this.data = {};
        this.saveData();
    }
    
    loadData() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            this.data = stored ? JSON.parse(stored) : {};
        } catch (error) {
            console.error('加载数据失败:', error);
            this.data = {};
        }
    }
    
    saveData() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.data));
        } catch (error) {
            console.error('保存数据失败:', error);
        }
    }
}

// ================================
// 事件管理器
// ================================

/**
 * 事件管理器 - 观察者模式
 */
class EventManager {
    constructor() {
        this.listeners = new Map();
    }
    
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }
    
    off(event, callback) {
        if (this.listeners.has(event)) {
            const callbacks = this.listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }
    
    emit(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`事件处理器错误 (${event}):`, error);
                }
            });
        }
    }
    
    once(event, callback) {
        const onceCallback = (data) => {
            callback(data);
            this.off(event, onceCallback);
        };
        this.on(event, onceCallback);
    }
}

// ================================
// 应用配置
// ================================

/**
 * 应用配置类
 */
class AppConfig {
    static get API_BASE_URL() {
        return process.env.REACT_APP_API_URL || 'http://localhost:8000';
    }
    
    static get CACHE_TTL() {
        return 5 * 60 * 1000; // 5分钟
    }
    
    static get MAX_HISTORY_ITEMS() {
        return 100;
    }
    
    static get CHART_COLORS() {
        return {
            positive: '#10b981',
            negative: '#ef4444',
            neutral: '#6b7280',
            primary: '#3b82f6',
            secondary: '#8b5cf6'
        };
    }
    
    static get EMOTION_COLORS() {
        return {
            '快乐': '#fbbf24',
            '悲伤': '#60a5fa',
            '愤怒': '#f87171',
            '焦虑': '#a78bfa',
            '恐惧': '#c084fc',
            '厌恶': '#fb923c',
            '惊讶': '#fde047',
            '平静': '#86efac',
            '兴奋': '#fca5a5',
            '沮丧': '#94a3b8'
        };
    }
}

// ================================
// 工具类
// ================================

/**
 * 日期工具类
 */
class DateUtils {
    static formatDate(date) {
        return new Intl.DateTimeFormat('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }
    
    static formatRelativeTime(date) {
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return '刚刚';
        if (minutes < 60) return `${minutes}分钟前`;
        if (hours < 24) return `${hours}小时前`;
        if (days < 30) return `${days}天前`;
        
        return this.formatDate(date);
    }
    
    static getDaysAgo(days) {
        const date = new Date();
        date.setDate(date.getDate() - days);
        return date;
    }
}

/**
 * 验证工具类
 */
class ValidationUtils {
    static validateText(text) {
        if (!text || typeof text !== 'text') {
            return { valid: false, message: '请输入有效的文本' };
        }
        
        if (text.trim().length === 0) {
            return { valid: false, message: '文本内容不能为空' };
        }
        
        if (text.length > 5000) {
            return { valid: false, message: '文本长度不能超过5000字符' };
        }
        
        return { valid: true };
    }
    
    static validateUserId(userId) {
        if (!userId || typeof userId !== 'string') {
            return { valid: false, message: '用户ID无效' };
        }
        
        if (userId.length > 50) {
            return { valid: false, message: '用户ID长度不能超过50字符' };
        }
        
        return { valid: true };
    }
}

// 导出所有类和工具
export {
    // 数据类
    EmotionData,
    SentimentAnalysisResult,
    HealthScore,
    UserStatistics,
    
    // 接口
    IApiService,
    IDataManager,
    IUIComponent,
    
    // 服务实现
    HttpApiService,
    CachedApiService,
    LocalDataManager,
    
    // 工具类
    EventManager,
    AppConfig,
    DateUtils,
    ValidationUtils
};