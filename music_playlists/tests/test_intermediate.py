import pytest as pytest

from music_playlists.intermediate.manage import Manage
from music_playlists.intermediate.models import Track


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
def test_match(track: dict, others: list[dict], expected: dict | None):
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


# 2024-10-18 19:20:40,069 - WARNING  - music-playlists: No match in 1 queries for track abc-radio: 'For Crying Out Loud' - 'FINNEAS'
# 2024-10-18 19:20:40,069 - WARNING  - music-playlists: No match in 5 service tracks for queries ['finneas for crying out loud']
# 2024-10-18 19:20:40,095 - WARNING  - music-playlists: No match in 4 queries for track abc-radio: 'take your vibes and go' - 'Kito', 'Kah- Lo', 'Baauer', 'brazy'
# 2024-10-18 19:20:40,095 - WARNING  - music-playlists: No match in 18 service tracks for queries ['kito kah lo baauer brazy take your vibes and go', 'kito kah lo baauer take your vibes and go', 'kito kah lo take your vibes and go', 'kito take your vibes and go']
# 2024-10-18 19:20:40,106 - WARNING  - music-playlists: No match in 1 queries for track abc-radio: 'Roxanne' - 'South Summit'
# 2024-10-18 19:20:40,106 - WARNING  - music-playlists: No match in 5 service tracks for queries ['south summit roxanne']
# 2024-10-18 19:20:40,134 - WARNING  - music-playlists: No match in 3 queries for track abc-radio: 'THE BADDEST (BADDER)' - 'Joey Valence & Brae', 'Ayesha Erotica'
# 2024-10-18 19:20:40,134 - WARNING  - music-playlists: No match in 15 service tracks for queries ['joey valence brae ayesha erotica the baddest (badder)', 'joey valence brae the baddest (badder)', 'joey valence the baddest (badder)']
# 2024-10-18 19:20:40,141 - WARNING  - music-playlists: No match in 1 queries for track abc-radio: 'BRITNEY IN '03' - 'REDD.'
# 2024-10-18 19:20:40,141 - WARNING  - music-playlists: No match in 2 service tracks for queries ['redd. britney in 03']
# 2024-10-18 19:20:40,760 - WARNING  - music-playlists: No match in 1 queries for track abc-radio: 'For Crying Out Loud' - 'FINNEAS'
# 2024-10-18 19:20:40,760 - WARNING  - music-playlists: No match in 20 service tracks for queries ['finneas for crying out loud']
# 2024-10-18 19:20:40,826 - WARNING  - music-playlists: No match in 2 queries for track abc-radio: 'Talk talk featuring troye sivan' - 'Charli xcx & Troye Sivan'
# 2024-10-18 19:20:40,826 - WARNING  - music-playlists: No match in 40 service tracks for queries ['charli xcx troye sivan talk talk featuring troye sivan', 'charli xcx talk talk featuring troye sivan']
# 2024-10-18 19:20:40,908 - WARNING  - music-playlists: No match in 4 queries for track abc-radio: 'take your vibes and go' - 'Kito', 'Kah- Lo', 'Baauer', 'brazy'
# 2024-10-18 19:20:40,908 - WARNING  - music-playlists: No match in 80 service tracks for queries ['kito kah lo baauer brazy take your vibes and go', 'kito kah lo baauer take your vibes and go', 'kito kah lo take your vibes and go', 'kito take your vibes and go']
# 2024-10-18 19:20:40,969 - WARNING  - music-playlists: No match in 1 queries for track abc-radio: 'Roxanne' - 'South Summit'
# 2024-10-18 19:20:40,969 - WARNING  - music-playlists: No match in 20 service tracks for queries ['south summit roxanne']
# 2024-10-18 19:20:41,155 - WARNING  - music-playlists: No match in 1 queries for track abc-radio: 'BRITNEY IN '03' - 'REDD.'
# 2024-10-18 19:20:41,155 - WARNING  - music-playlists: No match in 20 service tracks for queries ['redd. britney in 03']
# 2024-10-18 19:20:41,248 - WARNING  - music-playlists: No match in 1 queries for track abc-radio: 'STUPID' - 'YG'
# 2024-10-18 19:20:41,248 - WARNING  - music-playlists: No match in 20 service tracks for queries ['yg stupid']
# 2024-10-18 19:20:41,443 - WARNING  - music-playlists: No match in 1 queries for track abc-radio: 'Stuff I Don't Need {Ft. BANKS}' - 'Kimbra'
# 2024-10-18 19:20:41,443 - WARNING  - music-playlists: No match in 5 service tracks for queries ['kimbra stuff i dont need {ft. banks}']
# 2024-10-18 19:20:41,482 - WARNING  - music-playlists: No match in 2 queries for track abc-radio: 'Hollywood' - 'Toro Y Moi', 'Ben Gibbard'
# 2024-10-18 19:20:41,482 - WARNING  - music-playlists: No match in 10 service tracks for queries ['toro y moi ben gibbard hollywood', 'toro y moi hollywood']
# 2024-10-18 19:20:42,071 - WARNING  - music-playlists: No match in 1 queries for track abc-radio: 'Bothering Me' - 'Sarah Blasko'
# 2024-10-18 19:20:42,071 - WARNING  - music-playlists: No match in 20 service tracks for queries ['sarah blasko bothering me']
# 2024-10-18 19:20:42,338 - WARNING  - music-playlists: No match in 1 queries for track abc-radio: 'Stuff I Don't Need {Ft. BANKS}' - 'Kimbra'
# 2024-10-18 19:20:42,338 - WARNING  - music-playlists: No match in 20 service tracks for queries ['kimbra stuff i dont need {ft. banks}']
# 2024-10-18 19:20:42,553 - WARNING  - music-playlists: No match in 2 queries for track abc-radio: 'Hollywood' - 'Toro Y Moi', 'Ben Gibbard'
# 2024-10-18 19:20:42,553 - WARNING  - music-playlists: No match in 40 service tracks for queries ['toro y moi ben gibbard hollywood', 'toro y moi hollywood']
# 2024-10-18 19:20:44,462 - WARNING  - music-playlists: No match in 1 queries for track abc-radio: 'ON THE MOVE! feat. Tiana Khasi' - 'Close Counters'
# 2024-10-18 19:20:44,462 - WARNING  - music-playlists: No match in 5 service tracks for queries ['close counters on the move! feat. tiana khasi']
