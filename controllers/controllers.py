# -*- coding: utf-8 -*-
# from odoo import http


# class LeadersApp(http.Controller):
#     @http.route('/leaders_app/leaders_app', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/leaders_app/leaders_app/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('leaders_app.listing', {
#             'root': '/leaders_app/leaders_app',
#             'objects': http.request.env['leaders_app.leaders_app'].search([]),
#         })

#     @http.route('/leaders_app/leaders_app/objects/<model("leaders_app.leaders_app"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('leaders_app.object', {
#             'object': obj
#         })
