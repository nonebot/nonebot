# 贡献指南

## 安装

首先 fork 本项目，然后克隆并安装：

```bash
git clone git@github.com:YOUR_USERNAME/nonebot
cd nonebot
pip install -e .   # 注意点号
```

## 测试

目前本项目没有单元测试。如需贡献新功能或修复 bug，请在提交 PR 之前做好测试，并在 PR 中提供测试过程和结果。

## 代码风格

请使用 Flake8 确保代码风格正确：

```bash
flake8 --config .flake8
```

另外，变量、函数、类、方法、模块等的命名应与项目其它部分一致，且含义清晰。以下划线开头的的标识符表示文件内部的定义，不以下划线开头但是注释标明为 `"INTERNAL API"` 的函数和类等也表示模块内部的 API。其余标识符表示 NoneBot 暴露在外的 API，这些 API 应该包含在对应文件的 `__all__`。

### 注释风格

代码的注释风格遵循 [Google Style Docstring](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)，同时参照 [Cheat Sheet](https://github.com/nonebot/nb-autodoc#cheat-sheet) 和项目其他部分进行编写。

## 文档

所有项目文档都在 `/docs` 目录，并使用 [VuePress](https://vuepress.vuejs.org/) 生成网页文件。

其中 `/docs/api` 使用 [nb-autodoc](https://github.com/nonebot/nb-autodoc) 并根据项目源码自动生成，不应该直接修改。

当添加新功能或修改已有功能时，应同时修改源代码的注释部分和 [`changelog.md`](changelog.md) 对应部分；功能尚未发布时，在代码注释中的版本应使用 `master` 标记，在 `changelog.md` 中应填写在 `## master` 二级标题下。

### 测试文档

生成 API 文档：

```bash
pip install .[scheduler]    # 安装 NoneBot 及其全部依赖
pip install git+https://github.com/nonebot/nb-autodoc.git
nb-autodoc nonebot --vuepress
cp -r build/nonebot/* docs/api    # 更新 API 文档
```

确保网页正常生成并能访问：

```bash
yarn install
yarn docs:dev
```

## 提交 PR

在你 fork 的仓库的「Pull requests」页面，点「New pull request」可提交 PR，具体细节请参考网上教程。

请在 PR 中解释该 PR 所做的事情，和相关测试结果等。

最后，感谢你的贡献！
