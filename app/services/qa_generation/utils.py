from .config import qa_generation_service_settings


def build_contexts(records: list[dict]) -> list[str]:
    """从 records 构建 context 列表"""
    contexts = []
    for record in records:
        contents = record.get("消息内容", [])
        if not isinstance(contents, list):
            continue
        context = "\n".join(
            [
                f"{idx + 1}. {content.get('sender', '').replace('\n', '')}: {content.get('content', '').replace('\n', '')}"
                for idx, content in enumerate(contents)
            ]
        )
        if len(context) > qa_generation_service_settings.max_context_length:
            context = context[: qa_generation_service_settings.max_context_length]
        contexts.append(context)
    return contexts
