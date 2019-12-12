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
    formatDataTable()
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
}