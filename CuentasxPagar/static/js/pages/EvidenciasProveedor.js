$(document).ready(function(){

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
        columns: [ 0,1,2,3,4,5,6,7,8,9]
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
          return '<button type="button" class="btn btn-primary btn-elevate btn-pill btn-sm" id="btnAprovarEvidencias"><i class="fa fa-clock"></i></button>';
        }
      },
      {
        "targets": 3,
        "className": "text-center bold",
        "mRender": function (data, type, full) {
          return '<button type="button" class="btn btn-primary btn-elevate btn-pill btn-sm" id="btnEvidenciasFisicas"><i class="fa fa-clock"></i></button>';
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
  });

  $('#btnGuardarEvidenciasP').on('click', function(){
    validarGuardarEvidencias();
  });


//Boton evidencias digitales
  $(document).on('click', '#btnAprovarEvidencias', function(){
    var IDViaje = $($(this).parents('tr')[0]).data('idviaje');
    GetEvidenciaMesaControl(IDViaje);
  });

//Boton Evidencias Fisicas
  $(document).on('click', '#btnEvidenciasFisicas', function(){
    var IDViaje = $($(this).parents('tr')[0]).data('idviaje');
    GetEvidenciasFisicas(IDViaje);
  });



//APROBAR EVIDENCIA
  $(document).on('click', '.AprobarEvidencia', function(){
    WaitMe_Show('#WaitModalEP')
    var removeBtnAprovar = $(this);
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
    var btnSelected = $(this);
    var getDOMInput = $(this).parents()[1];
    var getValorInput = $($(getDOMInput).find('input#ComentarioEvidencia')).val();
    Swal.fire({
      title: 'Rechazar Evidencia',
      text: "Estas a un paso de rechazar esta evidencia",
      type: 'warning',
      // input: 'text',
      // inputAttributes: {
      //   required: true,
      //   placeholder: "Motivo de la eliminación",
      //   id: "motivoRechazo"
      // },
      // validationMessage: 'Ingresa el motivo del rechazo',
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
          //ComentarioRechazo: $("#motivoRechazo").val(),
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

$(document).on('click', '#btnAprobarEVFisica', function(){
  $(this).removeClass('btn-outline-danger');
  $(this).addClass('btn-success');
  $(this).prop('disabled', true);
});

// LIMPIAR MODAL AL CERRARLO
  $('#ModalValidarEvidencias').on('hidden.bs.modal', function(){
    $('#VerEvidencia').empty();
  });

  $('#ModalValidarEvidenciasFisicas').on('hidden.bs.modal', function(){
    $('#listaEvidenciasFisicas').empty();
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
  $('.kt-portlet__head-title').each(function(){
    arrCompleteEvidences.push($(this).find('a')[0] == undefined ? 'false':'true');
  });
  arrCompleteEvidences.includes("false") ? alertToastError("Debes subir todas las evidencias"):saveEvidencias();
}

var saveEvidencias = function(){
  var arrEvidencias = [];
  $('.kt-portlet__head-title').each(function(){
    arrEvidencias.push({'IDPedido': $(this).data('idpedido'), 'Evidencia': $(this).data('urlEvidencia'), 'IDViaje': $(this).data('idviaje')});
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
        title: 'La factura ha sido validada correctamente',
        showConfirmButton: true,
        timer: 2500
      })
      // var trBtnAprovar= $(btn).closest('tr');
      // var findInput = $(trBtnAprovar).find('input[name="checkEC"]')[0];
      // $(findInput).css('display', 'block');
      // $(btn).remove();
      // WaitMe_Hide('#TbPading');
    }
    else if(response.status == 500)
    {
      Swal.fire({
        type: 'error',
        title: 'Hubo un error validando la factura',
        showConfirmButton: false,
        timer: 2500
      })
      // WaitMe_Hide('#TbPading');
    }

  }).catch(function(ex){
    console.log(ex);
  });
}
