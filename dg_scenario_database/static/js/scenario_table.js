
function getTagHTML(tag) {
  tagHTML = '<div class="tag badge bg-secondary">' + tag;
  if (loggedIn) {
    tagHTML += '<span class="tag-remove-btn">x</span>';
  }
  tagHTML += '</div>';
  return tagHTML;
}

// Function to add a new tag
function addTag(inputElement, newTag, scenario_id) {
  if (newTag) {
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
          tagHTML = getTagHTML(newTag);
          inputElement.replaceWith(tagHTML);
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

$(document).ready(function () {

	const table = $('#scenario_table').DataTable({
		dom: "<'row'<'col-sm-12 col-md-4'l><'col-sm-12 col-md-4 category-dropdown-wrapper'<'category-label'><'category-dropdown'>><'col-sm-12 col-md-4'f>>" +
		"<'row'<'col-sm-12'tr>>" +
		"<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
		processing: true,
		serverSide: true,
    order: [[4, "asc"], [1, "asc"]],
		pagingType: "full_numbers",
		lengthMenu: [ [20, 50, 100, -1], [20, 50, 100, "All"] ],
		jQueryUI: true,
		ajax: {
			url: '/get_scenario_data',
			data: function (d) {
				d.selected_category = $('#category-filter').val();
			}
		},
		columns: [
			{data: "ID", visible: false},
			{data: "Title"},
			{data: "Teaser"},
			{data: "Author"},
			{data: "Year"},
			{data: "Category"},
			{data: "Tags", render: function (data) {
				var tagsHtml = '';
				data.forEach(function (tag) {
					tagsHtml += getTagHTML(tag);
				});
				return tagsHtml;
			}},
			{data: "Votes", render: function (data) {
				n_votes = data[0];
				upvoted = data[1];
				html = '<div class="row upvote_field"><div class="col-auto upvote_count">' + n_votes + '</div>';
				if (loggedIn) {
					html += '<div class="col text-right"><svg height="16" width="16"><polygon points="8,1 1,15 15,15" class="upvote_delta';
					if (upvoted) {
						html += ' upvoted';
					}
					html += '"/></svg></div>';
				}
				html += '</div>';
				return html;
			}},
		],
		createdRow: function (row, data, dataIndex) {
			var tagsCell = $(row).find('td:eq(5)');
			tagsCell.addClass('tag_cell');
		}
	});

  $('#category-filter').on('change', function () {
    table.ajax.reload();
  })

  $('.category-label').text('Categories displayed: ');
  $('#category-filter').appendTo('.category-dropdown'); // add dropdown to table header

  if (loggedIn) {
    // Add click event for removing tags
    $('#scenario_table').on('click', '.tag-remove-btn', function () {
      const tag = $(this).closest('.tag');
      const tagText = tag.text().trim().slice(0, -1).trim();
      const tagCell = tag.parent()
      const row = table.row(tagCell.parent())
      const scenario_id = row.data()['ID']
      console.log(scenario_id);
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

        input.autocomplete({
          source: existingTags,
          minLength: 0,
          select: function (event, ui) {
            event.preventDefault();
            $(this).val(ui.item.value);
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

        // Remove input when the input loses focus
        input.on('blur', function () {
          $(this).remove();
        });

        // Add the new tag when the user presses Enter
        input.on('keydown', function (event) {
          if (event.keyCode === 13) { // Enter key
            event.preventDefault();
            const newTag = $(this).val().trim();
            const row = table.row($(this).parents('tr'));
            const id = row.data()['ID'];
            addTag($(this), newTag, id);
          }
        });
      }
    });

    // add click event for upvoting
    $('#scenario_table').on('click', '.upvote_delta', function () {
      row = table.row($(this).parents('tr'));
      scenario_id = row.data()['ID'];
      const count = $(this).parents('.upvote_field').children('.upvote_count');
      if (!$(this).hasClass('upvoted')) {
        // add vote
        $(this).addClass('upvoted');
        count.html(parseInt(count.html()) + 1);
        $.ajax({
          url: '/vote',
          method: 'POST',
          contentType: 'application/json',
          data: JSON.stringify({
            scenario_id: scenario_id,
            vote: 'add'
          }),
          success: function (response) {
            if (!response.success) {
              console.error('Upvote unsuccesfull');
            } else {
            }
          },
          error: function (jqXHR, textStatus, errorThrown) {
            console.error('AJAX error:', textStatus, errorThrown);
          }
        });
      } else {
        // remove vote
        $(this).removeClass('upvoted');
        count.html(parseInt(count.html()) - 1);
        $.ajax({
          url: '/vote',
          method: 'POST',
          contentType: 'application/json',
          data: JSON.stringify({
            scenario_id: scenario_id,
            vote: 'remove'
          }),
          success: function (response) {
            if (!response.success) {
              console.error('Removal unsuccesfull');
            } else {
            }
          },
          error: function (jqXHR, textStatus, errorThrown) {
            console.error('AJAX error:', textStatus, errorThrown);
          }
        });
      }
    });
  }

});

