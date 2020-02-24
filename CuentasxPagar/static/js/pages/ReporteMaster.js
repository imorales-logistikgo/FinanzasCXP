$(document).ready(function() {

  formatTableReporteFacturas();

$('#btnAplicarFiltro').on('click', getReportesByFilters);

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



  //Filtro Rango fecha
  $('input[name="FiltroFecha"]').daterangepicker({
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

  $('input[name="FiltroFecha"]').on('apply.daterangepicker', function(ev, picker) {
    $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
  });


})


function getReportesByFilters() {
  arrProveedor = $('#cboProveedor').val();
  arrStatus = $('#cboStatus').val();
  arrProyectos = $('#cboProyecto').val();
  strMoneda = [];
  $('#rdMXN').is(':checked') ? strMoneda.push('MXN') : null;
  $('#rdUSD').is(':checked') ? strMoneda.push('USD') : null;
  WaitMe_Show('#TbPading');
  if($('#chkMonthYear').is(':checked')){
    arrMonth = $('#filtroxMes').val();
    Year = $('#filtroxAno').val();
    getReportes("arrMonth="+ JSON.stringify(arrMonth) +"&Year="+ Year +"&Proveedor="+ JSON.stringify(arrProveedor) +"&Status="+ JSON.stringify(arrStatus) +"&Moneda="+ JSON.stringify(strMoneda)+ "&Proyecto="+ JSON.stringify(arrProyectos));
  }
  else{
    startDate = ($('#cboFechaDescarga').data('daterangepicker').startDate._d).toLocaleDateString('en-US');
    endDate = ($('#cboFechaDescarga').data('daterangepicker').endDate._d).toLocaleDateString('en-US');
    getReportes("FechaFacturaDesde="+ startDate +"&FechaFacturaHasta="+ endDate +"&Proveedor="+ JSON.stringify(arrProveedor) +"&Status="+ JSON.stringify(arrStatus) +"&Moneda="+ JSON.stringify(strMoneda) + "&Proyecto="+ JSON.stringify(arrProyectos));
  }
}

function getReportes(params) {
  fetch("/ReporteMaster/FilterBy?" + params, {
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
    formatTableReporteFacturas();
    WaitMe_Hide('#TbPading');
  }).catch(function(ex){
    console.log("no success!");
  });
}

function formatTableReporteFacturas()
{
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
   /*exportOptions: {
    columns: ':visible'
  }*/
 }
],
columnDefs: [
{
    "targets": [0,1],
    "className": "dt-head-center dt-body-center",
},
{
    "targets": 2,
    "className": "dt-head-center dt-body-center",
},
{
    "targets": [3,4,5],
    "className": "dt-head-center dt-body-center",
},
{
    "targets": 6,
    "className": "dt-head-center dt-body-center",
    "mRender": function (data, type, full) {
      return (full[6] == 'True' ? "Si":"No");
    }
},
{
    "targets": 7,
    "className": "dt-head-center dt-body-center",
    "mRender": function (data, type, full) {
      return (full[7] == 'True' ? "Si":"No");
    }
},
{
    "targets": 10,
    "className": "dt-head-center dt-body-center",
    "mRender": function (data, type, full) {
      return (full[10] == 'True' ? "Si":"No");
    }
},
{
    "targets": [12,13,14,15],
    "className": "dt-head-center dt-body-right",
},
{
    "targets": 16,
    "className": "dt-head-center dt-body-center",
    "mRender": function (data, type, full) {
      return (full[14] == 'True' ? "Si":"No");
    }
},
{
    "targets": [18,19,20,21,22],
    "className": "dt-head-center dt-body-right",
},
]

  });
}
