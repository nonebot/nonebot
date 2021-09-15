module.exports = {
    title: 'NoneBot',
    description: '基于 OneBot（原 CQHTTP）标准的 Python 异步 QQ 机器人框架',
    markdown: {
        lineNumbers: true
    },
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
    ga: 'UA-115509121-2',
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
            { text: 'API', link: '/api.md' },
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
                        'command-session',
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
                    ]
                }
            ],
        },
    }
}
