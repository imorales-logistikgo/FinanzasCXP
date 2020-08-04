$(document).ready(function(){

    $("#DescargarCartaNoAdeudo").on("click", function(){
        window.open('/CartaNoAdeudo/GetCartaNoAdeudo')
    });

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
  					note: 'Logisti-k',
           browserBackButtonClose: true,
         }
         var uppyDashboard = Uppy.Core({
           autoProceed: false,
           restrictions: {
  						maxFileSize: 4200000, // 5mb
  						maxNumberOfFiles: 1,
  						minNumberOfFiles: 1,
                        allowedFileTypes:['.pdf']
           },
           locale: Uppy.locales.es_ES,
//           onBeforeFileAdded: (currentFile, file) => {
//             if(Object.values(file)[0] === undefined)
//             {
//               console.log("+1")
//             }
//             else
//             {
//               if((currentFile.type === Object.values(file)[0].meta.type))
//               {
//                 uppyDashboard.info(`Los archivos deben ser diferentes`, 'error', 500)
//                 return false
//               }
//               else
//               {
//                 console.log("ok")
//               }
//             }
//
//           }
         });
         uppyDashboard.use(Dashboard, options);
         uppyDashboard.use(XHRUpload, { endpoint: 'https://api-bgk-debug.logistikgo.com/api/Viaje/SaveevidenciaTest', method: 'post'});
         uppyDashboard.use(GoogleDrive, { target: Dashboard, companionUrl: 'https://companion.uppy.io' });
         uppyDashboard.on('upload-success', (file, response) => {
         const fileName = file.name
          if (file.extension === 'pdf')
           {
             const urlPDF = response.body
             $('#CartaNoAdeudo').data("rutaarchivoPDF", urlPDF)
             document.querySelector('.uploaded-files-proveedor').innerHTML +=
             `<ol><li id="listaArchivos"><a href="${urlPDF}" target="_blank" name="url" id="RutaPDF">${fileName}</a></li></ol>`
           }
           else
           {
                const urlPDF = response.body
                $('#CartaNoAdeudo').data("rutaarchivoXML", urlPDF)
                document.querySelector('.uploaded-files-proveedor').innerHTML +=
                `<ol><li id="listaArchivos"><a href="${urlPDF}" target="_blank" name="url" id="RutaXML">${fileName}</a></li></ol>`
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

})