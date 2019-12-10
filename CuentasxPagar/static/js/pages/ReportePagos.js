$(document).ready(function(){

  $('#TableReportePagos').DataTable({
    "scrollX": true,
    "language": {
      "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
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
      "targets": [1,2],
      "width": "10%",
      "className": "dt-head-center dt-body-center"
    },

    {
      "targets": [3],
      "width": "5%",
      "className": "dt-head-center dt-body-right"
    },
    {
      "targets": [4],
      "width": "9%",
      "className": "dt-head-center dt-body-right"
    },

    {
      "targets": 5,
      "width": "2%",
      "className": "dt-head-center dt-body-center",
      "mRender": function (data, type, full) {
        return  '<button type ="button" class="btn btn-success btn-elevate btn-pill btn-sm" data-toggle="modal" data-target="#ModalComplementos" data-backdrop="static" data-keyboard="false"><i class="fas fa-upload"></i></button>';
      }
    },

    {
        "targets": 6,
        "width": "2%",
        "className": "dt-head-center dt-body-center",
        "mRender": function (data, type, full) {
          return  '<button type ="button" class="btnEliminarPago btn btn-danger btn-elevate btn-pill btn-sm"><i class="flaticon-delete"></i></button>';
        }
    }
    ]
  });

  //rago fecha para el Filtro
  $('input[name="filtroFechaReportePagos"]').daterangepicker({
   autoUpdateInput: false
  });

  $('input[name="filtroFechaReportePagos"]').on('apply.daterangepicker', function(ev, picker) {
    $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
  });

  $('#ModalComplementos').on('hidden.bs.modal', function(){
   var id = '#ComplementosPagos';
   var verComp = '.uploaded-files-pagos';
   KTUppyEvidencias.init(id, verComp)
  });


  KTUtil.ready(function() {
    var id = '#ComplementosPagos';
    var verComp = '.uploaded-files-pagos';
    KTUppyEvidencias.init(id, verComp);
  });



});
