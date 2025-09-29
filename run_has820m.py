from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from has_simulation import HideAndSeekSimulator

class HaS820mModel:
    """
    封装 HaS-820m 模型的加载和使用
    """
    def __init__(self, device=None):
        # 自动选择设备，如果有GPU则使用GPU
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"正在加载 HaS-820m 模型到 {self.device}...")
        
        # 加载模型和分词器
        self.tokenizer = AutoTokenizer.from_pretrained("SecurityXuanwuLab/HaS-820m")
        self.model = AutoModelForCausalLM.from_pretrained("SecurityXuanwuLab/HaS-820m").to(self.device)
        print("模型加载完成！")
    
    def generate(self, text: str, max_length: int = 100) -> str:
        """使用模型生成文本"""
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            output = self.model.generate(**inputs, max_length=max_length)
        result = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return result
    
    def paraphrase(self, text: str, max_length: int = 100) -> str:
        """使用模型进行文本改写/释义"""
        prompt = f"<s>Paraphrase the text:{text}\n\n"
        return self.generate(prompt, max_length)


def main():
    """
    腾讯实验室 HaS (Hide and Seek) 隐私保护技术的完整演示流程
    1. 初始化脱敏工具和模型
    2. 准备包含隐私信息的输入文本
    3. 执行脱敏操作（Hide阶段）
    4. 使用大模型处理脱敏后的文本
    5. 执行还原操作（Seek阶段）
    6. 比较原始文本和还原后的文本
    """
    # 初始化脱敏模拟器
    simulator = HideAndSeekSimulator()
    
    # 准备包含隐私信息的输入文本
    sensitive_input = """
    王小明的手机号是13812345678，身份证号为110101199003079876，
    他的邮箱是xiaoming@example.com。他最近购买了一部新手机。
    """
    
    print("===== 原始文本 =====")
    print(sensitive_input.strip())
    print()
    
    # 模拟本地终端脱敏处理（Hide阶段）
    hidden_text, code_map = simulator.hide(sensitive_input)
    print("===== 脱敏后文本 =====")
    print(hidden_text.strip())
    print()
    print("===== 脱敏映射关系 =====")
    for original, encoded in code_map.items():
        print(f"{original} -> {encoded}")
    print()
    
    try:
        # 初始化 HaS-820m 模型（这一步可能需要下载模型，如果网络受限可能会失败）
        model = HaS820mModel()
        
        # 使用大模型处理脱敏后的文本
        print("===== 调用大模型处理 =====")
        # 使用模型进行文本改写
        llm_output = model.paraphrase(hidden_text)
        print(llm_output)
        print()
        
        # 还原处理（Seek阶段）
        restored_text = simulator.seek(llm_output)
        print("===== 还原后文本 =====")
        print(restored_text)
        print()
        
        # 完整流程演示
        print("===== 完整流程演示 =====")
        # 定义一个模拟大模型的函数
        def mock_llm(text):
            # 这里只是简单示例，实际应该调用真正的大模型
            return f"[大模型处理结果]: {text}\n这是大模型生成的额外内容。"        
        
        # 执行完整流程
        hidden, llm_result, restored = simulator.process(sensitive_input, mock_llm)
        print("脱敏后:", hidden.strip())
        print("大模型输出:", llm_result.strip())
        print("还原后:", restored.strip())
    except Exception as e:
        print(f"\n注意：加载模型时发生错误: {e}")
        print("\n如果您无法访问Hugging Face或下载模型，可以使用以下简化版本进行测试：")
        
        # 简化版本：直接使用模拟的大模型函数
        def mock_llm_simple(text):
            return f"处理后的文本: {text}\n这是模拟的大模型输出。"
        
        # 执行完整流程
        hidden, llm_result, restored = simulator.process(sensitive_input, mock_llm_simple)
        print("脱敏后:", hidden.strip())
        print("模拟大模型输出:", llm_result.strip())
        print("还原后:", restored.strip())


if __name__ == "__main__":
    main()