import openai
import requests
import json
from typing import Dict, Any

class MedicalAnalyzer:
    def __init__(self):
        self.setup_ai_models()
        
    def setup_ai_models(self):
        # 从配置文件加载API密钥和URL
        config = self.load_config()
        self.openai_client = openai.OpenAI(
            api_key=config['openai']['api_key'],
            base_url=config['openai']['base_url']
        )
        self.deepseek_api_key = config['deepseek']['api_key']
        self.deepseek_base_url = config['deepseek']['base_url']

    def load_config(self) -> Dict[str, Any]:
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                import yaml
                return yaml.safe_load(f)
        except Exception as e:
            return {
                'openai': {
                    'api_key': '',
                    'base_url': 'https://api.openai.com/v1'
                },
                'deepseek': {
                    'api_key': '',
                    'base_url': 'https://api.deepseek.com/v1'
                }
            }

    def build_medical_prompt(self, user_info: Dict[str, Any], symptoms: str) -> str:
        return f"""作为一个专业的AI医疗助手,请基于以下信息进行分析,并严格按照指定格式输出:

患者基本信息:
- 年龄: {user_info['age']}岁
- 性别: {user_info['gender']}
- 身高: {user_info.get('height', '未提供')}cm
- 体重: {user_info.get('weight', '未提供')}kg
- 症状描述: {symptoms}

请按以下格式提供分析结果:

=== 初步诊断分析 ===
主要诊断：[诊断名称]
诊断依据：[具体说明]
鉴别诊断：[需要排除的疾病]
可能并发症：[可能出现的并发症]
ICD-10编码：[对应的ICD-10编码]

=== 检查建议 ===
实验室检查：
[具体检查项目]

影像学检查：
[具体检查项目]

其他辅助检查：
[其他必要检查]

=== 用药方案 ===
推荐用药：
- [药品1]：[剂量] [用法]
用药说明：[具体说明]
注意事项：[用药注意事项]

- [药品2]：[剂量] [用法]
用药说明：[具体说明]
注意事项：[用药注意事项]

- [药品3]：[剂量] [用法]
用药说明：[具体说明]
注意事项：[用药注意事项]

- [药品4]：[剂量] [用法]
用药说明：[具体说明]
注意事项：[用药注意事项]

- [药品5]：[剂量] [用法]
用药说明：[具体说明]
注意事项：[用药注意事项]

=== 手术建议 ===
手术名称：[手术名称]
手术编码：[ICD-9-CM-3编码]
手术说明：[具体说明]

=== DRGs信息 ===
MDC分组：[MDC分组]
DRG分组：[具体DRG分组]
优化建议：[优化建议]

=== 生活指导 ===
饮食建议：[具体建议]
活动建议：[具体建议]
复诊计划：[具体安排]
预防保健：[具体措施]

=== 医保信息 ===
医保类别：[医保类别]
报销范围：[可报销项目]
自付比例：[自付比例说明]

注意事项:
1. 所有建议均基于循证医学证据
2. 用药建议符合国家基本药物目录
3. 诊疗方案符合医保支付政策
4. 本建议仅供参考,具体诊疗请遵医嘱

免责声明：本分析结果仅供参考,不能替代专业医生的诊疗意见。请务必在专业医疗机构进行正规诊疗。

请严格按照以上格式输出，特别是用药信息部分，每个药品必须包含名称、剂量、用法、说明和注意事项，并使用统一的格式和缩进。
"""

    def get_openai_analysis(self, prompt: str) -> str:
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的医疗AI助手,基于医学知识提供分析和建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")

    def get_deepseek_analysis(self, prompt: str) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个专业的医疗AI助手,基于医学知识提供分析和建议。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(
                f"{self.deepseek_base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                raise Exception(f"API返回错误: {response.text}")
        except Exception as e:
            raise Exception(f"DeepSeek API调用失败: {str(e)}")

    def analyze(self, user_info: Dict[str, Any], symptoms: str) -> str:
        # 构建医疗提示词
        prompt = self.build_medical_prompt(user_info, symptoms)
        
        # 调用两个模型获取分析结果
        openai_result = self.get_openai_analysis(prompt)
        deepseek_result = self.get_deepseek_analysis(prompt)
        
        # 合并分析结果
        final_result = f"""=== AI 综合诊断分析 ===

OpenAI 分析建议:
{openai_result}

DeepSeek 分析建议:
{deepseek_result}

免责声明:本分析结果仅供参考,具体诊疗请遵医嘱。
"""
        return final_result 