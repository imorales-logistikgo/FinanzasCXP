var xml;
var pdf;
$(document).ready(function(){
  formatDataTable();

  $('#btnAplicarFiltro').on('click', getPagosByFilters);

   $(document).on('click', '.btnDetallePago', fnGetDetallePago);

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


  $('input[name="FiltroFechaReportePagosCancelados"]').daterangepicker({
   autoUpdateInput: false,
   showDropdowns:true,
   autoApply:true,
   locale: {
       daysOfWeek: [
           "Do",
           "Lu",
           "Ma",
           "Mi",
           "Ju",
           "Vi",
           "Sa"
       ],
       monthNames: [
           "Enero",
           "Febrero",
           "Marzo",
           "Abril",
           "Mayo",
           "Junio",
           "Julio",
           "Agosto",
           "Septiembre",
           "Octubre",
           "Noviembre",
           "Diciembre"
       ],
   }
 });

  $('input[name="FiltroFechaReportePagosCancelados"]').on('apply.daterangepicker', function(ev, picker) {
    $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
  });

});


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
  fetch("/ReportePagosCancelados/FilterBy?" + params, {
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
    formatDataTable();
    WaitMe_Hide('#TbPading');
  }).catch(function(ex){
    console.log("no success!");
  });
}

function formatDataTable() {
  $('#TableReportePagosCancelados').DataTable({
    "language": {
      "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
    "scrollX": true,
    "responsive": false,
    "paging": true,
    "dom": 'Bfrtip',
    "buttons": [
      {
        extend: 'excel',
        text: '<i class="fas fa-file-excel fa-lg"></i>',

      }
    ],
  /*  fixedColumns:   {
    leftColumns: 1
  },*/
    columnDefs: [
      {
          "targets": [0],
          "width": "10%",
          "className": "dt-head-center dt-body-center"
      },
      {
        "targets": 1,
        //"width": "15%",
        "className": "dt-head-center dt-body-center"
      },

      {
        "targets": [2,3,4],
        "width": "15%",
        "className": "dt-head-center dt-body-center"
      },
      {
        "targets": 5,
        "width": "10%",
        "className": "dt-head-center dt-body-right"
      },

      {
        "targets": 6,
        "width": "12px",
        "className": "dt-head-center dt-body-center"
      },
      {
        "targets": [7],
      "width": "25%",
        "className": "dt-head-center dt-body-left"
      },
      {
        "targets": 8,
        "width": "2%",
        "className": "dt-head-center dt-body-center",
        "mRender": function (data, type, full) {
          xml = $('input[name="IDPago"]').data("xmlarchivo");
          return  (xml != "" ? '<a href="'+xml+'" target="_blank" class="btnEliminarPago btn btn-primary btn-elevate btn-pill btn-sm"><i class="fas fa-file-excel fa-lg"></i></a>':'');
        }

      },
      {
        "targets": 9,
        "width": "2%",
        "className": "dt-head-center dt-body-center",
        "mRender": function (data, type, full) {
          pdf = $('input[name="IDPago"]').data("pdfarchivo");
          return  (pdf != "" ? '<a href="'+pdf+'" target="_blank" class="btnEliminarPago btn btn-primary btn-elevate btn-pill btn-sm"><i class="fas fa-file-pdf fa-lg"></i></a>':'');
        }

      }
    ]
  });
}

var fnGetDetallePago = function () {
  var IDPago = $(this).parents('tr').data('idpago');
  WaitMe_Show('#divTableDetallesPago');

  fetch("/ReportePagos/GetDetallesPago?IDPago=" + IDPago, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    return response.clone().json();
  }).then(function(data){
    WaitMe_Hide('#divTableDetallesPago');
    $('#divTableDetallesPago').html(data.htmlRes);
  }).catch(function(ex){
    console.log("no success!");
  });
}
