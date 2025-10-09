import unittest
import time
import re
from has_entropy_sensitive_retrieval import (
    EntropyEnhancedSensitiveModel,
    EntropyEnhancedHaSWorkflow
)

class TestEntropyEnhancedSensitiveModel(unittest.TestCase):
    """测试增强版信息熵敏感词模型"""
    
    def setUp(self):
        """每个测试用例前的设置"""
        self.model = EntropyEnhancedSensitiveModel()
        # 配置模型参数以提高测试效率
        self.model.max_token_len = 32
        self.model.min_token_len = 2
    
    def test_char_entropy(self):
        """测试字符香农熵计算"""
        # 测试低熵文本（重复字符）
        low_entropy_text = "aaaaaaaaaa"
        low_entropy = self.model._char_entropy(low_entropy_text)
        self.assertAlmostEqual(low_entropy, 0.0, places=4)
        
        # 测试高熵文本（随机字符）
        high_entropy_text = "abcdefghij"
        high_entropy = self.model._char_entropy(high_entropy_text)
        self.assertGreater(high_entropy, 3.0)  # 理论上应该接近log2(10) ≈ 3.3219
    
    def test_ngram_entropy(self):
        """测试N-gram熵计算"""
        # 测试2-gram熵
        text = "abcabcabc"
        bigram_entropy = self.model._ngram_entropy(text, 2)
        # 文本中有3种2-gram: 'ab', 'bc', 'ca'
        self.assertAlmostEqual(bigram_entropy, 1.58496, places=5)  # log2(3) ≈ 1.58496
        
        # 测试3-gram熵
        trigram_entropy = self.model._ngram_entropy(text, 3)
        # 文本中有3种3-gram: 'abc', 'bca', 'cab'
        self.assertAlmostEqual(trigram_entropy, 1.58496, places=5)  # log2(3) ≈ 1.58496
    
    def test_tokenize_simple(self):
        """测试简单分词功能"""
        text = "腾讯科技(深圳)有限公司成立于1998年11月"
        tokens = self.model._tokenize_simple(text)
        expected_tokens = ["腾讯科技", "(", "深圳", ")", "有限公司成立于", "1998", "年", "11", "月"]
        self.assertEqual(tokens, expected_tokens)
    
    def test_regex_detect_sensitive(self):
        """测试正则表达式检测敏感信息"""
        # 测试手机号检测
        text = "我的联系电话是13800138000和13900139000"
        matches = self.model._regex_detect_sensitive(text)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]['type'], 'phone')
        self.assertEqual(matches[0]['text'], '13800138000')
        self.assertEqual(matches[1]['type'], 'phone')
        self.assertEqual(matches[1]['text'], '13900139000')
        
        # 测试身份证号检测
        text = "张三的身份证号是110101199001011234，李四的身份证号是110101199001011235"
        matches = self.model._regex_detect_sensitive(text)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]['type'], 'id')
        self.assertEqual(matches[1]['type'], 'id')
        
        # 测试邮箱检测
        text = "我的邮箱是zhangsan@example.com和lisi@test.com"
        matches = self.model._regex_detect_sensitive(text)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]['type'], 'email')
        self.assertEqual(matches[1]['type'], 'email')
    
    def test_detect_sensitive_info(self):
        """测试综合检测敏感信息"""
        text = "张三（身份证号：110101199001011234）是腾讯科技(深圳)有限公司的CEO，联系电话是13800138000，邮箱是zhangsan@example.com"
        
        # 检测敏感信息
        sensitive_info = self.model.detect_sensitive_info(text)
        
        # 应该至少检测到：姓名、身份证号、公司、职位、电话、邮箱
        detected_types = set([info['type'] for info in sensitive_info])
        self.assertIn('name', detected_types)
        self.assertIn('id', detected_types)
        self.assertIn('company', detected_types)
        self.assertIn('position', detected_types)
        self.assertIn('phone', detected_types)
        self.assertIn('email', detected_types)
        
        # 验证至少有6个敏感信息
        self.assertGreaterEqual(len(sensitive_info), 6)
    
    def test_desensitize_placeholder(self):
        """测试使用占位符进行脱敏"""
        text = "张三的联系电话是13800138000，邮箱是zhangsan@example.com"
        desensitized_text, mapping, session_id = self.model.desensitize(text, strategy='placeholder')
        
        # 验证脱敏结果
        self.assertIn('<name_1>', desensitized_text)
        self.assertIn('<phone_1>', desensitized_text)
        self.assertIn('<email_1>', desensitized_text)
        
        # 验证映射关系
        self.assertEqual(mapping['<name_1>'], '张三')
        self.assertEqual(mapping['<phone_1>'], '13800138000')
        self.assertEqual(mapping['<email_1>'], 'zhangsan@example.com')
        
        # 验证会话ID不为空
        self.assertIsNotNone(session_id)
    
    def test_desensitize_pseudonymization(self):
        """测试使用假名化进行脱敏"""
        text = "张三的联系电话是13800138000，邮箱是zhangsan@example.com"
        desensitized_text, mapping, session_id = self.model.desensitize(text, strategy='pseudonymization')
        
        # 验证脱敏结果不包含原始敏感信息
        self.assertNotIn('张三', desensitized_text)
        self.assertNotIn('13800138000', desensitized_text)
        
        # 验证映射关系结构正确
        for key, value in mapping.items():
            if key.startswith('<PSEUDO_name'):
                self.assertIsInstance(value, tuple)
                self.assertEqual(len(value), 2)
                # 验证生成的姓名长度与原始相同
                self.assertEqual(len(value[0]), len(value[1]))
            elif key.startswith('<PSEUDO_phone'):
                self.assertIsInstance(value, tuple)
                self.assertEqual(len(value), 2)
                # 验证生成的手机号格式正确
                self.assertTrue(re.match(r'1[3-9]\d{9}', value[0]))
    
    def test_restore(self):
        """测试还原脱敏后的文本"""
        original_text = "张三的联系电话是13800138000，邮箱是zhangsan@example.com"
        
        # 先进行脱敏
        desensitized_text, mapping, session_id = self.model.desensitize(original_text, strategy='placeholder')
        
        # 再进行还原
        restored_text = self.model.restore(desensitized_text, mapping)
        
        # 验证还原后的文本与原始文本相同
        self.assertEqual(restored_text, original_text)
    
    def test_session_management(self):
        """测试会话管理功能"""
        # 创建多个会话
        session_ids = []
        for i in range(5):
            text = f"测试文本{i}，联系电话是1380013800{i}"
            _, _, session_id = self.model.desensitize(text)
            session_ids.append(session_id)
        
        # 验证所有会话都被保存
        for session_id in session_ids:
            self.assertIn(session_id, self.model.sessions)
        
        # 测试获取会话映射
        for session_id in session_ids:
            mapping = self.model.get_session_mapping(session_id)
            self.assertIsInstance(mapping, dict)

class TestEntropyEnhancedHaSWorkflow(unittest.TestCase):
    """测试增强版HaS工作流"""
    
    def setUp(self):
        """每个测试用例前的设置"""
        self.workflow = EntropyEnhancedHaSWorkflow()
    
    def test_configure(self):
        """测试配置工作流"""
        # 配置参数
        config = {
            'sensitive_types': ['name', 'phone', 'email'],
            'desensitization_strategy': 'pseudonymization',
            'enable_entropy_detection': False
        }
        
        # 应用配置
        self.workflow.configure(**config)
        
        # 验证配置是否生效
        self.assertEqual(self.workflow.config['sensitive_types'], ['name', 'phone', 'email'])
        self.assertEqual(self.workflow.config['desensitization_strategy'], 'pseudonymization')
        self.assertFalse(self.workflow.config['enable_entropy_detection'])
        self.assertFalse(self.workflow.endside_model.enable_entropy_detection)
    
    def test_run_desensitization(self):
        """测试运行脱敏流程"""
        text = "张三的联系电话是13800138000，邮箱是zhangsan@example.com"
        result = self.workflow.run_desensitization(text)
        
        # 验证结果结构
        self.assertIn('desensitized_text', result)
        self.assertIn('session_id', result)
        self.assertIn('mapping', result)
        self.assertIn('num_sensitive', result)
        
        # 验证脱敏结果
        self.assertIn('<name_1>', result['desensitized_text'])
        self.assertIn('<phone_1>', result['desensitized_text'])
        self.assertIn('<email_1>', result['desensitized_text'])
        
        # 验证敏感信息数量
        self.assertEqual(result['num_sensitive'], 3)
        
        # 验证当前会话信息
        self.assertEqual(self.workflow.current_session_id, result['session_id'])
        self.assertEqual(self.workflow.current_mapping, result['mapping'])
    
    def test_run_restore(self):
        """测试运行还原流程"""
        original_text = "张三的联系电话是13800138000，邮箱是zhangsan@example.com"
        
        # 先进行脱敏
        desensitization_result = self.workflow.run_desensitization(original_text)
        desensitized_text = desensitization_result['desensitized_text']
        session_id = desensitization_result['session_id']
        mapping = desensitization_result['mapping']
        
        # 模拟大模型处理后的输出
        llm_output = f"处理结果：{desensitized_text}\n这是生成的额外内容。"
        
        # 进行还原
        restore_result = self.workflow.run_restore(llm_output, session_id, mapping)
        
        # 验证结果结构
        self.assertIn('restored_text', restore_result)
        self.assertIn('session_id', restore_result)
        
        # 验证还原后的文本包含原始敏感信息
        self.assertIn('张三', restore_result['restored_text'])
        self.assertIn('13800138000', restore_result['restored_text'])
        self.assertIn('zhangsan@example.com', restore_result['restored_text'])
    
    def test_run_complete_workflow(self):
        """测试运行完整的工作流"""
        original_text = "张三的联系电话是13800138000，邮箱是zhangsan@example.com"
        
        # 运行完整工作流
        result = self.workflow.run_complete_workflow(original_text)
        
        # 验证结果结构
        self.assertIn('original_text', result)
        self.assertIn('desensitized_text', result)
        self.assertIn('llm_output', result)
        self.assertIn('restored_text', result)
        self.assertIn('session_id', result)
        self.assertIn('num_sensitive', result)
        self.assertIn('processing_time', result)
        
        # 验证还原后的文本包含原始敏感信息
        self.assertIn('张三', result['restored_text'])
        self.assertIn('13800138000', result['restored_text'])
        self.assertIn('zhangsan@example.com', result['restored_text'])
        
        # 验证处理时间是有效的
        self.assertGreater(result['processing_time'], 0)

class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def setUp(self):
        """每个测试用例前的设置"""
        self.model = EntropyEnhancedSensitiveModel()
        self.workflow = EntropyEnhancedHaSWorkflow()
    
    def test_detection_performance(self):
        """测试敏感信息检测性能"""
        # 准备测试数据
        test_text = """这是一份包含多个敏感信息的测试文本。
姓名：张三、李四、王五、赵六、钱七、孙八、周九、吴十。
电话：13800138000、13900139000、13700137000、13600136000、13500135000。
邮箱：zhangsan@example.com、lisi@example.com、wangwu@example.com、zhaoliu@example.com、qianqi@example.com。
身份证号：110101199001011234、110101199001011235、110101199001011236、110101199001011237、110101199001011238。
公司：腾讯科技(深圳)有限公司、阿里巴巴(中国)网络技术有限公司、百度在线网络技术(北京)有限公司、华为技术有限公司、字节跳动有限公司。
"""
        
        # 记录开始时间
        start_time = time.time()
        
        # 执行检测
        sensitive_info = self.model.detect_sensitive_info(test_text)
        
        # 记录结束时间
        end_time = time.time()
        
        # 计算处理时间
        processing_time = end_time - start_time
        
        # 打印性能信息
        print(f"\n=== 检测性能测试 ===")
        print(f"文本长度: {len(test_text)} 字符")
        print(f"识别到的敏感信息数量: {len(sensitive_info)}")
        print(f"处理时间: {processing_time:.4f} 秒")
        print(f"每秒处理字符数: {len(test_text) / processing_time:.2f} 字符/秒")
        
        # 验证处理时间在合理范围内（对于普通计算机，处理这样的文本应该在1秒以内）
        self.assertLess(processing_time, 1.0)
        
        # 验证识别到的敏感信息数量
        self.assertGreaterEqual(len(sensitive_info), 20)  # 应该至少识别到20个敏感信息
    
    def test_workflow_performance(self):
        """测试完整工作流性能"""
        # 准备测试数据
        test_text = """这是一份包含多个敏感信息的测试文本。
姓名：张三、李四、王五。
电话：13800138000、13900139000。
邮箱：zhangsan@example.com、lisi@example.com。
身份证号：110101199001011234、110101199001011235。
公司：腾讯科技(深圳)有限公司、阿里巴巴(中国)网络技术有限公司。
"""
        
        # 记录开始时间
        start_time = time.time()
        
        # 执行完整工作流
        result = self.workflow.run_complete_workflow(test_text)
        
        # 记录结束时间
        end_time = time.time()
        
        # 计算处理时间
        processing_time = end_time - start_time
        
        # 打印性能信息
        print(f"\n=== 完整工作流性能测试 ===")
        print(f"文本长度: {len(test_text)} 字符")
        print(f"识别到的敏感信息数量: {result['num_sensitive']}")
        print(f"工作流报告的处理时间: {result['processing_time']:.4f} 秒")
        print(f"实际测试的处理时间: {processing_time:.4f} 秒")
        print(f"每秒处理字符数: {len(test_text) / processing_time:.2f} 字符/秒")
        
        # 验证处理时间在合理范围内
        self.assertLess(processing_time, 1.0)
        
        # 验证识别到的敏感信息数量
        self.assertGreaterEqual(result['num_sensitive'], 10)  # 应该至少识别到10个敏感信息

# 批量测试函数
def batch_test():
    """批量测试函数，用于验证系统在多种场景下的性能和准确性"""
    print("\n=== HaS隐私保护技术 - 增强版信息熵敏感词检索系统 批量测试 ===")
    
    # 创建工作流实例
    workflow = EntropyEnhancedHaSWorkflow()
    
    # 测试用例
    test_cases = [
        {
            "name": "个人信息",
            "text": "我叫张三，身份证号码是110101199001011234，联系电话是13800138000，邮箱是zhangsan@example.com，今年30岁，住在北京市海淀区中关村南大街5号。"
        },
        {
            "name": "金融信息",
            "text": "客户王小明的银行卡号是6222020200012345678，账户余额为123,456.78元，信用额度提升了20%，达到了50,000元。"
        },
        {
            "name": "企业信息",
            "text": "腾讯科技(深圳)有限公司的CEO是马化腾，位于深圳市南山区海天二路33号腾讯滨海大厦，成立于1998年11月11日。阿里巴巴(中国)网络技术有限公司的创始人是马云，总部位于杭州市余杭区文一西路969号。"
        },
        {
            "name": "网络安全",
            "text": "服务器IP地址是192.168.1.1，管理员账号是admin，密码是Admin@123，端口号是8080。备份服务器的IP是192.168.1.2，账号是backup。"
        },
        {
            "name": "混合信息",
            "text": "李华是百度在线网络技术(北京)有限公司的技术总监，联系电话是13700137000，邮箱是lihua@baidu.com。他的身份证号是110101198501011234，银行卡号是6228480010000000000，今年35岁，住在北京市海淀区西二旗大街39号。"
        }
    ]
    
    # 执行测试
    total_time = 0
    total_sensitive = 0
    
    print("\n=== 测试用例结果 ===")
    
    for i, test_case in enumerate(test_cases):
        print(f"\n测试用例 {i+1}/{len(test_cases)}: {test_case['name']}")
        print(f"文本长度: {len(test_case['text'])} 字符")
        
        start_time = time.time()
        
        try:
            # 执行完整工作流
            result = workflow.run_complete_workflow(test_case['text'])
            
            processing_time = time.time() - start_time
            total_time += processing_time
            total_sensitive += result['num_sensitive']
            
            # 打印测试结果
            print(f"识别到的敏感信息数量: {result['num_sensitive']}")
            print(f"处理时间: {processing_time:.4f} 秒")
            print(f"每秒处理字符数: {len(test_case['text']) / processing_time:.2f} 字符/秒")
            
            # 显示脱敏示例
            print(f"脱敏示例: {result['desensitized_text'][:100]}{'...' if len(result['desensitized_text']) > 100 else ''}")
            
        except Exception as e:
            print(f"测试失败: {str(e)}")
    
    # 打印汇总信息
    print("\n=== 测试汇总 ===")
    print(f"总测试用例数: {len(test_cases)}")
    print(f"识别到的敏感信息总数: {total_sensitive}")
    print(f"平均处理时间: {total_time / len(test_cases):.4f} 秒")
    print(f"总处理时间: {total_time:.4f} 秒")
    print(f"平均每秒处理字符数: {sum(len(case['text']) for case in test_cases) / total_time:.2f} 字符/秒")
    print("\n=== 批量测试结束 ===")

# 运行测试
if __name__ == "__main__":
    # 运行单元测试
    print("=== 运行单元测试 ===")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    # 运行批量测试
    print("\n=== 运行批量测试 ===")
    batch_test()