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
          return (full[2] == 'True' ?'<button class="btn btn-primary btn-elevate btn-pill btn-sm"><i class="fa fa-clock"></i></button>':'<button class="btn btn-primary btn-elevate btn-pill btn-sm" disabled><i class="fa fa-clock"></i></button>');
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

  $(document).on('click', '#btnAprovarEvidencias', function(){
    var IDViaje = $($(this).parents('tr')[0]).data('idviaje');
    GetEvidenciaMesaControl(IDViaje);
  });

  $(document).on('click', '.AprobarEvidencia', function(){
    jParams = {
      IDSaveEvidencia: $(this).data('idevidenciaaprobar'),
      TipoEvidencia: $(this).data('tipoevidencia'),
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

        $(this).parents()[0].remove();
      }
      else if(response.status == 500)
      {
        Swal.fire({
          type: 'error',
          title: 'Hubo un error validando la evidencia',
          showConfirmButton: false,
          timer: 2500
        })
        // WaitMe_Hide('#TbPading');
      }

    }).catch(function(ex){
      console.log(ex);
    });

    // var a=$(this).data('idevidenciaaprobar');
    // $(this).parents()[0].remove();
    // console.log(a);
  });

  $(document).on('click', '.RechazarEvidencia', function(){
    var a=$(this).data('idevidenciarechazar');
    $(this).parents()[0].remove();
    console.log(a);
  });

  $('#ModalValidarEvidencias').on('hidden.bs.modal', function(){
    $('#VerEvidencia').empty();
  });

});

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
