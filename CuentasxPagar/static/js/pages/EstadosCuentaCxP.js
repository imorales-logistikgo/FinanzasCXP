var table;
var proveedor;
$(document).ready(function()
{
  var calculo =0;
  var evXML;
  var idfac;
  var totConv=0;
//tabla estados de cuenta
formatDataTableFacturas();
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


//eliminar row de la tabla estados de cuenta
$(document).on( 'click', '.btnEliminarFactura', function () {
 Swal.fire({
  title: '¿Estas Seguro?',
  text: "Estas a un click de eliminar algo importante",
  type: 'warning',
  showCancelButton: true,
  confirmButtonColor: '#3085d6',
  cancelButtonColor: '#d33',
  confirmButtonText: 'Si'
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

//elementos a mostrar al abrirse el modeal de subir cobros
$('#modalSubirPagos').on('shown.bs.modal', function(){
  $('#FechaPago').datepicker({
    format: 'yyyy/mm/dd',
    todayHighlight: true
  });
  $("#FechaPago").datepicker('setDate', 'today' );

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
$(document).on('click', '#btnSubirPagos',showDatosObtenidos);

//validar el total del cobro por cada factura seleccionada -- en el modal subir cobros
$('#tableAddPago').on("change", 'input[name="totalPago"]', function(){
  var table = $('#tableAddPago').DataTable();
  var datosRow = table.row($(this).parents('tr')).data();
  if(parseFloat($(this).val()) >= datosRow[2])
  {
    (datosRow[3] === 'MXN') ?  $(this).val(datosRow[2]) : $(this).val(totConv)
  }
  $('input#valCobro').each(function(){
   calculo = calculo + parseFloat($(this).val());
 });
  $('#AddCosto').val(calculo);
  calculo = 0;
});


//validacion si tienes los archivos pdf y xml
$(document).on('click', '#btnSavePago', function(){
  //console.log($('input[name="TipoCambioPago"]').val());
  if($('#ComplementosPagos').data("rutaarchivoPDF") != undefined || $('#ComplementosPagos').data("rutaarchivoXML") != undefined)
  {
    if($('input[name="FolioPago"]').val() != "")
    {
      //alert("puedes subir el pago");
      savePagoxProveedor();
    }
    else
    {
      alertToastError("El folio no puede estar vacio");
    }
  }
  else
  {
    alertToastError("Son necesarios los complementos PDF y XML");
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


$('input[name="TipoCambioPago"]').on('change', function(){
  showDatosObtenidos();
});


//FUNCIONES DE ESTADOS DE CUENTA

//funcion limpiar modal
function CleanModal()
{
 $('input[name="FolioPago"]').val('');
 $('.uploaded-files ol').remove();
 $('#comentariosEC').val('');
 $('#TipoCambioPago').val(1);
 calculo = 0;
 totConv = 0;
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


//funcion para obtener los datos de la tabla Estados de cuenta para mostrarlos en la tabla del modal subir pagos
function showDatosObtenidos(){
 var datos = Getdatos();
 var TBalance=0, total=0;
 for (var i=0; i<datos.length; i++)
 {
   if(datos[i][3] == 'MXN')
   {
     var Balance = parseFloat(datos[i][2]);
     var tot = parseFloat(datos[i][1]);
     total = total + Balance;
   }
   if(datos[i][3] == 'USD')
   {
     var tipoCambio = $('input[name="TipoCambioPago"]').val();
     var Balance = parseFloat(datos[i][2] * tipoCambio);
     var tot = parseFloat(datos[i][1]);
     totConv = Balance;
      // datos[i].push(tot);
      total = total + Balance;
    }

  }

  var h = [datos];
  $('#tableAddPago').DataTable({
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
     return (full[3] === 'MXN' ? `$ <input class="col-6 text-right valCobro" type="number" data-idfact="${full[5]}" name="totalPago" id="valCobro" value="${full[2]}">` : '<input type="number" class="valCobro" data-idfact="'+ full[5] +'" name="totalPago" id="valCobro" value="'+totConv+'">');
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

});

var fnGetFacturas = function () {
  startDate = ($('#cboFechaDescarga').data('daterangepicker').startDate._d).toLocaleDateString('en-US');
  endDate = ($('#cboFechaDescarga').data('daterangepicker').endDate._d).toLocaleDateString('en-US');
  arrStatus = $('#cboStatus').val();
  arrProveedor = $('#cboCliente').val();
  strMoneda = $('#rdMXN').is(':checked') ? 'MXN' : 'USD';
  WaitMe_Show('#divTablaFacturas');
  fetch("/EstadosdeCuenta/FilterBy?FechaDescargaDesde="+ startDate +"&FechaDescargaHasta="+ endDate +"&Status="+ JSON.stringify(arrStatus) +"&Cliente="+ JSON.stringify(arrProveedor) +"&Moneda="+ strMoneda, {
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
    "scrollX": "100%",
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


    columnDefs: [ {
      orderable: false,
      targets:   0,
      "className": "text-center",
      "width": "1%",
      "mRender": function (data, type, full) {
        idfac = $('input[name="EvidenciaXML"]').data("facturaid");
        return (full[10] != 'Cobrada' && full[10] != 'Cancelada' ? '<input type="checkbox" name="checkEC" id="estiloCheckbox" data-idfactu="'+idfac+'"/>': '');
      }
    },
    {
      "name": "Status",
      "width": "5%",
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
      "targets": [8,9, 10]

    },
    {
      "className": "text-right",
      'width' : '5%',
      "targets": [4,5,6,7]
    },
    {
      "width": "3%",
      "className": "text-center",
      "targets": 12,
      "mRender": function (data, type, full) {
        evXML = $('input[name="EvidenciaXML"]').data("evidenciaxml");
        return '<a href="'+evXML+'" target="_blank" class="BtnVerXML btn btn-primary btn-elevate btn-pill btn-sm"><i class="flaticon2-file"></i></a>';
      }
    },
    {
      "width": "3%",
      "className": "text-center",
      "targets": 13,
      "mRender": function (data, type, full) {
       return ( full[10] === 'Pendiente' ? '<button type ="button" class="btnEliminarFactura btn btn-danger btn-elevate btn-pill btn-sm" data-idfact="'+idfac+'"><i class="flaticon-delete"></i></button>':'');
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
    console.log("no success!");
  });
}

function savePagoxProveedor()  {
  jParams = {
    Folio: $('#FolioPago').val(),
    Total:$('#AddCosto').val(),
    FechaPago: $('#Fechapago').val(),
    TipoCambio: $('#TipoCambioPago').val(),
    Comentarios: $('#comentariosEC').val(),
    RutaXML: $('#RutaXML').attr('href'),
    RutaPDF: $('#RutaPDF').attr('href'),
    proveedor: proveedor,
  }

  fetch("/EstadosdeCuenta/SaveCobroxCliente", {
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
      WaitMe_Hide('#WaitModalPE');
    }

  }).then(function(IDCobro){
    SavePagoxFactura(IDCobro);
  }).catch(function(ex){
    console.log("no success!");
  });
}

function SavePagoxFactura(IDCobro)
{
  var arrCobros = [];
  $('.valCobro').each(function() {
    IDFactura = $(this).data('idfact');
    Total = $(this).val();
    arrCobros.push({'Total': Total, 'IDFactura': IDFactura});
  });

  jParams = {
    IDCobro: IDCobro,
    arrCobros: arrCobros,
  }

  fetch("/EstadosdeCuenta/SaveCobroxFactura", {
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
      WaitMe_Hide('#WaitModalPE');
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
    }

  }).catch(function(ex){
    console.log("no success!");
  });
}
