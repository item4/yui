import inspect

import aiohttp

from sqlalchemy.orm.exc import NoResultFound

from .commons import HEADERS
from .commons import get_urls
from .models import Character
from .models import Coupling
from .models import Genre
from .models import Tag
from .models import Target
from .models import Watch
from ....box import box
from ....box import route
from ....command import C
from ....command import U
from ....command import argument
from ....event import Message
from ....utils import format
from ....utils.html import get_root


box.assert_channel_required('toranoana')

TRANSLATE_MAP = {
    '전체': Target.wildcard,
    '전부': Target.wildcard,
    'all': Target.wildcard,
    '*': Target.wildcard,
    '일반': Target.common,
    '전연령': Target.common,
    'normal': Target.common,
    'common': Target.common,
    '성인': Target.adult,
    '성인물': Target.adult,
    '성인용': Target.adult,
    '18': Target.adult,
    '19': Target.adult,
    'r18': Target.adult,
    'r': Target.adult,
    '제외': Target.nobody,
    '금지': Target.nobody,
    'no': Target.nobody,
    'x': Target.nobody,
}


class Toranoana(route.RouteApp):
    def __init__(self) -> None:
        self.name = 'tora'
        self.route_list = [
            route.Route(name='add', callback=self.add),
            route.Route(name='추가', callback=self.add),
            route.Route(name='구독', callback=self.add),
            route.Route(name='list', callback=self.list),
            route.Route(name='목록', callback=self.list),
            route.Route(name='delete', callback=self.delete),
            route.Route(name='del', callback=self.delete),
            route.Route(name='삭제', callback=self.delete),
            route.Route(name='취소', callback=self.delete),
            route.Route(name='alias', callback=self.alias),
        ]

    def get_short_help(self, prefix: str):
        return f'{format.code(f"{prefix}tora")}: 토라노아나 구독'

    def get_full_help(self, prefix: str):
        addr = format.code(
            'https://ec.toranoana.shop/'
            'joshi/ec/cot/genre/GNRN00001186/all/all/'
        )
        code = format.code('GNRN00001186')
        g_code = format.code('[g_code]')

        add_example = format.code(f'{prefix}tora add 남성일반 여성제외 [g_code]')

        add = format.code('add')
        추가 = format.code('추가')
        구독 = format.code('구독')
        list_ = format.code('list')
        목록 = format.code('목록')
        del_ = format.code('del')
        delete = format.code('delete')
        삭제 = format.code('삭제')
        취소 = format.code('취소')

        return inspect.cleandoc(
            f"""
        {format.bold('토라노아나 구독')}

        토라노아나 동인지 코너를 구독할 때 사용됩니다.
        구독하기로 한 장르의 신간을 1시간 간격으로 조회합니다.

        구독 추가 예시: {add_example}
        - 남성/여성 + 전체/성인/일반/제외 조합이 가능합니다.
        - {g_code} 자리에는 토라노아나 고유코드를 적어야 합니다.
        - 가령 주소가 {addr}이라면 대문자 G로 시작하는 {code}가 {g_code} 입니다.

        구독 목록 예시: {format.code(f'{prefix}tora list')}
        구독 목록이 타인에게는 보여지지 않습니다.

        구독 취 예시: {format.code(f'{prefix}tora del [id]')}
        {format.code('[id]')} 자리에는 list 명령에서 나오는 고유번호를 입력해주세요.

        {add} 대신 {추가}, {구독} 을 사용할 수 있습니다.
        {list_} 대신 {목록} 을 사용할 수 있습니다.
        {del_} 대신 {delete}, {삭제}, {취소} 를 사용할 수 있습니다."""
        )

    async def fallback(self, bot, event: Message):
        await bot.say(event.channel, f'Usage: `{bot.config.PREFIX}help tora`')

    @argument('male_target')
    @argument('female_target')
    @argument('code')
    async def add(
        self,
        bot,
        event: Message,
        sess,
        male_target: str,
        female_target: str,
        code: str,
    ):
        try:
            male = TRANSLATE_MAP[
                male_target.replace('남성', '').replace('남', '').strip()
            ]
            female = TRANSLATE_MAP[
                female_target.replace('여성', '').replace('여', '').strip()
            ]
        except KeyError:
            await bot.say(
                event.channel,
                '인식할 수 없는 구독타겟이에요!',
            )
            return

        scan_urls = get_urls(code, male, female)

        if not scan_urls:
            await bot.say(
                event.channel,
                '구독 설정이 올바르지 않아요!' ' 적어도 한 가지 소스는 수신할 수 있도록 해주세요!',
            )
            return

        if U.owner.get().id == event.user.id:
            target = C.toranoana.get()
            target_desc = f'{format.link(target)} 채널에'
        else:
            target = event.user
            target_desc = f'{format.link(target)}님께 DM으로'

        watch = (
            sess.query(Watch)
            .filter(
                Genre.code == code,
                Watch.genre_id == Genre.id,
                Watch.print_target_id == target.id,
            )
            .first()
        )
        if watch:
            await bot.say(
                event.channel,
                f'{format.code(watch.genre.easy_name)} 장르는 이미 구독중이에요!',
            )
            return

        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(scan_urls[0]) as resp:
                blob = await resp.text()
            h = get_root(blob)

            genre = Genre()
            genre.code = code
            genre.name = (
                h.cssselect('.search-result h1')[0]
                .text_content()
                .replace('ジャンル：', '')
                .replace(' 作品一覧', '')
                .replace(' の同人誌一覧', '')
                .strip()
            )

            watch = Watch()
            watch.genre = genre
            watch.male = male
            watch.female = female
            watch.print_target_id = target.id

            with sess.begin():
                sess.add(genre)
                sess.add(watch)

        await bot.say(
            event.channel,
            f'{format.code(genre.name)}의 구독을 시작했어요!'
            f' 정보를 취합한 뒤, {target_desc}'
            f' 변화 내역을 공유해드릴게요!',
        )

    async def list(self, bot, event: Message, sess):
        if U.owner.get().id == event.user.id:
            target = C.toranoana.get()
            target_desc = f'{format.link(target)} 채널에서'
        else:
            target = event.user
            target_desc = f'{format.link(target)}님의 DM으로'
        watches: list[Watch] = sess.query(Watch).filter_by(
            print_target_id=target.id,
        )
        watch_list = '\n'.join(
            '- #{id}: {genre_name} (남성향: {male} / 여성향: {female})'.format(
                id=w.id,
                genre_name=format.code(w.genre.easy_name),
                male=w.male_text,
                female=w.female_text,
            )
            for w in watches
        )
        if watch_list:
            text = f'{target_desc} 구독중인 내역을 알려드릴게요!\n\n{watch_list}'
        else:
            text = f'{target_desc} 구독중인 내역이 없어요!'

        await bot.api.chat.postEphemeral(
            event.channel,
            event.user,
            text,
            as_user=True,
        )

    @argument('id')
    async def delete(self, bot, event: Message, sess, id: str):
        if U.owner.get().id == event.user.id:
            target = C.toranoana.get()
        else:
            target = event.user
        try:
            watch: Watch = (
                sess.query(Watch)
                .filter_by(
                    id=id,
                    print_target_id=target.id,
                )
                .one()
            )
        except NoResultFound:
            await bot.api.chat.postEphemeral(
                event.channel,
                event.user,
                f'해당하는 구독건을 찾을 수 없어요!'
                f' {format.code(f"{bot.config.PREFIX}tora list")}에서'
                ' 자신이 구독중인 항목의 ID값을 입력해주세요!',
                as_user=True,
            )
            return

        with sess.begin():
            sess.delete(watch)

        await bot.api.chat.postEphemeral(
            event.channel,
            event.user,
            '구독이 취소되었어요!',
            as_user=True,
        )

    @argument('field')
    @argument('origin')
    @argument('alternative')
    async def alias(
        self,
        bot,
        event: Message,
        sess,
        field: str,
        origin: str,
        alternative: str,
    ):
        if U.owner.get().id != event.user.id:
            await bot.say(
                event.channel,
                '해당 명령어를 사용할 권한이 없어요!',
            )
            return

        o = (
            sess.query(
                {
                    'tag': Tag,
                    'coupling': Coupling,
                    'character': Character,
                }.get(field, Genre)
            )
            .filter_by(name=origin)
            .first()
        )

        if not o:
            await bot.say(event.channel, '조회에 실패했어요!')
            return

        o.name_ko = alternative
        with sess.begin():
            sess.add(o)

        field_name = {'tag': '태그', 'coupling': '커플링', 'character': '캐릭터'}.get(
            field, '장르'
        )
        await bot.say(event.channel, f'{field_name}: {o.name} -> {o.name_ko}')


box.register(Toranoana())
