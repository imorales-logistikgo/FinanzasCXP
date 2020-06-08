$(document).ready(function(){

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

  });

});

var validacionBuscarFolio = function(){
  $('#inputBuscarViajeProveedor').focus();
  $('#inputBuscarViajeProveedor').addClass("border border-danger")
  alertToastError("Ingresa un Folio");
}

var validarGuardarEvidencias = function (){
  $('.uppy-DashboardItem-previewLink').each(function(){
    $(this).attr('href');
  });
}
