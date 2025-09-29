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

```
has_hide_seek/
├── has_simulation.py           # HaS技术的核心模拟实现
├── run_has820m.py              # 集成HaS-820m模型的完整流程演示
├── test.py                     # 单元测试和实体替换演示
├── endside_model_integration.py # 端侧小模型与大模型集成实现
└── README.md                   # 项目说明文档
```

### 文件说明

1. **has_simulation.py**：实现了`HideAndSeekSimulator`类，包含完整的脱敏（Hide）和还原（Seek）功能，可以识别和处理手机号、身份证号、邮箱和中文姓名等敏感信息。

2. **run_has820m.py**：封装了HaS-820m模型的加载和使用，并展示了完整的隐私保护流程：脱敏 -> 调用大模型 -> 还原。

3. **test.py**：包含单元测试用例，测试脱敏、还原等功能，并提供了实体替换功能的演示。

4. **endside_model_integration.py**：实现了端侧小模型与大模型的集成框架，提供了完整的工作流封装、自定义敏感信息处理、以及多场景测试。

## 安装依赖

运行本项目需要安装以下Python库：

```bash
pip install transformers torch
```

## 使用指南

### 基本用法

```python
from has_simulation import HideAndSeekSimulator

# 创建模拟器实例
simulator = HideAndSeekSimulator(use_uuid=False, preserve_format=True)

# 输入文本
text = "王小明的手机号是13812345678，身份证号为110101199003079876，邮箱是xiaoming@example.com"

# 完整处理流程：脱敏 -> 调用大模型 -> 还原
hidden_text, llm_output, restored_text = simulator.process(text)

print("原始文本:", text)
print("脱敏后文本:", hidden_text)
print("还原后文本:", restored_text)
```

### 简化版函数调用

```python
from has_simulation import encode_sensitive, decode_sensitive

# 脱敏处理
encoded_text, code_map = encode_sensitive("王小明的手机号是13812345678")

# 还原处理
restored_text = decode_sensitive(encoded_text, code_map)
```

### 指定敏感信息类型

```python
# 只对手机号和身份证号进行脱敏
specific_types = ["phone", "id"]
encoded_text, code_map = encode_sensitive(text, specific_types)

# 或者使用高级参数控制
encoded_text, code_map = simulator.hide_with_params(
    text, 
    include_types=["phone", "id"]  # 包含的类型
    # exclude_types=["email", "name"]  # 排除的类型
)
```

### 使用UUID模式提高安全性

```python
# 创建使用UUID模式的模拟器
uuid_simulator = HideAndSeekSimulator(use_uuid=True, preserve_format=False)

# 执行脱敏
encoded_text, code_map = uuid_simulator.hide(text)
```

### 自定义敏感信息类型

```python
# 定义自定义替换函数
def custom_replace_ip(match):
    original = match.group()
    encoded = "***.***.***.***"
    simulator.hide_map[original] = encoded
    simulator.seek_map[encoded] = original
    return encoded

# 定义自定义模式
custom_patterns = {
    "ip_address": (r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", custom_replace_ip)
}

# 使用自定义模式
text_with_ip = "服务器IP地址是192.168.1.1，管理员邮箱是admin@example.com"
custom_encoded, custom_map = simulator.hide_with_params(text_with_ip, custom_patterns=custom_patterns)
```

### 处理大模型输出中的错误

```python
# 模拟大模型输出中的拼写错误
llm_output_with_errors = "张敏的手机号是138****5678，身份号码为110101********9876"

# 使用模糊匹配还原
restored_with_fuzzy = simulator.seek_with_options(llm_output_with_errors, use_fuzzy_matching=True)
```

### 保存和加载映射关系

```python
# 保存映射关系
simulator.save_mapping("mapping.json")

# 加载映射关系
new_simulator = HideAndSeekSimulator()
new_simulator.load_mapping("mapping.json")
```

### 批量处理

```python
texts = [
    "王小明的手机号是13812345678",
    "李华的邮箱是lihua@example.com",
    "张伟的身份证号是110101199001011234"
]

# 定义模拟大模型函数
def mock_llm(text):
    return f"处理后的文本: {text}"

# 批量处理
results = simulator.batch_process(texts, mock_llm_func=mock_llm)

for i, (hidden, llm_out, restored) in enumerate(results):
    print(f"\n文本 {i+1}:")
    print(f"脱敏后: {hidden}")
    print(f"大模型输出: {llm_out}")
    print(f"还原后: {restored}")
```

### 用户交互模式

项目中的多个脚本支持用户交互模式，可以直接在命令行中手动输入需要脱敏的文本，或选择预设的输入模板：

#### has_simulation.py

```bash
python has_simulation.py
```

运行后，您可以：
- 选择预设的输入模板（个人信息、公司信息、交易信息）
- 输入自定义文本进行脱敏处理
- 选择是否使用UUID模式
- 指定需要脱敏的敏感信息类型
- 查看脱敏结果、模拟大模型输出和还原结果

#### test_restore.py

```bash
python test_restore.py
```

运行后，您可以：
- 选择预设的输入模板（场景1-银行卡信息、场景2-个人身份信息、场景3-交易信息、场景4-网络安全信息）
- 输入数字1-4直接使用对应场景
- 输入自定义文本进行脱敏处理
- 选择脱敏模式（标准模式或UUID模式）
- 查看脱敏结果、脱敏映射关系、模拟大模型输出和还原结果
- 了解敏感信息的识别和还原情况

### 输入模板样例

以下是预设的输入模板样例：

#### has_simulation.py 模板

##### 1. 个人信息模板
```
王小明的手机号是13812345678，身份证号为110101199003079876，
他的邮箱是xiaoming@example.com，银行卡号为6222 1234 5678 9012。
他住在北京市朝阳区建国路88号，出生日期是1990/03/07。
```

##### 2. 公司信息模板
```
北京科技有限公司的联系电话是13987654321，
法定代表人是李华，公司地址在上海市浦东新区张江高科技园区博云路2号。
公司邮箱是contact@beijingtech.com。
```

##### 3. 交易信息模板
```
交易单号：TX202305160001，
付款人：张伟，手机号：13712345678，
收款人：刘芳，卡号：6226 8888 8888 8888，
交易金额：10000.00元，交易日期：2023-05-16。
```

#### test_restore.py 模板

##### 1. 场景1 - 银行卡信息
```
客户您好，您的尾号为1234的工商银行储蓄卡于2024年5月1日发生一笔转账交易，
金额为5000元，对方账户为招商银行尾号4321，
交易编号为PAY202405010001，如有疑问请联系客服热线400-123-4567。
```

##### 2. 场景2 - 个人身份信息
```
张先生（身份证号：110101199001011234）于2024年5月1日在我司申请办理信用卡，
联系电话为13812345678，紧急联系人是李女士（13987654321），
居住地址为北京市朝阳区建国路88号，工作单位为北京科技有限公司。
```

##### 3. 场景3 - 交易信息
```
交易单号为TX202405010001的付款方是张三，金额为10000元，
收款方是李四，银行账户为6222020200012345678，交易时间为2024-05-01 10:30:45，
交易状态为已完成，备注为项目经费。
```

##### 4. 场景4 - 网络安全信息
```
服务器IP地址是192.168.1.100，管理员账户为admin，密码为Admin12345，
数据库连接字符串为jdbc:mysql://localhost:3306/userdb?user=root&password=Root12345，
访问令牌为eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c。
```

### 完整流程演示

运行`run_has820m.py`文件，体验完整的HaS隐私保护流程：

```bash
python run_has820m.py
```

这个脚本会展示：
- 原始文本（包含隐私信息）
- 脱敏后文本
- 脱敏映射关系
- 大模型处理结果
- 还原后文本

如果无法下载HaS-820m模型，脚本会自动使用模拟的大模型函数进行演示。

### 运行单元测试

```bash
python test.py test
```

### 实体替换演示

```bash
python test.py
```

这将演示模拟的HaS-820m模型的实体替换效果。

## 端侧小模型与大模型集成

### 集成架构

端侧小模型与大模型集成实现了一个完整的隐私保护工作流，主要包含以下组件：

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

1. **端侧小模型封装**：提供了完整的端侧小模型封装，负责敏感信息的本地处理

2. **模拟大模型**：内置了模拟大模型函数，用于测试整个集成流程

3. **工作流集成**：封装了端侧小模型与大模型的完整交互流程

4. **自定义敏感信息处理**：支持通过继承方式自定义敏感信息的处理逻辑

5. **完整场景测试**：包含多个测试场景，验证不同类型敏感信息的处理效果

### 使用方法

运行端侧小模型与大模型集成演示：

```bash
python endside_model_integration.py
```

这将自动运行所有测试场景，并展示每个场景的原始输入、脱敏结果和还原结果。

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