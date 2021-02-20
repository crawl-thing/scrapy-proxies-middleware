# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import requests
from scrapy import signals

import random

from twisted.internet.error import TCPTimedOutError, TimeoutError

from .lib.scrapy_proxies_config.client.py_cli import ProxyFetcher






class FundspiderDownloaderMiddleware(object):
    # def get_redis_conn(**kwargs):
    #     host = kwargs.get('host', settings.get('REDIS_HOST'))
    #     port = kwargs.get('port', settings.get('REDIS_PORT'))
    #     db = kwargs.get('db', settings.get('DEFAULT_REDIS_DB'))
    #     password = kwargs.get('password', settings.get('REDIS_PASSWORD') )
    #     return redis.StrictRedis(host, port, db, password)
    def process_request_back(self, request, spider):
        for proxy_type in self.proxy_types:
            fetcher = ProxyFetcher(proxy_type, strategy=self.strategy, length=self.ip_level)
            self.proxies += fetcher.get_proxies()
        request.meta["proxy"] = random.choice(self.proxies)
        # request.headers["Proxy-Authorization"] = xun.headers

    def __init__(self, settings):
        self.mode = settings.get('PROXY_MODE')
        # 这里从配置选取类型，是要https还是http
        self.proxy_types = settings.get('PROXY_TYPE_LIST', ['https', 'http'])
        self.chosen_proxy = ''
        # ip代理列表
        self.proxies = []
        # 选择ip的复用模式
        self.strategy = settings.get('strategy', 'greedy')
        # ip 成绩等级
        self.ip_level = settings.get('IP_LEVEL', 8)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        pass

    def process_exception(self, request, exception, spider):
        if isinstance(exception, TimeoutError):
            self.process_request_back(request, spider)  # 连接超时才启用代理ip机制
            return request

        elif isinstance(exception, TCPTimedOutError):
            self.process_request_back(request, spider)
            return request
