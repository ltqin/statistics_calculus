from selenium import webdriver
import json
import time

def save_bilibili_cookie():
    # 启动浏览器（不要使用无头模式，以便手动登录）
    browser = webdriver.Chrome()
    
    try:
        # 打开B站首页
        browser.get("https://www.bilibili.com")
        print("请在浏览器中手动登录B站账号...")
        print("登录完成后，回到控制台按回车键继续...")
        
        # 等待用户手动登录
        input()
        
        # 获取所有Cookie
        cookies = browser.get_cookies()
        
        # 将Cookie保存到文件
        with open("b站cookie.txt", "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=4)
        
        print(f"Cookie已保存到 b站cookie.txt 文件，共 {len(cookies)} 个Cookie")
        
    except Exception as e:
        print(f"出错: {e}")
    finally:
        # 关闭浏览器
        browser.quit()

# 执行函数
save_bilibili_cookie()