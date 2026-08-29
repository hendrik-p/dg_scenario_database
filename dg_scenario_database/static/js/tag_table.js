const tagSortOptions = [
  {label: 'Name (A-Z)', col: 1, dir: 'asc'},
  {label: 'Name (Z-A)', col: 1, dir: 'desc'},
];
const TAG_DEFAULT_SORT_INDEX = 0;

$(document).ready(function () {
  $.ajax({
    url: "tag_table_config",
    method: "GET",
    success: function (config) {
      config.dom = "<'row toolbar-row'<'col-12 col-md-4'l><'col-12 col-md-4 sort-dropdown-wrapper'<'sort-label'><'sort-dropdown'>><'col-12 col-md-4'f>>" +
        "<'row'<'col-sm-12'tr>>" +
        "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>";
      config.pagingType = "full_numbers";
      config.jQueryUI = true;
      config.language = { searchPlaceholder: "Search tags..." };
      config.drawCallback = function () {
        $('#tag_table td.scenarios-cell').each(function () {
          var $cell = $(this);
          var $list = $cell.find('.scenarios-list');
          var rowTops = [];
          $list.children().each(function () {
            if (rowTops.indexOf(this.offsetTop) === -1) {
              rowTops.push(this.offsetTop);
            }
          });
          rowTops.sort(function (a, b) { return a - b; });
          if (rowTops.length > 2) {
            $list[0].style.setProperty('--scenarios-clamp', rowTops[2] + 'px');
            $cell.find('.scenarios-toggle').addClass('visible');
          } else {
            $list[0].style.removeProperty('--scenarios-clamp');
            $cell.find('.scenarios-toggle').removeClass('visible');
          }
        });
      };

      const table = $('#tag_table').DataTable(config);

      const $sortSelect = $('<select id="tag-sort-filter"></select>');
      tagSortOptions.forEach(function (opt, i) {
        $sortSelect.append($('<option>').val(i).text(opt.label));
      });
      $sortSelect.val(TAG_DEFAULT_SORT_INDEX);
      $('.sort-label').text('Sort by: ');
      $sortSelect.appendTo('.sort-dropdown');

      $sortSelect.on('change', function () {
        const opt = tagSortOptions[$(this).val()];
        table.order([opt.col, opt.dir]).draw();
      });

      $('#tag_table').on('click', '.scenarios-toggle', function () {
        const $cell = $(this).closest('.scenarios-cell');
        const expanded = $cell.toggleClass('expanded').hasClass('expanded');
        $(this).text(expanded ? 'Show less' : 'Show more');
      });

      $('#tag_table').on('click', '.btn', function() {
        const row = $(this).parents('tr');
        const name = table.row(row).data()['tag'];
        const id = table.row(row).data()['id'];
        $.ajax({
          url: '/remove_tag_from_database',
          method: 'POST',
          contentType: 'application/json',
          data: JSON.stringify({
            tag_id: id,
            tag_name: name,
          }),
          success: function (response) {
            if (response.success) {
              row.remove();
            } else {
              console.error('Failed to remove tag from database:', response.message);
            }
          },
          error: function (jqXHR, textStatus, errorThrown) {
            console.error('AJAX error:', textStatus, errorThrown);
          }
        })
      });
    }
  })
});
