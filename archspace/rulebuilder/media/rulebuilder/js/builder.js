$(document).ready(function() {
    function add_conditional(conditional, slot) {
        var new_conditional = conditional.clone();
        var parentprefix = slot.parents('table').eq(1).find('tr :input[name$="prototype"]:first').attr('name');
        if (parentprefix) {
            parentprefix = parentprefix.substring(0, parentprefix.length-'prototype'.length);
        } else {
            parentprefix = '';
        }
        var count_field = $(':input[name="'+parentprefix+'subform_count"]');
        var count = parseInt(count_field.val()) + 1;
        new_conditional.find(':input').each(function() {
            var original_name = $(this).attr('name');
            original_name = original_name.substring('_proto-'.length);
            $(this).attr('name', count + '-' + parentprefix + original_name);
        });
        var new_table = $('<tr><td></td><td><a href="#" class="deletelink">Remove</a></td></tr>');
        new_table.find('td:first').append(new_conditional);
        new_table.insertBefore(slot);
        count_field.val(count);
    }
    $('.rulebuilder .deletelink').live('click', function() {
        $(this).parents('tr:first').remove();
        return false;
    });
    $('.rulebuilder .addlink').live('click', function() {
        var prototype = $(this).parents('.rulebuilder:first').find('.available_prototypes > .'+$(this).parents('tr:first').find('select').val());
        var insert_before = $(this).parents('tr:first')
        add_conditional(prototype, insert_before);
        return false;
    });
});
