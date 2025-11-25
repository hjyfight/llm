#!/usr/bin/env python3
"""
测试情感分析API的脚本
"""

import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 开始测试情感分析API...")
    
    # 1. 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False
    
    # 2. 测试情感分析
    print("\n2. 测试情感分析...")
    test_text = "今天天气真好，心情很愉快！"
    try:
        response = requests.post(
            f"{base_url}/api/sentiment/analyze",
            json={
                "text": test_text,
                "user_id": "test_user"
            }
        )
        if response.status_code == 200:
            print("✅ 情感分析成功")
            result = response.json()
            print(f"   分析结果: {result['sentiment']}")
            print(f"   置信度: {result['confidence']}")
            print(f"   情感强度: {result['intensity']}")
            print(f"   情绪: {[e['name'] for e in result['emotions']]}")
        else:
            print(f"❌ 情感分析失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 情感分析请求失败: {e}")
        return False
    
    # 3. 测试历史记录
    print("\n3. 测试历史记录...")
    try:
        response = requests.get(f"{base_url}/api/sentiment/history/test_user")
        if response.status_code == 200:
            print("✅ 历史记录获取成功")
            history = response.json()
            print(f"   记录数量: {len(history)}")
        else:
            print(f"❌ 历史记录获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 历史记录请求失败: {e}")
        return False
    
    # 4. 测试统计数据
    print("\n4. 测试统计数据...")
    try:
        response = requests.get(f"{base_url}/api/sentiment/stats/test_user")
        if response.status_code == 200:
            print("✅ 统计数据获取成功")
            stats = response.json()
            print(f"   总记录数: {stats['total_records']}")
            print(f"   积极情感: {stats['positive_count']}")
            print(f"   消极情感: {stats['negative_count']}")
            print(f"   中性情感: {stats['neutral_count']}")
        else:
            print(f"❌ 统计数据获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 统计数据请求失败: {e}")
        return False
    
    print("\n🎉 所有测试通过！")
    return True

if __name__ == "__main__":
    test_api()