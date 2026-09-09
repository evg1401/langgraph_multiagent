from __future__ import annotations

from app.runner import RunResult

SEPARATOR = "=" * 70

ALL = "all"
FINAL = "final"
MODES = (ALL, FINAL)

# вся переписка
def format_transcript(result: RunResult) -> str:
    blocks = [
        f"{SEPARATOR}\n{message.name or 'user'}\n{SEPARATOR}\n{message.content}"
        for message in result.messages
    ]

    return "\n\n".join([*blocks, format_summary(result)])


def format_final(result: RunResult) -> str:
    return f"{result.final_text}\n\n{format_summary(result)}"


def format_summary(result: RunResult) -> str:
    return (
        f"{SEPARATOR}\n"
        f"Соцсеть: {result.network}; кругов доработки: {result.revisions}; "
        f"запусков агентов: "
        f"{', '.join(f'{name}×{count}' for name, count in result.runs.items()) or '—'}"
    )

# форматирование вывода
def render(result: RunResult, mode: str = ALL) -> str:
    formatters = {ALL: format_transcript, FINAL: format_final}
    try:
        return formatters[mode](result)
    except KeyError:
        raise ValueError(
            f"Неизвестный формат вывода «{mode}». Доступны: {', '.join(MODES)}"
        ) from None
