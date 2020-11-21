# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import xmltodict
import json
import base64
from odoo import api, fields, models
from itertools import groupby
from operator import itemgetter


class ImportXml(models.TransientModel):
    _name = "import.xml"

    xml_file = fields.Binary("Upload Xml file", attachment=True)
    file_name = fields.Char('File Name')
    skip_warning = fields.Boolean('Skip Warning')
    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.company)
    partner_id = fields.Many2one(
        'res.partner', string='Customer',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)

    def import_xml_record(self):
        data_file = base64.decodestring(self.xml_file)
        parse_dict = xmltodict.parse(data_file)
        master_data = json.dumps(parse_dict)
        master_item = json.loads(master_data).get('Project').get('Design').get('Catalog').get('Item')
        master_featureSet = json.loads(master_data).get('Project').get('Design').get('Catalog').get('FeatureSet')

        ProductProduct = self.env['product.product']
        xml_data_dict = []
        before_order_line = []
        after_order_line = []
        no_product = []
        style=master_featureSet.get('Code')

        grouper = itemgetter("ManufCode")
        result = []
        temp_dict={}
        for key, grp in groupby(sorted(master_item, key=grouper), key=grouper):
            # temp_dict = dict(zip(["ManufCode"], key))
            qty_done = 0
            for ml in grp:
                qty_done += float(ml.get("Quantity"))
                desc=ml.get('Description')
            # temp_dict.update({
            #     'ManufCode': key,
            # })
            # temp_dict.update({
            #     'Quantity': qty_done,
            # })
            xml_data_dict.append({
                'ManufCode': key,
                'Quantity': qty_done,
                'Description': desc,
                'FeatureSetRef': style,
            })

        # from pprintZ import pprint
        # print(result)

        # for item in master_item:
        #     xml_data_dict.append({'Quantity':item.get('Quantity'),
        #                         'ManufCode': item.get('ManufCode'),
        #                         'Description':item.get('Description'),
        #                         # 'FeatureSetRef': item.get('FeatureSetRef')
        #                         'FeatureSetRef': style,
        #                           })
        no_repeat = []
        for product in xml_data_dict:
            search_product = ProductProduct.search(['&',('default_code','=',product.get('ManufCode')),
                                                ('product_template_attribute_value_ids.name','=',product.get('FeatureSetRef'))]
                                                ,limit=1)
            # if not product_product and not self.skip_warning:
            #     msg = '[{}]' .format(product.get('ManufCode'))
            #     msg += "" + "" + "" + product.get('Description')
            #     raise UserError('Product not Found %s' % msg)
            if search_product: #and search_product not in no_repeat:
                before_order_line.append((0, 0, {'product_id': search_product.id,
                                            'name': '[' + search_product.default_code + ']' + (search_product.name).ljust(10) + '(' + product.get('FeatureSetRef') + ')',
                                            'display_type': False,
                                            'product_uom': search_product.product_tmpl_id.uom_id.id,
                                            'product_uom_qty': product.get('Quantity')}))
                # no_repeat.append(search_product)
            if not search_product :#and search_product not in no_repeat:
                msg = '[{}]' .format(product.get('ManufCode')).ljust(10)
                msg += "" + product.get('Description')
                msg += " Quantité=" + str(product.get('Quantity'))
                msg += " Style=" + product.get('FeatureSetRef')
                after_order_line.append((0, 0, {'name':  msg, 'display_type': 'line_note'}))
                # no_product.append({'Quantity':product.get('Quantity'),
                #                     'ManufCode': product.get('ManufCode'),
                #                     'Description':product.get('Description'),
                #                     'FeatureSetRef': product.get('FeatureSetRef')
                #                 })
                # no_repeat.append(search_product)

        # if order_line:
        Quotations = self.env['sale.order'].sudo().create({
            'partner_id': self.partner_id.id,
            'order_line': before_order_line,
            })
        # if len(no_product) > 0:
        #     NewProductID = []
        #     for res in no_product:
        #         new_product_id = ProductProduct.search([('default_code','=', res.get('ManufCode')), ('name','=', res.get('Description'))], limit=1)
        #         if not new_product_id:
        #             new_product_id = self.env['product.product'].create({
        #                 'name': res.get('Description'),
        #                 'type': 'product',
        #                 'default_code': res.get('ManufCode'),
        #             })
        #         NewProductID.append((0, 0, {'product_id': new_product_id.id,
        #                                         'name': '[' + new_product_id.default_code + ']' + new_product_id.name + '(' + res.get('FeatureSetRef') + ')',
        #                                         'display_type': False,
        #                                         'product_uom': new_product_id.product_tmpl_id.uom_id.id,
        #                                         'product_uom_qty': res.get('Quantity')}))
        #         ProductAttributeValue = self.env['product.template.attribute.value'].search([('attribute_id.name','=',res.get('FeatureSetRef')),
        #                                                             ('product_attribute_value_id.name','=',res.get('FeatureSetRef'))], limit=1)
        #         if ProductAttributeValue:
        #             new_product_id.write({'product_template_attribute_value_ids': [(6,0, [ProductAttributeValue.id])]})
        #         else:
        #             product_attribute = self.env['product.attribute'].sudo().create({'name': res.get('FeatureSetRef')})
        #             product_attribute_value = self.env['product.attribute.value'].sudo().create(
        #                             {'name': res.get('FeatureSetRef'),'attribute_id': product_attribute.id})

        #             attribute_line_id = self.env['product.template.attribute.line'].sudo().create({'active': True,
        #                                                         'product_tmpl_id': new_product_id.product_tmpl_id.id,
        #                                                         'attribute_id': product_attribute.id,
        #                                                         'value_ids': [(6,0, [product_attribute_value.id])] })

        self.env['sale.order.line'].create({
            'name': 'Produits non trouvés dans la base ODOO',
            'display_type': 'line_section',
            'order_id': Quotations.id,
        })
        Quotations.write({'order_line': after_order_line})
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }