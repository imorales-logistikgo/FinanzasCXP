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
       $(`#${data.Folios[i].Delivery}`).append(`<a class="uppy-DashboardItem-previewLink" target="_blank" rel="noreferrer noopener"></a>`)
      uploadEvidences(`#uploadEvidencesProveedor${data.Folios[i].Delivery}`, `${data.Folios[i].Delivery}`);
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
