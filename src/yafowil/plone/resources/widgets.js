if (window.yafowil === undefined) {
    window.yafowil = {};
}

(function($, yafowil) {
    "use strict";

    $(document).ready(function() {
        if (window.yafowil.array === undefined) {
            return;
        }
        var hooks = window.yafowil.array.hooks;
        for (var name in yafowil.arraypatterns) {
            var pattern = yafowil.arraypatterns[name];
            for (var hookname in yafowil.array.hooks) {
                if (pattern[hookname] !== undefined) {
                    var hook = pattern[hookname].bind(pattern);
                    hooks[hookname]['patterns_' + name + '_' + hookname] = hook;
                }
            }
            pattern.initialize();
        }
    });

    $.extend(yafowil, {

        arraypatterns: {

            relations: {
                selector: 'input.relateditems',
                source: 'array-relateditems',
                target: 'pat-relateditems',

                initialize: function() {
                    var relations = $(this.selector, document);
                    this.prepare_data(relations);
                },

                add: function(row) {
                    var relations = $(this.selector, row);
                    if (!relations.length) {
                        return;
                    }
                    this.prepare_data(relations);
                    require('pat-registry').scan(relations);
                },

                prepare_data: function(relations) {
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
                }
            },

            richtext: {
                selector: 'select.plonearrayrichtext',
                source: 'array-textareamimetypeselector',
                target: 'pat-textareamimetypeselector',

                initialize: function() {
                    var mimetype_selectors = $(this.selector, document);
                    var that = this;
                    mimetype_selectors.each(function() {
                        var mt_sel = $(this);
                        if (mt_sel.parents('.arraytemplate').length) {
                            return;
                        }
                        var data = mt_sel.data(that.source);
                        var name = $('textarea', mt_sel.parent()).attr('name');
                        data.textareaName = name;
                        mt_sel.removeClass(that.source)
                              .removeData(that.source)
                              .addClass(that.target)
                              .data(that.target, data);
                    });
                },

                before_add: function(row, container) {
                    this.destroy_editors(container);
                    var mt_sel = $(this.selector, row);
                    if (!mt_sel.length) {
                        return;
                    }
                    var data = mt_sel.data(this.source);
                    mt_sel.removeClass(this.source)
                          .removeData(this.source)
                          .addClass(this.target)
                          .data(this.target, data);
                },

                before_up: function(row) {
                    this.destroy_editors(row.parent());
                },

                before_down: function(row) {
                    this.destroy_editors(row.parent());
                },

                remove: function(row) {
                    this.destroy_editors(row.parent());
                },

                index: function(row, index) {
                    var mt_sel = $(this.selector, row);
                    if (!mt_sel.length) {
                        return;
                    }
                    if (mt_sel.parents('.arraytemplate').length) {
                        return;
                    }
                    var data = mt_sel.data(this.target);
                    if (!data) {
                        return;
                    }
                    var name = $('textarea', mt_sel.parent()).attr('name');
                    data.textareaName = name;
                    //mt_sel.data(this.target, data);
                    console.log('scan now');
                    console.log(mt_sel.data(this.target));
                    require('pat-registry').scan(mt_sel);
                    mt_sel.val('text/html');
                },

                destroy_editors: function(container) {
                    $(this.selector, container).each(function() {
                        var sel = $(this);
                        var ta = $('textarea', sel.parent());
                        var editor = tinymce.get(ta.attr('id'));
                        if (editor) {
                            console.log('destroy editor');
                            console.log(editor);
                            editor.destroy();
                        }
                    });
                },
            }
        }
    });

})(jQuery, yafowil);
