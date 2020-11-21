odoo.define('product_configurator_custom.ProductConfiguratorFormView', function (require) {
"use strict";

var ProductConfiguratorFormController = require('sale_product_configurator.ProductConfiguratorFormController');
var ProductConfiguratorFormRenderer = require('product_configurator_custom.ProductConfiguratorFormRendererCustom');
var FormView = require('web.FormView');
var viewRegistry = require('web.view_registry');

var ProductConfiguratorFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
        Controller: ProductConfiguratorFormController,
        Renderer: ProductConfiguratorFormRenderer,
    }),
});

viewRegistry.add('product_configurator_form', ProductConfiguratorFormView);

return ProductConfiguratorFormView;

});
