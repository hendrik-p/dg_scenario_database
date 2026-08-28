
const personIcon = '<svg class="meta-icon" viewBox="0 0 16 16" width="12" height="12" fill="currentColor"><path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2 1H6a4 4 0 0 0-4 4v1a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-1a4 4 0 0 0-4-4z"/></svg>';
const calendarIcon = '<svg class="meta-icon" viewBox="0 0 16 16" width="12" height="12" fill="currentColor"><path d="M4 0a.5.5 0 0 1 .5.5V1h7V.5a.5.5 0 0 1 1 0V1h.5A1.5 1.5 0 0 1 14.5 2.5v11A1.5 1.5 0 0 1 13 15H3a1.5 1.5 0 0 1-1.5-1.5v-11A1.5 1.5 0 0 1 3 1h.5V.5A.5.5 0 0 1 4 0zM2.5 6v7.5a.5.5 0 0 0 .5.5h10a.5.5 0 0 0 .5-.5V6h-11z"/></svg>';
const folderIcon = '<svg class="meta-icon" viewBox="0 0 16 16" width="12" height="12" fill="currentColor"><path d="M1 3.5A1.5 1.5 0 0 1 2.5 2h3.379a1.5 1.5 0 0 1 1.06.44l1.122 1.12A1.5 1.5 0 0 0 9.121 4H13.5A1.5 1.5 0 0 1 15 5.5v6A1.5 1.5 0 0 1 13.5 13h-11A1.5 1.5 0 0 1 1 11.5v-8z"/></svg>';

const sortOptions = [
  {label: 'Title (A-Z)', col: 1, dir: 'asc'},
  {label: 'Title (Z-A)', col: 1, dir: 'desc'},
  {label: 'Author (A-Z)', col: 3, dir: 'asc'},
  {label: 'Year (newest first)', col: 4, dir: 'desc'},
  {label: 'Year (oldest first)', col: 4, dir: 'asc'},
  {label: 'Votes (most first)', col: 7, dir: 'desc'},
  {label: 'Votes (least first)', col: 7, dir: 'asc'},
];
const DEFAULT_SORT_INDEX = 4; // Year (oldest first) - matches the table's initial order

function getTagHTML(tag) {
  tagHTML = '<div class="tag">' + tag;
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
		dom: "<'row toolbar-row'" +
			"<'col-12 col-md-6 toolbar-left'l<'sort-dropdown-wrapper'<'sort-label'><'sort-dropdown'>>>" +
			"<'col-12 col-md-6 toolbar-right'<'category-dropdown-wrapper'<'category-label'><'category-dropdown'>>f>" +
			">" +
		"<'row'<'col-sm-12'tr>>" +
		"<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
		processing: false,
		serverSide: true,
		searchDelay: 400,
    order: [[sortOptions[DEFAULT_SORT_INDEX].col, sortOptions[DEFAULT_SORT_INDEX].dir], [1, "asc"]],
		pagingType: "full_numbers",
		lengthMenu: [ [20, 50, 100, -1], [20, 50, 100, "All"] ],
    pageLength: 50,
		jQueryUI: true,
		language: {
			searchPlaceholder: "Search scenarios...",
		},
		ajax: {
			url: '/get_scenario_data',
			data: function (d) {
				d.selected_category = $('#category-filter').val();
			}
		},
		columns: [
			{data: "ID", visible: false},
			{data: "Title", className: "title-cell"},
			{data: "Teaser", className: "teaser-cell", render: function (data) {
				return '<span class="teaser-text">' + data + '</span><span class="teaser-toggle">Show more</span>';
			}},
			{data: "Author", className: "meta-cell", render: function (data, type, row) {
				var html = '<span class="meta-item">' + personIcon + '<span>' + data + '</span></span>';
				html += '<span class="meta-item">' + calendarIcon + '<span>' + row.Year + '</span></span>';
				html += '<span class="meta-item">' + folderIcon + '<span>' + row.Category + '</span></span>';
				return html;
			}},
			{data: "Year", visible: false},
			{data: "Category", visible: false},
			{data: "Tags", render: function (data) {
				var tagsHtml = '';
				data.forEach(function (tag) {
					tagsHtml += getTagHTML(tag);
				});
				return tagsHtml;
			}},
			{data: "Votes", className: "votes-cell", render: function (data) {
				n_votes = data[0];
				upvoted = data[1];
				label = n_votes === 1 ? 'vote' : 'votes';
				html = '<div class="votes-block">';
				if (loggedIn) {
					html += '<svg height="14" width="14" class="upvote-icon"><polygon points="7,1 1,13 13,13" class="upvote_delta';
					if (upvoted) {
						html += ' upvoted';
					}
					html += '"/></svg>';
				}
				html += '<div class="upvote_count">' + n_votes + '</div>';
				html += '<div class="votes-label">' + label + '</div>';
				html += '</div>';
				return html;
			}},
		],
		createdRow: function (row, data, dataIndex) {
			var tagsCell = $(row).find('td:eq(3)');
			tagsCell.addClass('tag_cell');
		},
		drawCallback: function () {
			$('#scenario_table td.teaser-cell').each(function () {
				var $cell = $(this);
				var $text = $cell.find('.teaser-text')[0];
				if ($text.scrollHeight > $text.clientHeight + 1) {
					$cell.find('.teaser-toggle').addClass('visible');
				}
			});
		},
	});

  $('#scenario_table').on('click', '.teaser-toggle', function () {
    const $cell = $(this).closest('.teaser-cell');
    const expanded = $cell.toggleClass('expanded').hasClass('expanded');
    $(this).text(expanded ? 'Show less' : 'Show more');
  });

  $('#category-filter').on('change', function () {
    table.ajax.reload();
  })

  $('.category-label').text('Categories displayed: ');
  $('#category-filter').appendTo('.category-dropdown'); // add dropdown to table header

  const $sortSelect = $('<select id="sort-filter"></select>');
  sortOptions.forEach(function (opt, i) {
    $sortSelect.append($('<option>').val(i).text(opt.label));
  });
  $sortSelect.val(DEFAULT_SORT_INDEX);
  $('.sort-label').text('Sort by: ');
  $sortSelect.appendTo('.sort-dropdown');

  $sortSelect.on('change', function () {
    const opt = sortOptions[$(this).val()];
    table.order([opt.col, opt.dir]).draw();
  });

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
      const count = $(this).parents('.votes-block').children('.upvote_count');
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

