# -*- coding: utf-8 -*-
# from odoo import http


# class SourceDocExtension(http.Controller):
#     @http.route('/source_doc_extension/source_doc_extension/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/source_doc_extension/source_doc_extension/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('source_doc_extension.listing', {
#             'root': '/source_doc_extension/source_doc_extension',
#             'objects': http.request.env['source_doc_extension.source_doc_extension'].search([]),
#         })

#     @http.route('/source_doc_extension/source_doc_extension/objects/<model("source_doc_extension.source_doc_extension"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('source_doc_extension.object', {
#             'object': obj
#         })
