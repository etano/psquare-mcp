"""Pins feed parsing against both ParentSquare feed layouts.

Posts used to be direct ``div.ps-box`` children of ``#feeds-list``. ParentSquare
now wraps each one in ``ul.feeds-list > li.feeds-list-item``, and the old
direct-child lookup returned no posts at all, so ``get_feeds`` and
``get_group_feed`` answered "No posts found." for feeds that had posts.
"""

from bs4 import BeautifulSoup

from parentsquare_mcp.parsers.feeds import parse_feed_page

POST = """
<div class="ps-box">
  <div class="feed">
    <div id="feed_{id}">
      <span role="heading">{title}</span>
      <a class="user-name">Teacher</a>
      <span class="time-ago" data-timestamp="2026-10-01T12:00:00Z"></span>
    </div>
  </div>
</div>
"""


def _page(body: str) -> BeautifulSoup:
    return BeautifulSoup(f'<div id="feeds-list">{body}</div>', "html.parser")


def test_direct_child_layout():
    soup = _page(POST.format(id=1, title="Old") + POST.format(id=2, title="Layout"))
    assert [p.id for p in parse_feed_page(soup)] == [1, 2]


def test_list_wrapped_layout():
    items = "".join(
        f'<li class="feeds-list-item">{POST.format(id=i, title=f"Post {i}")}</li>'
        for i in (10, 11, 12)
    )
    soup = _page(f'<ul class="feeds-list">{items}</ul>')
    posts = parse_feed_page(soup)
    assert [p.id for p in posts] == [10, 11, 12]
    assert posts[0].title == "Post 10"


def test_nested_ps_box_is_not_a_separate_post():
    inner = '<div class="ps-box"><div id="feed_99"></div></div>'
    outer = POST.format(id=5, title="Outer").replace("</div>\n  </div>\n</div>", f"</div>{inner}</div></div>", 1)
    soup = _page(f'<ul class="feeds-list"><li class="feeds-list-item">{outer}</li></ul>')
    assert [p.id for p in parse_feed_page(soup)] == [5]
