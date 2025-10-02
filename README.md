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

### 2. 增强的脱敏安全性
- ✅ 支持UUID模式的脱敏，生成高安全性的唯一标识符
- ✅ 基于哈希和随机盐值的令牌生成机制
- ✅ 保留格式或完全替换两种脱敏策略

### 3. 健壮的还原功能
- ✅ 精确的文本还原机制
- ✅ 支持模糊匹配还原，处理大模型输出中的拼写错误
- ✅ 基于相似度的智能还原策略

### 4. 灵活的配置选项
- ✅ 可选择性地对特定类型的敏感信息进行脱敏
- ✅ 支持包含/排除特定类型的敏感信息
- ✅ 可自定义敏感信息的正则表达式和处理函数

### 5. 实用工具功能
- ✅ 批量处理多文本
- ✅ 保存和加载脱敏映射关系
- ✅ 脱敏历史记录管理

## 项目结构

本项目经过优化，保留了核心功能，删除了重复和不必要的文件。当前项目结构如下：

```
has_hide_seek/
├── .gitignore           # Git忽略文件配置
├── README.md            # 项目介绍文档
├── README_ENHANCED.md   # 增强版工作流详细使用指南
├── has_workflow_improved.py  # 核心实现文件，包含增强版HaS隐私保护技术
└── test_case_complex.txt    # 复杂测试用例，包含多种敏感信息
```

`has_workflow_improved.py` 是项目的核心实现文件，包含了所有敏感信息识别、脱敏和还原的功能。

## 核心功能

项目的核心功能都集中在 `has_workflow_improved.py` 文件中，主要包括：

1. **EnhancedNamedEntityEndsideModel 类**：负责敏感信息识别、脱敏和还原
   - 支持识别姓名、公司、职位、部门、金额、业绩、手机号、身份证号、邮箱等多种敏感信息
   - 提供语义化占位符格式（如`<name>_0`）
   - 实现智能还原策略，处理大模型输出变化
   - 支持自定义敏感信息类型和处理规则

2. **模拟大模型交互**：通过简单的模拟大模型展示完整的隐私保护工作流

3. **用户交互界面**：提供命令行交互方式，支持自定义敏感信息类型选择

## 使用方法

要运行项目，只需执行以下命令：

```bash
python has_workflow_improved.py
```

运行后，您将看到交互式菜单，可以选择以下操作：

1. **使用预设场景进行演示** - 选择内置的4个预设场景（个人信息、金融信息、企业信息、网络安全信息）进行快速演示
2. **输入自定义文本进行演示** - 输入您自己的包含敏感信息的文本进行演示
3. **第一步：输入文本进行脱敏** - 生成可复制的脱敏文本，供复制到互联网大模型使用
4. **第二步：输入大模型回答进行还原** - 使用之前保存的脱敏映射关系还原大模型回答中的敏感信息
5. **退出程序** - 结束当前会话

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
   
3. **第二步：输入大模型回答进行还原**（选择菜单选项4）
   - 用户输入之前生成的会话ID
   - 用户输入大模型的回答文本
   - 系统使用之前保存的脱敏映射关系还原敏感信息
   - 输出包含还原后敏感信息的完整文本

## 安装依赖

本项目仅使用Python标准库，无需安装额外依赖包。您需要确保您的环境中安装了Python 3.6或更高版本。

```bash
# 检查Python版本
python --version
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
masked_text, mapping = endside_model.encode_sensitive(user_input, sensitive_types)

# 模拟大模型处理
def mock_llm(input_text):
    # 这里是您的大模型调用代码
    return f"处理结果：{input_text}\n这是生成的内容。"

llm_result = mock_llm(masked_text)

# 执行还原处理
restored_text = endside_model.decode_sensitive(llm_result, mapping)

print("原始文本:", user_input)
print("脱敏后文本:", masked_text)
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

#### 集成架构

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

1. **端侧小模型封装**：通过`EnhancedNamedEntityEndsideModel`类提供了完整的端侧小模型封装，使用`encode_sensitive`和`decode_sensitive`方法负责敏感信息的本地处理

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
    
    def encode_sensitive(self, user_input, sensitive_types=None):
        # 执行脱敏操作
        if sensitive_types:
            masked_text, mapping = self.simulator.hide_with_params(
                user_input, 
                include_types=sensitive_types,
                custom_patterns=self.custom_patterns
            )
        else:
            masked_text, mapping = self.simulator.hide(user_input)
        return masked_text, mapping
    
    def decode_sensitive(self, llm_output, mapping):
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
masked_text, mapping = custom_model.encode_sensitive(input_text)

# 调用大模型处理脱敏后的文本
llm_result = mock_llm(masked_text)

# 还原大模型输出
restored_text = custom_model.decode_sensitive(llm_result, mapping)
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
