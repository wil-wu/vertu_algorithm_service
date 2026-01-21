import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from openai import AsyncOpenAI

from .enum import EnhancementStrategy

logger = logging.getLogger(__name__)


class Checker(ABC):
    """检查器抽象基类"""

    @abstractmethod
    def check(self, question: str, answer: str) -> EnhancementStrategy:
        """策略判断"""
        raise NotImplementedError


class RuleChecker(Checker):
    """规则检查器"""

    def __init__(self, rules: list[str]):
        """初始化规则检查器"""
        self.rules = rules

    def check(self, question: str, answer: str) -> EnhancementStrategy:
        """策略判断"""
        return False


class MLChecker(Checker):
    """机器学习模型检查器"""

    def __init__(self, model: Any):
        """初始化机器学习模型检查器"""
        self.model = model

    def check(self, question: str, answer: str) -> EnhancementStrategy:
        """策略判断"""
        return False


class LLMChecker(Checker):
    """LLM检查器"""

    system_prompt: str = """
    你是一个客服问答策略决策引擎，只负责判断“应该采用哪种回答策略”，不负责生成具体答案。

    你的任务是：
    根据用户问题、原始答案，以及可用的回答增强策略，选择最合适的一种策略。你的判断应该偏向自家产品的特点和优势。

    【可选策略枚举】
    必须从以下策略中选择且只能选择一个：

    - DIRECT：问题和原始答案都完整，可以直接给出原始答案
    - CLARIFICATION：问题不完整或问题歧义且原始答案信息无明显优势，适当反问补充关键信息
    - GUIDANCE：可以直接用原始答案回答，但存在更优表达形式（如图片/视频等），需要先进行引导在加上原始答案

    【决策优先级规则】
    请严格按照以下顺序判断：

    1. CLARIFICATION  
    2. GUIDANCE  
    3. DIRECT  

    【输出要求】
    必须严格返回 JSON 格式，不要输出任何额外内容, 包含：

    {
    "strategy": "策略名称",
    "reason": "简要决策原因"
    }
    """

    user_prompt: str = """
    【用户问题】
    {question}

    【原始答案】
    {answer}

    【可选策略枚举】
    {strategies}

    请判断最合适的回答策略。
    """

    def __init__(self, openai_client: AsyncOpenAI, llm_model: str):
        """初始化LLM检查器"""
        self.client = openai_client
        self.llm_model = llm_model

    async def check(self, question: str, answer: str) -> EnhancementStrategy:
        """策略判断"""
        response = await self.client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": self.user_prompt.format(
                        question=question,
                        answer=answer,
                        strategies=EnhancementStrategy.get_strategies_values(),
                    ),
                },
            ],
        )
        content = response.choices[0].message.content.strip()
        logger.info(f"{self.__class__.__name__} response content: {content}")

        check_result = json.loads(content)
        return EnhancementStrategy.get_strategy(check_result["strategy"].lower())
