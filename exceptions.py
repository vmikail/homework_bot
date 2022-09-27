class HomeworkStatusError(Exception):
    """Исключение, если статус домашней работы отсутсвует в словаре
    вердиктов"""
    pass


class APIResponseError(Exception):
    """Исключение, если код ответа от сервера API != 200"""
    pass


class HomeworkTypeError(Exception):
    """Исключение, если от API в качестве homewroks получили не словарь"""
    pass


class JsonError(Exception):
    """Исключение для ошибок при соединении с енд-поинт"""
    pass


class APIAnswerKeyError(Exception):
    """Исключение для ошибок при использовании несуществующих ключей"""
    pass


class SendMessageError(Exception):
    """Исключение для ошибок отправки сообщения"""
    pass


class ApiConnectionError(Exception):
    """Исключение для ошибок отправки сообщения"""
    pass
