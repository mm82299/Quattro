# -*- coding: utf-8 -*-

from odoo import models

#----------------------------------------------------------
# Products
#----------------------------------------------------------
class ProductTemplate(models.Model):
    _inherit = "product.template"


    def name_get(self):
        res = super(ProductTemplate, self).name_get()
        return [(template.id, '%s' % (template.name))
                for template in self]
