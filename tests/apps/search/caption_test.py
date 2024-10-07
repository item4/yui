from yui.apps.search.caption import convert_released_dt
from yui.apps.search.caption import encode_url
from yui.apps.search.caption import fix_url
from yui.apps.search.caption import format_episode_num
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
