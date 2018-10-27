import pytest

from yui.apps.weather.aws.commands import aws, search_aws_zone
from yui.apps.weather.aws.models import AWS
from yui.event import create_event
from yui.utils.datetime import now

from ....util import FakeBot


@pytest.mark.asyncio
async def test_aws(fx_sess):
    dt = now()

    bot = FakeBot()
    bot.add_channel('C1', 'general')

    event = create_event({
        'type': 'message',
        'channel': 'C1',
    })

    await aws(bot, event, fx_sess, '인천')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '검색 결과가 없어요!'

    record = AWS()
    record.name = '인천'
    record.height = 1234
    record.is_raining = True
    record.rain15 = 111.111
    record.rain60 = 222.222
    record.rain6h = 333.333
    record.rain12h = 444.444
    record.rainday = 555.555
    record.temperature = 12.34
    record.wind_direction1 = 'SSW'
    record.wind_speed1 = 11.11
    record.wind_direction10 = 'NNE'
    record.wind_speed10 = 22.22
    record.humidity = 55
    record.pressure = 1234.56
    record.location = '인천광역시 중구 전동'
    record.observed_at = dt

    with fx_sess.begin():
        fx_sess.add(record)

    await aws(bot, event, fx_sess, '인천')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '[{}@인천/인천광역시 중구 전동]'
        ' 강수: 예(15min: 111.111/일일: 555.555)'
        ' / 12.34℃ / 바람: 남남서 11.11㎧ / 습도: 55% / 해면기압: 1234.56hPa'
    ).format(
        dt.strftime('%Y년 %m월 %d일 %H시 %M분')
    )

    record2 = AWS()
    record2.name = '인천'
    record2.height = 1234
    record2.is_raining = True
    record2.rain15 = 111.111
    record2.rain60 = 222.222
    record2.rain6h = 333.333
    record2.rain12h = 444.444
    record2.rainday = 555.555
    record2.temperature = 12.34
    record2.wind_direction1 = 'SSW'
    record2.wind_speed1 = 11.11
    record2.wind_direction10 = 'NNE'
    record2.wind_speed10 = 22.22
    record2.humidity = 55
    record2.pressure = 1234.56
    record2.location = '인천광역시 중구 전동'
    record2.observed_at = dt

    with fx_sess.begin():
        fx_sess.add(record2)

    await aws(bot, event, fx_sess, '인천')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == (
        '검색 결과가 여러가지 있어요! 시스템 관리자에게 문의해주세요!'
    )


@pytest.mark.asyncio
async def test_search_aws_zone(fx_sess):
    dt = now()

    bot = FakeBot()
    bot.add_channel('C1', 'general')

    event = create_event({
        'type': 'message',
        'channel': 'C1',
        'ts': '1234.5678'
    })

    await search_aws_zone(bot, event, fx_sess, 'name', '인')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '검색 결과가 없어요!'
    assert said.data['thread_ts'] == '1234.5678'

    record = AWS()
    record.name = '인천'
    record.height = 1234
    record.is_raining = True
    record.rain15 = 111.111
    record.rain60 = 222.222
    record.rain6h = 333.333
    record.rain12h = 444.444
    record.rainday = 555.555
    record.temperature = 12.34
    record.wind_direction1 = 'SSW'
    record.wind_speed1 = 11.11
    record.wind_direction10 = 'NNE'
    record.wind_speed10 = 22.22
    record.humidity = 55
    record.pressure = 1234.56
    record.location = '인천광역시 중구 전동'
    record.observed_at = dt

    with fx_sess.begin():
        fx_sess.add(record)

    await search_aws_zone(bot, event, fx_sess, 'name', '인천')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '검색 결과는 다음과 같습니다.\n\n인천(인천광역시 중구 전동)'
    assert said.data['thread_ts'] == '1234.5678'

    await search_aws_zone(bot, event, fx_sess, 'location', '인천')

    said = bot.call_queue.pop(0)
    assert said.method == 'chat.postMessage'
    assert said.data['channel'] == 'C1'
    assert said.data['text'] == '검색 결과는 다음과 같습니다.\n\n인천(인천광역시 중구 전동)'
    assert said.data['thread_ts'] == '1234.5678'
