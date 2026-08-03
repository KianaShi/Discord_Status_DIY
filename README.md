# 自定义状态展示工具

在 Discord 上展示自己写的"正在玩 XX"状态,不绑定任何真实游戏;附带一个本地学习
计时器(正计时/倒计时)。纯 `tkinter` 做的,没有额外的重框架。

# 直接下载链接
https://github.com/KianaShi/Discord_Status_DIY/releases/latest/download/DiscordStatusDIY.exe

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

或者直接双击 [start.bat](start.bat)(用 `pythonw` 启动,不会弹控制台黑窗口)。

直接运行也没问题,不用提前建 `config.json`——没有配置文件时程序会用空白的默认
配置把窗口打开,输入框是空的,状态会一直显示"○ 尚未连接"(这是正常状态,不是报
错),下方的学习计时器不受影响,可以直接用。

## 配置 Discord 状态

1. 去 <https://discord.com/developers/applications> 创建一个 Application,复制它
   的 Client ID。
2. 打开桌面版 Discord 并保持登录(Rich Presence 需要 Discord 客户端在本地跑着才
   能显示)。
3. 在软件里填好 **App ID** 和**显示文字**。
4. 想换图标的话,点"打开Discord图标上传页面"按钮(会用你填的 App ID 自动拼出
   对应网址跳转过去),在该 Application 的 **Rich Presence -> Art Assets** 页面上
   传一张图标(建议静态 PNG、正方形、512×512 左右;GIF 不会动,不建议用)。注意:
   当前这版软件只推送文字,不会把图标 key 发给 Discord,这个按钮只是给你留的一个
   快捷入口,方便你自己去后台管理素材。
5. 点"保存"(只写配置文件,不会立刻生效)或者直接点"重启"(保存 + 让程序自己重
   新启动一次,一步到位)。

### "启用状态推送"开关

标签页顶部的开关控制这次启动要不要真的去连 Discord。关掉它,存盘重启后这次启动
就会跳过 Discord 连接,状态会显示"○ 已停用(未启用推送)"——想临时不推送又不想
清空已经填好的信息时用这个。

### Client ID 留空会怎样?

不会报错,只是这次启动不会尝试连接 Discord,状态一直显示"○ 尚未连接"。

## 本地学习计时器

界面下方固定显示,和 Discord 无关,纯本地看的:支持正计时和倒计时(倒计时可以填
分钟数),开始/暂停/重置三个按钮。

## 目录说明

```
main.py                  程序入口(GUI)
ui_theme.py              配色、圆角卡片/按钮/开关这些自定义控件
timer_widget.py          学习计时器组件
start.bat                双击启动用的快捷方式(pythonw,无控制台窗口)
providers/base.py        Provider 抽象基类
providers/discord_provider.py
config.example.json      配置模板,可以分享
config.json              你的真实配置(不会被 git 追踪)
```

## 隐私 / 开源

- 代码本身不包含任何真实凭证。真实配置存在 `config.json` 里,已经在 `.gitignore`
  里排除,不会随代码一起分享出去。
- 想用的人复制 `config.example.json` 改名成 `config.json`,填自己的信息就能独立
  使用,不会跟你的账号有任何关联。

## 扩展新平台

照着 `providers/base.py` 的 `StatusProvider` 接口(`connect` / `update_status` /
`clear_status` / `close`)新建一个文件实现即可,`main.py` 基本不用改。
