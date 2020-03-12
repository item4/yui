import datetime

from .commons import cleanup_by_event_logs, cleanup_by_history
from ....box import box
from ....command import Cs, Us, option
from ....event import Message
from ....transform import choice
from ....utils.datetime import now

box.assert_config_required('OWNER_USER_TOKEN', str)
box.assert_channels_required('auto_cleanup_targets')
box.assert_users_required('force_cleanup')

COOLTIME = datetime.timedelta(minutes=5)


@box.command('청소')
@option('--count', '-c', default=100)
@option(
    '--mode',
    'm',
    transform_func=choice(
        ['log', 'history'], fallback='history', case='lower'
    ),
    default='log',
)
async def cleanup(bot, sess, event: Message, count: int, mode: str):
    """
    채널 청소

    해당 채널의 메시지 최근 100개를 즉각적으로 삭제합니다.
    채널당 5분의 쿨타임을 가지며, 자동 청소 채널 이외의 채널은 관리자만 사용 가능합니다.

    """

    try:
        channels = Cs.auto_cleanup_targets.gets()
        force_cleanup = Us.force_cleanup.gets()
    except KeyError:
        await bot.say(
            event.channel, '권한 검사 도중 에러가 발생했어요! 잠시 후에 다시 시도해주세요!',
        )
        return

    now_dt = now()

    if event.user not in force_cleanup:
        if event.channel not in channels:
            await bot.say(
                event.channel, '본 채널에서 이 명령어를 사용할 수 있는 권한이 없어요!',
            )
            return
        count = 100

        if event.channel.id in cleanup.last_call:
            last_call = cleanup.last_call[event.channel.id]
            if now_dt - last_call < COOLTIME:
                fine = (last_call + COOLTIME).strftime('%H시 %M분')
                await bot.say(
                    event.channel, f'아직 쿨타임이에요! {fine} 이후로 다시 시도해주세요!',
                )
                return

    if event.channel in channels and mode == 'log':
        deleted = await cleanup_by_event_logs(
            bot, sess, event.channel, event.ts,
        )
    else:
        deleted = await cleanup_by_history(
            bot, event.channel, event.ts, count,
        )

    await bot.say(
        event.channel, f'본 채널에서 최근 {deleted:,}개의 메시지를 삭제했어요!',
    )

    cleanup.last_call[event.channel.id] = now_dt
