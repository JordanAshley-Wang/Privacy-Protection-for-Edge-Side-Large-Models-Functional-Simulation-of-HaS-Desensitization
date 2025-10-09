import re
import math
import random
import time
from collections import Counter, defaultdict

class EntropyEnhancedSensitiveModel:
    def __init__(self):
        # 系统配置参数
        self.enable_entropy_detection = True
        self.entropy_threshold = 1.2
        self.high_entropy_threshold = 3.5
        self.max_token_len = 64
        self.min_token_len = 2
        self.enable_radical_analysis = False  # 禁用激进分析以提高效率
        self.enable_position_entropy = True  # 启用位置熵分析
        
        # 敏感信息类型配置
        self.sensitive_types = {
            'name': {'enable': True, 'regex': None, 'entropy_based': True},
            'company': {'enable': True, 'regex': None, 'entropy_based': True},
            'position': {'enable': True, 'regex': None, 'entropy_based': True},
            'department': {'enable': True, 'regex': None, 'entropy_based': True},
            'phone': {'enable': True, 'regex': r'(?:13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}', 'entropy_based': False},
            'id': {'enable': True, 'regex': r'[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]', 'entropy_based': False},
            'email': {'enable': True, 'regex': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 'entropy_based': False},
            'bank_card': {'enable': True, 'regex': r'\b(?:\d{16}|\d{17}|\d{18}|\d{19})\b', 'entropy_based': True},
            'amount': {'enable': True, 'regex': r'[￥$]?\d+(?:,\d{3})*(?:\.\d{1,2})?|\d+(?:,\d{3})*(?:\.\d{1,2})?[元rmb]?', 'entropy_based': False},
            'performance': {'enable': True, 'regex': r'\d+\.?\d*[\u767e\u5343\u4e07\u4ebf]?\s*%', 'entropy_based': False},
            'age': {'enable': True, 'regex': r'\b[1-9]\d?岁\b', 'entropy_based': False},
            'address': {'enable': True, 'regex': None, 'entropy_based': True},
            'zipcode': {'enable': True, 'regex': r'\b\d{6}\b', 'entropy_based': False},
            'ip': {'enable': True, 'regex': r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b', 'entropy_based': False},
            'account': {'enable': True, 'regex': None, 'entropy_based': True}
        }
        
        # 常见姓氏集合
        self.COMMON_SURNAMES = set('王李张刘陈杨赵黄周吴徐孙胡朱高林何郭马罗梁宋郑谢韩唐冯于董萧程曹袁邓许傅沈曾彭吕苏卢蒋蔡贾丁魏薛叶阎余潘杜戴夏钟汪田任姜范方石姚谭廖邹熊金陆郝孔白崔康毛邱秦江史顾侯邵孟龙万段漕钱汤尹黎易常武乔贺赖龚文')
        
        # 公司后缀集合
        self.COMPANY_SUFFIXES = ('有限公司', '有限责任公司', '股份有限公司', '集团有限公司', '集团股份有限公司', '科技有限公司', '信息技术有限公司', '网络科技有限公司', '电子科技有限公司', '软件有限公司')
        
        # 常见称谓和停用词
        self.MINOR_STOPWORDS = {'先生', '女士', '小姐', '同志', '经理', '总监', '总裁', '董事长', '总经理', '副总经理', '部门经理'}
        
        # 位置权重配置
        self.position_weights = {
            'start': 1.5,  # 句子开头
            'middle': 1.0,  # 句子中间
            'end': 1.2,  # 句子结尾
            'after_colon': 1.3,  # 冒号后
            'after_comma': 1.1,  # 逗号后
        }
        
        # 会话管理
        self.sessions = {}
        self.session_counter = 0
        
        # 初始化脱敏策略
        self.desensitization_strategies = {
            'placeholder': self._placeholder_desensitize,
            'pseudonymization': self._pseudonymization_desensitize,
            'anonymization': self._anonymization_desensitize,
            'generalization': self._generalization_desensitize
        }
    
    def configure(self, **kwargs):
        """配置模型参数"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _char_entropy(self, text):
        """计算字符串的字符香农熵"""
        if not text or len(text) <= 1:
            return 0
        
        # 计算字符频率
        char_counts = Counter(text)
        total_chars = len(text)
        
        # 计算香农熵
        entropy = 0.0
        for count in char_counts.values():
            probability = count / total_chars
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _ngram_entropy(self, text, n=2):
        """计算字符串的N-gram熵"""
        if not text or len(text) < n:
            return 0
        
        # 生成N-gram
        ngrams = [text[i:i+n] for i in range(len(text)-n+1)]
        ngram_counts = Counter(ngrams)
        total_ngrams = len(ngrams)
        
        # 计算熵
        entropy = 0.0
        for count in ngram_counts.values():
            probability = count / total_ngrams
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _position_entropy(self, text, position_info):
        """计算位置相关的加权熵"""
        base_entropy = self._char_entropy(text)
        
        # 应用位置权重
        weight = 1.0
        for pos_type, pos_weight in self.position_weights.items():
            if pos_type in position_info:
                weight *= pos_weight
                break  # 只应用第一个匹配的位置权重
        
        return base_entropy * weight
    
    def _tokenize_simple(self, text):
        """简单分词，将文本按汉字串、字母数字串和其他字符分段"""
        # 使用正则表达式进行简单分词
        # 匹配汉字、字母数字和其他字符
        pattern = r'([\u4e00-\u9fa5]+)|([a-zA-Z0-9]+)|(\S)'
        tokens = re.findall(pattern, text)
        
        # 合并匹配结果
        result = []
        for token in tokens:
            # 取第一个非空的匹配组
            for t in token:
                if t:
                    result.append(t)
                    break
        
        return result
    
    def _get_position_info(self, text, start_idx, end_idx):
        """获取文本位置信息"""
        position_info = set()
        
        # 检查是否在句子开头
        if start_idx == 0 or text[start_idx-1] in '。！？':
            position_info.add('start')
        # 检查是否在句子结尾
        elif end_idx == len(text) or text[end_idx] in '。！？':
            position_info.add('end')
        # 检查是否在句子中间
        else:
            position_info.add('middle')
        
        # 检查是否在冒号后
        if start_idx > 0 and text[start_idx-1] == ':':
            position_info.add('after_colon')
        # 检查是否在逗号后
        elif start_idx > 0 and text[start_idx-1] == ',':
            position_info.add('after_comma')
        
        return position_info
    
    def _entropy_detect_candidates(self, text):
        """基于信息熵和启发式规则检测敏感信息候选"""
        if not text or not self.enable_entropy_detection:
            return []
        
        candidates = []
        tokens = self._tokenize_simple(text)
        
        # 遍历所有可能的token组合作为候选
        for i in range(len(tokens)):
            for j in range(i+1, min(i+self.max_token_len//2, len(tokens))):
                candidate_text = ''.join(tokens[i:j+1])
                
                # 跳过太短的候选
                if len(candidate_text) < self.min_token_len:
                    continue
                
                # 获取位置信息
                start_idx = text.find(candidate_text)
                end_idx = start_idx + len(candidate_text)
                position_info = self._get_position_info(text, start_idx, end_idx)
                
                # 计算综合熵值
                char_entropy = self._char_entropy(candidate_text)
                bigram_entropy = self._ngram_entropy(candidate_text, 2)
                trigram_entropy = self._ngram_entropy(candidate_text, 3) if len(candidate_text) >= 3 else 0
                
                # 综合不同粒度的熵值
                combined_entropy = (char_entropy * 0.5 + bigram_entropy * 0.3 + trigram_entropy * 0.2)
                
                # 应用位置权重
                if self.enable_position_entropy:
                    combined_entropy = self._position_entropy(candidate_text, position_info)
                
                # 启发式规则判断
                is_sensitive = False
                sensitive_type = None
                
                # 公司名称检测
                if any(suffix in candidate_text for suffix in self.COMPANY_SUFFIXES):
                    is_sensitive = True
                    sensitive_type = 'company'
                # 姓名检测
                elif len(candidate_text) >= 2 and candidate_text[0] in self.COMMON_SURNAMES:
                    is_sensitive = True
                    sensitive_type = 'name'
                # 账号/标识检测（高熵值）
                elif combined_entropy > self.high_entropy_threshold and re.search(r'[a-zA-Z0-9]{6,}', candidate_text):
                    is_sensitive = True
                    sensitive_type = 'account'
                # 低熵值文本可能包含结构化信息
                elif combined_entropy < self.entropy_threshold:
                    is_sensitive = True
                    sensitive_type = 'general'
                
                if is_sensitive:
                    candidates.append({
                        'text': candidate_text,
                        'start': start_idx,
                        'end': end_idx,
                        'entropy': combined_entropy,
                        'type': sensitive_type
                    })
        
        # 按熵值和长度排序，优先选择熵值高、长度长的候选
        candidates.sort(key=lambda x: (x['entropy'], len(x['text'])), reverse=True)
        
        # 去重，保留最长的匹配
        unique_candidates = []
        covered_positions = set()
        
        for candidate in candidates:
            # 检查是否与已选择的候选重叠
            overlap = False
            for pos in range(candidate['start'], candidate['end']):
                if pos in covered_positions:
                    overlap = True
                    break
            
            if not overlap:
                unique_candidates.append(candidate)
                # 标记覆盖的位置
                for pos in range(candidate['start'], candidate['end']):
                    covered_positions.add(pos)
        
        return unique_candidates
    
    def _regex_detect_sensitive(self, text):
        """使用正则表达式检测敏感信息"""
        sensitive_matches = []
        
        for sensitive_type, config in self.sensitive_types.items():
            if not config['enable'] or not config['regex']:
                continue
            
            pattern = config['regex']
            matches = re.finditer(pattern, text)
            
            for match in matches:
                sensitive_matches.append({
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'type': sensitive_type
                })
        
        # 按起始位置排序
        sensitive_matches.sort(key=lambda x: x['start'])
        
        return sensitive_matches
    
    def detect_sensitive_info(self, text):
        """综合检测文本中的敏感信息"""
        if not text:
            return []
        
        # 使用正则表达式检测
        regex_matches = self._regex_detect_sensitive(text)
        
        # 使用信息熵检测候选
        entropy_candidates = self._entropy_detect_candidates(text)
        
        # 合并结果
        all_matches = regex_matches.copy()
        
        # 添加熵检测的结果，避免重复
        regex_positions = set()
        for match in regex_matches:
            for pos in range(match['start'], match['end']):
                regex_positions.add(pos)
        
        for candidate in entropy_candidates:
            # 检查是否与正则匹配重叠
            overlap = False
            for pos in range(candidate['start'], candidate['end']):
                if pos in regex_positions:
                    overlap = True
                    break
            
            if not overlap:
                # 尝试确定具体的敏感类型
                if candidate['type'] == 'general':
                    candidate_type = self._classify_general_sensitive(candidate['text'])
                else:
                    candidate_type = candidate['type']
                
                all_matches.append({
                    'text': candidate['text'],
                    'start': candidate['start'],
                    'end': candidate['end'],
                    'type': candidate_type
                })
        
        # 按起始位置排序
        all_matches.sort(key=lambda x: x['start'])
        
        return all_matches
    
    def _classify_general_sensitive(self, text):
        """对通用敏感信息进行更精确的分类"""
        # 简单的规则分类
        if len(text) >= 2 and any(title in text for title in ('经理', '总监', '总裁', '董事长', '总经理', '副总经理', '部门经理')):
            return 'position'
        elif len(text) >= 2 and any(dept in text for dept in ('部门', '部', '处', '科', '组', '室')):
            return 'department'
        elif len(text) >= 4 and any(addr in text for addr in ('省', '市', '区', '县', '街道', '路', '号')):
            return 'address'
        else:
            # 默认返回general类型
            return 'general'
    
    def _placeholder_desensitize(self, text, sensitive_info, mapping, counter):
        """使用标准占位符进行脱敏"""
        sensitive_type = sensitive_info['type']
        placeholder = f'<{sensitive_type}_{counter}>'
        mapping[placeholder] = sensitive_info['text']
        return placeholder
    
    def _pseudonymization_desensitize(self, text, sensitive_info, mapping, counter):
        """使用假名化进行脱敏（生成替代信息）"""
        sensitive_type = sensitive_info['type']
        sensitive_text = sensitive_info['text']
        
        # 根据不同类型生成不同的替代信息
        if sensitive_type == 'name':
            # 生成随机姓名
            surname = random.choice(list(self.COMMON_SURNAMES))
            given_names = ''.join(random.choice('伟芳娜秀英敏静强磊军洋勇艳杰丽娟涛磊玲超霞亮明燕刚' ) for _ in range(len(sensitive_text)-1))
            pseudonym = surname + given_names
        elif sensitive_type == 'phone':
            # 生成随机手机号
            prefix = random.choice(['13', '14', '15', '16', '17', '18', '19'])
            pseudonym = prefix + ''.join(random.choices('0123456789', k=9))
        elif sensitive_type == 'id':
            # 生成随机身份证号（简化版）
            area_code = ''.join(random.choices('123456789', k=6))
            birth_year = str(random.randint(1950, 2005))
            birth_month = str(random.randint(1, 12)).zfill(2)
            birth_day = str(random.randint(1, 28)).zfill(2)
            sequence = ''.join(random.choices('0123456789', k=3))
            check_digit = random.choice('0123456789X')
            pseudonym = area_code + birth_year + birth_month + birth_day + sequence + check_digit
        else:
            # 其他类型简单地用长度相同的星号替代
            pseudonym = '*' * len(sensitive_text)
        
        # 保存映射关系
        placeholder = f'<PSEUDO_{sensitive_type}_{counter}>'
        mapping[placeholder] = (pseudonym, sensitive_text)
        
        return pseudonym
    
    def _anonymization_desensitize(self, text, sensitive_info, mapping, counter):
        """使用匿名化进行脱敏（统一替换为固定标记）"""
        sensitive_type = sensitive_info['type']
        placeholder = f'[REDACTED_{sensitive_type.upper()}]'
        mapping[placeholder] = sensitive_info['text']
        return placeholder
    
    def _generalization_desensitize(self, text, sensitive_info, mapping, counter):
        """使用数据泛化进行脱敏"""
        sensitive_type = sensitive_info['type']
        sensitive_text = sensitive_info['text']
        
        # 根据不同类型进行泛化处理
        if sensitive_type == 'amount':
            # 金额泛化：保留数量级，四舍五入到最近的百位或千位
            match = re.search(r'\d+(?:,\d{3})*(?:\.\d{1,2})?', sensitive_text)
            if match:
                amount_str = match.group().replace(',', '')
                try:
                    amount = float(amount_str)
                    if amount >= 1000:
                        generalized = f'约{round(amount / 1000)}千元'
                    else:
                        generalized = f'约{round(amount / 100)}百元'
                except:
                    generalized = '[金额信息]'
            else:
                generalized = '[金额信息]'
        elif sensitive_type == 'age':
            # 年龄泛化：转换为年龄段
            match = re.search(r'\d+', sensitive_text)
            if match:
                age = int(match.group())
                if age < 18:
                    generalized = '未成年'
                elif age < 30:
                    generalized = '20-30岁'
                elif age < 40:
                    generalized = '30-40岁'
                elif age < 50:
                    generalized = '40-50岁'
                else:
                    generalized = '50岁以上'
            else:
                generalized = '[年龄信息]'
        else:
            # 其他类型简单处理
            generalized = f'[{sensitive_type}信息]'
        
        # 保存映射关系
        placeholder = f'<GENERAL_{sensitive_type}_{counter}>'
        mapping[placeholder] = (generalized, sensitive_text)
        
        return generalized
    
    def desensitize(self, text, sensitive_types=None, strategy='placeholder'):
        """对文本进行脱敏处理"""
        if not text:
            return text, {}
        
        # 检测敏感信息
        detected_sensitive = self.detect_sensitive_info(text)
        
        # 如果指定了敏感类型，过滤结果
        if sensitive_types:
            detected_sensitive = [info for info in detected_sensitive if info['type'] in sensitive_types]
        
        # 按照结束位置倒序排序，避免替换时位置偏移
        detected_sensitive.sort(key=lambda x: x['end'], reverse=True)
        
        # 执行脱敏替换
        result_text = text
        mapping = {}
        counter = defaultdict(int)
        
        for sensitive_info in detected_sensitive:
            sensitive_type = sensitive_info['type']
            counter[sensitive_type] += 1
            
            # 获取脱敏策略函数
            desensitize_func = self.desensitization_strategies.get(strategy, self._placeholder_desensitize)
            
            # 执行脱敏
            placeholder = desensitize_func(result_text, sensitive_info, mapping, counter[sensitive_type])
            
            # 替换文本中的敏感信息
            start = sensitive_info['start']
            end = sensitive_info['end']
            result_text = result_text[:start] + placeholder + result_text[end:]
        
        # 创建会话ID并保存映射
        session_id = self._create_session(mapping)
        
        return result_text, mapping, session_id
    
    def restore(self, text, mapping, session_id=None):
        """还原脱敏后的文本"""
        if not text or not mapping:
            return text
        
        # 如果提供了会话ID，尝试从会话中获取映射
        if session_id and session_id in self.sessions:
            session_mapping = self.sessions[session_id]
            # 合并映射
            mapping = {**mapping, **session_mapping}
        
        # 执行还原替换
        result_text = text
        
        # 按照替换文本长度倒序排序，避免替换时位置偏移
        sorted_items = sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True)
        
        for placeholder, original_text in sorted_items:
            # 处理假名化和数据泛化的特殊映射
            if isinstance(original_text, tuple):
                pseudonym_text, actual_original = original_text
                result_text = result_text.replace(pseudonym_text, actual_original)
            else:
                result_text = result_text.replace(placeholder, original_text)
        
        return result_text
    
    def _create_session(self, mapping):
        """创建一个新的会话并保存映射"""
        self.session_counter += 1
        session_id = f"session_{int(time.time())}_{self.session_counter}"
        self.sessions[session_id] = mapping
        
        # 限制会话数量，避免内存泄漏
        if len(self.sessions) > 1000:
            # 删除最早的会话
            oldest_session = min(self.sessions.keys())
            del self.sessions[oldest_session]
        
        return session_id
    
    def get_session_mapping(self, session_id):
        """获取指定会话的映射关系"""
        return self.sessions.get(session_id, {})

class EntropyEnhancedHaSWorkflow:
    def __init__(self):
        # 初始化端侧小模型
        self.endside_model = EntropyEnhancedSensitiveModel()
        
        # 初始化配置
        self.config = {
            'sensitive_types': ['name', 'company', 'position', 'phone', 'id', 'email'],
            'desensitization_strategy': 'placeholder',
            'enable_entropy_detection': True,
            'enable_position_entropy': True
        }
        
        # 会话管理
        self.current_session_id = None
        self.current_mapping = {}
    
    def configure(self, **kwargs):
        """配置工作流参数"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
        
        # 配置端侧模型
        self.endside_model.configure(**kwargs)
    
    def run_desensitization(self, user_input):
        """执行脱敏流程"""
        # 调用端侧模型进行脱敏
        desensitized_text, mapping, session_id = self.endside_model.desensitize(
            user_input,
            sensitive_types=self.config['sensitive_types'],
            strategy=self.config['desensitization_strategy']
        )
        
        # 保存会话信息
        self.current_session_id = session_id
        self.current_mapping = mapping
        
        # 记录脱敏结果
        num_sensitive = len(mapping)
        
        return {
            'desensitized_text': desensitized_text,
            'session_id': session_id,
            'mapping': mapping,
            'num_sensitive': num_sensitive
        }
    
    def run_restore(self, llm_output, session_id=None, mapping=None):
        """执行还原流程"""
        # 使用提供的会话ID或映射，否则使用当前会话
        if session_id:
            mapping = self.endside_model.get_session_mapping(session_id)
        elif not mapping:
            mapping = self.current_mapping
        
        # 调用端侧模型进行还原
        restored_text = self.endside_model.restore(llm_output, mapping)
        
        return {
            'restored_text': restored_text,
            'session_id': session_id or self.current_session_id
        }
    
    def run_complete_workflow(self, user_input):
        """运行完整的脱敏-处理-还原工作流"""
        # 记录开始时间
        start_time = time.time()
        
        # 1. 脱敏处理
        desensitization_result = self.run_desensitization(user_input)
        desensitized_text = desensitization_result['desensitized_text']
        session_id = desensitization_result['session_id']
        mapping = desensitization_result['mapping']
        
        # 2. 模拟大模型处理（实际应用中应替换为真实的大模型调用）
        llm_output = self._mock_llm_processing(desensitized_text)
        
        # 3. 还原处理
        restore_result = self.run_restore(llm_output, session_id, mapping)
        restored_text = restore_result['restored_text']
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        return {
            'original_text': user_input,
            'desensitized_text': desensitized_text,
            'llm_output': llm_output,
            'restored_text': restored_text,
            'session_id': session_id,
            'num_sensitive': len(mapping),
            'processing_time': processing_time
        }
    
    def _mock_llm_processing(self, input_text):
        """模拟大模型的处理过程"""
        # 简单的模拟处理，实际应用中应替换为真实的大模型调用
        # 这里只是为了演示，实际上应该调用真正的大模型API
        mock_responses = [
            f"处理结果：{input_text}\n这是生成的内容。",
            f"根据您提供的信息：{input_text}\n我分析得出以下结论。",
            f"关于{input_text}的问题，我的回答如下。"
        ]
        
        # 随机选择一个模拟响应
        return random.choice(mock_responses)

# 用户交互演示函数
def user_interaction_demo():
    """用户交互演示"""
    print("=== 腾讯实验室 HaS 隐私保护技术 - 增强版信息熵敏感词检索系统 ===")
    print("本系统可以帮助您识别并保护文本中的敏感信息。")
    
    # 创建工作流实例
    workflow = EntropyEnhancedHaSWorkflow()
    
    while True:
        print("\n请选择操作：")
        print("1. 执行完整的脱敏-处理-还原流程")
        print("2. 仅执行脱敏处理")
        print("3. 使用已有会话ID执行还原处理")
        print("4. 退出")
        
        choice = input("请输入选项 (1-4): ")
        
        if choice == '1':
            # 执行完整流程
            user_input = input("请输入要处理的文本：")
            result = workflow.run_complete_workflow(user_input)
            
            print("\n=== 处理结果 ===")
            print(f"原始文本：{result['original_text']}")
            print(f"脱敏后：{result['desensitized_text']}")
            print(f"大模型输出：{result['llm_output']}")
            print(f"还原后：{result['restored_text']}")
            print(f"识别到的敏感信息数量：{result['num_sensitive']}")
            print(f"会话ID：{result['session_id']}")
            print(f"处理时间：{result['processing_time']:.4f}秒")
            
        elif choice == '2':
            # 仅执行脱敏
            user_input = input("请输入要脱敏的文本：")
            result = workflow.run_desensitization(user_input)
            
            print("\n=== 脱敏结果 ===")
            print(f"脱敏后：{result['desensitized_text']}")
            print(f"识别到的敏感信息数量：{result['num_sensitive']}")
            print(f"会话ID：{result['session_id']}")
            print("请保存会话ID，用于后续的还原处理。")
            
        elif choice == '3':
            # 执行还原
            session_id = input("请输入会话ID：")
            llm_output = input("请输入大模型的输出文本：")
            
            result = workflow.run_restore(llm_output, session_id)
            
            print("\n=== 还原结果 ===")
            print(f"还原后：{result['restored_text']}")
            
        elif choice == '4':
            # 退出
            print("感谢使用，再见！")
            break
        
        else:
            print("无效的选项，请重新输入。")

# 批量测试函数
def batch_test():
    """批量测试函数"""
    print("=== 批量测试开始 ===")
    
    # 创建工作流实例
    workflow = EntropyEnhancedHaSWorkflow()
    
    # 测试用例
    test_cases = [
        {
            "name": "个人信息",
            "text": "我叫张三，身份证号码是110101199001011234，联系电话是13800138000，邮箱是zhangsan@example.com"
        },
        {
            "name": "金融信息",
            "text": "客户王小明的银行卡号是6222020200012345678，账户余额为123,456.78元，信用额度提升了20%"
        },
        {
            "name": "企业信息",
            "text": "腾讯科技(深圳)有限公司的CEO是马化腾，位于深圳市南山区海天二路33号腾讯滨海大厦"
        },
        {
            "name": "网络安全",
            "text": "服务器IP地址是192.168.1.1，管理员账号是admin，密码是Admin@123"
        }
    ]
    
    # 执行测试
    total_time = 0
    total_sensitive = 0
    
    for test_case in test_cases:
        print(f"\n测试用例：{test_case['name']}")
        start_time = time.time()
        
        result = workflow.run_complete_workflow(test_case['text'])
        
        processing_time = time.time() - start_time
        total_time += processing_time
        total_sensitive += result['num_sensitive']
        
        print(f"识别到的敏感信息数量：{result['num_sensitive']}")
        print(f"处理时间：{processing_time:.4f}秒")
        
        # 打印脱敏和还原的示例（只显示前100个字符）
        print(f"脱敏示例：{result['desensitized_text'][:100]}{'...' if len(result['desensitized_text']) > 100 else ''}")
    
    # 打印汇总信息
    print("\n=== 测试汇总 ===")
    print(f"总测试用例数：{len(test_cases)}")
    print(f"识别到的敏感信息总数：{total_sensitive}")
    print(f"平均处理时间：{total_time / len(test_cases):.4f}秒")
    print(f"总处理时间：{total_time:.4f}秒")
    print("=== 批量测试结束 ===")

if __name__ == "__main__":
    # 运行用户交互演示
    user_interaction_demo()
    
    # 可选：运行批量测试
    # batch_test()