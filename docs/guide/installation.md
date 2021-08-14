# 安装

## NoneBot

> **注意**
>
> 请确保你的 Python 版本 >= 3.7。

可以使用 pip 安装已发布的最新版本：

```bash
pip install nonebot
```

如果你需要使用最新的（可能尚未发布的）特性，可以克隆 Git 仓库后手动安装：

```bash
git clone https://github.com/nonebot/nonebot.git
cd nonebot
python setup.py install
```

以上命令中的 `pip`、`python` 可能需要根据情况换成 `pip3`、`python3`。

## go-cqhttp 插件

> **提示**
>
> 可以参照 [go-cqhttp 帮助中心](https://docs.go-cqhttp.org/) 的使用教程。

从 [release](https://github.com/Mrs4s/go-cqhttp/releases) 界面下载对应系统的 go-cqhttp 可执行文件，并解压。双击 `go-cqhttp.exe`，输入「3」，使用反向 Websocket 通信，按下回车，系统自动生成默认配置文件。

打开 go-cqhttp 默认配置文件 `config.yml` 进行简单配置，修改 QQ 账号以及密码。再次运行 `go-cqhttp.exe`，如果得到以下提示则安装成功。

```
[2021-08-12 16:37:01] [INFO]: 登录成功 欢迎使用: blablab
```

如出现需要认证的信息, 请自行认证设备。

> **提示**
>
> 请尽量下载最新版本的 go-cqhttp，通常建议插件在大版本内尽量及时升级至最新版本。
