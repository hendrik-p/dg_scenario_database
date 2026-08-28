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
