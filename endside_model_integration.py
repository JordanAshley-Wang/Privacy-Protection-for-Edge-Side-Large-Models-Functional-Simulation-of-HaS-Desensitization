import re
import time
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
            restored_text = self.simulator.seek_with_options(
                llm_response,
                use_fuzzy_matching=True,
                min_confidence=0.7
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
        # 在实际应用中，这里会调用真实的大模型API
        mock_responses = [
            f"根据您提供的信息：{desensitized_text}\n这是大模型生成的回答内容。",
            f"我已收到您的请求：{desensitized_text}\n以下是相关的处理结果和建议。",
            f"关于您提到的：{desensitized_text}\n我的分析和结论如下。",
            f"感谢您的提问。针对{desensitized_text}，我的回答是：\n这是大模型根据脱敏信息生成的内容。"
        ]
        
        # 随机选择一个回答模板（为了简化，这里固定选择第一个）
        response = mock_responses[0]
        
        print(f"[{self.model_name}] 处理完成，已生成回答。")
        return response

class HaSWorkflow:
    """
    HaS (Hide and Seek) 完整工作流
    集成端侧小模型和大模型，实现完整的隐私保护交互流程
    """
    def __init__(self):
        # 初始化端侧小模型
        self.endside_model = EndsideModel()
        # 初始化模拟大模型
        self.large_model = MockLargeModel()
        
    def run(self, user_input, sensitive_types=None, use_uuid_mode=False):
        """
        运行完整的HaS工作流
        
        参数:
        user_input: 用户输入的原始文本
        sensitive_types: 指定需要脱敏的敏感信息类型列表
        use_uuid_mode: 是否使用UUID模式进行脱敏
        
        返回:
        dict: 包含各阶段结果的字典
        """
        print("\n===== HaS 隐私保护工作流开始 =====")
        print(f"用户原始输入: {user_input}")
        
        # 阶段1: 端侧小模型脱敏处理
        desensitized_text, mapping = self.endside_model.desensitize(
            user_input, sensitive_types, use_uuid_mode
        )
        
        # 阶段2: 将脱敏文本传输至大模型
        print("[系统] 将脱敏后的文本传输给大模型...")
        llm_response = self.large_model.process(desensitized_text)
        
        # 阶段3: 端侧小模型整合还原脱敏数据
        final_response = self.endside_model.restore(llm_response)
        
        # 输出各阶段结果
        print("\n===== HaS 隐私保护工作流结果 =====")
        print(f"脱敏后文本: {desensitized_text}")
        print(f"脱敏映射关系: {mapping}")
        print(f"大模型原始输出: {llm_response}")
        print(f"最终还原结果: {final_response}")
        print("==================================")
        
        # 返回完整结果
        return {
            'original_input': user_input,
            'desensitized_text': desensitized_text,
            'mapping': mapping,
            'llm_response': llm_response,
            'final_response': final_response
        }

# 演示不同场景下的HaS工作流
def demonstrate_has_workflow():
    """
    演示HaS工作流在不同场景下的应用
    """
    print("\n===== HaS 端侧小模型与大模型集成演示 =====")
    
    # 创建HaS工作流实例
    has_workflow = HaSWorkflow()
    
    # 场景1: 个人信息处理
    print("\n\n[场景1] 处理包含个人敏感信息的查询")
    personal_info = "你好，我叫王小明，我的手机号是13812345678，身份证号是110101199003079876，请帮我查询一下我的账户余额。"
    has_workflow.run(personal_info)
    
    # 场景2: 企业信息处理
    print("\n\n[场景2] 处理包含企业敏感信息的查询")
    company_info = "我们公司是北京科技有限公司，统一社会信用代码是91110108MA00123456，法人是李华，请帮我生成一份公司简介。"
    has_workflow.run(company_info, sensitive_types=['name', 'custom'])
    
    # 场景3: 使用UUID模式进行脱敏
    print("\n\n[场景3] 使用UUID模式进行脱敏")
    financial_info = "交易单号为TX202405010001的付款方是张三，金额为10000元，请帮我核对一下交易状态。"
    has_workflow.run(financial_info, use_uuid_mode=True)
    
    # 场景4: 自定义敏感信息类型
    print("\n\n[场景4] 处理自定义敏感信息类型")
    custom_info = "IP地址是192.168.1.1的服务器出现了故障，访问密码是admin123，请帮忙解决。"
    
    # 由于HideAndSeekSimulator没有add_custom_pattern方法
    # 我们创建一个新的HaSWorkflow实例，在内部使用自定义模式
    print("[系统] 创建支持自定义敏感信息类型的HaS工作流...")
    
    # 定义自定义敏感信息处理类
    class CustomEndsideModel(EndsideModel):
        def desensitize(self, user_input, sensitive_types=None, use_uuid_mode=False):
            # 定义自定义模式
            custom_patterns = {
                'ip': (r'\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b', lambda x: '***.***.***.***'),
                'password': (r'密码是([a-zA-Z0-9]{6,20})', lambda x: '密码是********')
            }
            
            # 创建带自定义模式的simulator实例
            self.simulator = HideAndSeekSimulator(
                use_uuid=use_uuid_mode,
                custom_patterns=custom_patterns
            )
            
            # 调用父类方法执行脱敏
            if sensitive_types:
                hidden_text, code_map = self.simulator.hide(user_input, specific_types=sensitive_types)
            else:
                hidden_text, code_map = self.simulator.hide(user_input)
            
            # 保存当前映射关系
            self.current_mapping = code_map
            self.history_mappings.append(code_map)
            
            print(f"[端侧小模型] 脱敏完成。识别并处理了 {len(code_map)} 处敏感信息。")
            return hidden_text, code_map
    
    # 创建使用自定义端侧模型的工作流
    custom_has_workflow = HaSWorkflow()
    custom_has_workflow.endside_model = CustomEndsideModel()
    
    # 运行自定义敏感信息处理
    custom_has_workflow.run(custom_info, sensitive_types=['ip', 'password'])

if __name__ == "__main__":
    # 运行演示
    demonstrate_has_workflow()