def get_base_url(stage):
    URLS = {
        'staging': 'https://api.greenlight.ai/staging-ext',
        'production': 'https://api.greenlight.ai/beta-ext'
    }

    if (stage in URLS): return URLS[stage]
    raise KeyError('Stage' + stage + 'not recognized')

