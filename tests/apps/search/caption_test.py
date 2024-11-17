from yui.apps.search.caption import Caption
from yui.apps.search.caption import convert_released_dt
from yui.apps.search.caption import encode_url
from yui.apps.search.caption import fix_url
from yui.apps.search.caption import format_episode_num
from yui.apps.search.caption import make_caption_attachments
from yui.apps.search.caption import make_caption_list
from yui.apps.search.caption import print_time
from yui.apps.search.caption import remove_protocol


def test_remove_protocol():
    assert remove_protocol("http://example.com") == "example.com"
    assert remove_protocol("https://example.com") == "example.com"


def test_fix_url():
    assert fix_url("http://example.com") == "https://example.com"
    assert fix_url("https://example.com") == "https://example.com"
    assert fix_url("example.com") == "https://example.com"

    assert fix_url("http://test.egloos.com") == "http://test.egloos.com"
    assert fix_url("https://test.egloos.com") == "http://test.egloos.com"
    assert fix_url("test.egloos.com") == "http://test.egloos.com"

    assert fix_url("") == ""
    assert fix_url("http://") == ""
    assert fix_url("https://") == ""


def test_convert_released_dt():
    assert convert_released_dt("2021-01-02T03:04:05") == "2021년 01월 02일 03시"
    assert convert_released_dt("20210102030405") == "2021년 01월 02일 03시"
    assert convert_released_dt("wrong format") == "wrong format"


def test_print_time():
    assert print_time("1234") == "12:34"


def test_encode_url():
    assert (
        encode_url("https://example.com/a/b/c/d")
        == "https://example.com/a/b/c/d"
    )
    assert (
        encode_url("https://example.com/한글/주소/경로")
        == "https://example.com/%ED%95%9C%EA%B8%80/%EC%A3%BC%EC%86%8C/%EA%B2%BD%EB%A1%9C"
    )


def test_format_episode_num():
    assert format_episode_num("0") == "단편"
    assert format_episode_num("1") == "1화"
    assert format_episode_num("2.5") == "2.5화"
    assert format_episode_num("9999") == "완결"


def test_make_caption_list_empty():
    result = make_caption_list([])
    assert len(result) == 1
    assert result[0].fallback == "자막 제작자가 없습니다."
    assert result[0].text == "자막 제작자가 없습니다."


def test_make_caption_attachments():
    captions = [
        Caption(
            maker="A",
            episode_num="0",
            url="https://a.dev/a/1",
            released_at="2024년 11월 11일 11시",
        ),
        Caption(
            maker="B",
            episode_num="1",
            url="https://b.dev/a/2",
            released_at="2024년 11월 12일 13시",
        ),
        Caption(
            maker="C",
            episode_num="0",
            url="https://c.dev/a/3",
            released_at="",
        ),
        Caption(
            maker="D",
            episode_num="1",
            url="https://d.dev/a/4",
            released_at="",
        ),
        Caption(
            maker="E",
            episode_num="0",
            url="",
            released_at="2024년 11월 14일 15시",
        ),
        Caption(
            maker="F",
            episode_num="0",
            url="",
            released_at="",
        ),
    ]
    result = make_caption_attachments(captions)
    assert result[0].author_name == "A"
    assert result[0].text == "단편 2024년 11월 11일 11시 https://a.dev/a/1"
    assert result[1].author_name == "B"
    assert result[1].text == "1화 2024년 11월 12일 13시 https://b.dev/a/2"
    assert result[2].author_name == "C"
    assert result[2].text == "단편 https://c.dev/a/3"
    assert result[3].author_name == "D"
    assert result[3].text == "1화 https://d.dev/a/4"
    assert result[4].author_name == "E"
    assert result[4].text == "준비중 2024년 11월 14일 15시"
    assert result[5].author_name == "F"
    assert result[5].text == "준비중"


def test_make_caption_list():
    captions = [
        Caption(
            maker="A",
            episode_num="0",
            url="https://a.dev/a/1",
            released_at="2024년 11월 11일 11시",
        ),
        Caption(
            maker="B",
            episode_num="1",
            url="https://b.dev/a/2",
            released_at="2024년 11월 12일 13시",
        ),
        Caption(
            maker="C",
            episode_num="0",
            url="https://c.dev/a/3",
            released_at="",
        ),
        Caption(
            maker="D",
            episode_num="1",
            url="https://d.dev/a/4",
            released_at="",
        ),
        Caption(
            maker="E",
            episode_num="0",
            url="",
            released_at="2024년 11월 14일 15시",
        ),
        Caption(
            maker="F",
            episode_num="0",
            url="",
            released_at="",
        ),
    ]
    result = make_caption_list(captions)

    assert result[0].author_name == "B"
    assert result[0].text == "1화 2024년 11월 12일 13시 https://b.dev/a/2"
    assert result[1].author_name == "D"
    assert result[1].text == "1화 https://d.dev/a/4"
    assert result[2].author_name == "A"
    assert result[2].text == "단편 2024년 11월 11일 11시 https://a.dev/a/1"
    assert result[3].author_name == "C"
    assert result[3].text == "단편 https://c.dev/a/3"
    assert result[4].author_name == "E"
    assert result[4].text == "준비중 2024년 11월 14일 15시"
    assert result[5].author_name == "F"
    assert result[5].text == "준비중"
