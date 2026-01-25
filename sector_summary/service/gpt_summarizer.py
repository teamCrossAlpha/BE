import json
from openai import OpenAI

from common.config import settings
from sector_summary.service.gpt_prompt import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

client = OpenAI(api_key=settings.openai_api_key)


def summarize_sector(
    sector_key: str,
    sector_display: str,
    articles: list[dict]
) -> dict:
    prompt = USER_PROMPT_TEMPLATE.format(
        sector_display=sector_display,
        articles_json=json.dumps(articles, ensure_ascii=False)
    )

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    return json.loads(res.choices[0].message.content)
