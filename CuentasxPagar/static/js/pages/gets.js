function Getdatos(t){
  //var arrSelect=[];
  // $("input[name=checkEC]:checked").each(function () {
  //   var datosRow = table.row($(this).parents('tr')).data();
  //   var prueba = $(this).data("idfactu");
  //   arrSelect.push([datosRow[1],datosRow[7], datosRow[8], datosRow[9], datosRow[7], prueba, datosRow[2]]);
  // });
  var datosRow = table.row($(t).parents('tr')).data();
  var prueba = $(t).data("idfactu");
  arrSelect.push([datosRow[1],datosRow[7], datosRow[8], datosRow[9], datosRow[7], prueba, datosRow[2]]);
  return arrSelect;
}

function removeItemFromArr (arr, item) {
  var newArr=[];
  for(var i=0;i<arr.length;i++){
      var jsonItem = JSON.stringify(arr[i]) == JSON.stringify(item[0]);
      jsonItem ? console.log("eliminado") : newArr.push(arr[i]);
  }
  arrSelect = newArr;
}

//OBTENER EL FOLIO PARA SUBIR LAS EVIDENCIAS A XD DESDE EL USUARIO DEL PROVEEDOR
var GetFolioEvidencias = function(Folio){
  WaitMe_Show('#TbPading');
  fetch(`/EvidenciasProveedor/FindFolioProveedorE?Folio=${Folio}`, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    return response.clone().json();
  }).then(function(data){
    if(!data.Found || data.Folios.length == 0) {
      Swal.fire({
        type: 'error',
        title: 'El folio indicado no existe en el sistema',
        showConfirmButton: false,
        timer: 2500
      });
      $('#inputBuscarViajeProveedor').addClass("border border-danger");
      $('#inputBuscarViajeProveedor').focus();
      WaitMe_Hide('#TbPading');
    }
    else {
      var arrStatus = [];
      // $('#StatusEvidencias').append(`Estatus: <strong>Pendiente</strong> <i class="fa fa-clock fa-1x"></i>`)
      for(var i=0; i<data.Folios.length; i++)
      {
          $('#allEvidences').append(`<div class="col-sm-4 col-lg-4 col-md-4">
                              	<div class="kt-portlet kt-portlet--height-fluid">
                                <h5>Estatus: <strong>${data.Folios[i].Status}</strong></h5>
                              		<div class="kt-portlet__head" id="headUppyTitulo">
                              			<div class="kt-portlet__head-label">
                              				<h3 class="kt-portlet__head-title" id='${data.Folios[i].Delivery.replace(/ /g, "")}' data-status="${data.Folios[i].Status}" data-evidencia="${data.Folios[i].TipoEvidencia}">
                              					${data.Folios[i].Delivery.replace(/ /g, "")}
                              				</h3>
                              			</div>
                              		</div>
                              			<div class="kt-portlet__body">
                              				<div class="row" id="prueba">
                              				</div>
                              				<div class="kt-uppy verificar" id="uploadEvidencesProveedor${data.Folios[i].Delivery.replace(/ /g, "")}">
                              					<div  class="kt-uppy__dashboard"></div>
                              					<div class="kt-uppy__progress"></div>
                              				</div>
                                      <input type="text" id="ComentarioEvidencia" class="form-control" placeholder="Comentario" disabled value="${data.Folios[i].ComentarioRechazo}">
                              			</div>
                              	</div>
                              </div>`);

          $(`#${data.Folios[i].Delivery.replace(/ /g, "")}`).data('idpedido', data.Folios[i].XD_IDPedido)
          $(`#${data.Folios[i].Delivery.replace(/ /g, "")}`).data('idviaje', data.Folios[i].IDViaje)
          $(`#${data.Folios[i].Delivery.replace(/ /g, "")}`).data('tipoevidencia', data.Folios[i].TipoEvidencia)
          $('#BtnHojaLiberacion').data('IDViajeHL', data.Folios[i].IDViaje)
          $('#BtnHojaLiberacion').data('TipoEvidenciaHL', data.Folios[i].TipoEvidencia)
          data.Folios[i].Status == 'Pendiente' || data.Folios[i].Status == 'Rechazada' ? uploadEvidences(`#uploadEvidencesProveedor${data.Folios[i].Delivery.replace(/ /g, "")}`, `${data.Folios[i].Delivery.replace(/ /g, "")}`) : ($(`#uploadEvidencesProveedor${data.Folios[i].Delivery.replace(/ /g, "")}`).append(`<div class="row">
            <div class="col-md-4" ><img src="/static/img/pdf-2.png" height="150px" width="150px" style="position:relative; left:70px; bottom:20px"></div>
          </div>`)/*, $('#btnGuardarEvidenciasP').prop('disabled', true), $('#HojaLiberacion').html('<strong>Hoja de liberacion lista para descargar</strong>')*/);
          arrStatus.push(data.Folios[i].Status)
      }
//      console.log(arrStatus.includes('Rechazada'))
      if(arrStatus.includes('Pendiente') || arrStatus.includes('Rechazada') || arrStatus.includes('Otro') || arrStatus.includes('Enviada')){
        $('.BtnHojaLiberacion').css('display', 'none');
        arrStatus.includes('Pendiente') || arrStatus.includes('Rechazada') ? "": $('#btnGuardarEvidenciasP').prop('disabled', true);
      }
      else{
        $('.BtnHojaLiberacion').css('display', 'block');
        $('#BtnHojaLiberacion').removeClass('btn-danger');
        $('#BtnHojaLiberacion').addClass('btn-success');
        $('#btnGuardarEvidenciasP').prop('disabled', true);
        // $('#HojaLiberacion').html('<strong>Hoja de liberacion lista para descargar</strong>')
      }


      $('#FolioProveedorEvidencia').text(data.Folios.Delivery);
      $('#uploadEvidenciasModal').css('display', 'block');
      $('#inputBuscarViajeProveedor').removeClass("border border-danger");
      $('#inputBuscarViajeProveedor').addClass("border border-success");
      $('#inputBuscarViajeProveedor,#buscarViajeProveedor').prop('disabled', true);
      WaitMe_Hide('#TbPading');
    }
  }).catch(function(ex){
    console.log(ex);
    WaitMe_Hide('#TbPading');
  });
}


var GetUUID = function(xml){
    try{
        const proxyURL = "https://cors-anywhere.herokuapp.com/";
        var newXML = proxyURL + xml;
        var newUUID;
        var req = new XMLHttpRequest();
           req.open('GET', newXML, false);
           req.send(null);
           if (req.status == 200)
           {
               var resp = req.responseXML;
               var obNodosUI = resp.getElementsByTagName("cfdi:Complemento")[0];
               var timbreFiscal = obNodosUI.getElementsByTagName('tfd:TimbreFiscalDigital')[0]
               newUUID = timbreFiscal.getAttribute('UUID');
           }
           else
           {
               newUUID = '';
           }
        return newUUID;
    }
    catch(error){
      alertToastError('Ocurrio un error al obtener el UUID');
      console.error(error);
      newUUID = '';
    }
}


var GetEvidenciaMesaControl = function(IDViaje,Folio){
  WaitMe_Show('#TbPading');
  fetch(`/EvidenciasProveedor/GetEvidenciasMesaControl?XD_IDViaje=${IDViaje}&Folio=${Folio}`, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    if(response.status == 200){
      return response.clone().json();
    }
    else if(response.status == 500){
      Swal.fire({
        type: 'error',
        title: 'Ocurrio un error al obtener las evidencias',
        showConfirmButton: false,
        timer: 2500
      });
    }
  }).then(function(data){
    if(data.Evidencias.length == 0) {
      Swal.fire({
        type: 'error',
        title: 'El Folio aun no tiene evidencias',
        showConfirmButton: false,
        timer: 2500
      });
      WaitMe_Hide('#TbPading');
    }
    else {
      $('#ModalValidarEvidencias').modal({backdrop: 'static', keyboard: false, show: true});
      for(var i=0; i<data.Evidencias.length; i++)
      {
        $('#VerEvidencia').append(`
            <div class="col-md-4">
              <div class="card bg-light mb-3" style="max-width: 25rem;">
                <div class="card-header" id="${data.Evidencias[i].Delivery}">${data.Evidencias[i].Delivery}</div>
                <div class="card-body">
                  <a href="${data.Evidencias[i].URLEvidencia}" target="_blank"><img src='/static/img/pdf-2.png' height="150px" width="200px"></img></a>
                </div>
                <div class="card-footer">
                <button class="btn btn-outline-success btn-elevate btn-circle btn-icon AprobarEvidencia" title="Aprobar" data-idviaje="${data.Evidencias[i].XD_IDViaje}" data-idevidenciaaprobar="${data.Evidencias[i].IDEvidencia}" data-tipoevidencia="${data.Evidencias[i].TipoEvidencia}" ><i class="fa fa-check"></i></button>
                <button class="btn btn-outline-danger btn-elevate btn-circle btn-icon RechazarEvidencia" title="Rechazar" data-idviaje="${data.Evidencias[i].XD_IDViaje}" data-tipoevidencia="${data.Evidencias[i].TipoEvidencia}" data-idevidenciarechazar="${data.Evidencias[i].IDEvidencia}"><i class="flaticon-cancel"></i></button>
                </div>
                <input type="text" placeholder="Comentario" class="form-control" id="ComentarioEvidencia">
              </div>
            </div>
          `)

          $(`#${data.Evidencias[i].Delivery}`).append(`<a href="${data.Evidencias[i].URLEvidencia}" target="_blank"><i class="fa fa-eye"></i></a>`);
      }
      WaitMe_Hide('#TbPading');
    }
  }).catch(function(ex){
    console.log(ex);
    WaitMe_Hide('#TbPading');
  });
}

var GetEvidenciasFisicas = function(IDViaje, Folio){
  WaitMe_Show('#TbPading');
  fetch(`/EvidenciasProveedor/GetEvidenciaFisica?XD_IDViaje=${IDViaje}&Folio=${Folio}`, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    if(response.status == 200){
      return response.clone().json();
    }
    else if(response.status == 500){
      Swal.fire({
        type: 'error',
        title: 'Ocurrio un error al obtener las evidencias',
        showConfirmButton: false,
        timer: 2500
      });
    }
  }).then(function(data){
    if(data.EvidenciaFisica.length == 0) {
      Swal.fire({
        type: 'error',
        title: 'El folio aun no tiene todas las evidencias digitales o las evidencia ya fueron aprobadas',
        showConfirmButton: false,
        timer: 2500
      });
      WaitMe_Hide('#TbPading');
    }
    else {
      $('#ModalValidarEvidenciasFisicas').modal({backdrop: 'static', keyboard: false, show: true});
      for(var i=0; i<data.EvidenciaFisica.length; i++)
      {
        $('#listaEvidenciasFisicas').append(`
            <li class="kt-nav__item kt-nav__item--active">
              <h3 class="kt-nav__link">
                <i class="kt-nav__link-icon flaticon2-rocket-2"></i>
                <span class="kt-nav__link-text">${data.EvidenciaFisica[i].Delivery}</span>
                <span class="kt-nav__link-badge">
                  <button type="button" name="button" class="btn btn-outline-danger btn-elevate btn-circle btn-icon" id="btnAprobarEVFisica" data-idviaje="${data.EvidenciaFisica[i].XD_IDViaje}" data-idpedido="${data.EvidenciaFisica[i].XD_IDPedido}" data-tipoevidenciafisica="${data.EvidenciaFisica[i].Delivery}"><i class="fa fa-check"></i></button>
                </span>
              </h3>
            </li>
          `)
      }
      WaitMe_Hide('#TbPading');
    }
  }).catch(function(ex){
    console.log(ex);
    WaitMe_Hide('#TbPading');
  });
}



var GetIsEvidenciaDigitalCompleta = function(IDViaje, TipoEv){
  var url;
  TipoEv == 'BKG' ? url = `/EvidenciasProveedor/EvidenciaDigitalCompletaBKG?`: url = `/EvidenciasProveedor/EvidenciaDigitalCompleta?`;
  fetch(`${url}IDViaje=${IDViaje}`,{
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    if(response.status == 200){
      return response.clone().json();
    }
    else if(response.status == 500){
      Swal.fire({
        type: 'error',
        title: 'Ocurrio un error prueba',
        showConfirmButton: false,
        timer: 2500
      });
    }
  }).then(function(data){
    if(data.IsEvidenciaDigitalCompleta){
       $(btn).removeClass('btn-primary');
       $(btn).addClass('btn-success');
       var changeIcon = $(btn).find('i')[0];
       $(changeIcon).removeClass('fa-clock');
       $(changeIcon).addClass('fa-check')
       $(btn).prop('disabled', true);
    }
  }).catch(function(ex){
    console.log(ex);
  });
}

var GetHojaLiberacion = function(IDViaje, Proyecto){
  fetch(`/EvidenciasProveedor/DescargarHojaLiberacion?IDViaje=${IDViaje}&Proyecto=${Proyecto}`, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    if(response.status == 200){
      return response.clone().json();
    }
    else if(response.status == 500){
      Swal.fire({
        type: 'error',
        title: 'Ocurrio un error obteniendo la hoja de liberacion',
        showConfirmButton: false,
        timer: 2500
      });
      WaitMe_HideBtn('#BtnHojaLiberacion')
    }
    else if(response.status == 400){
      Swal.fire({
        type: 'error',
        title: 'Las evidencias fisicas aún no estan validadas',
        showConfirmButton: false,
        timer: 3500
      });
      WaitMe_HideBtn('#BtnHojaLiberacion')
    }
  }).then(function(data){
    if(data.HojaLiberacion == null){
      Swal.fire({
        type: 'error',
        title: 'Hoja de liberacion no disponible',
        showConfirmButton: false,
        timer: 2500
      });
      WaitMe_HideBtn('#BtnHojaLiberacion')
    }
    else if(!data.HojaLiberacion){
      Swal.fire({
      type: 'error',
      title: 'Solo se puede descargar la hoja de liberacion 1 vez',
      showConfirmButton: false,
      timer: 2500
    });
    WaitMe_HideBtn('#BtnHojaLiberacion')
    }
    else{
      $('#BtnHojaLiberacion').attr('href', data.HojaLiberacion);
      window.open(data.HojaLiberacion, '_blank');
      $('#BtnHojaLiberacion').removeAttr('href');
      WaitMe_HideBtn('#BtnHojaLiberacion')
    }
  }).catch(function(ex){
    console.log(ex);
  });
}

async function GetIdDocumentoAndImpPagado (xml){
  try{
      const proxyURL = "https://cors-anywhere.herokuapp.com/";
      var newXML = proxyURL + xml;
      var arrDataXML = [];
      var req = new XMLHttpRequest();
         req.open('GET', newXML, false);
         req.send(null);
         if (req.status == 200){
             var resp = req.responseXML;
             var obNodosUI = resp.getElementsByTagName("cfdi:Complemento")[0];
             var TimbreFiscal = obNodosUI.getElementsByTagName('pago10:Pago')[0]
             var each = TimbreFiscal.getElementsByTagName('pago10:DoctoRelacionado')
             for (var i=0; i<each.length; i++){
               var idDocumento = each[i].getAttribute('IdDocumento')
               var ImpPagado = each[i].getAttribute('ImpPagado')
               arrDataXML.push({"IdDocumento":idDocumento.toUpperCase(), "ImpPagado":ImpPagado})
             }
          }
      const a = await GetFacturasxPago(idPag,arrDataXML);
      // return arrDataXML;

        /*$.ajax({
        url: `/ReportePagos/GetUUIDEachFactura?XML=${xml}`,
        type: 'GET',
        async:false,
        contentType: "application/json; charset=utf-8",
        // beforeSend: fnBeforeSend,
        success: function(data){
            GetFacturasxPago(idPag,data.arrDataXML)
        },
        error: function(request, status, error){
          alertToastError("Ocurrio un problema al leer el xml");
          console.log(error);
        }
    });*/
  }
  catch(error){
    alertToastError('Ocurrio un error al leer el archivo xml');
    console.error(error);
  }
}

var GetFacturasxPago =  function(Pago, arrXML){
  $.ajax({
        url: `/ReportePagos/GetFacturasxPago?IDPago=${Pago}`,
        type: 'GET',
        async:false,
        contentType: "application/json; charset=utf-8",
        // beforeSend: fnBeforeSend,
        success: function(data){
              var Comprobacion = [];
              loop1:
               for (var i=0;i<data.DataBD.length;i++){
                var indicador = false
                loop2:
                  for (var j=0; j<arrXML.length;j++){
                    if (data.DataBD[i].IdDocumento.toUpperCase().trim() == arrXML[j].IdDocumento.toUpperCase().trim() && parseFloat(data.DataBD[i].ImpPagado).toFixed(2) == parseFloat(arrXML[j].ImpPagado).toFixed(2)){
                      indicador = true
                      break loop2;
                    }
                  }
                  Comprobacion.push(indicador)
                }
              valComp = Comprobacion.includes(false);
        },
        error: function(request, status, error){
          alertToastError("Ocurrio un problema");
          console.log(error);
        }
    });
 }


var GetFechaPagoAndTipoComplemento = function(xml){
  try{
      const proxyURL = "https://cors-anywhere.herokuapp.com/";
      var newXML = proxyURL + xml;
      var arrDataXML = [];
      var req = new XMLHttpRequest();
         req.open('GET', newXML, false);
         req.send(null);
         if (req.status == 200){
             var resp = req.responseXML;
             var obNodos = resp.getElementsByTagName("cfdi:Complemento")
             var etiquetaFecha = obNodos[0].getElementsByTagName("pago10:Pagos")
             var etiquetafecha2 = etiquetaFecha[0].getElementsByTagName("pago10:Pago")
             var atributoFechaPago = etiquetafecha2[0].getAttribute('FechaPago')
             var findTipoComprobante = resp.getElementsByTagName("cfdi:Comprobante")
             var TipoCom= findTipoComprobante[0].getAttribute('TipoDeComprobante')
             var ValidacionFechaAndComp = GetFechaPago(atributoFechaPago,TipoCom)
          }
  }
  catch(error){
    alertToastError('Ocurrio un error al leer el archivo xml');
    console.error(error);
  }
}

var GetFechaPago = function(Fecha,TipoComp){
  $.ajax({
        url: `/ReportePagos/GetFechaPago?IDPago=${idPag}&FechaXML=${Fecha}&TComplemento=${TipoComp}`,
        type: 'GET',
        async:false,
        contentType: "application/json; charset=utf-8",
        success: function(data){
          FP = data.Fecha
        },
        error: function(request, status, error){
          alertToastError("Ocurrio un problema");
          console.log(error);
        }
    });
}


var GetValidacionCFDIAndOther = function(XML){
  $.ajax({
        url: `/PendientesEnviar/GetValidacionesCFDIAndOther?XML=${XML}`,
        type: 'GET',
        async:false,
        contentType: "application/json; charset=utf-8",
        success: function(data){
          valCFDIAndOther = data.Response;
        },
        error: function(request, status, error){
          alertToastError("Ocurrio un error al leer el archivo xml");
          valCFDIAndOthe = false
          console.log(error);
        }
    });
}

var GetFolioViajeXML = function(XML,Folio, id){
  $.ajax({
        url: `/PendientesEnviar/GetFolioViajeXML?XML=${XML}&Folio=${Folio}`,
        type: 'GET',
        async:false,
        contentType: "application/json; charset=utf-8",
        success: function(data){
          FViaje = data.Folio;
        },
        error: function(request, status, error){
          alertToastError("Ocurrio un error al leer el archivo xml");
          console.log(error);
        }
    });
}


var GetMontoPago = function(XML, IDPago){
  $.ajax({
        url: `/ReportePagos/GetMontoPagoXML?XML=${XML}&IDPago=${IDPago}`,
        type: 'GET',
        async:false,
        contentType: "application/json; charset=utf-8",
        success: function(data){
          ValidarMontoXML = data.Response;
        },
        error: function(request, status, error){
          alertToastError("Ocurrio un error al leer el archivo xml");
          ValidarMontoXML = false
          console.log(error);
        }
  });
}

var GetEvidenciasForCXP = function(IDViaje, Folio){
    WaitMe_Show('#TbPadingCXP');
  fetch(`/EvidenciasProveedor/GetEvidenciasCXP?XD_IDViaje=${IDViaje}&Folio=${Folio}`, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    if(response.status == 200){
      return response.clone().json();
    }
    else if(response.status == 500){
      Swal.fire({
        type: 'error',
        title: 'Ocurrio un error al obtener las evidencias',
        showConfirmButton: false,
        timer: 2500
      });
    }
  }).then(function(data){
    if(data.Evidencias.length == 0) {
      Swal.fire({
        type: 'error',
        title: 'El Folio aun no tiene evidencias',
        showConfirmButton: false,
        timer: 2500
      });
      WaitMe_Hide('#TbPadingCXP');
    }
    else {
      $('#ModalEvidenciasCXP').modal({backdrop: 'static', keyboard: false, show: true});
      for(var i=0; i<data.Evidencias.length; i++)
      {
        $('#VerEvidenciaCXP').append(`
            <div class="col-md-4">
              <div class="card bg-light mb-3" style="max-width: 25rem;">
                <div class="card-header" >${data.Evidencias[i].Titulo}</div>
                <div class="card-body">
                  <a href="${data.Evidencias[i].RutaArchivo}" target="_blank"><img src='/static/img/pdf-2.png' height="150px" width="160px"></img></a>
                </div>
              </div>
            </div>
          `)

          $(`#${data.Evidencias[i].Titulo}`).append(`<a href="${data.Evidencias[i].RutaArchivo}" target="_blank"><i class="fa fa-eye"></i></a>`);
      }
      WaitMe_Hide('#TbPadingCXP');
    }
  }).catch(function(ex){
    console.log(ex);
    WaitMe_Hide('#TbPadingCXP');
  });
}

var GetEvidenciaMC = function(IDViaje)
{
    WaitMe_Show('#TbPadingMC');
  fetch(`/EvidenciasProveedor/GetEvidenciasMC?IDViaje=${IDViaje}`, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    if(response.status == 200){
      return response.clone().json();
    }
    else if(response.status == 500){
      Swal.fire({
        type: 'error',
        title: 'Ocurrio un error al obtener las evidencias',
        showConfirmButton: false,
        timer: 2500
      });
      WaitMe_HideBtn("#TbPading")
    }
    else if(response.status == 400){
    Swal.fire({
        type: 'error',
        title: 'Ya cuenta con esta evidencia',
        showConfirmButton: false,
        timer: 2500
    });
    WaitMe_Hide("#TbPading")
    }
  }).then(function(data){
    if(data.Evidencias.length == 0) {
      Swal.fire({
        type: 'error',
        title: 'No se pudo obtener la evidencia',
        showConfirmButton: false,
        timer: 2500
      });
      WaitMe_Hide('#TbPadingMC');
    }
    else {
      $('#ModalEvidenciasMC').modal({backdrop: 'static', keyboard: false, show: true});
      WaitMe_Hide("#TbPading")
      for(var i=0; i<data.Evidencias.length; i++)
      {
        $('#SubirEvidenciaMC').append(`<div class="col-sm-5 col-lg-5 col-md-5">
                              	<div class="kt-portlet kt-portlet--height-fluid">
                                <h5>Estatus: <strong>${data.Evidencias[i].Status}</strong></h5>
                              		<div class="kt-portlet__head" id="headUppyTitulo">
                              			<div class="kt-portlet__head-label">
                              				<h3 class="kt-portlet__head-title" id='${data.Evidencias[i].Delivery.replace(/ /g, "")}' data-status="${data.Evidencias[i].Status}" data-evidencia="${data.Evidencias[i].TipoEvidencia}">
                              					${data.Evidencias[i].Delivery.replace(/ /g, "")}
                              				</h3>
                              			</div>
                              		</div>
                              			<div class="kt-portlet__body">
                              				<div class="row" id="prueba">
                              				</div>
                              				<div class="kt-uppy verificar" id="uploadEvidencesProveedor${data.Evidencias[i].Delivery.replace(/ /g, "")}">
                              					<div  class="kt-uppy__dashboard"></div>
                              					<div class="kt-uppy__progress"></div>
                              				</div>
                                      <input type="text" id="ComentarioEvidencia" class="form-control" placeholder="Comentario" disabled value="${data.Evidencias[i].ComentarioRechazo}">
                              			</div>
                              	</div>
                                </div>`);
          $(`#${data.Evidencias[i].Delivery.replace(/ /g, "")}`).data('idpedido', data.Evidencias[i].XD_IDPedido)
          $(`#${data.Evidencias[i].Delivery.replace(/ /g, "")}`).data('idviaje', data.Evidencias[i].IDViaje)
          $(`#${data.Evidencias[i].Delivery.replace(/ /g, "")}`).data('tipoevidencia', data.Evidencias[i].TipoEvidencia)
          data.Evidencias[i].Status == 'Pendiente' || data.Evidencias[i].Status == 'Rechazada' ? uploadEvidences(`#uploadEvidencesProveedor${data.Evidencias[i].Delivery.replace(/ /g, "")}`, `${data.Evidencias[i].Delivery.replace(/ /g, "")}`) : ($(`#uploadEvidencesProveedor${data.Evidencias[i].Delivery.replace(/ /g, "")}`).append(`<div class="row">
            <div class="col-md-4" ><img src="/static/img/pdf-2.png" height="150px" width="150px" style="position:relative; left:70px; bottom:20px"></div>
            </div>`))
      }
      WaitMe_Hide('#TbPadingMC');
    }
  }).catch(function(ex){
    console.log(ex);
    WaitMe_Hide('#TbPadingMC');
  });
}


var  GetReporteTotales = function(params){
  fetch(`/ReporteGeneralMC/ReporteByFilter?${params}`, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    return response.clone().json();
  }).then(function(data){
    $('#divTablaReproteGeneral').html(data.htmlRes);
    DataTableStyle();
//    $('#TableReporteGeneral').css("display", "block");
    WaitMe_Hide('#divTablaReproteGeneral');
  }).catch(function(ex){
    console.log(ex);
    WaitMe_Hide('#divTablaReproteGeneral');
    alertToastError("Ocurrio un error");
  });
}


var GetIsEvidenciaServiciosCompleta = function(IDViaje){
    fetch(`/EvidenciasProveedor/AllEvServiciosTrue?IDViaje=${IDViaje}`,{
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    if(response.status == 200){
      return response.clone().json();
    }
    else if(response.status == 500){
      Swal.fire({
        type: 'error',
        title: 'Ocurrio un error',
        showConfirmButton: false,
        timer: 2500
      });
    }
  }).then(function(data){
    if(data.data){
       $(btn).removeClass('btn-primary');
       $(btn).addClass('btn-success');
       var changeIcon = $(btn).find('i')[0];
       $(changeIcon).removeClass('fa-clock');
       $(changeIcon).addClass('fa-check')
       $(btn).prop('disabled', true);
    }
  }).catch(function(ex){
    console.log(ex);
  });
}