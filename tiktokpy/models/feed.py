from typing import ClassVar, List, Optional

from pydantic import BaseModel, HttpUrl


class AuthorInfo(BaseModel):
    id: str
    username: str
    nickname: str
    avatar: HttpUrl
    signature: str
    is_verified: bool

    class Config:
        fields: ClassVar[dict] = {
            "username": "uniqueId",
            "avatar": "avatarLarger",
            "is_verified": "verified",
        }


class MusicInfo(BaseModel):
    id: str
    title: str
    link: str = ""
    author_name: str = ""
    is_original: bool
    cover: str = ""

    class Config:
        fields: ClassVar[dict] = {
            "is_original": "original",
            "author_name": "authorName",
            "link": "playUrl",
            "cover": "coverLarge",
        }


class StatisticsInfo(BaseModel):
    plays: int
    likes: int
    comments: int
    shares: int

    class Config:
        fields: ClassVar[dict] = {
            "likes": "diggCount",
            "shares": "shareCount",
            "comments": "commentCount",
            "plays": "playCount",
        }


class ChallengeInfo(BaseModel):
    id: str
    title: str
    desc: str
    profile_thumb: str
    profile_medium: str
    profile_larger: str
    cover_thumb: str = ""
    cover_medium: str = ""
    cover_larger: str = ""

    class Config:
        fields: ClassVar[dict] = {
            "profile_thumb": "profileThumb",
            "profile_medium": "profileMedium",
            "profile_larger": "profileLarger",
            "cover_thumb": "coverThumb",
            "cover_medium": "coverMedium",
            "cover_larger": "coverLarger",
        }


class VideoInfo(BaseModel):
    id: str
    height: int
    width: int
    duration: int
    ratio: str
    cover: HttpUrl
    play_addr: Optional[HttpUrl]
    download_addr: Optional[HttpUrl]

    class Config:
        fields: ClassVar[dict] = {
            "play_addr": "playAddr",
            "download_addr": "downloadAddr",
        }

    @property
    def original_video_url(self) -> str:
        return f"https://api2.musical.ly/aweme/v1/playwm/?video_id={self.id}"


class ImageUrls(BaseModel):
    url_list: List[HttpUrl]

    class Config:
        fields: ClassVar[dict] = {"url_list": "urlList"}


class ImageInfo(BaseModel):
    image_height: int
    image_width: int
    image_url: ImageUrls

    class Config:
        fields: ClassVar[dict] = {
            "image_url": "imageURL",
            "image_width": "imageWidth",
            "image_height": "imageHeight",
        }


class ImagePostlInfo(BaseModel):
    cover: ImageInfo
    images: List[ImageInfo]


class FeedItem(BaseModel):
    id: str
    desc: str
    create_time: int
    author: AuthorInfo
    music: MusicInfo
    stats: StatisticsInfo
    video: VideoInfo
    image_post: ImagePostlInfo = None
    challenges: List[ChallengeInfo] = []

    class Config:
        fields: ClassVar[dict] = {"create_time": "createTime", "image_post": "imagePost"}


class FeedItems(BaseModel):
    __root__: List[FeedItem]
