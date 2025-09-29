import time
import re
from typing import Dict, Tuple, Optional, List

class EnhancedNamedEntityEndsideModel:
    """
    增强版端侧小模型 - 使用命名实体占位符进行脱敏
    提供更精确的敏感信息识别、脱敏和还原功能，使用<name>、<company>等占位符格式
    """
    def __init__(self):
        # 存储当前会话的脱敏映射关系
        self.current_mapping = {}
        # 存储会话ID，用于标识不同的用户会话
        self.session_id = self._generate_session_id()
        # 配置选项
        self.config = {
            'enable_entity_placeholder': True,  # 使用实体占位符格式
            'preserve_format': True,           # 是否保留原始格式
            'enable_fuzzy_matching': True,     # 是否启用模糊匹配还原
            'min_confidence': 0.7,             # 模糊匹配的最小置信度
            'max_distance': 3,                 # 允许的最大字符差异
            'custom_patterns': None            # 自定义敏感信息模式
        }
        # 定义敏感信息类型和对应的正则表达式
        self.sensitive_patterns = {
            'name': {
                'pattern': r'我叫([\u4e00-\u9fa5]{2,4})|姓名是([\u4e00-\u9fa5]{2,4})|名字是([\u4e00-\u9fa5]{2,4})|([\u4e00-\u9fa5]{2,4})(?=，且|，系|，是|，就职|，担任|\s)','description': '姓名','placeholder': '<name>'
            },
            'company': {
                'pattern': r'(?:来自|就职于|属于|是)?([\u4e00-\u9fa5]+(?:公司|有限责任公司|股份有限公司|集团|企业|厂|所|院|校|移动|电信|联通|银行))',
                'description': '公司名称',
                'placeholder': '<company>'
            },
            'position': {
                'pattern': r'(总经理|副总经理|总监|经理|主管|总裁|副总裁|董事长|副董事长|部长|副部长|主任|副主任)',
                'description': '职位',
                'placeholder': '<position>'
            },
            'phone': {
                'pattern': r'(1[3-9]\d{1})(\d{4})(\d{4})',
                'description': '手机号',
                'placeholder': '<phone>'
            },
            'id': {
                'pattern': r'(\d{6})(\d{8})(\d{4}[\dXx])',
                'description': '身份证号',
                'placeholder': '<id>'
            },
            'email': {
                'pattern': r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                'description': '邮箱',
                'placeholder': '<email>'
            },
            'bank_card': {
                'pattern': r'([1-9]\d{3})\s*(\d{4})\s*(\d{4})\s*(\d{4})',
                'description': '银行卡号',
                'placeholder': '<bank_card>'
            },
            'amount': {
                'pattern': r'(\d+(?:\.\d{1,2})?)\s*(亿|万|千|百|元|美元|欧元|英镑|日元)',
                'description': '金额',
                'placeholder': '<amount>'
            },
            'performance': {
                'pattern': r'(年化|年|月|季度|半年)\s*([百]?分之\s*\d+(?:\.\d+)?)',
                'description': '业绩指标',
                'placeholder': '<performance>'
            },
            'department': {
                'pattern': r'(业务部|财务部|技术部|人力资源部|市场部|销售部|研发部|客服部|运营部|行政部|合规部|风险管理部|投资银行部|资产管理部|自营资产部)',
                'description': '部门',
                'placeholder': '<department>'
            }
        }
        # 预编译正则表达式以提高性能
        self.compiled_patterns = {}
        for key, value in self.sensitive_patterns.items():
            self.compiled_patterns[key] = re.compile(value['pattern'])

    def _generate_session_id(self):
        """生成唯一的会话ID"""
        return f"session_{int(time.time())}_{int(time.time() * 1000) % 10000}"

    def configure(self, **kwargs):
        """
        配置端侧小模型的参数
        
        参数:
        **kwargs: 配置参数，如use_uuid, preserve_format, enable_fuzzy_matching等
        """
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
        return self

    def desensitize(self, user_input: str, sensitive_types: Optional[List[str]] = None):
        """
        使用端侧小模型对用户输入进行脱敏处理，只对指定类型的敏感信息进行脱敏
        
        参数:
        user_input: 用户输入的原始文本
        sensitive_types: 指定需要脱敏的敏感信息类型列表，如['name', 'company', 'position']
                        None表示使用默认的敏感类型列表
        
        返回:
        tuple: (脱敏后的文本, 脱敏映射关系)
        """
        print(f"[{self.session_id}] 端侧小模型正在执行敏感信息识别和脱敏处理...")
        
        # 保存用户输入用于上下文理解
        self.last_user_input = user_input
        
        # 重置当前映射关系
        self.current_mapping = {}
        
        # 模拟端侧小模型的处理时间
        time.sleep(0.2)
        
        # 确定要处理的敏感信息类型
        if sensitive_types is None:
            # 默认敏感信息类型：姓名、公司、职位、部门、金额、业绩
            sensitive_types = ['name', 'company', 'position', 'department', 'amount', 'performance']
        else:
            # 确保传入的是列表
            if isinstance(sensitive_types, str):
                sensitive_types = [sensitive_types]
        
        # 过滤出有效的敏感信息类型
        # 处理可能的中文逗号和空格
        processed_types = []
        for t in sensitive_types:
            # 替换中文逗号为英文逗号，并分割
            parts = re.split(r'[,，]', t)
            processed_types.extend([p.strip() for p in parts if p.strip()])
        
        valid_types = [t for t in processed_types if t in self.compiled_patterns]
        
        # 对每种敏感信息类型进行脱敏处理
        desensitized_text = user_input
        entity_count = 0
        
        # 按照优先级排序处理，避免嵌套匹配问题
        priority_order = ['company', 'department', 'position', 'performance', 'amount', 'email', 'phone', 'id', 'name']
        processing_order = [t for t in priority_order if t in valid_types] + [t for t in valid_types if t not in priority_order]
        
        # 用于记录已处理的位置，避免重复脱敏
        processed_positions = []
        
        for type_name in processing_order:
            pattern = self.compiled_patterns[type_name]
            placeholder = self.sensitive_patterns[type_name]['placeholder']
            
            # 查找所有匹配项
            matches = pattern.finditer(desensitized_text)
            for match in matches:
                # 检查是否与已处理的位置重叠
                start, end = match.span()
                overlap = False
                for p_start, p_end in processed_positions:
                    if not (end <= p_start or start >= p_end):
                        overlap = True
                        break
                
                if not overlap:
                    # 对于姓名类型，如果使用了捕获组，取第一个非空的捕获组
                    if type_name == 'name':
                        original_text = None
                        for i in range(1, len(match.groups()) + 1):
                            if match.group(i) is not None:
                                original_text = match.group(i)
                                break
                        if original_text is None:
                            original_text = match.group()
                    else:
                        original_text = match.group()
                    
                    # 生成唯一的占位符ID
                    unique_id = f"{placeholder}_{entity_count}"
                    entity_count += 1
                    
                    # 保存映射关系
                    self.current_mapping[unique_id] = original_text
                    
                    # 替换原文中的敏感信息
                    desensitized_text = desensitized_text[:start] + unique_id + desensitized_text[end:]
                    
                    # 更新已处理的位置（注意：替换后文本长度可能变化，需要重新计算位置）
                    new_end = start + len(unique_id)
                    processed_positions.append((start, new_end))
                    
                    # 由于文本长度发生变化，需要重新计算后续匹配位置，这里采用简单策略：重新编译并查找
                    break
            
            # 重复处理直到没有更多匹配项
            while True:
                matches = pattern.finditer(desensitized_text)
                found = False
                for match in matches:
                    start, end = match.span()
                    overlap = False
                    for p_start, p_end in processed_positions:
                        if not (end <= p_start or start >= p_end):
                            overlap = True
                            break
                    
                    if not overlap:
                        original_text = match.group()
                        unique_id = f"{placeholder}_{entity_count}"
                        entity_count += 1
                        
                        self.current_mapping[unique_id] = original_text
                        desensitized_text = desensitized_text[:start] + unique_id + desensitized_text[end:]
                        
                        new_end = start + len(unique_id)
                        processed_positions.append((start, new_end))
                        found = True
                        break
                
                if not found:
                    break
        
        print(f"[{self.session_id}] 端侧小模型脱敏完成。识别并处理了 {entity_count} 处敏感信息。")
        return desensitized_text, self.current_mapping

    def restore(self, llm_response: str):
        """
        使用端侧小模型将脱敏数据重新整合至大模型返回的文本中
        
        参数:
        llm_response: 大模型返回的包含脱敏标记的文本
        
        返回:
        str: 还原后的完整文本
        """
        print(f"[{self.session_id}] 端侧小模型正在执行脱敏数据还原处理...")
        
        # 模拟端侧小模型的处理时间
        time.sleep(0.2)
        
        # 对大模型输出进行预处理，提高还原准确率
        processed_response = self._preprocess_llm_output(llm_response)
        
        # 执行还原操作
        restored_text = processed_response
        
        # 按照占位符长度从长到短排序，避免部分匹配
        for placeholder_id, original_text in sorted(self.current_mapping.items(), key=lambda x: len(x[0]), reverse=True):
            # 替换占位符为原始文本
            restored_text = restored_text.replace(placeholder_id, original_text)
        
        # 对还原结果进行后处理，提高文本质量
        final_text = self._postprocess_restored_text(restored_text)
        
        print(f"[{self.session_id}] 端侧小模型还原处理完成。")
        return final_text

    def _preprocess_llm_output(self, llm_response: str):
        """
        对大模型输出进行预处理，提高还原准确率
        
        参数:
        llm_response: 大模型返回的文本
        
        返回:
        str: 预处理后的文本
        """
        # 去除多余的空白字符
        processed = re.sub(r'\s+', ' ', llm_response)
        # 规范化标点符号
        processed = re.sub(r'[，]', ',', processed)
        processed = re.sub(r'[。]', '.', processed)
        return processed.strip()

    def _postprocess_restored_text(self, restored_text: str):
        """
        对还原结果进行后处理，提高文本质量
        
        参数:
        restored_text: 还原后的文本
        
        返回:
        str: 后处理后的文本
        """
        # 可以在这里添加更多后处理逻辑，如修复标点符号、调整语序等
        return restored_text

    def get_session_info(self):
        """
        获取当前会话信息
        
        返回:
        dict: 会话信息
        """
        return {
            'session_id': self.session_id,
            'current_mapping_count': len(self.current_mapping),
            'config': self.config
        }

class EnhancedMockLargeModel:
    """
    增强版模拟大模型
    提供更真实的文本处理效果，包括文本改写、语法调整等
    """
    def __init__(self, model_name="豆包大模型"):
        self.model_name = model_name
        # 文本改写模板
        self.rephrase_templates = [
            f"根据您提供的信息：{{}}\n这是{model_name}生成的详细回答内容。",
            f"我已收到您的请求：{{}}\n以下是{model_name}的处理结果和建议。",
            f"关于您提到的：{{}}\n{model_name}的分析和结论如下。",
            f"感谢您的提问。针对{{}}，我的回答是：\n这是{model_name}根据脱敏信息生成的内容。"
        ]
        # 模拟文本改写的替换规则
        self.rephrase_rules = {
            '是': ['为', '系', '乃'],
            '的': ['之'],
            '请': ['烦请', '劳驾'],
            '我': ['本人'],
            '你': ['您', '阁下'],
            '谢谢': ['感谢', '谢谢'],
            '手机': ['移动电话', '手机设备'],
            '身份证': ['居民身份证', '身份证件'],
            '银行卡': ['银行账户', '银行卡号'],
            '公司': ['企业', '公司'],
            '地址': ['地址信息', '所在地']
        }

    def process(self, desensitized_text: str):
        """
        模拟大模型处理脱敏后的文本
        
        参数:
        desensitized_text: 脱敏后的文本
        
        返回:
        str: 大模型处理后的结果
        """
        print(f"[{self.model_name}] 正在处理脱敏后的文本...")
        
        # 模拟大模型处理时间
        import random
        time.sleep(random.uniform(0.5, 1.2))
        
        # 对输入文本进行模拟改写
        rephrased_text = self._rephrase_text(desensitized_text)
        
        # 随机选择一个回答模板
        template = random.choice(self.rephrase_templates)
        response = template.format(rephrased_text)
        
        # 随机添加一些额外信息，模拟大模型的创造性
        if random.random() > 0.5:
            additional_info = self._generate_additional_info(desensitized_text)
            response = f"{response}\n\n{additional_info}"
        
        print(f"[{self.model_name}] 处理完成，已生成回答。")
        return response

    def _rephrase_text(self, text: str):
        """
        模拟文本改写过程
        
        参数:
        text: 需要改写的文本
        
        返回:
        str: 改写后的文本
        """
        result = text
        # 应用替换规则，但保留占位符不变
        import random
        for original, replacements in self.rephrase_rules.items():
            # 检查original是否是占位符的一部分
            is_placeholder_part = False
            for placeholder_id in self._get_placeholders(result):
                if original in placeholder_id:
                    is_placeholder_part = True
                    break
            
            if original in result and not is_placeholder_part:
                # 随机决定是否替换
                if random.random() > 0.3:
                    replacement = random.choice(replacements)
                    result = result.replace(original, replacement)
        
        # 随机调整句式结构，但避免破坏占位符
        if random.random() > 0.7 and '，' in result:
            parts = result.split('，')
            if len(parts) > 2:
                # 随机重新排列部分内容，但要确保占位符所在的部分不被拆分
                # 这里采用简单策略：不进行复杂的句式调整，以保证占位符的完整性
                pass
        
        return result
    
    def _get_placeholders(self, text: str):
        """提取文本中的所有占位符"""
        return re.findall(r'<\w+_\d+>', text)

    def _generate_additional_info(self, original_text: str):
        """
        生成额外的相关信息，模拟大模型的创造性
        
        参数:
        original_text: 原始文本
        
        返回:
        str: 生成的额外信息
        """
        import random
        additional_infos = [
            "以上内容仅供参考，具体情况请以实际为准。",
            "如需更详细的信息，建议提供更多背景资料。",
            "根据相关规定，此类信息请妥善保管，避免泄露。",
            "为了保护您的隐私，我们已对敏感信息进行特殊处理。",
            "如有其他问题，请随时提出，我们将尽力为您提供帮助。"
        ]
        
        # 根据输入文本中的占位符类型选择更相关的额外信息
        if any(p in original_text for p in ['<phone>', '<email>', '<id>']):
            additional_infos.append("请确保您提供的个人联系方式正确无误，以便我们及时与您取得联系。")
        elif any(p in original_text for p in ['<company>', '<position>', '<department>']):
            additional_infos.append("企业信息可能涉及商业机密，请根据实际需要进行适当的保密措施。")
        elif any(p in original_text for p in ['<amount>', '<performance>']):
            additional_infos.append("金融数据具有敏感性，请确保在合适的场合使用这些信息。")
        
        return random.choice(additional_infos)

class CompleteHaSWorkflow:
    """
    完整的HaS (Hide and Seek) 隐私保护工作流
    集成增强版端侧小模型和模拟大模型，提供更完善的隐私保护交互体验
    """
    def __init__(self):
        # 初始化增强版端侧小模型
        self.endside_model = EnhancedNamedEntityEndsideModel()
        # 初始化增强版模拟大模型
        self.large_model = EnhancedMockLargeModel()
        # 存储工作流执行历史
        self.execution_history = []

    def configure_endside_model(self, **kwargs):
        """
        配置端侧小模型的参数
        
        参数:
        **kwargs: 配置参数
        
        返回:
        self: 当前工作流实例，支持链式调用
        """
        self.endside_model.configure(**kwargs)
        return self

    def run(self, user_input: str, sensitive_types: Optional[List[str]] = None):
        """
        运行完整的HaS工作流
        
        参数:
        user_input: 用户输入的原始文本
        sensitive_types: 指定需要脱敏的敏感信息类型列表
        
        返回:
        dict: 包含各阶段结果的字典
        """
        print(f"\n===== HaS 隐私保护工作流 [会话: {self.endside_model.session_id}] 开始 =====")
        print(f"用户原始输入: {user_input}")
        
        # 阶段1: 端侧小模型脱敏处理
        start_time = time.time()
        desensitized_text, mapping = self.endside_model.desensitize(
            user_input, sensitive_types
        )
        desensitize_time = time.time() - start_time
        
        # 阶段2: 将脱敏文本传输至大模型
        print(f"[{self.endside_model.session_id}] 系统将脱敏后的文本传输给大模型...")
        start_time = time.time()
        llm_response = self.large_model.process(desensitized_text)
        llm_process_time = time.time() - start_time
        
        # 阶段3: 端侧小模型整合还原脱敏数据
        start_time = time.time()
        final_response = self.endside_model.restore(llm_response)
        restore_time = time.time() - start_time
        
        # 记录执行历史
        execution_record = {
            'timestamp': time.time(),
            'session_id': self.endside_model.session_id,
            'original_input': user_input,
            'desensitized_text': desensitized_text,
            'mapping': mapping,
            'llm_response': llm_response,
            'final_response': final_response,
            'timing': {
                'desensitize': desensitize_time,
                'llm_process': llm_process_time,
                'restore': restore_time,
                'total': desensitize_time + llm_process_time + restore_time
            }
        }
        self.execution_history.append(execution_record)
        
        # 输出各阶段结果
        print(f"\n===== HaS 隐私保护工作流 [会话: {self.endside_model.session_id}] 结果 =====")
        print(f"脱敏后文本: {desensitized_text}")
        print(f"脱敏映射关系: {mapping}")
        print(f"大模型原始输出: {llm_response}")
        print(f"最终还原结果: {final_response}")
        print(f"性能指标: 脱敏={desensitize_time:.3f}s, 大模型处理={llm_process_time:.3f}s, 还原={restore_time:.3f}s, 总耗时={desensitize_time + llm_process_time + restore_time:.3f}s")
        print(f"============================================================")
        
        # 返回完整结果
        return execution_record

# 预设场景测试数据
preset_scenarios = [
    {
        "name": "个人信息处理",
        "description": "包含姓名、手机号、身份证号等个人敏感信息",
        "input": "你好，我叫王小明，我的手机号是13812345678，身份证号是110101199003079876，请帮我查询一下我的账户余额。",
        "sensitive_types": ['name', 'phone', 'id']
    },
    {
        "name": "金融信息处理",
        "description": "包含银行卡号、交易金额等金融敏感信息",
        "input": "我需要查询银行卡号为6222 1234 5678 9012的最近一笔交易，金额大约是10000元。",
        "sensitive_types": ['bank_card', 'amount']
    },
    {
        "name": "企业信息处理",
        "description": "包含公司名称、职位、部门等企业敏感信息",
        "input": "我叫王通，是申万宏源证券业务部总经理，本年度我募集资金100亿，在自营资产部同志们的努力下，做到了年化百分之二十的好成绩。",
        "sensitive_types": ['name', 'company', 'department', 'position', 'amount', 'performance']
    },
    {
        "name": "网络安全信息处理",
        "description": "包含IP地址、密码等网络安全敏感信息",
        "input": "服务器IP地址是192.168.1.1，访问密码是Admin12345，请帮忙解决登录问题。",
        "sensitive_types": None  # 将在自定义配置中处理
    }
]

# 用户交互演示
def user_interaction_demo():
    """
    用户交互演示模式，允许用户手动选择场景或输入自定义文本
    """
    print("\n===== HaS (Hide and Seek) 隐私保护技术 - 增强版演示 ======")
    print("该工具演示了在大模型交互过程中保护用户隐私的完整流程。")
    print("端侧小模型将用户输入中的敏感信息脱敏后提交给大模型，")
    print("再将大模型的输出结果中的敏感信息还原，确保用户隐私安全。")
    print("提示：输入 'exit' 或 '退出' 结束程序。\n")
    
    while True:
        try:
            # 显示菜单
            print("请选择操作：")
            print("1. 使用预设场景进行演示")
            print("2. 输入自定义文本进行演示")
            print("3. 退出程序")
            
            choice = input("请选择 (1-3): ").strip()
            
            if choice == '1':
                # 预设场景演示
                print("\n请选择预设场景：")
                for i, scenario in enumerate(preset_scenarios, 1):
                    print(f"{i}. {scenario['name']}: {scenario['description']}")
                
                scenario_choice = input("请选择场景 (1-4): ").strip()
                if scenario_choice.isdigit() and 1 <= int(scenario_choice) <= len(preset_scenarios):
                    scenario_idx = int(scenario_choice) - 1
                    selected_scenario = preset_scenarios[scenario_idx]
                    
                    # 创建工作流实例
                    has_workflow = CompleteHaSWorkflow()
                    
                    # 运行工作流
                    has_workflow.run(
                        selected_scenario['input'], 
                        selected_scenario['sensitive_types']
                    )
                else:
                    print("无效的选择，请重新输入。\n")
                    continue
            elif choice == '2':
                # 自定义文本演示
                print("请输入您需要处理的文本：")
                custom_text = input().strip()
                if not custom_text:
                    print("输入不能为空，请重新输入。\n")
                    continue
                
                # 创建工作流实例
                has_workflow = CompleteHaSWorkflow()
                
                # 询问用户是否需要指定脱敏类型
                specify_types = input("是否需要指定脱敏的信息类型？(y/n，默认n)：").strip().lower() == 'y'
                
                if specify_types:
                    print("请选择需要脱敏的信息类型（多个类型用逗号分隔，如 name,company,position）：")
                    print("支持的类型：name(姓名), company(公司), position(职位), department(部门),")
                    print("phone(手机号), id(身份证), email(邮箱), bank_card(银行卡),")
                    print("amount(金额), performance(业绩指标)")
                    
                    types_input = input("请输入类型：").strip().lower()
                    sensitive_types = [t.strip() for t in types_input.split(',') if t.strip()]
                else:
                    sensitive_types = None  # 使用默认类型
                
                # 运行工作流
                has_workflow.run(custom_text, sensitive_types)
            elif choice in ['3', 'exit', '退出']:
                print("感谢使用HaS隐私保护工作流演示，再见！")
                break
            else:
                print("无效的选择，请重新输入。\n")
                continue
            
            # 询问用户是否继续
            continue_choice = input("\n是否继续？(y/n，默认y)：").strip().lower()
            if continue_choice != 'y':
                print("感谢使用HaS隐私保护工作流演示，再见！")
                break
            
            print("\n" + "="*80 + "\n")
            
        except Exception as e:
            print(f"处理过程中发生错误：{e}")
            print("请重新输入或选择退出。\n")

# 批量测试
def batch_test():
    """
    批量测试不同场景下的HaS工作流性能
    """
    print("\n===== HaS (Hide and Seek) 隐私保护技术 - 批量测试 ======")
    
    # 测试不同配置组合
    configurations = [
        {"name": "标准配置", "enable_entity_placeholder": True, "preserve_format": True, "enable_fuzzy_matching": True},
        {"name": "简化模式", "enable_entity_placeholder": True, "preserve_format": False, "enable_fuzzy_matching": False}
    ]
    
    for config in configurations:
        print(f"\n\n----- 测试配置: {config['name']} -----\n")
        
        total_times = []
        
        for i, scenario in enumerate(preset_scenarios, 1):
            print(f"场景 {i}: {scenario['name']}")
            
            # 创建工作流实例
            has_workflow = CompleteHaSWorkflow()
            has_workflow.configure_endside_model(**config)
            
            # 运行工作流
            result = has_workflow.run(
                scenario['input'],
                scenario['sensitive_types']
            )
            
            # 记录总耗时
            total_times.append(result['timing']['total'])
        
        # 计算平均耗时
        avg_time = sum(total_times) / len(total_times)
        print(f"\n配置 '{config['name']}' 的平均处理时间: {avg_time:.3f}秒")

if __name__ == "__main__":
    # 默认运行用户交互演示
    user_interaction_demo()
    
    # 如果需要进行批量测试，可以取消下面一行的注释
    # batch_test()