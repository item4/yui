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
            'https://ecs.toranoana.jp/tora/ec/app/catalog/list/'
            f'?coterieGenreCode1={code}'
        )
    if male in [Target.adult, Target.wildcard]:
        result.append(
            f'https://ec.toranoana.jp/tora_r/ec/app/catalog/list/'
            f'?coterieGenreCode1={code}'
        )
    if female in [Target.common, Target.wildcard]:
        result.append(
            'https://ecs.toranoana.jp/joshi/ec/app/catalog/list/'
            f'?coterieGenreCode1={code}'
        )
    if female in [Target.adult, Target.wildcard]:
        result.append(
            'https://ec.toranoana.jp/joshi_r/ec/app/catalog/list/'
            f'?coterieGenreCode1={code}'
        )
    return result
