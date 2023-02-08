from yui.utils.html import strip_tags


def test_strip_tags():
    assert strip_tags("aaa<b>bbb<span>ccc</span>ddd</b>eee<img>fff") == (
        "aaabbbcccdddeeefff"
    )
