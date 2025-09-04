import time
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import asyncio
import os
from bs4 import BeautifulSoup


def extract_author_institutions(html):
    """
    从HTML中提取作者单位信息
    
    参数:
        html (str): 包含作者单位信息的HTML片段
        
    返回:
        list: 作者单位列表
    """
    soup = BeautifulSoup(html, 'html.parser')
    institutions = []
    
    # 查找所有class为'author'的h3标签
    for author_section in soup.find_all('h3', class_='author'):
        # 跳过包含作者姓名的部分（通常有id="authorpart"）
        if 'id' in author_section.attrs and 'authorpart' in author_section['id']:
            continue
            
        # 提取单位信息
        for span in author_section.find_all('span'):
            a_tag = span.find('a')
            if a_tag:
                # 获取纯文本并去除首尾空白
                institution = a_tag.get_text(strip=True)
                if institution:  # 确保不是空字符串
                    institutions.append(institution)
                    
    return institutions

async def async_post_email(title: str, recipient: str, text: str) -> dict:
    search_url = "https://mail.bupt.edu.cn/"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            timeout=60000,
            args=['--start-maximized']
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = await context.new_page()
        
        try:
            # ========== 登录 ==========
            await page.goto(search_url, timeout=60000)
            await page.wait_for_timeout(2000)
            
            username = "liuzl"
            password = os.getenv("BUPT_EMAIL_PASSWORD")
            
            await page.fill('#qquin', username)
            await page.fill('#pp', password)
            await page.click('.login_btn')
            
            # 等待登录完成
            await page.wait_for_selector('#composebtn', state='visible', timeout=10000)
            
            # ========== 写信 ==========
            await page.click('#composebtn')
            
            # 等待写信窗口加载
            await page.wait_for_timeout(4000)
            # await asyncio.sleep(4)
            # 输入收件人
            # await asyncio.sleep(2)
            compose_frame = None
            for frame in page.frames:
                if "compose_wedrive" in frame.url:
                    compose_frame = frame
                    break
            
            if compose_frame is None:
                raise Exception("没有找到写信 mainFrame")
            # ====== 输入收件人 ======
# 注意：用 toAreaCtrl 里面的 input[type=input]
            await compose_frame.fill('#toAreaCtrl input[type="input"]', recipient)
            # await compose_frame.keyboard.press("Tab")   # 触发失焦，让系统把地址写入 textarea#to


            await asyncio.sleep(0.5)
            await page.keyboard.press('Tab')
            await asyncio.sleep(0.5)
            await page.keyboard.type(title)
            await asyncio.sleep(0.5)
            await page.keyboard.press('Tab')
            await page.keyboard.type(text)
            
            
            # ========== 发送邮件 ==========
            await compose_frame.wait_for_selector('input[name="sendbtn"]', state="visible", timeout=15000)
            await compose_frame.click('input[name="sendbtn"]')
            await asyncio.sleep(5)
            return {"status": "success", "message": "邮件发送成功"}

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            await page.screenshot(path='error_debug.png')
            return {"status": "error", "message": f"操作失败: {str(e)}"}
        finally:
            await browser.close()
        
def sync_post_email(title: str, recipient: str, text: str) -> dict:
    search_url = "https://mail.bupt.edu.cn/"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            timeout=60000,
            args=['--start-maximized']
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = context.new_page()
        
        try:
            # ========== 登录 ==========
            page.goto(search_url, timeout=60000)
            page.wait_for_timeout(2000)
            
            username = "liuzl"
            password = os.getenv("BUPT_EMAIL_PASSWORD")
            
            page.fill('#qquin', username)
            page.fill('#pp', password)
            page.click('.login_btn')
            
            # 等待登录完成
            page.wait_for_selector('#composebtn', state='visible', timeout=10000)
            
            # ========== 写信 ==========
            page.click('#composebtn')
            
            
            
            page.wait_for_timeout(4000)
            # time.sleep(4)
            
            # 输入收件人
            compose_frame = None
            for frame in page.frames:
                if "compose_wedrive" in frame.url:
                    compose_frame = frame
                    break
            
            if compose_frame is None:
                raise Exception("没有找到写信 mainFrame")
            
            # ====== 输入收件人 ======
            compose_frame.fill('#toAreaCtrl input[type="input"]', recipient)
            
            time.sleep(0.5)
            page.keyboard.press('Tab')
            time.sleep(0.5)
            page.keyboard.type(title)
            time.sleep(0.5)
            page.keyboard.press('Tab')
            page.keyboard.type(text)
            
            # ========== 发送邮件 ==========
            compose_frame.wait_for_selector('input[name="sendbtn"]', state="visible", timeout=15000)
            compose_frame.click('input[name="sendbtn"]')
            time.sleep(5)
            return {"status": "success", "message": "邮件发送成功"}

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            page.screenshot(path='error_debug.png')
            return {"status": "error", "message": f"操作失败: {str(e)}"}
        finally:
            browser.close()
async def main():
    return await async_post_email("test", "zilong.liu@shopee.com;", "test_text")

if __name__ == "__main__":
    # result = asyncio.run(main())
    # print(result)
    result = sync_post_email("test", "zilong.liu@shopee.com;", "test_text")
    print(result)