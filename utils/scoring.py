
from collections import Counter

def get_result_animal(scores):
    most_common = Counter(scores).most_common(1)
    most_score = most_common[0][0] if most_common else 0
    score_to_animal = {
        1: {"name": "Сурикат", "description": "Ты командный игрок и душа компании."},
        2: {"name": "Выдра", "description": "Ты весел, обожаешь воду."},
        3: {"name": "Ленивец", "description": "Ты любишь покой и гамак."},
        4: {"name": "Манул", "description": "Ты скрытный и независимый."},
        5: {"name": "Козёл", "description": "Упрямый, независимый и харизматичный!"},
        6: {"name": "Шиншилла", "description": "Ты ценишь уют и перекусы."},
        7: {"name": "Слон", "description": "Ты добрый и мудрый гигант."},
        8: {"name": "Тигр", "description": "Ты — мощный лидер, охотник по жизни."},
        9: {"name": "Лев", "description": "Ты прирождённый правитель и вдохновитель."}
    }
    return score_to_animal.get(most_score, {
        "name": "Сцинк", "description": "Ты уникальный и редкий, как сцинк."
    })
