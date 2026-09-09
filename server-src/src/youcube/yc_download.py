#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YouCube download-mode dispatcher.

Normal YouCube requests include width/height and are routed to
yc_download_videos.py.

YouCube --no-video requests omit width/height and are routed to
yc_download_AudioOnly.py.
"""

from yc_download_videos import (
    DATA_FOLDER,
    FFMPEG_PATH,
    SANJUUNI_PATH,
    download as download_video_mode,
)
from yc_download_AudioOnly import download as download_audio_only_mode


def download(
    url,
    resp,
    loop,
    width,
    height,
    spotify_url_processor,
):
    """Route each media request to the correct downloader."""
    if width is None or height is None:
        return download_audio_only_mode(
            url,
            resp,
            loop,
            None,
            None,
            spotify_url_processor,
        )

    return download_video_mode(
        url,
        resp,
        loop,
        width,
        height,
        spotify_url_processor,
    )
