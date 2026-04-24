# -*- coding: utf-8 -*-

from werkzeug.urls import url_decode, url_encode, url_parse

from odoo import models
from odoo.http import request
from odoo.tools.misc import str2bool


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls, endpoint):
        cls._sync_content_only_session()
        if cls._should_add_content_only(endpoint):
            parsed = url_parse(request.httprequest.url)
            query_params = url_decode(parsed.query)
            query_params['content_only'] = cls._get_content_only_value()
            new_url = parsed.replace(query=url_encode(query_params)).to_url()
            return cls._redirect(new_url)
        return super()._dispatch(endpoint)

    @classmethod
    def _handle_error(cls, exception):
        cls._sync_content_only_session()
        if cls._should_add_content_only():
            parsed = url_parse(request.httprequest.url)
            query_params = url_decode(parsed.query)
            query_params['content_only'] = cls._get_content_only_value()
            new_url = parsed.replace(query=url_encode(query_params)).to_url()
            return cls._redirect(new_url)
        return super()._handle_error(exception)

    @classmethod
    def _should_add_content_only(cls, endpoint=None):
        if request.httprequest.method not in ('GET', 'HEAD'):
            return False
        if 'content_only' in request.httprequest.args:
            return False
        if request.httprequest.path.startswith('/web'):
            return False
        if endpoint and endpoint.routing.get('type') != 'http':
            return False
        return True

    @classmethod
    def _sync_content_only_session(cls):
        if 'content_only' in request.httprequest.args:
            request.session['portal_content_only'] = cls._parse_content_only(
                request.httprequest.args.get('content_only')
            )

    @classmethod
    def _get_content_only_value(cls):
        if 'content_only' in request.httprequest.args:
            return cls._parse_content_only(request.httprequest.args.get('content_only'))
        return request.session.get('portal_content_only', False)

    @staticmethod
    def _parse_content_only(value):
        return bool(str2bool(value, default=False))
