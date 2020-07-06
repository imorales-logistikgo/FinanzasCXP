
function ContadorCheck(input, btnSubir)
{
  var cont = 0;
  $(input).each(function (){
    if($(this).is(':checked'))
    {
      cont++;
    }
   });
   $(btnSubir).prop('disabled', !cont !=0);
return cont;
}

var validarMismoProveedor = function(validarIdProveedor_, check_){
	if (validarIdProveedor_ != proveedor) {
		$(check_).prop('checked', false);
		alertToastError("El proveedor debe ser el mismo");
	}
}
//var ContadorCheck = (btnSubir) => arrSelect.length >= 1 ? $(btnSubir).prop('disabled', false) : $(btnSubir).prop('disabled', true);

// plugin para subir los archivos de las facturas en Modal Pendientes de enviar
"use strict";

		// Class definition
		var KTUppyEvidencias = function () {
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
			var PluginEvicencias = function(idP, ver){
				//var id = '#kt_uppy_1';
        var id = idP;
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
           browserBackButtonClose: true
         }

         var uppyDashboard1 = Uppy.Core({
           autoProceed: false,
           restrictions: {
						maxFileSize: 4200000, // 5mb
						maxNumberOfFiles: 1,
						minNumberOfFiles: 1,
           allowedFileTypes:['.pdf', '.xml', 'image/*']
         },
         locale: Uppy.locales.es_ES,
         onBeforeFileAdded: (currentFile, file) => {
           console.log(Object.values(file));
          // console.log(currentFile.type)
          // console.log($('.uppy-DashboardContent-title').length)
           //if($('.uppy-DashboardContent-title').length == 0)
           if(Object.values(file)[0] === undefined)
           {
             console.log("+1")
           }
           else
           {
             if((currentFile.type === Object.values(file)[0].meta.type))
             {
               uppyDashboard1.info(`Los archivos deben ser diferentes`, 'error', 500)
               return false
             }
             else
             {
               console.log("ok")
             }
           }

             }
           });


         uppyDashboard1.use(Dashboard, options);
         uppyDashboard1.use(XHRUpload, { endpoint: 'https://api-bgk-debug.logistikgo.com/api/Viaje/SaveevidenciaTest', method: 'post'});
				//uppyDashboard.use(XHRUpload, { endpoint: 'http://localhost:63510/api/Viaje/SaveevidenciaTest', method: 'post'});
				uppyDashboard1.use(GoogleDrive, { target: Dashboard, companionUrl: 'https://companion.uppy.io' });
        uppyDashboard1.on('upload-success', (file, response) => {
          console.log(file)
          const fileName = file.name
          if (file.extension === 'pdf')
          {
           const urlPDF = response.body
           $(idP).data("rutaarchivoPDF", urlPDF)
           document.querySelector(ver).innerHTML +=
           `<ol><li id="listaArchivos"><a href="${urlPDF}" target="_blank" name="url" id="RutaPDF">${fileName}</a></li></ol>`
                 //  console.log($('#kt_uppy_1').data("rutaarchivoPDF"))
               }
               else if(file.extension === 'xml')
               {
                 const urlPDF = response.body
                 $(idP).data("rutaarchivoXML", urlPDF)
                 document.querySelector(ver).innerHTML +=
                 `<ol><li id="listaArchivos"><a href="${urlPDF}" target="_blank" name="url" id="RutaXML">${fileName}</a></li></ol>`
                   //console.log($('#kt_uppy_1').data("rutaarchivoXML"))
                 }
                 else
                 {
                   const urlPDF = response.body
                   $(idP).data("rutaarchivoIMG", urlPDF)
                   document.querySelector(ver).innerHTML +=
                   `<ol><li id="listaArchivos"><a href="${urlPDF}" target="_blank" name="url" id="RutaXML">${fileName}</a></li></ol>`
                 }
                 rutaComprobante = response.body
                 //const url = response.body
   // `<embed src="${url}">`
 });

      }
      return {
				// public functions
				init: function(id, ver) {
					PluginEvicencias(id, ver);
				}
			};
		}();




function leerxml(xml)
{
  try{
      const proxyURL = "https://cors-anywhere.herokuapp.com/";
      var newXML = proxyURL + xml;
      var rest;
      var req = new XMLHttpRequest();
         req.open('GET', newXML, false);
         req.send(null);
         console.log(req);
         if (req.status == 200)
         {
             var resp = req.responseXML;
             var obNodos = resp.children[0].attributes;
             var total = obNodos.Total;
             (total != undefined) ? rest = total.nodeValue : rest = null;
         }
         else
         {
             rest = null;
         }
      return rest;
  }
  catch(error){
    Swal.fire({
      type: 'error',
      title: 'Ocurrio un error al leer el XML',
      showConfirmButton: false,
      timer: 2500
    })
    console.error(error);
    return null;
  }
}

function WaitMe_Show(idForm) {
    $(idForm).waitMe({
        effect: 'ios',
        text: 'Por favor espera...',
        bg: 'rgb(255,255,255)',
        color: '#38227F',
        sizeW: '',
        sizeH: '',
        source: ''
    });
};

function WaitMe_Hide(idForm) {
        $(idForm).waitMe('hide');
};

function WaitMe_ShowBtn(idForm) {
    $(idForm).waitMe({
        effect: 'ios',
        //text: 'Por favor espera...',
        bg: 'rgb(255,255,255)',
        maxSize : 30,
        color: '#38227F',
        sizeW: '',
        sizeH: '',
        source: ''
    });
};

function WaitMe_HideBtn(idForm) {
        $(idForm).waitMe('hide');
};


function alertToastError(msj)
{
  toastr.options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": false,
    "progressBar": false,
    "positionClass": "toast-bottom-center",
    "preventDuplicates": false,
    "onclick": null,
    "showDuration": "200",
    "hideDuration": "1000",
    "timeOut": "6000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
  };

  toastr.error(msj);
}

function alertToastSuccess(msj)
{
  toastr.options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": false,
    "progressBar": false,
    "positionClass": "toast-top-right",
    "preventDuplicates": false,
    "onclick": null,
    "showDuration": "200",
    "hideDuration": "1000",
    "timeOut": "6000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
  };

  toastr.success(msj);
}

function truncarDecimales (x, posiciones = 0) {
  var s = x.toString()
    var l = s.length
    var decimalLength = s.indexOf('.') + 1
    if(decimalLength === 0)
    {
         var numStr = s
         return Number(numStr)
    }
  else
    {
        var numStr = s.slice(0, decimalLength + posiciones)
        return Number(numStr)
    }
}

function truncarDecimalesPE (x, posiciones = 0) {
  var s = x.toString()
    var l = s.length
    var decimalLength = s.indexOf('.') + 1
    if(decimalLength === 0)
    {
         var numStr = s
         return Number(numStr)
    }
  else
    {
        var numStr = s.slice(0, decimalLength + posiciones)
        return numStr;
    }
}


function fechaVencimineto(fecha)
{
  var newDate;
  var day = $(fecha).datepicker('getDate').getDate();
  var month = $(fecha).datepicker('getDate').getMonth() +1;
  var year = $(fecha).datepicker('getDate').getFullYear();
  if (month != 12)
  {
    var newMonth =  month + 1;
    newDate = year + "/" + newMonth + "/" + day;
  }
  else
  {
    var newMonth = 1;
    var newYear = year + 1;
    newDate = newYear + "/" + newMonth + "/" + day;
  }
  return newDate;
}

function leerXMLTransportista(xml)
{
  try{
      const proxyURL = "https://cors-anywhere.herokuapp.com/";
      var newXML = proxyURL + xml;
      var rest;
      var req = new XMLHttpRequest();
         req.open('GET', newXML, false);
         req.send(null);
         if (req.status == 200)
         {
             var resp = req.responseXML;
             var obNodos = resp.children[0].attributes;
             var total = obNodos.Total;
             (total != undefined) ? rest = total.nodeValue : rest = 0;
         }
         else
         {
             rest = 0;
         }
      return rest;
  }
  catch(error){
    Swal.fire({
      type: 'error',
      title: 'Ocurrio un error al leer el XML',
      showConfirmButton: false,
      timer: 2500
    })
    console.error(error);
  }
}

function jsonAccesoriosXD ()
{
  var allAccesorios = ﻿[
    {
      "descripcion": "Almacenaje",
      "costo": 0,
      "IsAplicaRetencion": false
    },
    {
      "descripcion": "Demora",
      "costo": 0,
      "IsAplicaRetencion": false
    },
    {
      "descripcion": "Estadias",
      "costo": 0,
      "IsAplicaRetencion": false
    },
    {
      "descripcion": "Maniobras de carga",
      "costo": 0,
      "IsAplicaRetencion": false
    },
    {
      "descripcion": "Maniobras de descarga",
      "costo": 0,
      "IsAplicaRetencion": false
    },
    {
      "descripcion": "Peaje",
      "costo": 0,
      "IsAplicaRetencion": false
    },
    {
      "descripcion": "Recarga de ajuste de gasolina",
      "costo": 0,
      "IsAplicaRetencion": true
    },
    {
      "descripcion": "Retraso",
      "costo": 0,
      "IsAplicaRetencion": false
    },
    {
      "descripcion": "Viaje Local",
      "costo": 0,
      "IsAplicaRetencion": true
    },
    {
      "descripcion": "Custodias",
      "costo": 0,
      "IsAplicaRetencion": false
    },
    {
      "descripcion": "Otro",
      "costo": 0,
      "IsAplicaRetencion": true
    }
  ]

return allAccesorios;
}

function reajusteAccesorios(){
  var contTotalReajuste = 0;
  var datosInputsA = $("input[name='dataAccesoriosIPT']");
  for(var i = 0; i<datosInputsA.length; i++)
  {
    +$(datosInputsA[i]).val().includes("-") ? $(datosInputsA[i]).val(valorAnterioInputs): contTotalReajuste += +$(datosInputsA[i]).val();
  }
  return contTotalReajuste;
}

function recalculoRetencion()
{
  var thisAccesorio = 0;
  var datosInputsA = $("input[name='dataAccesoriosIPT']");
  for(var i = 0; i<datosInputsA.length; i++)
  {
    var aplicaRetencion = $(datosInputsA[i]).data('isretencion');
    if (aplicaRetencion)
    {
      thisAccesorio +=  +$(datosInputsA[i]).val() * 0.04;
    }
  }
  recalculoReajuste(thisAccesorio);
}

function reajusteRepartos()
{
  var totalNewRepartos = 0;
  $("input[id=costoRepartosInput]").each(function () {
    totalNewRepartos += +$(this).val();
  });
  return totalNewRepartos
}

function getFolioXML(xml)
{
    const proxyURL = "https://cors-anywhere.herokuapp.com/";
    var newXML = proxyURL + xml;
    var rest;
    var req = new XMLHttpRequest();
       req.open('GET', newXML, false);
       req.send(null);
       console.log(req);
       if (req.status == 200)
       {
           var resp = req.responseXML;
           var obNodos = resp.children[0].attributes;
           var fol = obNodos.Folio ? obNodos.Folio.nodeValue : obNodos.Serie.nodeValue;
           rest = fol.replace(/^0+/, '');
       }
       else
       {
           rest = null;
       }
    return rest;
}

var getSerieProveedor = function(idProveedor){
  return fetch("/PendientesEnviar/GetSerieProveedor?IDProveedor=" + idProveedor, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    }
  }).then(function(response){
    if (response.status == 200)
    {
      return response.json();
    }
    else
    {
      Swal.fire({
        type: 'error',
        title: 'Algo salio mal',
        showConfirmButton: false,
        timer: 2500
      })
    }
  }).then(function(data){
    return data;
  }).catch(function(ex){
    console.log(ex);
  });
}

var getProveedorAmericano = function(idProveedor) {
  return fetch("/PendientesEnviar/GetProveedorByID?IDProveedor=" + idProveedor, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    }
  }).then(function(response){
    if (response.status == 200)
    {
      return response.json();
    }
    else
    {
      Swal.fire({
        type: 'error',
        title: 'Algo salio mal',
        showConfirmButton: false,
        timer: 2500
      })
    }
  }).then(function(data){
    return data;
  }).catch(function(ex){
    console.log(ex);
  });
}

function Dasboard(){

  var uppyDashboard = Uppy.Core({
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
  });
  return uppyDashboard;
}

var uploadEvidences = function(idU, ver){
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
          var id = idU;
          var options = {
            proudlyDisplayPoweredByUppy: false,
            target: id,
            inline: true,
            height: 160,
            width: 300,
            replaceTargetContent: true,
            showProgressDetails: true,
            note: 'Logisti-k',
           browserBackButtonClose: true,
         }
         var uppyDashboard = Uppy.Core({
           autoProceed: false,
           restrictions: {
              maxFileSize: 4200000, // 5mb
              maxNumberOfFiles: 1,
              minNumberOfFiles: 1,
              allowedFileTypes:['.pdf', 'image/*']
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
          uppyDashboard.use(GoogleDrive, { target: Dashboard, companionUrl: 'https://companion.uppy.io' });
          uppyDashboard.on('upload-success', (file, response) => {

           //$(`.uppy-DashboardItem-previewLink`).prop('href', `${response.body}`);
           $(`#${ver}`).append(`<a class="uppy-DashboardItem-previewLink" href="${response.body}" target="_blank" rel="noreferrer noopener"></a>`)
           $(`#${ver}`).append('<i class="fa fa-eye"></i>');
           $(`#${ver}`).css('color', 'green');
           $(`#${ver}`).data('urlEvidencia', response.body);
           $(`#${ver}`).data('nombrearchivo', file.name);

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


var FolioViajeXML = function(xml, folioB){
  try {
    const proxyURL = "https://cors-anywhere.herokuapp.com/";
    var newXML = proxyURL + xml;
    var FolioTrueOrFalse;
    var req = new XMLHttpRequest();
       req.open('GET', newXML, false);
       req.send(null);
       if (req.status == 200)
       {
         var resp = req.responseXML;
         var obNodosUI = resp.getElementsByTagName("cfdi:Concepto")[0];
         var folio = obNodosUI.getAttribute('Descripcion');
         var withoutBR = folio.replace(/\n|\r/g, " ")
         var withoutComa = withoutBR.replace(/,/g, "")
         var withoutPunto = withoutComa.replace(/\./g,'')
         var newArrFolio = withoutPunto.split(" ")
         var buscarFolio =  newArrFolio.indexOf(folioB)
         if (buscarFolio != -1){
          newArrFolio[buscarFolio] == folioB ? FolioTrueOrFalse=true:FolioTrueOrFalse= false;
         }
         else{
          var folio1 = obNodosUI.getAttribute('NoIdentificacion');
          var withoutBR1 = folio1.replace(/\n|\r/g, " ")
          var withoutComa1 = withoutBR1.replace(/,/g, "")
          var withoutPunto1 = withoutComa1.replace(/\./g,'')
          var newArrFolio1 = withoutPunto1.split(" ")
          var buscarFolio1 =  newArrFolio1.indexOf(folioB)
          buscarFolio1 != -1 ? newArrFolio1[buscarFolio1] == folioB ?( FolioTrueOrFalse = true, console.log(FolioTrueOrFalse)): FolioTrueOrFalse = false : FolioTrueOrFalse = false;
         }
       }
       else
       {
           FolioTrueOrFalse = false;
       }
    return FolioTrueOrFalse;
  } catch (e) {
    alertToastError("Ocurrio un error al leer el archivo xml");
    console.log(e);
    return FolioTrueOrFalse = false;
  }
}

var RFCRecerptor = function(xml){
  try {
    const proxyURL = "https://cors-anywhere.herokuapp.com/";
    var newXML = proxyURL + xml;
    var RFCInXML;
    var req = new XMLHttpRequest();
       req.open('GET', newXML, false);
       req.send(null);
       if (req.status == 200)
       {
         var resp = req.responseXML;
         var obNodosUI = resp.getElementsByTagName("cfdi:Receptor")[0];
         var rfc = obNodosUI.getAttribute('Rfc');
         RFCInXML = rfc;
       }
       else
       {
           RFCInXML = null;
       }
    return RFCInXML;
  } catch (e) {
    alertToastError("Ocurrio un error al leer el archivo xml");
    console.log(e);
    return RFCInXML = null;
  }
}

//
// var EvidenciasCustodia = function(){
//   var TipoEvidencia = [
//     {
//       "Titulo": "CORREO",
//       "Tipo": "EVCUSTODIAF"
//     },
//     {
//       "Titulo": "FOLIO",
//       "Tipo": "EVCUSTODIAF"
//     },
//   ]
//   return TipoEvidencia;
// }
//
// var SubirEvidenciasCustodia = function(status,delivery,XD_IDPedido,IDViaje,TipoEvidencia,RutaArchivo){
//   var item = EvidenciasCustodia();
//   for (var i=0; i<item.length; i++){
//     $('#allEvidences').append(`<div class="col-sm-4 col-lg-4 col-md-4">
//                           <div class="kt-portlet kt-portlet--height-fluid">
//                           <h5>Estatus: <strong>${status}</strong></h5>
//                             <div class="kt-portlet__head" id="headUppyTitulo">
//                               <div class="kt-portlet__head-label">
//                                 <h3 class="kt-portlet__head-title" id='${delivery.replace(/ /g, "")}' data-status="${status}">
//                                   ${delivery.replace(/ /g, "")}
//                                 </h3>
//                               </div>
//                             </div>
//                               <div class="kt-portlet__body">
//                                 <div class="row" id="prueba">
//                                 </div>
//                                 <div class="kt-uppy verificar" id="uploadEvidencesProveedor${delivery.replace(/ /g, "")}">
//                                   <div  class="kt-uppy__dashboard"></div>
//                                   <div class="kt-uppy__progress"></div>
//                                 </div>
//                                 <input type="text" id="ComentarioEvidencia" class="form-control" placeholder="Comentario" disabled>
//                               </div>
//                           </div>
//                         </div>`);
//
//     $(`#${delivery.replace(/ /g, "")}`).data('idpedido', XD_IDPedido)
//     $(`#${delivery.replace(/ /g, "")}`).data('idviaje', IDViaje)
//     $(`#${delivery.replace(/ /g, "")}`).data('tipoevidencia', TipoEvidencia)
//     status == 'Pendiente' || status == 'Rechazada' ? uploadEvidences(`#uploadEvidencesProveedor${delivery.replace(/ /g, "")}`, `${delivery.replace(/ /g, "")}`) : ($(`#uploadEvidencesProveedor${delivery.replace(/ /g, "")}`).append(`<div class="row">
//       <div class="col-md-4"><embed src="${RutaArchivo}"></div>
//     </div>`)/*, $('#btnGuardarEvidenciasP').prop('disabled', true)*/);
//   }
// }
