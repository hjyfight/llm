#!/usr/bin/env python3
"""
测试情感分析API的脚本（使用urllib）
"""

import urllib.request
import urllib.parse
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 开始测试情感分析API...")
    
    # 1. 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        with urllib.request.urlopen(f"{base_url}/api/health") as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print("✅ 健康检查通过")
                print(f"   响应: {data}")
            else:
                print(f"❌ 健康检查失败: {response.status}")
                return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False
    
    # 2. 测试情感分析
    print("\n2. 测试情感分析...")
    test_data = {
        "text": "今天天气真好，心情很愉快！",
        "user_id": "test_user"
    }
    
    try:
        data = json.dumps(test_data).encode('utf-8')
        req = urllib.request.Request(
            f"{base_url}/api/sentiment/analyze",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                result = json.loads(response.read().decode())
                print("✅ 情感分析成功")
                print(f"   分析结果: {result['sentiment']}")
                print(f"   置信度: {result['confidence']}")
                print(f"   情感强度: {result['intensity']}")
                print(f"   情绪: {[e['name'] for e in result['emotions']]}")
                
                # 保存ID用于后续测试
                record_id = result.get('id')
                print(f"   记录ID: {record_id}")
                
            else:
                print(f"❌ 情感分析失败: {response.status}")
                return False
    except Exception as e:
        print(f"❌ 情感分析请求失败: {e}")
        return False
    
    # 3. 测试历史记录
    print("\n3. 测试历史记录...")
    try:
        with urllib.request.urlopen(f"{base_url}/api/sentiment/history/test_user") as response:
            if response.status == 200:
                history = json.loads(response.read().decode())
                print("✅ 历史记录获取成功")
                print(f"   记录数量: {len(history)}")
            else:
                print(f"❌ 历史记录获取失败: {response.status}")
                return False
    except Exception as e:
        print(f"❌ 历史记录请求失败: {e}")
        return False
    
    # 4. 测试统计数据
    print("\n4. 测试统计数据...")
    try:
        with urllib.request.urlopen(f"{base_url}/api/sentiment/stats/test_user") as response:
            if response.status == 200:
                stats = json.loads(response.read().decode())
                print("✅ 统计数据获取成功")
                print(f"   总记录数: {stats['total_records']}")
                print(f"   积极情感: {stats['positive_count']}")
                print(f"   消极情感: {stats['negative_count']}")
                print(f"   中性情感: {stats['neutral_count']}")
            else:
                print(f"❌ 统计数据获取失败: {response.status}")
                return False
    except Exception as e:
        print(f"❌ 统计数据请求失败: {e}")
        return False
    
    print("\n🎉 所有测试通过！")
    print("✅ 数据库连接正常")
    print("✅ API接口正常")
    print("✅ 情感分析功能正常")
    print("✅ 历史记录功能正常")
    print("✅ 统计功能正常")
    print("✅ 'generator' object has no attribute 'bind' 错误已修复！")
    
    return True

if __name__ == "__main__":
    test_api()