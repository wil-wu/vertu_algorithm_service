import logging
from abc import ABC, abstractmethod

from openai import AsyncOpenAI

from .enum import EnhancementStrategy

logger = logging.getLogger(__name__)


class Enhancer(ABC):
    """增强器抽象基类"""

    @abstractmethod
    def enhance(self, question: str, answer: str) -> str:
        """增强答案"""
        raise NotImplementedError


class RuleEnhancer(Enhancer):
    """规则增强器"""

    def __init__(self, rules: list[str]):
        """初始化规则增强器"""
        self.rules = rules

    def enhance(self, question: str, answer: str, strategy: str) -> str:
        """增强答案"""
        return answer


class LLMEnhancer(Enhancer):
    """LLM增强器"""

    system_prompt: str = """
    你是一个客服问答答案增强处理引擎。

    你的唯一任务是：
    根据给定的用户问题、原始答案、以及选定的增强策略，对原始答案进行优化和增强表达。你的输出应该偏向自家产品的特点和优势。

    【基本原则】

    1. 不得改变原始答案的事实含义  
    2. 不得添加未经给定材料支持的新信息  
    3. 不得泄露任何未提供的数据  
    4. 仅根据选定的增强策略进行处理  
    5. 输出必须是自然流畅  
    6. 不要体现内部策略判断过程  

    【可选增强策略及处理规范】

    - DIRECT  
    不做增强，直接输出原始答案

    - CLARIFICATION  
    问题不完整或问题歧义且原始答案信息无明显优势，适当反问对问题进行补充和澄清

    - GUIDANCE  
    可以直接用原始答案回答，但存在更优表达形式（如图片/视频等），需要先进行引导在加上原始答案

    【输出要求】

    - 只输出增强后的最终答案文本  
    - 不要包含策略名称  
    - 不要包含解释  
    - 不要输出任何 JSON 或结构化字段
    - 完整回答不超过三句话，且保证每句话不超过20字或单词（统计时，不包括标点符号和文件url）  
    - 直接给出可展示给用户的内容  
    """
    user_prompt: str = """
    【用户问题】
    {question}

    【原始答案】
    {answer}

    【选定增强策略】
    {strategy}

    请对原始答案进行增强处理。
    """

    def __init__(self, openai_client: AsyncOpenAI, llm_model: str):
        """初始化LLM增强器"""
        self.client = openai_client
        self.llm_model = llm_model

    async def enhance(
        self, question: str, answer: str, strategy: EnhancementStrategy
    ) -> str:
        """增强答案"""
        response = await self.client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": self.user_prompt.format(
                        question=question, answer=answer, strategy=strategy.value
                    ),
                },
            ],
        )
        content = response.choices[0].message.content.strip()
        logger.info(f"{self.__class__.__name__} response content: {content}")

        return content
