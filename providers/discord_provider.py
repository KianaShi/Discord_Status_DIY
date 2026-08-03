from providers.base import StatusProvider

try:
    from pypresence import Presence
except ImportError:
    Presence = None


class DiscordProvider(StatusProvider):
    """基于 pypresence 的 Discord Rich Presence 实现。

    图标必须是提前在 Discord Developer Portal 的
    Rich Presence -> Art Assets 里上传好的素材 key,这里只是把 key 名字传给
    Discord,不会上传/替换图片本身。
    """

    def __init__(self, client_id: str, details: str, large_image_key: str):
        self.client_id = client_id
        self.details = details
        self.large_image_key = large_image_key
        self.rpc = None
        self.connected = False

    def connect(self) -> bool:
        if Presence is None:
            raise RuntimeError("未安装 pypresence,请先 pip install -r requirements.txt")
        if not self.client_id:
            raise ValueError("Discord Client ID 为空")
        self.rpc = Presence(self.client_id)
        self.rpc.connect()
        self.connected = True
        return True

    def update_status(self, text: str, icon: str) -> bool:
        if not self.connected or self.rpc is None:
            return False
        self.rpc.update(details=text or None, large_image=icon or None)
        return True

    def clear_status(self) -> None:
        if self.connected and self.rpc is not None:
            try:
                self.rpc.clear()
            except Exception:
                pass

    def close(self) -> None:
        if self.rpc is not None:
            try:
                self.rpc.close()
            except Exception:
                pass
        self.connected = False
