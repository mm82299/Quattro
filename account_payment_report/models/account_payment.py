# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = "account.payment"
    _description = "Payments"

    document_number = fields.Char(string="Numero de la Piéce")
    maturity_date = fields.Date(string='Echeance', copy=False, tracking=True)
    type_document_id = fields.Many2one('document.type', string="Type Piéce")
    type_bank_id = fields.Many2one('document.bank', string="Banque")
    cheque_owner = fields.Char(string="Propriétaire du compte")
    payment_lines = fields.One2many('account.payment.invoice.report.lines', 'payment_id', string="Payement Lines")
    amount = fields.Monetary("Montant", compute="set_line_group")
    # amount = fields.Float(string="Montant", compute="set_line_group")
    # amount_line=[]
    @api.onchange('payment_lines')
    def set_line_group(self):
        for rec in self:
            bundle = rec.payment_lines
            lst_price = 0.0
            for each in bundle:
                lst_price += each.amount
            rec.write({'amount': lst_price})


class AccountPaymentLines(models.Model):
    _name = "account.payment.invoice.report.lines"
    _description = "Payments Lines"

    type_document_id = fields.Many2one('document.type', string="Type Piéce", tracking=True)
    document_number = fields.Char(string="Numéro de la Piéce", tracking=True)
    type_bank_id = fields.Many2one('document.bank', string="Banque", tracking=True)
    maturity_date = fields.Date(string='Echeance', copy=False, tracking=True)
    cheque_owner = fields.Char(string="Propriétaire du compte", track_visibility="onchange")
    amount = fields.Float(string="Montant", digits=(12,3))
    payment_id = fields.Many2one('account.payment.invoice.report', string="Payement ID")

class DocumentType(models.Model):
    _name = "document.type"
    _description = "Document Type"

    name = fields.Char(string="Name")
    document_help = fields.Char(string="Help")


class DocumentBank(models.Model):
    _name = "document.bank"
    _description = "Document Bank"

    name = fields.Char(string="Name")
    document_help = fields.Char(string="Help")

    #name = fields.Char(string="Name")
    #document_help = fields.Char(string="Help")


