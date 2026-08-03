from abc import ABC, abstractmethod


class StatusProvider(ABC):
    """所有平台 provider 的公共接口。新增平台时继承此类即可,主程序不需要改动。"""

    @abstractmethod
    def connect(self) -> bool:
        """建立连接/校验凭证。成功返回 True。"""
        raise NotImplementedError

    @abstractmethod
    def update_status(self, text: str, icon: str) -> bool:
        """把自定义文字/图标推送为当前状态。成功返回 True。"""
        raise NotImplementedError

    @abstractmethod
    def clear_status(self) -> None:
        """清除当前状态。"""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """释放连接资源。"""
        raise NotImplementedError
