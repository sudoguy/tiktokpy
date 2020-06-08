from typing import List, Optional

from pydantic import BaseModel


class UserInfo(BaseModel):
    username: str
    nickname: str


class MusicInfo(BaseModel):
    title: str
    link: str


class StatisticsInfo(BaseModel):
    likes: int
    comments: int
    shares: int


class VideoInfo(BaseModel):
    id: str
    # link on page
    link: str
    video_url: Optional[str]
    # preview_image: str

    # @property
    # def original_video_url(self) -> str:
    #     return f"https://api2.musical.ly/aweme/v1/playwm/?video_id={self.private_id}"


class FeedItem(BaseModel):
    user_info: UserInfo
    avatar: str
    title: str
    music_info: MusicInfo
    statistics: StatisticsInfo
    video_info: VideoInfo


class FeedItems(BaseModel):
    __root__: List[FeedItem]
