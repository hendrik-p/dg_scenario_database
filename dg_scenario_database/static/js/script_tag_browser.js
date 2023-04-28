$(document).ready(function () {
  $.ajax({
    url: "tag_table_config",
    method: "GET",
    success: function (config) {
      const table = $('#tag_table').DataTable(config);
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
