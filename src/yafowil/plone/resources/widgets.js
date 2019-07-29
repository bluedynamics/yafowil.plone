if (window.yafowil === undefined) {
    window.yafowil = {};
}

(function($, yafowil) {
    "use strict";

    $(document).ready(function() {
        if (window.yafowil.array !== undefined) {
            $.extend(window.yafowil.array.hooks.add, {
                patterns_array_add: yafowil.arraypatterns.add
            });
            //$.extend(window.yafowil.array.hooks.up, {
            //    patterns_array_add: yafowil.arraypatterns.update
            //});
            //$.extend(window.yafowil.array.hooks.down, {
            //    patterns_array_add: yafowil.arraypatterns.update
            //});
            yafowil.arraypatterns.initialize();
        }
    });

    $.extend(yafowil, {

        // patterns integration for array blueprint
        arraypatterns: {

            mapping: [{
                selector: 'input.relateditems',
                source: 'array-relateditems',
                target: 'pat-relateditems'
            }, {
                selector: 'select.plonerichtext',
                source: 'array-textareamimetypeselector',
                target: 'pat-textareamimetypeselector',

                add_mod: function(context, data) {
                    //console.log('Richtext add modifier');
                    //console.log($('textarea', context).attr('name'));
                    //console.log(data);
                    data.textareaName = $('textarea', context).attr('name');
                },

                update_mod: function(context, data) {
                    //console.log('Richtext update modifier');
                    //console.log($('textarea', context).attr('name'));
                    //console.log(data);
                    //data.textareaName = $('textarea', context).attr('name');
                }
            }],

            initialize: function() {
                $(yafowil.arraypatterns.mapping).each(function() {
                    yafowil.arraypatterns.initialize_pattern(
                        document,
                        this.selector,
                        this.source,
                        this.target,
                        null
                    );
                });
            },

            initialize_pattern: function(context, selector, source, target, data_mod) {
                var elements = $(selector, context);
                elements.each(function() {
                    var el = $(this);
                    // ignore array template
                    if (el.parents('.arraytemplate').length) {
                        console.log('Ignore template');
                        console.log(el)
                        return;
                    }
                    var data = el.data(source);
                    if (data_mod) {
                        data_mod(context, data);
                    }
                    el.removeClass(source);
                    el.removeData(source);
                    el.addClass(target);
                    el.data(target, data);
                });
                return elements;
            },

            update_pattern: function(context, selector, target, data_mod) {
                console.log('update');
                if (!data_mod) {
                    return;
                }
                var elements = $(selector, context);
                elements.each(function() {
                    var el = $(this);
                    var data = el.data(target);
                    data_mod(context, data);
                });
                return elements;
            },

            add: function(row) {
                // scan new row for proper pattern initialization
                $(yafowil.arraypatterns.mapping).each(function() {
                    var elements = yafowil.arraypatterns.initialize_pattern(
                        row,
                        this.selector,
                        this.source,
                        this.target,
                        this.add_mod
                    );
                    if (!elements.length) {
                        return;
                    }
                    require('pat-registry').scan(elements);
                });
            },

            update: function(row) {
                // update row data if necessary
                $(yafowil.arraypatterns.mapping).each(function() {
                    var elements = yafowil.arraypatterns.update_pattern(
                        row,
                        this.selector,
                        this.target,
                        this.update_mod
                    );
                    if (!elements.length) {
                        return;
                    }
                    require('pat-registry').scan(elements);
                });
            }
        }
    });

})(jQuery, yafowil);
