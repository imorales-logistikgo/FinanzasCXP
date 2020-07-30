$(document).ready(function(){
  formatTableReporteFacturas();

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

  $(document).on('click','#DescargarReporteTotales', function(){
    var arrStatusReporte = []
    $('input[name="StatusReprote"]:checked').each(function() {
      arrStatusReporte.push($(this).val())
    });
    arrStatusReporte.push($('input[name="MonedaReprote"]').val())
    arrStatusReporte.length == 1 || arrStatusReporte.length >=4 ? alertToastError('Selecciona al menos una opcion') : DownloadReporteByTotales(arrStatusReporte)
  })



//rago fecha para el Filtro
$('input[name="filtroFechaReporteFacturas"]').daterangepicker({
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

$('input[name="filtroFechaReporteFacturas"]').on('apply.daterangepicker', function(ev, picker) {
  $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
});

$('#btnAplicarFiltro').on('click', getReportesByFilters);


function getReportesByFilters() {
  arrProveedor = $('#cboProveedor').val();
  arrStatus = $('#cboStatus').val();
  strMoneda = [];
  $('#rdMXN').is(':checked') ? strMoneda.push('MXN') : null;
  $('#rdUSD').is(':checked') ? strMoneda.push('USD') : null;
  WaitMe_Show('#TbPading');
  if($('#chkMonthYear').is(':checked')){
    arrMonth = $('#filtroxMes').val();
    Year = $('#filtroxAno').val();
    getReportes("arrMonth="+ JSON.stringify(arrMonth) +"&Year="+ Year +"&Proveedor="+ JSON.stringify(arrProveedor) +"&Status="+ JSON.stringify(arrStatus) +"&Moneda="+ JSON.stringify(strMoneda));
  }
  else{
    startDate = ($('#cboFechaDescarga').data('daterangepicker').startDate._d).toLocaleDateString('en-US');
    endDate = ($('#cboFechaDescarga').data('daterangepicker').endDate._d).toLocaleDateString('en-US');
    getReportes("FechaFacturaDesde="+ startDate +"&FechaFacturaHasta="+ endDate +"&Proveedor="+ JSON.stringify(arrProveedor) +"&Status="+ JSON.stringify(arrStatus) +"&Moneda="+ JSON.stringify(strMoneda));
  }
}

function getReportes(params) {
  fetch("/ReporteFacturas/FilterBy?" + params, {
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
    console.log(ex);
  });
}

function formatTableReporteFacturas() {
if (UserRol != 'Proveedor')
{
  $("#TableReporteFacturas").DataTable({
    "scrollX": true,
    "scrollY": "395px",
    "language": {
      "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
    "lengthMenu": [200],
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
      "targets": 2,
      "width": "15px",
      "className": "dt-head-center dt-body-center"
    },

    {
      "targets": [3,4,5,6],
      "width": "12px",
      "className": "dt-head-center dt-body-right"
    },
    {
      "targets": [7],
      "width": "12px",
      "className": "dt-head-center dt-body-center",
      "mRender": function (data, type, full) {
        return (full[7] == 'CANCELADA' ? 'RECHAZADA': full[7]);
      }
    },
    ]
  });
}
else
{
  $("#TableReporteFacturas").DataTable({
    "scrollX": true,
    "scrollY": "450px",
    "language": {
      "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
    "lengthMenu": [200],
    "responsive": false,
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
      "targets": 3,
      "width": "15px",
      "className": "dt-head-center dt-body-center",
      "mRender": function (data, type, full) {
        return (full[3] == 'CANCELADA' ? 'RECHAZADA': full[3]);
      }
    },
    {
      "targets": 4,
      "width": "15px",
      "className": "dt-head-center dt-body-center"
    },
    {
      "targets": 5,
      "width": "12px",
      "className": "dt-head-center dt-body-left"
    },
    ]
  });
}

}
});


var DownloadReporteByTotales = (params) => window.open(`/ReporteFacturas/GetReporteTotales/${params}/`)
