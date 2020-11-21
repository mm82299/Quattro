from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class HnConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_tax = fields.Boolean(string="Timbre Fiscal")
    amount_tax = fields.Monetary(string="Montant")
    sales_tax_account = fields.Many2one('account.account', string="TVA Vente")
    purchase_tax_account = fields.Many2one('account.account', string="TVA Achat")

    def get_values(self):
        ks_res = super(HnConfigSettings, self).get_values()
        ks_res.update(
            enable_tax=self.env['ir.config_parameter'].sudo().get_param('enable_tax'),
            sales_tax_account=int(self.env['ir.config_parameter'].sudo().get_param('sales_tax_account')),
            purchase_tax_account=int(self.env['ir.config_parameter'].sudo().get_param('purchase_tax_account')),
            amount_tax=float(self.env['ir.config_parameter'].sudo().get_param('amount_tax')),
        )
        return ks_res

    def set_values(self):
        super(HnConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('enable_tax', self.enable_tax)
        if self.enable_tax:
            self.env['ir.config_parameter'].set_param('amount_tax', self.amount_tax)
            self.env['ir.config_parameter'].set_param('sales_tax_account', self.sales_tax_account.id)
            self.env['ir.config_parameter'].set_param('purchase_tax_account', self.purchase_tax_account.id)
