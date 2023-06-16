import werkzeug.exceptions as errors

class BaseError(errors.HTTPException):
    pass

class InternalError(BaseError, errors.InternalServerError):
    name = 'INTERNAL_ERROR'

    def __init__(self, message: str):
        super().__init__(description=message)

class BadRequest(BaseError, errors.BadRequest):
    name = 'BAD_REQUEST'

    def __init__(self, message: str):
        super().__init__(description=message)

class NotFound(BaseError, errors.NotFound):
    name = 'NOT_FOUND'

    def __init__(self, message: str):
        super().__init__(description=message)

class Conflict(BaseError, errors.Conflict):
    name = 'CONFLICT'

    def __init__(self, message: str):
        super().__init__(description=message)

class Unauthorized(BaseError, errors.Unauthorized):
    name = 'UNAUTHORIZED'

    def __init__(self, message: str):
        super().__init__(description=message)

class Forbidden(BaseError, errors.Forbidden):
    name = 'FORBIDDEN'

    def __init__(self, message: str):
        super().__init__(description=message)

class TooManyRequests(BaseError, errors.TooManyRequests):
    name = 'TOO_MANY_REQUESTS'

    def __init__(self, message: str):
        super().__init__(description=message)

class OpenAiCommunicationError(BaseError):
    name = 'OPENAI_COMMUNICATION_ERROR'
    code = 200

    def __init__(self):
        super().__init__(description='problema para comunicação com a OpenAI')

class OpenAiRateLimitError(BaseError):
    name = 'OPENAI_RATE_LIMIT_ERROR'
    code = 200

    def __init__(self):
        super().__init__(description='openAI com uso do modelo sobrecarregado, tente mais tarde')

class OpenAiRequestError(BaseError):
    name = 'OPENAI_REQUEST_ERROR'
    code = 200

    def __init__(self):
        super().__init__(description='openAI retornou uma resposta com erro; Falha na request')
