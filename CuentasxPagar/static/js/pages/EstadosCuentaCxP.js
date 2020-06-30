var table, arrSelect=[];
var proveedor;
var rutaComprobante;
var idprov;
var idViajeProyecto;
var typeProyecto;
var totalIncialNoReajuste;
var ivaProcentaje = 0.16;
var retencionProcentaje = 0.04;
var diferenciaReajuste = 0;
var idFacturaReajuste, valorAnterioInputs, valorAnterioInputsRepartos, indexRowReajuste, showBtnA;
var costoRepartoDefault, costoAccesoriosDefault, costoRecoleccionDefault, costoViajeDefault, tipoViaje;
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

$(document).on('click', '.btnDetallePago', fnGetDetallePago);

//ejecuta varias funciones cada que el checkbox es seleccionado en la tabla estados de cuenta
$(document).on( 'change', 'input[name="checkEC"]', function () {
  if($(this).is(':checked'))
  {
    ValidacionCheckboxPagos($($(this).parents('tr')).data('idproveedor'), this) ? Getdatos(this):"";
    arrSelect.length >= 1 ? $('#btnSubirPagos').prop('disabled', false) : $('#btnSubirPagos').prop('disabled', true);
  }
  else
  {
    var arrN = [];
    var a = table.row($(this).parents('tr')).data();
    var prueba = $(this).data("idfactu");
    arrN.push([a[1], a[7], a[8], a[9], a[7], prueba, a[2]])
    removeItemFromArr(arrSelect, arrN)
    arrSelect.length >= 1 ? $('#btnSubirPagos').prop('disabled', false) : ($('#btnSubirPagos').prop('disabled', true), proveedor="");
  }
});

$('#btnAplicarFiltro').on('click', fnGetFacturas);

$(document).on('click', '.btnDetalleFactura',getDetalleFactura);

//$(document).on('click', '.btnDetallePago',getDetallePago);

//eliminar row de la tabla estados de cuenta
$(document).on( 'click', '.btnEliminarFactura', function () {
 Swal.fire({
  title: '¿Estas Seguro?',
  text: "Estas a un click de eliminar algo importante",
  type: 'warning',
  input: 'text',
  inputAttributes: {
    required: true,
    placeholder: "Motivo de la eliminación",
    id: "motivoEliminacionCXP"
  },
  validationMessage: 'Ingresa el motivo de la eliminación',
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
    WaitMe_Show('#TbPading');
    var idFac = $(this).data('idfact');
    var btn = $(this);
    ValidarFactura(idFac, btn);
  }
})
});


//***INICIAR CODIGO PARA LA FUNCIONALIDAD DE RAJUSTE***//

$(document).on('click', '.btnEditarFactura', function(){
  WaitMe_Show('#modalWaitReajuste');
  $('#btnSaveReajuste').prop('disabled', true);
  showBtnA = $(this);
  var t =  $('#TableEstadosdeCuenta').DataTable();
  var totalXMl_ = t.row($(this).parents('tr')).data()[16];
  indexRowReajuste = t.row($(this).parents('tr')).index();
  idFacturaReajuste = $(this).data('idfact');
  fetch(`/EstadosdeCuenta/GetDataReajuste?IDFactura=${$(this).data('idfact')}`, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    if (response.status == 200)
    {
      return response.clone().json();
    }
    else if (response.status == 500)
    {
      Swal.fire({
        type: 'error',
        title: 'Algo salio mal, por favor intenta de nuevo',
        showConfirmButton: false,
        timer: 2500
      })
      $('#ModalReajusteCXP').modal('hide');
      WaitMe_Hide('#modalWaitReajuste');
    }
  }).then(function(data){
    $('#CostoReajuste').val(+data.DataBKG[0].CostoViaje.toFixed(2));
    data.DataBKG[0].Proyecto == 'BKG' ? $('#CostoRecoleccionReajuste').val(+data.DataBKG[0].CostoRecoleccion.toFixed(2)): ($('#CostoRecoleccionReajuste').val(0));
    $('#CostoRecoleccionReajuste').val() == 0 ? $('#CostoRecoleccionReajuste').prop('disabled', true) : $('#CostoRecoleccionReajuste').prop('disabled', false)
    $('#costoAccesoriosReajuste').val(+data.DataBKG[0].CostoAccesorios.toFixed(2))
    $('#costoRepartosReajuste').val(+data.DataBKG[0].CostoRepartos.toFixed(2))
    $('#subtotalReajuste').val(+data.DataBKG[0].CostoSubtotal.toFixed(2));
    $('#IVAReajuste').val(+data.DataBKG[0].CostoIVA.toFixed(2));
    $('#RetencionReajuste').val(+data.DataBKG[0].CostoRetencion.toFixed(2));
    $('#TotalReajuste').val(+data.DataBKG[0].CostoTotal.toFixed(2));
    tipoViaje = data.DataBKG[0].TipoViaje;

    $('#costoAccesoriosReajuste').val() == 0 ? $('#AccesoriosReajuste').prop('disabled', true): $('#AccesoriosReajuste').prop('disabled', false);
    $('#costoRepartosReajuste').val() == 0 ? $('#RepartosReajuste').prop('disabled', true):$('#RepartosReajuste').prop('disabled', false);

    idViajeProyecto = data.DataBKG[0].IDViaje;
    typeProyecto = data.DataBKG[0].Proyecto;
    totalIncialNoReajuste = +data.DataBKG[0].CostoTotal.toFixed(2);
    costoViajeDefault = +data.DataBKG[0].CostoViaje.toFixed(2);
    costoRecoleccionDefault = +$('#CostoRecoleccionReajuste').val();
    costoRepartoDefault = $('#costoRepartosReajuste').val();
    costoAccesoriosDefault = $('#costoAccesoriosReajuste').val();
    xmlValor = +totalXMl_;
    $('#FolioReajuste').html(data.DataBKG[0].Folio);
    +$('#TotalProveedor').val(xmlValor.toFixed(2)) != totalIncialNoReajuste ? $('#TotalProveedor').css('background-color', '#F91919') : $('#TotalProveedor').css('background-color', '#09DD08');
    WaitMe_Hide('#modalWaitReajuste');
  }).catch(function(ex){
    console.log(ex);
  });

});


//Modal reajuste de los accesorios
$('#ModalReajusteAccesorios').on('shown.bs.modal', function(){
  WaitMe_Show('#modalWaitReajusteAccesorios');
  fetch(`/EstadosdeCuenta/GetAccesoriosxViaje?IDViaje=${idViajeProyecto}&Proyecto=${typeProyecto}`, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    if (response.status == 200)
    {
      return response.clone().json();
    }
    else if (response.status == 500)
    {
      Swal.fire({
        type: 'error',
        title: 'Algo salio mal, por favor intentalo de nuevo',
        showConfirmButton: false,
        timer: 2500
      })
    }
  }).then(function(data){
    var accesorioCosto = 0;
    if (typeProyecto == 'BKG'){
      for (var i = 0; i<data.NewData.length; i++)
      {
        document.querySelector(".listaAccesorios").innerHTML += `
        <div>
          <div class="row py-2" >
            <div class="col col-md-7">
             <label>`+data.NewData[i].NombreAccesorio+`</label>
            </div>
            <div class="col col-md-5" id="inputsAccesoriosModal">
              <input type="number" name="dataAccesoriosIPT" min="0" class="form-control" data-isretencion="`+data.NewData[i].IsAplicaRetencion+`" id="`+data.NewData[i].NombreAccesorio.replace(/ /g, "")+`" value="`+data.NewData[i].CostoAccesorio+`">
            </div>
          </div>
        </div>`;
      }
    }
    else if (typeProyecto == 'XD') {
      var dataJsonAccesorios = jsonAccesoriosXD();
      for (var i=0; i < dataJsonAccesorios.length; i++)
        {
          for (var j = 0; j<data.NewData.length; j++)
          {
              accesorioCosto = dataJsonAccesorios[i].descripcion == data.NewData[j].NombreAccesorio ? dataJsonAccesorios[i].costo = data.NewData[j].CostoAccesorio : accesorioCosto;
          }
          document.querySelector(".listaAccesorios").innerHTML += `
          <div>
            <div class="row py-2" >
              <div class="col col-md-7">
               <label>`+dataJsonAccesorios[i].descripcion+`</label>
              </div>
              <div class="col col-md-5" id="inputsAccesoriosModal">
                <input type="number" name="dataAccesoriosIPT" min="0" class="form-control" data-isretencion="`+dataJsonAccesorios[i].IsAplicaRetencion+`" id="`+dataJsonAccesorios[i].descripcion.replace(/ /g, "")+`" value="`+accesorioCosto+`" required>
              </div>
            </div>
          </div>`;
          accesorioCosto = 0;
          data.NewData[0] == undefined ? $('input[id="'+dataJsonAccesorios[i].descripcion+'"]').prop('disabled', true): $('input[id="'+dataJsonAccesorios[i].descripcion+'"]').prop('disabled', false);
        }
    }

    $('#cTotalAccesorios').val($('#costoAccesoriosReajuste').val());
    WaitMe_Hide('#modalWaitReajusteAccesorios');
  }).catch(function(ex){
    console.log(ex)
  });
});


//modal reajuste de los repartos
$('#ModalReajusteRepartos').on('shown.bs.modal', function(){
  WaitMe_Show('#modalWaitReajusteRepartos');
  fetch("/EstadosdeCuenta/GetRepartosxViaje?IDViaje="+ idViajeProyecto+"&Proyecto="+typeProyecto, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    if (response.status == 200)
    {
      return response.clone().json();
    }
    else if (response.status == 500)
    {
      Swal.fire({
        type: 'error',
        title: 'Algo salio mal, por favor intentalo de nuevo',
        showConfirmButton: false,
        timer: 2500
      })
    }
  }).then(function(data){
    for (var i=0; i < data.NewDataR.length; i++)
      {
        document.querySelector("#trRepartos").innerHTML += `
            <tr>
              <td></td>
              <td>`+data.NewDataR[i].deliveries+`</td>
              <td>`+data.NewDataR[i].ciudadDestino+`</td>
              <td><input type="number" class="form-control" id="costoRepartosInput" value="`+data.NewDataR[i].costo+`"></td>
            </tr>`;
      }
    formatoTableRepartos();
    WaitMe_Hide('#modalWaitReajusteRepartos');
  }).catch(function(ex){
    console.log(ex)
  });
});


//al cerrar el modal de reajuste los campos se limpian
$('#ModalReajusteCXP').on('hidden.bs.modal', cleanModalReajuste);

//al cerrar el modal de accesorios los campos del modal se limpian
$(document).on('hidden.bs.modal', '#ModalReajusteAccesorios', cleanModalAccesorios);

// al cerrar el modal de repartos, los campos del modal se limpian
$(document).on('hidden.bs.modal', '#ModalReajusteRepartos', function(){
  $('#tableRepartos').DataTable().destroy();
  $('#trRepartos tr').remove();
  $('#btnSaveRepartosReajuste').prop('disabled', true);
});

//validar que solo el total se pueda reajustar solo $1
$("#TotalReajuste").on('change', function(){
  $(this).val() > (+totalIncialNoReajuste + 1) || $(this).val() < (+totalIncialNoReajuste - 1) ? ($(this).val(+totalIncialNoReajuste), alertToastError("Solo se permite ajustar $1")) : (diferenciaReajuste = $(this).val() - (+totalIncialNoReajuste));
  +$('#TotalProveedor').val() == +$('#TotalReajuste').val() ? ($('#TotalProveedor').css('background-color', '#09DD08'), $('#btnSaveReajuste').prop('disabled', false)) : ($('#TotalProveedor').css('background-color', '#F91919'), $('#btnSaveReajuste').prop('disabled', true));
})

//recalculo cuando se modifica el valor del costo
$("#CostoReajuste").on('change', function(){
  WaitMe_Show('#modalWaitReajuste');
  +$(this).val() > costoViajeDefault ? ($(this).val(costoViajeDefault), alertToastError(`El total no puede ser mayor a $${costoViajeDefault}`), getAccesorios()) : (getAccesorios());
  WaitMe_Hide('#modalWaitReajuste');
});

$("#CostoRecoleccionReajuste").on('change', function(){
  WaitMe_Show('#modalWaitReajuste');
  +$(this).val() > costoRecoleccionDefault ? ($(this).val(costoRecoleccionDefault), alertToastError(`El total no puede ser mayor a $${costoRecoleccionDefault}`), getAccesorios()) : (getAccesorios());
  WaitMe_Hide('#modalWaitReajuste');
});

//onfocus para obtener el valor del input de los accesorios antes del evento change
$(document).on('focus', "input[name='dataAccesoriosIPT']", function(){
  valorAnterioInputs = $(this).val();
});

//validaciones para el reajuste de accesorios
$(document).on('change', "input[name='dataAccesoriosIPT']",function(){
  var newTotalAccesorios = reajusteAccesorios();
  newTotalAccesorios > costoAccesoriosDefault ? ($(this).val(valorAnterioInputs), alertToastError(`El total no puede ser mayor a $${costoAccesoriosDefault}`), $("#btnSaveAccesoriosReajuste").prop('disabled', true)) : ($('#cTotalAccesorios').val(newTotalAccesorios), $("#btnSaveAccesoriosReajuste").prop('disabled', false));
});

//onfocus para obtener el valor del input de los repartos antes del evento change
$(document).on('focus', "input[id=costoRepartosInput]", function(){
  valorAnterioInputsRepartos = $(this).val();
});

//validaciones para el reajuste de los repartos
$(document).on('change', '#costoRepartosInput', function(){
  var newTotalRepartos = reajusteRepartos();
  newTotalRepartos > costoRepartoDefault ? ($(this).val(valorAnterioInputsRepartos), alertToastError(`El total no puede ser mayor a $${costoRepartoDefault}`), $('#btnSaveRepartosReajuste').prop('disabled', true)) : ($('#costoRepartosReajuste').val(newTotalRepartos), $('#btnSaveRepartosReajuste').prop('disabled', false));
})

//guardar nuevo total de reajuste de repartos
$(document).on('click', '#btnSaveRepartosReajuste', function(){
  getAccesorios();
  $('#ModalReajusteRepartos').modal('hide');
  $('#TotalReajuste').prop('disabled', true);
});

//guardar nuevo total de reajuste de accesorios
$("#btnSaveAccesoriosReajuste").on('click', function(){
  $('#costoAccesoriosReajuste').val($('#cTotalAccesorios').val());
  recalculoRetencion();
  $('#ModalReajusteAccesorios').modal('hide');
  $('#TotalReajuste').prop('disabled', true);
});

// guardar los nuevos valores del reajuste
$('#btnSaveReajuste').on('click', function(){
  WaitMe_Show('#modalWaitReajuste');
  jParams = {
    IDFactura: idFacturaReajuste,
    Costo: $('#CostoReajuste').val(),
    CostoRecoleccion: $('#CostoRecoleccionReajuste').val(),
    CostoAccesorios:$('#costoAccesoriosReajuste').val(),
    CostoRepartos: $('#costoRepartosReajuste').val(),
    Subtotal: $('#subtotalReajuste').val(),
    IVA: $('#IVAReajuste').val(),
    Retencion: $('#RetencionReajuste').val(),
    Total: $('#TotalReajuste').val(),
    DiferenciaReajuste: diferenciaReajuste.toFixed(2),
    IDViaje: idViajeProyecto,
    Proyecto: typeProyecto,
    Motivo: $('#MotivoReajuste').val(),
  }
  fetch("/EstadosdeCuenta/saveReajuste", {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify(jParams)
  }).then(function(response,DataFacturaByID){
    if(response.status == 200)
    {
      return response.clone().json();
    }
    else if(response.status == 500 || response.status == 400)
    {
      Swal.fire({
        type: 'error',
        title: 'No se pudo guardar el reajuste',
        showConfirmButton: false,
        timer: 3500
      })
      WaitMe_Hide('#modalWaitReajuste');
     }
  }).then(function(data){
    var t =  $('#TableEstadosdeCuenta').DataTable();
    for (var i=0; i<data.DataFacturaByID.length; i++)
    {
       t.cell(indexRowReajuste,4).data(data.DataFacturaByID[i].newSubtotal);
       t.cell(indexRowReajuste,5).data(data.DataFacturaByID[i].newIVA);
       t.cell(indexRowReajuste,6).data(data.DataFacturaByID[i].newRetencion);
       t.cell(indexRowReajuste,7).data(data.DataFacturaByID[i].newTotal);
       t.cell(indexRowReajuste,8).data(data.DataFacturaByID[i].newTotal);
    }

    var btnEditar = (showBtnA)[0];
    $(btnEditar).css('display', 'none');
    var showbtn_= $(showBtnA).parents("tr").find("td")[14];
    var btnAprov = $(showbtn_).children()[0];
    btnAprov.style.display = "block";

   Swal.fire({
      type: 'success',
      title: 'Reajuste guardado correctamente',
      showConfirmButton: true,
      timer: 3500
    })
    $('#ModalReajusteCXP').modal('hide');
    WaitMe_Hide('#modalWaitReajuste');
  }).catch(function(ex){
    console.log(ex);
  });
});



//***TERMINA CODIGO PARA LA FUNCIONALIDAD DE REAJUSTE***//



//elementos a mostrar al abrirse el modeal de subir cobros
$('#modalSubirPagos').on('shown.bs.modal', function(){
  $('#FechaPago').datepicker({
    format: 'yyyy/mm/dd',
    todayHighlight: true,
    language: 'es'
  });
  $("#FechaPago").datepicker('setDate', 'today' );

});

$(document).on('change', '#FolioPago', fnCheckFolioEC);

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
      if(parseFloat($(this).val()) > datosRow[7])
      {
        (datosRow[3] === 'MXN') ?  $(this).val(datosRow[2].replace(/(\$)|(,)/g,'')) : $(this).val(datosRow[7])
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
 rutaComprobante = "";
}
//funcion para mostrar u ocultar el input del timpo de cambio
function mostrarTipoCambio()
{
  var found;
  var datos = arrSelect;
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

//validacion mismo cliente en los checkbox
function ValidacionCheckboxPagos(validarIdProveedor_, check_){
  var checked = $("input[name='checkEC']:checked");
  idprov = $($(checked[0]).parents('tr')[0]).data("idproveedor");
  proveedor == undefined || proveedor == '' ? proveedor = validarIdProveedor_ : validarMismoProveedor(validarIdProveedor_, check_)
  return (validarIdProveedor_ == proveedor)
}

//funcion para obtener los datos de la tabla Estados de cuenta para mostrarlos en la tabla del modal subir pagos
function showDatosObtenidos(){
 var datos = arrSelect;
 var TBalance=0, total=0;
 for (var i=0; i<datos.length; i++)
 {
   if(datos[i][3] == 'MXN')
   {
     var Balance = +datos[i][2].replace(/(\$)|(,)/g,'');
     var tot = +datos[i][1].replace(/(\$)|(,)/g,'');
     total = total + Balance;
   }
   if(datos[i][3] == 'USD')
   {
     var tipoCambio = $('input[name="TipoCambioPago"]').val();
     var Balance = +datos[i][2].replace(/(\$)|(,)/g,'') * tipoCambio;
     var tot = +datos[i][1].replace(/(\$)|(,)/g,'');
     totConv = Balance;
     datos[i].splice(7, 1, totConv)
     total = total + Balance;
    }
  }

  var h = [datos];
  $('#tableAddPago').DataTable({
  "responsive": false,
  "scrollX":false,
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
     "width": "150px"
   },
   {
     "className": "text-right",
     "targets": [1,2],
     "width": "150px"
   },
   {
    "className": "text-center",
    "targets": 3,
    "width": "150px"
  },
  {
    "className": "dt-head-center dt-body-right",
    "targets": 4,
    "width": "150px",
    "mRender": function (data, type, full) {
     return (full[3] === 'MXN' ? `$ <input class="col-md-6 col-sm-6 text-right valCobro" type="number" data-idfact="${full[5]}" name="totalPago" id="valCobro" value="${full[2].replace(/(\$)|(,)/g,'')}" min="0" pattern="^[0-9]+" required>` : `$ <input type="number" class="col-md-6 col-sm-6 text-right valCobro" data-idfact="${full[5]}" name="totalPago" id="valCobro" value="${full[7]}" min="0" pattern="^[0-9]+">`);
   }
 },

 ]
});

  $('#AddCosto').val(total.toFixed(2));
}

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
    arrSelect = [];
    proveedor = '';
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
    MotivoEliminacion: $('#motivoEliminacionCXP').val()
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
    "scrollY": "360px",
    "language": {
      "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
    },
    "responsive": false,
    "paging": false,
    //"lengthMenu": [20],
    "dom": 'Bfrtip',
    "buttons": [
    {
      extend: 'excel',
      text: '<i class="fas fa-file-excel fa-lg"></i>',
      exportOptions: {
              columns: ':visible'
      }
    }
    ],
    columnDefs: [ {
      orderable: false,
      targets:   0,
      "className": "text-center",
      "width": "1%",
      "mRender": function (data, type, full) {
        isAuth = $('input[name="EvidenciaXML"]').data("isautorizada");
        idfac = $('input[name="EvidenciaXML"]').data("facturaid");
        return (full[10] != 'cancelada'.toUpperCase() && full[10] != 'pagada'.toUpperCase() && isAuth != 'False' ? '<input type="checkbox" class="chk" name="checkEC" id="estiloCheckbox" data-idfactu="'+idfac+'"/>': '<input type="checkbox" name="checkEC" id="estiloCheckbox" data-idfactu="'+idfac+'" style="display:none"/>');
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
      "className": "text-right",
      'width' : '5%',
      "targets": [4,5,6,7,8]
    },
    {
      "width": "5%",
      "className": "text-center",
      "targets": 9
    },
    {
      "width": "5%",
      "className": "text-center",
      "targets": 10,
      "mRender": function (data, type, full) {
        return (full[10] == 'CANCELADA' ? 'RECHAZADA':full[10]);
      }
    },
    {
      "name": "Status",
      //"width": "5%",
      "className": "text-center bold",
      "targets": 11,
      "mRender": function (data, type, full) {
        idfac = $('input[name="EvidenciaXML"]').data("facturaid");
        return (full[11] != "" ? `<a  href="#detallesPago" class="btnDetallePago" data-toggle="modal" data-backdrop="static" data-keyboard="false" data-folio="${full[11]}" id="foliopagos">Ver Pagos</a>` : "");
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
        var totalSistema = +full[7].replace(/(\$)|(,)/g,'');
        if (UserRol == 'cxp1@logistikgo' || UserRol == 'jfraga@logistikgo')
          return (full[10] == 'pendiente'.toUpperCase() && +full[16] != totalSistema.toFixed(2) && +full[16]!=0 ? '<a href="#ModalReajusteCXP" title="Editar" class="btnEditarFactura btn btn-dark btn-elevate btn-pill btn-sm" data-toggle="modal" data-backdrop="static" data-keyboard="false" data-idfact="'+idfac+'"><i class="far fa-edit"></i></a>': '');
        else
          return '';
     }
    },
    {
      "width": "3%",
      "className": "text-center",
      "targets": 14,
      "mRender": function (data, type, full) {
       var totalSistema = +full[7].replace(/(\$)|(,)/g,'');
       return ( full[10] == 'pendiente'.toUpperCase() && isAuth == 'False' && (+full[16] == totalSistema.toFixed(2)) ? '<button type ="button" title="Aprobar" name="aprobarFactura" class="btnAprobarFactura btn btn-success btn-elevate btn-pill btn-sm" data-idfact="'+idfac+'"><i class="flaticon2-checkmark"></i></button>': full[10] == 'pendiente'.toUpperCase() && isAuth == 'False' && +full[16]==0 ? '<button type ="button" title="Aprobar" name="aprobarFactura" class="btnAprobarFactura btn btn-success btn-elevate btn-pill btn-sm" data-idfact="'+idfac+'"><i class="flaticon2-checkmark"></i></button>':'<button type ="button" title="Aprobar" name="aprobarFactura" class="btnAprobarFactura btn btn-success btn-elevate btn-pill btn-sm" data-idfact="'+idfac+'" style="display:none"><i class="flaticon2-checkmark"></i></button>');
     }
    },
    {
      "width": "3%",
      "className": "text-center",
      "targets": 15,
      "mRender": function (data, type, full) {
          return ( full[10] === 'pendiente'.toUpperCase() ? '<button type ="button" class="btnEliminarFactura btn btn-danger btn-elevate btn-pill btn-sm" data-idfact="'+idfac+'" title="Eliminar"><i class="flaticon-delete"></i></button>':'');
      }
    },
    {
      "targets":16,
      "visible": false
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
    IDProveedor: proveedor,
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
  }).then(function(response, data){

    if(response.status == 200)
    {
      Swal.fire({
        type: 'success',
        title: 'La factura ha sido validada correctamente',
        showConfirmButton: true,
        timer: 2500
      })
      var trBtnAprovar= $(btn).closest('tr');
      var findInput = $(trBtnAprovar).find('input[name="checkEC"]')[0];
      $(findInput).css('display', 'block');
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
    console.log(ex);
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
    TipoCambio: $('#TipoCambioPago').val()
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
  }).then(function(response, data){

    if(response.status == 200)
    {
      Swal.fire({
        type: 'success',
        title: 'El pago fue guardado correctamente',
        showConfirmButton: true,
        //timer: 3500
      })
      //alertToastSuccess(data);
      arrSelect = [];
      proveedor = '';
      $('#modalSubirPagos').modal('hide');

      var table = $('#TableEstadosdeCuenta').DataTable();
      $("input[name=checkEC]:checked").each(function () {
        table.row($(this).parents('tr')).remove().draw();
      });
      $('#btnSubirPagos').prop('disabled', true);
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

var fnCheckFolioEC = function () {
  WaitMe_ShowBtn('#btnSavePago');
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
      WaitMe_HideBtn('#btnSavePago');
    }
    else {
      $('#btnSavePago').attr('disabled',false);
      WaitMe_HideBtn('#btnSavePago');
    }
  }).catch(function(ex){
    console.log(ex);
  });
}

function EnviarCorreoProveedor() {
  jParams = {};
  fetch("/EstadosdeCuenta/EnviarCorreoProveedor", {
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
        title: 'Se ha enviado un correo al proveedor',
        showConfirmButton: false,
        timer: 2500
      })
    }
    else if(response.status == 500)
    {
      Swal.fire({
        type: 'error',
        title: 'No pudo enviarse correo al proveedor',
        showConfirmButton: false,
        timer: 2500
      })
    }
  }).catch(function(ex){
    console.log("no success!");
  });
}

var fnGetDetallePago = function () {
  var IDFactura = $(this).parents('tr').data('idfactura');
  WaitMe_Show('#divTableDetallesPago');

  fetch("/EstadosdeCuenta/GetDetallesPago?IDFactura=" + IDFactura, {
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

function cleanModalReajuste()
{
  $('#CostoReajuste').val("");
  $('#costoAccesoriosReajuste').val("")
  $('#costoRepartosReajuste').val("")
  $('#subtotalReajuste').val("");
  $('#IVAReajuste').val("");
  $('#RetencionReajuste').val("");
  $('#TotalReajuste').val("");
  diferenciaReajuste = 0;
  $('#TotalReajuste').prop('disabled', false);
  $('#CostoRecoleccionReajuste').prop('disabled', false);
  $('#btnSaveRepartosReajuste').prop('disabled', true);
  $("#TotalReajuste").prop('disabled', false);
}

function cleanModalAccesorios()
{
  $('.listaAccesorios div').remove();
  $("#btnSaveAccesoriosReajuste").prop('disabled', true);
}

function formatoTableRepartos()
{
  var t = $('#tableRepartos').DataTable( {
    "paging": false,
    "columnDefs": [ {
        "searchable": false,
        "orderable": false,
        "targets": 0
    } ],
} );

t.on( 'order.dt search.dt', function () {
    t.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
        cell.innerHTML = i+1;
    } );
} ).draw();
}


function recalculoReajuste(retencionAccesorios)
{
  WaitMe_Show('#modalWaitReajuste');
  //diferenciaReajuste = 0;
  var costoViaje = 0;
  typeProyecto == 'BKG' && +$('#CostoReajuste').val() == 0 ? costoViaje = +$('#CostoRecoleccionReajuste').val() : costoViaje = +$('#CostoReajuste').val();
  var recalculoSubtotal = costoViaje+(+$('#costoAccesoriosReajuste').val())+(+$('#costoRepartosReajuste').val());
  var recalculoIVA = recalculoSubtotal * ivaProcentaje;
  var recalculoRetencion = ((tipoViaje != 'CUSTODIA' ? (costoViaje * retencionProcentaje) : 0) + retencionAccesorios) + ((+$('#costoRepartosReajuste').val())* retencionProcentaje);
  var recalculoTotal = ((Number(recalculoSubtotal.toFixed(2)) + Number(recalculoIVA.toFixed(2))) - recalculoRetencion.toFixed(2));

  $('#subtotalReajuste').val(recalculoSubtotal.toFixed(2));
  $('#IVAReajuste').val(recalculoIVA.toFixed(2));
  $('#RetencionReajuste').val(recalculoRetencion.toFixed(2));
  $('#TotalReajuste').val(recalculoTotal.toFixed(2));
  +$('#TotalProveedor').val() == +$('#TotalReajuste').val() ? ($('#TotalProveedor').css('background-color', '#09DD08'), $('#btnSaveReajuste').prop('disabled', false)) : ($('#TotalProveedor').css('background-color', '#F91919'), $('#btnSaveReajuste').prop('disabled', true));
  $("#TotalReajuste").prop('disabled', true);
  WaitMe_Hide('#modalWaitReajuste');
}

function getAccesorios()
{
  fetch(`/EstadosdeCuenta/GetAccesoriosxViaje?IDViaje=${idViajeProyecto}&Proyecto=${typeProyecto}`, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    WaitMe_Show('#modalWaitReajuste');
    if (response.status == 200)
    {
      return response.clone().json();
    }
    else if (response.status == 500)
    {
      Swal.fire({
        type: 'error',
        title: 'Algo salio mal, por favor intentalo de nuevo',
        showConfirmButton: false,
        timer: 2500
      })
      $('#btnSaveReajuste').prop('disabled', true)
      WaitMe_Hide('#modalWaitReajuste');
    }
  }).then(function(data){
    if (typeProyecto == 'BKG')
    {
      var accesorioRetencionCosto = 0;
      for (var i = 0; i<data.NewData.length; i++)
      {
        data.NewData[i].IsAplicaRetencion ? accesorioRetencionCosto+= (+data.NewData[i].CostoAccesorio*retencionProcentaje) : "";
      }
      recalculoReajuste(accesorioRetencionCosto);
    }
    else if (typeProyecto == 'XD') {
      var accesorioRetencionCosto = 0;
      var dataJsonAccesorios = jsonAccesoriosXD();
      for (var i=0; i < dataJsonAccesorios.length; i++)
        {
          for (var j = 0; j<data.NewData.length; j++)
          {
            dataJsonAccesorios[i].descripcion == data.NewData[j].NombreAccesorio && dataJsonAccesorios[i].IsAplicaRetencion ? accesorioRetencionCosto += (+data.NewData[j].CostoAccesorio*retencionProcentaje) : "";
          }
        }
        recalculoReajuste(accesorioRetencionCosto);
    }
    WaitMe_Hide('#modalWaitReajuste');
  }).catch(function(ex){
    console.log(ex)
  });
}
