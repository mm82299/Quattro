from ast import literal_eval
from odoo import api, models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoice_paid_amount = fields.Float(compute='_get_invoice_paid_amount', string='Payment Amount', help='This field will give the payment amount of the particular customer.')

    #For getting the invoice paid amount of the customer
    def _get_invoice_paid_amount(self):
        for record in self:
            total_amount = 0.0
            invoice_paid_ids = self.env['account.payment'].sudo().search([('partner_id', '=', record.id)])
            if invoice_paid_ids:
                for invoice in invoice_paid_ids:
                    total_amount += invoice.amount
                    record.invoice_paid_amount = total_amount
            else:
                record.invoice_paid_amount = 0





    def open_partner_history(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment History',
            'view_mode': 'tree',
            'res_model': 'account.payment',
            'domain': [('partner_id', '=', self.id)],
            'context': "{'create': False}"
        }

