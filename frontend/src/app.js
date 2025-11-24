/**
 * 主应用类 - 智能情感分析系统
 */

import { 
    HttpApiService, 
    CachedApiService, 
    LocalDataManager,
    EventManager,
    ValidationUtils,
    AppConfig
} from './core';

import {
    SentimentInputComponent,
    SentimentResultComponent,
    HistoryListComponent,
    StatisticsChartComponent
} from './components';

/**
 * 主应用类 - 单例模式
 */
class SentimentAnalysisApp {
    constructor() {
        if (SentimentAnalysisApp.instance) {
            return SentimentAnalysisApp.instance;
        }
        
        this.isInitialized = false;
        this.currentUserId = 'default_user';
        this.eventManager = new EventManager();
        this.components = {};
        this.services = {};
        
        SentimentAnalysisApp.instance = this;
    }
    
    /**
     * 初始化应用
     */
    async initialize() {
        if (this.isInitialized) return;
        
        console.log('初始化情感分析应用...');
        
        try {
            // 初始化服务
            await this.initializeServices();
            
            // 初始化组件
            this.initializeComponents();
            
            // 绑定事件
            this.bindEvents();
            
            // 加载初始数据
            await this.loadInitialData();
            
            this.isInitialized = true;
            console.log('应用初始化完成');
            
            // 触发初始化完成事件
            this.eventManager.emit('app-initialized');
            
        } catch (error) {
            console.error('应用初始化失败:', error);
            this.showError('应用初始化失败，请刷新页面重试');
        }
    }
    
    /**
     * 初始化服务
     */
    async initializeServices() {
        // 创建API服务
        const httpApiService = new HttpApiService(AppConfig.API_BASE_URL);
        this.services.apiService = new CachedApiService(httpApiService);
        
        // 创建数据管理器
        this.services.dataManager = new LocalDataManager();
        
        // 测试API连接
        try {
            await this.services.apiService.getUserStatistics(this.currentUserId, 1);
            console.log('API连接测试成功');
        } catch (error) {
            console.warn('API连接测试失败，将使用缓存模式:', error.message);
        }
    }
    
    /**
     * 初始化组件
     */
    initializeComponents() {
        // 情感输入组件
        const inputContainer = document.querySelector('#sentiment-input');
        if (inputContainer) {
            this.components.input = new SentimentInputComponent(inputContainer, {
                placeholder: '请输入您想要分析的情感内容，比如今天的心情、遇到的事情等...',
                maxLength: 5000
            });
        }
        
        // 情感结果组件
        const resultContainer = document.querySelector('#sentiment-result');
        if (resultContainer) {
            this.components.result = new SentimentResultComponent(resultContainer);
        }
        
        // 历史记录组件
        const historyContainer = document.querySelector('#history-list');
        if (historyContainer) {
            this.components.history = new HistoryListComponent(historyContainer, {
                maxItems: 50
            });
        }
        
        // 统计图表组件
        const statisticsContainer = document.querySelector('#statistics-charts');
        if (statisticsContainer) {
            this.components.statistics = new StatisticsChartComponent(statisticsContainer);
        }
        
        // 渲染所有组件
        Object.values(this.components).forEach(component => {
            component.render();
        });
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 输入组件事件
        if (this.components.input) {
            this.components.input.on('analyze', (text) => {
                this.handleAnalyzeSentiment(text);
            });
            
            this.components.input.on('clear', () => {
                this.components.result.update(null);
            });
        }
        
        // 历史记录组件事件
        if (this.components.history) {
            this.components.history.on('view-detail', (item) => {
                this.handleViewDetail(item);
            });
            
            this.components.history.on('analyze-again', (text) => {
                this.handleAnalyzeAgain(text);
            });
            
            this.components.history.on('refresh', () => {
                this.loadHistoryData();
            });
            
            this.components.history.on('clear', () => {
                this.handleClearHistory();
            });
        }
        
        // 统计组件事件
        if (this.components.statistics) {
            this.components.statistics.on('period-change', (days) => {
                this.loadStatisticsData(days);
            });
        }
        
        // Tab切换事件
        this.bindTabEvents();
        
        // 全局错误处理
        window.addEventListener('error', (event) => {
            console.error('全局错误:', event.error);
            this.showError('发生了未知错误，请刷新页面重试');
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            console.error('未处理的Promise拒绝:', event.reason);
            this.showError('网络请求失败，请检查网络连接');
        });
    }
    
    /**
     * 绑定Tab切换事件
     */
    bindTabEvents() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');
                
                // 更新按钮状态
                tabButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // 更新内容显示
                tabContents.forEach(content => {
                    if (content.id === `${targetTab}-tab`) {
                        content.classList.add('active');
                    } else {
                        content.classList.remove('active');
                    }
                });
                
                // 触发Tab切换事件
                this.eventManager.emit('tab-changed', targetTab);
            });
        });
    }
    
    /**
     * 加载初始数据
     */
    async loadInitialData() {
        try {
            await Promise.all([
                this.loadHistoryData(),
                this.loadStatisticsData(30)
            ]);
        } catch (error) {
            console.warn('加载初始数据失败:', error);
        }
    }
    
    /**
     * 处理情感分析
     */
    async handleAnalyzeSentiment(text) {
        try {
            // 验证输入
            const validation = ValidationUtils.validateText(text);
            if (!validation.valid) {
                this.showError(validation.message);
                return;
            }
            
            // 重置输入组件加载状态
            if (this.components.input) {
                this.components.input.setLoading(false);
            }
            
            // 调用API分析
            const result = await this.services.apiService.analyzeSentiment(text, this.currentUserId);
            
            // 保存到本地存储
            this.services.dataManager.saveAnalysis(result);
            
            // 更新结果组件
            if (this.components.result) {
                this.components.result.update(result);
            }
            
            // 刷新历史记录和统计
            await this.refreshData();
            
            // 触发分析完成事件
            this.eventManager.emit('analysis-completed', result);
            
        } catch (error) {
            console.error('情感分析失败:', error);
            this.showError('情感分析失败，请稍后重试');
            
            // 重置输入组件状态
            if (this.components.input) {
                this.components.input.setLoading(false);
            }
        }
    }
    
    /**
     * 查看详情
     */
    handleViewDetail(item) {
        if (this.components.result) {
            this.components.result.update(item);
            
            // 切换到分析结果Tab
            this.switchToTab('analysis');
        }
    }
    
    /**
     * 重新分析
     */
    handleAnalyzeAgain(text) {
        if (this.components.input) {
            this.components.input.clear();
            
            // 填充文本到输入框
            const textarea = document.querySelector('.sentiment-textarea');
            if (textarea) {
                textarea.value = text;
                textarea.dispatchEvent(new Event('input'));
            }
            
            // 切换到分析输入Tab
            this.switchToTab('analysis');
            
            // 聚焦到输入框
            setTimeout(() => textarea.focus(), 100);
        }
    }
    
    /**
     * 清空历史记录
     */
    async handleClearHistory() {
        try {
            this.services.dataManager.clearCache();
            await this.loadHistoryData();
            this.showSuccess('历史记录已清空');
        } catch (error) {
            console.error('清空历史记录失败:', error);
            this.showError('清空历史记录失败');
        }
    }
    
    /**
     * 加载历史数据
     */
    async loadHistoryData() {
        try {
            let history;
            
            // 尝试从API获取
            try {
                history = await this.services.apiService.getUserHistory(this.currentUserId, 50);
            } catch (error) {
                // API失败时使用本地数据
                console.warn('API获取历史失败，使用本地数据:', error);
                history = this.services.dataManager.getHistory(this.currentUserId);
            }
            
            if (this.components.history) {
                this.components.history.update(history);
            }
            
        } catch (error) {
            console.error('加载历史数据失败:', error);
        }
    }
    
    /**
     * 加载统计数据
     */
    async loadStatisticsData(days = 30) {
        try {
            let statistics;
            
            // 尝试从API获取
            try {
                const apiStats = await this.services.apiService.getUserStatistics(this.currentUserId, days);
                statistics = apiStats;
            } catch (error) {
                // API失败时使用本地数据
                console.warn('API获取统计失败，使用本地数据:', error);
                statistics = this.services.dataManager.getStatistics(this.currentUserId);
            }
            
            if (this.components.statistics) {
                this.components.statistics.update(statistics);
            }
            
        } catch (error) {
            console.error('加载统计数据失败:', error);
        }
    }
    
    /**
     * 刷新数据
     */
    async refreshData() {
        await Promise.all([
            this.loadHistoryData(),
            this.loadStatisticsData(30)
        ]);
    }
    
    /**
     * 切换到指定Tab
     */
    switchToTab(tabName) {
        const tabButton = document.querySelector(`[data-tab="${tabName}"]`);
        if (tabButton) {
            tabButton.click();
        }
    }
    
    /**
     * 显示错误消息
     */
    showError(message) {
        this.showMessage(message, 'error');
    }
    
    /**
     * 显示成功消息
     */
    showSuccess(message) {
        this.showMessage(message, 'success');
    }
    
    /**
     * 显示消息
     */
    showMessage(message, type = 'info') {
        // 创建消息元素
        const messageEl = document.createElement('div');
        messageEl.className = `message message-${type}`;
        messageEl.textContent = message;
        
        // 添加到页面
        document.body.appendChild(messageEl);
        
        // 显示动画
        setTimeout(() => messageEl.classList.add('show'), 10);
        
        // 自动隐藏
        setTimeout(() => {
            messageEl.classList.remove('show');
            setTimeout(() => {
                if (messageEl.parentNode) {
                    messageEl.parentNode.removeChild(messageEl);
                }
            }, 300);
        }, 3000);
    }
    
    /**
     * 设置用户ID
     */
    setUserId(userId) {
        const validation = ValidationUtils.validateUserId(userId);
        if (!validation.valid) {
            throw new Error(validation.message);
        }
        
        this.currentUserId = userId;
        this.refreshData();
    }
    
    /**
     * 获取当前用户ID
     */
    getUserId() {
        return this.currentUserId;
    }
    
    /**
     * 获取服务实例
     */
    getService(serviceName) {
        return this.services[serviceName];
    }
    
    /**
     * 获取组件实例
     */
    getComponent(componentName) {
        return this.components[componentName];
    }
    
    /**
     * 销毁应用
     */
    destroy() {
        // 销毁组件
        Object.values(this.components).forEach(component => {
            if (component && typeof component.destroy === 'function') {
                component.destroy();
            }
        });
        
        // 清理服务
        this.services = {};
        this.components = {};
        this.eventManager = null;
        this.isInitialized = false;
    }
}

// 创建全局应用实例
const app = new SentimentAnalysisApp();

// 导出应用实例
export default app;

// 导出类（用于测试）
export { SentimentAnalysisApp };