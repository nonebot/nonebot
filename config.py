config = {
    'fallback_command': 'natural_language.process',
    'fallback_command_after_nl_processors': 'ai.tuling123',
    'command_start_flags': ('', '/', '／'),  # Add '' (empty string) here to allow commands without start flags
    'command_name_separators': ('->', '::', '/'),  # Regex
    'command_args_start_flags': ('，', '：', ',', ', ', ':', ': ','[\\s]'),  # Regex
    'command_args_separators': ('，', ',','[\\s]'),  # Regex

    'message_sources': [
        {
            'via': 'coolq_http_api',
            'login_id': '3010897940',
            'superuser_id': '3010897940',
            'api_url': 'http://qqbot.wvps.pw:5700',
            'token': ''
        }
    ]
}
