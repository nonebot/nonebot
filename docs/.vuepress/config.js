module.exports = {
    title: 'NoneBot',
    description: '基于 OneBot（原 CQHTTP）标准的 Python 异步 QQ 机器人框架',
    markdown: {
        lineNumbers: true
    },
    extendMarkdown(md) {
        md.use(require('markdown-it-attrs'))
    },
    plugins: [
        ['@vuepress/google-analytics', {
            ga: 'UA-115509121-2'
        }]
    ],
    head: [
        ['link', { rel: 'icon', href: `/logo.png` }],
        ['link', { rel: 'manifest', href: '/manifest.json' }],
        ['meta', { name: 'theme-color', content: '#ffffff' }],
        ['meta', { name: 'application-name', content: 'NoneBot' }],
        ['meta', { name: 'apple-mobile-web-app-title', content: 'NoneBot' }],
        ['meta', { name: 'apple-mobile-web-app-capable', content: 'yes' }],
        ['link', { rel: 'apple-touch-icon', href: `/icons/apple-touch-icon.png` }],
        ['link', { rel: 'mask-icon', href: '/icons/safari-pinned-tab.svg', color: '#5bbad5' }],
        ['meta', { name: 'msapplication-TileImage', content: '/icons/mstile-150x150.png' }],
        ['meta', { name: 'msapplication-TileColor', content: '#00aba9' }]
    ],
    themeConfig: {
        repo: 'nonebot/nonebot',
        docsDir: 'docs',
        editLinks: true,
        editLinkText: '在 GitHub 上编辑此页',
        lastUpdated: '上次更新',
        activeHeaderLinks: false,
        nav: [
            { text: 'v2', link: 'https://v2.nonebot.dev' },
            { text: '主页', link: '/' },
            { text: '指南', link: '/guide/' },
            { text: '进阶', link: '/advanced/' },
            { text: 'API', link: '/api/' },
            { text: '术语表', link: '/glossary.md' },
            { text: '更新日志', link: '/changelog.md' },
            { text: '论坛', link: 'https://discussions.nonebot.dev/' },
            { text: '赞助', link: 'https://afdian.net/@nonebot' },
        ],
        sidebar: {
            '/guide/': [
                {
                    title: '指南',
                    collapsable: false,
                    children: [
                        '',
                        'installation',
                        'getting-started',
                        'whats-happened',
                        'basic-configuration',
                        'command',
                        'nl-processor',
                        'ai-chat',
                        'notice-and-request',
                        'onebot',
                        'scheduler',
                        'usage',
                        'whats-next',
                    ]
                }
            ],
            '/advanced/': [
                {
                    title: '进阶',
                    collapsable: false,
                    children: [
                        '',
                        'flow-diagram',
                        // 'command-session', may not be needed
                        'command-argument',
                        'command-group',
                        'message',
                        'permission',
                        'decorator',
                        'database',
                        'server-app',
                        'scheduler',
                        'logging',
                        'configuration',
                        'larger-application',
                        'deployment',
                        'legacy_features',
                    ]
                }
            ],
            '/api/': [
                {
                    title: 'API Reference',
                    collapsable: false,
                    sidebarDepth: 0,
                    children: [
                        {
                            title: 'nonebot 模块',
                            path: './'
                        },
                        {
                            title: 'nonebot.argparse 模块',
                            path: 'argparse'
                        },
                        {
                            title: 'nonebot.default_config 模块',
                            path: 'default_config'
                        },
                        {
                            title: 'nonebot.exceptions 模块',
                            path: 'exceptions'
                        },
                        {
                            title: 'nonebot.helpers 模块',
                            path: 'helpers'
                        },
                        {
                            title: 'nonebot.log 模块',
                            path: 'log'
                        },
                        {
                            title: 'nonebot.message 模块',
                            path: 'message'
                        },
                        {
                            title: 'nonebot.natural_language 模块',
                            path: 'natural_language'
                        },
                        {
                            title: 'nonebot.notice_request 模块',
                            path: 'notice_request'
                        },
                        {
                            title: 'nonebot.permission 模块',
                            path: 'permission'
                        },
                        {
                            title: 'nonebot.plugin 模块',
                            path: 'plugin'
                        },
                        {
                            title: 'nonebot.sched 模块',
                            path: 'sched'
                        },
                        {
                            title: 'nonebot.session 模块',
                            path: 'session'
                        },
                        {
                            title: 'nonebot.typing 模块',
                            path: 'typing'
                        },
                        {
                            title: 'nonebot.command 模块',
                            path: 'command/'
                        },
                        {
                            title: 'nonebot.command.group 模块',
                            path: 'command/group'
                        },
                        {
                            title: 'nonebot.command.argfilter 模块',
                            path: 'command/argfilter/'
                        },
                        {
                            title: 'nonebot.command.argfilter.controllers 模块',
                            path: 'command/argfilter/controllers'
                        },
                        {
                            title: 'nonebot.command.argfilter.converters 模块',
                            path: 'command/argfilter/converters'
                        },
                        {
                            title: 'nonebot.command.argfilter.extractors 模块',
                            path: 'command/argfilter/extractors'
                        },
                        {
                            title: 'nonebot.command.argfilter.validators 模块',
                            path: 'command/argfilter/validators'
                        },
                        {
                            title: 'nonebot.experimental 模块',
                            path: 'experimental/'
                        },
                        {
                            title: 'nonebot.experimental.permission 模块',
                            path: 'experimental/permission'
                        },
                        {
                            title: 'nonebot.experimental.plugin 模块',
                            path: 'experimental/plugin'
                        },
                    ]
                }
            ]
        },
    }
}
