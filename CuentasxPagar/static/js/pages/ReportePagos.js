var idPag;
var btn;
$(document).ready(function(){
  var idPago;
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

  //rago fecha para el Filtro
  $('input[name="filtroFechaReportePagos"]').daterangepicker({
   autoUpdateInput: false
 });

  $('input[name="filtroFechaReportePagos"]').on('apply.daterangepicker', function(ev, picker) {
    $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
  });

  $('#ModalComplementos').on('hidden.bs.modal', function(){
   $('.uploaded-files-ComplemetoPagos ol').remove();
   $('.uploaded-files-ComplemetoPagos ol').remove();
 });

 $('#ModalComplementos').on('shown.bs.modal', function(){
   $('#ComplementosPagos').data("rutaarchivoPDF", null);
   $('#ComplementosPagos').data("rutaarchivoXML", null);
 });


  $(document).on('click', '#btnComplementos', function() {
    btn = $(this);
    var totalPago = $(this).data('totalpago').replace(/(\$)|(,)/g,'');
    idPag =  $(this).data('idpagocomplementos');
    subirComplementoPagoProveedor(totalPago);
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
    WaitMe_Show('#TbPading');
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

function SaveComplementosPago(pdf, xml)
{
  jParams = {
    IDPago: idPag,
    RutaPDF: pdf,
    RutaXML: xml,
  }
  fetch("/ReportePagos/SaveComplementosPago", {
    method: "POST",
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
      Swal.fire({
        type: 'success',
        title: 'Los complementos del pago fueron guardados correctamente',
        showConfirmButton: false,
        timer: 2500
      })
      var table = $('#TableReportePagos').DataTable();
      table.row($(btn).parents('tr')).remove().draw();
      $('#ModalComplementos').modal('hide');
      WaitMe_Hide('#waitModalPago');
    }
    else if(response.status == 500)
    {
      Swal.fire({
        type: 'error',
        title: 'Ocurrio un error, por favor intenta de nuevo',
        showConfirmButton: false,
        timer: 2500
      })
      $('#ModalComplementos').modal('hide');
      WaitMe_Hide('#waitModalPago');
    }
  }).catch(function(ex){
    console.log(ex);
  });
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
    "scrollX": true,
    "language": {
      "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
    //"responsive": true,
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
        idPago = $('input[name="IDPago"]').data("pagoid");
        return (full[6] != "" ? '':`<button type ="button" id="btnComplementos" class="btn btn-success btn-elevate btn-pill btn-sm" data-totalpago="${full[3]}" data-vercomplementoxml="${full[6]}" data-vercomplementopdf="${full[7]}" data-idpagocomplementos="`+idPago+`" data-toggle="modal" data-target="#ModalComplementos" data-backdrop="static" data-keyboard="false"><i class="fas fa-upload"></i></button>`);
      }
    },
    {
      "targets": 10,
      "width": "2%",
      "className": "dt-head-center dt-body-center",
      "mRender": function (data, type, full) {
        idPago = $('input[name="IDPago"]').data("pagoid");
        if(UserRol != "Proveedor")
          return  '<button type ="button" class="btnEliminarPago btn btn-danger btn-elevate btn-pill btn-sm" data-idpago="'+idPago+'"><i class="flaticon-delete"></i></button>';
        else
          return '';
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
      WaitMe_Hide('#TbPading');
    }
    else if(response.status == 500)
    {
      res = false;
      WaitMe_Hide('#TbPading');
    }
  }).catch(function(ex){
    res = false;
    WaitMe_Hide('#TbPading');
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

function subirComplementoPagoProveedor(totalPago)
{
  // plugin para subir los archivos del proveedor
  "use strict";

      // Class definition
      var KTUppy = function () {
        const Tus = Uppy.Tus;
        const ProgressBar = Uppy.ProgressBar;
        const StatusBar = Uppy.StatusBar;
        const FileInput = Uppy.FileInput;
        const Informer = Uppy.Informer;
        const XHRUpload = Uppy.XHRUpload;


        // to get uppy companions working, please refer to the official documentation here: https://uppy.io/docs/companion/
        const Dashboard = Uppy.Dashboard;
        const GoogleDrive = Uppy.GoogleDrive;
        const Webcam = Uppy.Webcam;

        // Private functions
        var initUppy1 = function(){
          var id = '#ComplementosPagos';

          var options = {
            proudlyDisplayPoweredByUppy: false,
            target: id,
            inline: true,
            height: 260,
            replaceTargetContent: true,
            showProgressDetails: true,
            note: 'Logisti-k',
             browserBackButtonClose: true,

           }

           var uppyDashboard = Uppy.Core({
             autoProceed: false,
             restrictions: {
              maxFileSize: 5000000, // 5mb
              maxNumberOfFiles: 2,
              minNumberOfFiles: 2,
             allowedFileTypes:['.pdf', '.xml']
           },
           locale: Uppy.locales.es_ES,
           onBeforeFileAdded: (currentFile, file) => {
             if(Object.values(file)[0] === undefined)
             {
               console.log("+1")
             }
             else
             {
               if((currentFile.type === Object.values(file)[0].meta.type))
               {
                 uppyDashboard.info(`Los archivos deben ser diferentes`, 'error', 500)
                 return false
               }
               else
               {
                 console.log("ok")
               }
             }

           }
         });


           uppyDashboard.use(Dashboard, options);
           uppyDashboard.use(XHRUpload, { endpoint: 'https://api-bgk-debug.logistikgo.com/api/Viaje/SaveevidenciaTest', method: 'post'});
          //uppyDashboard.use(XHRUpload, { endpoint: 'http://localhost:63510/api/Viaje/SaveevidenciaTest', method: 'post'});
          uppyDashboard.use(Webcam, {target: Dashboard});
          uppyDashboard.use(GoogleDrive, { target: Dashboard, companionUrl: 'https://companion.uppy.io' });
          uppyDashboard.on('upload-success', (file, response) => {
            const fileName = file.name
            if (file.extension === 'pdf')
            {
             const urlPDF = response.body
             $('#ComplementosPagos').data("rutaarchivoPDF", urlPDF)
             document.querySelector('.uploaded-files-ComplemetoPagos').innerHTML +=
             `<ol><li id="listaArchivos"><a href="${urlPDF}" target="_blank" name="url" id="RutaPDF">${fileName}</a></li></ol>`

                 }
                 else
                 {

                   const urlXMLCheck = response.body
                   var to = leerXMLTransportista(urlXMLCheck)
                   if(to != totalPago)
                   {
                     alertToastError("El total del pago no coincide con el total calculado del sistema")
                      //uppyDashboard.reset()
                      uppyDashboard.cancelAll()
                    }
                    else
                    {
                     const urlPDF = response.body
                     $('#ComplementosPagos').data("rutaarchivoXML", urlPDF)
                     document.querySelector('.uploaded-files-ComplemetoPagos').innerHTML +=
                     `<ol><li id="listaArchivos"><a href="${urlPDF}" target="_blank" name="url" id="RutaXML">${fileName}</a></li></ol>`
                    }
                  }
                  if($('#ComplementosPagos').data("rutaarchivoXML") != null && $('#ComplementosPagos').data("rutaarchivoPDF") != null || $('#ComplementosPagos').data("rutaarchivoXML") != undefined && $('#ComplementosPagos').data("rutaarchivoPDF") != undefined)
                  {
                    var pdf = $('#ComplementosPagos').data("rutaarchivoPDF");
                    var xml = $('#ComplementosPagos').data("rutaarchivoXML");
                    WaitMe_Show('#waitModalPago');
                    SaveComplementosPago(pdf, xml);
                  }


   });
    }
        return {
          // public functions
          init: function() {
            initUppy1();
          }
        };
      }();

      KTUtil.ready(function() {
        KTUppy.init();
      });

}
