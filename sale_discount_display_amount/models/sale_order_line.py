# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    discount_total = fields.Monetary(
        compute="_compute_amount", string="Discount Subtotal", store=True
    )
    price_total_no_discount = fields.Monetary(
        compute="_compute_amount", string="Subtotal Without Discount", store=True
    )

    def _compute_discount(self):
        for line in self:
            line.price_total_no_discount = 0
            line.discount_total = 0
            if not line.discount:
                line.price_total_no_discount = line.price_total
                continue
            price = line.price_unit
            # Afin de corriger les anciens devis ayant un coefficient =0
            if not line.coif_total:
                line.coif_total = 1
            taxes = line.tax_id.compute_all(
                price,
                line.order_id.currency_id,
                line.product_uom_qty * line.coif_total,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,

            )
            # else:
            #     taxes = line.tax_id.compute_all(
            #         price,
            #         line.order_id.currency_id,
            #         line.product_uom_qty,
            #         product=line.product_id,
            #         partner=line.order_id.partner_shipping_id,
            #
            #     )

            price_total_no_discount = taxes["total_included"]
            discount_total = price_total_no_discount - line.price_total

            line.update(
                {
                    "discount_total": discount_total,
                    "price_total_no_discount": price_total_no_discount,
                }
            )

    @api.depends("product_uom_qty", "discount", "price_unit", "tax_id")
    def _compute_amount(self):
        res = super(SaleOrderLine, self)._compute_amount()
        self._compute_discount()
        return res
