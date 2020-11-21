# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    origin = fields.Char('Source Document', copy=True,
        help="Reference of the document that generated this purchase order "
             "request (e.g. a sales order)")

    Client = fields.Many2one('res.partner', string="Client")

    Document = fields.Many2one('sale.order', string="Document")


    @api.onchange('origin')
    def _onchange_origin_customer_name(self):
        if self.origin:
            sale_order_no = self.env['sale.order'].search([('name', '=', self.origin )])
            if sale_order_no:
                self.Document = sale_order_no
                self.Client = sale_order_no.partner_id
            else:
                self.Client = ''
        return

    @api.onchange('Document')
    def _onchange_origin_order_customer_name(self):
        if self.Document:
            self.Client = self.Document.partner_id
        else:
            self.Client = ''
        return


class Picking(models.Model):
    _inherit = "stock.picking"

    # supplier_invoice = fields.Many2one('account.move',string="Supplier Invoice")
    Document_frs = fields.Char(string='Document Fournisseur')

