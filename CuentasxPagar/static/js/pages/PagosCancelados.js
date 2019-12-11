$(document).ready(function(){
  $('#TableReportePagosCancelados').DataTable({
    "language": {
      "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
    "scrollX": "100%",
    "responsive": true,
    "paging": true,
    "dom": 'Bfrtip',
    "buttons": [
      {
        extend: 'excel',
        text: '<i class="fas fa-file-excel fa-lg"></i>',

      }
    ],
    columnDefs: [
      {
          "targets": [0],
          "width": "10%",
          "className": "dt-head-center dt-body-center"
      },

      {
        "targets": [1,2,3],
        "width": "15%",
        "className": "dt-head-center dt-body-center"
      },

      {
        "targets": 4,
        "width": "12px",
        "className": "dt-head-center dt-body-center"
      },
      {
        "targets": [5,6,7,8,9],
        "width": "12px",
        "className": "dt-head-center dt-body-right"
      },
    ]
  });

  //filtro de fecha solo por mes y año
  $(document).on( 'change', 'input[name="fechaxMesyAño"]', function () {
    if($(this).is(':checked')){
      $('#filtroxMesyAno').css("display", "block");
      $('#fechaRango').hide();
    }
    else
    {
      $('#filtroxMesyAno').css("display", "none");
      $('#fechaRango').show();
    }
  });

});
