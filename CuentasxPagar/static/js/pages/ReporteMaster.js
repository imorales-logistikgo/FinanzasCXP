$(document).ready(function() {
  $('#TablaReporteMaster').DataTable({
    "scrollX": true,
"scrollY": "400px",
 "language": {
   "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
 },
 "responsive": false,
 "paging": false,
 "dom": 'Bfrtip',
 "buttons": [
 {
   extend: 'excel',
   text: '<i class="fas fa-file-excel fa-lg"></i>',
   exportOptions: {
    columns: ':visible'
   }
 }
],
columnDefs: [
{
    "targets": 6,
    "mRender": function (data, type, full) {
      return (full[6] == 1 ? "Si":"No");
    }
},
{
    "targets": 7,
    "mRender": function (data, type, full) {
      return (full[7] == 1 ? "Si":"No");
    }
},
{
    "targets": 14,
    "mRender": function (data, type, full) {
      return (full[14] == 1 ? "Si":"No");
    }
},
{
    "targets": 21,
    "mRender": function (data, type, full) {
      return (full[21] == 1 ? "Si":"No");
    }
}
]

  });
})
