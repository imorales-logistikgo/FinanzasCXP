var proveedor;
var moneda;
var Ev;
var EvDigital;
var EvFisica;
var idprov, folioCheck;
var table;
var subtotal = 0, Tiva=0, TRetencion=0, total=0;
var totalViaje = 0;
var idPend, uuid;
var totalXML=0, totalXMLProveedor=0, valCFDIAndOther, FViaje;

$(document).ready(function() {
  $(document).keydown(function(e){
      if(e.which === 123){
         return false;
      }
  });
  $(document).bind("contextmenu",function(e) {
   e.preventDefault();
  });

//Tabla Pendientes de enviar
formatDataTable();
$('#TablePendientesEnviar').css("display", "block");

//on click select row checkbox
$(document).on( 'change', 'input[name="checkPE"]', function () {
  var input = 'input[name="checkPE"]';
  var btnSubir = '#btnSubirFacturaPendientesEnviar';
  if($(this).is(':checked'))
  {
    folioCheck = table.row($(this).parents('tr')).data()[1];
    FiltroCheckboxProveedor();
    adddatos();
    ContadorCheck(input, btnSubir);
  }
  else
  {
    adddatos();
    ContadorCheck(input, btnSubir);
  }
});

//Depurado
$(document).on('change', 'input[name="Depurado"]',function(){
  if ($(this).is(':checked')){
    $('#txtFolioFactura').prop('disabled', false)
  }
  else{
    $('#txtFolioFactura').prop('disabled', true)
  }
})

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

//on click para el boton del modal subir factura
$(document).on('click', '#btnSubirFacturaPendientesEnviar', function(){
  getDatos();
  mostrarTipoCambio();
});

//FOLIO VERIFICACION USER AMERICANO
$(document).on('change', '#txtFolioFacturaP, #txtFolioFactura', function() {
  var TipoUsr = $(this).attr('id') == 'txtFolioFactura' ? "Lgk": "Proveedor"
  fnCheckFolio($(this).val().replace(/ /g, "").trim().toUpperCase(), "", TipoUsr);
});

//APLICAR FILTROS
$('#btnAplicarFiltro').on('click', fnGetPendientesEnviar);

//VALIDACION PARA GUARDAR FACTURAS
$('#btnGuardarFactura').on('click', function(){
  if($('#Depurado').is(':checked') ? true : $('#kt_uppy_1').data("rutaarchivoPDF") != undefined && $('#kt_uppy_1').data("rutaarchivoXML") != undefined || $('#kt_uppy_1').data("rutaarchivoPDF") != null && $('#kt_uppy_1').data("rutaarchivoXML") != null)
  {
    if($('#txtFolioFactura').val() != "" && $('#FechaRevision').val() != "" && $('#FechaFactura').val() != "" && $('#FechaVencimiento').val() != "")
    {
      WaitMe_Show('#WaitModalPE');
      saveFactura();
    }
    else
    {
      alertToastError("El folio y las fechas no pueden estar vacias");
    }

  }
  else
  {
    alertToastError("Son necesarios los complementos PDF y XML");

  }
});


//btn guardar archivos proveedor
$('#btnGuardarFacturaP').on('click', function(){
    if(IDUsuraio_ == 3126 || IDUsuraio_ == 3254 ? $('#archivosProveedor').data("rutaarchivoPDF") != undefined  || $('#archivosProveedor').data("rutaarchivoPDF") != null : $('#archivosProveedor').data("rutaarchivoPDF") != undefined && $('#archivosProveedor').data("rutaarchivoXML") != undefined || $('#archivosProveedor').data("rutaarchivoPDF") != null && $('#archivosProveedor').data("rutaarchivoXML") != null)
  {
    if($('#txtFolioFacturaP').val() != "" && $('#FechaRevisionP').val() != "" && $('#FechaFacturaP').val() != "" && $('#FechaVencimientoP').val() != "" && $('input[name="TipoCambio"]').val() != "")
    {
      WaitMe_Show('#WaitModalPEProveedor');
      saveFacturaP();
    }
    else
    {
      alertToastError("El folio y las fechas no pueden estar vacias");
    }
  }
  else
  {
    alertToastError("Son necesarios los complementos PDF y XML");
  }
});

//buscador para el proveedor
$('#buscarFolioProveedor').on('click', function(){
  if($('#inputBuscarFolioProveedor').val() != "")
  {
    $('#inputBuscarFolioProveedor').prop("disabled", true);
    $('#buscarFolioProveedor').prop("disabled", true);
    BuscarFolioProveedor();
  }
  else
  {
    alertToastError("Por favor ingrese un folio");
  }
});

$(document).on('click', '#btnCerrarDivproveedor', function(){
  limpiarDivProveedor();
});

//ocultar columnas tabla Pendientes enviar
$('input[name="Fecha Descarga"]').on('change', function(e){
 e.preventDefault();
 var column = table.column(3);
 column.visible( ! column.visible() );
});
$('input[name="Subtotal"]').on('change', function(e){
  e.preventDefault();
  var column = table.column(4);
  column.visible( ! column.visible() );
});

$('input[name="IVA"]').on('change', function(e){
 e.preventDefault();
 var column = table.column(5);
 column.visible( ! column.visible() );
});
$('input[name="Retencion"]').on('change', function(e){
 e.preventDefault();
 var column = table.column(6);
 column.visible( ! column.visible() );
});
$('input[name="Total"]').on('change', function(e){
 e.preventDefault();
 var column = table.column(7);
 column.visible( ! column.visible() );
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

// Filtro select cliente
$("#kt_select2_3").select2({
  placeholder: "Proveedor"
});

//Fechas modal
$('#kt_modal_2').on('shown.bs.modal', function(){
  $('#FechaFactura').datepicker({
    format: 'yyyy/mm/dd',
    todayHighlight: true,
    endDate: '+0d',
    language: 'es'
  });
  $("#FechaFactura").datepicker('setDate', GetCurrentDate());
  $('#FechaRevision').datepicker({
    format: 'yyyy/mm/dd',
    todayHighlight: true,
    language: 'es'
  });
  $("#FechaRevision").datepicker('setDate', GetCurrentDate());

  $('#FechaVencimiento').datepicker({
   format: 'yyyy/mm/dd',
   todayHighlight: true,
   language: 'es',
   changeMonth: true,
   changeYear: true,
 });
});

$('#FechaRevision').on('change', function(){
  if($("#FechaRevision").val() < $("#FechaFactura").val())
  {
    alertToastError("La fecha de revision no puede ser antes que la fecha de factura");
    $("#FechaRevision").datepicker('setDate', $("#FechaFactura").val() )
  }
  $('#FechaVencimiento').datepicker({
    format: 'yyyy/mm/dd',
    language: 'es'
  });
  $("#FechaVencimiento").datepicker('setDate', fechaVencimineto("#FechaRevision"));
});

$('#FechaRevisionP').on('change', function(){
  $('#FechaVencimientoP').datepicker({
    format: 'yyyy/mm/dd',
  });
  $("#FechaVencimientoP").datepicker('setDate', fechaVencimineto("#FechaRevisionP"));
});


//limpiar modal
$('#kt_modal_2').on('hidden.bs.modal', function(){
  LimpiarModalSF();
  KTUppy.init()
});

$('input[name="TipoCambio"]').on('keyup change', function(){
  if($('input[name="TipoCambio"]').val() >=1)
  {
    getDatos();
  }
  else
  {
    alertToastError("El tipo de cambio debe ser mayor a 0");
    $('input[name="TipoCambio"]').val('');
  }
});




//FUNCIONES PARA PendienteS DE ENVIAR

//funcion para mostrar u ocultar el input del timpo de cambio
function mostrarTipoCambio()
{
  var found;
  var datos = adddatos();
  for(var i=0; i<datos.length; i++)
  {
    // datos[i][3].push(datos[i][3]);
    found = datos[i][5].includes('USD');
  }
  if(found != true)
  {
   $('#inputTipoCambio').hide();
   $('#labelTipoCambio').hide();
 }
 else
 {
   $('#inputTipoCambio').show();
   $('#labelTipoCambio').show();
 }
}



//validacion mismo cliente en los checkbox
function FiltroCheckboxProveedor(){
  var checked = $("input[name='checkPE']:checked");
  idprov = $($(checked[0]).parents('tr')[0]).data("idproveedor");
  $("input[name=checkPE]:checked").each(function () {
   var check = table.row($(this).parents('tr')).data();
   if(checked.length > 1)
   {
     if (check[2] != proveedor || check[8] != moneda) {
      $(this).prop('checked', false);
      alertToastError("El proveedor y la moneda deben ser iguales");
    }
    else
    {
      console.log("ok");
    }
  }
  else
  {
    proveedor = check[2];
    moneda = check[8];
  }
});
}

//funcion limpiar modal subir facturas de Pendientes de enviar
function LimpiarModalSF()
{
  $('input[name="FolioFactura"]').val("");
  $('input[name="Comentarios"]').val("");
  $('input[name="TipoCambio"]').val(1);
  TestFile = null;
  $('.uploaded-files ol').remove();
  $('#see').hide();
  $('#seeAlert').hide();
  //ids = [];
  $('#kt_uppy_1').data("rutaarchivoXML", null);
  $('#kt_uppy_1').data("rutaarchivoPDF", null);
  uuid = '';
  folioCheck = "";
  $('#Depurado').prop('checked', false);
  $('#btnGuardarFactura').prop('disabled',true)
  valCFDIAndOthe = ""
}



// plugin para subir los archivos de las facturas en Modal Pendientes de enviar
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

			// Private functions
			var initUppy1 = function(){
				var id = '#kt_uppy_1';

				var options = {
					proudlyDisplayPoweredByUppy: false,
					target: id,
					inline: true,
					height: 260,
					replaceTargetContent: true,
					showProgressDetails: true,
					note: 'Logisti-k',

					/*metaFields: [
						{ id: 'name', name: 'Name', placeholder: 'file name' },
						{ id: 'caption', name: 'Caption', placeholder: 'describe what the image is about' }
           ],*/
           browserBackButtonClose: true,

         }
         var uppyDashboard = Dasboard();
//         getProveedorAmericano(idprov);
        /* var uppyDashboard = Uppy.Core({
           autoProceed: false,
           restrictions: {
						maxFileSize: 4200000, // 5mb
						maxNumberOfFiles: 2,
						minNumberOfFiles: 2,
           allowedFileTypes:['.pdf', '.xml']
         },
         locale: Uppy.locales.es_ES,
         onBeforeFileAdded: (currentFile, file) => {
           //if($('.uppy-DashboardContent-title').length == 0)
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
       });*/


        uppyDashboard.use(Dashboard, options);
        uppyDashboard.use(XHRUpload, { endpoint: 'https://api-bgk-debug.logistikgo.com/api/Viaje/SaveevidenciaTest', method: 'post'});
		uppyDashboard.use(GoogleDrive, { target: Dashboard, companionUrl: 'https://companion.uppy.io' });
        uppyDashboard.on('upload-success', (file, response) => {
          const fileName = file.name
          if (file.extension === 'pdf')
          {
           const urlPDF = response.body
           $('#kt_uppy_1').data("rutaarchivoPDF", urlPDF)
           document.querySelector('.uploaded-files').innerHTML +=
           `<ol><li id="listaArchivos"><a href="${urlPDF}" target="_blank" name="url" id="RutaPDF">${fileName}</a></li></ol>`
                 //  console.log($('#kt_uppy_1').data("rutaarchivoPDF"))
               }
               else
               {
                 const urlXMLCheck = response.body
                 totalXML = leerxml(urlXMLCheck)
//                 var folioInFactura = FolioViajeXML(urlXMLCheck, folioCheck)
                 GetFolioViajeXML(urlXMLCheck, folioCheck)
                 GetValidacionCFDIAndOther(urlXMLCheck)
                 if(+totalXML > (Number(total.toFixed(2)) + 1) || totalXML == null || !FViaje || !valCFDIAndOther)
                 {
                   $("#btnGuardarFactura").prop("disabled", true)
                   alertToastError(`El total de la factura no coincide con el total calculado del sistema $${total.toFixed(2)}`)
                   uppyDashboard.cancelAll()
                  }
                  else
                  {
                   uuid = GetUUID(urlXMLCheck);
                   const urlPDF = response.body
                   $('#kt_uppy_1').data("rutaarchivoXML", urlPDF)
                   document.querySelector('.uploaded-files').innerHTML +=
                   `<ol><li id="listaArchivos"><a href="${urlPDF}" target="_blank" name="url" id="RutaXML">${fileName}</a></li></ol>`
                   getSerieProveedor(idprov).then((response) =>  fnCheckFolio(response.Serie + getFolioXML(urlXMLCheck), uppyDashboard, "Lgk")).catch((e) => (uppyDashboard.cancelAll(), $('.uploaded-files ol').remove(), alertToastError("Algo salio mal :(")));
                 }
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

  });


//funcion para obtener los datos de cada checkbox seleccionado en la tabla Pendientes de enviar
function adddatos(){
  var arrSelect=[];
  $("input[name=checkPE]:checked").each(function () {
    var table = $('#TablePendientesEnviar').DataTable();
    var datosRow = table.row($(this).parents('tr')).data();
    arrSelect.push([datosRow[1], datosRow[4], datosRow[5], datosRow[6], datosRow[7], datosRow[8]]);
  });
  return arrSelect;
}


//funcion para obtener los datos de la tabla PENDIENTE de enviar para mostrarlos en la tabla del modal subir facturas
function getDatos(){
 var datos = adddatos();
 var newData = [];
 subtotal = 0, Tiva=0, TRetencion=0, total=0, moneda, totalCambio=0;
 for (var i=0; i<datos.length; i++)
 {
  moneda = datos[i][5];
  if(datos[i][5] === "MXN")
  {
    var sub = parseFloat(datos[i][1].replace(/(\$)|(,)/g,''));
    var iva = parseFloat(datos[i][2].replace(/(\$)|(,)/g,''));
    var retencion = parseFloat(datos[i][3].replace(/(\$)|(,)/g,''));
    var tot = parseFloat(datos[i][4].replace(/(\$)|(,)/g,''));
    subtotal = subtotal + sub;
    Tiva = Tiva + iva;
    TRetencion = TRetencion + retencion;
    total = total + tot;
    datos[i].push("null");

  }
  if(datos[i][5] === "USD")
  {
    var tipoCambio = $('input[name="TipoCambio"]').val();

    var folio = datos[i][0];
    var sub = parseFloat(datos[i][1].replace(/(\$)|(,)/g,''));
    var iva = parseFloat(datos[i][2].replace(/(\$)|(,)/g,''));
    var retencion = parseFloat(datos[i][3].replace(/(\$)|(,)/g,''));
    var tot = parseFloat(datos[i][4].replace(/(\$)|(,)/g,''));
    var totCambio = (parseFloat(datos[i][4].replace(/(\$)|(,)/g,'')) * tipoCambio);
    datos[i].push(totCambio);
        //newData.push([folio, sub, iva, retencion, tot]);
        subtotal = subtotal + sub;
        Tiva = Tiva + iva;
        TRetencion = TRetencion + retencion;
        total = total + tot;
        totalCambio = totalCambio + totCambio;

      }
    }

    var h = [datos];
    var table = $('#ResumTable').DataTable({
      "language": {
        "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
      },
      destroy: true,
      data: h[0],
      columnDefs: [
      {
       "targets": 0,
       "className": "dt-head-center dt-body-center bold"
     },
     {
       "targets": [1,2,3,4],
       "className": "dt-head-center dt-body-right"
     },
     {
       "targets": 5,
       "className": "dt-head-center dt-body-center"
     },
     {
       "targets": 6,
       "width": "10%",
       "className": "dt-head-center dt-body-center"
     }
     ]

   });

    $('#sub').html('<strong>$'+subtotal.toFixed(2)+'</strong>');
    $('#iva').html('<strong>$'+Tiva.toFixed(2)+'</strong>');
    $('#retencion').html('<strong>$'+TRetencion.toFixed(2)+'</strong>');
    $('#total').html('<strong>$'+total.toFixed(2)+'</strong>');
    $('#Moneda').html('');
    $('#totalCambio').html('<strong>$'+truncarDecimales(totalCambio, 2)+'<strong>');
    $('#verTotalPE').html('<strong>$'+total.toFixed(2)+'</strong>');
  }

  function saveFacturaP() {
    jParams = {
      FolioFactura: $('#txtFolioFacturaP').val().replace(/ /g, "").trim().toUpperCase(),
      Proveedor: proveedor,
      FechaFactura: $('#FechaFacturaP').val(),
      FechaRevision: $('#FechaRevisionP').val(),
      FechaVencimiento: $('#FechaVencimientoP').val(),
      Moneda: moneda,
      SubTotal: truncarDecimalesPE(subtotal, 2),
      IVA: truncarDecimalesPE(Tiva, 2),
      Retencion: truncarDecimalesPE(TRetencion, 2),
      Total: truncarDecimalesPE(total, 2),
      RutaXML: $('#archivosProveedor').data("rutaarchivoXML") == undefined ? "":$('#archivosProveedor').data("rutaarchivoXML"),
      RutaPDF: $('#archivosProveedor').data("rutaarchivoPDF"),
      TipoCambio: 1,
      Comentarios: $('#txtComentariosP').val(),
      IDProveedor: idprov,
      TotalXML: +totalXMLProveedor,
      UUID: uuid,
      Estado: $('#Depurado').is(':checked') ? "YU":'NU'
    }

    fetch("/PendientesEnviar/SaveFactura", {
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
        $('#btnSubirFacturaPendientesEnviar').prop("disabled", true);
    //  console.log(ids);
    return response.clone().json();
  }
  else if(response.status == 500)
  {
    Swal.fire({
      type: 'error',
      title: 'El folio indicado ya existe en el sistema',
      showConfirmButton: false,
      timer: 2500
    })
    WaitMe_Hide('#WaitModalPEProveedor');
      //console.log("El folio indicado ya existe en el sistema");
    }

  }).then(function(IDFactura){
    SavePartidasxFacturaP(IDFactura);
  }).catch(function(ex){
    console.log("no success!");
  });
}

function SavePartidasxFacturaP(IDFactura) {
  var arrPendientes = [];
  arrPendientes.push(idPend);
  jParams = {
    IDFactura: IDFactura,
    arrPendientes: arrPendientes,
  }

  fetch("/PendientesEnviar/SavePartidasxFactura", {
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
      WaitMe_Hide('#WaitModalPEProveedor');
      $('#contenedorSubirArchivosproveedor').css("display", "none");
      $('#inputBuscarFolioProveedor').prop("disabled", false);
      $('#buscarFolioProveedor').prop("disabled", false);
      Swal.fire({
        type: 'success',
        title: 'Factura guardada correctamente',
        showConfirmButton: false,
        timer: 1500
      })
      uuid = '';
      limpiarDivProveedor();
    }
    else if(response.status == 500)
    {
      alertToastError("Error al guardar la partida");
      //console.log("Error al guardar la partida");
    }
  }).catch(function(ex){
    console.log("no success!");
  });
}


function saveFactura() {
  jParams = {
    FolioFactura: $('#txtFolioFactura').val().replace(/ /g, "").trim().toUpperCase(),
    Proveedor: proveedor,
    FechaFactura: $('#FechaFactura').val(),
    FechaRevision: $('#FechaRevision').val(),
    FechaVencimiento: $('#FechaVencimiento').val(),
    Moneda: moneda,
    SubTotal: subtotal,
    IVA: Tiva,
    Retencion: TRetencion,
    Total: total,
    RutaXML: $('#Depurado').is(':checked') ? "" : $('#kt_uppy_1').data("rutaarchivoXML"),
    RutaPDF: $('#Depurado').is(':checked') ? "" : $('#kt_uppy_1').data("rutaarchivoPDF"),
    TipoCambio: $('#txtTipoCambio').val(),
    Comentarios: $('#txtComentarios').val(),
    IDProveedor:idprov,
    TotalXML: $('#Depurado').is(':checked') ? null : +totalXML,
    UUID: $('#Depurado').is(':checked') ? null : uuid,
    Estado: $('#Depurado').is(':checked') ? "YU":'NU'
  }

  fetch("/PendientesEnviar/SaveFactura", {
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
      $('#btnSubirFacturaPendientesEnviar').prop("disabled", true);
    //  console.log(ids);
    return response.clone().json();
  }
  else if(response.status == 500)
  {
    Swal.fire({
      type: 'error',
      title: 'El folio indicado ya existe en el sistema',
      showConfirmButton: false,
      timer: 2500
    })
    WaitMe_Hide('#WaitModalPE');
      //console.log("El folio indicado ya existe en el sistema");
    }

  }).then(function(IDFactura){
    SavePartidasxFactura(IDFactura);
  }).catch(function(ex){
    console.log("no success!");
  });
}

function SavePartidasxFactura(IDFactura) {
  var arrPendientes = [];
  var currentIDPending = 0;
  $("#TablePendientesEnviar input[name=checkPE]:checked").each(function () {
    currentIDPending = $($(this).parents('tr')[0]).data('idpendienteenviar');
    if(!arrPendientes.includes(currentIDPending))
      arrPendientes.push(currentIDPending);
  });
  jParams = {
    IDFactura: IDFactura,
    arrPendientes: arrPendientes,
  }

  fetch("/PendientesEnviar/SavePartidasxFactura", {
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
      WaitMe_Hide('#WaitModalPE');
      $("#kt_modal_2").modal('hide');
      var table = $('#TablePendientesEnviar').DataTable();
      $("#TablePendientesEnviar input[name=checkPE]:checked").each(function () {
        table.row($(this).parents('tr')).remove().draw();
      });

      Swal.fire({
        type: 'success',
        title: 'Factura guardada correctamente',
        showConfirmButton: false,
        timer: 1500
      })
      uuid = '';
      folioCheck = "";
      $('#divTablaPendientesEnviar').html(data.htmlRes)
      formatDataTable();
    }
    else if(response.status == 500)
    {
      alertToastError("Error al guardar la partida");
      //console.log("Error al guardar la partida");
    }
  }).catch(function(ex){
    console.log("no success!");
  });
}

var fnGetPendientesEnviar = function () {
  arrStatus = $('#cboStatus').val();
  arrProveedores = $('#cboProveedor').val();
  strMoneda = $('#rdMXN').is(':checked') ? 'MXN' : 'USD';
  WaitMe_Show('#divTablaPendientesEnviar');
  if($('#chkMonthYear').is(':checked')){
    arrMonth = $('#filtroxMes').val();
    Year = $('#filtroxAno').val();
    getPendientesEnviar("arrMonth="+ JSON.stringify(arrMonth) +"&Year="+ Year +"&Status="+ JSON.stringify(arrStatus)
      +"&Proveedor="+ JSON.stringify(arrProveedores) +"&Moneda="+ strMoneda);
  }
  else
  {
    startDate = ($('#cboFechaDescarga').data('daterangepicker').startDate._d).toLocaleDateString('en-US');
    endDate = ($('#cboFechaDescarga').data('daterangepicker').endDate._d).toLocaleDateString('en-US');
    getPendientesEnviar("FechaDescargaDesde="+ startDate +"&FechaDescargaHasta="+ endDate +"&Status="+ JSON.stringify(arrStatus)
      +"&Proveedor="+ JSON.stringify(arrProveedores) +"&Moneda="+ strMoneda);
  }
}

function getPendientesEnviar(params){
  fetch("/PendientesEnviar/FilterBy?" + params, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    return response.clone().json();
  }).then(function(data){
    $('#divTablaPendientesEnviar').html(data.htmlRes);
    formatDataTable();
    $('#TablePendientesEnviar').css("display", "block");
  }).catch(function(ex){
    console.log("no success!");
  });
}

var fnCheckFolio = function (folio, cancel, user) {
  WaitMe_ShowBtn(user == 'Lgk' ? '#btnGuardarFactura': '#btnGuardarFacturaP');
  $('#btnGuardarFactura').prop('disabled', true);
  fetch("/PendientesEnviar/CheckFolioDuplicado?Folio=" + folio, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    return response.clone().json();
  }).then(function(data){
    if(data.IsDuplicated) {
      Swal.fire({
        type: 'error',
        title: 'El folio indicado ya existe en el sistema',
        showConfirmButton: false,
        timer: 2500
      })
      user == 'Lgk' ? ($('#btnGuardarFactura').attr('disabled',true),$('#txtFolioFactura').val('')) : user == 'Proveedor' ? ($('#btnGuardarFacturaP').attr('disabled',true),$('#txtFolioFacturaP').val('')):"";
      IDUsuraio_ == 3126 || IDUsuraio_ == 3254 ? "":cancel.cancelAll();
      IDUsuraio_ != 3126 && user == 'Lgk' || IDUsuraio_ != 3254 && user == 'Lgk' ? $('.uploaded-files ol').remove(): IDUsuraio_ != 3126 && user == 'Proveedor' || IDUsuraio_ != 3254 && user == 'Proveedor' ? $('.uploaded-files-proveedor ol').remove() : "";
      WaitMe_HideBtn(user == 'Lgk' ? '#btnGuardarFactura': '#btnGuardarFacturaP');
    }
    else {
      user == 'Lgk' ? ($('#btnGuardarFactura').attr('disabled',false),$('#txtFolioFactura').val(folio)) : user == 'Proveedor' ? ($('#btnGuardarFacturaP').attr('disabled',false),$('#txtFolioFacturaP').val(folio)):"";
      //$('#txtFolioFactura').val(folio);
      //$("#btnGuardarFactura").prop("disabled", false);
      WaitMe_HideBtn(user == 'Lgk' ? '#btnGuardarFactura': '#btnGuardarFacturaP');
    }
  }).catch(function(ex){
    console.log(ex);
  });
}

function BuscarFolioProveedor() {
  WaitMe_Show('#TbPading');
  fetch("/PendientesEnviar/FindFolioProveedor?Folio=" + $('#inputBuscarFolioProveedor').val(), {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    return response.clone().json();
  }).then(function(data){
    if(!data.Found) {
      Swal.fire({
        type: 'error',
        title: 'El folio indicado no existe en el sistema',
        showConfirmButton: false,
        timer: 2500
      })
      $('#contenedorSubirArchivosproveedor').css("display", "none");
      $('#inputBuscarFolioProveedor').prop("disabled", false);
      $('#buscarFolioProveedor').prop("disabled", false);
      WaitMe_Hide('#TbPading');
    }
    else {
      moneda = data.Moneda
      subtotal = data.Subtotal;
      Tiva = data.IVA;
      TRetencion = data.Retencion;
      total = data.Total;
      idPend = data.IDPendienteEnviar;
      totalViaje = +data.Total;
      proveedor = data.Proveedor;
      idprov = data.IDProveedor;
      folioCheck = data.Folio;
      $('#FolioConcepto').html(data.Folio);
      $('#ProveedorConcepto').html(data.Proveedor);
      $('#FechaConcepto').html(data.FechaDescarga);
      $('#contenedorSubirArchivosproveedor').css("display", "block");
      $('#FechaFacturaP').datepicker({
        format: 'yyyy/mm/dd',
        todayHighlight: true,
        endDate: '+0d',
        language:'es'
      });

      $("#FechaFacturaP").datepicker('setDate', GetCurrentDate());
      $('#FechaRevisionP').datepicker({
        format: 'yyyy/mm/dd',
        todayHighlight: true,
        language: 'es'
      });

      $("#FechaRevisionP").datepicker('setDate', GetCurrentDate());
      $('#FechaVencimientoP').prop('disabled', true);
      $('#FechaVencimientoP').datepicker({
       format: 'yyyy/mm/dd',
       todayHighlight: true,
       changeMonth: true,
       changeYear: true
     });

      archivosproveedor();
      WaitMe_Hide('#TbPading');
    }
  }).catch(function(ex){
    $('#contenedorSubirArchivosproveedor').css("display", "none");
    WaitMe_Hide('#TbPading');
  });
}


function formatDataTable() {
  table = $('#TablePendientesEnviar').DataTable( {
   "scrollX": true,
   //"scrollCollapse": true,
   'scrollY': '400px',
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
     exportOptions: {
       columns: [ 0,1,2,3,4,5,6,7,8,9]
     }
   }
   ],

   columnDefs: [ {
     orderable: false,
     targets:   0,
     "className": "dt-head-center dt-body-center",
     "width": "1%",
     "mRender": function (data, type, full) {
       EvDigital = $('input[name="isEvicencias"]').data("evidenciadigital");
       EvFisica = $('input[name="isEvicencias"]').data("evidenciafisica");
         //idPendienteenviar = $('input[name="isEvicencias"]').data("idPendienteenviar");
         return (EvDigital != 'False' && full[9] == 'finalizado'.toUpperCase() && EvFisica != 'False' ? '<input type="checkbox" name="checkPE" id="estiloCheckbox" />': '');
       }
     },
     {
      //"width": "5%",
      "className": "text-center bold",
      "targets": 1
    },
    {
      //"width": "20%",
      "className": "dt-head-center dt-body-center",
      "targets": [2,3]
    },
    {
      "className": "dt-head-center dt-body-right",
      'width' : '5%',
      "targets": [4,5,6,7]
    },
    {
      "width": "5%",
      "className": "dt-head-center dt-body-center",
      "targets": [8,9]

    },

    {
      "width": "5%",
      "className": "dt-head-center dt-body-center",
      "targets": 10,
      "mRender": function (data, type, full) {
        return (EvDigital != 'False' && EvFisica != 'False' ? 'Si':'No');
      }
    }]
  } );
}

function archivosproveedor()
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
        //const Webcam = Uppy.Webcam;
  			// Private functions
  			var initUppy1 = function(){
  				var id = '#archivosProveedor';
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
         var filesMin = IDUsuraio_ == 3126 || IDUsuraio_ == 3254 ? 1:2;
         IDUsuraio_ == 3126 || IDUsuraio_ == 3254 ? $('#txtFolioFacturaP').prop("disabled", false):$('#txtFolioFacturaP').prop("disabled", true);
         var uppyDashboard = Uppy.Core({
           autoProceed: false,
           restrictions: {
  						maxFileSize: 4200000, // 5mb
  						maxNumberOfFiles: 2,
  						minNumberOfFiles: filesMin,
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
          //uppyDashboard.use(Webcam, {target: Dashboard});
          uppyDashboard.use(GoogleDrive, { target: Dashboard, companionUrl: 'https://companion.uppy.io' });
          uppyDashboard.on('upload-success', (file, response) => {
            const fileName = file.name
            if (file.extension === 'pdf')
            {
             const urlPDF = response.body
             $('#archivosProveedor').data("rutaarchivoPDF", urlPDF)
             document.querySelector('.uploaded-files-proveedor').innerHTML +=
             `<ol><li id="listaArchivos"><a href="${urlPDF}" target="_blank" name="url" id="RutaPDF">${fileName}</a></li></ol>`
             //IDUsuraio_ == 3126 ? getSerieProveedor(idprov).then((response) =>  (response.Serie, uppyDashboard, "Proveedor")).catch((e) => (uppyDashboard.cancelAll(), $('.uploaded-files ol').remove(), alertToastError("Algo salio mal :("))): '';
           }
           else
           {
             const urlXMLCheck = response.body
             totalXMLProveedor = leerXMLTransportista(urlXMLCheck)
//             var folioInFactura = FolioViajeXML(urlXMLCheck, folioCheck)
             GetFolioViajeXML(urlXMLCheck, folioCheck)
             GetValidacionCFDIAndOther(urlXMLCheck)
             if(+totalXMLProveedor > (Number(totalViaje.toFixed(2)) + 1) || totalXMLProveedor == null || !FViaje || !valCFDIAndOther)
             {
               alertToastError(`La factura no coincide con el sistema, por favor intente de nuevo.`)
               uppyDashboard.cancelAll()
               $('.uploaded-files-proveedor ol').remove();
             }
             else
             {
                uuid = GetUUID(urlXMLCheck);
                const urlPDF = response.body
                $('#archivosProveedor').data("rutaarchivoXML", urlPDF)
                document.querySelector('.uploaded-files-proveedor').innerHTML +=
                `<ol><li id="listaArchivos"><a href="${urlPDF}" target="_blank" name="url" id="RutaXML">${fileName}</a></li></ol>`
                getSerieProveedor(idprov).then((response) => fnCheckFolio(response.Serie + getFolioXML(urlXMLCheck), uppyDashboard, "Proveedor")).catch((e) => (uppyDashboard.cancelAll(), $('.uploaded-files ol').remove(), alertToastError("Algo salio mal :(")));
             }
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


    function limpiarDivProveedor()
    {
      $('#archivosProveedor').data("rutaarchivoXML", null);
      $('#archivosProveedor').data("rutaarchivoPDF", null);
      $('.uploaded-files-proveedor ol').remove();
      $('#contenedorSubirArchivosproveedor').css("display", "none");
      $('#inputBuscarFolioProveedor').prop("disabled", false);
      $('#buscarFolioProveedor').prop("disabled", false);
      $('#inputBuscarFolioProveedor').val('');
      $('#txtFolioFacturaP').val('');
      $('#txtComentariosP').val('');
      folioCheck="";
      valCFDIAndOthe=""
    }
