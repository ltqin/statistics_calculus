import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertModel
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 设置设备
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用设备: {device}")

class CommentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class SimpleBERTClassifier(nn.Module):
    def __init__(self, n_classes=3):
        super(SimpleBERTClassifier, self).__init__()
        self.bert = BertModel.from_pretrained('bert-base-chinese')
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(self.bert.config.hidden_size, n_classes)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        output = self.dropout(pooled_output)
        return self.classifier(output)

class DeepLearningAnalyzer:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
        self.model = None
        self.label_map = {'反对': 0, '中立': 1, '支持': 2}
        self.reverse_label_map = {v: k for k, v in self.label_map.items()}
    
    def preprocess_text(self, text):
        """文本预处理"""
        if pd.isna(text):
            return ""
        text = str(text)
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'@\S+', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def prepare_training_data(self, df):
        """准备训练数据（使用规则方法生成伪标签）"""
        print("准备训练数据...")
        
        texts = []
        labels = []
        
        for idx, row in df.iterrows():
            if idx % 500 == 0:
                print(f"处理进度: {idx}/{len(df)}")
            
            text = self.preprocess_text(row['评论内容'])
            if len(text) < 5:  # 跳过太短的文本
                continue
                
            texts.append(text)
            
            # 使用规则方法生成伪标签
            sentiment = self.rule_based_classification(text)
            labels.append(self.label_map[sentiment])
        
        return texts, labels
    
    def rule_based_classification(self, text):
        """规则方法生成伪标签"""
        text_lower = text.lower()
        
        negative_keywords = ['车门打不开', '设计缺陷', '安全隐患', '电池起火', '自燃', '虚假宣传']
        positive_keywords = ['酒驾', '超速', '人的问题', '驾驶问题', '支持小米']
        
        neg_count = sum(1 for word in negative_keywords if word in text_lower)
        pos_count = sum(1 for word in positive_keywords if word in text_lower)
        
        if neg_count > pos_count:
            return '反对'
        elif pos_count > neg_count:
            return '支持'
        else:
            return '中立'
    
    def train_model(self, texts, labels, epochs=2, batch_size=8):
        """训练深度学习模型"""
        print("开始训练深度学习模型...")
        
        # 分割数据
        from sklearn.model_selection import train_test_split
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        
        # 创建数据集
        train_dataset = CommentDataset(train_texts, train_labels, self.tokenizer)
        val_dataset = CommentDataset(val_texts, val_labels, self.tokenizer)
        
        # 创建数据加载器
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        # 初始化模型
        self.model = SimpleBERTClassifier(n_classes=3)
        self.model.to(device)
        
        # 优化器和损失函数
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=2e-5)
        criterion = nn.CrossEntropyLoss()
        
        # 训练循环
        for epoch in range(epochs):
            self.model.train()
            total_loss = 0
            
            for batch in train_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                
                optimizer.zero_grad()
                outputs = self.model(input_ids, attention_mask)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            # 验证
            val_accuracy = self.evaluate_model(val_loader)
            print(f'Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(train_loader):.4f}, Val Accuracy: {val_accuracy:.2f}%')
        
        print("模型训练完成!")
    
    def evaluate_model(self, val_loader):
        """评估模型"""
        self.model.eval()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                
                outputs = self.model(input_ids, attention_mask)
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        return 100 * correct / total
    
    def predict(self, texts):
        """使用深度学习模型预测"""
        if self.model is None:
            raise ValueError("请先训练模型")
        
        self.model.eval()
        predictions = []
        probabilities = []
        
        with torch.no_grad():
            for text in texts:
                text = self.preprocess_text(text)
                encoding = self.tokenizer(
                    text,
                    add_special_tokens=True,
                    max_length=128,
                    padding='max_length',
                    truncation=True,
                    return_tensors='pt'
                )
                
                input_ids = encoding['input_ids'].to(device)
                attention_mask = encoding['attention_mask'].to(device)
                
                outputs = self.model(input_ids, attention_mask)
                probs = torch.softmax(outputs, dim=1)
                _, predicted = torch.max(outputs, 1)
                
                predictions.append(self.reverse_label_map[predicted.item()])
                probabilities.append(probs.cpu().numpy()[0])
        
        return predictions, probabilities
    
    def analyze_comments_deep_learning(self, df, sample_size=500):
        """使用深度学习分析评论"""
        print("使用深度学习方法分析评论...")
        
        if sample_size and len(df) > sample_size:
            df = df.sample(sample_size, random_state=42)
            print(f"采样 {sample_size} 条评论进行深度学习分析")
        
        # 准备数据
        texts = [self.preprocess_text(row['评论内容']) for _, row in df.iterrows()]
        
        # 训练模型
        training_texts, training_labels = self.prepare_training_data(df)
        self.train_model(training_texts, training_labels, epochs=2, batch_size=8)
        
        # 预测
        predictions, probabilities = self.predict(texts)
        
        # 整理结果
        results = []
        sentiment_counts = {'反对': 0, '中立': 0, '支持': 0}
        
        for idx, (pred, prob) in enumerate(zip(predictions, probabilities)):
            results.append({
                '用户': df.iloc[idx]['用户'],
                '评论内容': df.iloc[idx]['评论内容'][:100] + '...' if len(df.iloc[idx]['评论内容']) > 100 else df.iloc[idx]['评论内容'],
                'AI观点分类': pred,
                '反对概率': f"{prob[0]:.3f}",
                '中立概率': f"{prob[1]:.3f}",
                '支持概率': f"{prob[2]:.3f}",
                '置信度': f"{max(prob):.3f}",
                '点赞数': df.iloc[idx].get('点赞数', 0)
            })
            
            sentiment_counts[pred] += 1
        
        return pd.DataFrame(results), sentiment_counts

def main_deep_learning():
    """深度学习版本的主函数"""
    # 读取数据
    try:
        df = pd.read_csv('bilibili_comments_深度分析小米成都事故敲响安全警钟_20251110_160928.csv', 
                        encoding='utf-8')
    except:
        try:
            df = pd.read_csv('bilibili_comments_深度分析小米成都事故敲响安全警钟_20251110_160928.csv', 
                           encoding='gbk')
        except Exception as e:
            print(f"读取文件失败: {e}")
            return
    
    print(f"成功读取 {len(df)} 条评论")
    
    # 初始化深度学习分析器
    analyzer = DeepLearningAnalyzer()
    
    # 使用深度学习分析
    result_df, sentiment_counts = analyzer.analyze_comments_deep_learning(df, sample_size=500)
    
    # 输出结果
    print("\n" + "="*60)
    print("              深度学习评论分析报告")
    print("="*60)
    
    total = len(result_df)
    print(f"\n分析评论总数: {total}")
    
    print("\n观点分布:")
    for sentiment, count in sentiment_counts.items():
        percentage = (count / total) * 100
        print(f"  {sentiment}: {count}条 ({percentage:.1f}%)")
    
    # 保存结果
    output_file = 'deep_learning_analysis_results.csv'
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n深度学习分析结果已保存至: {output_file}")
    
    # 显示示例
    print("\n分类示例 (随机3条):")
    sample_results = result_df.sample(min(3, len(result_df)))
    for _, row in sample_results.iterrows():
        print(f"\n{row['AI观点分类']} (置信度: {row['置信度']})")
        print(f"  反对概率: {row['反对概率']}, 中立概率: {row['中立概率']}, 支持概率: {row['支持概率']}")
        print(f"  内容: {row['评论内容']}")

if __name__ == "__main__":
    main_deep_learning()