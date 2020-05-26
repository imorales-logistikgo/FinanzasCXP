function Getdatos(t){
  //var arrSelect=[];
  // $("input[name=checkEC]:checked").each(function () {
  //   var datosRow = table.row($(this).parents('tr')).data();
  //   var prueba = $(this).data("idfactu");
  //   arrSelect.push([datosRow[1],datosRow[7], datosRow[8], datosRow[9], datosRow[7], prueba, datosRow[2]]);
  // });
  var datosRow = table.row($(t).parents('tr')).data();
  var prueba = $(t).data("idfactu");
  arrSelect.push([datosRow[1],datosRow[7], datosRow[8], datosRow[9], datosRow[7], prueba, datosRow[2]]);
  return arrSelect;
}

function removeItemFromArr (arr, item) {
  var newArr=[];
  for(var i=0;i<arr.length;i++){
      var jsonItem = JSON.stringify(arr[i]) == JSON.stringify(item[0]);
      jsonItem ? console.log("eliminado") : newArr.push(arr[i]);
  }
  arrSelect = newArr;
}

function f(){

    $(".chk").each(function () {
       var datosRow = table.row($(this).parents('tr')).data();
       console.log(table.row($(this).closest('tr').index()));
       //var l = table.row($(this).parents('tr')).remove().draw();
       //console.log(l);
       console.log(datosRow);
    });
}
