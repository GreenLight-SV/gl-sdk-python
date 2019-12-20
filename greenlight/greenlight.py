class GreenLight():
    """GreenLight client"""

    base_url = 'https://api.greenlight.ai'

    def __init__(self, stage, apikey):
        """
        Construct a new client for the GreenLight service
        
        :param str stage: Which API server to use.  Currently 'staging-ext' and 'site-ext' are supported.

        :param apikey: Your secret key for this stage.
        """

        self.stage = stage
        self.apikey = apikey
        

