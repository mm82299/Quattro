from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class HntimbreFiscale(models.Model):
    _inherit = "account.move"
    global_tax_rate = fields.Float(string='Timbre Fiscal',default=lambda self: self.env['ir.config_parameter'].sudo().get_param('amount_tax'),readonly=True,
                                    states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    amount_global_tax = fields.Monetary(string="Timbre Fiscal", readonly=True, compute='_compute_amount',
                                         track_visibility='always', store=True)
    enable_tax = fields.Boolean(compute='verify_tax')
    sales_tax_account = fields.Integer(compute='verify_tax')
    purchase_tax_account = fields.Integer(compute='verify_tax')

    @api.depends('name')
    def verify_tax(self):
        for rec in self:
            rec.enable_tax = rec.env['ir.config_parameter'].sudo().get_param('enable_tax')
            rec.sales_tax_account = rec.env['ir.config_parameter'].sudo().get_param('sales_tax_account')
            rec.purchase_tax_account = rec.env['ir.config_parameter'].sudo().get_param('purchase_tax_account')

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'global_tax_rate')
    def _compute_amount(self):
        for rec in self:
            res = super(HntimbreFiscale, rec)._compute_amount()
            rec.calculate_tax()
            rec.update_universal_tax()
            sign = rec.type in ['in_refund', 'out_refund'] and -1 or 1
            rec.amount_total_company_signed = rec.amount_total * sign
            rec.amount_total_signed = rec.amount_total * sign
        return res

    def calculate_tax(self):
        for rec in self:
            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            if rec.global_tax_rate != 0.0 and rec.type in type_list:
                rec.amount_global_tax = (  rec.global_tax_rate)
            else:
                rec.amount_global_tax = 0.0
            rec.amount_total = rec.amount_global_tax + rec.amount_total

    def update_universal_tax(self):
        for rec in self:
            already_exists = self.line_ids.filtered(
                lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
            already_exists = self.line_ids.filtered(
                lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
            terms_lines = self.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            other_lines = self.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
            if already_exists:
                amount = rec.amount_global_tax
                if rec.sales_tax_account \
                        and (rec.type == "out_invoice"
                             or rec.type == "out_refund") \
                        and rec.global_tax_rate > 0:
                    if rec.type == "out_invoice":
                        already_exists.update({
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        })
                    else:
                        already_exists.update({
                            'debit': amount > 0.0 and amount or 0.0,
                            'credit': amount < 0.0 and -amount or 0.0,
                        })
                if rec.purchase_tax_account \
                        and (rec.type == "in_invoice"
                             or rec.type == "in_refund") \
                        and rec.global_tax_rate > 0:
                    if rec.type == "in_invoice":
                        already_exists.update({
                            'debit': amount > 0.0 and amount or 0.0,
                            'credit': amount < 0.0 and -amount or 0.0,
                        })
                    else:
                        already_exists.update({
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        })
                total_balance = sum(other_lines.mapped('balance'))
                total_amount_currency = sum(other_lines.mapped('amount_currency'))
                terms_lines.update({
                    'amount_currency': -total_amount_currency,
                    'debit': total_balance < 0.0 and -total_balance or 0.0,
                    'credit': total_balance > 0.0 and total_balance or 0.0,
                })
            if not already_exists and rec.global_tax_rate > 0:
                in_draft_mode = self != self._origin
                if not in_draft_mode:
                    rec._recompute_universal_tax_lines()
                print()
    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        res = super(HntimbreFiscale, self)._prepare_refund(invoice, date_invoice=None, date=None,
                                                              description=None, journal_id=None)
        print(res)
        return res

    @api.onchange('global_tax_rate', 'line_ids')
    def _recompute_universal_tax_lines(self):
        for rec in self:
            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            if rec.global_tax_rate > 0 and rec.type in type_list:
                if rec.is_invoice(include_receipts=True):
                    in_draft_mode = self != self._origin
                    ks_name = "Timbre Fiscal"
                    ks_name = ks_name + \
                              " @ " + str(self.global_tax_rate)
                    # ks_name = ks_name + " for " + \
                    #           ("Invoice No: " + str(self.ids)
                    #            if self._origin.id
                    #            else (self.display_name))
                    terms_lines = self.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                    already_exists = self.line_ids.filtered(
                        lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
                    if already_exists:
                        amount = self.amount_global_tax
                        if self.sales_tax_account \
                                and (self.type == "out_invoice"
                                     or self.type == "out_refund"):
                            already_exists.update({
                                'name': ks_name,
                                'debit': amount < 0.0 and -amount or 0.0,
                                'credit': amount > 0.0 and amount or 0.0,
                            })
                        if self.purchase_tax_account \
                                and (self.type == "in_invoice"
                                     or self.type == "in_refund"):
                            already_exists.update({
                                'name': ks_name,
                                'debit': amount > 0.0 and amount or 0.0,
                                'credit': amount < 0.0 and -amount or 0.0,
                            })
                    else:
                        new_tax_line = self.env['account.move.line']
                        create_method = in_draft_mode and \
                                        self.env['account.move.line'].new or \
                                        self.env['account.move.line'].create

                        if self.sales_tax_account \
                                and (self.type == "out_invoice"
                                     or self.type == "out_refund"):
                            amount = self.amount_global_tax
                            dict = {
                                'move_name': self.name,
                                'name': ks_name,
                                'price_unit': self.amount_global_tax,
                                'quantity': 1,
                                'debit': amount < 0.0 and -amount or 0.0,
                                'credit': amount > 0.0 and amount or 0.0,
                                'account_id': int(self.purchase_tax_account),
                                'move_id': self._origin,
                                'date': self.date,
                                'exclude_from_invoice_tab': True,
                                'partner_id': terms_lines.partner_id.id,
                                'company_id': terms_lines.company_id.id,
                                'company_currency_id': terms_lines.company_currency_id.id,
                            }
                            if self.type == "out_invoice":
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            if in_draft_mode:
                                self.line_ids += create_method(dict)
                                # Updation of Invoice Line Id
                                duplicate_id = self.invoice_line_ids.filtered(
                                    lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
                                self.invoice_line_ids = self.invoice_line_ids - duplicate_id
                            else:
                                dict.update({
                                    'price_unit': 0.0,
                                    'debit': 0.0,
                                    'credit': 0.0,
                                })
                                self.line_ids = [(0, 0, dict)]

                        if self.purchase_tax_account \
                                and (self.type == "in_invoice"
                                     or self.type == "in_refund"):
                            amount = self.amount_global_tax
                            dict = {
                                'move_name': self.name,
                                'name': ks_name,
                                'price_unit': self.amount_global_tax,
                                'quantity': 1,
                                'debit': amount > 0.0 and amount or 0.0,
                                'credit': amount < 0.0 and -amount or 0.0,
                                'account_id': int(self.sales_tax_account),
                                'move_id': self.id,
                                'date': self.date,
                                'exclude_from_invoice_tab': True,
                                'partner_id': terms_lines.partner_id.id,
                                'company_id': terms_lines.company_id.id,
                                'company_currency_id': terms_lines.company_currency_id.id,
                            }

                            if self.type == "in_invoice":
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            self.line_ids += create_method(dict)
                            # updation of invoice line id
                            duplicate_id = self.invoice_line_ids.filtered(
                                lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
                            self.invoice_line_ids = self.invoice_line_ids - duplicate_id

                    if in_draft_mode:
                        # Update the payement account amount
                        terms_lines = self.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                        other_lines = self.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                        total_balance = sum(other_lines.mapped('balance'))
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        terms_lines.update({
                            'amount_currency': -total_amount_currency,
                            'debit': total_balance < 0.0 and -total_balance or 0.0,
                            'credit': total_balance > 0.0 and total_balance or 0.0,
                        })
                    else:
                        terms_lines = self.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                        other_lines = self.line_ids.filtered(
                            lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                        already_exists = self.line_ids.filtered(
                            lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
                        total_balance = sum(other_lines.mapped('balance')) - amount
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        dict1 = {
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        }
                        dict2 = {
                            'debit': total_balance < 0.0 and -total_balance or 0.0,
                            'credit': total_balance > 0.0 and total_balance or 0.0,
                        }
                        self.line_ids = [(1, already_exists.id, dict1), (1, terms_lines.id, dict2)]
                        print()

            elif self.global_tax_rate <= 0:
                already_exists = self.line_ids.filtered(
                    lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
                if already_exists:
                    self.line_ids -= already_exists
                    terms_lines = self.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                    other_lines = self.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
                    total_balance = sum(other_lines.mapped('balance'))
                    total_amount_currency = sum(other_lines.mapped('amount_currency'))
                    terms_lines.update({
                        'amount_currency': -total_amount_currency,
                        'debit': total_balance < 0.0 and -total_balance or 0.0,
                        'credit': total_balance > 0.0 and total_balance or 0.0,
                    })











