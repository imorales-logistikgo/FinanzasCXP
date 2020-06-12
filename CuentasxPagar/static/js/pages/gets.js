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
  fetch(`/EvidenciasProveedor/FindFolioProveedor?Folio=${Folio}`, {
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
      });
      $('#inputBuscarViajeProveedor').addClass("border border-danger");
      $('#inputBuscarViajeProveedor').focus();
      WaitMe_Hide('#TbPading');
    }
    else {
      $('#StatusEvidencias').append(`Estatus: <strong>Pendiente</strong> <i class="fa fa-clock fa-1x"></i>`)
      for(var i=0; i<data.Folios.length; i++)
      {
        if (data.Folios[i].Estatus == 'Pendiente' || data.Folios[i].Estatus == 'Rechazado') {
          $('#allEvidences').append(`<div class="col-sm-4 col-lg-4 col-md-4">
                              	<div class="kt-portlet kt-portlet--height-fluid">
                              		<div class="kt-portlet__head" id="headUppyTitulo">
                              			<div class="kt-portlet__head-label">
                              				<h3 class="kt-portlet__head-title" id='${data.Folios[i].Delivery}'>
                              					${data.Folios[i].Delivery}
                              				</h3>
                              			</div>
                              		</div>
                              			<div class="kt-portlet__body">
                              				<div class="row" id="prueba">
                              				</div>
                              				<div class="kt-uppy verificar" id="uploadEvidencesProveedor${data.Folios[i].Delivery}">
                              					<div  class="kt-uppy__dashboard"></div>
                              					<div class="kt-uppy__progress"></div>
                              				</div>
                                      <input type="text" id="ComentarioEvidencia" class="form-control" placeholder="Comentario">
                              			</div>
                              	</div>
                              </div>`);

          $(`#${data.Folios[i].Delivery}`).data('idpedido', data.Folios[i].XD_IDPedido)
          $(`#${data.Folios[i].Delivery}`).data('idviaje', data.Folios[i].IDViaje)
          uploadEvidences(`#uploadEvidencesProveedor${data.Folios[i].Delivery}`, `${data.Folios[i].Delivery}`);
        }
        else{
          $('#allEvidences').append(`
            <div class="alert alert-warning alert-dismissible fade show" role="alert">
              <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
              <strong>La evidencia ah sido enviada.</strong>
            </div>
            `)
        }
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


var GetEvidenciaMesaControl = function(IDViaje){
  WaitMe_Show('#TbPading');
  fetch(`/EvidenciasProveedor/GetEvidenciasMesaControl?XD_IDViaje=${IDViaje}`, {
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
                <div class="card-header">${data.Evidencias[i].Delivery}</div>
                <div class="card-body">
                  <a href="${data.Evidencias[i].URLEvidencia}" target="_blank"><embed src='${data.Evidencias[i].URLEvidencia}' height="150px" width="220px"></a>
                </div>
                <div class="card-footer">
                <button class="btn btn-outline-success btn-elevate btn-circle btn-icon AprobarEvidencia" title="Aprobar" data-idevidenciaaprobar="${data.Evidencias[i].IDEvidencia}" data-tipoevidencia="${data.Evidencias[i].TipoEvidencia}" ><i class="fa fa-check"></i></button>
                <button class="btn btn-outline-danger btn-elevate btn-circle btn-icon RechazarEvidencia" title="Rechazar" data-tipoevidencia="${data.Evidencias[i].TipoEvidencia}" data-idevidenciarechazar="${data.Evidencias[i].IDEvidencia}"><i class="flaticon-cancel"></i></button>
                </div>
                <input type="text" placeholder="Comentario" class="form-control" id="ComentarioEvidencia">
              </div>
            </div>
          `)
      }
      WaitMe_Hide('#TbPading');
    }
  }).catch(function(ex){
    console.log(ex);
    WaitMe_Hide('#TbPading');
  });
}

var GetEvidenciasFisicas = function(IDViaje){
  WaitMe_Show('#TbPading');
  fetch(`/EvidenciasProveedor/GetEvidenciaFisica?XD_IDViaje=${IDViaje}`, {
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
        title: 'El folio aun no tiene todas las evidencias digitales',
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
                  <button type="button" name="button" class="btn btn-outline-danger btn-elevate btn-circle btn-icon" id="btnAprobarEVFisica" data-idviaje="${data.EvidenciaFisica[i].XD_IDViaje}" data-idpedido="${data.EvidenciaFisica[i].XD_IDPedido}"><i class="fa fa-check"></i></button>
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
