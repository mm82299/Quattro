# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    coif_total = fields.Float(digits='Product Unit of Measure')

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'coif_total')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            #################
            if not line.coif_total:
                line.coif_total=1


            # if line.coif_total > 0:
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id,
                                            (line.product_uom_qty * line.coif_total), product=line.product_id,
                                            partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            # else:
            #     taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
            #                                     product=line.product_id, partner=line.order_id.partner_shipping_id)
            #
            #     line.update({
            #         'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            #         'price_total': taxes['total_included'],
            #         'price_subtotal': taxes['total_excluded'],
            #     })
            # else:
            #     taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            #     line.update({
            #         'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            #         'price_total': taxes['total_included'],
            #         'price_subtotal': taxes['total_excluded'],
            #     })

