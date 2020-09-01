var btn, IDViaje;
$(document).ready(function(){
$.fn.modal.Constructor.prototype._enforceFocus = function() {};

  formatDataTable();
  $('#btnAplicarFiltro').on('click', fnGetEvidenciasByFilter);
  $("#inputBuscarViajeProveedor").keypress(function(e) {
    if (e.which == 13) {
        return false;
    }
  });

    $('#TableEvidenciasCXP').DataTable({
        "scrollY":"400px"
    });

  $('#buscarViajeProveedor').on('click', function(){
    $('#inputBuscarViajeProveedor').val() == "" ? validacionBuscarFolio() : GetFolioEvidencias($('#inputBuscarViajeProveedor').val());
  });


    $(document).on('click',"#BtnShowEvidencia",function(){
        var folio = $($(this).parents('tr')[0]).data('folio');
        var IDViaje = $($(this).parents('tr')[0]).data('idviaje');
//        folio.includes('FTL') ? IDViaje = $($(this).parents('tr')[0]).data('idviajebkg') : IDViaje = $($(this).parents('tr')[0]).data('idviaje');
        GetEvidenciasForCXP(IDViaje, folio.trim())
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

  //filtro de fecha solo por mes y año
  $(document).on( 'change', 'input[name="fechaxMesyAño"]', function () {
    if($(this).is(':checked')){
      $('#filtroxMesyAno').css("display", "block");
      $('#fechaRango').hide();
    }
    else
    {
      $('#filtroxMesyAno').css("display", "none");
      $('#fechaRango').show();
    }
  });

  $('input[name="FiltroFecha"]').daterangepicker({
   autoUpdateInput: false,
   showDropdowns:true,
   autoApply:true,
   locale: {
         daysOfWeek: [
             "Do",
             "Lu",
             "Ma",
             "Mi",
             "Ju",
             "Vi",
             "Sa"
         ],
         monthNames: [
             "Enero",
             "Febrero",
             "Marzo",
             "Abril",
             "Mayo",
             "Junio",
             "Julio",
             "Agosto",
             "Septiembre",
             "Octubre",
             "Noviembre",
             "Diciembre"
         ],
     }
  });

  $('input[name="FiltroFecha"]').on('apply.daterangepicker', function(ev, picker) {
    $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
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
      else{
        WaitMe_Hide('#WaitModalEP')
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

  $('#ModalEvidenciasCXP').on('hidden.bs.modal', function(){
    $('#VerEvidenciaCXP').empty();
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
       $(this).data('status') == 'Aprobada' ? '': $(this).data('status') == 'Pendiente' || $(this).data('status') == 'Rechazada' ? arrCompleteEvidences.push($(this).find('a')[0] == undefined ? 'false':'true'):'';
    }
  });
  if($('.kt-portlet__head-title').data('evidencia') == 'BKG'){
    arrCompleteEvidencesRemission.includes("false") ? alertToastError("Debes subir todas las evidencias") : arrCompleteEvidences.length != 0 ? arrCompleteEvidences.includes("true") ? saveEvidencias() : alertToastError("Debes subir todas las evidencias"): saveEvidencias();
  }else{
    arrCompleteEvidences.includes("true") ?saveEvidencias(): alertToastError("Debes subir todas las evidencias");
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

var fnGetEvidenciasByFilter = function () {
  arrProveedor = $('#cboProveedor').val();
  arrStatus = $('#cboStatus').val();
  arrProyectos = $('#cboProyecto').val();
  WaitMe_Show('#TbPading');
  if($('#chkMonthYear').is(':checked')){
    arrMonth = $('#filtroxMes').val();
    Year = $('#filtroxAno').val();
    getEvidenciasByFilter("arrMonth="+ JSON.stringify(arrMonth) +"&Year="+ Year +"&Proveedor="+ JSON.stringify(arrProveedor) +"&Status="+ JSON.stringify(arrStatus) +"&Proyecto="+ JSON.stringify(arrProyectos));
  }
  else{
    startDate = ($('#cboFechaDescarga').data('daterangepicker').startDate._d).toLocaleDateString('en-US');
    endDate = ($('#cboFechaDescarga').data('daterangepicker').endDate._d).toLocaleDateString('en-US');
    getEvidenciasByFilter("FechaFacturaDesde="+ startDate +"&FechaFacturaHasta="+ endDate +"&Proveedor="+ JSON.stringify(arrProveedor) +"&Status="+ JSON.stringify(arrStatus) +"&Proyecto="+ JSON.stringify(arrProyectos));
  }
}

function getEvidenciasByFilter(params){
  fetch("/EvidenciasProveedor/FilterBy?" + params, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
  }).then(function(response){
    return response.clone().json();
  }).then(function(data){
    $('#divTablaPendientesEnviar').html(data.htmlRes);
    formatDataTable();
    // $('#TableEvidenciasProveedor').css("display", "block");
  }).catch(function(ex){
    console.log(ex);
  });
}

function formatDataTable(){
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
}
