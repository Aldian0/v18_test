# -*- coding: utf-8 -*-
# from odoo import http


# class DsBaseTransaksi(http.Controller):
#     @http.route('/ds_base_transaksi/ds_base_transaksi', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ds_base_transaksi/ds_base_transaksi/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ds_base_transaksi.listing', {
#             'root': '/ds_base_transaksi/ds_base_transaksi',
#             'objects': http.request.env['ds_base_transaksi.ds_base_transaksi'].search([]),
#         })

#     @http.route('/ds_base_transaksi/ds_base_transaksi/objects/<model("ds_base_transaksi.ds_base_transaksi"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ds_base_transaksi.object', {
#             'object': obj
#         })

