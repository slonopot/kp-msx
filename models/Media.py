class Media:

    def __init__(self, data):
        self.title = data.get('title')
        self.n = data.get('number')
        self.season = data.get('snumber')

    def to_subtitle(self):
        return f'[S{self.season}/E{self.n}] {self.title}'
