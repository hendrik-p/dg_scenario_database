$(document).ready(function () {
  const table = $('#scenario_table').DataTable({
    "order": [[4, "asc"], [1, "asc"]],
    "pageLength" : 50,
    "lengthMenu": [ [20, 50, 100, -1], [20, 50, 100, "All"] ],
    "columns": [
      {data: "id", visible: false},
      {data: "title"},
      {data: "teaser"},
      {data: "author"},
      {data: "year"},
      {data: "tags"},
    ]
  });

  // Add click event for removing tags
  $('#scenario_table').on('click', '.tag-remove-btn', function () {
    const tag = $(this).closest('.tag');
    const tagText = tag.text().slice(0, -1)
    const tagCell = tag.parent()
    const row = table.row(tagCell.parent())
    const scenario_id = row.data()['id']
    $.ajax({
      url: '/remove_tag',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({
        tag: tagText,
        scenario_id: scenario_id,
      }),
      success: function (response) {
        if (response.success) {
          tag.remove();
        }
        else {
          console.error('Failed to remove tag:', response.message);
        }
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.error('AJAX error:', textStatus, errorThrown);
      },
    })
  });

  // Add click event for adding tags
  $('#scenario_table').on('click', '.tag_cell', function (e) {
    if (!$(e.target).is('.tag-remove-btn') && !$(e.target).is('.tag')) {
      const input = $('<input type="text" class="tag-input">');
      $(this).append(input);
      input.focus();

      // Collect all existing tags
      const existingTags = [];
      $('.tag').each(function () {
        const tagText = $(this).text().slice(0, -1); // Remove the "x" from the end
        if (existingTags.indexOf(tagText) === -1) {
          existingTags.push(tagText);
        }
      });

      // Initialize the Autocomplete widget
      input.autocomplete({
        source: existingTags,
        minLength: 0,
        select: function (event, ui) {
          event.preventDefault();
          $(this).replaceWith(`<div class="tag badge bg-secondary">${ui.item.value}<span class="tag-remove-btn">x</span></div>`);
          input.data('selected', true);
        },
        close: function () {
          if (input.data('selected')) {
            $(this).remove();
          }
        },
        create: function () {
          $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
            return $('<li>')
              .append($('<div>').addClass('dropdown-item').text(item.label))
              .appendTo(ul.addClass('dropdown-menu'));
          };
        },
      });

      // Show the suggestions immediately when the input is focused
      input.on('focus', function () {
        $(this).autocomplete('search', '');
      });

      // Add the new tag when the input loses focus
      input.on('blur', function () {
        addTag($(this));
      });

      // Add the new tag when the user presses Enter
      input.on('keydown', function (event) {
        if (event.keyCode === 13) { // Enter key
          event.preventDefault();
          addTag($(this));
        }
      });

      // Function to add a new tag
      function addTag(inputElement) {
        const newTag = inputElement.val().trim();
        if (newTag) {
          const row = table.row(inputElement.parents('tr'))
          const scenario_id = row.data()['id']
          console.log(scenario_id)
          $.ajax({
            url: '/add_tag',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
              tag: newTag,
              scenario_id: scenario_id,
            }),
            success: function (response) {
              if (response.success) {
                inputElement.replaceWith(`<div class="tag badge bg-secondary">${newTag}<span class="tag-remove-btn">x</span></div>`);
              } else {
                console.error('Error adding tag:', response.message);
                inputElement.remove()
              }
            },
            error: function (jqXHR, textStatus, errorThrown) {
              console.error('AJAX error:', textStatus, errorThrown);
              inputElement.remove()
            }
          });
        } else {
          inputElement.remove();
        }
      }
    }
  });
});

