<<<<<<< HEAD
# 腾讯实验室 HaS (Hide and Seek) 隐私保护技术 - 增强版

## 项目概述

本项目是腾讯实验室HaS（Hide and Seek）大模型隐私保护技术的增强实现版本，通过对用户输入的敏感信息进行脱敏处理，并能在大模型输出后进行精准还原，从而在本地终端侧防范隐私数据泄露。本版本特别增强了基于信息熵的敏感词检索能力，适合在内网低配置环境中运行。

系统支持用户两次输入输出流程：
1. 用户输入原始文本 → 系统输出脱敏文本
2. 用户使用脱敏文本与大模型交互 → 系统将大模型返回的文本还原为包含原始敏感信息的文本

## 核心功能

1. **隐私保护**：对用户上传给大模型的prompt（提示词）进行隐私信息脱敏
2. **信息还原**：在大模型返回计算结果后进行精准恢复
3. **轻量级**：脱敏与还原算法经过优化，可在低配置内网环境高效部署
4. **适用广泛**：适用于机器翻译、文本摘要、文本润色、阅读理解、文本分类等多种NLP任务场景

## 技术特点

### 1. 增强版信息熵算法
- **多维度熵计算**：结合字符熵、N-gram熵和位置熵进行综合评分
- **自适应阈值**：通过高低熵阈值区分不同类型的敏感信息
- **轻量级实现**：低依赖、高效率，适合在低配置环境运行

### 2. 多策略脱敏机制
- **标准占位符**：将敏感信息替换为 `<type>_n` 格式的占位符
- **假名化**：生成逼真的替代信息（如随机姓名、随机手机号等）
- **匿名化**：使用 `[REDACTED_TYPE]` 格式的匿名化标记
- **数据泛化**：降低数据粒度（如年龄转年龄段、金额四舍五入等）

### 3. 高效敏感信息检测
- **结合正则与信息熵**：提高敏感信息识别的准确性和召回率
- **重叠候选去重**：智能处理重叠的敏感信息，优先选择更合适的匹配
- **支持15种敏感信息类型**：姓名、公司、职位、手机号、身份证、邮箱等

## 支持的敏感信息类型

1. **name** - 姓名（基于常见姓氏库和字符熵检测）
2. **company** - 公司名称（基于公司后缀和文本结构）
3. **position** - 职位信息
4. **department** - 部门信息
5. **phone** - 手机号码（11位数字，支持常见号段）
6. **id** - 身份证号码（18位，支持校验规则）
7. **email** - 电子邮箱地址
8. **bank_card** - 银行卡号（16-19位数字）
9. **amount** - 金额信息（支持带货币符号）
10. **performance** - 业绩指标
11. **age** - 年龄信息
12. **address** - 地址信息
13. **zipcode** - 邮政编码（6位数字）
14. **ip** - IP地址（IPv4格式）
15. **account** - 账号信息（基于字符熵和长度检测）

## 主要组件

### 1. EntropyEnhancedSensitiveModel

增强版信息熵敏感信息检测与处理模型，负责本地敏感信息的识别、脱敏和还原。主要特性包括：

- 支持多种敏感信息类型识别
- 提供多种脱敏策略：标准占位符、假名化、匿名化和数据泛化
- 实现智能还原策略，可处理大模型输出的变化
- 支持自定义敏感信息模式
- 提供会话管理功能

### 2. EntropyEnhancedHaSWorkflow

集成增强版信息熵敏感词检测的完整工作流，集成端侧小模型和模拟大模型。主要特性包括：

- 实现完整的脱敏-处理-还原流程
- 支持灵活的配置选项
- 提供详细的执行结果和性能指标
- 记录工作流执行历史

### 3. EnhancedMockLargeModel

增强版模拟大模型，模拟真实大模型的文本处理效果。主要特性包括：

- 实现文本改写和语法调整
- 模拟大模型的创造性输出
- 根据输入内容生成相关额外信息
- 支持不同回答模板

## 系统配置

系统支持多种配置选项，可根据实际需求进行调整：

```python
{
    # 信息熵检测配置
    'enable_entropy_detection': True,     # 是否启用信息熵检测
    'entropy_threshold': 1.2,             # 低熵阈值
    'high_entropy_threshold': 3.5,        # 高熵阈值
    'max_token_len': 64,                  # 最大token长度
    'min_token_len': 2,                   # 最小token长度
    
    # 脱敏策略配置
    'enable_entity_placeholder': True,    # 标准占位符
    'enable_pseudonymization': True,      # 假名化
    'enable_anonimization': True,         # 匿名化
    'enable_generalization': True,        # 数据泛化
    
    # 性能优化配置
    'enable_fuzzy_matching': True,        # 模糊匹配
    'preserve_format': True,              # 保留原始格式
    'batch_process_size': 1024,           # 批处理大小
    
    # 中文处理配置
    'enable_ngram_entropy': True,         # ngram熵计算
    'ngram_size': 2,                      # ngram大小
    'enable_radical_analysis': False,     # 激进分析
    'enable_position_entropy': True,      # 位置熵计算
}
```

## 安装与依赖

本项目基于Python开发，主要依赖项包括：

- Python 3.6+ 
- 无特殊依赖，使用Python标准库即可运行

安装步骤：

1. 确保已安装Python 3.6或更高版本
2. 克隆或下载项目代码
3. 无需安装额外依赖

## 使用方法

### 基本使用

运行系统主入口文件：

```bash
python main.py
```

也可以直接运行核心实现文件：

```bash
python has_entropy_sensitive_retrieval.py
```

运行后，您将看到交互式菜单，可以选择以下操作：

1. **使用预设场景进行演示** - 选择内置的4个预设场景（个人信息、金融信息、企业信息、网络安全信息）进行快速演示
2. **输入自定义文本进行演示** - 输入您自己的包含敏感信息的文本进行演示
3. **第一步：输入文本进行脱敏** - 生成可复制的脱敏文本，供复制到互联网大模型使用
4. **第二步：输入大模型回答进行还原** - 使用之前保存的脱敏映射关系还原大模型回答中的敏感信息
5. **退出程序** - 结束当前会话

在选择演示模式后，系统会询问您是否需要指定脱敏策略：

1. 标准占位符（<name>_0）
2. 假名化（生成逼真的替代信息）
3. 匿名化（[REDACTED_NAME]）
4. 数据泛化（降低数据粒度，如年龄转年龄段）

### 实际使用场景

#### 场景一：在内网电脑上保护敏感信息
1. 用户在内网电脑上运行程序，选择"3. 第一步：输入文本进行脱敏"
2. 输入包含敏感信息的文本，系统生成脱敏文本并显示会话ID
3. 用户将脱敏文本复制到外网环境，使用大模型进行处理
4. 大模型返回处理后的文本
5. 用户回到内网电脑，运行程序，选择"4. 第二步：输入大模型回答进行还原"
6. 输入会话ID和大模型返回的文本，系统还原敏感信息

#### 场景二：批量处理敏感文档
可以修改 `batch_test()` 函数，批量处理多个文档并进行脱敏还原操作。

## 项目结构

本项目包含以下主要文件：

```
has_hide_seek/
├── .gitignore                         # Git忽略文件配置
├── README.md                          # 项目介绍文档
├── has_workflow_improved.py           # 原始增强版实现文件
├── has_entropy_sensitive_retrieval.py # 基于信息熵的增强版实现
├── main.py                            # 系统主入口文件
├── requirements.txt                   # 项目依赖配置
├── test_case_complex.txt              # 测试用例文件
└── test_entropy_system.py             # 系统测试文件
```

## 性能优化建议

1. **对于低配置环境**：
   - 关闭 `enable_radical_analysis` 选项
   - 设置较小的 `max_token_len` 值
   - 考虑禁用 `enable_ngram_entropy` 和 `enable_position_entropy` 以提高速度

2. **对于高精度需求环境**：
   - 启用所有信息熵检测选项
   - 调整 `entropy_threshold` 和 `high_entropy_threshold` 值以获得最佳效果
   - 可以扩展常见姓氏库和公司后缀库

## 扩展开发

本系统支持进一步扩展，您可以：

1. 添加新的敏感信息类型和检测规则
2. 改进信息熵计算算法以提高检测准确性
3. 扩展假名化策略，生成更逼真的替代信息
4. 集成实际的大模型API调用功能
5. 开发图形用户界面(GUI)以提升用户体验

## 安全注意事项

1. **会话管理**：当前系统使用内存中的会话字典保存映射关系，请确保在敏感环境中适当保护会话ID
2. **数据保护**：在实际应用中，建议添加数据加密功能，保护存储的敏感信息映射关系
3. **访问控制**：考虑添加用户认证和访问控制机制，限制对系统的访问
4. **定期更新**：定期更新敏感信息检测规则和算法，以适应不断变化的安全需求

## 免责声明

本系统仅作为敏感信息保护的辅助工具，不能保证100%识别和保护所有敏感信息。在实际应用中，请结合其他安全措施，并根据您的具体需求进行适当的调整和测试。

## 参考资料

1. 香农熵理论：https://zhuanlan.zhihu.com/p/48461603
2. 信息熵在文本分析中的应用：https://blog.csdn.net/universsky2015/article/details/137316348
3. 数据脱敏技术综述：https://arxiv.org/pdf/2309.03057
4. 隐私保护与数据安全：https://xz.aliyun.com/news/16523
5. 敏感信息检测技术：https://xz.aliyun.com/news/18876

# 执行还原处理
restored_text = endside_model.restore(llm_result, mapping)

print("原始文本:", user_input)
print("脱敏后文本:", desensitized_text)
print("大模型输出:", llm_result)
print("还原后文本:", restored_text)
```

### 指定敏感信息类型

您可以根据需要选择要脱敏的敏感信息类型：

```python
# 只对姓名和公司进行脱敏
sensitive_types = ["name", "company"]
desensitized_text, mapping = endside_model.desensitize(user_input, sensitive_types)

# 也可以使用逗号分隔的字符串
sensitive_types = "name,company,position"
desensitized_text, mapping = endside_model.desensitize(user_input, sensitive_types)
```

### 配置选项

端侧小模型支持多种配置选项：

```python
# 配置端侧小模型
endside_model = EnhancedNamedEntityEndsideModel()
endside_model.configure(
    use_uuid=False,         # 是否使用UUID格式的占位符
    preserve_format=True,   # 是否保留原始格式
    enable_fuzzy_matching=True  # 是否启用模糊匹配还原
)
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
            "password": r"password\s*[:=]\s*['\"]([^'"]+)['\"]"
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

### 处理大模型输出中的错误

`EnhancedNamedEntityEndsideModel`类内置了模糊匹配还原功能，可以处理大模型输出中可能出现的小错误：

```python
# 创建模型并启用模糊匹配
model = EnhancedNamedEntityEndsideModel(enable_fuzzy_matching=True)

# 示例文本
text = "张敏的手机号是13812345678，身份证号为110101199001011234"

# 脱敏处理
masked_text, mapping = model.encode_sensitive(text)

# 模拟大模型输出中的拼写错误
llm_output_with_errors = masked_text.replace("手机号是", "联系电话为")

# 使用模糊匹配还原
restored_text = model.decode_sensitive(llm_output_with_errors, mapping)
print("还原后：", restored_text)
```

### 批量处理

您可以扩展`EnhancedNamedEntityEndsideModel`类来支持批量处理：

```python
# 扩展模型以支持批量处理
class BatchProcessingModel(EnhancedNamedEntityEndsideModel):
    def batch_process(self, texts, mock_llm_func=None):
        results = []
        
        for text in texts:
            # 脱敏处理
            masked_text, mapping = self.encode_sensitive(text)
            
            # 模拟大模型处理
            if mock_llm_func:
                llm_result = mock_llm_func(masked_text)
            else:
                # 默认的模拟大模型处理
                llm_result = f"处理结果: {masked_text}\n这是生成的内容。"
            
            # 还原处理
            restored_text = self.decode_sensitive(llm_result, mapping)
            
            results.append((masked_text, llm_result, restored_text))
        
        return results

# 使用批量处理模型
batch_model = BatchProcessingModel()
texts = [
    "王小明的手机号是13812345678",
    "李华的邮箱是lihua@example.com",
    "张伟的身份证号是110101199001011234"
]

results = batch_model.batch_process(texts)

for i, (hidden, llm_out, restored) in enumerate(results):
    print(f"\n文本 {i+1}:")
    print(f"脱敏后: {hidden}")
    print(f"大模型输出: {llm_out}")
    print(f"还原后: {restored}")
```

### 用户交互模式

运行主脚本即可进入用户交互模式：

```bash
python has_workflow_improved.py
```

运行后，您可以：
- 输入自定义文本进行脱敏处理
- 选择需要脱敏的敏感信息类型
- 查看脱敏结果、模拟大模型输出和还原结果
- 选择是否继续处理新的文本

### 输入示例

以下是一些常用的输入示例，展示不同类型敏感信息的处理效果：

#### 个人信息示例
```
王小明的手机号是13812345678，身份证号为110101199003079876，
他的邮箱是xiaoming@example.com，银行卡号为6222 1234 5678 9012。
他住在北京市朝阳区建国路88号，出生日期是1990/03/07。
```

#### 公司信息示例
```
北京科技有限公司的联系电话是13987654321，
法定代表人是李华，公司地址在上海市浦东新区张江高科技园区博云路2号。
公司邮箱是contact@beijingtech.com。
```

#### 交易信息示例
```
交易单号：TX202305160001，
付款人：张伟，手机号：13712345678，
收款人：刘芳，卡号：6226 8888 8888 8888，
交易金额：10000.00元，交易日期：2023-05-16。
```

#### 网络安全信息示例
```
服务器IP地址是192.168.1.100，管理员账户为admin，密码为Admin12345，
数据库连接字符串为jdbc:mysql://localhost:3306/userdb?user=root&password=Root12345。
```

### 完整流程演示

所有的功能都已经整合到`has_workflow_improved.py`文件中，运行以下命令体验完整的HaS隐私保护流程：

```bash
python has_workflow_improved.py
```

这个脚本会展示：
- 原始文本（包含隐私信息）
- 脱敏后文本
- 脱敏映射关系
- 模拟大模型处理结果
- 还原后文本

### 端侧小模型与大模型集成

### 集成架构

`has_workflow_improved.py`实现了一个完整的隐私保护工作流，主要包含以下组件：

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  用户输入   │ ──> │   端侧小模型 │ ──> │   大模型    │
└─────────────┘     └─────────────┘     └─────────────┘
        ^                   │                  │
        │                   ▼                  │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  还原结果   │ <── │ 脱敏与还原   │ <── │ 模型输出    │
└─────────────┘     └─────────────┘     └─────────────┘
```

这种架构确保了敏感信息不会离开用户设备，同时保留了大模型的强大能力。端侧小模型负责本地的脱敏和还原操作，而大模型则专注于处理不包含敏感信息的文本内容。

### 核心功能

1. **端侧小模型封装**：通过`EnhancedNamedEntityEndsideModel`类提供了完整的端侧小模型封装，负责敏感信息的本地处理

2. **模拟大模型**：内置了模拟大模型函数，用于测试整个集成流程

3. **工作流集成**：封装了端侧小模型与大模型的完整交互流程

4. **自定义敏感信息处理**：支持通过继承方式自定义敏感信息的处理逻辑

5. **完整场景测试**：包含多个测试场景，验证不同类型敏感信息的处理效果

### 使用方法

运行端侧小模型与大模型集成演示：

```bash
python has_workflow_improved.py
```

这将启动交互式界面，您可以输入文本并查看脱敏、大模型处理和还原的完整流程。

### 测试场景

集成实现包含以下测试场景：

1. **个人敏感信息处理**：处理包含姓名、手机号、身份证号等个人信息的文本

2. **企业敏感信息处理**：处理包含公司名称、联系电话、企业邮箱等信息的文本

3. **UUID模式脱敏**：演示使用UUID模式对敏感信息进行高安全性脱敏

4. **自定义敏感信息类型**：演示如何通过继承和自定义模式处理特定类型的敏感信息（如IP地址和密码）

### 自定义敏感信息处理示例

以下是创建自定义端侧模型并处理特定类型敏感信息的示例：

```python
# 定义自定义端侧模型类
class CustomEndsideModel:
    def __init__(self, custom_patterns=None):
        # 初始化端侧小模型（HaS模拟器）
        self.simulator = HideAndSeekSimulator(use_uuid=True)
        # 保存自定义模式
        self.custom_patterns = custom_patterns or {}
    
    def desensitize(self, user_input, sensitive_types=None):
        # 执行脱敏操作
        if sensitive_types:
            hidden_text, mapping = self.simulator.hide_with_params(
                user_input, 
                include_types=sensitive_types,
                custom_patterns=self.custom_patterns
            )
        else:
            hidden_text, mapping = self.simulator.hide(user_input)
        return hidden_text, mapping
    
    def restore(self, llm_output, mapping):
        # 执行还原操作
        # 注意：需要将mapping应用到模拟器的seek_map
        for original, encoded in mapping.items():
            self.simulator.seek_map[encoded] = original
        
        # 使用模糊匹配进行还原，提高还原成功率
        restored_text = self.simulator.seek_with_options(
            llm_output, 
            use_fuzzy_matching=True,
            min_confidence=0.7
        )
        return restored_text

# 创建自定义端侧模型实例，处理IP地址和密码
custom_patterns = {
    "ip_address": (r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", None),
    "password": (r"密码[:：]?\s*([a-zA-Z0-9]{6,20})", None)
}

# 创建自定义端侧模型实例
custom_model = CustomEndsideModel(custom_patterns=custom_patterns)

# 处理包含自定义敏感信息的文本
input_text = "服务器IP地址是192.168.1.1，管理员密码是Admin12345"
hidden_text, mapping = custom_model.desensitize(input_text)

# 调用大模型处理脱敏后的文本
llm_result = mock_llm(hidden_text)

# 还原大模型输出
restored_text = custom_model.restore(llm_result, mapping)
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

test_restore.py中的还原策略经过增强，包含以下特点：

1. 维护脱敏前后的双向映射关系
2. 在大模型返回结果后，根据映射关系进行精准还原
3. 按照字符长度从长到短进行替换，避免部分匹配导致的错误
4. 支持正则表达式精确匹配，提高还原准确率
5. 提供模糊匹配还原功能，可处理大模型输出中的拼写错误和格式变化

模糊匹配还原基于字符串相似度计算，在test_restore.py中进行了特别优化：
- 降低模糊匹配置信度阈值至0.5，提高还原成功率
- 增加max_distance参数允许更多字符差异
- 关闭单词边界匹配，适应不同上下文
- 新增文本格式预处理步骤（去除多余空白字符）
- 增加二次模糊匹配尝试，提高还原覆盖率

### 还原结果验证机制

test_restore.py实现了改进的还原结果验证机制：

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

## 应用场景

- **大模型推理时的隐私保护**：在将用户输入发送给大模型前进行脱敏，防止敏感信息泄露
- **边缘设备上的隐私计算**：在资源受限的边缘设备上实现高效的隐私保护
- **数据处理和分析**：在数据分析过程中保护用户隐私
- **API服务中的隐私防护**：在API服务中集成，为用户提供隐私保护

## 注意事项

1. 本实现是对腾讯实验室HaS技术的模拟，可能与实际技术存在差异
2. 对于复杂的敏感信息识别，可能需要根据具体场景调整正则表达式
3. 在生产环境中使用时，建议进一步评估安全性和性能
4. 模糊匹配还原功能是简化版实现，对于复杂场景可能需要更高级的算法
5. 加载HaS-820m模型需要网络连接，如果网络受限，脚本会自动使用模拟模式

## 参考资料

- 腾讯实验室 HaS 技术：https://xlab.tencent.com/cn/2023/12/05/hide_and_seek/
- HaS-820m 开源模型：https://huggingface.co/SecurityXuanwuLab/HaS-820m

## License

[MIT License](https://opensource.org/licenses/MIT)


要运行项目，只需执行以下命令：

```bash
python has_workflow_improved.py
```

按照提示输入文本和选择敏感信息类型，系统会自动执行脱敏处理、模拟大模型处理和敏感信息还原流程。

这些文件已被整合到has_workflow_improved.py中，项目结构已优化。

## 安装依赖

运行本项目需要安装以下Python库：

```bash
pip install re time random
```

## 快速开始

### 基本演示

运行增强版HaS隐私保护技术演示：

```bash
python has_workflow_improved.py
```

这将启动一个交互式界面，您可以输入文本并选择要脱敏的敏感信息类型，系统会自动执行脱敏处理、模拟大模型处理和敏感信息还原流程。

### 使用流程

1. 运行主脚本：`python has_workflow_improved.py`
2. 按照提示输入您想处理的文本
3. 选择要脱敏的敏感信息类型（如name,company,position）
4. 查看脱敏后的文本、大模型处理结果和还原后的文本
5. 选择是否继续处理新的文本

项目的核心功能都集中在`has_workflow_improved.py`文件中，包括敏感信息识别、脱敏和还原的完整实现。

### 代码集成示例

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

### 指定敏感信息类型

您可以根据需要选择要脱敏的敏感信息类型：

```python
# 只对姓名和公司进行脱敏
sensitive_types = ["name", "company"]
desensitized_text, mapping = endside_model.desensitize(user_input, sensitive_types)

# 也可以使用逗号分隔的字符串
sensitive_types = "name,company,position"
desensitized_text, mapping = endside_model.desensitize(user_input, sensitive_types)
```

### 配置选项

端侧小模型支持多种配置选项：

```python
# 配置端侧小模型
endside_model = EnhancedNamedEntityEndsideModel()
endside_model.configure(
    use_uuid=False,         # 是否使用UUID格式的占位符
    preserve_format=True,   # 是否保留原始格式
    enable_fuzzy_matching=True  # 是否启用模糊匹配还原
)
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
            "password": r"password\s*[:=]\s*['\"]([^'"]+)['\"]"
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

### 处理大模型输出中的错误

`EnhancedNamedEntityEndsideModel`类内置了模糊匹配还原功能，可以处理大模型输出中可能出现的小错误：

```python
# 创建模型并启用模糊匹配
model = EnhancedNamedEntityEndsideModel(enable_fuzzy_matching=True)

# 示例文本
text = "张敏的手机号是13812345678，身份证号为110101199001011234"

# 脱敏处理
masked_text, mapping = model.encode_sensitive(text)

# 模拟大模型输出中的拼写错误
llm_output_with_errors = masked_text.replace("手机号是", "联系电话为")

# 使用模糊匹配还原
restored_text = model.decode_sensitive(llm_output_with_errors, mapping)
print("还原后：", restored_text)
```

### 批量处理

您可以扩展`EnhancedNamedEntityEndsideModel`类来支持批量处理：

```python
# 扩展模型以支持批量处理
class BatchProcessingModel(EnhancedNamedEntityEndsideModel):
    def batch_process(self, texts, mock_llm_func=None):
        results = []
        
        for text in texts:
            # 脱敏处理
            masked_text, mapping = self.encode_sensitive(text)
            
            # 模拟大模型处理
            if mock_llm_func:
                llm_result = mock_llm_func(masked_text)
            else:
                # 默认的模拟大模型处理
                llm_result = f"处理结果: {masked_text}\n这是生成的内容。"
            
            # 还原处理
            restored_text = self.decode_sensitive(llm_result, mapping)
            
            results.append((masked_text, llm_result, restored_text))
        
        return results

# 使用批量处理模型
batch_model = BatchProcessingModel()
texts = [
    "王小明的手机号是13812345678",
    "李华的邮箱是lihua@example.com",
    "张伟的身份证号是110101199001011234"
]

results = batch_model.batch_process(texts)

for i, (hidden, llm_out, restored) in enumerate(results):
    print(f"\n文本 {i+1}:")
    print(f"脱敏后: {hidden}")
    print(f"大模型输出: {llm_out}")
    print(f"还原后: {restored}")
```

### 用户交互模式

运行主脚本即可进入用户交互模式：

```bash
python has_workflow_improved.py
```

运行后，您可以：
- 输入自定义文本进行脱敏处理
- 选择需要脱敏的敏感信息类型
- 查看脱敏结果、模拟大模型输出和还原结果
- 选择是否继续处理新的文本

### 输入示例

以下是一些常用的输入示例，展示不同类型敏感信息的处理效果：

#### 个人信息示例
```
王小明的手机号是13812345678，身份证号为110101199003079876，
他的邮箱是xiaoming@example.com，银行卡号为6222 1234 5678 9012。
他住在北京市朝阳区建国路88号，出生日期是1990/03/07。
```

#### 公司信息示例
```
北京科技有限公司的联系电话是13987654321，
法定代表人是李华，公司地址在上海市浦东新区张江高科技园区博云路2号。
公司邮箱是contact@beijingtech.com。
```

#### 交易信息示例
```
交易单号：TX202305160001，
付款人：张伟，手机号：13712345678，
收款人：刘芳，卡号：6226 8888 8888 8888，
交易金额：10000.00元，交易日期：2023-05-16。
```

#### 网络安全信息示例
```
服务器IP地址是192.168.1.100，管理员账户为admin，密码为Admin12345，
数据库连接字符串为jdbc:mysql://localhost:3306/userdb?user=root&password=Root12345。
```

### 完整流程演示

所有的功能都已经整合到`has_workflow_improved.py`文件中，运行以下命令体验完整的HaS隐私保护流程：

```bash
python has_workflow_improved.py
```

这个脚本会展示：
- 原始文本（包含隐私信息）
- 脱敏后文本
- 脱敏映射关系
- 模拟大模型处理结果
- 还原后文本

### 端侧小模型与大模型集成

### 集成架构

`has_workflow_improved.py`实现了一个完整的隐私保护工作流，主要包含以下组件：

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  用户输入   │ ──> │   端侧小模型 │ ──> │   大模型    │
└─────────────┘     └─────────────┘     └─────────────┘
        ^                   │                  │
        │                   ▼                  │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  还原结果   │ <── │ 脱敏与还原   │ <── │ 模型输出    │
└─────────────┘     └─────────────┘     └─────────────┘
```

这种架构确保了敏感信息不会离开用户设备，同时保留了大模型的强大能力。端侧小模型负责本地的脱敏和还原操作，而大模型则专注于处理不包含敏感信息的文本内容。

### 核心功能

1. **端侧小模型封装**：通过`EnhancedNamedEntityEndsideModel`类提供了完整的端侧小模型封装，负责敏感信息的本地处理

2. **模拟大模型**：内置了模拟大模型函数，用于测试整个集成流程

3. **工作流集成**：封装了端侧小模型与大模型的完整交互流程

4. **自定义敏感信息处理**：支持通过继承方式自定义敏感信息的处理逻辑

5. **完整场景测试**：包含多个测试场景，验证不同类型敏感信息的处理效果

### 使用方法

运行端侧小模型与大模型集成演示：

```bash
python has_workflow_improved.py
```

这将启动交互式界面，您可以输入文本并查看脱敏、大模型处理和还原的完整流程。

### 测试场景

集成实现包含以下测试场景：

1. **个人敏感信息处理**：处理包含姓名、手机号、身份证号等个人信息的文本

2. **企业敏感信息处理**：处理包含公司名称、联系电话、企业邮箱等信息的文本

3. **UUID模式脱敏**：演示使用UUID模式对敏感信息进行高安全性脱敏

4. **自定义敏感信息类型**：演示如何通过继承和自定义模式处理特定类型的敏感信息（如IP地址和密码）

### 自定义敏感信息处理示例

以下是创建自定义端侧模型并处理特定类型敏感信息的示例：

```python
# 定义自定义端侧模型类
class CustomEndsideModel:
    def __init__(self, custom_patterns=None):
        # 初始化端侧小模型（HaS模拟器）
        self.simulator = HideAndSeekSimulator(use_uuid=True)
        # 保存自定义模式
        self.custom_patterns = custom_patterns or {}
    
    def desensitize(self, user_input, sensitive_types=None):
        # 执行脱敏操作
        if sensitive_types:
            hidden_text, mapping = self.simulator.hide_with_params(
                user_input, 
                include_types=sensitive_types,
                custom_patterns=self.custom_patterns
            )
        else:
            hidden_text, mapping = self.simulator.hide(user_input)
        return hidden_text, mapping
    
    def restore(self, llm_output, mapping):
        # 执行还原操作
        # 注意：需要将mapping应用到模拟器的seek_map
        for original, encoded in mapping.items():
            self.simulator.seek_map[encoded] = original
        
        # 使用模糊匹配进行还原，提高还原成功率
        restored_text = self.simulator.seek_with_options(
            llm_output, 
            use_fuzzy_matching=True,
            min_confidence=0.7
        )
        return restored_text

# 创建自定义端侧模型实例，处理IP地址和密码
custom_patterns = {
    "ip_address": (r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", None),
    "password": (r"密码[:：]?\s*([a-zA-Z0-9]{6,20})", None)
}

# 创建自定义端侧模型实例
custom_model = CustomEndsideModel(custom_patterns=custom_patterns)

# 处理包含自定义敏感信息的文本
input_text = "服务器IP地址是192.168.1.1，管理员密码是Admin12345"
hidden_text, mapping = custom_model.desensitize(input_text)

# 调用大模型处理脱敏后的文本
llm_result = mock_llm(hidden_text)

# 还原大模型输出
restored_text = custom_model.restore(llm_result, mapping)
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

test_restore.py中的还原策略经过增强，包含以下特点：

1. 维护脱敏前后的双向映射关系
2. 在大模型返回结果后，根据映射关系进行精准还原
3. 按照字符长度从长到短进行替换，避免部分匹配导致的错误
4. 支持正则表达式精确匹配，提高还原准确率
5. 提供模糊匹配还原功能，可处理大模型输出中的拼写错误和格式变化

模糊匹配还原基于字符串相似度计算，在test_restore.py中进行了特别优化：
- 降低模糊匹配置信度阈值至0.5，提高还原成功率
- 增加max_distance参数允许更多字符差异
- 关闭单词边界匹配，适应不同上下文
- 新增文本格式预处理步骤（去除多余空白字符）
- 增加二次模糊匹配尝试，提高还原覆盖率

### 还原结果验证机制

test_restore.py实现了改进的还原结果验证机制：

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

## 应用场景

- **大模型推理时的隐私保护**：在将用户输入发送给大模型前进行脱敏，防止敏感信息泄露
- **边缘设备上的隐私计算**：在资源受限的边缘设备上实现高效的隐私保护
- **数据处理和分析**：在数据分析过程中保护用户隐私
- **API服务中的隐私防护**：在API服务中集成，为用户提供隐私保护

## 注意事项

1. 本实现是对腾讯实验室HaS技术的模拟，可能与实际技术存在差异
2. 对于复杂的敏感信息识别，可能需要根据具体场景调整正则表达式
3. 在生产环境中使用时，建议进一步评估安全性和性能
4. 模糊匹配还原功能是简化版实现，对于复杂场景可能需要更高级的算法
5. 加载HaS-820m模型需要网络连接，如果网络受限，脚本会自动使用模拟模式

## 参考资料

- 腾讯实验室 HaS 技术：https://xlab.tencent.com/cn/2023/12/05/hide_and_seek/
- HaS-820m 开源模型：https://huggingface.co/SecurityXuanwuLab/HaS-820m

## License

[MIT License](https://opensource.org/licenses/MIT)
