# 部署

## 基本部署

NoneBot 所基于的 aiocqhttp 库使用的 web 框架是 Quart，因此 NoneBot 的部署方法和 Quart 一致（[Deploying Quart](https://pgjones.gitlab.io/quart/tutorials/deployment.html)）。

Quart 官方建议使用 Hypercorn 来部署，这需要一个 ASGI app 对象，在 NoneBot 中，可使用 `nonebot.get_bot().asgi` 获得 ASGI app 对象。

具体地，通常在项目根目录下创建一个 `run.py` 文件如下：

```python
import os
import sys

import nonebot

import config

nonebot.init(config)
bot = nonebot.get_bot()
app = bot.asgi

if __name__ == '__main__':
    bot.run()
```

然后使用下面命令部署：

```python
hypercorn run:app
```

另外，NoneBot 配置文件的 `DEBUG` 项默认为 `True`，在生产环境部署时请注意修改为 `False` 以提高性能。

## 使用 Docker Compose 与 gocqhttp 同时部署

Docker Compose 是 Docker 官方提供的一个命令行工具，用来定义和运行由多个容器组成的应用。通过建立一个名为 `docker-compose.yml` 的文件，可以将部署过程中需要的参数记录在其中，并由单个命令完成应用的创建和启动。

`docker-compose.yml` 文件的示例如下：

```yaml
version: "3"

services:
  gocqhttp:
    image: pcrbot/gocqhttp:latest
    volumes:
      - ./gocqhttp:/usr/src/app:delegated # 用于保存 gocqhttp 相关文件，请复制 config.yml 等文件到此
    tty: true
    stdin_open: true
    environment:
      - TZ=Asia/Shanghai
    depends_on:
      - awesome-bot

  awesome-bot:
    build: ./awesome-bot # 构建nonebot执行环境，Dockerfile见下面的例子
    expose:
      - "8080"
    environment:
      - TZ=Asia/Shanghai

networks:
  default:
    name: workspace-default
```

部分说明见注释。NoneBot 运行环境由文件 `./awesome-bot/Dockerfile` 控制构建。如果项目中使用了第三方库，可以在这一步骤进行安装。`Dockerfile` 内容例如：

```Dockerfile
FROM python:3.9-alpine
WORKDIR /usr/src/app
RUN pip install --no-cache-dir "nonebot[scheduler]"
COPY . .
CMD ["python", "bot.py"]
```

目录结构应如此：

```
workspace
├── docker-compose.yml
├── gocqhttp/
│   ├── config.yml
│   └── ...
└── awesome-bot/
    ├── Dockerfile
    ├── bot.py
    └── ...
```

上述文件编辑完成后，输入命令 `docker-compose build && docker-compose up` 即可一次性启动 gocqhhtp 和 NoneBot（可通过 `docker-compose up -d` 在后台启动。更多 Docker Compose 用法见 [官方文档](https://docs.docker.com/compose/reference/overview/)。
