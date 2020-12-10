var Transportista_ID;

$(document).ready(function(){
$("#TablaPassword").DataTable({
    "lengthMenu": [10],
    "language": {
     "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
   },
});

$("#TablaAddCorreo").DataTable({
    "lengthMenu": [10],
    "language": {
     "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
   },
});


$(document).on('click', '#BloquearAccesoProveedor', function(){
    BloquearProveedor($(this).data('id'), $(this))
});

$(document).on('click', '#AccesoProveedor', function(){
    DesbloquearProveedor($(this).data('id'), $(this))
});

$(document).on('click', '#NewCorreo', function(){
    Transportista_ID = $(this).data('idtransportista');
});

$(document).on('click', '.Correos',fnGetDetalleCorreo);

$("#GuardarCorreo").on('click', function(){
    if ($('#EmailAdd').val() == ""){
        alertToastError("Debes ingresar un correo");
    }
    else{
        AddCorreoByTransportista($('#EmailAdd').val())
    }
});

$('#AddCorreo').on('hidden.bs.modal', function(){
  LimpiarModalAddCorreo();
});

$(document).on('click', "#ActivarCorreo, #DesactivarCorreo",function(){
    ActivarCorreo($(this).data('idcorreo'), $(this)[0].id, $(this));
});

$(document).on('click', "#CartaNOAdeudo",function(){
    window.open(`/CartaNoAdeudoMC/CreateCartaNoadeudoMC?IDProveedor=${$(this).data('idtransportista')}`)
});

});




var BloquearProveedor =  function(usuario, btn){
  WaitMe_Show('#TablaPassword');
  jParams = {
    IDUsuario: usuario
  }
  fetch("/Dashboard/BloquearAccesoProveedor", {
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
        title: 'Proveedor bloqueado Exitosamente',
        showConfirmButton: false,
        timer: 2500
      })
        $(btn).removeClass();
        $(btn).addClass('btn btn-success btn-elevate btn-circle btn-icon');
        $(btn).children()[0].remove();
        $(btn).html("<i class='fa fa-lock-open'></i>");
        $(btn).removeAttr('id');
        $(btn).attr('id', 'AccesoProveedor');
        $(btn).removeAttr('title');
        $(btn).attr('title', 'Permitir Acceso');
        WaitMe_Hide('#TablaPassword')
    }
    else if(response.status == 500)
    {
      Swal.fire({
        type: 'error',
        title: 'Ocurrio un error, por favor intenta de nuevo',
        showConfirmButton: false,
        timer: 2500
      })
      WaitMe_Hide('#TablaPassword')
    }
  }).catch(function(ex){
    console.log(ex);
    alertToastError("Ocurrio un error")
    WaitMe_Hide('#TablaPassword')
  });
}


var DesbloquearProveedor =  function(usuario, btn){
   WaitMe_Show('#TablaPassword');
  jParams = {
    IDUsuario: usuario
  }
  fetch("/Dashboard/DesbloquearAccesoProveedor", {
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
        title: 'Proveedor desbloqueado Exitosamente',
        showConfirmButton: false,
        timer: 2500
      })
        $(btn).removeClass();
        $(btn).addClass('btn btn-danger btn-elevate btn-circle btn-icon');
        $(btn).children()[0].remove();
        $(btn).html("<i class='fa fa-lock'></i>");
        $(btn).removeAttr('id');
        $(btn).attr('id', 'BloquearAccesoProveedor');
        $(btn).removeAttr('title');
        $(btn).attr('title', 'Bloquear Acceso');
        WaitMe_Hide('#TablaPassword')
    }
    else if(response.status == 500)
    {
      Swal.fire({
        type: 'error',
        title: 'Ocurrio un error, por favor intenta de nuevo',
        showConfirmButton: false,
        timer: 2500
      })
      WaitMe_Hide('#TablaPassword')
    }
  }).catch(function(ex){
    WaitMe_Hide('#TablaPassword')
    console.log(ex);
  });
}

var fnGetDetalleCorreo = function () {
  var IDFactura = $(this).data('idtransportista');
  WaitMe_Show('#divTablaDetalles');
  fetch(`/Dashboard/GetDetallesCorreo?IDTransportista=${IDFactura}`, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    return response.clone().json();
  }).then(function(data){
    $('#divTablaDetalles').html(data.htmlRes);
    $('#tablaDetallesCorreos').DataTable();
    WaitMe_Hide('#divTablaDetalles');
  }).catch(function(ex){
     Swal.fire({
        type: 'error',
        title: 'Ocurrio un error, por favor intenta de nuevo',
        showConfirmButton: false,
        timer: 2500
     })
     WaitMe_Hide('#divTablaDetalles');
     $("#detallesCorreos").modal('hide');
     console.log(ex);
  });
}


var AddCorreoByTransportista = function(Correo){
   WaitMe_Show('#divTablaDetallesAdd');
  jParams = {
    IDTransportista: Transportista_ID,
    Correo: Correo
  }
  fetch("/Dashboard/AddCorreoByTransportista", {
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
        title: 'Correo guardado correctamente',
        showConfirmButton: false,
        timer: 2500
      })
      $("#AddCorreo").modal('hide');
      WaitMe_Hide('#divTablaDetallesAdd')
    }
    else if(response.status == 500)
    {
      Swal.fire({
        type: 'error',
        title: 'Ocurrio un error, por favor intenta de nuevo',
        showConfirmButton: false,
        timer: 2500
      })
      WaitMe_Hide('#divTablaDetallesAdd')
    }
  }).catch(function(ex){
    console.log(ex);
    WaitMe_Hide('#divTablaDetallesAdd')
    alertToastError("Ocurrio un error")
  });
}


var LimpiarModalAddCorreo = function(){
    $('#EmailAdd').val('');
    Transportista_ID = null;
}


var ActivarCorreo = function(idcorreo, accion, btn){
  WaitMe_Show('#divTablaDetalles');
  jParams = {
    IDCorreo: idcorreo,
    Accion: accion
  }
  fetch("/Dashboard/ActivarOrDesactivarCorreoToSendEmail", {
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
        title: accion == 'ActivarCorreo' ? 'Correo Activado correctamente' : 'Correo Desactivado correctamente',
        showConfirmButton: false,
        timer: 2500
      })
      $(btn).removeClass();
      accion == 'ActivarCorreo' ? $(btn).addClass('btn btn-danger btn-elevate btn-circle btn-icon') : $(btn).addClass('btn btn-success btn-elevate btn-circle btn-icon');
      $(btn).children()[0].remove();
      accion == 'ActivarCorreo' ? $(btn).html("<i class='fa fa-lock'></i>") : $(btn).html("<i class='fa fa-lock-open'></i>");
      $(btn).removeAttr('id');
      accion == 'ActivarCorreo' ? $(btn).attr('id', 'DesactivarCorreo') : $(btn).attr('id', 'ActivarCorreo')
      $(btn).removeAttr('title');
      accion == 'ActivarCorreo' ? $(btn).attr('title', 'Desactivar Correo') : $(btn).attr('title', 'Activar Correo');
      var table = $('#tablaDetallesCorreos').DataTable();
      index = table.row($(btn).parents('tr')).index()
      accion == 'ActivarCorreo' ? table.cell(index,1).data("Si") : table.cell(index,1).data("No");
      WaitMe_Hide('#divTablaDetalles')
    }
    else if(response.status == 500)
    {
      Swal.fire({
        type: 'error',
        title: 'Ocurrio un error, por favor intenta de nuevo',
        showConfirmButton: false,
        timer: 2500
      })
      WaitMe_Hide('#divTablaDetalles')
    }
  }).catch(function(ex){
    console.log(ex);
    WaitMe_Hide('#divTablaDetalles')
    alertToastError("Ocurrio un error")
  });
}
