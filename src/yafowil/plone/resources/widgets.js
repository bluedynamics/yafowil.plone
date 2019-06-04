if (window.yafowil === undefined) {
    window.yafowil = {};
}

(function($, yafowil) {
    "use strict";

    $(document).ready(function() {
        if (window.yafowil.array !== undefined) {
            $.extend(window.yafowil.array.hooks.add, {
                references_array_add: yafowil.references.array_add
            });
            yafowil.references.initialize_array_relations(document);
        }
    });

    $.extend(yafowil, {

        references: {
            // array integration for relation blueprint

            initialize_array_relations: function(context) {
                // translate array-relateditems data to pat-relateditems
                var selector = 'input.relateditems';
                var source = 'array-relateditems';
                var target = 'pat-relateditems';
                var relations = $(selector, context);
                relations.each(function() {
                    var el = $(this);
                    // ignore array templates
                    if (el.attr('name').indexOf('.TEMPLATE.') > -1) {
                        return;
                    }
                    var data = el.data(source);
                    el.removeClass(source);
                    el.removeData(source);
                    el.addClass(target);
                    el.data(target, data);
                });
                return relations;
            },

            array_add: function(row) {
                // scan new row. needed for proper relateditems pattern
                // initialization
                var relations = yafowil.references.initialize_array_relations(row);
                if (!relations.length) {
                    return;
                }
                require('pat-registry').scan(relations);
            }
        }
    });

})(jQuery, yafowil);
