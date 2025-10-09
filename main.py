import sys
import os
import time
import logging
from has_entropy_sensitive_retrieval import EntropyEnhancedHaSWorkflow

# 配置日志
def setup_logger():
    """配置日志记录器"""
    logger = logging.getLogger('has_privacy_system')
    logger.setLevel(logging.INFO)
    
    # 检查日志目录是否存在，如果不存在则创建
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建文件处理器
    log_file = os.path.join(log_dir, f'has_system_{time.strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 主程序类
class HaSPrivacySystem:
    def __init__(self):
        """初始化HaS隐私保护系统"""
        # 设置日志
        self.logger = setup_logger()
        self.logger.info("=== HaS隐私保护技术 - 增强版信息熵敏感词检索系统 启动 ===")
        
        # 初始化工作流
        self.workflow = EntropyEnhancedHaSWorkflow()
        
        # 加载配置
        self.load_config()
        
        # 记录系统信息
        self.logger.info("系统初始化完成")
        self.logger.info(f"敏感信息检测类型: {', '.join(self.workflow.config['sensitive_types'])}")
        self.logger.info(f"脱敏策略: {self.workflow.config['desensitization_strategy']}")
        self.logger.info(f"启用熵检测: {self.workflow.config['enable_entropy_detection']}")
        self.logger.info(f"启用位置熵: {self.workflow.config['enable_position_entropy']}")
    
    def load_config(self):
        """加载系统配置"""
        # 这里可以根据需要从配置文件加载参数
        # 当前使用默认配置，可以根据实际需求修改
        config = {
            'sensitive_types': ['name', 'company', 'position', 'phone', 'id', 'email', 
                              'bank_card', 'amount', 'performance', 'age', 'address', 
                              'zipcode', 'ip', 'account', 'department'],
            'desensitization_strategy': 'placeholder',  # placeholder, pseudonymization, anonymization, generalization
            'enable_entropy_detection': True,
            'enable_position_entropy': True,
            'entropy_threshold': 1.2,
            'high_entropy_threshold': 3.5,
            'max_token_len': 64,
            'min_token_len': 2
        }
        
        # 应用配置
        self.workflow.configure(**config)
    
    def process_text(self, text, mode='complete'):
        """处理文本
        mode: 'complete' - 完整的脱敏-处理-还原流程
              'desensitize' - 仅执行脱敏处理
              'restore' - 仅执行还原处理
        """
        try:
            if mode == 'complete':
                self.logger.info(f"执行完整工作流，文本长度: {len(text)}字符")
                result = self.workflow.run_complete_workflow(text)
                
                # 记录处理结果
                self.logger.info(f"处理完成，识别敏感信息: {result['num_sensitive']}个")
                self.logger.info(f"处理时间: {result['processing_time']:.4f}秒")
                
                return result
                
            elif mode == 'desensitize':
                self.logger.info(f"执行脱敏处理，文本长度: {len(text)}字符")
                result = self.workflow.run_desensitization(text)
                
                # 记录脱敏结果
                self.logger.info(f"脱敏完成，识别敏感信息: {result['num_sensitive']}个")
                
                return result
                
            elif mode == 'restore':
                # 还原处理需要额外的参数
                self.logger.info("执行还原处理")
                # 注意：这里需要调用者提供session_id和llm_output
                # 此方法主要用于API调用
                raise NotImplementedError("还原处理需要单独调用run_restore方法")
                
            else:
                self.logger.error(f"不支持的处理模式: {mode}")
                raise ValueError(f"不支持的处理模式: {mode}")
                
        except Exception as e:
            self.logger.error(f"处理文本时出错: {str(e)}")
            raise
    
    def process_file(self, input_file, output_file=None):
        """处理文件"""
        try:
            # 检查输入文件是否存在
            if not os.path.exists(input_file):
                self.logger.error(f"输入文件不存在: {input_file}")
                raise FileNotFoundError(f"输入文件不存在: {input_file}")
            
            # 读取文件内容
            self.logger.info(f"开始处理文件: {input_file}")
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # 处理文本
            result = self.process_text(text, mode='complete')
            
            # 确定输出文件路径
            if output_file is None:
                # 默认在输入文件名后添加_processed后缀
                file_name, file_ext = os.path.splitext(input_file)
                output_file = f"{file_name}_processed{file_ext}"
            
            # 写入结果到输出文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"=== 原始文本 ===\n{result['original_text']}\n\n")
                f.write(f"=== 脱敏后文本 ===\n{result['desensitized_text']}\n\n")
                f.write(f"=== 模拟大模型输出 ===\n{result['llm_output']}\n\n")
                f.write(f"=== 还原后文本 ===\n{result['restored_text']}\n\n")
                f.write(f"=== 处理统计信息 ===\n")
                f.write(f"识别到的敏感信息数量: {result['num_sensitive']}\n")
                f.write(f"会话ID: {result['session_id']}\n")
                f.write(f"处理时间: {result['processing_time']:.4f}秒\n")
            
            self.logger.info(f"处理结果已保存到: {output_file}")
            
            return {
                'output_file': output_file,
                'session_id': result['session_id'],
                'num_sensitive': result['num_sensitive'],
                'processing_time': result['processing_time']
            }
            
        except Exception as e:
            self.logger.error(f"处理文件时出错: {str(e)}")
            raise
    
    def interactive_mode(self):
        """交互模式"""
        print("\n=== HaS隐私保护技术 - 增强版信息熵敏感词检索系统 ===")
        print("欢迎使用交互式界面，您可以选择以下操作：")
        
        while True:
            print("\n--- 主菜单 ---")
            print("1. 处理文本")
            print("2. 处理文件")
            print("3. 显示系统配置")
            print("4. 退出系统")
            
            choice = input("请输入您的选择 (1-4): ")
            
            if choice == '1':
                self._handle_text_processing()
            elif choice == '2':
                self._handle_file_processing()
            elif choice == '3':
                self._show_system_config()
            elif choice == '4':
                self.logger.info("=== HaS隐私保护技术 - 增强版信息熵敏感词检索系统 关闭 ===")
                print("感谢使用，再见！")
                break
            else:
                print("无效的选择，请重新输入。")
    
    def _handle_text_processing(self):
        """处理文本的交互逻辑"""
        print("\n--- 文本处理 ---")
        print("请选择处理模式：")
        print("1. 完整的脱敏-处理-还原流程")
        print("2. 仅执行脱敏处理")
        
        mode_choice = input("请输入您的选择 (1-2): ")
        
        if mode_choice == '1':
            text = input("请输入要处理的文本: ")
            print("正在处理...")
            
            try:
                result = self.process_text(text, mode='complete')
                
                print("\n=== 处理结果 ===")
                print(f"原始文本: {result['original_text']}")
                print(f"脱敏后: {result['desensitized_text']}")
                print(f"模拟大模型输出: {result['llm_output']}")
                print(f"还原后: {result['restored_text']}")
                print(f"识别到的敏感信息数量: {result['num_sensitive']}")
                print(f"会话ID: {result['session_id']}")
                print(f"处理时间: {result['processing_time']:.4f}秒")
                
            except Exception as e:
                print(f"处理文本时出错: {str(e)}")
                
        elif mode_choice == '2':
            text = input("请输入要脱敏的文本: ")
            print("正在脱敏...")
            
            try:
                result = self.process_text(text, mode='desensitize')
                
                print("\n=== 脱敏结果 ===")
                print(f"脱敏后: {result['desensitized_text']}")
                print(f"识别到的敏感信息数量: {result['num_sensitive']}")
                print(f"会话ID: {result['session_id']}")
                print("请保存会话ID，用于后续的还原处理。")
                
            except Exception as e:
                print(f"脱敏文本时出错: {str(e)}")
                
        else:
            print("无效的选择，返回主菜单。")
    
    def _handle_file_processing(self):
        """处理文件的交互逻辑"""
        print("\n--- 文件处理 ---")
        
        input_file = input("请输入要处理的文件路径: ")
        output_file = input("请输入输出文件路径 (可选，直接回车使用默认路径): ")
        
        if not output_file.strip():
            output_file = None
            
        print(f"正在处理文件: {input_file}")
        
        try:
            result = self.process_file(input_file, output_file)
            
            print("\n=== 文件处理结果 ===")
            print(f"处理结果已保存到: {result['output_file']}")
            print(f"识别到的敏感信息数量: {result['num_sensitive']}")
            print(f"会话ID: {result['session_id']}")
            print(f"处理时间: {result['processing_time']:.4f}秒")
            
        except Exception as e:
            print(f"处理文件时出错: {str(e)}")
    
    def _show_system_config(self):
        """显示系统配置"""
        print("\n--- 系统配置 ---")
        print(f"敏感信息检测类型: {', '.join(self.workflow.config['sensitive_types'])}")
        print(f"脱敏策略: {self.workflow.config['desensitization_strategy']}")
        print(f"启用熵检测: {self.workflow.config['enable_entropy_detection']}")
        print(f"启用位置熵: {self.workflow.config['enable_position_entropy']}")
        print(f"熵阈值: {self.workflow.config['entropy_threshold']}")
        print(f"高熵阈值: {self.workflow.config['high_entropy_threshold']}")
        print(f"最大token长度: {self.workflow.config['max_token_len']}")
        print(f"最小token长度: {self.workflow.config['min_token_len']}")

# 命令行接口函数
def cli():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HaS隐私保护技术 - 增强版信息熵敏感词检索系统')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 交互模式命令
    subparsers.add_parser('interactive', help='启动交互式界面')
    
    # 处理文本命令
    text_parser = subparsers.add_parser('text', help='处理文本')
    text_parser.add_argument('--input', '-i', required=True, help='输入文本')
    text_parser.add_argument('--mode', '-m', choices=['complete', 'desensitize'], default='complete', help='处理模式')
    text_parser.add_argument('--output', '-o', help='输出文件路径')
    
    # 处理文件命令
    file_parser = subparsers.add_parser('file', help='处理文件')
    file_parser.add_argument('--input', '-i', required=True, help='输入文件路径')
    file_parser.add_argument('--output', '-o', help='输出文件路径')
    
    # 显示配置命令
    subparsers.add_parser('config', help='显示系统配置')
    
    # 解析参数
    args = parser.parse_args()
    
    # 创建系统实例
    system = HaSPrivacySystem()
    
    # 根据命令执行相应操作
    if args.command == 'interactive':
        system.interactive_mode()
        
    elif args.command == 'text':
        try:
            result = system.process_text(args.input, mode=args.mode)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    if args.mode == 'complete':
                        f.write(f"=== 原始文本 ===\n{result['original_text']}\n\n")
                        f.write(f"=== 脱敏后文本 ===\n{result['desensitized_text']}\n\n")
                        f.write(f"=== 模拟大模型输出 ===\n{result['llm_output']}\n\n")
                        f.write(f"=== 还原后文本 ===\n{result['restored_text']}\n\n")
                    else:
                        f.write(f"=== 脱敏后文本 ===\n{result['desensitized_text']}\n\n")
                    
                    f.write(f"=== 处理统计信息 ===\n")
                    f.write(f"识别到的敏感信息数量: {result['num_sensitive']}\n")
                    f.write(f"会话ID: {result['session_id']}\n")
                    
                print(f"处理结果已保存到: {args.output}")
                
            else:
                # 输出到控制台
                if args.mode == 'complete':
                    print("\n=== 处理结果 ===")
                    print(f"原始文本: {result['original_text']}")
                    print(f"脱敏后: {result['desensitized_text']}")
                    print(f"模拟大模型输出: {result['llm_output']}")
                    print(f"还原后: {result['restored_text']}")
                else:
                    print("\n=== 脱敏结果 ===")
                    print(f"脱敏后: {result['desensitized_text']}")
                    
                print(f"识别到的敏感信息数量: {result['num_sensitive']}")
                print(f"会话ID: {result['session_id']}")
                
        except Exception as e:
            print(f"处理文本时出错: {str(e)}")
            sys.exit(1)
            
    elif args.command == 'file':
        try:
            result = system.process_file(args.input, args.output)
            print(f"\n=== 文件处理结果 ===")
            print(f"处理结果已保存到: {result['output_file']}")
            print(f"识别到的敏感信息数量: {result['num_sensitive']}")
            print(f"会话ID: {result['session_id']}")
            print(f"处理时间: {result['processing_time']:.4f}秒")
            
        except Exception as e:
            print(f"处理文件时出错: {str(e)}")
            sys.exit(1)
            
    elif args.command == 'config':
        system._show_system_config()
        
    else:
        # 如果没有提供命令，显示帮助信息
        parser.print_help()
        sys.exit(1)

# 主函数
def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 有命令行参数，使用CLI模式
        cli()
    else:
        # 没有命令行参数，使用交互式模式
        system = HaSPrivacySystem()
        system.interactive_mode()

if __name__ == "__main__":
    main()