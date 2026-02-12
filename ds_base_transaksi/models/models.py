# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class ds_base_transaksi(models.Model):
#     _name = 'ds_base_transaksi.ds_base_transaksi'
#     _description = 'ds_base_transaksi.ds_base_transaksi'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

