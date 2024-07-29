from yui.apps.search.caption import convert_released_dt
from yui.apps.search.caption import encode_url
from yui.apps.search.caption import fix_url
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


def test_convert_released_dt():
    assert convert_released_dt("2021-01-02T03:04:05") == "2021년 01월 02일 03시"
    assert convert_released_dt("20210102030405") == "2021년 01월 02일 03시"


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
