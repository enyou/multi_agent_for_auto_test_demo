#!/usr/bin/env python3
# element_extractor.py

import json
from typing import List, Any, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
from pathlib import Path
import datetime

from playwright.sync_api import sync_playwright, TimeoutError


@dataclass
class ElementInfo:
    """元素信息数据类"""
    tag_name: str
    element_type: str  # input, button, link, etc.
    id: Optional[str] = None
    name: Optional[str] = None
    class_list: List[str] = None
    placeholder: Optional[str] = None
    value: Optional[str] = None
    text: Optional[str] = None
    href: Optional[str] = None
    type: Optional[str] = None  # input type
    role: Optional[str] = None
    aria_label: Optional[str] = None
    data_testid: Optional[str] = None

    def __post_init__(self):
        if self.class_list is None:
            self.class_list = []


class ElementExtractor:
    """元素提取器"""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def navigate_to_url(self, url: str, wait_for_load: str = "networkidle", timeout: int = 30000):
        """导航到指定URL"""
        self.page = self.browser.new_page()

        # 设置视口大小
        self.page.set_viewport_size({"width": 1280, "height": 800})

        try:
            # 导航到页面
            response = self.page.goto(
                url, wait_until=wait_for_load, timeout=timeout)

            if response and response.status >= 400:
                print(f"警告: 页面返回状态码 {response.status}")

            # 等待页面完全加载
            self.page.wait_for_load_state(wait_for_load)

            # 滚动页面以加载懒加载元素
            self._scroll_page()

            return True
        except TimeoutError:
            print(f"超时: 页面加载时间超过 {timeout/1000} 秒")
            return False
        except Exception as e:
            print(f"导航到页面时出错: {e}")
            return False

    def _scroll_page(self):
        """滚动页面以加载所有元素"""
        try:
            # 模拟滚动到底部
            self.page.evaluate("""
                window.scrollTo(0, document.body.scrollHeight);
            """)
            self.page.wait_for_timeout(1000)  # 等待内容加载

            # 滚动回顶部
            self.page.evaluate("""
                window.scrollTo(0, 0);
            """)
        except:
            pass

    def get_all_elements(self) -> List[ElementInfo]:
        """获取所有相关元素信息（排除div、label、form和文本元素）"""
        if not self.page:
            raise ValueError("页面未加载，请先调用 navigate_to_url()")

        print("正在收集页面元素信息...")

        # 执行JavaScript收集元素信息（排除div、label、form和文本元素）
        elements_data = self.page.evaluate("""
            () => {
                // 定义需要收集的元素类型（只收集交互性元素，排除文本元素）
                const targetSelectors = [
                    'input', 'textarea', 'button', 'select', 'a',
                    '[role="button"]', '[role="link"]', '[role="textbox"]',
                    '[data-testid]', '[data-qa]', '[data-cy]', '[data-test]'
                ];
                
                // 合并所有选择器选中的元素
                const allElements = [];
                const seenElements = new Set();
                
                for (const selector of targetSelectors) {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => {
                        // 跳过不需要的元素类型
                        const tagName = el.tagName.toLowerCase();
                        const excludedTags = ['div', 'label', 'form', 'span', 'p', 
                                            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                                            'ul', 'li', 'ol', 'table', 'tr', 'td', 'th',
                                            'br', 'hr', 'b', 'i', 'em', 'strong', 'small',
                                            'mark', 'del', 'ins', 'sub', 'sup', 'pre', 'code'];
                        
                        if (excludedTags.includes(tagName)) {
                            return;
                        }
                        
                        if (!seenElements.has(el)) {
                            seenElements.add(el);
                            allElements.push(el);
                        }
                    });
                }
                
                // 补充：收集有id或class的元素（排除不需要的元素）
                const elementsWithIdOrClass = document.querySelectorAll('[id], [class]');
                elementsWithIdOrClass.forEach(el => {
                    // 跳过不需要的元素类型
                    const tagName = el.tagName.toLowerCase();
                    const excludedTags = ['div', 'label', 'form', 'span', 'p', 
                                        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                                        'ul', 'li', 'ol', 'table', 'tr', 'td', 'th',
                                        'br', 'hr', 'b', 'i', 'em', 'strong', 'small',
                                        'mark', 'del', 'ins', 'sub', 'sup', 'pre', 'code'];
                    
                    if (excludedTags.includes(tagName)) {
                        return;
                    }
                    
                    if (!seenElements.has(el)) {
                        seenElements.add(el);
                        allElements.push(el);
                    }
                });
                
                // 收集元素信息
                return allElements.map(el => {
                    return {
                        tagName: el.tagName.toLowerCase(),
                        id: el.id || null,
                        name: el.getAttribute('name'),
                        className: el.className || '',
                        classList: el.className ? el.className.trim().split(/\\s+/) : [],
                        placeholder: el.getAttribute('placeholder'),
                        value: el.value || el.textContent || el.innerText || null,
                        text: el.textContent ? el.textContent.trim().substring(0, 100) : null,
                        href: el.href || el.getAttribute('href'),
                        type: el.type || el.getAttribute('type'),
                        role: el.getAttribute('role'),
                        ariaLabel: el.getAttribute('aria-label'),
                        dataTestid: el.getAttribute('data-testid') || el.getAttribute('data-qa') || el.getAttribute('data-cy') || el.getAttribute('data-test')
                    };
                });
            }
        """)

        # 转换为ElementInfo对象
        elements = []
        for data in elements_data:
            element_info = ElementInfo(
                tag_name=data['tagName'],
                element_type=self._categorize_element(
                    data['tagName'], data['type'], data['role']),
                id=data['id'],
                name=data['name'],
                class_list=data['classList'],
                placeholder=data['placeholder'],
                value=data['value'],
                text=data['text'],
                href=data['href'],
                type=data['type'],
                role=data['role'],
                aria_label=data['ariaLabel'],
                data_testid=data['dataTestid']
            )
            elements.append(element_info)

        print(f"共收集到 {len(elements)} 个元素（已排除div、label、form和文本元素）")
        return elements

    def _categorize_element(self, tag_name: str, element_type: Optional[str], role: Optional[str]) -> str:
        """对元素进行分类"""
        if tag_name == 'input':
            return element_type if element_type else 'input'
        elif tag_name == 'button':
            return 'button'
        elif tag_name == 'textarea':
            return 'textarea'
        elif tag_name == 'select':
            return 'select'
        elif tag_name == 'a':
            return 'link'
        elif role:
            return f"role-{role}"
        else:
            return tag_name


def save_to_json(data: Any, filename: str):
    """保存数据到JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"数据已保存到: {filename}")


def run(url, write_to_json=False):
    """主函数 - 只有url一个参数"""

    # 使用默认值
    wait_time = 3  # 减少等待时间
    json_file = ""
    all_data = []
    if write_to_json:
        # 创建输出目录
        output_dir = './element_reports'
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(exist_ok=True)

        # 从URL生成文件名
        page_name = urlparse(url).path.replace("/", "").strip()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{page_name}_{timestamp}"

        # 文件路径
        json_file = output_dir_path / f"{base_filename}_elements.json"

    print(f"开始分析: {url}")

    try:
        # 使用ElementExtractor
        with ElementExtractor() as extractor:
            # 导航到页面
            if extractor.navigate_to_url(url):
                # 等待额外时间确保动态内容加载
                extractor.page.wait_for_timeout(wait_time * 1000)

                # 获取所有元素（已排除div、label、form和文本元素）
                elements = extractor.get_all_elements()
                all_data = [asdict(e) for e in elements]
                if write_to_json:
                    save_to_json(all_data, json_file)
                    print(f"\n数据已保存到: {json_file}")
            return all_data

    except Exception as e:
        print(f"分析过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run("http://localhost:5173/login?pass=123", True)
