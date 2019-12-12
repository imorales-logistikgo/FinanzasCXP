$(document).ready(function(){
var idPago;
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
      "targets": [5,6],
      "visible": false
    },
    {
      "targets": 7,
      "width": "2%",
      "className": "dt-head-center dt-body-center",
      "mRender": function (data, type, full) {
        return  (full[5]!= "" && full[6]!= "" ? `<a href="${full[5]}" target="_blank" class="btn btn-primary btn-elevate btn-pill btn-sm"><i class="flaticon2-file"></i></a>`:'');
      }
    },
    {
      "targets": 8,
      "width": "2%",
      "className": "dt-head-center dt-body-center",
      "mRender": function (data, type, full) {
        return  `<button type ="button" id="btnComplementos" class="btn btn-success btn-elevate btn-pill btn-sm" data-vercomplementoxml="${full[5]}" data-vercomplementopdf="${full[6]}" data-toggle="modal" data-target="#ModalComplementos" data-backdrop="static" data-keyboard="false"><i class="fas fa-upload"></i></button>`;
      }
    },

    {
        "targets": 9,
        "width": "2%",
        "className": "dt-head-center dt-body-center",
        "mRender": function (data, type, full) {
        idPago = $('input[name="IDPago"]').data("pagoid");
          return  '<button type ="button" class="btnEliminarPago btn btn-danger btn-elevate btn-pill btn-sm" data-idpago="'+idPago+'"><i class="flaticon-delete"></i></button>';
        }
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

  //rago fecha para el Filtro
  $('input[name="filtroFechaReportePagos"]').daterangepicker({
   autoUpdateInput: false
  });

  $('input[name="filtroFechaReportePagos"]').on('apply.daterangepicker', function(ev, picker) {
    $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
  });

  $('#ModalComplementos').on('hidden.bs.modal', function(){
   $('.uploaded-files-new ol').remove();
   $('.uploaded-files-pagos ol').remove();
   var id = '#ComplementosPagos';
   var verComp = '.uploaded-files-new';
   KTUppyEvidencias.init(id, verComp)
  });


  KTUtil.ready(function() {
    var id = '#ComplementosPagos';
    var verComp = '.uploaded-files-new';
    KTUppyEvidencias.init(id, verComp);
  });


$(document).on('click', '#btnComplementos', function() {
  console.log($(this).data("vercomplementoxml"));
  if($(this).data("vercomplementoxml") != "" && $(this).data("vercomplementopdf") != "")
  {
    $('#alertaComplementos').hide();
    document.querySelector('.uploaded-files-pagos').innerHTML +=
    `<ol><li id="listaArchivos"><a href="${$(this).data("vercomplementoxml")}" target="_blank" name="url" id="RutaXML">XML</a></li></ol>`
    document.querySelector('.uploaded-files-pagos').innerHTML +=
    `<ol><li id="listaArchivos"><a href="${$(this).data("vercomplementopdf")}" target="_blank" name="url" id="RutaPDF">PDF</a></li></ol>`
  }
  else
  {
    $('#alertaComplementos').show();
    $('#alertaComplementos').html('<strong class="alert alert-warning">Este pago no tiene complementos</strong>');
  }
});

//eliminar row de la tabla estados de cuenta
$(document).on( 'click', '.btnEliminarPago', function () {
 Swal.fire({
  title: '¿Estas Seguro?',
  text: "Estas a un click de eliminar un pago importante",
  type: 'warning',
  showCancelButton: true,
  confirmButtonColor: '#3085d6',
  cancelButtonColor: '#d33',
  confirmButtonText: 'Aceptar'
}).then((result) => {
  if (result.value) {
    console.log($(this).data('idpago'));
    Swal.fire(
      'Eliminado!',
      'Eliminado con exito',
      'success'
      )
  }
  //else
  //  alertToastError("Error al eliminar la factura");
})
});


});
