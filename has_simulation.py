import re
import random
import string
import hashlib
import uuid
from typing import Dict, Tuple, Optional, Callable, List
from datetime import datetime

class HideAndSeekSimulator:
    """
    腾讯实验室 HaS (Hide and Seek) 隐私保护技术的完整模拟实现。
    该技术通过对用户输入的敏感信息进行脱敏处理，并能在大模型输出后进行还原。
    增强版实现包含更多敏感信息类型、更强的脱敏安全性和更健壮的还原功能。
    """
    def __init__(self, custom_patterns: Optional[Dict[str, Tuple[str, Callable]]] = None, 
                 use_uuid: bool = False, 
                 preserve_format: bool = True):
        # 定义常见敏感信息的正则表达式和对应的处理函数
        self.patterns = {
            "phone": (r"(1[3-9]\d{1})(\d{4})(\d{4})".encode('unicode-escape').decode(), self.replace_phone),  # 手机号
            "id": (r"(\d{6})(\d{8})(\d{4}[\dXx])".encode('unicode-escape').decode(), self.replace_id),     # 身份证号
            "email": (r"([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", self.replace_email),  # 邮箱
            "name": (r"[\u4e00-\u9fa5]{2,4}", self.replace_name),  # 中文姓名
            "bank_card": (r"([1-9]\d{3})\s*(\d{4})\s*(\d{4})\s*(\d{4})", self.replace_bank_card),  # 银行卡号
            "credit_card": (r"([1-9]\d{3})[-]?(\d{4})[-]?(\d{4})[-]?(\d{4})".encode('unicode-escape').decode(), self.replace_credit_card),  # 信用卡号
            "address": (r"([省市区])([^省市区]+?)(路|街|巷|弄)[^省市区]+?\d+(号|弄)?", self.replace_address),  # 地址
            "company": (r"[\u4e00-\u9fa5]+(公司|有限责任公司|股份有限公司|集团|企业|厂|所|院|校)", self.replace_company),  # 公司名称
            "date": (r"(\d{4})[-/]?(\d{1,2})[-/]?(\d{1,2})".encode('unicode-escape').decode(), self.replace_date),  # 日期
        }
        
        # 添加自定义模式
        if custom_patterns:
            for key, (pattern, func) in custom_patterns.items():
                self.patterns[key] = (pattern, func)
        
        # 存储脱敏映射关系
        self.hide_map = {}
        
        # 存储还原映射关系
        self.seek_map = {}
        
        # 映射历史，用于支持多次脱敏/还原操作
        self.mapping_history = []
        
        # 常见中文姓氏和名字，用于替换真实姓名
        self.common_surnames = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴', 
                               '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马']
        self.common_given_names = ['伟', '芳', '娜', '秀英', '敏', '静', '强', '磊', '军', '洋', 
                                  '勇', '杰', '涛', '丽', '艳', '辉', '超', '刚', '明', '亮']
        
        # 常见地名和公司名称词库
        self.common_locations = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉', '西安', '重庆']
        self.common_company_words = ['科技', '信息', '网络', '电子', '软件', '数据', '智能', '数字', '互联', '通信']
        
        # 生成随机字符串的工具
        self.random_string_pool = string.ascii_letters + string.digits
        
        # 配置选项
        self.use_uuid = use_uuid  # 是否使用UUID进行脱敏，提高安全性
        self.preserve_format = preserve_format  # 是否保留原始格式
        
        # 性能优化：预编译正则表达式
        self.compiled_patterns = {}
        for key, (pattern, func) in self.patterns.items():
            try:
                self.compiled_patterns[key] = (re.compile(pattern), func)
            except re.error:
                print(f"警告：正则表达式 '{pattern}' 无效，跳过编译。")
                self.compiled_patterns[key] = (None, func)
    
    
    def generate_random_string(self, length: int) -> str:
        """生成指定长度的随机字符串"""
        return ''.join(random.choice(self.random_string_pool) for _ in range(length))
    
    def generate_salt(self) -> str:
        """生成随机盐值，增强脱敏安全性"""
        return hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()[:8]
    
    def generate_token(self, original: str) -> str:
        """生成唯一标识符，用于敏感信息的映射"""
        if self.use_uuid:
            return f"HAS_{uuid.uuid4().hex[:16]}"
        else:
            # 生成基于哈希的令牌，保留一定的唯一性
            salt = self.generate_salt()
            return f"HAS_{hashlib.md5((original + salt).encode()).hexdigest()[:16]}"
    
    def replace_phone(self, match) -> str:
        """替换手机号，保留首尾数字"""
        original = match.group()
        if self.preserve_format:
            encoded = f"{match.group(1)}****{match.group(3)}"
        else:
            encoded = self.generate_token(original)
        # 创建双向映射
        self.hide_map[original] = encoded
        self.seek_map[encoded] = original
        return encoded
    
    def replace_id(self, match) -> str:
        """替换身份证号，保留首尾数字"""
        original = match.group()
        if self.preserve_format:
            encoded = f"{match.group(1)}********{match.group(3)}"
        else:
            encoded = self.generate_token(original)
        # 创建双向映射
        self.hide_map[original] = encoded
        self.seek_map[encoded] = original
        return encoded
    
    def replace_email(self, match) -> str:
        """替换邮箱，保留域名部分"""
        original = match.group()
        if self.preserve_format:
            encoded = f"***@{match.group(2)}"
        else:
            encoded = self.generate_token(original)
        # 创建双向映射
        self.hide_map[original] = encoded
        self.seek_map[encoded] = original
        return encoded
    
    def replace_name(self, match) -> str:
        """替换中文姓名，使用常见姓氏和名字组合"""
        original = match.group()
        if self.use_uuid:
            encoded = self.generate_token(original)
        else:
            # 随机生成一个新名字
            new_surname = random.choice(self.common_surnames)
            new_given_name = ''.join(random.choices(self.common_given_names, k=random.randint(1, 2)))
            encoded = new_surname + new_given_name
            # 确保新名字与原名字长度相同
            while len(encoded) != len(original):
                if len(encoded) < len(original):
                    encoded += random.choice(self.common_given_names)
                else:
                    encoded = encoded[:-1]
        # 创建双向映射
        self.hide_map[original] = encoded
        self.seek_map[encoded] = original
        return encoded
    
    def replace_bank_card(self, match) -> str:
        """替换银行卡号，保留首尾四位数字"""
        original = match.group()
        if self.preserve_format:
            encoded = f"{match.group(1)} **** **** {match.group(4)}"
        else:
            encoded = self.generate_token(original)
        # 创建双向映射
        self.hide_map[original] = encoded
        self.seek_map[encoded] = original
        return encoded
    
    def replace_credit_card(self, match) -> str:
        """替换信用卡号，保留首尾四位数字"""
        original = match.group()
        if self.preserve_format:
            encoded = f"{match.group(1)}-****-****-{match.group(4)}"
        else:
            encoded = self.generate_token(original)
        # 创建双向映射
        self.hide_map[original] = encoded
        self.seek_map[encoded] = original
        return encoded
    
    def replace_address(self, match) -> str:
        """替换地址信息"""
        original = match.group()
        if self.use_uuid:
            encoded = self.generate_token(original)
        else:
            # 保留省市，替换具体街道和门牌号
            province_city = match.group(1)
            random_location = random.choice(self.common_locations)
            encoded = f"{province_city}{random_location}路{random.randint(100, 999)}号"
        # 创建双向映射
        self.hide_map[original] = encoded
        self.seek_map[encoded] = original
        return encoded
    
    def replace_company(self, match) -> str:
        """替换公司名称"""
        original = match.group()
        if self.use_uuid:
            encoded = self.generate_token(original)
        else:
            # 生成随机公司名称
            random_surname = random.choice(self.common_surnames)
            random_word = random.choice(self.common_company_words)
            # 保留公司类型后缀
            suffix = re.search(r'(公司|有限责任公司|股份有限公司|集团|企业|厂|所|院|校)$', original)
            if suffix:
                encoded = f"{random_surname}{random_word}{suffix.group(1)}"
            else:
                encoded = f"{random_surname}{random_word}科技有限公司"
        # 创建双向映射
        self.hide_map[original] = encoded
        self.seek_map[encoded] = original
        return encoded
    
    def replace_date(self, match) -> str:
        """替换日期信息"""
        original = match.group()
        if self.preserve_format:
            # 生成随机但合理的日期
            year = random.randint(1950, 2023)
            month = random.randint(1, 12)
            # 处理不同月份的天数
            if month in [4, 6, 9, 11]:
                day = random.randint(1, 30)
            elif month == 2:
                # 简单判断闰年
                is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                day = random.randint(1, 29 if is_leap else 28)
            else:
                day = random.randint(1, 31)
            
            # 保持原始分隔符
            separator = '-' if '-' in original else '/' if '/' in original else ''
            encoded = f"{year}{separator}{month:02d}{separator}{day:02d}"
        else:
            encoded = self.generate_token(original)
        # 创建双向映射
        self.hide_map[original] = encoded
        self.seek_map[encoded] = original
        return encoded
    
    def hide(self, text: str, specific_types: Optional[List[str]] = None) -> Tuple[str, Dict[str, str]]:
        """
        执行脱敏操作（Hide阶段）
        对输入文本进行隐私信息识别和替换
        
        参数:
        - text: 要脱敏的文本
        - specific_types: 指定要脱敏的信息类型列表，None表示脱敏所有类型
        
        返回:
        - 脱敏后的文本
        - 脱敏映射关系
        """
        # 重置映射关系
        self.hide_map = {}
        self.seek_map = {}
        
        encoded_text = text
        
        # 确定要处理的类型
        types_to_process = specific_types if specific_types else list(self.compiled_patterns.keys())
        
        # 按照优先级进行替换
        # 优先级顺序：邮箱 > 银行卡号 > 信用卡号 > 身份证号 > 手机号 > 日期 > 地址 > 公司 > 姓名
        priority_order = ["email", "bank_card", "credit_card", "id", "phone", "date", "address", "company", "name"]
        
        # 构建处理顺序
        processing_order = []
        for type_name in priority_order:
            if type_name in types_to_process:
                processing_order.append(type_name)
                types_to_process.remove(type_name)
        # 添加剩余的类型
        processing_order.extend(types_to_process)
        
        # 执行替换
        for type_name in processing_order:
            pattern, func = self.compiled_patterns.get(type_name, (None, None))
            if pattern and func:
                try:
                    encoded_text = pattern.sub(func, encoded_text)
                except Exception as e:
                    print(f"警告：处理 {type_name} 类型时出错: {str(e)}")
        
        # 保存映射历史
        self.mapping_history.append((self.hide_map.copy(), self.seek_map.copy()))
        
        return encoded_text, self.hide_map
    
    def hide_with_params(self, text: str, 
                         include_types: Optional[List[str]] = None, 
                         exclude_types: Optional[List[str]] = None, 
                         custom_patterns: Optional[Dict[str, Tuple[str, Callable]]] = None) -> Tuple[str, Dict[str, str]]:
        """
        带参数的脱敏操作，更灵活地控制脱敏过程
        
        参数:
        - text: 要脱敏的文本
        - include_types: 要包含的敏感信息类型（与exclude_types二选一）
        - exclude_types: 要排除的敏感信息类型（与include_types二选一）
        - custom_patterns: 自定义敏感信息类型和处理函数
        
        返回:
        - 脱敏后的文本
        - 脱敏映射关系
        """
        # 处理自定义模式
        if custom_patterns:
            temp_patterns = {}
            for key, (pattern, func) in custom_patterns.items():
                try:
                    temp_patterns[key] = (re.compile(pattern), func)
                    # 临时添加到已编译模式中
                    self.compiled_patterns[key] = temp_patterns[key]
                except re.error:
                    print(f"警告：自定义正则表达式 '{pattern}' 无效，跳过。")
        
        # 确定要处理的类型
        if include_types:
            types_to_process = include_types
        elif exclude_types:
            types_to_process = [t for t in self.compiled_patterns.keys() if t not in exclude_types]
        else:
            types_to_process = list(self.compiled_patterns.keys())
        
        # 执行脱敏
        result_text, result_map = self.hide(text, types_to_process)
        
        # 清理临时添加的模式
        if custom_patterns:
            for key in custom_patterns.keys():
                if key in self.compiled_patterns:
                    del self.compiled_patterns[key]
        
        return result_text, result_map
    
    def seek(self, text: str) -> str:
        """
        执行还原操作（Seek阶段）
        将脱敏后的文本还原为原始文本
        
        返回:
        - 还原后的文本
        """
        if not self.seek_map:
            return text
        
        decoded_text = text
        # 按照字符长度从长到短排序，避免部分匹配
        for encoded, original in sorted(self.seek_map.items(), key=lambda x: len(x[0]), reverse=True):
            # 使用正则替换，确保更精确的匹配
            try:
                # 对特殊字符进行转义
                escaped_encoded = re.escape(encoded)
                # 使用单词边界确保精确匹配
                if self.preserve_format and not self.use_uuid:
                    # 对于保留格式的替换，使用更精确的匹配
                    pattern = re.compile(rf"\b{escaped_encoded}\b")
                else:
                    # 对于UUID格式的替换，直接进行字符串替换
                    decoded_text = decoded_text.replace(encoded, original)
                    continue
                
                # 使用正则替换
                decoded_text = pattern.sub(original, decoded_text)
            except Exception:
                # 如果正则替换失败，回退到简单的字符串替换
                decoded_text = decoded_text.replace(encoded, original)
        
        return decoded_text
    
    def seek_with_options(self, text: str, 
                         use_fuzzy_matching: bool = False, 
                         min_confidence: float = 0.7) -> str:
        """
        带选项的还原操作，增强还原的鲁棒性
        
        参数:
        - text: 要还原的文本
        - use_fuzzy_matching: 是否使用模糊匹配
        - min_confidence: 模糊匹配的最小置信度（0-1）
        
        返回:
        - 还原后的文本
        """
        if not self.seek_map:
            return text
        
        decoded_text = text
        
        if use_fuzzy_matching:
            # 实现简单的模糊匹配还原
            # 这个实现是简化版的，实际应用中可能需要更复杂的模糊匹配算法
            words = re.findall(r'\S+', text)
            for word in words:
                best_match = None
                best_score = min_confidence
                
                for encoded, original in self.seek_map.items():
                    # 简单的编辑距离计算作为相似度指标
                    score = self._calculate_similarity(word, encoded)
                    if score > best_score:
                        best_score = score
                        best_match = (encoded, original)
                
                if best_match:
                    encoded, original = best_match
                    decoded_text = decoded_text.replace(word, original)
        else:
            # 使用标准还原方法
            decoded_text = self.seek(text)
        
        return decoded_text
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """
        计算两个字符串的相似度（简化版）
        
        返回:
        - 相似度分数（0-1）
        """
        # 简单的基于长度和共同字符的相似度计算
        if not s1 or not s2:
            return 0.0
            
        # 计算共同字符数
        common_chars = len(set(s1) & set(s2))
        # 计算最长字符串长度
        max_len = max(len(s1), len(s2))
        # 返回相似度分数
        return common_chars / max_len
    
    def process(self, text: str, mock_llm_func=None, use_fuzzy_matching: bool = False) -> Tuple[str, str, str]:
        """
        完整处理流程：脱敏 -> 调用大模型 -> 还原
        
        参数:
        - text: 输入文本
        - mock_llm_func: 模拟大模型的函数
        - use_fuzzy_matching: 还原时是否使用模糊匹配
        
        返回:
        - 脱敏后的文本
        - 大模型输出
        - 还原后的文本
        """
        # 1. 脱敏处理
        hidden_text, _ = self.hide(text)
        
        # 2. 调用大模型（这里可以替换为真实的大模型调用）
        if mock_llm_func:
            llm_output = mock_llm_func(hidden_text)
        else:
            # 如果没有提供模拟大模型函数，简单地复制脱敏后的文本
            llm_output = hidden_text
        
        # 3. 还原处理
        if use_fuzzy_matching:
            restored_text = self.seek_with_options(llm_output, use_fuzzy_matching=True)
        else:
            restored_text = self.seek(llm_output)
        
        return hidden_text, llm_output, restored_text
    
    def save_mapping(self, file_path: str) -> bool:
        """
        保存脱敏映射关系到文件
        
        参数:
        - file_path: 保存文件路径
        
        返回:
        - 是否保存成功
        """
        try:
            import json
            # 将映射关系转换为可序列化的格式
            serializable_map = {}
            for k, v in self.hide_map.items():
                serializable_map[str(k)] = str(v)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "hide_map": serializable_map
                }, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存映射关系失败: {str(e)}")
            return False
    
    def load_mapping(self, file_path: str) -> bool:
        """
        从文件加载脱敏映射关系
        
        参数:
        - file_path: 映射文件路径
        
        返回:
        - 是否加载成功
        """
        try:
            import json
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 恢复映射关系
            self.hide_map = {}
            self.seek_map = {}
            
            if "hide_map" in data:
                for k, v in data["hide_map"].items():
                    self.hide_map[k] = v
                    self.seek_map[v] = k
            
            return True
        except Exception as e:
            print(f"加载映射关系失败: {str(e)}")
            return False
    
    def batch_process(self, texts: List[str], mock_llm_func=None) -> List[Tuple[str, str, str]]:
        """
        批量处理文本
        
        参数:
        - texts: 文本列表
        - mock_llm_func: 模拟大模型的函数
        
        返回:
        - 处理结果列表，每项包含(脱敏文本, 大模型输出, 还原文本)
        """
        results = []
        for text in texts:
            # 为每个文本创建一个新的映射关系
            self.hide_map = {}
            self.seek_map = {}
            
            hidden_text, llm_output, restored_text = self.process(text, mock_llm_func)
            results.append((hidden_text, llm_output, restored_text))
        
        return results
    
    def clear_history(self) -> None:
        """
        清除映射历史
        """
        self.mapping_history = []

# 简化版函数，方便直接调用
def encode_sensitive(origin_text, specific_types=None):
    """
    模拟腾讯实验室 "HaS" 的功能，对输入文本进行脱敏处理。
    
    参数:
    - origin_text: 原始文本
    - specific_types: 指定要脱敏的信息类型列表
    
    返回:
    - 脱敏后的文本
    - 脱敏映射关系
    """
    simulator = HideAndSeekSimulator()
    encoded_text, code_map = simulator.hide(origin_text, specific_types)
    return encoded_text, code_map


def decode_sensitive(encoded_text, code_map):
    """
    还原脱敏后的文本
    
    参数:
    - encoded_text: 脱敏后的文本
    - code_map: 脱敏映射关系
    
    返回:
    - 还原后的文本
    """
    # 创建临时模拟器实例
    simulator = HideAndSeekSimulator()
    # 设置还原映射
    simulator.hide_map = code_map
    simulator.seek_map = {v: k for k, v in code_map.items()}
    # 执行还原
    return simulator.seek(encoded_text)


def user_interaction_demo():
    """
    用户交互演示模式，允许用户手动输入需要脱敏的文本
    """
    print("===== HaS (Hide and Seek) 隐私保护技术 - 用户交互模式 =====")
    print("该工具可以帮助您对文本中的敏感信息进行脱敏处理和还原。")
    print("支持识别：手机号、身份证号、邮箱、中文姓名、银行卡号、信用卡号、地址、公司名称、日期等。")
    print("提示：输入 'exit' 或 '退出' 结束程序。\n")
    
    # 创建模拟器实例
    simulator = HideAndSeekSimulator(use_uuid=False, preserve_format=True)
    
    while True:
        try:
            # 获取用户输入
            print("请输入需要脱敏的文本（或输入模板编号获取示例文本）：")
            print("1. 个人信息模板")
            print("2. 公司信息模板")
            print("3. 交易信息模板")
            print("4. 自定义输入")
            
            choice = input("请选择 (1-4): ").strip()
            
            # 预设模板
            if choice == '1':
                origin_text = """
                王小明的手机号是13812345678，身份证号为110101199003079876，
                他的邮箱是xiaoming@example.com，银行卡号为6222 1234 5678 9012。
                他住在北京市朝阳区建国路88号，出生日期是1990/03/07。
                """
                print(f"\n已加载个人信息模板：\n{origin_text}\n")
            elif choice == '2':
                origin_text = """
                北京科技有限公司的联系电话是13987654321，
                法定代表人是李华，公司地址在上海市浦东新区张江高科技园区博云路2号。
                公司邮箱是contact@beijingtech.com。
                """
                print(f"\n已加载公司信息模板：\n{origin_text}\n")
            elif choice == '3':
                origin_text = """
                交易单号：TX202305160001，
                付款人：张伟，手机号：13712345678，
                收款人：刘芳，卡号：6226 8888 8888 8888，
                交易金额：10000.00元，交易日期：2023-05-16。
                """
                print(f"\n已加载交易信息模板：\n{origin_text}\n")
            elif choice == '4':
                print("请输入您需要脱敏的文本（输入完后按Enter键）：")
                origin_text = input().strip()
                if not origin_text:
                    print("输入不能为空，请重新输入。\n")
                    continue
            elif choice.lower() in ['exit', '退出']:
                print("感谢使用HaS隐私保护工具，再见！")
                break
            else:
                print("无效的选择，请重新输入。\n")
                continue
            
            # 询问用户是否使用UUID模式
            use_uuid = input("是否使用UUID模式进行脱敏？(y/n，默认n)：").strip().lower() == 'y'
            if use_uuid:
                simulator = HideAndSeekSimulator(use_uuid=True, preserve_format=False)
            else:
                simulator = HideAndSeekSimulator(use_uuid=False, preserve_format=True)
            
            # 询问用户是否需要指定脱敏类型
            specify_types = input("是否需要指定脱敏的信息类型？(y/n，默认n)：").strip().lower() == 'y'
            
            if specify_types:
                print("请选择需要脱敏的信息类型（多个类型用逗号分隔，如 phone,id,email）：")
                print("支持的类型：phone(手机号), id(身份证), email(邮箱), name(姓名),")
                print("bank_card(银行卡), credit_card(信用卡), address(地址),")
                print("company(公司名称), date(日期)")
                
                types_input = input("请输入类型：").strip().lower()
                specific_types = [t.strip() for t in types_input.split(',') if t.strip()]
                
                # 测试完整处理流程 - 指定类型
                hidden_text, llm_output, restored_text = simulator.process(origin_text)
                print("\n===== 脱敏结果（指定类型）=====")
            else:
                # 测试完整处理流程 - 所有类型
                hidden_text, llm_output, restored_text = simulator.process(origin_text)
                print("\n===== 脱敏结果（所有类型）=====")
            
            print("原始文本：", origin_text)
            print("\n脱敏后文本：", hidden_text)
            print("\n模拟大模型输出：", llm_output)
            print("\n还原后文本：", restored_text)
            print("\n脱敏映射关系：", simulator.hide_map)
            
            # 询问用户是否继续
            continue_choice = input("\n是否继续处理其他文本？(y/n，默认y)：").strip().lower()
            if continue_choice != 'y':
                print("感谢使用HaS隐私保护工具，再见！")
                break
            
            print("\n" + "="*60 + "\n")
            
        except Exception as e:
            print(f"处理过程中发生错误：{e}")
            print("请重新输入文本或选择退出。\n")

# 原始的演示代码（作为备用）
def original_demo():
    # 创建模拟器实例
    simulator = HideAndSeekSimulator(use_uuid=False, preserve_format=True)
    
    # 测试输入文本 - 包含多种敏感信息
    origin_text = """
    王小明的手机号是13812345678，身份证号为110101199003079876，
    他的邮箱是xiaoming@example.com，银行卡号为6222 1234 5678 9012。
    他在北京市朝阳区建国路88号的北京科技有限公司工作，
    出生日期是1990/03/07。
    """

    print("===== 基本功能测试 ======")
    print("原始文本：", origin_text.strip())
    
    # 测试完整处理流程
    hidden_text, llm_output, restored_text = simulator.process(origin_text)
    
    print("\n脱敏后文本：", hidden_text.strip())
    print("\n模拟大模型输出：", llm_output.strip())
    print("\n还原后文本：", restored_text.strip())
    print("\n脱敏映射关系：", simulator.hide_map)
    
    print("\n\n===== 指定敏感信息类型测试 ======")
    # 只脱敏手机号和身份证号
    encoded_text, code_map = encode_sensitive(origin_text, specific_types=["phone", "id"])
    print("仅脱敏手机号和身份证号：", encoded_text.strip())
    print("映射关系：", code_map)
    
    print("\n\n===== 高级功能测试 ======")
    # 测试UUID模式
    uuid_simulator = HideAndSeekSimulator(use_uuid=True, preserve_format=False)
    uuid_encoded, uuid_map = uuid_simulator.hide(origin_text)
    print("UUID模式脱敏：", uuid_encoded.strip())
    print("UUID映射关系：", uuid_map)
    
    # 测试自定义模式
    def custom_replace_ip(match):
        original = match.group()
        encoded = "***.***.***.***"
        uuid_simulator.hide_map[original] = encoded
        uuid_simulator.seek_map[encoded] = original
        return encoded
    
    custom_patterns = {
        "ip_address": (r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", custom_replace_ip)
    }
    
    # 创建一个包含IP地址的文本
    text_with_ip = "服务器IP地址是192.168.1.1，管理员邮箱是admin@example.com"
    custom_encoded, custom_map = simulator.hide_with_params(text_with_ip, custom_patterns=custom_patterns)
    print("\n自定义模式脱敏（IP地址）：", custom_encoded)
    print("自定义映射关系：", custom_map)
    
    # 测试模糊匹配还原
    print("\n\n===== 模糊匹配还原测试 ======")
    # 模拟大模型输出时的拼写错误
    llm_output_with_errors = "张敏的手机号是138****5678，身份号码为110101********9876，"
    "他的邮箱是***@example.com"
    
    # 使用模糊匹配还原
    restored_with_fuzzy = simulator.seek_with_options(llm_output_with_errors, use_fuzzy_matching=True)
    print("带错误的大模型输出：", llm_output_with_errors)
    print("模糊匹配还原结果：", restored_with_fuzzy)

if __name__ == "__main__":
    # 默认运行用户交互模式
    user_interaction_demo()
    
    # 如果需要运行原始演示，可以取消下面一行的注释
    # original_demo()