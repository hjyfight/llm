#!/usr/bin/env python3
"""
面向对象架构验证脚本
验证所有面向对象组件是否正常工作
"""

import sys
import os
import traceback
from datetime import datetime

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def test_imports():
    """测试所有核心模块导入"""
    print("🔍 测试核心模块导入...")
    
    try:
        from core.service_factory import get_service_manager, get_sentiment_service
        print("✅ 服务工厂导入成功")
    except Exception as e:
        print(f"❌ 服务工厂导入失败: {e}")
        return False
    
    try:
        from core.analyzer import LLMAnalyzer, CachedAnalyzer
        print("✅ 分析器模块导入成功")
    except Exception as e:
        print(f"❌ 分析器模块导入失败: {e}")
        return False
    
    try:
        from core.data_manager import DatabaseManager
        print("✅ 数据管理器模块导入成功")
    except Exception as e:
        print(f"❌ 数据管理器模块导入失败: {e}")
        return False
    
    try:
        from core.health_assessor import MentalHealthAssessor
        print("✅ 健康评估器模块导入成功")
    except Exception as e:
        print(f"❌ 健康评估器模块导入失败: {e}")
        return False
    
    try:
        from core.knowledge_retriever import MentalHealthKnowledgeRetriever
        print("✅ 知识检索器模块导入成功")
    except Exception as e:
        print(f"❌ 知识检索器模块导入失败: {e}")
        return False
    
    try:
        from core.user_manager import SimpleUserManager
        print("✅ 用户管理器模块导入成功")
    except Exception as e:
        print(f"❌ 用户管理器模块导入失败: {e}")
        return False
    
    return True

def test_interfaces():
    """测试接口定义"""
    print("\n🔍 测试接口定义...")
    
    try:
        from core import (
            ISentimentAnalyzer, IDataManager, IHealthAssessor,
            IKnowledgeRetriever, IUserManager, IUIComponent
        )
        print("✅ 所有接口导入成功")
        return True
    except Exception as e:
        print(f"❌ 接口导入失败: {e}")
        return False

def test_data_classes():
    """测试数据传输对象"""
    print("\n🔍 测试数据传输对象...")
    
    try:
        from core import (
            EmotionData, SentimentAnalysisResult, HealthScore,
            User, UserStatistics
        )
        
        # 测试EmotionData
        emotion = EmotionData("快乐", 0.8)
        assert emotion.name == "快乐"
        assert emotion.intensity == 0.8
        assert emotion.get_intensity_percentage() == 80
        print("✅ EmotionData测试通过")
        
        # 测试User
        user = User("test_user", datetime.now(), datetime.now())
        assert user.id == "test_user"
        print("✅ User测试通过")
        
        print("✅ 所有数据传输对象测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据传输对象测试失败: {e}")
        traceback.print_exc()
        return False

def test_service_factory():
    """测试服务工厂"""
    print("\n🔍 测试服务工厂...")
    
    try:
        from core.service_factory import get_service_manager
        
        # 测试服务管理器单例
        manager1 = get_service_manager()
        manager2 = get_service_manager()
        assert manager1 is manager2, "服务管理器应该是单例"
        print("✅ 服务管理器单例测试通过")
        
        # 测试健康检查
        health_status = manager1.health_check()
        assert "status" in health_status
        print("✅ 健康检查测试通过")
        
        print("✅ 服务工厂测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 服务工厂测试失败: {e}")
        traceback.print_exc()
        return False

def test_configuration():
    """测试配置类"""
    print("\n🔍 测试配置类...")
    
    try:
        from core import SystemConfig, Logger
        
        # 测试系统配置
        assert hasattr(SystemConfig, 'API_BASE_URL')
        assert hasattr(SystemConfig, 'CACHE_TTL')
        print("✅ 系统配置测试通过")
        
        # 测试日志记录器
        logger = Logger.get_logger("test")
        assert logger is not None
        print("✅ 日志记录器测试通过")
        
        print("✅ 配置类测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置类测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始面向对象架构验证")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("接口定义", test_interfaces),
        ("数据传输对象", test_data_classes),
        ("服务工厂", test_service_factory),
        ("配置类", test_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！面向对象架构验证成功！")
        print("\n✨ 面向对象架构特性:")
        print("  • SOLID原则应用")
        print("  • 设计模式实现")
        print("  • 分层架构设计")
        print("  • 接口驱动开发")
        print("  • 依赖注入支持")
        print("\n🚀 项目已准备就绪，可以启动服务！")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关模块")
        return 1

if __name__ == "__main__":
    sys.exit(main())