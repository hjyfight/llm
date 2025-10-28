"""
演示脚本 - 用于测试和展示系统功能

使用方法：
1. 确保已配置 .env 文件（包含OPENAI_API_KEY）
2. 运行: python demo.py
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入服务
from llm_service import llm_service
from rag_service import rag_service
from models import SessionLocal, SentimentRecord


def print_section(title):
    """打印章节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def demo_sentiment_analysis():
    """演示情感分析功能"""
    print_section("1. 情感分析演示")
    
    # 测试文本
    test_texts = [
        "今天的工作压力很大，感觉有点焦虑和疲惫。虽然完成了任务，但总觉得不够好，担心明天的presentation。",
        "今天天气真好！和朋友一起去公园玩，心情特别愉快。感觉生活充满希望。",
        "又是普通的一天，没什么特别的事情发生。"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"测试 {i}:")
        print(f"输入文本: {text}\n")
        
        try:
            # 调用LLM分析
            result = llm_service.analyze_sentiment(text)
            
            print(f"情感分类: {result['sentiment']} (置信度: {result['confidence']:.2f})")
            print(f"情感强度: {result['intensity']:.2f}")
            print(f"\n识别的情绪:")
            for emotion in result['emotions']:
                print(f"  - {emotion['name']}: {emotion['intensity']:.2f}")
            
            print(f"\n详细分析: {result['analysis']}")
            print(f"\n可能原因: {result['causes']}")
            
            # 保存到数据库（可选）
            db = SessionLocal()
            record = SentimentRecord(
                user_id="demo_user",
                text=text,
                sentiment=result['sentiment'],
                confidence=result['confidence'],
                emotions=json.dumps(result['emotions'], ensure_ascii=False),
                intensity=result['intensity'],
                analysis=result['analysis'],
                causes=result['causes'],
                suggestions=""
            )
            db.add(record)
            db.commit()
            db.close()
            
            print("\n✅ 分析完成并保存到数据库")
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
        
        print("-" * 60)


def demo_rag_knowledge():
    """演示RAG知识检索功能"""
    print_section("2. RAG知识检索演示")
    
    # 测试查询
    queries = [
        ("anxiety", "焦虑"),
        ("sadness", "悲伤"),
        ("stress", "压力")
    ]
    
    for emotion, chinese_name in queries:
        print(f"查询情绪: {chinese_name} ({emotion})")
        
        try:
            results = rag_service.search_by_emotion(emotion, top_k=2)
            
            if results:
                print(f"找到 {len(results)} 条相关知识:\n")
                for i, item in enumerate(results, 1):
                    print(f"{i}. {item['content']}")
                    print(f"   类别: {item['metadata'].get('category', 'N/A')}")
                    print(f"   技巧: {item['metadata'].get('technique', 'N/A')}")
                    print()
            else:
                print("未找到相关知识\n")
                
        except Exception as e:
            print(f"❌ 检索失败: {e}\n")
        
        print("-" * 60)


def demo_suggestion_generation():
    """演示建议生成功能"""
    print_section("3. 个性化建议生成演示")
    
    # 模拟情感分析结果
    sentiment_data = {
        'sentiment': 'negative',
        'emotions': [
            {'name': 'anxiety', 'intensity': 0.8},
            {'name': 'stress', 'intensity': 0.7}
        ],
        'intensity': 0.75,
        'analysis': '文本显示出明显的焦虑和压力情绪，主要与工作表现和未来的presentation有关。',
        'causes': '可能是由于完美主义倾向和对自我能力的质疑导致的焦虑。'
    }
    
    print("基于以下情感分析结果:")
    print(json.dumps(sentiment_data, indent=2, ensure_ascii=False))
    print("\n生成个性化建议:\n")
    
    try:
        suggestions = llm_service.generate_suggestions(sentiment_data, user_history=[])
        print(suggestions)
        print("\n✅ 建议生成完成")
    except Exception as e:
        print(f"❌ 生成失败: {e}")


def demo_health_assessment():
    """演示健康评估功能"""
    print_section("4. 心理健康评估演示")
    
    # 从数据库获取历史记录
    db = SessionLocal()
    records = db.query(SentimentRecord).filter(
        SentimentRecord.user_id == "demo_user"
    ).order_by(SentimentRecord.created_at.desc()).all()
    db.close()
    
    if len(records) == 0:
        print("⚠️  没有历史记录，请先运行情感分析演示")
        return
    
    print(f"基于 {len(records)} 条历史记录进行评估...\n")
    
    # 转换为字典列表
    records_dicts = [record.to_dict() for record in records]
    
    try:
        assessment = llm_service.assess_mental_health(records_dicts)
        
        print(f"总体健康得分: {assessment['overall_score']}/100")
        print(f"风险等级: {assessment['risk_level']}")
        
        print("\n主要关注点:")
        for concern in assessment['key_concerns']:
            print(f"  - {concern}")
        
        print("\n改善建议:")
        for rec in assessment['recommendations']:
            print(f"  - {rec}")
        
        print(f"\n详细分析:\n{assessment['detailed_analysis']}")
        
        print("\n✅ 评估完成")
    except Exception as e:
        print(f"❌ 评估失败: {e}")


def demo_statistics():
    """演示统计功能"""
    print_section("5. 数据统计演示")
    
    # 从数据库获取记录
    db = SessionLocal()
    records = db.query(SentimentRecord).filter(
        SentimentRecord.user_id == "demo_user"
    ).all()
    db.close()
    
    if len(records) == 0:
        print("⚠️  没有记录数据")
        return
    
    # 统计
    total = len(records)
    positive = sum(1 for r in records if r.sentiment == 'positive')
    negative = sum(1 for r in records if r.sentiment == 'negative')
    neutral = sum(1 for r in records if r.sentiment == 'neutral')
    avg_intensity = sum(r.intensity or 0 for r in records) / total
    
    print(f"总记录数: {total}")
    print(f"积极情感: {positive} ({positive/total*100:.1f}%)")
    print(f"消极情感: {negative} ({negative/total*100:.1f}%)")
    print(f"中性情感: {neutral} ({neutral/total*100:.1f}%)")
    print(f"平均情感强度: {avg_intensity:.2f}")
    
    # 情绪统计
    emotion_counts = {}
    for record in records:
        try:
            emotions = json.loads(record.emotions) if isinstance(record.emotions, str) else record.emotions
            for emotion in emotions:
                name = emotion.get('name', 'unknown')
                emotion_counts[name] = emotion_counts.get(name, 0) + 1
        except:
            pass
    
    print("\n最常见的情绪:")
    for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {emotion}: {count}次")


def main():
    """主函数"""
    print("\n" + "🌟"*30)
    print("  智能情感分析与心理健康辅助系统 - 功能演示")
    print("🌟"*30)
    
    # 检查环境变量
    if not os.getenv('OPENAI_API_KEY'):
        print("\n❌ 错误: 未找到 OPENAI_API_KEY")
        print("请在 .env 文件中配置你的 OpenAI API Key")
        sys.exit(1)
    
    print("\n✅ 环境配置正常\n")
    
    # 运行演示
    try:
        # 1. 情感分析
        demo_sentiment_analysis()
        
        # 2. RAG知识检索
        demo_rag_knowledge()
        
        # 3. 建议生成
        demo_suggestion_generation()
        
        # 4. 健康评估
        demo_health_assessment()
        
        # 5. 统计
        demo_statistics()
        
        print_section("演示完成")
        print("✅ 所有功能演示完毕！")
        print("\n接下来你可以:")
        print("  1. 启动后端服务: python main.py")
        print("  2. 启动前端应用: cd ../frontend && npm start")
        print("  3. 访问 http://localhost:3000 使用完整应用")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  演示被中断")
    except Exception as e:
        print(f"\n\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
