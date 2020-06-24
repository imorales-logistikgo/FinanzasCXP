var btn, IDViaje;
$(document).ready(function(){
$.fn.modal.Constructor.prototype._enforceFocus = function() {};
  $('#TableEvidenciasProveedor').DataTable({
    "scrollX": true,
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
        columns: [0,1,2,3]
      }
    }
    ],
    columnDefs: [
      {
        "targets": 0,
        "className": "text-center bold",
      },
      {
        "targets": 1,
        "className": "text-center",
      },
      {
        "targets": 2,
        "className": "text-center bold",
        "mRender": function (data, type, full) {
          return (full[2] == 'True' ? '<button type="button" class="btn btn-success btn-elevate btn-pill btn-sm" id="btnAprovarEvidencias" disabled><i class="fa fa-check"></i></button>':'<button type="button" class="btn btn-primary btn-elevate btn-pill btn-sm" id="btnAprovarEvidencias"><i class="fa fa-clock"></i></button>');
        }
      },
      {
        "targets": 3,
        "className": "text-center bold",
        "mRender": function (data, type, full) {
          return (full[3] == 'True' ? '<button type="button" class="btn btn-success btn-elevate btn-pill btn-sm" id="btnEvidenciasFisicas" disabled><i class="fa fa-check"></i></button>': '<button type="button" class="btn btn-primary btn-elevate btn-pill btn-sm" id="btnEvidenciasFisicas"><i class="fa fa-clock"></i></button>');
        }
      }
     ]
  });

  $("#inputBuscarViajeProveedor").keypress(function(e) {
    if (e.which == 13) {
        return false;
    }
  });

  $('#buscarViajeProveedor').on('click', function(){
    $('#inputBuscarViajeProveedor').val() == "" ? validacionBuscarFolio() : GetFolioEvidencias($('#inputBuscarViajeProveedor').val());
  });


  $('#btnCerrarDivProveedorEvidencias').on('click', function(){
    $('#uploadEvidenciasModal').css('display', 'none');
    $('#inputBuscarViajeProveedor').removeClass("border border-success");
    $('#inputBuscarViajeProveedor,#buscarViajeProveedor').prop('disabled', false);
    $('#inputBuscarViajeProveedor').val('');
    $('#inputBuscarViajeProveedor').focus();
    $('#allEvidences').empty();
    $('#StatusEvidencias').empty();
    $('#btnGuardarEvidenciasP').prop('disabled', false)
    $('#BtnHojaLiberacion').removeAttr('href');
  });

  $('#btnGuardarEvidenciasP').on('click', function(){
    validarGuardarEvidencias();
  });


//Boton evidencias digitales
  $(document).on('click', '#btnAprovarEvidencias', function(){
    btn=$(this)
    var folio = $($(this).parents('tr')[0]).data('folio');
    folio.includes('FTL') ? IDViaje = $($(this).parents('tr')[0]).data('idviajebkg') : IDViaje = $($(this).parents('tr')[0]).data('idviaje');
    GetEvidenciaMesaControl(IDViaje, folio.trim());
  });

//Boton Evidencias Fisicas
  $(document).on('click', '#btnEvidenciasFisicas', function(){
    var folio = $($(this).parents('tr')[0]).data('folio');
    folio.includes('FTL') ? IDViaje = $($(this).parents('tr')[0]).data('idviajebkg') : IDViaje = $($(this).parents('tr')[0]).data('idviaje');
    GetEvidenciasFisicas(IDViaje, folio);
  });



//APROBAR EVIDENCIA
  $(document).on('click', '.AprobarEvidencia', function(){
    WaitMe_Show('#WaitModalEP')
    var removeBtnAprovar = $(this);
    var tipoEv = $(this).data('tipoevidencia');
    var getDOMInput = $(this).parents()[1];
    var getValorInput = $($(getDOMInput).find('input#ComentarioEvidencia')).val();
    jParams = {
      IDSaveEvidencia: $(this).data('idevidenciaaprobar'),
      TipoEvidencia: $(this).data('tipoevidencia'),
      Comentarios: getValorInput,
    }
    fetch("/EvidenciasProveedor/SaveAprobarEvidencia", {
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
          title: 'Evidencia validada correctamente',
          showConfirmButton: true,
          timer: 2500
        })
        $(removeBtnAprovar).parents()[0].remove()
        GetIsEvidenciaDigitalCompleta(IDViaje, tipoEv);
        WaitMe_Hide('#WaitModalEP');
      }
      else if(response.status == 500)
      {
        Swal.fire({
          type: 'error',
          title: 'Hubo un error validando la evidencia',
          showConfirmButton: false,
          timer: 2500
        })
         WaitMe_Hide('#WaitModalEP');
      }

    }).catch(function(ex){
      WaitMe_Hide('#WaitModalEP')
      console.log(ex);
    });
  });



//RECHAZAR EVIDENCIA
  $(document).on('click', '.RechazarEvidencia', function(){
    WaitMe_Show('#WaitModalEP')
    var btnSelected = $(this);
    var getDOMInput = $(this).parents()[1];
    var getValorInput = $($(getDOMInput).find('input#ComentarioEvidencia')).val();
    Swal.fire({
      title: 'Rechazar Evidencia',
      text: "Estas a un paso de rechazar esta evidencia",
      type: 'warning',
      input: 'text',
      inputAttributes: {
        required: true,
        placeholder: "Motivo de la eliminación",
        id: "motivoRechazo"
      },
      validationMessage: 'Ingresa el motivo del rechazo',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Aceptar'
    }).then((result) => {
      if (result.value) {
        jParams = {
          IDRechazarEvidencia: $(this).data('idevidenciarechazar'),
          TipoEvidencia: $(this).data('tipoevidencia'),
          Comentarios: getValorInput,
          ComentarioRechazo: $("#motivoRechazo").val(),
        }
        fetch("/EvidenciasProveedor/RechazarEvidencias", {
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
              title: 'Evidencia Rechazada',
              showConfirmButton: true,
              timer: 2500
            })
            $(btnSelected).parents()[0].remove()
            $(btn).removeClass('btn-primary');
            $(btn).addClass('btn-danger');
            var changeIcon = $(btn).find('i')[0];
            $(changeIcon).removeClass('fa-clock');
            $(changeIcon).addClass('fa-window-close')
            WaitMe_Hide('#WaitModalEP');
            //$(btn).prop('disabled', true);
          }
          else if(response.status == 500)
          {
            Swal.fire({
              type: 'error',
              title: 'Hubo un error al rechazar la evidencia',
              showConfirmButton: false,
              timer: 2500
            })
             WaitMe_Hide('#WaitModalEP');
          }

        }).catch(function(ex){
          WaitMe_Hide('#WaitModalEP')
          console.log(ex);
        });

      }
    });
  });

//APROBAR EVIDENCIA FISICA
  $(document).on('click', '#btnAprobarEVFisica', function(){
    var btn = $(this)
    Swal.fire({
    title: '¿Estas Seguro?',
    text: "Aprobar evidencia fisica",
    type: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Aceptar'
    }).then((result) => {
    if (result.value) {
      WaitMe_Show('#WaitModalEPF');
      jParams = {
        IDViaje: $(this).data('idviaje'),
        IDPedido: $(this).data('idpedido'),
        TipoEvidencia: $(this).data('tipoevidenciafisica')
      }
      fetch("/EvidenciasProveedor/SaveEvidenciaFisica", {
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
            title: 'Evidencia fisica validada correctamente',
            showConfirmButton: true,
            timer: 2500
          })
          $(btn).removeClass('btn-outline-danger');
          $(btn).addClass('btn-success');
          $(btn).prop('disabled', true);
          WaitMe_Hide('#WaitModalEPF');
        }
        else if(response.status == 500)
        {
          Swal.fire({
            type: 'error',
            title: 'Hubo un error al validar la evidencia fisica',
            showConfirmButton: false,
            timer: 2500
          })
           WaitMe_Hide('#WaitModalEPF');
        }

      }).catch(function(ex){
        WaitMe_Hide('#WaitModalEPF')
        console.log(ex);
      });
    }
    })
});

// LIMPIAR MODAL AL CERRARLO
  $('#ModalValidarEvidencias').on('hidden.bs.modal', function(){
    $('#VerEvidencia').empty();
  });

  $('#ModalValidarEvidenciasFisicas').on('hidden.bs.modal', function(){
    $('#listaEvidenciasFisicas').empty();
  });

  //HOJA DE LIBERACION
    $(document).on('click', '#BtnHojaLiberacion', function(){
      WaitMe_ShowBtn('#BtnHojaLiberacion')
      var IDViajeHoja = $(this).data('IDViajeHL');
      GetHojaLiberacion(IDViajeHoja, $(this).data('TipoEvidenciaHL'))
    });


});


//***** CODIGO PARA EL PROVEEDOR ****////
var validacionBuscarFolio = function(){
  $('#inputBuscarViajeProveedor').focus();
  $('#inputBuscarViajeProveedor').addClass("border border-danger")
  alertToastError("Ingresa un Folio");
}

var validarGuardarEvidencias = function (){
  var arrCompleteEvidences = [];
  var arrCompleteEvidencesRemission = []
  $('.kt-portlet__head-title').each(function(){
    if($(this).data('tipoevidencia') == 'BKG'){
      $(this).data('status') == 'Aprobada' ? '': $(this).prop('id').includes('Remision') && ($(this).data('status') == 'Rechazada' || $(this).data('status') == 'Pendiente') ? arrCompleteEvidencesRemission.push($(this).find('a')[0] == undefined ? 'false':'true') : $(this).prop('id') !='Remision' && $(this).data('status') == 'Rechazada' || $(this).data('status') == 'Pendiente' ? arrCompleteEvidences.push($(this).find('a')[0] == undefined ? 'false':'true') : "";
    }
    else{
       $(this).data('status') == 'Aprobada' ? '': arrCompleteEvidences.push($(this).find('a')[0] == undefined ? 'false':'true');
    }
  });
  if($('.kt-portlet__head-title').data('evidencia') == 'BKG'){
    arrCompleteEvidencesRemission.includes("false") ? alertToastError("Debes subir todas las evidencias") : arrCompleteEvidences.length != 0 ? arrCompleteEvidences.includes("true") ? saveEvidencias() : alertToastError("Debes subir todas las evidencias"): saveEvidencias();
  }else{
    arrCompleteEvidences.includes("false") ? alertToastError("Debes subir todas las evidencias"):saveEvidencias();
  }
}

var saveEvidencias = function(){
  WaitMe_Show('#uploadEvidenciasModal');
  var IDViajeCheck;
  var arrEvidencias = [];
  $('.kt-portlet__head-title').each(function(){
    IDViajeCheck = $(this).data('idviaje');
    $(this).data('status') == 'Aprobada' ? "":$(this).find('a')[0] == undefined ? "" : arrEvidencias.push({'IDPedido': $(this).data('idpedido'), 'Evidencia': $(this).data('urlEvidencia'), 'IDViaje': $(this).data('idviaje'), TipoEvidencia: $(this).data('tipoevidencia'), NombreArchivo: $(this).data('nombrearchivo'), Titulo: $(this).prop('id'), Status:$(this).data('status')});
  });

  jParams = {
    arrEvidencias: arrEvidencias,
  }

  fetch("/EvidenciasProveedor/SaveEvidencias", {
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
        title: 'La evidencia ha sido guardada correctamente',
        showConfirmButton: true,
        timer: 2500
      })
      $('#uploadEvidenciasModal').css('display', 'none');
      $('#inputBuscarViajeProveedor').removeClass("border border-success");
      $('#inputBuscarViajeProveedor,#buscarViajeProveedor').prop('disabled', false);
      $('#inputBuscarViajeProveedor').val('');
      $('#inputBuscarViajeProveedor').focus();
      $('#allEvidences').empty();
      $('#StatusEvidencias').empty();
      $('#btnGuardarEvidenciasP').prop('disabled', false)
      WaitMe_Hide('#uploadEvidenciasModal');
    }
    else if(response.status == 500)
    {
      Swal.fire({
        type: 'error',
        title: 'Hubo un error al guardar la evidencia',
        showConfirmButton: false,
        timer: 2500
      })
       WaitMe_Hide('#uploadEvidenciasModal');
    }

  }).catch(function(ex){
    console.log(ex);
    WaitMe_Hide('#uploadEvidenciasModal');
  });
}
