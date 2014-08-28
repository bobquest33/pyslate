# -*- coding: utf-8 -*-
"""
Created on Sun Aug 24 21:58:40 2014

@author: Dipanjan
"""

from __future__ import absolute_import
import re
import codecs
from urllib import urlencode
import urllib2 as request
import sys

PY2 = int(sys.version[0]) == 2

class Translator(object):

    """A language translator and detector.

    Usage:
    ::
        >>> from pyslate import Translator
        >>> tr = Translator()
        >>> tr.translate('hello world', from_lang='en', to_lang='de')
        u'hallo Welt'
        >>> t.detect("hallo Welt")
        u'de'
    """

    string_pattern = r"\"(([^\"\\]|\\.)*)\""
    translation_pattern = re.compile(
                        r"\,?\["
                           + string_pattern + r"\,"
                           + string_pattern + r"\,"
                           + string_pattern + r"\,"
                           + string_pattern
                        + r"\]")
    detection_pattern = re.compile(
        r".*?\,\"([a-z]{2}(\-\w{2})?)\"\,.*?", flags=re.S)

    url = "http://translate.google.com/translate_a/t"

    headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) '
            'AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19')}

    def translate(self, source, from_lang='en', to_lang='en', host=None, type_=None):
        """Translate the source text from one language to another."""
        if PY2:
            source = source.encode('utf-8')
        data = {"client": "t", "ie": "UTF-8", "oe": "UTF-8",
                "sl": from_lang, "tl": to_lang, "text": source}
        json5 = self._get_json5(self.url, host=host, type_=type_, data=data)
        return self._get_translation_from_json5(json5)

    def detect(self, source, host=None, type_=None):
        """Detect the source text's language."""
        if PY2:
            source = source.encode('utf-8')
        data = {"client": "t", "ie": "UTF-8", "oe": "UTF-8", "text": source}
        json5 = self._get_json5(self.url, host=host, type_=type_, data=data)
        lang = self._get_language_from_json5(json5)
        return lang

    def _get_language_from_json5(self, content):
        match = self.detection_pattern.match(content)
        if not match:
            return None
        return match.group(1)

    def _get_translation_from_json5(self, content):
        result = u""
        pos = 2
        while True:
            m = self.translation_pattern.match(content, pos)
            if not m:
                break
            result += m.group(1)
            pos = m.end()
        return _unescape(result)

    def _get_json5(self, url, host=None, type_=None, data=None):
        encoded_data = urlencode(data).encode('utf-8')
        req = request.Request(url=url, headers=self.headers, data=encoded_data)
        if host or type_:
            req.set_proxy(host=host, type=type_)
        resp = request.urlopen(req)
        content = resp.read()
        return content.decode('utf-8')


def _unescape(text):
    """Unescape unicode character codes within a string.
    """
    pattern = r'\\{1,2}u[0-9a-fA-F]{4}'
    decode = lambda x: codecs.getdecoder('unicode_escape')(x.group())[0]
    return re.sub(pattern, decode, text)
