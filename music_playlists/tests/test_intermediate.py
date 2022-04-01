from typing import Optional

import pytest as pytest

from music_playlists.intermediate.manage import Manage
from music_playlists.intermediate.track import Track


@pytest.mark.parametrize(
    "track,others,expected",
    [
        ({"title": "", "artists": []}, [], None),
        (
            {"title": "", "artists": []},
            [{"title": "", "artists": []}],
            {"title": "", "artists": []},
        ),
        (
            {"title": "For My Friends", "artists": ["King Princess"]},
            [{"title": "For My Friends", "artists": ["King Princess"]}],
            {"title": "For My Friends", "artists": ["King Princess"]},
        ),
        (
            {"title": "GAY 4 ME", "artists": ["G Flip", "Lauren Sanderson"]},
            [
                {
                    "title": "GAY 4 ME (feat. Lauren Sanderson)",
                    "artists": ["G Flip", "Lauren Sanderson"],
                }
            ],
            {
                "title": "GAY 4 ME (feat. Lauren Sanderson)",
                "artists": ["G Flip", "Lauren Sanderson"],
            },
        ),
        (
            {"title": "it's not that bad", "artists": ["Caroline & Claude"]},
            [{"title": "It's Not That Bad", "artists": ["Caroline & Claude"]}],
            {"title": "It's Not That Bad", "artists": ["Caroline & Claude"]},
        ),
        (
            {"title": "How Do I Know?", "artists": ["Thomas Headon"]},
            [{"title": "How Do I Know", "artists": ["Thomas Headon"]}],
            {"title": "How Do I Know", "artists": ["Thomas Headon"]},
        ),
        (
            {"title": "Head on Fire", "artists": ["Griff x Sigrid"]},
            [{"title": "Head on Fire", "artists": ["Griff", "Sigrid"]}],
            {"title": "Head on Fire", "artists": ["Griff", "Sigrid"]},
        ),
        (
            {"title": "Head on Fire", "artists": ["Griff", "Sigrid"]},
            [{"title": "Head on Fire", "artists": ["Griff x Sigrid"]}],
            {"title": "Head on Fire", "artists": ["Griff x Sigrid"]},
        ),
        (
            {
                "title": "bbycakes",
                "artists": ["mura masa", "lil uzi vert", "pinkpantheress", "shygirl"],
            },
            [
                {
                    "title": "bbycakes (with lil uzi vert, pinkpantheress & shygirl)",
                    "artists": [
                        "mura masa",
                        "lil uzi vert",
                        "pinkpantheress",
                        "shygirl",
                    ],
                }
            ],
            {
                "title": "bbycakes (with lil uzi vert, pinkpantheress & shygirl)",
                "artists": ["mura masa", "lil uzi vert", "pinkpantheress", "shygirl"],
            },
        ),
        (
            {
                "title": "bbycakes (with lil uzi vert, pinkpantheress & shygirl)",
                "artists": ["mura masa", "lil uzi vert", "pinkpantheress", "shygirl"],
            },
            [
                {
                    "title": "bbycakes",
                    "artists": [
                        "mura masa",
                        "lil uzi vert",
                        "pinkpantheress",
                        "shygirl",
                    ],
                }
            ],
            {
                "title": "bbycakes",
                "artists": ["mura masa", "lil uzi vert", "pinkpantheress", "shygirl"],
            },
        ),
        (
            {"title": "next high", "artists": ["mansionair"]},
            [{"title": "next high", "artists": ["mansionair", "kim tee"]}],
            {"title": "next high", "artists": ["mansionair", "kim tee"]},
        ),
    ],
)
def test_match(track: dict, others: list[dict], expected: Optional[dict]):
    m = Manage()

    a = Track(
        title=track.get("title"),
        artists=track.get("artists"),
        origin_code="",
        raw=None,
    )
    available = [
        Track(title=i.get("title"), artists=i.get("artists"), origin_code="", raw=None)
        for i in others
    ]
    actual = m.match(a, available)

    if expected:
        expected = Track(
            title=expected.get("title"),
            artists=expected.get("artists"),
            origin_code="",
            raw=None,
        )
    assert expected == actual
