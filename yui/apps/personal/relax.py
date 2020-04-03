from ..manage.cleanup.models import EventLog
from ...box import box
from ...command.helpers import C

box.assert_channel_required('relax')


@box.cron('30 19 * * *')
async def relax(bot, sess):
    channel = C.relax.get()
    resp = await bot.say(
        channel,
        '[자동] 저는 인간관계에 그리 능숙하지 못합니다. 그래서 매번 사람들에게 상처를 '
        '주고, 인간관계를 망쳐왔습니다. 저는 제 이런 부분을 고치고 싶다고 생각합니다. '
        '혹시라도 제가 인간관계에 있어서 부적절한 모습을 보이면 주저치 말고 지적해주세요.'
        ' 비록 이제까지 망쳐왔던 것들을 되돌릴 수 없을지더라도, 앞으로의 삶에서 같은 '
        '잘못을 반복하고 싶지 않습니다. 제발 부탁드립니다. 말을 해주지 않으면 모르는 '
        '미숙한 저에게, 문제가 되는 부분은 그때그때 분명하게 말씀해주세요.\n'
        '괜찮습니다. 앞으로 더 괜찮아져야하기에 그렇구요.\n'
        '(본 메시지는 하루에 1차례 자동 전송됩니다)',
        token=bot.config.OWNER_USER_TOKEN,
    )
    e = EventLog()
    e.channel = channel.id
    e.ts = resp.body['ts']

    with sess.begin():
        sess.add(e)
