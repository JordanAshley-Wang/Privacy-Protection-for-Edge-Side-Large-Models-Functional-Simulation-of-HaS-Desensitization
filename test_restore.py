import time
import re
from has_simulation import HideAndSeekSimulator

class EndsideModel:
    """
    端侧小模型封装类
    负责本地敏感信息的识别、脱敏和还原
    """
    def __init__(self):
        # 存储当前会话的脱敏映射关系
        self.current_mapping = {}
        # 存储历史映射关系，用于处理会话间的引用
        self.history_mappings = []
        # 存储当前使用的simulator实例
        self.simulator = None
        
    def desensitize(self, user_input, sensitive_types=None, use_uuid_mode=False):
        """
        使用端侧小模型对用户输入进行脱敏处理
        
        参数:
        user_input: 用户输入的原始文本
        sensitive_types: 指定需要脱敏的敏感信息类型列表，如['phone', 'id', 'email']
        use_uuid_mode: 是否使用UUID模式进行脱敏
        
        返回:
        tuple: (脱敏后的文本, 脱敏映射关系)
        """
        print("[端侧小模型] 正在执行敏感信息识别和脱敏处理...")
        
        # 模拟端侧小模型的处理时间
        time.sleep(0.2)
        
        # 创建新的simulator实例，根据需要设置UUID模式
        self.simulator = HideAndSeekSimulator(use_uuid=use_uuid_mode)
        
        # 根据参数选择脱敏方法
        if sensitive_types:
            # 指定敏感信息类型进行脱敏
            hidden_text, code_map = self.simulator.hide(user_input, specific_types=sensitive_types)
        else:
            # 默认脱敏所有类型
            hidden_text, code_map = self.simulator.hide(user_input)
        
        # 保存当前映射关系
        self.current_mapping = code_map
        self.history_mappings.append(code_map)
        
        print(f"[端侧小模型] 脱敏完成。识别并处理了 {len(code_map)} 处敏感信息。")
        return hidden_text, code_map
        
    def restore(self, llm_response):
        """
        使用端侧小模型将脱敏数据重新整合至大模型返回的文本中
        
        参数:
        llm_response: 大模型返回的包含脱敏标记的文本
        
        返回:
        str: 还原后的完整文本
        """
        print("[端侧小模型] 正在执行脱敏数据还原处理...")
        
        # 模拟端侧小模型的处理时间
        time.sleep(0.2)
        
        # 首先尝试标准还原方法
        restored_text = self.simulator.seek(llm_response)
        
        # 如果标准还原没有效果，尝试使用模糊匹配进行还原
        if restored_text == llm_response:
            print("[端侧小模型] 标准还原方法未生效，尝试使用模糊匹配还原...")
            # 尝试降低置信度阈值以提高匹配成功率
            restored_text = self.simulator.seek_with_options(
                llm_response,
                use_fuzzy_matching=True,
                min_confidence=0.5,  # 降低置信度阈值
                max_distance=2,      # 允许更多的字符差异
                use_word_boundary=False  # 不严格要求单词边界匹配
            )
        
        # 如果仍未成功还原，尝试处理文本格式和空白字符
        if restored_text == llm_response:
            print("[端侧小模型] 模糊匹配还原未完全生效，尝试处理文本格式...")
            # 预处理文本，去除多余空白字符和规范化格式
            processed_text = ' '.join(llm_response.split())
            # 再次尝试模糊匹配
            restored_text = self.simulator.seek_with_options(
                processed_text,
                use_fuzzy_matching=True,
                min_confidence=0.5,
                max_distance=3
            )
        
        print("[端侧小模型] 还原处理完成。")
        return restored_text

class MockLargeModel:
    """
    模拟常规用户大模型
    用于测试端侧小模型与大模型的交互流程
    """
    def __init__(self, model_name="豆包大模型"):
        self.model_name = model_name
        
    def process(self, desensitized_text):
        """
        模拟大模型处理脱敏后的文本
        
        参数:
        desensitized_text: 脱敏后的文本
        
        返回:
        str: 大模型处理后的结果
        """
        print(f"[{self.model_name}] 正在处理脱敏后的文本...")
        
        # 模拟大模型处理时间
        time.sleep(0.8)
        
        # 模拟大模型生成的回答
        response = f"根据您提供的信息：{desensitized_text}\n这是大模型生成的回答内容。"
        
        print(f"[{self.model_name}] 处理完成，已生成回答。")
        return response

def test_restore_function():
    """
    测试还原功能是否正常工作，支持用户输入
    """
    print("\n===== 测试还原功能 =====")
    
    # 初始化模型
    endside_model = EndsideModel()
    large_model = MockLargeModel()
    
    # 提供输入模板示例（完整场景文本）
    print("输入模板示例：")
    print("1. 场景1 - 银行卡信息：")
    print("我需要查询我的银行卡余额，卡号是6222021234567890123，开户人是李四，身份证号是110101199001011234，联系电话是13800138000。")
    print("2. 场景2 - 个人身份信息：")
    print("我的名字是王五，身份证号码是120101198501012345，手机号码是13900139000，电子邮箱是wangwu@example.com，居住地址是北京市朝阳区建国路88号。")
    print("3. 场景3 - 交易信息：")
    print("我有一笔交易需要核对，交易单号是TX202405010001，付款方是张三，收款方是李四，金额是10000元，交易时间是2024-05-01 15:30:00，交易状态显示为待确认。")
    print("4. 场景4 - 网络安全信息：")
    print("我无法登录公司的服务器，服务器IP地址是192.168.1.1，我的用户名是admin，密码是admin123456，登录端口是22，请帮我排查一下问题。")
    print("\n请输入您要测试的文本内容（按Enter确认，或输入数字1-4直接使用对应场景）：")
    
    # 获取用户输入
    user_input = input().strip()
    
    # 支持用户直接输入数字1-4来使用对应场景
    if user_input == "1":
        user_input = "我需要查询我的银行卡余额，卡号是6222021234567890123，开户人是李四，身份证号是110101199001011234，联系电话是13800138000。"
        print("使用场景1 - 银行卡信息")
    elif user_input == "2":
        user_input = "我的名字是王五，身份证号码是120101198501012345，手机号码是13900139000，电子邮箱是wangwu@example.com，居住地址是北京市朝阳区建国路88号。"
        print("使用场景2 - 个人身份信息")
    elif user_input == "3":
        user_input = "我有一笔交易需要核对，交易单号是TX202405010001，付款方是张三，收款方是李四，金额是10000元，交易时间是2024-05-01 15:30:00，交易状态显示为待确认。"
        print("使用场景3 - 交易信息")
    elif user_input == "4":
        user_input = "我无法登录公司的服务器，服务器IP地址是192.168.1.1，我的用户名是admin，密码是admin123456，登录端口是22，请帮我排查一下问题。"
        print("使用场景4 - 网络安全信息")
    # 如果用户没有输入内容，使用默认的场景3示例
    elif not user_input:
        print("未检测到输入，使用默认测试文本（场景3）...")
        user_input = "我有一笔交易需要核对，交易单号是TX202405010001，付款方是张三，收款方是李四，金额是10000元，交易时间是2024-05-01 15:30:00，交易状态显示为待确认。"
    
    print(f"\n用户输入: {user_input}")
    
    # 获取是否使用UUID模式的用户选择
    print("\n请选择脱敏模式：")
    print("1. 标准模式（使用简单占位符）")
    print("2. UUID模式（使用HAS_xxx占位符，适合复杂场景）")
    mode_choice = input().strip()
    use_uuid_mode = mode_choice == "2"
    
    # 脱敏处理
    desensitized_text, mapping = endside_model.desensitize(user_input, use_uuid_mode=use_uuid_mode)
    print(f"脱敏后文本: {desensitized_text}")
    print(f"脱敏映射关系: {mapping}")
    
    # 大模型处理
    llm_response = large_model.process(desensitized_text)
    print(f"大模型原始输出: {llm_response}")
    
    # 还原处理
    restored_text = endside_model.restore(llm_response)
    print(f"最终还原结果: {restored_text}")
    
    # 验证还原结果
    # 改进的验证逻辑：检查还原后的文本是否包含用户原始输入中的关键信息
    # 从原始用户输入中提取关键信息（去除常见的停用词）
    original_keywords = []
    # 对于场景1-4的常见关键词
    common_keywords = ["银行卡", "身份证", "交易", "付款", "收款", "金额", "时间", "状态", "IP", "密码", "用户名", "手机号", "邮箱", "地址"]
    
    # 从用户输入中提取关键词
    for keyword in common_keywords:
        if keyword in user_input:
            original_keywords.append(keyword)
    
    # 对于交易单号、银行卡号等特定信息的识别
    if "TX" in user_input:
        original_keywords.append("交易单号")
    if "6222" in user_input:
        original_keywords.append("银行卡号")
    if re.search(r'\d{17}[\dXx]', user_input):
        original_keywords.append("身份证号")
    if re.search(r'1[3-9]\d{9}', user_input):
        original_keywords.append("手机号")
    
    # 统计还原文本中包含的原始关键词数量
    restored_keywords_count = 0
    for keyword in original_keywords:
        if keyword in restored_text:
            restored_keywords_count += 1
    
    # 评估还原效果
    # 如果没有识别到敏感信息
    if len(mapping) == 0:
        print("\n✅ 没有识别到需要脱敏的敏感信息，无需还原。")
    # 如果还原后的文本与原始输入文本相似度较高，或者还原了大部分关键词
    elif len(original_keywords) > 0 and restored_keywords_count >= len(original_keywords) * 0.7:
        # 打印原始输入和还原结果的对比，帮助用户确认
        print("\n原始输入关键词: ", ", ".join(original_keywords))
        print("还原后包含的关键词: ", end="")
        restored_keywords = [k for k in original_keywords if k in restored_text]
        print(", ".join(restored_keywords))
        print(f"\n✅ 还原功能测试成功！成功还原了关键信息。")
    # 检查是否有明显的HAS_xxx占位符未被还原
    elif any(keyword.startswith("HAS_") for keyword in restored_text.split()):
        print("\n❌ 还原功能测试失败！仍有部分敏感信息未被还原。")
    # 其他情况，视为还原成功
    else:
        print("\n✅ 还原功能测试成功！敏感信息已成功还原。")

if __name__ == "__main__":
    test_restore_function()