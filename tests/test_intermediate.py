import pytest as pytest

from music_playlists import intermediate as inter


_inter_manage = inter.Manage()


@pytest.mark.parametrize(
    "title_a,artists_a,title_b,artists_b,expected",
    [
        (
            "Low Down (part i)",
            ["Michael Kiwanuka"],
            "Lowdown (part i)",
            ["Michael Kiwanuka"],
            True,
        ),
        ("A.I", ["Morukerdu"], "A. I", ["Morukerdu"], True),
        (
            "Wasted Lenses",
            ["Aislinn Sharp"],
            "Wasted Lenses - Radio Edit",
            ["Aislinn Sharp"],
            True,
        ),
        ("Wolves", ["Total Buzzkill"], "Wolves", ["Totalbuzzkill"], True),
        (
            "Walk With Me In Hell",
            ["Lamb Of God"],
            "Walk with Me In Hell",
            ["Lamb of God"],
            True,
        ),
        (
            "Queen Of The Junkyard",
            ["Fat Dog And The Tits"],
            "Queen of the Junkyard",
            ["Fat Dog and The Tits"],
            True,
        ),
    ],
)
def test_match(
    title_a: str,
    artists_a: list[str],
    title_b: str,
    artists_b: list[str],
    expected: bool,
):
    a = inter.Track(
        origin_code="",
        track_id="",
        title=title_a,
        artists=artists_a,
        raw=None,
    )
    available = [
        inter.Track(
            origin_code="",
            track_id="",
            title=title_b,
            artists=artists_b,
            raw=None,
        )
    ]
    actual = _inter_manage.match(a, available, 5)
    if expected is True:
        assert actual is not None
    else:
        assert actual is None


@pytest.mark.parametrize(
    "original_title,expected_title,original_artists,expected_artists",
    [
        (None, "", None, []),
        ("", "", [], []),
        (
            "For My Friends",
            "for my friends",
            ["King Princess"],
            ["king princess"],
        ),
        (
            "SLOW IT DOWN",
            "slow it down",
            ["The Kid LAROI & Quavo"],
            ["the kid laroi", "quavo"],
        ),
        (
            "Going On",
            "going on",
            ["Young Franco, piri & MC DT"],
            ["young franco", "piri", "mc dt"],
        ),
        (
            "GAY 4 ME (feat. Lauren Sanderson)",
            "gay 4 me",
            ["G Flip"],
            ["g flip", "lauren sanderson"],
        ),
        (
            "The Girls (Xero)",
            "the girls",
            ["Devotions"],
            ["devotions", "xero"],
        ),
        (
            "Day In, Day Out (Tape/Off)",
            "day in, day out",
            ["Smallest Horse"],
            ["smallest horse", "tape off"],
        ),
        (
            "It's Not That Bad",
            "its not that bad",
            ["Caroline & Claude"],
            ["caroline", "claude"],
        ),
        (
            "How Do I Know?",
            "how do i know",
            ["Thomas Headon"],
            ["thomas headon"],
        ),
        (
            "Head on Fire",
            "head on fire",
            ["Griff x Sigrid"],
            ["griff", "sigrid"],
        ),
        (
            "bbycakes (with lil uzi vert, pinkpantheress & shygirl)",
            "bbycakes",
            ["mura masa"],
            ["mura masa", "lil uzi vert", "pinkpantheress", "shygirl"],
        ),
        (
            "stuff i dont need {ft. banks}",
            "stuff i dont need",
            ["kimbra"],
            ["kimbra", "banks"],
        ),
        (
            "the baddest (badder)",
            "the baddest",
            ["joey valence", "brae"],
            ["joey valence", "brae", "badder"],
        ),
        (
            "the baddest (badder) [feat. ayesha erotica]",
            "the baddest",
            ["joey valence", "brae"],
            ["joey valence", "brae", "badder", "ayesha erotica"],
        ),
        (
            "for cryin out loud!",
            "for crying out loud",
            ["finneas"],
            ["finneas"],
        ),
        (
            "talk talk featuring troye sivan",
            "talk talk",
            ["charli xcx"],
            ["charli xcx", "troye sivan"],
        ),
        (
            "Low Down (part i)",
            "low down",
            ["Michael Kiwanuka"],
            ["michael kiwanuka", "part i"],
        ),
        (
            "Walk With Me In Hell",
            "walk with me in hell",
            ["Lamb Of God"],
            ["lamb of god"],
        ),
        (
            "Big Dreams",
            "big dreams",
            ["Amyl And The Sniffers"],
            ["amyl", "the sniffers"],
        ),
        (
            "A. I",
            "a i",
            ["Morukerdu"],
            ["morukerdu"],
        ),
    ],
)
def test_intermediate_normalised_track(
    original_title, expected_title, original_artists, expected_artists
):
    n = _inter_manage.normalise_info(original_title, original_artists)
    assert n.title == expected_title
    assert n.artists == expected_artists
