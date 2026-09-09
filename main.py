from __future__ import annotations

import sys
from app import reporting
from app.brief import BriefError, load_brief
from app.config import ConfigError, Settings
from app.langfuse import create_langfuse_handler
from app.runner import ContentFactory

def main() -> int:
    try:
        settings = Settings.from_env()
        settings.validate()
        brief = load_brief(settings.brief_file)

        langfuse_client, langfuse_handler = create_langfuse_handler(settings.langfuse)
        try:
            result = ContentFactory.from_settings(settings, langfuse_handler).run(brief)
        finally:
            if langfuse_client is not None:
                langfuse_client.flush()
    except (ConfigError, BriefError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        
        return 1
    except KeyboardInterrupt:
        print("Прогон прерван", file=sys.stderr)

        return 2

    print(reporting.render(result, reporting.ALL))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
