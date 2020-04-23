$(document).ready(function(){

  formatDataTableCanceladas();

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
  $('input[name="FiltroFechaReporteCanceladas"]').daterangepicker({
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

  $('input[name="FiltroFechaReporteCanceladas"]').on('apply.daterangepicker', function(ev, picker) {
    $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
  });

  $('#btnAplicarFiltro').on('click', getReportesByFilters);

});

function getReportesByFilters() {
  arrProveedores = $('#cboProveedor').val();
  strMoneda = [];
  $('#rdMXN').is(':checked') ? strMoneda.push('MXN') : null;
  $('#rdUSD').is(':checked') ? strMoneda.push('USD') : null;
  //WaitMe_Show('#TbPading');
  if($('#chkMonthYear').is(':checked')){
    arrMonth = $('#filtroxMes').val();
    Year = $('#filtroxAno').val();
    getReportes("arrMonth="+ JSON.stringify(arrMonth) +"&Year="+ Year +"&Proveedor="+ JSON.stringify(arrProveedores) +"&Moneda="+ JSON.stringify(strMoneda));
  }
  else {
    startDate = ($('#cboFechaDescarga').data('daterangepicker').startDate._d).toLocaleDateString('en-US');
    endDate = ($('#cboFechaDescarga').data('daterangepicker').endDate._d).toLocaleDateString('en-US');
    getReportes("FechaFacturaDesde="+ startDate +"&FechaFacturaHasta="+ endDate +"&Proveedor="+ JSON.stringify(arrProveedores) +"&Moneda="+ JSON.stringify(strMoneda));
  }
}

function getReportes(params) {
  WaitMe_Show('#TbPading');
  fetch("/ReporteCanceladas/FilterBy?" + params, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    return response.clone().json();
  }).then(function(data){
    WaitMe_Hide('#TbPading');
    $('#TbPading').html(data.htmlRes);
    formatDataTableCanceladas();
  }).catch(function(ex){
    console.log("no success!");
  });
}

function formatDataTableCanceladas() {
  $("#TableReporteCanceladas").DataTable({
    "scrollX": true,
    "scrollY": "395px",
    "language": {
      "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
    "lengthMenu": [50],
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
      "width": "10px",
      "className": "dt-head-center dt-body-center"
    },
    {
      "targets": 1,
      //"width": "15px",
      "className": "dt-head-center dt-body-center"
    },

    {
      "targets": [2,3],
      "width": "15px",
      "className": "dt-head-center dt-body-center"
    },

    {
      "targets": 4,
      "width": "12px",
      "className": "dt-head-center dt-body-center"
    },
    {
      "targets": [5,6,7,8],
      "width": "12px",
      "className": "dt-head-center dt-body-right"
    },
    {
      "targets": [9/*,10*/],
      "className": "dt-head-center dt-body-left"
    },
    ]
  });

}
