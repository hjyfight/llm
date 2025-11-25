#!/usr/bin/env python3
"""
直接测试数据库连接和models修复
"""

import sys
import os
sys.path.append('/home/engine/project/backend')

def test_database_fix():
    print("🔧 测试数据库连接和models修复...")
    
    try:
        # 测试导入models
        print("1. 导入models模块...")
        from models import SentimentRecord, get_db, SessionLocal, engine
        print("✅ models模块导入成功")
        
        # 测试数据库引擎
        print("2. 测试数据库引擎...")
        print(f"   引擎类型: {type(engine)}")
        print("✅ 数据库引擎正常")
        
        # 测试SessionLocal
        print("3. 测试SessionLocal...")
        print(f"   SessionLocal类型: {type(SessionLocal)}")
        
        # 创建session实例
        session = SessionLocal()
        print(f"   Session实例类型: {type(session)}")
        print("✅ SessionLocal创建成功")
        
        # 测试get_db函数
        print("4. 测试get_db函数...")
        db_gen = get_db()
        print(f"   get_db返回类型: {type(db_gen)}")
        
        # 获取generator的值
        db_session = next(db_gen)
        print(f"   数据库会话类型: {type(db_session)}")
        print("✅ get_db函数正常")
        
        # 测试创建表
        print("5. 测试数据库表创建...")
        from models import Base
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")
        
        # 清理
        session.close()
        db_session.close()
        
        print("\n🎉 数据库测试全部通过！")
        print("✅ 'generator' object has no attribute 'bind' 错误已修复")
        print("✅ SQLAlchemy session配置正确")
        print("✅ 数据库连接正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_fix()
    if success:
        print("\n🚀 数据库修复验证成功！现在可以启动后端服务进行完整测试。")
    else:
        print("\n❌ 数据库修复验证失败！")