if (window.yafowil === undefined) {
    window.yafowil = {};
}

(function($, yafowil) {
    "use strict";

    $(document).ready(function() {
        if (window.yafowil.array !== undefined) {
            var hooks = window.yafowil.array.hooks;
            for (var name in yafowil.arraypatterns) {
                var pattern = yafowil.arraypatterns[name];
                if (pattern.add !== undefined) {
                    var hook = pattern.add.bind(pattern);
                    hooks.add['patterns_' + name + '_add'] = hook;
                }
                if (pattern.update !== undefined) {
                    var hook = pattern.update.bind(pattern);
                    hooks.update['patterns_' + name + '_update'] = hook;
                }
                pattern.initialize();
            }
        }
    });

    $.extend(yafowil, {

        arraypatterns: {

            relations: {
                selector: 'input.relateditems',
                source: 'array-relateditems',
                target: 'pat-relateditems',

                initialize: function() {
                    this._initialize_relations(document);
                },

                add: function(row) {
                    var relations = this._initialize_relations(row);
                    if (!relations.length) {
                        return;
                    }
                    require('pat-registry').scan(relations);
                },

                _initialize_relations: function(context) {
                    var relations = $(this.selector, context);
                    var that = this;
                    relations.each(function() {
                        var relation = $(this);
                        if (relation.parents('.arraytemplate').length) {
                            return;
                        }
                        var data = relation.data(that.source);
                        relation.removeClass(that.source)
                                .removeData(that.source)
                                .addClass(that.target)
                                .data(that.target, data);
                    });
                    return relations;
                }
            },

            richtext: {
                selector: 'select.plonearrayrichtext',
                source: 'array-textareamimetypeselector',
                target: 'pat-textareamimetypeselector',

                initialize: function() {
                    this._initialize_richtexts(document);
                },

                add: function(row) {
                    var richtexts = this._initialize_richtexts(row);
                    if (!richtexts.length) {
                        return;
                    }
                    require('pat-registry').scan(richtexts);
                },

                update: function(row, index) {
                    var richtext = $(this.selector, row);
                    if (!richtext.length) {
                        return;
                    }
                    if (richtext.parents('.arraytemplate').length) {
                        return;
                    }
                    var data = richtext.data(this.target);
                    if (!data) {
                        return;
                    }
                    var name = $('textarea', richtext.parent()).attr('name');
                    data.textareaName = name;
                },

                _initialize_richtexts: function(context) {
                    var richtexts = $(this.selector, context);
                    var that = this;
                    richtexts.each(function() {
                        var richtext = $(this);
                        if (richtext.parents('.arraytemplate').length) {
                            return;
                        }
                        var data = richtext.data(that.source);
                        var name = $('textarea', richtext.parent()).attr('name');
                        data.textareaName = name;
                        richtext.removeClass(that.source)
                                .removeData(that.source)
                                .addClass(that.target)
                                .data(that.target, data);
                    });
                    return richtexts;
                }
            }
        }
    });

})(jQuery, yafowil);
