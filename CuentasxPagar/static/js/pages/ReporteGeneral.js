$(document).ready(function(){

DataTableStyle()

//Filtro Rango fecha
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
  $(this).val(picker.startDate.format('YYYY/MM/DD') + ' - ' + picker.endDate.format('YYYY/MM/DD'));
});

$('#btnAplicarFiltro').on('click', fnGetReporteGeneral);

});



//*********************************FUNCIONES*********************************

var DataTableStyle = function(){
$('#TableReporteGeneral').DataTable({
    "scrollX": true,
    "scrollY": "350px",
    "dom": 'Bfrtip',
    "language": {
         "url": "https://cdn.datatables.net/plug-ins/1.10.16/i18n/Spanish.json"
     },
    "buttons": [
       {
          extend: 'excel',
          text: '<i class="fas fa-file-excel fa-lg"></i>',
       }
    ],
});
}


var fnGetReporteGeneral = function () {
  WaitMe_Show('#divTablaReproteGeneral');
  arrStatus = $('#cboStatus').val();
  arrClientes = $('#cboCliente').val();
  TipoViaje = $('#cboTipoViaje').val();
  startDate = ($('#cboFechaDescarga').data('daterangepicker').startDate.format('YYYY-MM-DD'));
  endDate = ($('#cboFechaDescarga').data('daterangepicker').endDate.format('YYYY-MM-DD'));
  GetReporteTotales("FechaDescargaDesde="+ startDate +"&FechaDescargaHasta="+ endDate +"&Status="+ JSON.stringify(arrStatus)
     +"&Cliente="+ JSON.stringify(arrClientes)+"&TipoViaje="+TipoViaje);
  }

