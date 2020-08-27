var uppyD;
$(document).ready(function(){
    $("#DescargarCartaNoAdeudo").on("click", function(){
        window.open('/CartaNoAdeudo/GetCartaNoAdeudo')
    });

    $("#TablaCartaNoAdeudo").DataTable({
        "scrollX": true
    });
    $("#TablaCartaNoAdeudoProveedor").DataTable();

    $("#btnGuardarCartaNoAdeudo").on('click', function(){
        $('#CartaNoAdeudo').data("rutaarchivoPDF") == undefined || $('#CartaNoAdeudo').data("rutaarchivoPDF") == null ? alertToastError("Ningun archivo ha sido cargado") : SaveCartaNoAdeudo();
    });

    $(document).on('click',"#BtnAprobarCarta", function(){
        AprobarCarta($(this))
    });

    $(document).on('click',"#BtnRechazarCarta", function(){
        var button = $(this)
        Swal.fire({
          title: '¿Estas Seguro?',
          text: "Estas a un click de Rechazar algo importante",
          type: 'warning',
          input: 'text',
          inputAttributes: {
            required: true,
            placeholder: "Motivo de la eliminación",
            id: "comentarioRechazoCarta"
          },
          validationMessage: 'Ingresa el motivo de la eliminación',
          showCancelButton: true,
          confirmButtonColor: '#3085d6',
          cancelButtonColor: '#d33',
          confirmButtonText: 'Aceptar'
        }).then(function(result) {
            if(result.value)
                RechazarCarta(button)
          });
    });




//PLUGIN PARA SUBIR LOS ARCHIVOS AL SERVIDOR
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
  				var id = '#CartaNoAdeudo';
  				var options = {
  					proudlyDisplayPoweredByUppy: false,
  					target: id,
  					inline: true,
  					height: 260,
  					replaceTargetContent: true,
  					showProgressDetails: true,
  					showLinkToFileUploadResult: true,
  					note: 'Logisti-k',
           browserBackButtonClose: true,
         }
         var uppyDashboard = Uppy.Core({
           autoProceed: false,
           restrictions: {
  						maxFileSize: 22000000, // 22MB
  						maxNumberOfFiles: 1,
  						minNumberOfFiles: 1,
                        allowedFileTypes:['.pdf'],
           },
           locale: Uppy.locales.es_ES,
           onBeforeFileAdded: (currentFile, file) => {
                console.log(currentFile.data)
           }
         });
         uppyDashboard.use(Dashboard, options);
         uppyDashboard.use(XHRUpload, { endpoint: 'upload', method: 'post', headers:{"X-CSRFToken": getCookie("csrftoken")}, metaFields: null, timeout: 0});
         uppyDashboard.use(GoogleDrive, { target: Dashboard, companionUrl: 'https://companion.uppy.io' });
         uppyDashboard.on('upload-error', (file, error, response) => {
            if (response.status == 500){
                alertToastError("La carta ya fue subida")
            }
         });
         uppyDashboard.on('upload-success', (file, response) => {
         const fileName = file.name
             const urlPDF = response.body.url
             $('#CartaNoAdeudo').data("rutaarchivoPDF", urlPDF)
             document.querySelector('.uploaded-files-proveedor').innerHTML +=
             `<ol><li id="listaArchivos"><a href="${urlPDF}" target="_blank" name="url" id="RutaPDF">${fileName}</a></li></ol>`
             uppyD =  uppyDashboard
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



//METODOS

    var SaveCartaNoAdeudo = function() {
      WaitMe_Show('#WaitmeSaveCarta')
      jParams = {
        RutaCartaNoAdeudo: $('#CartaNoAdeudo').data("rutaarchivoPDF")
      }
      fetch("/CartaNoAdeudo/SaveCartaNoAdeudo", {
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
            title: 'Carta No Adeudo Guardada Correctamente.',
            showConfirmButton: false,
            timer: 2500
          })
          LimpiarPluginArchivos()
          WaitMe_Hide('#WaitmeSaveCarta')
        }
        else if(response.status == 500)
        {
          Swal.fire({
            type: 'error',
            title: 'Ocurrio un error al guardar la Carta No Adeudo, Por favor intentalo de nuevo.',
            showConfirmButton: false,
            timer: 2500
          })
          WaitMe_Hide('#WaitmeSaveCarta')
         }
      }).catch(function(ex){
        console.log(ex);
      });
    }

    var LimpiarPluginArchivos = function(){
         $('#CartaNoAdeudo').data("rutaarchivoPDF", null)
         $('.uploaded-files-proveedor ol').remove()
         uppyD.cancelAll()
         //KTUppy.init();
    }


})

var AprobarCarta = function(btn){
    WaitMe_Show('#TbPading');
    jParams = {
        IDCarta: $(btn).data("idcarta"),
    }
  fetch("/CartaNoAdeudo/AprobarCarta", {
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
         title: 'Carta Validada correctamente',
         showConfirmButton: false,
         timer: 2500
      })
      var tablaIndexChange = $('#TablaCartaNoAdeudo').DataTable();
      index = tablaIndexChange.row($(btn).parents('tr')).index()
      tablaIndexChange.cell(index,3).data("APROBADA");
      btnWithParents = $(btn).parents('tr')
      findBtnRechazar = btnWithParents.find("#BtnRechazarCarta")[0]
      $(findBtnRechazar).remove()
      $(btn).remove()
      WaitMe_Hide('#TbPading');
    }
    else if(response.status == 500)
    {
       Swal.fire({
         type: 'error',
         title: 'Ocurrio un error al validar',
         showConfirmButton: false,
         timer: 2500
       })
       WaitMe_Hide('#TbPading');
    }
  }).catch(function(ex){
    console.log(ex);
    WaitMe_Hide('#TbPading');
  });
}

var RechazarCarta = function(btn){
        WaitMe_Show('#TbPading');
    jParams = {
        IDCarta: $(btn).data("idcarta"),
        ComentarioRechazo: $("#comentarioRechazoCarta").val()
    }
  fetch("/CartaNoAdeudo/RechazarCarta", {
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
         title: 'La carta fue rechazada',
         showConfirmButton: false,
         timer: 2500
      })
      var tablaIndexChange = $('#TablaCartaNoAdeudo').DataTable();
      index = tablaIndexChange.row($(btn).parents('tr')).index()
      tablaIndexChange.cell(index,3).data("RECHAZADA");
      btnWithParents = $(btn).parents('tr')
      findBtnAprobar = btnWithParents.find("#BtnAprobarCarta")[0]
      $(findBtnAprobar).remove()
      $(btn).remove()
      WaitMe_Hide('#TbPading');
    }
    else if(response.status == 500)
    {
       Swal.fire({
         type: 'error',
         title: 'Ocurrio un error al rechazar',
         showConfirmButton: false,
         timer: 2500
       })
       WaitMe_Hide('#TbPading');
    }
  }).catch(function(ex){
    console.log(ex);
    WaitMe_Hide('#TbPading');
  });
}