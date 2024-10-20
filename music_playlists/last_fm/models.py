import attrs
from beartype import beartype
from cattrs.gen import make_dict_unstructure_fn, make_dict_structure_fn, override

from music_playlists.intermediate.serialization import c


@beartype
@attrs.frozen
class Artist:
    name: str
    mbid: str
    url: str


@beartype
@attrs.frozen
class Image:
    text: str
    size: str


c.register_unstructure_hook(
    Image, make_dict_unstructure_fn(Image, c, text=override(rename="#text"))
)
c.register_structure_hook(
    Image, make_dict_structure_fn(Image, c, text=override(rename="#text"))
)


@beartype
@attrs.frozen
class Streamable:
    text: str
    fulltrack: str


c.register_unstructure_hook(
    Streamable, make_dict_unstructure_fn(Streamable, c, text=override(rename="#text"))
)
c.register_structure_hook(
    Streamable, make_dict_structure_fn(Streamable, c, text=override(rename="#text"))
)


@beartype
@attrs.frozen
class TrackAttr:
    # https://np.tritondigital.com/public/nowplaying?mountName=NOVA_1069&numberToFetch=11&eventType=track&request.preventCache=1648391310720
    # <?xml version="1.0" encoding="UTF-8"?><nowplaying-info-list><nowplaying-info mountName="NOVA_1069" timestamp="1648387646" type="track"><property name="cue_time_duration"><![CDATA[203918.277]]></property><property name="cue_time_start"><![CDATA[1648387646045]]></property><property name="cue_title"><![CDATA[Intentions]]></property><property name="track_artist_name"><![CDATA[Justin Bieber / Quavo]]></property><property name="track_id"><![CDATA[2ec8906c-adfc-40be-9ab4-655ec06a9590]]></property></nowplaying-info><nowplaying-info mountName="NOVA_1069" timestamp="1648387491" type="track"><property name="cue_time_duration"><![CDATA[157316.0465]]></property><property name="cue_time_start"><![CDATA[1648387491092]]></property><property name="cue_title"><![CDATA[Remember]]></property><property name="track_artist_name"><![CDATA[Becky Hill / David Guetta]]></property><property name="track_id"><![CDATA[502ff921-59e6-4536-b7d9-86c10c9feecf]]></property></nowplaying-info><nowplaying-info mountName="NOVA_1069" timestamp="1648386819" type="track"><property name="cue_time_duration"><![CDATA[189268.0062]]></property><property name="cue_time_start"><![CDATA[1648386819536]]></property><property name="cue_title"><![CDATA[Four Five Seconds]]></property><property name="track_artist_name"><![CDATA[Rihanna / Kanye West / Paul Mccartney]]></property><property name="track_id"><![CDATA[3ced6663-15a6-4248-9f9d-469590b2a0c4]]></property></nowplaying-info><nowplaying-info mountName="NOVA_1069" timestamp="1648386620" type="track"><property name="cue_time_duration"><![CDATA[200246.1234]]></property><property name="cue_time_start"><![CDATA[1648386620595]]></property><property name="cue_title"><![CDATA[Kiss Me More]]></property><property name="track_artist_name"><![CDATA[Doja Cat / Sza]]></property><property name="track_id"><![CDATA[3266f943-f5f8-4238-a6c7-53af6519dff1]]></property></nowplaying-info><nowplaying-info mountName="NOVA_1069" timestamp="1648386166" type="track"><property name="cue_time_duration"><![CDATA[195402.829]]></property><property name="cue_time_start"><![CDATA[1648386166535]]></property><property name="cue_title"><![CDATA[Toxic Pony]]></property><property name="track_artist_name"><![CDATA[Altego / Britney Spears / Ginuwine]]></property><property name="track_id"><![CDATA[5e917cc1-e880-4e92-9883-aeb48d41e2fc]]></property></nowplaying-info><nowplaying-info mountName="NOVA_1069" timestamp="1648385956" type="track"><property name="cue_time_duration"><![CDATA[200630.4152]]></property><property name="cue_time_start"><![CDATA[1648385956556]]></property><property name="cue_title"><![CDATA[Bad Case Of Loving You]]></property><property name="track_artist_name"><![CDATA[Lara D]]></property><property name="track_id"><![CDATA[363328b6-3d3c-4132-8da0-a9ef0771bddf]]></property></nowplaying-info><nowplaying-info mountName="NOVA_1069" timestamp="1648385759" type="track"><property name="cue_time_duration"><![CDATA[196916.6042]]></property><property name="cue_time_start"><![CDATA[1648385759725]]></property><property name="cue_title"><![CDATA[Bloodstone]]></property><property name="track_artist_name"><![CDATA[Guy Sebastian]]></property><property name="track_id"><![CDATA[d9eb4905-4c39-4555-8cb7-2616a6528670]]></property></nowplaying-info><nowplaying-info mountName="NOVA_1069" timestamp="1648385640" type="track"><property name="cue_time_duration"><![CDATA[121018.596]]></property><property name="cue_time_start"><![CDATA[1648385640862]]></property><property name="cue_title"><![CDATA[So Done]]></property><property name="track_artist_name"><![CDATA[The Kid Laroi]]></property><property name="track_id"><![CDATA[e2d362fb-6dde-421b-a917-775f5e6e6d1c]]></property></nowplaying-info><nowplaying-info mountName="NOVA_1069" timestamp="1648385471" type="track"><property name="cue_time_duration"><![CDATA[172068.4396]]></property><property name="cue_time_start"><![CDATA[1648385471229]]></property><property name="cue_title"><![CDATA[Gimme! Gimme! Gimme!]]></property><property name="track_artist_name"><![CDATA[Sgt. Slick]]></property><property name="track_id"><![CDATA[4037e891-c6d8-4b4b-ad2d-deaf0fb08564]]></property></nowplaying-info><nowplaying-info mountName="NOVA_1069" timestamp="1648385271" type="track"><property name="cue_time_duration"><![CDATA[202203.8841]]></property><property name="cue_time_start"><![CDATA[1648385271423]]></property><property name="cue_title"><![CDATA[Black And Gold]]></property><property name="track_artist_name"><![CDATA[Sam Sparro]]></property><property name="track_id"><![CDATA[b1311881-6fec-408a-98dc-0d05917177e6]]></property></nowplaying-info><nowplaying-info mountName="NOVA_1069" timestamp="1648385091" type="track"><property name="cue_time_duration"><![CDATA[180473.6632]]></property><property name="cue_time_start"><![CDATA[1648385091918]]></property><property name="cue_title"><![CDATA[Fallin']]></property><property name="track_artist_name"><![CDATA[Jessica Mauboy]]></property><property name="track_id"><![CDATA[883279cc-160e-4ed7-9c12-aa27d848402d]]></property></nowplaying-info></nowplaying-info-list>

    rank: str


@beartype
@attrs.frozen
class Track:
    name: str
    duration: str
    listeners: str
    mbid: str
    url: str
    streamable: Streamable
    artist: Artist
    image: list[Image]
    attr: TrackAttr


c.register_unstructure_hook(
    Track, make_dict_unstructure_fn(Track, c, attr=override(rename="@attr"))
)
c.register_structure_hook(
    Track, make_dict_structure_fn(Track, c, attr=override(rename="@attr"))
)
