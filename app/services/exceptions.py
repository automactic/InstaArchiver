class PostNotFound(Exception):
    event_code = 'post_not_found'

    def __init__(self, shortcode):
        self.shortcode = shortcode

    @property
    def message(self):
        return f'Post with shortcode {self.shortcode} does not exist.'

    @property
    def response(self):
        return {'event': self.event_code, 'shortcode': self.shortcode, 'message': self.message}
