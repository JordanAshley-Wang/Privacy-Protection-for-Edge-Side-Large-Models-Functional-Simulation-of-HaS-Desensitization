# 腾讯实验室 HaS (Hide and Seek) 隐私保护技术 - 增强版模拟

本项目模拟实现了腾讯实验室提出的HaS（Hide and Seek）大模型隐私保护技术，并进行了全面增强。该技术通过对用户输入的敏感信息进行脱敏处理，并能在大模型输出后进行精准还原，从而在本地终端侧防范隐私数据泄露。

## 项目介绍

腾讯安全玄武实验室披露的HaS技术是业内首个支持信息还原的自由文本脱敏技术，本增强版实现保留了原始技术的核心优势，并添加了更多高级功能：

- **隐私保护**：对用户上传给大模型的prompt（提示词）进行隐私信息脱敏
- **信息还原**：在大模型返回计算结果后进行精准恢复
- **轻量级**：脱敏与还原算法经过优化，可在手机、PC等终端上高效部署
- **适用广泛**：适用于机器翻译、文本摘要、文本润色、阅读理解、文本分类等多种NLP任务场景

## 增强版特性

本增强版实现相比原始版本，增加了以下功能和改进：

### 1. 扩展的敏感信息识别范围
- ✅ 手机号识别与脱敏
- ✅ 身份证号识别与脱敏
- ✅ 邮箱地址识别与脱敏
- ✅ 中文姓名识别与脱敏
- ✅ 银行卡号识别与脱敏
- ✅ 信用卡号识别与脱敏
- ✅ 地址信息识别与脱敏
- ✅ 公司名称识别与脱敏
- ✅ 日期信息识别与脱敏
- ✅ 支持自定义敏感信息类型
- ✅ 年龄、邮政编码、IP地址和账号等敏感信息类型

### 2. 增强的脱敏安全性
- ✅ 支持UUID模式的脱敏，生成高安全性的唯一标识符
- ✅ 基于哈希和随机盐值的令牌生成机制
- ✅ 保留格式或完全替换两种脱敏策略
- ✅ 多种脱敏策略：标准占位符、假名化、匿名化和数据泛化

### 3. 健壮的还原功能
- ✅ 精确的文本还原机制
- ✅ 支持模糊匹配还原，处理大模型输出中的拼写错误
- ✅ 基于相似度的智能还原策略
- ✅ 优化的还原结果验证机制

### 4. 灵活的配置选项
- ✅ 可选择性地对特定类型的敏感信息进行脱敏
- ✅ 支持包含/排除特定类型的敏感信息
- ✅ 可自定义敏感信息的正则表达式和处理函数
- ✅ 丰富的配置参数，可根据实际需求调整性能和安全级别

### 5. 实用工具功能
- ✅ 批量处理多文本
- ✅ 保存和加载脱敏映射关系
- ✅ 脱敏历史记录管理
- ✅ 性能监控功能，实时显示各阶段处理时间

### 6. 完整工作流集成
- ✅ 端侧小模型与大模型交互流程标准化、流程化
- ✅ 支持自动工作流模式和三步交互隐私保护流程
- ✅ 用户友好的交互界面，提供预设场景和自定义文本处理两种模式

## 主要组件

### 1. EnhancedNamedEntityEndsideModel

增强版端侧小模型封装类，负责本地敏感信息的识别、脱敏和还原。主要特性包括：

- 支持多种敏感信息类型识别（姓名、公司、职位、部门、手机号、身份证、邮箱、银行卡、金额、业绩指标、年龄、地址、邮政编码、IP地址、账号）
- 提供多种脱敏策略：标准占位符、假名化、匿名化和数据泛化
- 实现智能还原策略，可处理大模型输出的变化
- 支持自定义敏感信息模式
- 提供会话管理功能

### 2. EnhancedMockLargeModel

增强版模拟大模型，模拟真实大模型的文本处理效果。主要特性包括：

- 实现文本改写和语法调整
- 模拟大模型的创造性输出
- 根据输入内容生成相关额外信息
- 支持不同回答模板

### 3. CompleteHaSWorkflow

完整的HaS隐私保护工作流，集成端侧小模型和模拟大模型。主要特性包括：

- 实现完整的脱敏-处理-还原流程
- 支持灵活的配置选项
- 提供详细的执行结果和性能指标
- 记录工作流执行历史

### 4. EntropyEnhancedSensitiveModel

基于信息熵的增强版敏感词检测模型，实现了多维度熵计算和敏感信息检测。主要特性包括：

- 支持字符级熵计算，识别不规则文本模式
- 实现N-gram熵计算，分析文本上下文关系
- 提供自适应阈值调整机制
- 结合正则匹配和熵分析的混合检测策略

### 5. HaSPrivacySystem

系统级封装，提供统一的接口和用户交互体验。主要特性包括：

- 集成所有核心功能模块
- 提供命令行交互式界面
- 支持批处理模式
- 实现配置管理和会话持久化

## 项目结构

本项目包含以下核心文件：

```
has_hide_seek/
├── .gitignore                  # Git忽略文件配置
├── README.md                   # 项目介绍文档
├── README_ENHANCED.md          # 增强版工作流详细使用指南
├── has_workflow_improved.py    # 核心实现文件，包含增强版HaS隐私保护技术
├── has_entropy_sensitive_retrieval.py  # 基于信息熵的敏感词检测模块
├── main.py                     # 系统主程序入口
├── requirements.txt            # 项目依赖文件
├── test_entropy_system.py      # 增强版系统测试文件
└── test_case_complex.txt       # 复杂测试用例，包含多种敏感信息
```

## 核心功能

### 1. 端侧小模型封装

`EnhancedNamedEntityEndsideModel`类提供了完整的端侧小模型封装，使用`encode_sensitive`和`decode_sensitive`方法负责敏感信息的本地处理：

- 支持识别姓名、公司、职位、部门、金额、业绩、手机号、身份证号、邮箱等多种敏感信息
- 提供语义化占位符格式（如`<name>_0`）
- 实现智能还原策略，处理大模型输出变化
- 支持自定义敏感信息类型和处理规则

### 2. 基于信息熵的敏感词检测

`EntropyEnhancedSensitiveModel`类实现了多维度熵计算和敏感信息检测：

- 字符熵计算：分析文本中字符的分布规律，识别异常模式
- N-gram熵计算：分析相邻字符的组合模式，提高检测准确性
- 混合检测策略：结合正则匹配和熵分析，减少误报和漏报
- 自适应阈值：根据文本特点动态调整检测阈值

### 3. 完整工作流管理

`EntropyEnhancedHaSWorkflow`类实现了完整的脱敏-处理-还原工作流：

- 工作流配置：支持自定义各环节的处理参数
- 脱敏流程：集成多种脱敏策略，确保数据安全
- 还原流程：智能还原敏感信息，处理文本变化
- 性能监控：记录各环节处理时间，便于优化

### 4. 系统级集成

`HaSPrivacySystem`类提供了统一的系统接口：

- 系统初始化：加载配置和模型
- 文本处理：提供单文本和批量处理能力
- 文件处理：支持从文件读取和写入结果
- 交互式界面：提供命令行交互体验

## 安装与依赖

本项目基于Python开发，主要依赖项包括：

- Python 3.7+
- re (标准库)
- time (标准库)
- random (标准库)
- math (标准库)
- collections (标准库)
- uuid (标准库)

可选依赖（用于扩展功能）：
- numpy (用于高级数学计算)
- pandas (用于数据处理)
- Levenshtein (用于增强模糊匹配能力)

安装步骤：

1. 确保已安装Python 3.7或更高版本
2. 克隆或下载项目代码
3. 安装必要的依赖（如果需要扩展功能）：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

运行主程序，启动交互式界面：

```bash
python main.py
```

或者运行原始增强版工作流：

```bash
python has_workflow_improved.py
```

运行后，您将看到交互式菜单，可以选择以下操作：

1. **使用预设场景进行演示** - 选择内置的4个预设场景（个人信息、金融信息、企业信息、网络安全信息）进行快速演示
2. **输入自定义文本进行演示** - 输入您自己的包含敏感信息的文本进行演示
3. **第一步：输入文本进行脱敏** - 生成可复制的脱敏文本，供复制到互联网大模型使用
4. **第二步：输入大模型回答进行还原** - 使用之前保存的脱敏映射关系还原大模型回答中的敏感信息
5. **退出程序** - 结束当前会话

### 命令行参数

主程序支持以下命令行参数：

```bash
# 处理单个文本
python main.py --text "你的文本内容"

# 处理文件
python main.py --file input.txt --output output.txt

# 使用特定配置
python main.py --config config.json

# 批处理模式
python main.py --batch batch_input.txt
```

### 三步交互隐私保护流程

为了在与真实互联网大模型交互时确保隐私安全，我们实现了完整的三步交互流程：

1. **第一步：输入文本进行脱敏**（选择菜单选项3）
   - 用户输入包含敏感信息的文本
   - 系统识别并脱敏处理，生成可复制的脱敏文本
   - 系统保存脱敏映射关系，生成唯一会话ID
   - 系统提示用户复制脱敏文本

2. **中间步骤（外部操作）**
   - 用户手动将脱敏文本复制到互联网大模型（如ChatGPT、文心一言等）
   - 大模型处理脱敏文本并生成回答
   - 用户获取大模型的回答文本
   
3. **第二步：输入大模型回答进行还原**（选择菜单选项4）
   - 用户输入之前生成的会话ID
   - 用户输入大模型的回答文本
   - 系统验证会话ID的有效性
   - 系统使用之前保存的脱敏映射关系还原敏感信息
   - 应用模糊匹配算法处理文本变化
   - 输出包含还原后敏感信息的完整文本

这种三步交互模式确保了敏感信息不会离开用户的本地设备，同时还能享受大模型的强大能力。

### 预设场景

脚本内置了4个预设场景，覆盖不同类型的敏感信息：

1. **个人信息处理**：包含姓名、手机号、身份证号等个人敏感信息
2. **金融信息处理**：包含银行卡号、交易金额等金融敏感信息
3. **企业信息处理**：包含公司名称、统一社会信用代码等企业敏感信息
4. **网络安全信息处理**：包含IP地址、密码等网络安全敏感信息

### 脱敏策略选择

在处理过程中，系统会询问您是否需要指定脱敏策略：

1. 标准占位符（<name>_0）
2. 假名化（生成逼真的替代信息）
3. 匿名化（[REDACTED_NAME]）
4. 数据泛化（降低数据粒度，如年龄转年龄段）

### UUID安全模式

系统支持UUID模式进行脱敏，提供更高的安全性：

```
是否使用UUID模式进行脱敏？(y/n，默认n)：y
```

UUID模式通过生成随机唯一标识符替换敏感信息，而不是简单的格式保留替换。

## 工作流程详解

增强版工作流提供了两种交互模式，满足不同场景需求：

### 自动工作流模式（选项1和2）

自动工作流模式在一个会话内完成完整的隐私保护流程，适用于演示和集成测试：

1. **脱敏处理（Hide阶段）**
   - 端侧小模型识别文本中的敏感信息
   - 根据配置的脱敏策略替换敏感信息
   - 建立脱敏前后的映射关系
   - 输出脱敏后的文本

2. **大模型处理**
   - 脱敏后的文本被传输至模拟大模型
   - 模拟大模型生成回答（包含改写、语法调整等变化）

3. **还原处理（Seek阶段）**
   - 端侧小模型接收模拟大模型的返回结果
   - 根据映射关系还原敏感信息
   - 应用模糊匹配算法处理文本变化
   - 输出最终还原结果

### 基于信息熵的工作流

增强版工作流还集成了基于信息熵的敏感词检测功能：

1. **文本预处理**：清理和规范化输入文本
2. **熵特征提取**：计算文本的字符熵和N-gram熵
3. **敏感信息识别**：结合正则匹配和熵分析识别敏感信息
4. **脱敏处理**：根据检测结果应用相应的脱敏策略
5. **大模型交互**：将脱敏后的文本发送给大模型
6. **还原处理**：使用映射关系还原大模型输出中的敏感信息

## 配置选项详解

增强版工作流提供了多种配置选项，可以根据实际需求进行调整：

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| use_uuid | 布尔值 | False | 是否使用UUID模式进行脱敏 |
| preserve_format | 布尔值 | True | 是否保留原始敏感信息的格式 |
| enable_entity_placeholder | 布尔值 | True | 是否使用标准占位符（<name>_0格式）进行脱敏 |
| enable_pseudonymization | 布尔值 | False | 是否使用假名化策略（生成逼真的替代信息） |
| enable_anonimization | 布尔值 | False | 是否使用匿名化策略（[REDACTED_NAME]格式） |
| enable_generalization | 布尔值 | False | 是否使用数据泛化策略（降低数据粒度） |
| enable_fuzzy_matching | 布尔值 | True | 是否启用模糊匹配还原功能 |
| min_confidence | 浮点数 | 0.7 | 模糊匹配的最小置信度 |
| max_distance | 整数 | 3 | 模糊匹配允许的最大字符差异 |
| custom_patterns | 字典 | None | 自定义敏感信息模式和处理函数 |
| char_entropy_threshold | 浮点数 | 3.0 | 字符熵检测阈值 |
| ngram_entropy_threshold | 浮点数 | 4.0 | N-gram熵检测阈值 |
| use_combined_detection | 布尔值 | True | 是否使用组合检测策略 |

配置示例：

```python
# 配置端侧小模型
endside_model = EnhancedNamedEntityEndsideModel()
endside_model.configure(
    use_uuid=False,         # 是否使用UUID格式的占位符
    preserve_format=True,   # 是否保留原始格式
    enable_fuzzy_matching=True  # 是否启用模糊匹配还原
)

# 配置基于信息熵的敏感词检测模型
entropy_model = EntropyEnhancedSensitiveModel()
entropy_model.configure(
    char_entropy_threshold=3.0,     # 字符熵阈值
    ngram_entropy_threshold=4.0,    # N-gram熵阈值
    ngram_size=2,                   # N-gram大小
    use_combined_detection=True     # 使用组合检测策略
)
```

## 代码集成示例

### 基本集成

如果您想在自己的项目中集成HaS隐私保护技术，可以参考以下示例：

```python
from has_workflow_improved import EnhancedNamedEntityEndsideModel

# 创建端侧小模型实例
endside_model = EnhancedNamedEntityEndsideModel()

# 输入文本
user_input = "我叫王通，来自中国移动业务部总经理，现在将开始我的述职报告"

# 选择需要脱敏的敏感信息类型
sensitive_types = ['name', 'company', 'position']

# 执行脱敏处理
desensitized_text, mapping = endside_model.desensitize(user_input, sensitive_types)

# 模拟大模型处理
def mock_llm(input_text):
    # 这里是您的大模型调用代码
    return f"处理结果：{input_text}\n这是生成的内容。"

llm_result = mock_llm(desensitized_text)

# 执行还原处理
restored_text = endside_model.restore(llm_result, mapping)

print("原始文本:", user_input)
print("脱敏后文本:", desensitized_text)
print("大模型输出:", llm_result)
print("还原后文本:", restored_text)
```

### 使用基于信息熵的检测

```python
from has_entropy_sensitive_retrieval import EntropyEnhancedSensitiveModel

# 创建基于信息熵的敏感词检测模型
entropy_model = EntropyEnhancedSensitiveModel()

# 配置模型参数
entropy_model.configure(
    char_entropy_threshold=3.0,
    ngram_entropy_threshold=4.0,
    ngram_size=2
)

# 检测敏感信息
text = "银行卡号：6222 1234 5678 9012，密码：abc123"
sensitive_info = entropy_model.detect_sensitive_info(text)
print("检测到的敏感信息:", sensitive_info)

# 执行脱敏处理
desensitized_text, mapping = entropy_model.desensitize(text)
print("脱敏后文本:", desensitized_text)
```

### 使用完整工作流

```python
from has_entropy_sensitive_retrieval import EntropyEnhancedHaSWorkflow

# 创建完整工作流实例
workflow = EntropyEnhancedHaSWorkflow()

# 配置工作流
workflow_config = {
    'use_uuid': False,
    'enable_fuzzy_matching': True,
    'char_entropy_threshold': 3.0,
    'ngram_entropy_threshold': 4.0
}
workflow.configure(**workflow_config)

# 执行完整工作流
text = "张敏的手机号是13812345678，身份证号为110101199001011234"
result = workflow.run_full_workflow(text)

print("原始文本:", result['original'])
print("脱敏后文本:", result['desensitized'])
print("大模型输出:", result['llm_output'])
print("还原后文本:", result['restored'])
print("处理时间:", result['timing'])
```

### 自定义敏感信息类型

您可以通过继承`EnhancedNamedEntityEndsideModel`类来实现自定义敏感信息处理逻辑：

```python
class CustomEndsideModel(EnhancedNamedEntityEndsideModel):
    def __init__(self):
        super().__init__()
        # 添加自定义敏感信息类型
        self.custom_patterns = {
            "ip_address": r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",
            "password": r"password\s*[:=]\s*['"]([^'"]+)['"]"
        }
    
    def encode_sensitive(self, text, sensitive_types=None):
        # 如果没有指定敏感类型，使用默认类型加上自定义类型
        if sensitive_types is None:
            sensitive_types = self.default_sensitive_types + list(self.custom_patterns.keys())
        
        # 添加自定义模式到正则表达式映射
        for type_name, pattern in self.custom_patterns.items():
            if type_name in sensitive_types:
                self.sensitive_patterns[type_name] = pattern
        
        # 调用父类方法进行脱敏
        return super().encode_sensitive(text, sensitive_types)

# 使用自定义模型
custom_model = CustomEndsideModel()
text = "服务器IP地址是192.168.1.1，数据库密码是'admin123'"
masked_text, mapping = custom_model.encode_sensitive(text)
print("脱敏后：", masked_text)
```

### 批量处理

您可以使用`HaSPrivacySystem`类的批量处理功能：

```python
from main import HaSPrivacySystem

# 创建系统实例
system = HaSPrivacySystem()

# 批量处理文本
texts = [
    "王小明的手机号是13812345678",
    "李华的邮箱是lihua@example.com",
    "张伟的身份证号是110101199001011234"
]

results = system.batch_process(texts)

for i, result in enumerate(results):
    print(f"\n文本 {i+1}:")
    print(f"脱敏后: {result['desensitized']}")
    print(f"大模型输出: {result['llm_output']}")
    print(f"还原后: {result['restored']}")
```

## 技术细节

### 脱敏策略（Hide）

增强版实现支持多种脱敏策略，可以根据需求灵活选择：

1. **手机号**：保留首尾各4位，中间用*号替换，或使用UUID替换
2. **身份证号**：保留前6位和后4位，中间用*号替换，或使用UUID替换
3. **邮箱**：保留域名部分，用户名用*号替换，或使用UUID替换
4. **中文姓名**：用常见姓氏和名字的组合进行替换，保持长度一致，或使用UUID替换
5. **银行卡号**：保留首尾4位，中间用*号替换，保持格式
6. **信用卡号**：保留首尾4位，中间用*号替换，保持格式
7. **地址信息**：保留省市，替换具体街道和门牌号，或使用UUID替换
8. **公司名称**：生成随机公司名称，保留公司类型后缀，或使用UUID替换
9. **日期信息**：生成随机但合理的日期，保持原始格式，或使用UUID替换
10. **自定义类型**：支持用户定义的敏感信息类型和处理函数

脱敏过程采用优先级处理机制，避免不同类型敏感信息之间的识别冲突。

### 还原策略（Seek）

还原策略经过增强，包含以下特点：

1. 维护脱敏前后的双向映射关系
2. 在大模型返回结果后，根据映射关系进行精准还原
3. 按照字符长度从长到短进行替换，避免部分匹配导致的错误
4. 支持正则表达式精确匹配，提高还原准确率
5. 提供模糊匹配还原功能，可处理大模型输出中的拼写错误和格式变化

模糊匹配还原基于字符串相似度计算，进行了特别优化：
- 降低模糊匹配置信度阈值至0.5，提高还原成功率
- 增加max_distance参数允许更多字符差异
- 关闭单词边界匹配，适应不同上下文
- 新增文本格式预处理步骤（去除多余空白字符）
- 增加二次模糊匹配尝试，提高还原覆盖率

### 基于信息熵的检测技术

增强版系统集成了基于信息熵的敏感词检测技术：

1. **字符熵计算**：分析文本中字符的分布情况，异常高或低的熵值可能表示敏感信息
2. **N-gram熵计算**：分析相邻字符的组合模式，识别特定格式的敏感信息
3. **混合检测策略**：结合正则表达式匹配和熵分析，提高检测准确性
4. **自适应阈值**：根据文本特点动态调整熵检测阈值

### 还原结果验证机制

实现了改进的还原结果验证机制：

1. **关键词提取**：从用户输入中提取关键词（如银行卡、身份证、IP、密码等）
2. **特定信息识别**：通过规则识别特定类型信息（如含"TX"识别为交易单号）
3. **关键词还原统计**：统计还原文本中包含的关键词数量
4. **综合评估**：基于关键词匹配度和占位符检查评估还原结果

这种验证机制能够更准确地判断还原是否成功，特别是在大模型输出发生变化的情况下。

### UUID模式与安全性

UUID模式使用以下技术确保脱敏安全性：

1. 采用UUID v4生成随机且唯一的标识符
2. 结合哈希函数和随机盐值增强安全性
3. 所有映射关系仅保存在本地内存中，不会上传到任何服务器
4. 支持将映射关系保存到本地文件，便于后续还原

### 性能优化

增强版实现包含多项性能优化：

1. 预编译正则表达式，提高敏感信息识别速度
2. 优化映射关系数据结构，加速查找和替换操作
3. 支持批量处理，提高多文本处理效率
4. 提供灵活的配置选项，可根据实际需求调整性能和安全级别
5. 熵计算算法优化，减少计算复杂度

## 性能指标

工作流执行过程中，系统会实时显示各阶段的处理时间：

- 脱敏时间：端侧小模型识别和处理敏感信息的时间
- 熵计算时间：基于信息熵的敏感词检测时间
- 大模型处理时间：模拟大模型处理文本的时间
- 还原时间：端侧小模型还原敏感信息的时间
- 总耗时：整个工作流的总执行时间

## 输入示例

以下是一些常用的输入示例，展示不同类型敏感信息的处理效果：

### 个人信息示例
```
王小明的手机号是13812345678，身份证号为110101199003079876，
他的邮箱是xiaoming@example.com，银行卡号为6222 1234 5678 9012。
他住在北京市朝阳区建国路88号，出生日期是1990/03/07。
```

### 公司信息示例
```
北京科技有限公司的联系电话是13987654321，
法定代表人是李华，公司地址在上海市浦东新区张江高科技园区博云路2号。
公司邮箱是contact@beijingtech.com。
```

### 交易信息示例
```
交易单号：TX202305160001，
付款人：张伟，手机号：13712345678，
收款人：刘芳，卡号：6226 8888 8888 8888，
交易金额：10000.00元，交易日期：2023-05-16。
```

### 网络安全信息示例
```
服务器IP地址是192.168.1.100，管理员账户为admin，密码为Admin12345，
数据库连接字符串为jdbc:mysql://localhost:3306/userdb?user=root&password=Root12345。
```

## 应用场景

- **大模型推理时的隐私保护**：在将用户输入发送给大模型前进行脱敏，防止敏感信息泄露
- **边缘设备上的隐私计算**：在资源受限的边缘设备上实现高效的隐私保护
- **数据处理和分析**：在数据分析过程中保护用户隐私
- **API服务中的隐私防护**：在API服务中集成，为用户提供隐私保护
- **金融领域数据处理**：处理包含银行卡、交易记录等敏感金融信息
- **医疗数据隐私保护**：保护患者的个人和医疗记录信息
- **企业内部文档处理**：保护企业内部敏感信息不被泄露

## 注意事项

1. 本实现是对腾讯实验室HaS技术的模拟，可能与实际技术存在差异
2. 对于复杂的敏感信息识别，可能需要根据具体场景调整正则表达式
3. 在生产环境中使用时，建议进一步评估安全性和性能
4. 模糊匹配还原功能是简化版实现，对于复杂场景可能需要更高级的算法
5. 加载HaS-820m模型需要网络连接，如果网络受限，脚本会自动使用模拟模式
6. 基于信息熵的检测可能会有一定的误报率，建议根据实际场景调整阈值

## 测试

项目包含完整的测试文件，您可以通过以下命令运行测试：

```bash
python test_entropy_system.py
```

测试文件包含以下测试内容：

1. **单元测试**：测试各个功能模块的基本功能
2. **集成测试**：测试完整工作流的集成效果
3. **性能测试**：测试系统在不同场景下的性能表现
4. **批量测试**：测试系统处理大量文本的能力

## 参考资料

- 腾讯实验室 HaS 技术：https://xlab.tencent.com/cn/2023/12/05/hide_and_seek/
- HaS-820m 开源模型：https://huggingface.co/SecurityXuanwuLab/HaS-820m

## License

[MIT License](https://opensource.org/licenses/MIT)
