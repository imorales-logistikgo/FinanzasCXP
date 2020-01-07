var table;
var proveedor;
var rutaComprobante;
$(document).ready(function()
{
  var calculo =0;
  var evXML;
  var idfac;
  var totConv=0;
  var isAuth;
//tabla estados de cuenta

formatDataTableFacturas();

$('#TableEstadosdeCuenta').css("display", "block");
// table.columns.adjust().draw();
//ejecuta varias funciones cada que el checkbox es seleccionado en la tabla estados de cuenta
$(document).on( 'change', 'input[name="checkEC"]', function () {
  var input = 'input[name="checkEC"]';
  var btnSubir = '#btnSubirPagos';
  if($(this).is(':checked'))
  {
    ValidacionCheckboxPagos();
    Getdatos();
    ContadorCheck(input, btnSubir);
  }
  else
  {
    Getdatos();
    ContadorCheck(input, btnSubir);
  }
});

$('#btnAplicarFiltro').on('click', fnGetFacturas);

$(document).on('click', '.btnDetalleFactura',getDetalleFactura);

$(document).on('click', '.btnDetallePago',getDetallePago);

//eliminar row de la tabla estados de cuenta
$(document).on( 'click', '.btnEliminarFactura', function () {
 Swal.fire({
  title: '¿Estas Seguro?',
  text: "Estas a un click de eliminar algo importante",
  type: 'warning',
  showCancelButton: true,
  confirmButtonColor: '#3085d6',
  cancelButtonColor: '#d33',
  confirmButtonText: 'Aceptar'
}).then(function(result) {
  if(result.value)
    return fnCancelarFactura($(this).data('idfact'));
}.bind(this)
).then((result) => {
  if (result) {
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


//Aprobar factura subida por el proveedor
$(document).on('click', '.btnAprobarFactura',function(){
  Swal.fire({
   title: '¿Estas Seguro?',
   text: "Validaras una factura importante",
   type: 'warning',
   showCancelButton: true,
   confirmButtonColor: '#5cb85c',
   cancelButtonColor: '#d33',
   confirmButtonText: 'Validar'
 }).then((result) => {
  if (result.value) {
  var btn = $(this);
    WaitMe_Show('#TbPading');
    var idFac = $(this).data('idfact');
    ValidarFactura(idFac, btn);
  }
})
});


//elementos a mostrar al abrirse el modeal de subir cobros
$('#modalSubirPagos').on('shown.bs.modal', function(){
  $('#FechaPago').datepicker({
    format: 'yyyy/mm/dd',
    todayHighlight: true
  });
  $("#FechaPago").datepicker('setDate', 'today' );

});

$(document).on('change', '#FolioPago', fnCheckFolio);

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
$('input[name="FiltroFechaPagos"]').daterangepicker({
 autoUpdateInput: false
});

$('input[name="FiltroFechaPagos"]').on('apply.daterangepicker', function(ev, picker) {
  $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
});


// cerrar modal de subir facturas
$('#modalSubirPagos').on('hidden.bs.modal', function(){
 CleanModal()
 var id = '#ComplementosPagos';
 var verComp = '.uploaded-files-pagos';
 KTUppyEvidencias.init(id, verComp)
});


//muestra los datos para la tabla del modal subir cobros al hacer click en el boton de  subir cobro
$(document).on('click', '#btnSubirPagos', function() {
  showDatosObtenidos();
  mostrarTipoCambio();
});

//validar el total del cobro por cada factura seleccionada -- en el modal subir cobros
$('#tableAddPago').on("keyup change", 'input[name="totalPago"]', function(){
  var table1 = $('#tableAddPago').DataTable();
  var datosRow = table1.row($(this).parents('tr')).data();
  if(datosRow[3] === 'MXN')
  {
    if(parseFloat($(this).val()) >= 0)
    {
    if(parseFloat($(this).val()) > datosRow[2].replace(/(\$)|(,)/g,''))
    {
      (datosRow[3] === 'MXN') ?  $(this).val(datosRow[2].replace(/(\$)|(,)/g,'')) : $(this).val(totConv)
    }
    }
    else
    {
      alertToastError("No se aceptan numero negativos o caracteres");
      //$('#btnSavePago').prop('disabled', true);
      $(this).val('');
    }
  }
  else
  {
    if(parseFloat($(this).val()) >= 0)
    {
    if(parseFloat($(this).val()) > totConv)
    {
      (datosRow[3] === 'MXN') ?  $(this).val(datosRow[2].replace(/(\$)|(,)/g,'')) : $(this).val(totConv)
    }
    }
    else
    {
      alertToastError("No se aceptan numero negativos o caracteres");
      $(this).val('');
    }
  }
  $('input#valCobro').each(function(){
   calculo = calculo + parseFloat($(this).val());
 });
  $('#AddCosto').val(truncarDecimales(calculo, 2));
  calculo = 0;
});


//validacion si tienes los archivos pdf y xml
$(document).on('click', '#btnSavePago', function(){
    if($('input[name="FolioPago"]').val() != "" && $('#FechaPago').val() != "" && $('input[name="totalPago"]').val() != "" && $('input[name="TipoCambioPago"]').val() != "")
    {
      savePagoxProveedor();
    }
    else
    {
      alertToastError("El folio, la fecha y el pago no pueden ser vacios");
    }
  });


//ocultar o mostrar campos de la tabla
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

//inicia el modal de subir complementos
KTUtil.ready(function() {
  var id = '#ComplementosPagos';
  var verComp = '.uploaded-files-pagos';
  KTUppyEvidencias.init(id, verComp);
});

$('input[name="TipoCambioPago"]').on('keyup change', function(){
  if($('input[name="TipoCambioPago"]').val() >=1)
  {
    showDatosObtenidos();
  }
  else
  {
    alertToastError("El tipo de cambio debe ser mayor a 0");
    $('input[name="TipoCambioPago"]').val('');
  }

});


//FUNCIONES DE ESTADOS DE CUENTA

//funcion limpiar modal
function CleanModal()
{
 $('input[name="FolioPago"]').val('');
 $('.uploaded-files-pagos ol').remove();
 $('#comentariosEC').val('');
 $('#TipoCambioPago').val(1);
 calculo = 0;
 totConv = 0;
 $('#ComplementosPagos').data("rutaarchivoXML", "");
 $('#ComplementosPagos').data("rutaarchivoPDF", "");
}


//obtiene los datos de cada checkbox seleccionado
function Getdatos(){
  var arrSelect=[];
  $("input[name=checkEC]:checked").each(function () {
    var datosRow = table.row($(this).parents('tr')).data();
    var prueba = $(this).data("idfactu");
    arrSelect.push([datosRow[1],datosRow[7], datosRow[8], datosRow[9], datosRow[7], prueba, datosRow[2]]);
  });
  return arrSelect;
}


//funcion para mostrar u ocultar el input del timpo de cambio
function mostrarTipoCambio()
{
  var found;
  var datos = Getdatos();
  for(var i=0; i<datos.length; i++)
  {
    // datos[i][3].push(datos[i][3]);
    found = datos[i][3].includes('USD');
  }
  if(found != true)
  {
   $('#tipoCambioP').hide();
 }
 else
 {
   $('#tipoCambioP').show();
 }
}

//funcion para obtener los datos de la tabla Estados de cuenta para mostrarlos en la tabla del modal subir pagos
function showDatosObtenidos(){
 var datos = Getdatos();
 var TBalance=0, total=0;
 for (var i=0; i<datos.length; i++)
 {
   if(datos[i][3] == 'MXN')
   {
     var Balance = parseFloat(datos[i][2].replace(/(\$)|(,)/g,''));
     var tot = parseFloat(datos[i][1].replace(/(\$)|(,)/g,''));
     total = total + Balance;
   }
   if(datos[i][3] == 'USD')
   {
     var tipoCambio = $('input[name="TipoCambioPago"]').val();
     var Balance = parseFloat(datos[i][2].replace(/(\$)|(,)/g,'') * tipoCambio);
     var tot = parseFloat(datos[i][1].replace(/(\$)|(,)/g,''));
     totConv = Balance;
      // datos[i].push(tot);
      total = total + Balance;
    }

  }

  var h = [datos];
  $('#tableAddPago').DataTable({
  "responsive": false,
    "language": {
      "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
    "paging": false,
    "info":   false,
    destroy: true,
    data: h[0],
    columnDefs: [
    {
     "className": "text-center",
     "targets": 0,
   },
   {
     "className": "text-right",
     "targets": [1,2]
   },
   {
    "className": "text-center",
    "targets": 3
  },
  {
    "className": "dt-head-center dt-body-right",
    "targets": 4,
    "mRender": function (data, type, full) {
     return (full[3] === 'MXN' ? `$ <input class="col-md-6 col-sm-6 text-right valCobro" type="number" data-idfact="${full[5]}" name="totalPago" id="valCobro" value="${full[2].replace(/(\$)|(,)/g,'')}" min="0" pattern="^[0-9]+" required>` : '$ <input type="number" class=""col-md-6 col-sm-6 text-right valCobro" data-idfact="'+ full[5] +'" name="totalPago" id="valCobro" value="'+totConv+'" min="0" pattern="^[0-9]+">');
   }
 },

 ]
});

  $('#AddCosto').val(truncarDecimales(total, 2));
}


//validacion mismo cliente en los checkbox
function ValidacionCheckboxPagos(){
  var checked = $("input[name='checkEC']:checked");
  $("input[name=checkEC]:checked").each(function () {
   var check = table.row($(this).parents('tr')).data();
   if(checked.length > 1)
   {
     if (check[2] != proveedor /*|| check[8] != moneda*/) {
       $(this).prop('checked', false);
       alertToastError("El proveedor debe ser el mismo");
     }
     else
     {
      console.log("ok");
    }
  }
  else
  {
    proveedor = check[2];
   // moneda = check[8];
 }
});
}

$('#tablaDetalles').DataTable({
  "responsive": true
});


});

var fnGetFacturas = function () {
  arrStatus = $('#cboStatus').val();
  arrProveedor = $('#cboCliente').val();
  strMoneda = [];
  $('#rdMXN').is(':checked') ? strMoneda.push('MXN') : null;
  $('#rdUSD').is(':checked') ? strMoneda.push('USD') : null;
  WaitMe_Show('#divTablaFacturas');
  if($('#chkMonthYear').is(':checked')){
    arrMonth = $('#filtroxMes').val();
    Year = $('#filtroxAno').val();
    getFacturas("arrMonth="+ JSON.stringify(arrMonth) +"&Year="+ Year +"&Status="+ JSON.stringify(arrStatus) +"&Proveedor="+ JSON.stringify(arrProveedor) +"&Moneda="+ JSON.stringify(strMoneda));
  }
  else{
    startDate = ($('#cboFechaDescarga').data('daterangepicker').startDate._d).toLocaleDateString('en-US');
    endDate = ($('#cboFechaDescarga').data('daterangepicker').endDate._d).toLocaleDateString('en-US');
    getFacturas("FechaFacturaDesde="+ startDate +"&FechaFacturaHasta="+ endDate +"&Status="+ JSON.stringify(arrStatus) +"&Proveedor="+ JSON.stringify(arrProveedor) +"&Moneda="+ JSON.stringify(strMoneda));
  }
}

function getFacturas (params) {
  fetch("/EstadosdeCuenta/FilterBy?" + params, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    return response.clone().json();
  }).then(function(data){
    WaitMe_Hide('#divTablaFacturas');
    $('#divTablaFacturas').html(data.htmlRes);
    formatDataTableFacturas();
    $('#TableEstadosdeCuenta').css("display", "block");
  }).catch(function(ex){
    console.log("no success!");
  });
}

var fnCancelarFactura = async function (IDFactura) {
  var res = false;
  jParams = {
    IDFactura: IDFactura,
  }
  WaitMe_Show('#divTablaFacturas');
  await fetch("/EstadosdeCuenta/CancelarFactura", {
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
      res = true;
    }
    else if(response.status == 500)
    {
      res = false;
    }
  }).catch(function(ex){
    res = false;
  });
  WaitMe_Hide('#divTablaFacturas');
  return res;
}

function formatDataTableFacturas(){
  table = $('#TableEstadosdeCuenta').DataTable({
    "scrollX": true,
    //"scrollY": "500px",
    "scrollCollapse": true,
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
    }
    ],
    fixedColumns:   {
      leftColumns: 1
    },

    columnDefs: [ {
      orderable: false,
      targets:   0,
      "className": "text-center",
      "width": "1%",
      "mRender": function (data, type, full) {
        isAuth = $('input[name="EvidenciaXML"]').data("isautorizada");
        idfac = $('input[name="EvidenciaXML"]').data("facturaid");
        return (full[10] != 'Cobrada' && full[10] != 'Cancelada' && full[10] != 'Pagada'? '<input type="checkbox" name="checkEC" id="estiloCheckbox" data-idfactu="'+idfac+'"/>': '');
      }
    },
    {
      "name": "Status",
      "width": "10%",
      "className": "text-center bold",
      "targets": 1,
      "mRender": function (data, type, full) {
        idfac = $('input[name="EvidenciaXML"]').data("facturaid");
        return `<a  href="#detallesFactura" class="btnDetalleFactura" data-toggle="modal" data-backdrop="static" data-keyboard="false" id="foliofactura">${full[1]}</a>`;
      }
    },
    {
      "name": "Status",
      "width": "10%",
      "className": "text-center",
      "targets": [2,3]
    },
    {
      "width": "5%",
      "className": "text-center",
      "targets": [9, 10]

    },
    {
      "className": "text-right",
      'width' : '5%',
      "targets": [4,5,6,7,8]
    },
    {
      "name": "Status",
      //"width": "5%",
      "className": "text-center bold",
      "targets": 11,
      "mRender": function (data, type, full) {
        idfac = $('input[name="EvidenciaXML"]').data("facturaid");
        return `<a  href="#detallesPago" class="btnDetallePago" data-toggle="modal" data-backdrop="static" data-keyboard="false" data-folio="${full[11]}" id="foliopagos">${full[11]}</a>`;
      }
    },
    {
      "width": "3%",
      "className": "text-center",
      "targets": 12,
      "mRender": function (data, type, full) {
        evXML = $('input[name="EvidenciaXML"]').data("evidenciaxml");
        return '<a href="'+evXML+'" target="_blank" class="BtnVerXML btn btn-primary btn-elevate btn-pill btn-sm"><i class="flaticon2-file" title="XML"></i></a>';
      }
    },
    {
      "width": "3%",
      "className": "text-center",
      "targets": 13,
      "mRender": function (data, type, full) {
       return ( full[10] == 'Pendiente' && isAuth != 'True' ? '<button type ="button" title="Aprobar" class="btnAprobarFactura btn btn-success btn-elevate btn-pill btn-sm" data-idfact="'+idfac+'"><i class="flaticon2-checkmark"></i></button>':'');
     }
    },
    {
      "width": "3%",
      "className": "text-center",
      "targets": 14,
      "mRender": function (data, type, full) {
       return ( full[10] === 'Pendiente' ? '<button type ="button" class="btnEliminarFactura btn btn-danger btn-elevate btn-pill btn-sm" data-idfact="'+idfac+'" title="Eliminar"><i class="flaticon-delete"></i></button>':'');
     }
   }
   ]
 });
}




function getDetalleFactura()
{
  var IDFactura = $(this).parents('tr').data('idfactura');
  WaitMe_Show('#divTableDetalles');

  fetch("/EstadosdeCuenta/GetDetallesFactura?IDFactura=" + IDFactura, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    return response.clone().json();
  }).then(function(data){
    WaitMe_Hide('#detallesFactura');
    $('#divTableDetalles').html(data.htmlRes);
  }).catch(function(ex){
    console.log(ex);
  });
}

function getDetallePago()
{
  $('#verArchivoPDFPAgo').prop("href", "http://lgklataforma.blob.core.windows.net/evidencias/f8e459bb-6da8-4fa9-a9db-8f9292585939.pdf");
  $('#imgArchivoPDF').prop("src", "../static/img/pdf-2.png");
  $('#verArchivoXMLPAgo').prop("href", "http://lgklataforma.blob.core.windows.net/evidencias/0a2228ec-ffe0-4808-957f-df08dc5b4107.xml");
  $('#imgArchivoXML').prop("src", "../static/img/xml-logo.png");
}


function savePagoxProveedor()  {
  WaitMe_Show('#waitModalSubirPagos');
  jParams = {
    Folio: $('#FolioPago').val(),
    Total:$('#AddCosto').val(),
    FechaPago: $('#FechaPago').val(),
    TipoCambio: $('#TipoCambioPago').val(),
    Comentarios: $('#comentariosEC').val(),
    RutaComprobante: rutaComprobante,
    Proveedor: proveedor,
  }

  fetch("/EstadosdeCuenta/SavePagoxProveedor", {
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
      WaitMe_Hide('#waitModalSubirPagos');
    }

  }).then(function(IDPago){
    SavePagoxFactura(IDPago);
  }).catch(function(ex){
    console.log("no success!");
  });
}

function ValidarFactura(IDFactura, btn) {
  jParams = {
    IDFactura: IDFactura,
  }

  fetch("/EstadosdeCuenta/ValidarFactura", {
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
        title: 'La factura ha sido validada correctamente',
        showConfirmButton: false,
        timer: 2500
      })
      $(btn).remove();
      WaitMe_Hide('#TbPading');
    }
    else if(response.status == 500)
    {
      Swal.fire({
        type: 'error',
        title: 'Hubo un error validando la factura',
        showConfirmButton: false,
        timer: 2500
      })
      WaitMe_Hide('#TbPading');
    }

  }).catch(function(ex){
    console.log("no success!");
  });
}

function SavePagoxFactura(IDPago)
{
  var arrPagos = [];
  $('.valCobro').each(function() {
    IDFactura = $(this).data('idfact');
    Total = $(this).val();
    arrPagos.push({'Total': Total, 'IDFactura': IDFactura});
  });

  jParams = {
    IDPago: IDPago,
    arrPagos: arrPagos,
  }

  fetch("/EstadosdeCuenta/SavePagoxFactura", {
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
        title: 'El pago fue guardado correctamente',
        showConfirmButton: false,
        timer: 2500
      })
      $('#modalSubirPagos').modal('hide');

      var table = $('#TableEstadosdeCuenta').DataTable();
      $("input[name=checkEC]:checked").each(function () {
        table.row($(this).parents('tr')).remove().draw();
      });
      WaitMe_Hide('#waitModalSubirPagos');
    }
    else if(response.status == 500)
    {
      Swal.fire({
        type: 'error',
        title: 'El folio indicado ya existe en el sistema',
        showConfirmButton: false,
        timer: 2500
      })
      WaitMe_Hide('#waitModalSubirPagos');
    }

  }).catch(function(ex){
    console.log("no success!");
  });
}

var fnCheckFolio = function () {
  fetch("/EstadosdeCuenta/CheckFolioDuplicado?Folio=" + $('#FolioPago').val(), {
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
      $('#btnSavePago').attr('disabled',true);
    }
    else {
      $('#btnSavePago').attr('disabled',false);
    }
  }).catch(function(ex){
    console.log("no success!");
  });
}
