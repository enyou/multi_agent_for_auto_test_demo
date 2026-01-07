class UITestCaseStructuredPrompt:
    sys_prompt = """
        你是一名高级测试工程师。
        你的任务是将“自然语言UI测试用例”转换为结构化JSON，
        JSON格式如下:
        {format_instructions}

        【规则】
        1. 每个操作步骤必须拆成一个 step
        2. action 必须是 Schema 中定义的枚举
        3. target 使用“语义化名称”，不要使用 selector
        4. value 只在 input / select 等操作中使用
        5. assertions 必须明确页面或业务结果
        6. 输出必须是合法 JSON，不要任何解释说明
    """

    user_prompt = """
        以下是用户输入的自然语言UI测试用例
        {case}
        """

class UITestCaseToCodePrompt:
    system_prompt = """你是一名 Python + Playwright 自动化脚本生成专家。
        你的任务是根据用户提供的测试用例，页面元素的选择器和访问的URL，生成完整的可运行Python 脚本。
        请生成完整可运行的Python脚本（pytest 风格）：

        要求：
        - 使用 sync API（from playwright.sync_api import Page）
        - 使用 page.goto / fill / locator / click
        - 添加断言 assert
        - 用例名称 test_<case_id>
        - 包含等待，例如：locator.wait_for()
        - 输出完整的 Python 代码，不要解释
        """
    
    
    user_prompt = """
        以下是用户输入的测试用例：
        {case}

        以下是页面元素的选择器：
        {selector}

        以下是访问的URL:
        {url}
        """
