import unittest
import sys
from has_simulation import HideAndSeekSimulator

class TestHideAndSeek(unittest.TestCase):
    """
    测试腾讯实验室 HaS (Hide and Seek) 隐私保护技术的模拟实现
    """
    
    def setUp(self):
        """每个测试用例前初始化模拟器"""
        self.simulator = HideAndSeekSimulator()
    
    def test_hide_phone(self):
        """测试手机号脱敏功能"""
        text = "我的手机号是13812345678，请联系我。"
        hidden_text, _ = self.simulator.hide(text)
        self.assertNotIn("13812345678", hidden_text)
        self.assertRegex(hidden_text, r"138\*{4}5678")
    
    def test_hide_id(self):
        """测试身份证号脱敏功能"""
        text = "我的身份证号是110101199003079876，请核实。"
        hidden_text, _ = self.simulator.hide(text)
        self.assertNotIn("110101199003079876", hidden_text)
        self.assertRegex(hidden_text, r"110101\*{8}9876")
    
    def test_hide_email(self):
        """测试邮箱脱敏功能"""
        text = "请发送邮件到xiaoming@example.com联系我。"
        hidden_text, _ = self.simulator.hide(text)
        self.assertNotIn("xiaoming@example.com", hidden_text)
        self.assertIn("***@example.com", hidden_text)
    
    def test_hide_name(self):
        """测试姓名脱敏功能"""
        text = "王小明是一名软件工程师。"
        hidden_text, code_map = self.simulator.hide(text)
        # 验证原始姓名不在脱敏文本中
        self.assertNotIn("王小明", hidden_text)
        # 验证脱敏后的姓名是中文姓名
        for original, encoded in code_map.items():
            if original == "王小明":
                self.assertRegex(encoded, r"[\u4e00-\u9fa5]{2,4}")
                self.assertEqual(len(encoded), len(original))
                break
        else:
            self.fail("未找到姓名脱敏映射")
    
    def test_seek(self):
        """测试还原功能"""
        text = "王小明的手机号是13812345678，邮箱是xiaoming@example.com。"
        # 先执行脱敏
        hidden_text, _ = self.simulator.hide(text)
        # 再执行还原
        restored_text = self.simulator.seek(hidden_text)
        # 验证还原后的文本与原始文本一致
        self.assertEqual(restored_text, text)
    
    def test_process(self):
        """测试完整处理流程"""
        text = "王小明的手机号是13812345678，邮箱是xiaoming@example.com。"
        
        # 定义一个简单的模拟大模型函数
        def mock_llm(input_text):
            return f"处理结果：{input_text}\n这是额外生成的内容。"
        
        # 执行完整流程
        hidden, llm_result, restored = self.simulator.process(text, mock_llm)
        
        # 验证脱敏效果
        self.assertNotIn("13812345678", hidden)
        self.assertNotIn("xiaoming@example.com", hidden)
        
        # 验证大模型输出包含脱敏后的内容
        self.assertIn(hidden.strip(), llm_result)
        
        # 验证还原效果 - 由于大模型可能生成新内容，我们只验证原始信息是否正确还原
        self.assertIn("王小明", restored)
        self.assertIn("13812345678", restored)
        self.assertIn("xiaoming@example.com", restored)
    
    def test_complex_text(self):
        """测试复杂文本的脱敏和还原"""
        complex_text = """
        用户信息登记：
        姓名：王小明
        手机号：13812345678
        身份证号：110101199003079876
        邮箱：xiaoming@example.com
        地址：北京市海淀区中关村南大街5号
        
        备注：用户希望在下周一收到通知。
        """
        
        # 执行脱敏和还原
        hidden_text, _ = self.simulator.hide(complex_text)
        restored_text = self.simulator.seek(hidden_text)
        
        # 验证敏感信息被正确脱敏和还原
        self.assertNotIn("13812345678", hidden_text)
        self.assertNotIn("110101199003079876", hidden_text)
        self.assertNotIn("xiaoming@example.com", hidden_text)
        self.assertNotIn("王小明", hidden_text)
        
        # 验证还原后的文本与原始文本一致
        self.assertEqual(restored_text, complex_text)


# 演示文本替换功能，模拟HaS-820m模型的实体替换效果
def demonstrate_entity_replacement():
    """
    演示实体替换功能，模拟HaS-820m模型的行为
    """
    print("\n===== HaS-820m 实体替换演示 =====")
    
    # 示例文本，与原始test.py中的示例类似
    original_text = "张伟用苹果(iPhone 13)换了一箱好吃的苹果。"
    print(f"原始文本: {original_text}")
    
    # 使用我们的模拟器进行处理
    simulator = HideAndSeekSimulator()
    
    # 执行脱敏
    hidden_text, code_map = simulator.hide(original_text)
    print(f"脱敏后文本: {hidden_text}")
    print(f"脱敏映射: {code_map}")
    
    # 模拟大模型处理后的文本（模拟实体替换）
    # 这里我们手动模拟HaS-820m模型的实体替换效果
    def mock_has_model(text):
        # 模拟替换品牌、型号和物品
        replacements = {
            "苹果": "华为",
            "iPhone 13": "Mate 20",
            "好吃的苹果": "美味的橙子"
        }
        
        result = text
        for original, new in replacements.items():
            result = result.replace(original, new)
        return result
    
    # 模拟大模型处理
    llm_output = mock_has_model(hidden_text)
    print(f"模拟大模型输出: {llm_output}")
    
    # 执行还原
    restored_text = simulator.seek(llm_output)
    print(f"还原后文本: {restored_text}")
    print("\n注意：这是模拟效果，实际的HaS-820m模型会有更复杂的替换逻辑。")


if __name__ == "__main__":
    # 如果有命令行参数指定运行单元测试，则运行测试
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        unittest.main(argv=[sys.argv[0]])
    else:
        # 否则运行演示
        demonstrate_entity_replacement()
