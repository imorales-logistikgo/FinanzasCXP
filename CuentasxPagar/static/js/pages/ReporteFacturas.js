$(document).ready(function(){
  formatTableReporteFacturas();

//rago fecha para el Filtro
$('input[name="filtroFechaReporteFacturas"]').daterangepicker({
 autoUpdateInput: false
});

$('input[name="filtroFechaReporteFacturas"]').on('apply.daterangepicker', function(ev, picker) {
  $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
});

$('#btnAplicarFiltro').on('click', getReportesByFilters);


function getReportesByFilters() {
  startDate = ($('#cboFechaDescarga').data('daterangepicker').startDate._d).toLocaleDateString('en-US');
  endDate = ($('#cboFechaDescarga').data('daterangepicker').endDate._d).toLocaleDateString('en-US');
  arrProveedor = $('#cboProveedor').val();
  strMoneda = [];
  $('#rdMXN').is(':checked') ? strMoneda.push('MXN') : null;
  $('#rdUSD').is(':checked') ? strMoneda.push('USD') : null;
  //WaitMe_Show('#TbPading');
  fetch("/ReporteFacturas/FilterBy?FechaCobroDesde="+ startDate +"&FechaCobroHasta="+ endDate +"&Proveedor="+ JSON.stringify(arrProveedor) +"&Moneda="+ JSON.stringify(strMoneda), {
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
    //WaitMe_Hide('#TbPading');
    formatTableCobros();
  }).catch(function(ex){
    console.log("no success!");
  });
}

function formatTableReporteFacturas() {
  $("#TableReporteFacturas").DataTable({
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
      "width": "10px",
      "className": "dt-head-center dt-body-center"
    },

    {
      "targets": [1,2],
      "width": "15px",
      "className": "dt-head-center dt-body-center"
    },

    {
      "targets": [3,4],
      "width": "12px",
      "className": "dt-head-center dt-body-right"
    },
    ]
  });
}
});
