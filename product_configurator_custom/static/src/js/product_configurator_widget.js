odoo.define('product_configurator_custom.product_configurator_custom', function (require) {
var ProductConfiguratorWidget = require('sale_product_configurator.product_configurator');

ProductConfiguratorWidget.include({

    _getMainProductChanges: function (mainProduct) {
        var result = {
            product_id: {id: mainProduct.product_id},
            product_template_id: {id: mainProduct.product_template_id},
            product_uom_qty: mainProduct.quantity,
            coif_total : mainProduct.coif_total
        };

        var customAttributeValues = mainProduct.product_custom_attribute_values;
        var customValuesCommands = [{operation: 'DELETE_ALL'}];
        if (customAttributeValues && customAttributeValues.length !== 0) {
            _.each(customAttributeValues, function (customValue) {
                // FIXME awa: This could be optimized by adding a "disableDefaultGet" to avoid
                // having multiple default_get calls that are useless since we already
                // have all the default values locally.
                // However, this would mean a lot of changes in basic_model.js to handle
                // those "default_" values and set them on the various fields (text,o2m,m2m,...).
                // -> This is not considered as worth it right now.
                customValuesCommands.push({
                    operation: 'CREATE',
                    context: [{
                        default_custom_product_template_attribute_value_id: customValue.custom_product_template_attribute_value_id,
                        default_custom_value: customValue.custom_value
                    }]
                });
            });
        }

        result['product_custom_attribute_value_ids'] = {
            operation: 'MULTI',
            commands: customValuesCommands
        };

        var noVariantAttributeValues = mainProduct.no_variant_attribute_values;
        var noVariantCommands = [{operation: 'DELETE_ALL'}];
        if (noVariantAttributeValues && noVariantAttributeValues.length !== 0) {
            var resIds = _.map(noVariantAttributeValues, function (noVariantValue) {
                return {id: parseInt(noVariantValue.value)};
            });

            noVariantCommands.push({
                operation: 'ADD_M2M',
                ids: resIds
            });
        }

        result['product_no_variant_attribute_value_ids'] = {
            operation: 'MULTI',
            commands: noVariantCommands
        };

        return result;
    },

});

return ProductConfiguratorWidget;

});
