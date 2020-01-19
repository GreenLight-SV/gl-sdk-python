import json

def get_base_url(stage):
    URLS = {
        'staging': 'https://api.greenlight.ai/staging-ext',
        'test': 'https://api.greenlight.ai/staging-ext',        # test is currently an alias for staging
        'sandbox': 'https://api.greenlight.ai/staging-ext',     # sandbox is currently an alias for staging

        'dev': 'https://api.greenlight.ai/dev-ext',

        'production': 'https://api.greenlight.ai/beta-ext',
        'site': 'https://api.greenlight.ai/beta-ext',           # site is currently an alias for production
        'beta': 'https://api.greenlight.ai/beta-ext'            # beta is currently an alias for production
    }

    if stage in URLS: return URLS[stage]
    raise KeyError(f'Stage {stage} not recognized')

def format_date(date):
    return date.strftime('%Y-%m-%d')

def jsonprint(x):
    print(json.dumps(x, indent=2))

