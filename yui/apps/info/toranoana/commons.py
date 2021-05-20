from .models import Target
from ....utils.http import USER_AGENT


HEADERS = {
    'Cookie': 'adflg=0',
    'User-Agent': USER_AGENT,
}


def get_urls(code: str, male: Target, female: Target) -> list[str]:
    result = []
    if male in [Target.common, Target.wildcard]:
        result.append(
            'https://ecs.toranoana.jp/tora/ec/app/catalog/list/'
            f'?coterieGenreCode1={code}'
            '&commodity_kind_name=%E5%90%8C%E4%BA%BA%E8%AA%8C'
            '&stock_status=%E2%97%8B%2C%E2%96%B3'
        )
    if male in [Target.adult, Target.wildcard]:
        result.append(
            f'https://ec.toranoana.jp/tora_r/ec/app/catalog/list/'
            f'?coterieGenreCode1={code}'
            '&commodity_kind_name=%E5%90%8C%E4%BA%BA%E8%AA%8C'
            '&stock_status=%E2%97%8B%2C%E2%96%B3'
        )
    if female in [Target.common, Target.wildcard]:
        result.append(
            'https://ecs.toranoana.jp/joshi/ec/app/catalog/list/'
            f'?coterieGenreCode1={code}'
            '&commodity_kind_name=%E5%90%8C%E4%BA%BA%E8%AA%8C'
            '&stock_status=%E2%97%8B%2C%E2%96%B3'
        )
    if female in [Target.adult, Target.wildcard]:
        result.append(
            'https://ec.toranoana.jp/joshi_r/ec/app/catalog/list/'
            f'?coterieGenreCode1={code}'
            '&commodity_kind_name=%E5%90%8C%E4%BA%BA%E8%AA%8C'
            '&stock_status=%E2%97%8B%2C%E2%96%B3'
        )
    return result
