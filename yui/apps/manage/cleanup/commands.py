import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from .commons import cleanup_by_event_logs
from .commons import cleanup_by_history
from .commons import collect_history_from_channel
from ....box import box
from ....command import option
from ....event import Message
from ....transform import choice
from ....utils.datetime import now

box.assert_channels_required("auto_cleanup_targets")
box.assert_users_required("force_cleanup")

COOLTIME = datetime.timedelta(minutes=5)


@box.command("청소")
@option(
    "--mode",
    "m",
    transform_func=choice(
        ["log", "history"], fallback="history", case="lower"
    ),
    default="log",
)
async def cleanup(bot, sess: AsyncSession, event: Message, mode: str):
    """
    채널 청소

    해당 채널의 메시지 최근 100개를 즉각적으로 삭제합니다.
    채널당 5분의 쿨타임을 가지며, 자동 청소 채널 이외의 채널은 관리자만 사용 가능합니다.

    """

    count = 100
    now_dt = now()
    is_dm = event.channel.startswith("D")
    if is_dm:
        mode = "history"
        token = None
        channels = []
        force_cleanup = []
    else:
        try:
            token = bot.config.USER_TOKEN
        except AttributeError:
            await bot.say(
                event.channel,
                "본 슬랙에서는 이 명령어를 DM 외의 용도로 사용할 수 없어요!",
            )
            return

        try:
            channels = bot.config.CHANNELS["auto_cleanup_targets"]
            force_cleanup = bot.config.USERS["force_cleanup"]
        except KeyError:
            await bot.say(
                event.channel,
                "권한 검사 도중 에러가 발생했어요! 잠시 후에 다시 시도해주세요!",
            )
            return

    if event.user not in force_cleanup and not is_dm:
        if event.channel not in channels:
            await bot.say(
                event.channel,
                "본 채널에서 이 명령어를 사용할 수 있는 권한이 없어요!",
            )
            return
        count = 100

        if event.channel in cleanup.last_call:
            last_call = cleanup.last_call[event.channel]
            if now_dt - last_call < COOLTIME:
                fine = (last_call + COOLTIME).strftime("%H시 %M분")
                await bot.say(
                    event.channel,
                    f"아직 쿨타임이에요! {fine} 이후로 다시 시도해주세요!",
                )
                return

    if event.channel in channels and mode == "log":
        deleted = await cleanup_by_event_logs(
            bot,
            sess,
            event.channel,
            event.ts,
            token,
        )
    else:
        deleted = await cleanup_by_history(
            bot,
            event.channel,
            event.ts,
            token,
            count,
        )

    await bot.say(
        event.channel,
        f"본 채널에서 최근 {deleted:,}개의 메시지를 삭제했어요!",
    )

    cleanup.last_call[event.channel] = now_dt


@box.command("수집")
async def collect(bot, sess: AsyncSession, event: Message):
    """
    채널 메시지 수집

    해당 채널의 메시지를 수집합니다.
    권한이 있는 사용자가 자동 청소 대상 채널에서만 사용 가능합니다.
    """

    try:
        channels = bot.config.CHANNELS["auto_cleanup_targets"]
        force_cleanup = bot.config.USERS["force_cleanup"]
    except KeyError:
        await bot.say(
            event.channel,
            "권한 검사 도중 에러가 발생했어요! 잠시 후에 다시 시도해주세요!",
        )
        return

    if event.user not in force_cleanup:
        await bot.say(
            event.channel,
            "이 명령어를 사용할 수 있는 권한이 없어요!",
        )
        return

    if event.channel not in channels:
        await bot.say(
            event.channel,
            "이 명령어를 사용할 수 없는 채널이에요!",
        )
        return

    collected = await collect_history_from_channel(bot, event.channel, sess)

    await bot.say(
        event.channel,
        f"본 채널에서 최근 {collected:,}개의 메시지를 수집했어요!",
    )
