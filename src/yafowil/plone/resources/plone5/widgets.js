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
        }
    });

    $.extend(yafowil, {


        references: {
            array_add: function(row) {
                // array integration for rlation blueprint
                // translate array-relateditems data to pat-relateditems
                // and scan new row. needed for proper relateditems pattern
                // initialization
                // XXX: ignore array templates if nested arrays in row
                var selector = 'input.relateditems';
                var source = 'array-relateditems';
                var target = 'pat-relateditems';
                var relations = $(selector, row);
                if (!relations.length) {
                    return;
                }
                relations.each(function() {
                    var el = $(this);
                    var data = el.data(source);
                    el.removeClass(source);
                    el.removeData(source);
                    el.addClass(target);
                    el.data(target, data);
                });
                require('pat-registry').scan(relations);
            }
        }
    });

})(jQuery, yafowil);
