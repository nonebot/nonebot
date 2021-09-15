# 安装

## NoneBot

:::warning 注意
请确保你的 Python 版本 >= 3.7。
:::

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

## go-cqhttp

:::tip 提示
可以参照 [go-cqhttp 帮助中心](https://docs.go-cqhttp.org/) 的使用教程。
:::

从 [release](https://github.com/Mrs4s/go-cqhttp/releases) 界面下载对应系统的 go-cqhttp 可执行文件，并解压。双击或在命令行中运行 `go-cqhttp`（Windows 上为 `go-cqhttp.exe`），在提示选择通信方式时，选择「反向 Websocket 通信」，程序将会自动生成默认配置文件。

打开 go-cqhttp 默认配置文件 `config.yml` 进行简单配置，修改 QQ 账号以及密码。再次运行 go-cqhttp，可能需要根据提示进行扫码或滑块验证，如果得到以下提示则登录成功：

```
[2021-08-12 16:37:01] [INFO]: 登录成功 欢迎使用: blablab
```

:::warning 注意
请尽量下载最新版本的 go-cqhttp，并及时更新。
:::
