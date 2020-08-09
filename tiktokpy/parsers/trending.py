from typing import Any, Dict, List, Optional, Union

from parsel import Selector

from tiktokpy.utils.logger import logger


class FeedItemsParser:
    def __init__(self, htmls: List[str]):
        self.htmls = htmls

    def _parse_actions(self, action_value: str) -> int:
        if "M" in action_value:
            # Example: 5.1M
            # Remove "M" from value and cast to float
            new_value = float(action_value[:-1])
            new_value = int(new_value * 1_000_000)
        elif "K" in action_value:
            # Example: 5.1K
            # Remove "K" from value and cast to float
            new_value = float(action_value[:-1])
            new_value = int(new_value * 1_000)
        else:
            new_value = int(action_value)

        return new_value

    def loads(self) -> List[Dict[str, Any]]:
        result = []

        for html in self.htmls:
            self.selector = Selector(text=html, type="html", base_url="https://www.tiktok.com/")

            body = {
                "avatar": self.avatar(),
                "title": self.title(),
                "user_info": self.user_info(),
                "music_info": self.music_info(),
                "statistics": self.statistics(),
                "video_info": self.video_info(),
            }

            result.append(body)
        logger.debug(f"Parsed {len(self.htmls)} trending items")

        return result

    def avatar(self) -> str:
        img = self.selector.css(".avatar > img")
        if not img:
            logger.warning("Avatar src not found")
            return ""

        return img.attrib["src"]

    def statistics(self) -> Dict[str, int]:
        likes = self.selector.css('.pc-action-bar strong[title="like"]::text').get(0)
        comments = self.selector.css('.pc-action-bar strong[title="comment"]::text').get(0)
        shares = self.selector.css('.pc-action-bar strong[title="share"]::text').get(0)

        return {
            "likes": self._parse_actions(likes),
            "comments": self._parse_actions(comments),
            "shares": self._parse_actions(shares),
        }

    def video_info(self) -> Dict[str, Optional[str]]:
        link = self.selector.css("a.item-video-card-wrapper").attrib["href"]
        _id = link.split("/")[-1]
        video_url = self.selector.css(".video-player")
        if video_url:
            video_url = video_url.attrib["src"]

        return {
            "id": _id,
            "link": link,
            "video_url": video_url or None,
        }

    def title(self) -> str:
        title = self.selector.css(".item-meta-title > strong::text").get("")

        return title

    def music_info(self) -> Dict[str, str]:
        title = self.selector.css(".music-title-content::text").get("")
        link = self.selector.css(".music-info a").attrib["href"]

        return {
            "title": title,
            "link": link,
        }

    def user_info(self) -> Dict[str, Union[str, bool]]:
        username = self.selector.css(".user-username::text").get("")
        nickname = self.selector.css(".user-nickname::text").get("")
        is_verified = bool(self.selector.css(".verified"))

        return {
            "username": username,
            "nickname": nickname,
            "is_verified": is_verified,
        }
