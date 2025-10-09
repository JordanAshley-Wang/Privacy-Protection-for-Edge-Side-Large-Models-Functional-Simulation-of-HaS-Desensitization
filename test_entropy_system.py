#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HaS (Hide and Seek) 隐私保护技术 - 增强版信息熵敏感词检索系统测试文件
包含单元测试和集成测试，验证系统各功能模块的正确性
"""

import unittest
import re
import time
from has_entropy_sensitive_retrieval import EntropyEnhancedSensitiveModel, EntropyEnhancedHaSWorkflow

class TestEntropySensitiveModel(unittest.TestCase):
    """测试增强版信息熵敏感词检测模型"""
    
    def setUp(self):
        """每个测试用例前的设置"""
        self.model = EntropyEnhancedSensitiveModel()
    
    def test_char_entropy(self):
        """测试字符熵计算功能"""
        # 测试低熵文本（重复字符）
        self.assertLess(self.model._char_entropy("aaaaa"), 0.5)
        
        # 测试中熵文本（有一定变化的字符）
        entropy_abc = self.model._char_entropy("abcde")
        self.assertGreater(entropy_abc, 2.0)
        self.assertLess(entropy_abc, 3.0)
        
        # 测试高熵文本（随机字符）
        entropy_random = self.model._char_entropy("a1b2c3d4")
        self.assertGreater(entropy_random, 2.5)
    
    def test_ngram_entropy(self):
        """测试N-gram熵计算功能"""
        # 测试低熵文本（重复模式）
        self.assertLess(self.model._ngram_entropy("ababab", 2), 1.0)
        
        # 测试高熵文本（随机模式）
        entropy = self.model._ngram_entropy("abcdef", 2)
        self.assertGreater(entropy, 2.0)
    
    def test_tokenize_simple(self):
        """测试简易分词功能"""
        text = "你好123world!"
        tokens = self.model._tokenize_simple(text)
        
        # 应该分为4个部分：中文、数字、英文、标点符号
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[0][2], "你好")
        self.assertEqual(tokens[0][3], "han")
        self.assertEqual(tokens[1][2], "123")
        self.assertEqual(tokens[1][3], "alnum")
        self.assertEqual(tokens[2][2], "world")
        self.assertEqual(tokens[2][3], "alnum")
        self.assertEqual(tokens[3][2], "!")
        self.assertEqual(tokens[3][3], "other")
    
    def test_entropy_detect_candidates(self):
        """测试基于信息熵的敏感候选检索功能"""
        text = "我叫张三，是恒信科技有限公司的经理。"
        candidates = self.model._entropy_detect_candidates(text)
        
        # 应该检测到姓名和公司名称
        detected_types = [c[2] for c in candidates]
        self.assertIn("name", detected_types)
        self.assertIn("company", detected_types)
    
    def test_regex_based_detection(self):
        """测试基于正则表达式的敏感信息检测功能"""
        text = "我的手机号是13812345678，邮箱是test@example.com。"
        candidates = self.model._regex_based_detection(text)
        
        # 应该检测到手机号和邮箱
        detected_types = [c[2] for c in candidates]
        self.assertIn("phone", detected_types)
        self.assertIn("email", detected_types)
    
    def test_desensitize(self):
        """测试脱敏功能"""
        text = "你好，我叫王小明，我的手机号是13812345678，请帮我查询一下。"
        desensitized_text, mapping = self.model.desensitize(text)
        
        # 验证脱敏后文本不包含原始敏感信息
        self.assertNotIn("王小明", desensitized_text)
        self.assertNotIn("13812345678", desensitized_text)
        
        # 验证映射关系正确建立
        self.assertTrue(len(mapping) > 0)
        
        # 验证脱敏标记格式正确（标准占位符）
        placeholder_pattern = r'<\w+>_\d+'
        self.assertTrue(re.search(placeholder_pattern, desensitized_text) is not None)
    
    def test_restore(self):
        """测试还原功能"""
        text = "你好，我叫王小明，我的手机号是13812345678，请帮我查询一下。"
        desensitized_text, _ = self.model.desensitize(text)
        restored_text = self.model.restore(desensitized_text)
        
        # 验证还原后的文本与原始文本基本一致
        # 注意：由于脱敏标记可能有位置偏移，这里只验证关键信息
        self.assertIn("王小明", restored_text)
        self.assertIn("13812345678", restored_text)

class TestEntropyHaSWorkflow(unittest.TestCase):
    """测试增强版信息熵敏感词检索工作流"""
    
    def setUp(self):
        """每个测试用例前的设置"""
        self.workflow = EntropyEnhancedHaSWorkflow()
    
    def test_configure_desensitization_strategy(self):
        """测试配置脱敏策略功能"""
        # 配置标准占位符策略
        self.workflow.configure_desensitization_strategy(
            enable_entity_placeholder=True,
            enable_pseudonymization=False,
            enable_anonimization=False,
            enable_generalization=False
        )
        
        # 验证配置是否正确应用
        self.assertTrue(self.workflow.config['enable_entity_placeholder'])
        self.assertFalse(self.workflow.config['enable_pseudonymization'])
        self.assertFalse(self.workflow.config['enable_anonimization'])
        self.assertFalse(self.workflow.config['enable_generalization'])
        
        # 配置假名化策略
        self.workflow.configure_desensitization_strategy(
            enable_pseudonymization=True,
            enable_anonimization=False,
            enable_generalization=False
        )
        
        # 验证配置是否正确应用
        self.assertTrue(self.workflow.config['enable_pseudonymization'])
    
    def test_configure_endside_model(self):
        """测试配置端侧模型功能"""
        # 配置模型参数
        self.workflow.configure_endside_model(
            entropy_threshold=1.5,
            enable_entropy_detection=True,
            max_token_len=48
        )
        
        # 验证配置是否正确应用
        self.assertEqual(self.workflow.config['entropy_threshold'], 1.5)
        self.assertTrue(self.workflow.config['enable_entropy_detection'])
        self.assertEqual(self.workflow.config['max_token_len'], 48)
        
        # 验证模型配置是否同步更新
        self.assertEqual(self.workflow.endside_model.config['entropy_threshold'], 1.5)
    
    def test_run_workflow(self):
        """测试完整工作流功能"""
        text = "我叫李华，在远大科技有限公司工作，手机号是13987654321。"
        result = self.workflow.run(text)
        
        # 验证结果包含所有必要字段
        self.assertIn('desensitized_text', result)
        self.assertIn('llm_text', result)
        self.assertIn('restored_text', result)
        self.assertIn('mapping', result)
        self.assertIn('timing', result)
        
        # 验证脱敏和还原过程
        self.assertNotIn('李华', result['desensitized_text'])
        self.assertIn('李华', result['restored_text'])
        self.assertNotIn('13987654321', result['desensitized_text'])
        self.assertIn('13987654321', result['restored_text'])

class TestPerformance(unittest.TestCase):
    """测试系统性能"""
    
    def test_performance_basic(self):
        """测试基本性能指标"""
        model = EntropyEnhancedSensitiveModel()
        text = "这是一个包含敏感信息的测试文本。我叫张三，电话是13812345678，身份证号是110101199001011234。"
        
        # 测试脱敏速度
        start_time = time.time()
        desensitized_text, _ = model.desensitize(text)
        desensitize_time = time.time() - start_time
        
        # 测试还原速度
        start_time = time.time()
        restored_text = model.restore(desensitized_text)
        restore_time = time.time() - start_time
        
        # 在普通计算机上，这些操作应该非常快（毫秒级）
        print(f"\n性能测试结果：")
        print(f"脱敏耗时: {desensitize_time*1000:.2f}毫秒")
        print(f"还原耗时: {restore_time*1000:.2f}毫秒")
        
        # 对于低配置环境，确保操作在可接受的时间内完成
        self.assertLess(desensitize_time, 0.5)  # 小于0.5秒
        self.assertLess(restore_time, 0.1)      # 小于0.1秒

class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_integration_complete_flow(self):
        """测试完整的脱敏还原流程"""
        # 创建工作流实例
        workflow = EntropyEnhancedHaSWorkflow()
        
        # 测试文本
        original_text = "用户王五的身份证号是440101199003071234，手机号码是13712345678，邮箱是wangwu@company.com，银行卡号是6222021234567890123。"
        
        # 执行脱敏
        desensitized_text, mapping = workflow.endside_model.desensitize(original_text)
        
        # 模拟大模型处理（简单修改文本）
        llm_processed_text = f"处理结果：根据{desensitized_text}中的信息，我们可以提供相应的服务。"
        
        # 执行还原
        restored_text = workflow.endside_model.restore(llm_processed_text)
        
        # 验证结果
        print(f"\n集成测试结果：")
        print(f"原始文本: {original_text}")
        print(f"脱敏后文本: {desensitized_text}")
        print(f"大模型处理后: {llm_processed_text}")
        print(f"还原后文本: {restored_text}")
        
        # 检查敏感信息是否正确还原
        self.assertIn("王五", restored_text)
        self.assertIn("440101199003071234", restored_text)
        self.assertIn("13712345678", restored_text)
        self.assertIn("wangwu@company.com", restored_text)
        self.assertIn("6222021234567890123", restored_text)

# 测试不同场景下的系统表现
def scenario_test():
    """场景测试"""
    print("\n===== HaS 隐私保护技术 - 场景测试 =====")
    
    # 创建工作流实例
    workflow = EntropyEnhancedHaSWorkflow()
    
    # 定义测试场景
    scenarios = [
        {
            "name": "个人信息场景",
            "text": "你好，我叫王小明，今年28岁，我的手机号是13812345678，身份证号是110101199003079876，住在北京市朝阳区建国路88号。"
        },
        {
            "name": "金融信息场景",
            "text": "客户张三在我行开立的银行卡号为6222 1234 5678 9012，最近一笔交易金额为15800元，发生在2023年6月15日。"
        },
        {
            "name": "企业信息场景",
            "text": "我是李明，担任恒信科技有限公司技术部总监，我们公司的邮箱是contact@hengxin-tech.com，联系电话是010-87654321。"
        },
        {
            "name": "网络安全场景",
            "text": "服务器的IP地址是192.168.1.100，访问端口是8080，管理员账号是admin，临时密码是Temp@2023!。"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n----- 场景: {scenario['name']} -----")
        
        # 执行脱敏
        desensitized_text, mapping = workflow.endside_model.desensitize(scenario['text'])
        
        # 打印结果
        print(f"原始文本: {scenario['text']}")
        print(f"脱敏后文本: {desensitized_text}")
        print(f"识别到的敏感信息数量: {len(mapping)}")
        print(f"敏感信息类型: {set([key.split('_')[0].strip('<') for key in mapping.keys() if key.startswith('<')])}")

if __name__ == "__main__":
    # 运行单元测试
    print("运行单元测试...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    # 运行场景测试
    print("\n运行场景测试...")
    scenario_test()
    
    print("\n所有测试完成！")