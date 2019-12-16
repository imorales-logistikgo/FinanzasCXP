$(document).ready(function(){
  var idPago;


  formatDataTable();

  $('#btnAplicarFiltro').on('click', getPagosByFilters);

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
   SaveComplementosPago();
 });

 $('#ModalComplementos').on('shown.bs.modal', function(){
   $('#ComplementosPagos').data("rutaarchivoPDF", "");
   $('#ComplementosPagos').data("rutaarchivoXML", "");
 });


  KTUtil.ready(function() {
    var id = '#ComplementosPagos';
    var verComp = '.uploaded-files-new';
    KTUppyEvidencias.init(id, verComp);
  });


  $(document).on('click', '#btnComplementos', function() {
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
    fnCancelarPago($(this).data('idpago'));
    var table = $('#TableReportePagos').DataTable();
    table.row($(this).parents('tr')).remove().draw();
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

function SaveComplementosPago()
{
  if($('#ComplementosPagos').data("rutaarchivoPDF") != "" && $('#ComplementosPagos').data("rutaarchivoXML") != "")
  {
    alert("It's correct");
  }
  else
  {
    alert("There is a error");
  }
}

function getPagosByFilters() {
  arrProveedor = $('#cboProveedor').val();
  strMoneda = [];
  $('#rdMXN').is(':checked') ? strMoneda.push('MXN') : null;
  $('#rdUSD').is(':checked') ? strMoneda.push('USD') : null;
  WaitMe_Show('#TbPading');
  if($('#chkMonthYear').is(':checked')){
    arrMonth = $('#filtroxMes').val();
    Year = $('#filtroxAno').val();
    getPagos("arrMonth="+ JSON.stringify(arrMonth) +"&Year="+ Year +"&Proveedor="+ JSON.stringify(arrProveedor) +"&Moneda="+ JSON.stringify(strMoneda));
  }
  else{
    startDate = ($('#cboFechaDescarga').data('daterangepicker').startDate._d).toLocaleDateString('en-US');
    endDate = ($('#cboFechaDescarga').data('daterangepicker').endDate._d).toLocaleDateString('en-US');
    getPagos("FechaPagoDesde="+ startDate +"&FechaPagoHasta="+ endDate +"&Proveedor="+ JSON.stringify(arrProveedor) +"&Moneda="+ JSON.stringify(strMoneda));
  }
}

function getPagos(params) {
  fetch("/ReportePagos/FilterBy?" + params, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    return response.clone().json();
  }).then(function(data){
    $('#TbPading').html(data.htmlRes);
    formatDataTable()
    WaitMe_Hide('#TbPading');
  }).catch(function(ex){
    console.log("no success!");
  });
}

function formatDataTable() {
$('#TableReportePagos').DataTable({
    "scrollX": '100%',
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
      "targets": [4,5],
      "width": "9%",
      "className": "dt-head-center dt-body-right"
    },
    {
      "targets": [6,7],
      "visible": false
    },
    {
      "targets": 8,
      "width": "2%",
      "className": "dt-head-center dt-body-center",
      "mRender": function (data, type, full) {
        return  (full[6]!= "" && full[7]!= "" ? `<a href="${full[6]}" target="_blank" class="btn btn-primary btn-elevate btn-pill btn-sm"><i class="flaticon2-file"></i></a>`:'');
      }
    },
    {
      "targets": 9,
      "width": "2%",
      "className": "dt-head-center dt-body-center",
      "mRender": function (data, type, full) {
        return  `<button type ="button" id="btnComplementos" class="btn btn-success btn-elevate btn-pill btn-sm" data-vercomplementoxml="${full[6]}" data-vercomplementopdf="${full[7]}" data-toggle="modal" data-target="#ModalComplementos" data-backdrop="static" data-keyboard="false"><i class="fas fa-upload"></i></button>`;
      }
    },

    {
      "targets": 10,
      "width": "2%",
      "className": "dt-head-center dt-body-center",
      "mRender": function (data, type, full) {
        idPago = $('input[name="IDPago"]').data("pagoid");
        return  '<button type ="button" class="btnEliminarPago btn btn-danger btn-elevate btn-pill btn-sm" data-idpago="'+idPago+'"><i class="flaticon-delete"></i></button>';
      }
    },
    ]
  });
}

var fnCancelarPago = function (IDPago) {
  var res;
  jParams = {
    IDPago: IDPago,
  }
  fetch("/ReportePagos/CancelarPago", {
    method: "PATCH",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify(jParams)
  }).then(function(response){
    if(response.status == 200)
    {
      res = true;
    }
    else if(response.status == 500)
    {
      res = false;
    }
  }).catch(function(ex){
    res = false;
  });
}
