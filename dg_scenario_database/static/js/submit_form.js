$(document).ready(function () {
  function split (val) {
    return val.split(/,\s*/);
  }

  function extractLast(term) {
    return split(term).pop();
  }

  $('#tags')
    .on("keydown", function(event) {
      if (event.key === "Enter" || event.keyCode === $.ui.keyCode.TAB) {
        var term = extractLast(this.value);
        if (term != "") {
          event.preventDefault();
        }
      }
    })
    .autocomplete({
      minLength: 0,
      source: function (request, response) {
        response($.ui.autocomplete.filter(existingTags, extractLast(request.term)));
      },
      focus: function() {
        return false;
      },
      select: function(event, ui) {
        var terms = split(this.value);
        terms.pop();
        terms.push(ui.item.value);
        terms.push("");
        this.value = terms.join(", ");
        return false;
      },
      create: function () {
        $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
          return $('<li>')
            .append($('<div>').addClass('dropdown-item').text(item.label))
            .appendTo(ul.addClass('dropdown-menu'));
        };
      },
    });
});
