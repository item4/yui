from fake_useragent import FakeUserAgent

from .models import Target


HEADERS = {
    'Cookie': 'adflg=0',
    'User-Agent': FakeUserAgent().chrome,
}


def get_urls(code: str, male: Target, female: Target) -> list[str]:
    result = []
    if male in [Target.common, Target.wildcard]:
        result.append(
            f'https://ec.toranoana.shop/tora/ec/cot/genre/{code}/all/all/'
        )
    if male in [Target.adult, Target.wildcard]:
        result.append(
            f'https://ec.toranoana.jp/tora_r/ec/cot/genre/{code}/all/all/'
        )
    if female in [Target.common, Target.wildcard]:
        result.append(
            f'https://ec.toranoana.shop/joshi/ec/cot/genre/{code}/all/all/'
        )
    if female in [Target.adult, Target.wildcard]:
        result.append(
            f'https://ec.toranoana.jp/joshi_r/ec/cot/genre/{code}/all/all/'
        )
    return result
