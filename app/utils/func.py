from typing import Optional
import re
from aiograph import Telegraph

from settings import AIOGRAPH_TOKEN


def get_prompt(text: str) -> Optional[str]:
    prompt_regex = r'<b>Промпт:</b>\s*<code>(.*?)</code>'

    prompt_values = re.findall(prompt_regex, text)

    if prompt_values:
        return prompt_values[0]

    return None


async def aiograph_url(pic_url: str) -> str:
    telegraph = Telegraph(
        token=AIOGRAPH_TOKEN
    )

    try:
        pic_url = await telegraph.upload_from_url(pic_url)
    finally:
        await telegraph.session.close()

    return pic_url
