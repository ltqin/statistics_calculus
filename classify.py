import pandas as pd
import re
import jieba
from collections import Counter

class CommentAnalyzer:
    def __init__(self):
        # 定义关键词词典
        self.negative_keywords = [
            '车门打不开', '门把手', '设计缺陷', '安全隐患', '电池起火', '自燃', '安全气囊',
            '救援', '封号', '删视频', '压热度', 'OTA', '虚假宣传', '召回', '垃圾', '坑人',
            '害人', '火化', '烧死', '骨灰', '活活烧死', '微动开关', '机械结构', '减配',
            '不负责任', '欺骗', '忽悠', '问题车', '缺陷', '危险', '可怕', '不敢买',
            '避雷', '远离', '不成熟', '实验品', '小白鼠', '工业垃圾', '死亡', '致命'
        ]
        
        self.positive_keywords = [
            '酒驾', '超速', '活该', '自作自受', '不怪车', '车没问题', '小米没问题',
            '雷总没问题', '支持小米', '米粉', '人的问题', '驾驶问题', '违规', '违法',
            '该死', '罪有应得', '自找的', '不负责', '危害社会', '庆幸', '好事',
            '清除垃圾', '为民除害', '死有余辜', '喝酒开车', '醉驾', '飙车'
        ]
        
        self.neutral_keywords = [
            '都有问题', '人车都有问题', '客观', '理性', '分析', '讨论', '思考',
            '疑问', '好奇', '不了解', '不确定', '可能', '或许', '大概', '据说',
            '听说', '有待', '等官方', '调查结果', '国标', '标准', '规范'
        ]

    def preprocess_text(self, text):
        """文本预处理"""
        if pd.isna(text):
            return ""
        # 去除特殊字符和表情符号
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'@\S+', '', text)
        text = re.sub(r'[^\w\u4e00-\u9fff]', ' ', text)
        return text.strip()

    def analyze_sentiment(self, text):
        """分析评论情感倾向"""
        text = self.preprocess_text(text)
        if not text:
            return "中立"
        
        # 分词
        words = list(jieba.cut(text))
        
        # 统计关键词出现次数
        neg_count = sum(1 for word in words for keyword in self.negative_keywords if keyword in word or word in keyword)
        pos_count = sum(1 for word in words for keyword in self.positive_keywords if keyword in word or word in keyword)
        neu_count = sum(1 for word in words for keyword in self.neutral_keywords if keyword in word or word in keyword)
        
        # 基于规则分类
        if neg_count > pos_count and neg_count > 0:
            return "反对"
        elif pos_count > neg_count and pos_count > 0:
            return "支持"
        elif neu_count > 0 or (neg_count == 0 and pos_count == 0):
            return "中立"
        else:
            return "中立"

    def classify_comments(self, df):
        """对DataFrame中的评论进行分类"""
        results = []
        
        for idx, row in df.iterrows():
            comment = row['评论内容']
            user = row['用户']
            
            sentiment = self.analyze_sentiment(comment)
            
            results.append({
                '用户': user,
                '评论内容': comment,
                '点赞数': row['点赞数'],
                '评论时间': row['评论时间'],
                '观点分类': sentiment
            })
            
            # 打印进度
            if idx % 100 == 0:
                print(f"已处理 {idx}/{len(df)} 条评论")
        
        return pd.DataFrame(results)

    def analyze_results(self, result_df):
        """分析分类结果"""
        total = len(result_df)
        sentiment_counts = result_df['观点分类'].value_counts()
        
        print("=" * 50)
        print("评论观点分类结果统计")
        print("=" * 50)
        
        for sentiment, count in sentiment_counts.items():
            percentage = (count / total) * 100
            print(f"{sentiment}者: {count}条 ({percentage:.2f}%)")
        
        print(f"总计: {total}条评论")
        
        # 各观点的高赞评论
        print("\n各观点的高赞评论 (前5):")
        for sentiment in ['反对', '支持', '中立']:
            high_likes = result_df[result_df['观点分类'] == sentiment].nlargest(5, '点赞数')
            print(f"\n{sentiment}者高赞评论:")
            for idx, row in high_likes.iterrows():
                print(f"  点赞{row['点赞数']}: {row['评论内容'][:50]}...")

def main():
    # 读取数据
    try:
        df = pd.read_csv('bilibili_comments_深度分析小米成都事故敲响安全警钟_20251110_160928.csv', encoding='utf-8')
    except:
        df = pd.read_csv('bilibili_comments_深度分析小米成都事故敲响安全警钟_20251110_160928.csv', encoding='gbk')
    
    print(f"成功读取 {len(df)} 条评论")
    
    # 初始化分析器
    analyzer = CommentAnalyzer()
    
    # 进行分类
    print("开始对评论进行分类...")
    result_df = analyzer.classify_comments(df)
    
    # 分析结果
    analyzer.analyze_results(result_df)
    
    # 保存结果
    output_file = 'classified_comments.csv'
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n分类结果已保存至: {output_file}")
    
    # 显示一些示例
    print("\n分类示例:")
    sample_results = result_df.sample(10)[['用户', '评论内容', '观点分类']]
    for idx, row in sample_results.iterrows():
        print(f"\n{row['观点分类']} - {row['用户']}: {row['评论内容'][:60]}...")

if __name__ == "__main__":
    main()