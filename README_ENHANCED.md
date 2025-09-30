# HaS (Hide and Seek) 隐私保护技术 - 增强版工作流使用指南

## 概述

本使用指南详细介绍了**HaS隐私保护技术增强版工作流**的功能和使用方法。该工作流实现了在大模型交互过程中保护用户隐私的完整流程，通过端侧小模型对用户输入进行脱敏处理，将脱敏后的文本提交给大模型，然后将大模型输出的结果中的敏感信息还原，从而保障用户隐私安全。

## 新增功能介绍

增强版工作流在原有HaS技术的基础上，增加了以下核心功能：

1. **增强的端侧小模型**：提供更强大的敏感信息识别、脱敏和还原能力
2. **智能还原策略**：能够处理大模型输出的文本变化，如改写、语法调整等
3. **完整工作流集成**：将端侧小模型与大模型交互过程标准化、流程化
4. **多种配置选项**：支持UUID安全模式、自定义敏感信息类型等高级功能
5. **用户友好的交互界面**：提供预设场景和自定义文本处理两种模式
6. **性能监控**：实时显示各阶段处理时间，便于性能优化

## 主要组件

### 1. EnhancedEndsideModel

增强版端侧小模型封装类，负责本地敏感信息的识别、脱敏和还原。主要特性包括：

- 支持多种敏感信息类型识别
- 提供标准和UUID两种脱敏模式
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

## 安装与依赖

本项目基于Python开发，主要依赖项包括：

- Python 3.7+ 
- re (标准库)
- time (标准库)
- random (标准库)

安装步骤：

1. 确保已安装Python 3.7或更高版本
2. 克隆或下载项目代码
3. 确保项目目录中包含has_workflow_improved.py文件

## 使用方法

### 基本使用

运行增强版工作流演示脚本：

```bash
python has_workflow_improved.py
```

运行后，您将看到交互式菜单，可以选择：

1. 使用预设场景进行演示
2. 输入自定义文本进行演示
3. 退出程序

### 预设场景

脚本内置了4个预设场景，覆盖不同类型的敏感信息：

1. **个人信息处理**：包含姓名、手机号、身份证号等个人敏感信息
2. **金融信息处理**：包含银行卡号、交易金额等金融敏感信息
3. **企业信息处理**：包含公司名称、统一社会信用代码等企业敏感信息
4. **网络安全信息处理**：包含IP地址、密码等网络安全敏感信息

### 自定义文本处理

您可以输入任意包含敏感信息的文本，系统将自动识别并处理其中的敏感信息。

### UUID安全模式

在处理过程中，系统会询问是否使用UUID模式进行脱敏。UUID模式提供更高的安全性，通过生成随机唯一标识符替换敏感信息，而不是简单的格式保留替换。

选择UUID模式：

```
是否使用UUID模式进行脱敏？(y/n，默认n)：y
```

### 自定义敏感信息处理

对于网络安全等特殊场景，系统支持自定义敏感信息类型的识别和处理。脚本中已预定义了以下自定义模式：

- IP地址：如192.168.1.1
- 密码：如密码是Admin12345
- 统一社会信用代码：如91110108MA00123456
- 交易单号：如TX202305160001

启用自定义敏感信息处理：

```
是否需要处理网络安全等自定义敏感信息？(y/n，默认n)：y
```

## 工作流程详解

完整的HaS隐私保护工作流包含以下三个主要阶段：

### 1. 脱敏处理（Hide阶段）

端侧小模型对用户输入的原始文本进行敏感信息识别和脱敏处理：

1. 识别文本中的敏感信息（如手机号、身份证号、邮箱等）
2. 根据配置的脱敏策略（标准或UUID模式）替换敏感信息
3. 建立脱敏前后的映射关系，用于后续还原
4. 输出脱敏后的文本

### 2. 大模型处理

脱敏后的文本被传输至大模型进行处理：

1. 大模型接收不包含敏感信息的文本
2. 大模型根据输入内容生成回答
3. 大模型可能会对输入文本进行改写、语法调整或添加额外信息
4. 大模型返回处理结果

### 3. 还原处理（Seek阶段）

端侧小模型将大模型返回的文本中的敏感信息还原：

1. 接收大模型返回的处理结果
2. 对结果进行预处理，提高还原准确率
3. 根据脱敏阶段建立的映射关系进行还原
4. 如果标准还原效果不佳，可启用模糊匹配进行智能还原
5. 对还原结果进行后处理，输出最终文本

## 配置选项详解

增强版工作流提供了多种配置选项，可以根据实际需求进行调整：

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| use_uuid | 布尔值 | False | 是否使用UUID模式进行脱敏 |
| preserve_format | 布尔值 | True | 是否保留原始敏感信息的格式 |
| enable_fuzzy_matching | 布尔值 | True | 是否启用模糊匹配还原功能 |
| min_confidence | 浮点数 | 0.7 | 模糊匹配的最小置信度 |
| max_distance | 整数 | 3 | 模糊匹配允许的最大字符差异 |
| custom_patterns | 字典 | None | 自定义敏感信息模式和处理函数 |

## 性能指标

工作流执行过程中，系统会实时显示各阶段的处理时间：

- 脱敏时间：端侧小模型识别和处理敏感信息的时间
- 大模型处理时间：模拟大模型处理文本的时间
- 还原时间：端侧小模型还原敏感信息的时间
- 总耗时：整个工作流的总执行时间

## 实际应用场景

### 1. 大模型交互时的隐私保护

在用户与大模型交互过程中，通过本工作流可以有效保护用户隐私：

```python
# 创建工作流实例
workflow = CompleteHaSWorkflow()
# 配置为UUID安全模式
workflow.configure_endside_model(use_uuid=True, enable_fuzzy_matching=True)
# 用户输入包含隐私信息的查询
user_query = "我叫张三，身份证号是110101199001011234，我的银行卡号是6222123456789012"
# 运行工作流
result = workflow.run(user_query)
# 获取最终回复（包含还原的敏感信息）
final_response = result['final_response']
```

### 2. 集成到实际应用系统

可以将本工作流集成到实际应用系统中，为用户提供隐私保护服务：

```python
from has_workflow_improved import CompleteHaSWorkflow

class PrivacyProtectedChatbot:
    def __init__(self):
        # 初始化HaS工作流
        self.has_workflow = CompleteHaSWorkflow()
        # 配置工作流参数
        self.has_workflow.configure_endside_model(
            use_uuid=True,
            enable_fuzzy_matching=True
        )
        
    def process_query(self, user_query):
        # 使用HaS工作流处理用户查询
        result = self.has_workflow.run(user_query)
        # 返回最终处理结果
        return result['final_response']

# 使用示例
chatbot = PrivacyProtectedChatbot()
response = chatbot.process_query("我的手机号是13812345678，请问如何修改密码？")
print(response)
```

### 3. 批量处理敏感文本

对于需要批量处理的敏感文本，可以使用工作流的批量处理功能：

```python
from has_workflow_improved import CompleteHaSWorkflow

# 准备批量文本
texts_to_process = [
    "用户王小明的手机号是13812345678，身份证号是110101199001011234",
    "李华的邮箱是lihua@example.com，银行卡号是6226888888888888",
    "北京科技有限公司的统一社会信用代码是91110108MA00123456"
]

# 批量处理
results = []
for text in texts_to_process:
    workflow = CompleteHaSWorkflow()
    result = workflow.run(text)
    results.append(result)
    
# 分析处理结果
for i, result in enumerate(results):
    print(f"\n文本 {i+1} 处理结果：")
    print(f"原始文本: {result['original_input']}")
    print(f"脱敏后: {result['desensitized_text']}")
    print(f"还原后: {result['final_response']}")
```

## 常见问题解答

### 1. 如何添加新的敏感信息类型？

您可以通过定义自定义模式来添加新的敏感信息类型：

```python
# 定义自定义敏感信息模式
def custom_replace_qq(match):
    original = match.group()
    encoded = "QQ_" + "*" * (len(original) - 2)
    return encoded

custom_patterns = {
    'qq_number': (r'QQ[:：]?\\s*(\\d{5,13})', custom_replace_qq)
}

# 配置工作流使用自定义模式
workflow = CompleteHaSWorkflow()
workflow.configure_endside_model(custom_patterns=custom_patterns)
```

### 2. 如何调整模糊匹配的参数？

您可以通过configure_endside_model方法调整模糊匹配的参数：

```python
workflow.configure_endside_model(
    enable_fuzzy_matching=True,
    min_confidence=0.6,  # 降低置信度阈值，提高还原率但可能降低准确率
    max_distance=5       # 增加允许的字符差异，适应更多变化
)
```

### 3. 如何在实际系统中集成本工作流？

您可以将本工作流作为一个组件集成到实际系统中：

1. 将has_workflow_improved.py文件添加到您的项目中
2. 确保项目中包含所需的依赖项
3. 在您的代码中导入并使用CompleteHaSWorkflow类
4. 根据实际需求配置工作流参数

### 4. 如何处理特定领域的敏感信息？

对于特定领域的敏感信息，您可以：

1. 定义该领域特有的敏感信息模式
2. 实现专门的处理函数
3. 通过custom_patterns参数配置到工作流中
4. 根据需要调整脱敏和还原策略

## 注意事项

1. 本实现是对腾讯实验室HaS技术的模拟，可能与实际技术存在差异
2. 演示中的大模型是模拟实现，实际应用中需要替换为真实的大模型API
3. 敏感信息的识别和还原效果可能受到文本复杂度、格式变化等因素影响
4. 在处理极长文本或包含大量敏感信息的文本时，可能会影响处理性能
5. 建议在实际应用中根据具体场景进行充分测试和优化

## 未来优化方向

1. 支持更多类型的敏感信息识别
2. 优化模糊匹配算法，提高还原准确率
3. 实现分布式处理，提高大规模文本处理能力
4. 支持更多大模型API的集成
5. 提供图形用户界面，方便非技术人员使用

## 版权声明

本项目基于腾讯实验室披露的HaS技术实现，仅供学习和研究使用。

---

通过本使用指南，您应该能够充分了解HaS隐私保护技术增强版工作流的功能和使用方法。如果您在使用过程中遇到任何问题或有任何建议，欢迎随时提出和交流。