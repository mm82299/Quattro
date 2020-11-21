odoo.define('product_configurator_custom.ProductConfiguratorFormRendererCustom', function (require) {
"use strict";

var FormRenderer = require('web.FormRenderer');
var VariantMixin = require('sale.VariantMixin');

var ProductConfiguratorFormRendererCustom = FormRenderer.extend(VariantMixin, {

    events: _.extend({}, FormRenderer.prototype.events, VariantMixin.events, {
        'click button.js_add_cart_json': 'onClickAddCartJSON',
        'change input.variant_custom_value': 'onClickgetValue',
        'change div.o_input_dropdown' : 'onchangetemplate'
    }),

    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.pricelistId = this.state.context.default_pricelist_id || 0;
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self.$el.append($('<div>', {class: 'configurator_container'}));
            self.renderConfigurator(self.configuratorHtml);
            self._checkMode();
        });
    },

    onchangetemplate: function (ev){
        this.att_1 = null
        this.att_2 = null
        this.att_3 = null

    },
    onClickgetValue: function (ev) {
        var self = this;
        var $target = $(ev.currentTarget);
        var attribut_name = $target.parents('li.variant_attribute ').data('attribute_name')
        // var attribut_id = $target.parents('li.variant_attribute ').data('attribute_id')
        var att_1
        var att_2
        var att_3
        var sum
        if (attribut_name == 'Length' || attribut_name == 'Longueur'){
            this.att_1 = parseFloat($target.val())}
        if (attribut_name == 'Width' || attribut_name == 'Largeur'){
            this.att_2 = parseFloat($target.val())}
        if (attribut_name == 'Pr' || attribut_name == 'Profondeur'){
            this.att_3 = parseFloat($target.val())
        }
        if (this.att_1){
            this.sum = this.att_1
        }
        if (this.att_1 && this.att_2){
            this.sum = this.att_1 * this.att_2
        }
        if (this.att_1 && this.att_2 && this.att_3){
            var new_val
            new_val = (this.att_1 + this.att_2)
            this.sum = (new_val * 2) * this.att_3
        }
        if (this.sum){
            this.$el.find('input[name="coif_total"]').val(this.sum)
        }
    },
    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Renders the product configurator within the form
     *
     * Will also:
     *
     * - add events handling for variant changes
     * - trigger variant change to compute the price and other
     *   variant specific changes
     *
     * @param {string} configuratorHtml the evaluated template of
     *   the product configurator
     */
    renderConfigurator: function (configuratorHtml) {
        var $configuratorContainer = this.$('.configurator_container');
        $configuratorContainer.empty();

        var $configuratorHtml = $(configuratorHtml);
        $configuratorHtml.appendTo($configuratorContainer);

        this.triggerVariantChange($configuratorContainer);
        this._applyCustomValues();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * If the configuratorMode in the given context is 'edit', we need to
     * hide the regular 'Add' button to replace it with an 'EDIT' button.
     *
     * If the configuratorMode is set to 'options', we will directly open the
     * options modal.
     *
     * @private
     */
    _checkMode: function () {
        if (this.state.context.configuratorMode === 'edit') {
            this.$('.o_sale_product_configurator_add').hide();
            this.$('.o_sale_product_configurator_edit').css('display', 'inline-block');
        } else if (this.state.context.configuratorMode === 'options') {
            this.trigger_up('handle_add');
        }
    },

    /**
     * Toggles the add button depending on the possibility of the current
     * combination.
     *
     * @override
     */
    _toggleDisable: function ($parent, isCombinationPossible) {
        VariantMixin._toggleDisable.apply(this, arguments);
        $parent.parents('.modal').find('.o_sale_product_configurator_add').toggleClass('disabled', !isCombinationPossible);
    },

    /**
     * Will fill the custom values input based on the provided initial configuration.
     *
     * @private
     */
    _applyCustomValues: function () {
        var self = this;
        var customValueIds = this.state.data.product_custom_attribute_value_ids;
        if (customValueIds) {
            _.each(customValueIds.data, function (customValue) {
                if (customValue.data.custom_value) {
                    var attributeValueId = customValue.data.custom_product_template_attribute_value_id.data.id;
                    var $input = self._findRelatedAttributeValueInput(attributeValueId);
                    $input
                        .closest('li[data-attribute_id]')
                        .find('.variant_custom_value')
                        .val(customValue.data.custom_value);
                }
            });
        }
    },

    /**
     * Find the $.Element input/select related to that product.attribute.value
     *
     * @param {integer} attributeValueId
     *
     * @private
     */
    _findRelatedAttributeValueInput: function (attributeValueId) {
        var selectors = [
            'ul.js_add_cart_variants input[data-value_id="' + attributeValueId + '"]',
            'ul.js_add_cart_variants option[data-value_id="' + attributeValueId + '"]'
        ];

        return this.$(selectors.join(', '));
    }
});

return ProductConfiguratorFormRendererCustom;

});
