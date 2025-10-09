import time
import re
import random
import uuid
from typing import Dict, Tuple, Optional, List, Any, cast

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
        # 最近一次用户原始输入（用于上下文与类型检查友好）
        self.last_user_input = ""
        # 配置选项
        self.config = {
            'enable_entity_placeholder': True,  # 使用实体占位符格式
            'preserve_format': True,           # 是否保留原始格式
            'enable_fuzzy_matching': True,     # 是否启用模糊匹配还原
            'min_confidence': 0.7,             # 模糊匹配的最小置信度
            'max_distance': 3,                 # 允许的最大字符差异
            'custom_patterns': None,           # 自定义敏感信息模式
            'enable_pseudonymization': False,  # 是否启用假名化
            'enable_anonimization': False,     # 是否启用匿名化
            'enable_generalization': True,     # 是否启用数据泛化（降低粒度）
            # 信息熵辅助检索
            'enable_entropy_detection': True,  # 启用信息熵/启发式候选召回
            'entropy_threshold': 1.2,          # 字符熵阈值（用于区分结构化/非结构化片段，经验值）
            'max_token_len': 32                # 最大候选token长度
        }
        # 存储假名映射关系（用于假名化）
        self.pseudonym_map = {}
        # 存储匿名化映射关系
        self.anonymization_map = {}
        # 存储数据泛化映射关系
        self.generalization_map = {}
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
            },
            'age': {
                'pattern': r'(\d{1,3})\s*岁',
                'description': '年龄',
                'placeholder': '<age>'
            },
            'address': {
                'pattern': r'(?:居住在|住在|地址是)?([\u4e00-\u9fa5]+省[\u4e00-\u9fa5]+市[\u4e00-\u9fa5]+区[\u4e00-\u9fa5]*路[\d]+号)',
                'description': '详细地址',
                'placeholder': '<address>'
            },
            'zipcode': {
                'pattern': r'(邮政编码|邮编)[:：]?\s*(\d{6})',
                'description': '邮政编码',
                'placeholder': '<zipcode>'
            },
            'ip': {
                'pattern': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
                'description': 'IP地址',
                'placeholder': '<ip>'
            },
            'account': {
                'pattern': r'(账号|账户|用户名)[：:]?\s*([a-zA-Z0-9_]{4,20})',
                'description': '账号/用户名',
                'placeholder': '<account>'
            }
        }
        # 预编译正则表达式以提高性能
        self.compiled_patterns = {}
        for key, value in self.sensitive_patterns.items():
            self.compiled_patterns[key] = re.compile(value['pattern'])
        # 常见中文姓氏与少量停用词（轻量、内置）
        self.common_surnames = set(list("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛范彭郎鲁韦昌马苗凤花方俞任袁柳唐罗薛伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉龚程邢裴陆荣翁荀羊於惠甄麴家封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯伊宁仇甘斜厉戎祖武符刘景詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲台从鄂索咸籍赖卓蔺屠蒙池乔阴欎胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍郤璩桑桂濮牛寿通边扈燕冀郏浦咸籍") )
        self.minor_stopwords = set(["先生","女士","小姐","同志","用户","客户","朋友","同学","同事","老师"])

    def _generate_session_id(self):
        """生成唯一的会话ID"""
        return f"session_{int(time.time())}_{int(time.time() * 1000) % 10000}"

    # ============ 信息熵/启发式辅助检索 ============

    def _char_entropy(self, s: str) -> float:
        """计算字符香农熵（基于字符分布，低依赖、轻量）"""
        if not s:
            return 0.0
        from math import log2
        freq = {}
        for ch in s:
            freq[ch] = freq.get(ch, 0) + 1
        n = len(s)
        h = 0.0
        for c in freq.values():
            p = c / n
            h -= p * log2(p)
        return h

    def _tokenize_simple(self, text: str):
        """
        简易分词：按 汉字串 / 字母数字串 / 其他 分段，返回[(start,end,token,type)]
        type in {'han','alnum','other'}
        """
        spans = []
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            if '\u4e00' <= ch <= '\u9fff':
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

    def _entropy_detect_candidates(self, text: str, valid_types: List[str]):
        """
        基于信息熵与启发式的敏感候选检索（低配可用）
        返回列表：[(start,end,type,original)]
        """
        if not self.config.get('enable_entropy_detection', True):
            return []

        candidates = []
        spans = self._tokenize_simple(text)
        ent_th_cfg = self.config.get('entropy_threshold', 1.2)
        ent_th = float(ent_th_cfg) if isinstance(ent_th_cfg, (int, float)) else 1.2
        max_len = self.config.get('max_token_len', 32)

        # 辅助：公司后缀
        company_suffixes = ("公司","有限责任公司","股份有限公司","集团","研究院","研究所","银行","证券","保险","基金","事业部","分公司","子公司","工作室","事务所")

        for (s, e, tok, ttype) in spans:
            if len(tok) == 0 or (e - s) > max_len:
                continue

            # 公司：中文串 + 公司后缀，熵通常中等，但结构特征明显
            if ttype == 'han' and any(tok.endswith(suf) for suf in company_suffixes):
                if 'company' in valid_types or not valid_types:
                    candidates.append((s, e, 'company', tok))
                continue

            # 姓名：2-3 汉字，首字常见姓氏，避免称谓
            if ttype == 'han' and 2 <= len(tok) <= 3:
                if tok[0] in self.common_surnames and tok not in self.minor_stopwords:
                    # 适当要求字符熵不过低（排除重复字名）
                    if self._char_entropy(tok) >= 0.5:
                        if 'name' in valid_types or not valid_types:
                            candidates.append((s, e, 'name', tok))
                        continue

            # 账号/标识：字母数字串 >= 6，字符类别多样或低熵结构数字长串
            if ttype == 'alnum' and len(tok) >= 6:
                h = self._char_entropy(tok)
                # 数字占比高或熵较低（规则化号码），视为账号/标识
                digit_ratio = sum(c.isdigit() for c in tok) / len(tok)
                if digit_ratio > 0.6 or h < ent_th:
                    if 'account' in valid_types or not valid_types:
                        candidates.append((s, e, 'account', tok))
                    continue

        # 合并/去重：按位置唯一
        candidates.sort(key=lambda x: x[0])
        merged = []
        last_end = -1
        for c in candidates:
            if c[0] >= last_end:
                merged.append(c)
                last_end = c[1]
        return merged

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
        
    def _generalize_age(self, age: str) -> str:
        """
        对年龄进行数据泛化（降低粒度）
        
        参数:
        age: 具体年龄字符串
        
        返回:
        str: 泛化后的年龄段
        """
        try:
            age_num = int(age)
            if age_num < 18:
                return '未成年人'
            elif 18 <= age_num < 30:
                return '18-29岁'
            elif 30 <= age_num < 40:
                return '30-39岁'
            elif 40 <= age_num < 50:
                return '40-49岁'
            elif 50 <= age_num < 60:
                return '50-59岁'
            else:
                return '60岁以上'
        except:
            return age
            
    def _generalize_address(self, address: str) -> str:
        """
        对地址进行数据泛化（降低粒度）
        
        参数:
        address: 详细地址字符串
        
        返回:
        str: 泛化后的地址（只保留省、市）
        """
        # 提取省和市的信息
        province_pattern = r'([\u4e00-\u9fa5]+省)'
        city_pattern = r'([\u4e00-\u9fa5]+市)'
        
        province_match = re.search(province_pattern, address)
        city_match = re.search(city_pattern, address)
        
        province = province_match.group(1) if province_match else ''
        city = city_match.group(1) if city_match else ''
        
        return f'{province}{city}'
        
    def _generalize_zipcode(self, zipcode: str) -> str:
        """
        对邮政编码进行数据泛化（降低粒度）
        
        参数:
        zipcode: 完整邮政编码
        
        返回:
        str: 泛化后的邮政编码（只保留前两位）
        """
        return zipcode[:2] + '0000'
        
    def _pseudonymize(self, sensitive_type: str, original_text: str) -> str:
        """
        对敏感信息进行假名化处理
        
        参数:
        sensitive_type: 敏感信息类型
        original_text: 原始敏感信息文本
        
        返回:
        str: 假名化后的信息
        """
        # 检查是否已经为该原始文本生成过假名
        if original_text in self.pseudonym_map:
            return self.pseudonym_map[original_text]
        
        # 根据不同类型生成不同格式的假名
        if sensitive_type == 'name':
            # 生成随机姓名
            family_names = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄']
            given_names = ['明', '华', '强', '伟', '丽', '静', '敏', '磊']
            pseudonym = random.choice(family_names) + random.choice(given_names)
            # 对于双字名，可以再加一个字
            if random.random() > 0.5:
                pseudonym += random.choice(given_names)
        elif sensitive_type == 'company':
            # 生成随机公司名
            prefixes = ['诚信', '创新', '科技', '发展', '未来', '远大', '东方']
            suffixes = ['科技有限公司', '贸易有限公司', '集团股份有限公司', '信息技术有限公司']
            pseudonym = random.choice(prefixes) + random.choice(suffixes)
        elif sensitive_type == 'phone':
            # 生成随机手机号
            pseudonym = '1' + str(random.randint(3, 9)) + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        else:
            # 其他类型使用UUID生成唯一标识符
            pseudonym = f"{sensitive_type}_{uuid.uuid4().hex[:6]}"
        
        # 保存映射关系
        self.pseudonym_map[original_text] = pseudonym
        self.pseudonym_map[pseudonym] = original_text
        
        return pseudonym
        
    def _anonymize(self, sensitive_type: str, original_text: str) -> str:
        """
        对敏感信息进行匿名化处理
        
        参数:
        sensitive_type: 敏感信息类型
        original_text: 原始敏感信息文本
        
        返回:
        str: 匿名化后的信息（如[REDACTED_NAME]）
        """
        # 生成匿名化标签
        anonymized_label = f"[REDACTED_{sensitive_type.upper()}]"
        
        # 保存映射关系
        unique_id = f"{sensitive_type}_{len(self.anonymization_map)}"
        self.anonymization_map[unique_id] = original_text
        self.anonymization_map[original_text] = unique_id
        
        return anonymized_label

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
        
        # 先进行信息熵/启发式候选召回，作为正则前置补充
        desensitized_text = user_input
        entity_count = 0

        processed_positions = []

        entropy_candidates = self._entropy_detect_candidates(user_input, valid_types)
        # 先替换这些候选，避免后续正则被语义改写影响
        # 从左到右处理，避免位置错乱
        for (start, end, etype, original_text) in entropy_candidates:
            # 跳过与已处理重叠
            overlap = any(not (end <= ps or start >= pe) for (ps, pe) in processed_positions)
            if overlap:
                continue
            # 选择占位符
            placeholder = self.sensitive_patterns.get(etype, {'placeholder': '<entity>'})['placeholder']
            if self.config['enable_pseudonymization']:
                replacement = self._pseudonymize(etype, original_text)
            elif self.config['enable_anonimization']:
                replacement = self._anonymize(etype, original_text)
            elif self.config['enable_generalization']:
                # 熵候选不做粒度降低，使用占位以便还原
                unique_id = f"{placeholder}_{entity_count}"
                entity_count += 1
                replacement = unique_id
            else:
                unique_id = f"{placeholder}_{entity_count}"
                entity_count += 1
                replacement = unique_id

            if not (self.config['enable_pseudonymization'] or self.config['enable_anonimization']):
                unique_id = f"{placeholder}_{entity_count - 1}"
                self.current_mapping[unique_id] = original_text

            # 执行替换并更新已处理区间（注意文本长度变化）
            desensitized_text = desensitized_text[:start] + replacement + desensitized_text[end:]
            new_end = start + len(replacement)
            processed_positions.append((start, new_end))

        # 对每种敏感信息类型进行脱敏处理（正则主流程）
        # 使用 processed_positions 避免与前置候选重复
        # 注意：下面已有代码块使用 processed_positions，我保留并复用
        
        # 按照优先级排序处理，避免嵌套匹配问题
        priority_order = ['company', 'department', 'position', 'performance', 'amount', 'email', 'phone', 'id', 'name', 'age', 'address', 'zipcode', 'ip', 'account']
        processing_order = [t for t in priority_order if t in valid_types] + [t for t in valid_types if t not in priority_order]
        
        # 用于记录已处理的位置，避免重复脱敏
        # processed_positions 已由熵候选阶段初始化与更新
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
                    
                    # 根据配置选择脱敏策略
                    if self.config['enable_pseudonymization']:
                        # 假名化处理
                        replacement = self._pseudonymize(type_name, original_text)
                    elif self.config['enable_anonimization']:
                        # 匿名化处理
                        replacement = self._anonymize(type_name, original_text)
                    elif self.config['enable_generalization']:
                        # 数据泛化处理（降低粒度）
                        if type_name == 'age':
                            replacement = self._generalize_age(original_text)
                        elif type_name == 'address':
                            replacement = self._generalize_address(original_text)
                        elif type_name == 'zipcode':
                            replacement = self._generalize_zipcode(original_text)
                        else:
                            # 其他类型使用标准占位符
                            unique_id = f"{placeholder}_{entity_count}"
                            entity_count += 1
                            replacement = unique_id
                    else:
                        # 标准占位符处理
                        unique_id = f"{placeholder}_{entity_count}"
                        entity_count += 1
                        replacement = unique_id
                    
                    # 保存映射关系
                    if not (self.config['enable_pseudonymization'] or self.config['enable_anonimization']):
                        # 对于假名化和匿名化，映射关系已经在对应的方法中保存
                        unique_id = f"{placeholder}_{entity_count - 1}"
                        self.current_mapping[unique_id] = original_text
                    
                    # 替换原文中的敏感信息
                    desensitized_text = desensitized_text[:start] + replacement + desensitized_text[end:]
                    
                    # 更新已处理的位置（注意：替换后文本长度可能变化，需要重新计算位置）
                    new_end = start + len(replacement)
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
                        
                        # 根据配置选择脱敏策略
                        if self.config['enable_pseudonymization']:
                            # 假名化处理
                            replacement = self._pseudonymize(type_name, original_text)
                        elif self.config['enable_anonimization']:
                            # 匿名化处理
                            replacement = self._anonymize(type_name, original_text)
                        elif self.config['enable_generalization']:
                            # 数据泛化处理（降低粒度）
                            if type_name == 'age':
                                replacement = self._generalize_age(original_text)
                            elif type_name == 'address':
                                replacement = self._generalize_address(original_text)
                            elif type_name == 'zipcode':
                                replacement = self._generalize_zipcode(original_text)
                            else:
                                # 其他类型使用标准占位符
                                unique_id = f"{placeholder}_{entity_count}"
                                entity_count += 1
                                replacement = unique_id
                        else:
                            # 标准占位符处理
                            unique_id = f"{placeholder}_{entity_count}"
                            entity_count += 1
                            replacement = unique_id
                        
                        # 保存映射关系
                        if not (self.config['enable_pseudonymization'] or self.config['enable_anonimization']):
                            # 对于假名化和匿名化，映射关系已经在对应的方法中保存
                            unique_id = f"{placeholder}_{entity_count - 1}"
                            self.current_mapping[unique_id] = original_text
                        
                        desensitized_text = desensitized_text[:start] + replacement + desensitized_text[end:]
                        
                        new_end = start + len(replacement)
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
        
        # 根据不同的脱敏策略执行还原
        if self.config['enable_pseudonymization']:
            # 处理假名化的还原
            for pseudonym, original_text in self.pseudonym_map.items():
                # 只处理假名到原始文本的映射
                if not pseudonym.startswith('<') and pseudonym != original_text:
                    restored_text = restored_text.replace(pseudonym, original_text)
        elif self.config['enable_anonimization']:
            # 处理匿名化的还原
            for anonymized_label in re.findall(r'\[REDACTED_\w+\]', restored_text):
                # 在匿名化映射中查找对应的原始文本
                for key, value in self.anonymization_map.items():
                    if key != value and isinstance(value, str) and anonymized_label in value:
                        restored_text = restored_text.replace(anonymized_label, key)
        else:
            # 处理标准占位符的还原
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
        **kwargs: 配置参数，包括enable_entity_placeholder, enable_pseudonymization, enable_anonimization, enable_generalization等
        
        返回:
        self: 当前工作流实例，支持链式调用
        """
        self.endside_model.configure(**kwargs)
        return self
    
    def configure_desensitization_strategy(self, 
                                enable_entity_placeholder=None, 
                                enable_pseudonymization=None, 
                                enable_anonimization=None, 
                                enable_generalization=None):
        """
        配置端侧模型的脱敏策略选项
        
        参数:
        enable_entity_placeholder: 是否使用标准占位符（<name>_0格式）
        enable_pseudonymization: 是否使用假名化策略
        enable_anonimization: 是否使用匿名化策略
        enable_generalization: 是否使用数据泛化策略
        
        返回:
        self: 当前工作流实例，支持链式调用
        """
        config_kwargs = {}
        if enable_entity_placeholder is not None:
            config_kwargs['enable_entity_placeholder'] = enable_entity_placeholder
        if enable_pseudonymization is not None:
            config_kwargs['enable_pseudonymization'] = enable_pseudonymization
        if enable_anonimization is not None:
            config_kwargs['enable_anonimization'] = enable_anonimization
        if enable_generalization is not None:
            config_kwargs['enable_generalization'] = enable_generalization
        
        self.endside_model.configure(**config_kwargs)
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
    
    # 存储会话映射关系，用于独立的还原操作
    session_mappings = {}
    
    while True:
        try:
            # 显示菜单
            print("请选择操作：")
            print("1. 使用预设场景进行演示")
            print("2. 输入自定义文本进行演示")
            print("3. 第一步：输入文本进行脱敏（生成可复制的脱敏文本）")
            print("4. 第二步：输入大模型回答进行还原（使用之前的脱敏映射）")
            print("5. 退出程序")
            
            choice = input("请选择 (1-5): ").strip()
            
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
                    
                    # 运行工作流（类型收敛）
                    inp = str(selected_scenario.get('input', ''))
                    st = selected_scenario.get('sensitive_types', None)
                    st_norm: Optional[List[str]] = st if isinstance(st, list) else None
                    has_workflow.run(inp, st_norm)
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
                
                # 运行工作流（类型收敛）
                st_norm: Optional[List[str]] = sensitive_types if isinstance(sensitive_types, list) else None
                has_workflow.run(custom_text, st_norm)
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
                has_workflow = CompleteHaSWorkflow()
                
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
                restore_model = EnhancedNamedEntityEndsideModel()
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
            # 仅在1、2选项中询问是否继续
            if choice in ['1', '2']:
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
            
            # 运行工作流（类型收敛）
            scen_inp = str(scenario.get('input', ''))
            scen_st = scenario.get('sensitive_types', None)
            scen_st_norm: Optional[List[str]] = scen_st if isinstance(scen_st, list) else None
            result = has_workflow.run(
                scen_inp,
                scen_st_norm
            )
            
            # 记录总耗时（类型安全）
            timing_dict = cast(Dict[str, Any], result.get('timing', {}))
            total_val = timing_dict.get('total', 0.0)
            total_times.append(float(total_val))
        
        # 计算平均耗时
        avg_time = sum(total_times) / len(total_times)
        print(f"\n配置 '{config['name']}' 的平均处理时间: {avg_time:.3f}秒")

# 重构后入口瘦封装，保持向后兼容
if __name__ == "__main__":
    from app import user_interaction_demo
    user_interaction_demo()