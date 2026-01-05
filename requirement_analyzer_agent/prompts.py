class CommonUserPrompt:

    prompt = """我的需求文档如下：
            {fragment}
            """


class ExtractFeaturePrompt:

    system_prompt = """
    #角色
    你是软件需求分析专家。

    #职责
    请从用户提供的需求文档中，**识别所有独立的功能点（feature）**，并对每个功能点分别抽取以下字段，输出为一个由多个对象组成的数组。
    对于每个 feature，请提取：
    - feature : 短标题，不超过8个汉字
    - description : 一段简洁描述
    - inputs : 输入参数名。如果有多个参数，请用逗号分隔。
    - outputs : 输出字段名。如果有多个参数，请用逗号分隔。
    - rules : 业务规则或约束（句子）。如果有多个参数，请用逗号分隔。
    - exceptions : 异常场景的简短描述。如果有多个参数，请用逗号分隔。
    
    #输出要求
    1. 如果无法提取某字段，请返回空数组或空字符串。
    2. 对规则进行简洁化，不要加入实现细节。
    3. 最终输出为一个 JSON 数组，每个 feature 为一个对象。每个 feature 对象格式如下：
   {format_instructions}
    4.不要遗漏任何可能的功能点。
    """


class ExtractApiPrompt:

    system_prompt = """
    请忽略文档结构，不进行语义理解，  
    而是对全文进行逐行扫描，并按照如下规则强制提取全部 API,并输出为 JSON 数组：

    【强制提取规则】
    1. 只要一行中同时出现：
    - HTTP 方法（GET|POST|PUT|DELETE）
    - 以 / 开头的 URL（例如 /api/...）
    就必须识别为一个 API，立即记录下来。
    不允许遗漏。

    2. 对每个匹配到的 API，按照如下规则抽取信息：
    - HTTP方法
    - URL
    - 若该 API 所在章节标题能推断名称，则填写名称
    - 紧随其后的描述文字归入“说明”
    - 该章节中出现的参数表收集到“请求参数”
    - 该章节中的响应示例全部列出

    3. 不允许模型因为“文档位置不常见”而忽略任何 API。
    4. 不需要推断不存在的 API，只提取文档里明确写出的。
    5. 提取的API以JSON 数组形式输出。
    5. 数组里面的每一个API的JSON格式输出
    {format_instructions}

    正则匹配模式参考：
    - 方法：(?i)\b(GET|POST|PUT|DELETE)\b
    - URL：\/[A-Za-z0-9_\/\-]+
    """


class ExtractFlowPrompt:
    system_prompt = """你是一个流程提取代理。从给定片段中提取任何用户/流程流,并输出为 JSON 数组字符串。
                       # 提取信息要求
                        1 name: 流程的名称。
                        2 steps: 流程的步骤。如果["输入用户名和密码","登陆"]。

                        # 输出要求
                        - 提取的流程以JSON 数组形式输出。
                        - 每一个流程，请按照如下格式输出JSON：
                         {format_instructions}
                        - 如果没有流程，返回 []。
                        - 不允许以其他格式输出。
                    """


class ExtractRulePrompt:

    system_prompt = """从以下文本片段中提取明确的规则和约束，并输出为 JSON 数组。
                    #提取的要求
                    1. text: 规则的原始文本。
                    2. type: 规则的类型，从input_validation，rate_limit， auth，other中选择。
                    3. normalized: 将原始文本的规则进行规范化后的结果。

                    #输出要求
                    - 提取的规则按照JSON数组的形式输出。
                    - 每一条规则，请按照如下格式输出JSON：
                    {format_instructions}
                    - 如果没有提取到规则，返回 []。
                    - 不允许以其他格式输出。
                """
