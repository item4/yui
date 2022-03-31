from yui.utils.url import b64_redirect


def test_b64_redirect():

    assert b64_redirect("item4").startswith(
        "https://item4.github.io/yui/helpers/b64-redirect.html?b64="
    )
