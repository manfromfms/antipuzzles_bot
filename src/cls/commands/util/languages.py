class Language:
    def __init__(self, ietf) -> None:
        if ietf is None:
            ietf = 'en'

        self.ietf = ietf

        # Redirect to the closest option (default will be English)
        if self.ietf in ['ru', 'uk', 'be']:
            self.ietf = 'ru'

        else:
            self.ietf = 'en'

        self.texts = {
            'Puzzle': {
                'en': 'Puzzle',
                'ru': 'Задача'
            },
            'Rating': {
                'en': 'Rating',
                'ru': 'Рейтинг'
            },
            'Solved': {
                'en': 'Solved',
                'ru': 'Задача'
            },
            'Game': {
                'en': 'Game',
                'ru': 'Партия'
            },
            'Opening': {
                'en': 'Opening',
                'ru': 'Дебют'
            },
            'Popularity': {
                'en': 'Popularity',
                'ru': 'Оценка'
            },
            'Themes': {
                'en': 'Themes',
                'ru': 'Темы'
            }
        
        }

        self.translations = {}

        print(self.ietf)

        for text in self.texts:
            self.translations[text] = self.texts[text][self.ietf]

