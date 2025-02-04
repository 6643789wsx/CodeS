from __future__ import annotations

import asyncio
from typing import Union

from aiohttp import ClientError
from telethon.errors import (
    ChannelPrivateError,
    ChatAdminRequiredError,
    ChatRestrictedError,
    ChatWriteForbiddenError,
    ExternalUrlInvalidError,
    GroupedMediaInvalidError,
    InputUserDeactivatedError,
    MediaEmptyError,
    MediaGroupedInvalidError,
    MediaInvalidError,
    PhotoContentTypeInvalidError,
    PhotoContentUrlEmptyError,
    PhotoCropSizeSmallError,
    PhotoInvalidDimensionsError,
    PhotoInvalidError,
    PhotoSaveFileInvalidError,
    UserIdInvalidError,
    UserIsBlockedError,
    VideoContentTypeInvalidError,
    VideoFileInvalidError,
    WebpageCurlFailedError,
    WebpageMediaEmptyError,
)


class EntityNotFoundError(ValueError):
    def __init__(self, peer: Union[int, str]):
        self.peer = peer
        super().__init__(f"Entity not found: {peer}")


class ContextTimeoutError(asyncio.TimeoutError):
    pass


UserBlockedErrors: tuple = (
    UserIsBlockedError,
    UserIdInvalidError,
    ChatWriteForbiddenError,
    ChannelPrivateError,
    InputUserDeactivatedError,
    ChatAdminRequiredError,
    EntityNotFoundError,
    ChatRestrictedError,
)
InvalidMediaErrors: tuple = (
    PhotoInvalidDimensionsError,
    PhotoSaveFileInvalidError,
    PhotoInvalidError,
    PhotoCropSizeSmallError,
    PhotoContentUrlEmptyError,
    PhotoContentTypeInvalidError,
    GroupedMediaInvalidError,
    MediaGroupedInvalidError,
    MediaInvalidError,
    VideoContentTypeInvalidError,
    VideoFileInvalidError,
    ExternalUrlInvalidError,
)
ExternalMediaFetchFailedErrors: tuple = (
    WebpageCurlFailedError,
    WebpageMediaEmptyError,
    MediaEmptyError,
)
MediaSendFailErrors = InvalidMediaErrors + ExternalMediaFetchFailedErrors


class RetryInIpv4(ClientError):
    def __init__(self, code: int = None, reason: str = None):
        self.code = code
        self.reason = reason
        super().__init__(
            f"{code} {reason}" if code and reason else (code or reason or "")
        )
