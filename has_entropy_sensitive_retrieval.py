#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HaS (Hide and Seek) 隐私保护技术 - 增强版信息熵敏感词检索系统
基于信息熵的敏感词检索、文本脱敏与还原功能
专为低配置内网环境设计，支持用户两次输入输出流程
"""

import re
import time
import json
import math
import random
import uuid
from typing import Dict, List, Tuple, Optional, Set, Any

# 预定义的敏感信息类型和默认配置
DEFAULT_CONFIG = {
    # 信息熵检测配置
    'enable_entropy_detection': True,
    'entropy_threshold': 1.2,  # 低熵阈值，低于此值可能是结构化信息
    'high_entropy_threshold': 3.5,  # 高熵阈值，高于此值可能是敏感数据
    'max_token_len': 64,
    'min_token_len': 2,
    
    # 脱敏策略配置
    'enable_entity_placeholder': True,  # 标准占位符 <name>_0
    'enable_pseudonymization': True,    # 假名化（生成逼真替代信息）
    'enable_anonimization': True,       # 匿名化 [REDACTED_NAME]
    'enable_generalization': True,      # 数据泛化（降低粒度）
    
    # 性能优化配置
    'enable_fuzzy_matching': True,      # 模糊匹配
    'preserve_format': True,            # 保留原始格式
    'batch_process_size': 1024,         # 批处理大小
    
    # 中文处理配置
    'enable_ngram_entropy': True,       # ngram熵计算
    'ngram_size': 2,                    # ngram大小
    'enable_radical_analysis': False,   # 激进分析（可提高召回率但可能增加误报）
    'enable_position_entropy': True,    # 位置熵计算
}

# 常见姓氏列表
COMMON_SURNAMES = set('王李张刘陈杨赵黄周吴徐孙胡朱高林何郭马罗梁宋郑谢韩唐冯于董萧程曹袁邓许傅沈曾彭吕苏卢蒋蔡贾丁魏薛叶阎余潘杜戴夏钟汪田任姜范方石姚谭廖邹熊金陆郝孔白崔康毛邱秦江史顾侯邵孟龙万段漕钱汤尹黎易常武乔贺赖龚文')

# 公司后缀列表
COMPANY_SUFFIXES = (
    "公司", "有限责任公司", "股份有限公司", "集团", "研究院", "研究所",
    "银行", "证券", "保险", "基金", "事业部", "分公司",
    "子公司", "工作室", "事务所", "中心", "学院", "医院"
)

# 常见称谓（排除在姓名识别之外）
MINOR_STOPWORDS = set([
    '先生', '女士', '经理', '主任', '总', '局长', '厅长', '处长',
    '科长', '员工', '同事', '同学', '老师', '医生', '护士',
    '客户', '用户', '顾客', '先生们', '女士们', '同志', '领导'
])

# 手机号前缀
PHONE_PREFIXES = ('13', '14', '15', '16', '17', '18', '19')

class EntropyEnhancedSensitiveModel:
    """基于信息熵的增强版敏感信息检测与处理模型"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化模型"""
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.session_id = self._generate_session_id()
        self.current_mapping: Dict[str, str] = {}
        self.pseudonym_map: Dict[str, str] = {}
        self.anonymization_map: Dict[str, str] = {}
        
        # 预编译正则表达式以提高性能
        self._compile_regex_patterns()
        
    def _generate_session_id(self) -> str:
        """生成唯一的会话ID"""
        return f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    def _compile_regex_patterns(self):
        """预编译常用的正则表达式模式"""
        # 身份证号
        self.id_pattern = re.compile(r'[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]')
        # 手机号
        self.phone_pattern = re.compile(r'1[3-9]\d{9}')
        # 银行卡号（16-19位数字）
        self.bank_card_pattern = re.compile(r'\b\d{16,19}\b')
        # 邮箱
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        # 金额（带小数点和可能的货币符号）
        self.amount_pattern = re.compile(r'([¥￥$]?\d+(?:\.\d{1,2})?)')
        # IP地址
        self.ip_pattern = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
        # 邮政编码
        self.zipcode_pattern = re.compile(r'\b\d{6}\b')
    
    # ============ 增强版信息熵计算方法 ============
    
    def _char_entropy(self, s: str) -> float:
        """计算字符香农熵（基于字符分布，低依赖、轻量）"""
        if not s or len(s) <= 1:
            return 0.0
        
        # 计算字符频率
        freq: Dict[str, int] = {}
        for ch in s:
            freq[ch] = freq.get(ch, 0) + 1
        
        # 计算香农熵
        n = len(s)
        entropy = 0.0
        for count in freq.values():
            probability = count / n
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _ngram_entropy(self, s: str, n: int = 2) -> float:
        """计算N-gram信息熵（捕获字符间的关联信息）"""
        if not s or len(s) < n:
            return 0.0
        
        # 生成n-gram
        ngrams = [s[i:i+n] for i in range(len(s) - n + 1)]
        
        # 计算n-gram频率
        freq: Dict[str, int] = {}
        for gram in ngrams:
            freq[gram] = freq.get(gram, 0) + 1
        
        # 计算熵
        total = len(ngrams)
        entropy = 0.0
        for count in freq.values():
            probability = count / total
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _position_entropy(self, tokens: List[Tuple[int, int, str, str]], text: str) -> Dict[int, float]:
        """计算文本中各位置的上下文熵"""
        pos_entropy: Dict[int, float] = {}
        window_size = 5  # 上下文窗口大小
        
        for i, (start, end, tok, ttype) in enumerate(tokens):
            # 获取上下文窗口
            start_window = max(0, i - window_size)
            end_window = min(len(tokens), i + window_size + 1)
            context_tokens = tokens[start_window:end_window]
            
            # 提取上下文文本
            context_text = ''.join([t[2] for t in context_tokens])
            
            # 计算上下文熵
            context_entropy = self._char_entropy(context_text)
            
            # 为窗口中的每个位置分配熵值
            for j in range(start_window, end_window):
                s, e, _, _ = tokens[j]
                pos_entropy[(s + e) // 2] = context_entropy
        
        return pos_entropy
    
    def _tokenize_simple(self, text: str) -> List[Tuple[int, int, str, str]]:
        """简易分词：按 汉字串 / 字母数字串 / 其他 分段"""
        spans = []
        i = 0
        n = len(text)
        
        while i < n:
            ch = text[i]
            if '\u4e00' <= ch <= '\u9fff':  # 汉字
                j = i + 1
                while j < n and '\u4e00' <= text[j] <= '\u9fff':
                    j += 1
                spans.append((i, j, text[i:j], 'han'))
                i = j
            elif ch.isalnum():
                j = i + 1
                while j < n and text[j].isalnum():
                    j += 1
                spans.append((i, j, text[i:j], 'alnum'))
                i = j
            else:
                spans.append((i, i+1, ch, 'other'))
                i += 1
        
        return spans
    
    # ============ 增强版敏感信息检测 ============
    
    def _entropy_detect_candidates(self, text: str, valid_types: Optional[List[str]] = None) -> List[Tuple[int, int, str, str]]:
        """基于信息熵与启发式的敏感候选检索（增强版）"""
        if not self.config.get('enable_entropy_detection', True):
            return []
        
        # 规范化有效类型
        valid_types = valid_types or []
        
        candidates: List[Tuple[int, int, str, str]] = []
        spans = self._tokenize_simple(text)
        
        # 获取配置参数
        ent_th = float(self.config.get('entropy_threshold', 1.2))
        high_ent_th = float(self.config.get('high_entropy_threshold', 3.5))
        max_len = int(self.config.get('max_token_len', 64))
        min_len = int(self.config.get('min_token_len', 2))
        enable_ngram = self.config.get('enable_ngram_entropy', True)
        enable_pos_entropy = self.config.get('enable_position_entropy', True)
        
        # 计算位置熵（如果启用）
        pos_entropy = self._position_entropy(spans, text) if enable_pos_entropy else {}
        
        for (s, e, tok, ttype) in spans:
            token_len = e - s
            
            # 过滤长度不符合要求的token
            if token_len < min_len or token_len > max_len:
                continue
            
            # 计算基本字符熵
            char_entropy = self._char_entropy(tok)
            
            # 计算n-gram熵（如果启用）
            ngram_entropy = self._ngram_entropy(tok, int(self.config.get('ngram_size', 2))) if enable_ngram else 0
            
            # 获取位置熵（如果有）
            position_entropy = pos_entropy.get((s + e) // 2, 0)
            
            # 综合评分（权重可调整）
            entropy_score = char_entropy * 0.5 + ngram_entropy * 0.3 + position_entropy * 0.2
            
            # 1. 公司名称识别：中文串 + 公司后缀
            if ttype == 'han' and any(tok.endswith(suf) for suf in COMPANY_SUFFIXES):
                if not valid_types or 'company' in valid_types:
                    candidates.append((s, e, 'company', tok))
                continue
            
            # 2. 姓名识别：2-3 汉字，首字常见姓氏
            if ttype == 'han' and 2 <= len(tok) <= 3:
                if tok[0] in COMMON_SURNAMES and tok not in MINOR_STOPWORDS:
                    # 适当要求字符熵不过低（排除重复字名）
                    if char_entropy >= 0.5:
                        if not valid_types or 'name' in valid_types:
                            candidates.append((s, e, 'name', tok))
                    continue
            
            # 3. 账号/标识识别：字母数字串 >= 6
            if ttype == 'alnum' and len(tok) >= 6:
                # 计算数字占比
                digit_ratio = sum(c.isdigit() for c in tok) / len(tok)
                
                # 规则1: 数字占比高且熵较低（可能是结构化号码）
                if digit_ratio > 0.6 and char_entropy < ent_th:
                    if not valid_types or 'account' in valid_types:
                        candidates.append((s, e, 'account', tok))
                # 规则2: 高熵混合字符（可能是加密或敏感信息）
                elif entropy_score > high_ent_th:
                    if not valid_types or 'account' in valid_types:
                        candidates.append((s, e, 'account', tok))
                continue
            
            # 4. 特殊格式检测：结合正则和熵
            # 手机号（11位数字）
            if ttype == 'alnum' and len(tok) == 11 and tok.startswith(PHONE_PREFIXES):
                if not valid_types or 'phone' in valid_types:
                    candidates.append((s, e, 'phone', tok))
                continue
            
            # 5. 低熵敏感信息检测（如身份证号、银行卡号等）
            if ttype == 'alnum' and len(tok) >= 15 and char_entropy < ent_th:
                if not valid_types or 'id' in valid_types:
                    candidates.append((s, e, 'id', tok))
                continue
        
        # 合并/去重：按位置唯一
        candidates = self._deduplicate_overlapping_candidates(candidates)
        
        return candidates
    
    def _deduplicate_overlapping_candidates(self, candidates: List[Tuple[int, int, str, str]]) -> List[Tuple[int, int, str, str]]:
        """去重并合并重叠的候选结果"""
        if not candidates:
            return []
        
        # 按起始位置排序
        candidates.sort(key=lambda x: (x[0], -(x[1] - x[0])))  # 优先选择较长的匹配
        
        # 去重重叠候选
        unique_candidates = [candidates[0]]
        
        for curr in candidates[1:]:
            overlap = False
            for i, prev in enumerate(unique_candidates):
                # 检查是否重叠
                if not (curr[1] <= prev[0] or curr[0] >= prev[1]):
                    overlap = True
                    # 如果当前候选类型与前一个不同，且长度更长，替换前一个
                    if curr[1] - curr[0] > prev[1] - prev[0]:
                        unique_candidates[i] = curr
                    break
            
            if not overlap:
                unique_candidates.append(curr)
        
        # 按起始位置排序返回
        unique_candidates.sort(key=lambda x: x[0])
        return unique_candidates
    
    def _regex_based_detection(self, text: str, valid_types: Optional[List[str]] = None) -> List[Tuple[int, int, str, str]]:
        """基于正则表达式的敏感信息检测"""
        valid_types = valid_types or []
        regex_candidates = []
        
        # 身份证号
        if not valid_types or 'id' in valid_types:
            for match in self.id_pattern.finditer(text):
                regex_candidates.append((match.start(), match.end(), 'id', match.group()))
        
        # 手机号
        if not valid_types or 'phone' in valid_types:
            for match in self.phone_pattern.finditer(text):
                regex_candidates.append((match.start(), match.end(), 'phone', match.group()))
        
        # 银行卡号
        if not valid_types or 'bank_card' in valid_types:
            for match in self.bank_card_pattern.finditer(text):
                regex_candidates.append((match.start(), match.end(), 'bank_card', match.group()))
        
        # 邮箱
        if not valid_types or 'email' in valid_types:
            for match in self.email_pattern.finditer(text):
                regex_candidates.append((match.start(), match.end(), 'email', match.group()))
        
        # 金额
        if not valid_types or 'amount' in valid_types:
            for match in self.amount_pattern.finditer(text):
                regex_candidates.append((match.start(), match.end(), 'amount', match.group()))
        
        # IP地址
        if not valid_types or 'ip' in valid_types:
            for match in self.ip_pattern.finditer(text):
                regex_candidates.append((match.start(), match.end(), 'ip', match.group()))
        
        # 邮政编码
        if not valid_types or 'zipcode' in valid_types:
            for match in self.zipcode_pattern.finditer(text):
                regex_candidates.append((match.start(), match.end(), 'zipcode', match.group()))
        
        return regex_candidates
    
    # ============ 脱敏策略实现 ============
    
    def _generate_pseudonym(self, original: str, type_name: str) -> str:
        """生成假名/替代信息"""
        # 如果已经有对应的假名，直接返回
        if original in self.pseudonym_map:
            return self.pseudonym_map[original]
        
        pseudonym = ""
        
        if type_name == 'name':
            # 生成随机姓名
            surname = random.choice(list(COMMON_SURNAMES))
            given_names = '伟芳娜秀英敏静强磊军洋杰丽娟桂兰英健明'  # 常见名字字符
            given_name_len = 1 if len(original) == 2 else 2  # 保持姓名长度一致
            given_name = ''.join(random.sample(given_names, given_name_len))
            pseudonym = surname + given_name
        
        elif type_name == 'phone':
            # 生成随机手机号
            prefix = random.choice(PHONE_PREFIXES)
            suffix = ''.join(random.choices('0123456789', k=9))
            pseudonym = prefix + suffix
        
        elif type_name == 'company':
            # 生成随机公司名
            prefixes = ['恒信', '远大', '诚信', '创新', '卓越', '华夏', '东方', '环球']
            industries = ['科技', '贸易', '金融', '投资', '咨询', '电子', '生物', '医药']
            suffix = original[original.rfind('公司'):] if '公司' in original else random.choice(['有限公司', '科技有限公司'])
            pseudonym = random.choice(prefixes) + random.choice(industries) + suffix
        
        else:
            # 其他类型生成UUID作为替代
            pseudonym = f"PSEUDO_{uuid.uuid4().hex[:8]}"
        
        # 保存映射关系
        self.pseudonym_map[original] = pseudonym
        
        return pseudonym
    
    def _generate_anonymization(self, type_name: str) -> str:
        """生成匿名化标记"""
        # 使用类型名称作为匿名化标记
        anonymization = f"[REDACTED_{type_name.upper()}]"
        return anonymization
    
    def _generate_placeholder(self, type_name: str, count: int) -> str:
        """生成标准占位符"""
        return f"<{type_name}>_{count}"
    
    def _generalize_data(self, original: str, type_name: str) -> str:
        """数据泛化（降低粒度）"""
        if type_name == 'amount':
            # 金额泛化：四舍五入到千位或万位
            try:
                # 移除货币符号
                amount_str = re.sub(r'[¥￥$]', '', original)
                amount = float(amount_str)
                if amount >= 10000:
                    return f"{round(amount / 10000)}万"
                elif amount >= 1000:
                    return f"{round(amount / 1000)}千"
                else:
                    return "少量"
            except:
                return "金额"
        
        elif type_name == 'age':
            # 年龄泛化：转换为年龄段
            try:
                age = int(original)
                if age < 18:
                    return "未成年"
                elif age < 30:
                    return "青年"
                elif age < 50:
                    return "中年"
                else:
                    return "老年"
            except:
                return "年龄"
        
        elif type_name == 'address':
            # 地址泛化：保留省份，移除详细信息
            # 简单实现，实际应用中可以使用更复杂的地址解析
            provinces = ['北京市', '上海市', '广东省', '江苏省', '浙江省', '山东省', '河南省', '四川省', '湖北省', '湖南省']
            if any(prov in original for prov in provinces):
                for prov in provinces:
                    if prov in original:
                        return prov + '某地'
            return "地址"
        
        else:
            # 其他类型简单返回类型名称
            return type_name
    
    # ============ 主脱敏和还原功能 ============
    
    def desensitize(self, text: str, sensitive_types: Optional[List[str]] = None) -> Tuple[str, Dict[str, str]]:
        """主脱敏函数：识别并脱敏敏感信息"""
        # 重置映射关系
        self.current_mapping = {}
        
        # 识别敏感信息（结合信息熵和正则方法）
        entropy_candidates = self._entropy_detect_candidates(text, sensitive_types)
        regex_candidates = self._regex_based_detection(text, sensitive_types)
        
        # 合并候选结果
        all_candidates = entropy_candidates + regex_candidates
        all_candidates = self._deduplicate_overlapping_candidates(all_candidates)
        
        # 按结束位置逆序排序，避免替换时位置偏移
        all_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 创建结果文本的副本
        result_text = text
        
        # 统计各类型出现次数
        type_count: Dict[str, int] = {}
        
        # 处理每个候选
        for start, end, type_name, original in all_candidates:
            # 更新类型计数
            type_count[type_name] = type_count.get(type_name, 0) + 1
            count = type_count[type_name]
            
            # 根据配置选择脱敏策略
            if self.config.get('enable_entity_placeholder', True):
                # 标准占位符策略
                placeholder = self._generate_placeholder(type_name, count)
                self.current_mapping[placeholder] = original
            
            elif self.config.get('enable_pseudonymization', True):
                # 假名化策略
                pseudonym = self._generate_pseudonym(original, type_name)
                self.current_mapping[pseudonym] = original
            
            elif self.config.get('enable_anonimization', True):
                # 匿名化策略
                anonymization = self._generate_anonymization(type_name)
                self.current_mapping[anonymization] = original
            
            elif self.config.get('enable_generalization', True):
                # 数据泛化策略
                generalized = self._generalize_data(original, type_name)
                self.current_mapping[generalized] = original
            
            else:
                # 默认使用占位符
                placeholder = self._generate_placeholder(type_name, count)
                self.current_mapping[placeholder] = original
            
            # 替换原文中的敏感信息
            placeholder = list(self.current_mapping.keys())[-1]  # 获取最后添加的占位符
            result_text = result_text[:start] + placeholder + result_text[end:]
        
        return result_text, self.current_mapping
    
    def restore(self, text: str) -> str:
        """还原函数：将脱敏文本中的标记替换回原始敏感信息"""
        result_text = text
        
        # 按长度降序排序映射键，避免部分匹配
        sorted_placeholders = sorted(self.current_mapping.keys(), key=len, reverse=True)
        
        for placeholder in sorted_placeholders:
            original = self.current_mapping[placeholder]
            # 替换文本中的占位符
            result_text = result_text.replace(placeholder, original)
        
        return result_text

class EntropyEnhancedHaSWorkflow:
    """集成增强版信息熵敏感词检测的完整HaS工作流"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化工作流"""
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.endside_model = EntropyEnhancedSensitiveModel(self.config)
    
    def configure_desensitization_strategy(
            self,
            enable_entity_placeholder: bool = True,
            enable_pseudonymization: bool = False,
            enable_anonimization: bool = False,
            enable_generalization: bool = False
    ):
        """配置脱敏策略"""
        self.config['enable_entity_placeholder'] = enable_entity_placeholder
        self.config['enable_pseudonymization'] = enable_pseudonymization
        self.config['enable_anonimization'] = enable_anonimization
        self.config['enable_generalization'] = enable_generalization
        
        # 更新模型配置
        self.endside_model.config = {**self.endside_model.config, **self.config}
    
    def configure_endside_model(self, **kwargs):
        """配置端侧模型"""
        self.config.update(kwargs)
        self.endside_model.config = {**self.endside_model.config, **self.config}
    
    def run(self, text: str, sensitive_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """运行完整工作流：脱敏→模拟大模型处理→还原"""
        start_time = time.time()
        
        # 脱敏处理
        desensitize_start = time.time()
        desensitized_text, mapping = self.endside_model.desensitize(text, sensitive_types)
        desensitize_time = time.time() - desensitize_start
        
        # 模拟大模型处理（实际应用中这里会调用外部大模型）
        llm_start = time.time()
        # 这里简单模拟大模型处理，实际应用中需要替换为真实的大模型调用
        llm_text = self._simulate_llm_processing(desensitized_text)
        llm_time = time.time() - llm_start
        
        # 还原处理
        restore_start = time.time()
        restored_text = self.endside_model.restore(llm_text)
        restore_time = time.time() - restore_start
        
        # 计算总耗时
        total_time = time.time() - start_time
        
        # 输出结果
        print(f"\n===== HaS 隐私保护工作流结果 ======")
        print(f"原始文本: {text}")
        print(f"脱敏后文本: {desensitized_text}")
        print(f"大模型处理后: {llm_text}")
        print(f"还原后文本: {restored_text}")
        print(f"\n===== 性能统计 ======")
        print(f"脱敏耗时: {desensitize_time:.3f}秒")
        print(f"大模型处理耗时: {llm_time:.3f}秒")
        print(f"还原耗时: {restore_time:.3f}秒")
        print(f"总耗时: {total_time:.3f}秒")
        print(f"识别到的敏感信息数: {len(mapping)}")
        print("====================================\n")
        
        return {
            'desensitized_text': desensitized_text,
            'llm_text': llm_text,
            'restored_text': restored_text,
            'mapping': mapping,
            'timing': {
                'desensitize': desensitize_time,
                'llm': llm_time,
                'restore': restore_time,
                'total': total_time
            }
        }
    
    def _simulate_llm_processing(self, text: str) -> str:
        """模拟大模型处理文本"""
        # 简单模拟大模型的文本改写和信息处理
        # 实际应用中，这里会将脱敏后的文本发送给外部大模型
        # 并接收大模型的处理结果
        return text

# ===== 演示和测试功能 =====

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
        "sensitive_types": None
    }
]

def user_interaction_demo():
    """用户交互演示功能"""
    print("\n===== HaS (Hide and Seek) 隐私保护技术 - 信息熵增强版演示 ======")
    print("提示：输入 'exit' 或 '退出' 结束程序。\n")
    print("本系统专为低配置内网环境设计，基于增强版信息熵算法实现敏感词检索和文本脱敏还原功能。\n")
    
    # 会话映射字典，用于保存脱敏映射关系
    session_mappings: Dict[str, Dict[str, Any]] = {}
    
    while True:
        try:
            print("请选择操作：")
            print("1. 使用预设场景进行演示")
            print("2. 输入自定义文本进行演示")
            print("3. 第一步：输入文本进行脱敏（生成可复制的脱敏文本）")
            print("4. 第二步：输入大模型回答进行还原（使用之前的脱敏映射）")
            print("5. 退出程序")
            
            choice = input("请选择 (1-5): ").strip()
            
            if choice == '1':
                # 使用预设场景进行演示
                print("\n请选择预设场景：")
                for i, scenario in enumerate(preset_scenarios, 1):
                    print(f"{i}. {scenario['name']}: {scenario['description']}")
                
                scenario_choice = input("请选择场景 (1-4): ").strip()
                if scenario_choice.isdigit() and 1 <= int(scenario_choice) <= len(preset_scenarios):
                    scenario_idx = int(scenario_choice) - 1
                    selected_scenario = preset_scenarios[scenario_idx]
                    
                    # 创建工作流实例
                    has_workflow = EntropyEnhancedHaSWorkflow()
                    
                    # 询问是否需要指定脱敏策略
                    specify_strategy = input("是否需要指定脱敏策略？(y/n，默认n)：").strip().lower() == 'y'
                    
                    if specify_strategy:
                        print("请选择脱敏策略：")
                        print("1. 标准占位符（<name>_0）")
                        print("2. 假名化（生成逼真的替代信息）")
                        print("3. 匿名化（[REDACTED_NAME]）")
                        print("4. 数据泛化（降低数据粒度，如年龄转年龄段）")
                        
                        strategy_choice = input("请选择策略 (1-4)：").strip()
                        
                        if strategy_choice == '1':
                            # 标准占位符策略
                            has_workflow.configure_desensitization_strategy(
                                enable_entity_placeholder=True,
                                enable_pseudonymization=False,
                                enable_anonimization=False,
                                enable_generalization=False
                            )
                        elif strategy_choice == '2':
                            # 假名化策略
                            has_workflow.configure_desensitization_strategy(
                                enable_pseudonymization=True,
                                enable_anonimization=False,
                                enable_generalization=False
                            )
                        elif strategy_choice == '3':
                            # 匿名化策略
                            has_workflow.configure_desensitization_strategy(
                                enable_pseudonymization=False,
                                enable_anonimization=True,
                                enable_generalization=False
                            )
                        elif strategy_choice == '4':
                            # 数据泛化策略
                            has_workflow.configure_desensitization_strategy(
                                enable_pseudonymization=False,
                                enable_anonimization=False,
                                enable_generalization=True
                            )
                    
                    # 运行工作流
                    inp = str(selected_scenario.get('input', ''))
                    st = selected_scenario.get('sensitive_types', None)
                    has_workflow.run(inp, st)
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
                has_workflow = EntropyEnhancedHaSWorkflow()
                
                # 询问用户是否需要指定脱敏策略
                specify_strategy = input("是否需要指定脱敏策略？(y/n，默认n)：").strip().lower() == 'y'
                
                if specify_strategy:
                    print("请选择脱敏策略：")
                    print("1. 标准占位符（<name>_0）")
                    print("2. 假名化（生成逼真的替代信息）")
                    print("3. 匿名化（[REDACTED_NAME]）")
                    print("4. 数据泛化（降低数据粒度，如年龄转年龄段）")
                    
                    strategy_choice = input("请选择策略 (1-4)：").strip()
                    
                    if strategy_choice == '1':
                        has_workflow.configure_desensitization_strategy(
                            enable_entity_placeholder=True,
                            enable_pseudonymization=False,
                            enable_anonimization=False,
                            enable_generalization=False
                        )
                    elif strategy_choice == '2':
                        has_workflow.configure_desensitization_strategy(
                            enable_pseudonymization=True,
                            enable_anonimization=False,
                            enable_generalization=False
                        )
                    elif strategy_choice == '3':
                        has_workflow.configure_desensitization_strategy(
                            enable_pseudonymization=False,
                            enable_anonimization=True,
                            enable_generalization=False
                        )
                    elif strategy_choice == '4':
                        has_workflow.configure_desensitization_strategy(
                            enable_pseudonymization=False,
                            enable_anonimization=False,
                            enable_generalization=True
                        )
                
                # 询问用户是否需要指定脱敏类型
                specify_types = input("是否需要指定脱敏的信息类型？(y/n，默认n)：").strip().lower() == 'y'
                
                if specify_types:
                    print("请选择需要脱敏的信息类型（多个类型用逗号分隔，如 name,company,position）：")
                    print("支持的类型：name(姓名), company(公司), position(职位), department(部门),")
                    print("phone(手机号), id(身份证), email(邮箱), bank_card(银行卡),")
                    print("amount(金额), performance(业绩指标), age(年龄), address(地址),")
                    print("zipcode(邮政编码), ip(IP地址), account(账号)")
                    
                    types_input = input("请输入类型：").strip().lower()
                    sensitive_types = [t.strip() for t in types_input.split(',') if t.strip()]
                else:
                    sensitive_types = None  # 使用默认类型
                
                # 运行工作流
                has_workflow.run(custom_text, sensitive_types)
            
            elif choice == '3':
                # 仅进行脱敏处理
                print("\n===== 仅脱敏处理模式 =====")
                print("此模式适用于实际使用场景：")
                print("1. 在内网电脑上输入包含敏感信息的文本")
                print("2. 系统对文本进行脱敏处理")
                print("3. 用户将脱敏后的文本复制到外网使用大模型")
                print("4. 保存脱敏映射关系，用于后续还原操作")
                
                custom_text = input("\n请输入您需要脱敏的文本：").strip()
                if not custom_text:
                    print("输入不能为空，请重新输入。\n")
                    continue
                
                # 创建工作流实例
                has_workflow = EntropyEnhancedHaSWorkflow()
                
                # 询问用户是否需要指定脱敏策略
                specify_strategy = input("是否需要指定脱敏策略？(y/n，默认n)：").strip().lower() == 'y'
                
                if specify_strategy:
                    print("请选择脱敏策略：")
                    print("1. 标准占位符（<name>_0）")
                    print("2. 假名化（生成逼真的替代信息）")
                    print("3. 匿名化（[REDACTED_NAME]）")
                    print("4. 数据泛化（降低数据粒度，如年龄转年龄段）")
                    
                    strategy_choice = input("请选择策略 (1-4)：").strip()
                    
                    if strategy_choice == '1':
                        has_workflow.configure_desensitization_strategy(
                            enable_entity_placeholder=True,
                            enable_pseudonymization=False,
                            enable_anonimization=False,
                            enable_generalization=False
                        )
                    elif strategy_choice == '2':
                        has_workflow.configure_desensitization_strategy(
                            enable_pseudonymization=True,
                            enable_anonimization=False,
                            enable_generalization=False
                        )
                    elif strategy_choice == '3':
                        has_workflow.configure_desensitization_strategy(
                            enable_pseudonymization=False,
                            enable_anonimization=True,
                            enable_generalization=False
                        )
                    elif strategy_choice == '4':
                        has_workflow.configure_desensitization_strategy(
                            enable_pseudonymization=False,
                            enable_anonimization=False,
                            enable_generalization=True
                        )
                
                # 询问用户是否需要指定脱敏类型
                specify_types = input("是否需要指定脱敏的信息类型？(y/n，默认n)：").strip().lower() == 'y'
                
                if specify_types:
                    print("请选择需要脱敏的信息类型（多个类型用逗号分隔，如 name,company,position）：")
                    print("支持的类型：name(姓名), company(公司), position(职位), department(部门),")
                    print("phone(手机号), id(身份证), email(邮箱), bank_card(银行卡),")
                    print("amount(金额), performance(业绩指标), age(年龄), address(地址),")
                    print("zipcode(邮政编码), ip(IP地址), account(账号)")
                    
                    types_input = input("请输入类型：").strip().lower()
                    sensitive_types = [t.strip() for t in types_input.split(',') if t.strip()]
                else:
                    sensitive_types = None  # 使用默认类型
                
                # 执行脱敏处理
                print(f"\n===== 脱敏处理开始 =====")
                print(f"用户原始输入: {custom_text}")
                
                # 仅执行脱敏处理，不调用模拟大模型
                desensitized_text, mapping = has_workflow.endside_model.desensitize(custom_text, sensitive_types)
                
                # 保存映射关系到会话字典
                session_id = has_workflow.endside_model.session_id
                session_mappings[session_id] = {
                    'mapping': mapping,
                    'pseudonym_map': has_workflow.endside_model.pseudonym_map,
                    'anonymization_map': has_workflow.endside_model.anonymization_map,
                    'config': has_workflow.endside_model.config
                }
                
                print(f"脱敏后文本: {desensitized_text}")
                print(f"脱敏映射关系已保存，会话ID: {session_id}")
                print("\n请复制上面的脱敏后文本，在外部大模型中使用。")
                print("提示：请记下会话ID，后续还原时需要使用。")
                print("===== 脱敏处理完成 =====")
                
            elif choice == '4':
                # 仅进行还原处理
                print("\n===== 仅还原处理模式 =====")
                print("此模式适用于实际使用场景：")
                print("1. 用户已在外网大模型中使用脱敏文本")
                print("2. 将大模型生成的文本输入到此模式")
                print("3. 系统根据之前保存的映射关系还原敏感信息")
                
                # 检查是否有可用的会话映射
                if not session_mappings:
                    print("错误：未找到任何保存的脱敏映射关系。")
                    print("请先使用'仅进行脱敏处理'功能生成映射关系。")
                    continue
                
                # 显示可用的会话ID
                print("可用的会话ID列表：")
                for session_id in session_mappings.keys():
                    print(f"- {session_id}")
                
                session_id = input("请输入用于还原的会话ID：").strip()
                
                if session_id not in session_mappings:
                    print(f"错误：未找到会话ID '{session_id}' 的映射关系。")
                    continue
                
                # 获取映射关系
                session_data = session_mappings[session_id]
                
                # 创建新的端侧模型实例
                restore_model = EntropyEnhancedSensitiveModel()
                restore_model.session_id = session_id
                restore_model.current_mapping = session_data['mapping']
                restore_model.pseudonym_map = session_data['pseudonym_map']
                restore_model.anonymization_map = session_data['anonymization_map']
                restore_model.config = session_data['config']
                
                # 获取大模型生成的文本
                llm_text = input("请输入大模型生成的文本：").strip()
                if not llm_text:
                    print("输入不能为空，请重新输入。\n")
                    continue
                
                # 执行还原处理
                print(f"\n===== 还原处理开始 =====")
                restored_text = restore_model.restore(llm_text)
                
                print(f"还原后的文本: {restored_text}")
                print("===== 还原处理完成 =====")
                
            elif choice in ['5', 'exit', '退出']:
                print("感谢使用HaS隐私保护工作流演示，再见！")
                break
            
            else:
                print("无效的选择，请重新输入。\n")
                continue
            
            # 询问用户是否继续
            if choice in ['1', '2']:
                continue_choice = input("\n是否继续？(y/n，默认y)：").strip().lower()
                if continue_choice != 'y':
                    print("感谢使用HaS隐私保护工作流演示，再见！")
                    break
            
            print("\n" + "="*80 + "\n")
            
        except Exception as e:
            print(f"处理过程中发生错误：{e}")
            print("请重新输入或选择退出。\n")

def batch_test():
    """批量测试不同场景下的HaS工作流性能"""
    print("\n===== HaS (Hide and Seek) 隐私保护技术 - 批量测试 ======")
    
    # 测试不同配置组合
    configurations = [
        {"name": "标准配置", "enable_entity_placeholder": True, "preserve_format": True, "enable_fuzzy_matching": True},
        {"name": "简化模式", "enable_entity_placeholder": True, "preserve_format": False, "enable_fuzzy_matching": False},
        {"name": "高性能模式", "enable_entity_placeholder": True, "enable_entropy_detection": True, "enable_radical_analysis": False}
    ]
    
    from typing import Dict, Any, cast
    
    for config in configurations:
        print(f"\n\n----- 测试配置: {config['name']} -----")
        
        total_times = []
        
        for i, scenario in enumerate(preset_scenarios, 1):
            print(f"场景 {i}: {scenario['name']}")
            
            # 创建工作流实例
            has_workflow = EntropyEnhancedHaSWorkflow()
            has_workflow.configure_endside_model(**config)
            
            # 运行工作流
            scen_inp = str(scenario.get('input', ''))
            scen_st = scenario.get('sensitive_types', None)
            result = has_workflow.run(
                scen_inp,
                scen_st
            )
            
            # 记录总耗时
            timing_dict = cast(Dict[str, Any], result.get('timing', {}))
            total_val = timing_dict.get('total', 0.0)
            total_times.append(float(total_val))
        
        # 计算平均耗时
        avg_time = sum(total_times) / len(total_times)
        print(f"\n配置 '{config['name']}' 的平均处理时间: {avg_time:.3f}秒")

# ===== 程序入口 =====

if __name__ == "__main__":
    user_interaction_demo()
    # 如需批量测试，取消下面一行的注释
    # batch_test()