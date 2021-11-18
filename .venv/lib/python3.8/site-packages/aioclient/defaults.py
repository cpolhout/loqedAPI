from aioclient.retries import RetryStrategy


class ClientDefaults:
    TIMEOUT = 30
    HEADERS = {
        'User-Agent': 'AioClient1.0',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate'
    }
    RETRY_STRATEGY = RetryStrategy()
