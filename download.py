import requests
import json
import csv
import time
import re
from datetime import datetime
import os

class BilibiliCommentDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Origin': 'https://www.bilibili.com'
        })
        self.comments = []
        
    def clean_text(self, text):
        """清理文本中的多余空格和特殊字符"""
        if not text:
            return ""
        
        # 移除多余空格（包括全角空格）
        text = re.sub(r'[\s\u3000]+', ' ', text)
        
        # 移除首尾空格
        text = text.strip()
        
        return text
    
    def load_cookies_from_file(self, cookie_file="b站cookie.txt"):
        """从文件加载Cookie"""
        try:
            if not os.path.exists(cookie_file):
                print(f"❌ Cookie文件 '{cookie_file}' 不存在")
                return False
                
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # 将Cookie添加到session
            for cookie in cookies_data:
                self.session.cookies.set(
                    cookie['name'],
                    cookie['value'],
                    domain=cookie.get('domain', '.bilibili.com'),
                    path=cookie.get('path', '/')
                )
            
            print(f"✅ 已加载 {len(cookies_data)} 个Cookie")
            return True
        except Exception as e:
            print(f"❌ 加载Cookie失败: {e}")
            return False
    
    def get_video_aid(self, bvid):
        """通过BV号获取视频aid"""
        try:
            url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            response = self.session.get(url)
            data = response.json()
            
            if data['code'] == 0:
                aid = data['data']['aid']
                title = data['data']['title']
                print(f"✅ 获取视频信息成功: {title}")
                print(f"📹 视频AID: {aid}")
                return aid, title
            else:
                print(f"❌ 获取视频信息失败: {data['message']}")
                return None, None
        except Exception as e:
            print(f"❌ 获取视频AID时出错: {e}")
            return None, None
    
    def get_comments_by_api(self, aid, max_comments=1000):
        """通过API获取评论 - 增加最大评论数"""
        try:
            page = 1
            total_comments = 0
            
            while total_comments < max_comments:
                url = f"https://api.bilibili.com/x/v2/reply?type=1&oid={aid}&sort=2&pn={page}&ps=20"
                
                response = self.session.get(url)
                data = response.json()
                
                if data['code'] != 0:
                    print(f"❌ 获取评论失败: {data.get('message', '未知错误')}")
                    break
                
                if 'data' not in data or 'replies' not in data['data']:
                    print("❌ 评论数据格式异常")
                    break
                
                replies = data['data']['replies']
                if not replies:
                    print("✅ 已获取所有评论")
                    break
                
                # 处理当前页的评论
                for reply in replies:
                    if total_comments >= max_comments:
                        break
                    
                    # 清理用户昵称和评论内容
                    user_name = self.clean_text(reply['member']['uname'])
                    content = self.clean_text(reply['content']['message'])
                    
                    comment = {
                        "user": user_name,
                        "content": content,
                        "likes": reply['like'],
                        "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reply['ctime'])),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    self.comments.append(comment)
                    total_comments += 1
                
                print(f"📝 第 {page} 页获取了 {len(replies)} 条评论，总计 {total_comments} 条")
                
                # 显示当前页的前几条评论作为预览
                if page == 1 and replies:
                    print("\n📋 评论预览:")
                    for i, reply in enumerate(replies[:3], 1):
                        user_name = self.clean_text(reply['member']['uname'])
                        content = self.clean_text(reply['content']['message'])
                        print(f"  {i}. [{user_name}] {content}")
                
                page += 1
                time.sleep(0.5)  # 避免请求过快
                
            return total_comments
            
        except Exception as e:
            print(f"❌ 获取评论时出错: {e}")
            return 0
    
    def get_hot_comments(self, aid, max_comments=50):
        """获取热门评论"""
        try:
            url = f"https://api.bilibili.com/x/v2/reply?type=1&oid={aid}&sort=1&ps={max_comments}&pn=1"
            
            response = self.session.get(url)
            data = response.json()
            
            if data['code'] == 0 and 'data' in data and 'replies' in data['data']:
                replies = data['data']['replies']
                
                for reply in replies:
                    # 清理用户昵称和评论内容
                    user_name = self.clean_text(reply['member']['uname'])
                    content = self.clean_text(reply['content']['message'])
                    
                    comment = {
                        "user": user_name,
                        "content": content,
                        "likes": reply['like'],
                        "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reply['ctime'])),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "is_hot": True
                    }
                    
                    self.comments.append(comment)
                
                print(f"🔥 获取了 {len(replies)} 条热门评论")
                return len(replies)
            else:
                print("❌ 获取热门评论失败")
                return 0
                
        except Exception as e:
            print(f"❌ 获取热门评论时出错: {e}")
            return 0
    
    def remove_duplicate_comments(self):
        """去除重复评论"""
        if not self.comments:
            return 0
            
        original_count = len(self.comments)
        
        # 基于用户和内容去重
        seen = set()
        unique_comments = []
        
        for comment in self.comments:
            # 创建唯一标识
            identifier = (comment["user"], comment["content"])
            
            if identifier not in seen:
                seen.add(identifier)
                unique_comments.append(comment)
        
        removed_count = original_count - len(unique_comments)
        self.comments = unique_comments
        
        if removed_count > 0:
            print(f"🧹 已移除 {removed_count} 条重复评论")
        
        return removed_count
    
    def save_comments_to_file(self, filename=None, video_title="B站视频评论"):
        """将评论保存到文件 - 使用UTF-8 BOM编码解决Excel乱码"""
        if not self.comments:
            print("❌ 没有评论可保存")
            return
            
        # 去除重复评论
        self.remove_duplicate_comments()
            
        if not filename:
            # 使用视频标题作为文件名的一部分
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bilibili_comments_{safe_title}_{timestamp}"
            if len(filename) > 100:  # 限制文件名长度
                filename = f"bilibili_comments_{timestamp}"
        
        # 保存为JSON（保持UTF-8编码）
        json_filename = f"{filename}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                "video_title": video_title,
                "video_url": f"https://www.bilibili.com/video/BV19848ztEjy",
                "comments": self.comments,
                "count": len(self.comments),
                "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, f, ensure_ascii=False, indent=2)
        
        # 保存为CSV - 使用UTF-8 BOM编码解决Excel乱码问题
        csv_filename = f"{filename}.csv"
        with open(csv_filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["用户", "评论内容", "点赞数", "评论时间", "采集时间"])
            for comment in self.comments:
                writer.writerow([
                    comment["user"],
                    comment["content"],
                    comment["likes"],
                    comment["time"],
                    comment["timestamp"]
                ])
        
        print(f"💾 评论已保存到文件:")
        print(f"   JSON: {json_filename} (UTF-8编码)")
        print(f"   CSV: {csv_filename} (UTF-8 BOM编码，Excel可正常显示)")
    
    def download_comments(self, bvid, max_comments=1000, include_hot=True):
        """下载评论的主函数 - 增加默认最大评论数"""
        print(f"🎬 开始下载视频 {bvid} 的评论...")
        
        # 加载Cookie
        self.load_cookies_from_file("b站cookie.txt")
        
        # 获取视频AID和标题
        aid, video_title = self.get_video_aid(bvid)
        if not aid:
            print("❌ 无法获取视频信息，程序终止")
            return
        
        # 获取热门评论
        if include_hot:
            self.get_hot_comments(aid, min(50, max_comments))
        
        # 获取普通评论
        remaining_comments = max_comments - len(self.comments)
        if remaining_comments > 0:
            self.get_comments_by_api(aid, remaining_comments)
        
        # 保存评论
        if self.comments:
            self.save_comments_to_file(video_title=video_title)
            
            # 显示统计信息
            print(f"\n📊 下载完成!")
            print(f"   视频标题: {video_title}")
            print(f"   总评论数: {len(self.comments)}")
            print(f"   热门评论: {len([c for c in self.comments if c.get('is_hot', False)])}")
            
            # 显示前几条评论作为预览
            print(f"\n📋 评论预览:")
            for i, comment in enumerate(self.comments[:5], 1):
                hot_tag = "🔥 " if comment.get('is_hot', False) else ""
                print(f"  {i}. {hot_tag}[{comment['user']}] {comment['content']}")
            
            if len(self.comments) > 5:
                print(f"  ... 还有 {len(self.comments)-5} 条评论")
        else:
            print("❌ 未获取到任何评论")


def clean_existing_csv(input_file, output_file=None):
    """清理现有的CSV文件中的多余空格"""
    if output_file is None:
        output_file = input_file.replace('.csv', '_cleaned.csv')
    
    try:
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # 清理每一行的数据
        cleaned_rows = []
        for row in rows:
            cleaned_row = [re.sub(r'[\s\u3000]+', ' ', cell).strip() for cell in row]
            cleaned_rows.append(cleaned_row)
        
        # 保存清理后的文件
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(cleaned_rows)
        
        print(f"✅ 已清理文件: {input_file} -> {output_file}")
        return True
    except Exception as e:
        print(f"❌ 清理文件失败: {e}")
        return False


def main():
    downloader = BilibiliCommentDownloader()
    
    try:
        # 下载指定BV号的评论 - 可以设置更大的数值
        bvid = "BV19848ztEjy"
        
        # 询问用户想要获取多少条评论
        try:
            user_input = input("请输入要获取的评论数量 (默认1000): ").strip()
            max_comments = int(user_input) if user_input else 1000
        except ValueError:
            print("输入无效，使用默认值1000")
            max_comments = 1000
            
        downloader.download_comments(bvid, max_comments=max_comments, include_hot=True)
        
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()