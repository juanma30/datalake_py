jQuery(".onlynumbers").on('input', function (evt) {
  jQuery(this).val(jQuery(this).val().replace(/[^0-9]/g, ''));
});
jQuery(".onlytext").on('input', function (evt) {
   jQuery(this).val(jQuery(this).val().replace(/[^a-zA-Z0-9 ]/g, ''));
});

var dataesp = {
  "sProcessing":     "Cargando...",
  "sLengthMenu":     "Mostrar _MENU_ registros",
  "sZeroRecords":    "No se encontraron resultados",
  "sEmptyTable":     "No hay datos",
  "sInfo":           "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
  "sInfoEmpty":      "Mostrando registros del 0 al 0 de un total de 0 registros",
  "sInfoFiltered":   "(filtrado de un total de _MAX_ registros)",
  "sInfoPostFix":    "",
  "sSearch":         "Buscar:",
  "sUrl":            "",
  "sInfoThousands":  ",",
  "sLoadingRecords": "Cargando...",
  "oPaginate": {
    "sFirst":    "Primero",
    "sLast":     "Último",
    "sNext":     "Siguiente",
    "sPrevious": "Anterior"
  },
  "oAria": {
    "sSortAscending":  ": Activar para ordenar la columna de manera ascendente",
    "sSortDescending": ": Activar para ordenar la columna de manera descendente"
  }
};
//guardar los datos del formulario
$("#saveUserForm").submit(function (event) {
  event.preventDefault();
  var valid;
  valid = validateForm();
  if(valid) {
    $.ajax({
      url:  $(this).attr("action"),
      type: $(this).attr("method"),
      data: new FormData($(this)[0]),
      contentType: false,
      processData: false,
      success: function(response) {
        if (response['code'] == 0) {
          window.location.reload();
        }else{
          $('#newUsuario').removeClass('alert-success');
          $('#newUsuario').addClass('alert-warning');
          $('#newUsuario').show();
          $('#newUsuario').html(response['msg']);
        }
      },
      error: function(data){
        console.error('invalid data');
      }
    });
  }


});

$('#newElemnt').click(function(){
  $('#passsection').hide();
  $('#checkpassword').checked(false);
  document.getElementById('operation').value ='new';
  //document.getElementById('deleteElement').value = 'newUsuario';
  document.getElementById('idUsuario').value = 0;
  $('#newUsuario').hide();
  document.getElementById('name').value = '';
  document.getElementById('lastName').value = '';
  document.getElementById('username').value = '';
  document.getElementById('password').value = '';
  document.getElementById('repeatPasword').value = '';
 
});
$('#checkpassword').click(function(){
  if($(this).is(":checked")){
   //habilitar los inputs
   inputDisableEnabled(false);
   
  }else{
   //desabilita los inputs
   inputDisableEnabled(true);

  }
});
//editar las consultas
$("#saveConsulta").submit(function (event) {
  event.preventDefault();
  if (validate()) {
    $.ajax({
          url:  $(this).attr("action"),
          type: $(this).attr("method"),
          data: new FormData($(this)[0]),
          contentType: false,
          processData: false,
          success: function(response) {
            $("#loader_screen").css("display", "none");
              if (response['code'] == 0) {
                $('#newAlert').removeClass('alert-warning');
                $('#newAlert').addClass('alert-success');
                $('#newAlert').show();
                $('#newAlert').html(response['msg']);
                setTimeout(function(){ $('.editElemnt').modal('toggle'); }, 2000);

              }else{
                $('#newAlert').removeClass('alert-success');
                $('#newAlert').addClass('alert-warning');
                $('#newAlert').show();
                $('#newAlert').html(response['msg']);
              }
          },
          error: function(data){
            console.error('invalid data');
          }
        });
  }else {
    $('#newAlert').removeClass('alert-success');
    $('#newAlert').addClass('alert-warning');
    $('#newAlert').show();
    $('#newAlert').html('Inserte un JSON valido.');
  }
});
document.getElementById("btnDelete").onclick = function() {deleteUser(document.getElementById('deleteElement').value)};
document.getElementById("newElemnt").onclick = function() {prepareEdit()};

function deleteUser(user) {
  $.ajax({
        url:  '/php/userData.php?user='+user,
        type: 'PUT',
        contentType: false,
        processData: false,
        success: function(response) {
          if(response.code == 1 ){
            $('#alertUser').show();
            $('#alertUser').html(response.msg);
          }else{
            window.location.reload();
          }
        },
        error: function(data){
          console.error('invalid data');
        }
      });
}
function prepareEdit(){
  inputDisableEnabled(false);
}

function inputDisableEnabled(valor){
  document.getElementById('password').disabled = valor;
  document.getElementById('repeatPasword').disabled = valor;
}
function getUser(elemnt){
  $('#passsection').show();
  $('#newUsuario').hide();
  let idUser =elemnt.dataset.edit;
  let rol =elemnt.dataset.rol;
  let paretChild =elemnt.parentElement.parentElement.children;
  let name = paretChild[1].textContent;
  let lastName = paretChild[2].textContent;
  let userName = paretChild[3].textContent;
  document.getElementById('operation').value ='edit';
  // document.getElementById('accion').innerHTML ='Editar' ;
  document.getElementById('name').value =name ;
  document.getElementById('lastName').value =lastName ;
  document.getElementById('username').value =userName ;
  document.getElementById('idUsuario').value =idUser ;
  document.getElementById('password').disabled = true;
  document.getElementById('repeatPasword').disabled = true;
  document.getElementById('role').value =parseInt(rol);
}
function getName(elemnt){
  let idUser =elemnt.dataset.delete;
  let name =elemnt.parentElement.parentElement.children[1].textContent;
  document.getElementById('nameModal').innerHTML = name;
  document.getElementById('deleteElement').value = idUser;
}
function validate(){
  let valid = false;
  let jsontext = document.getElementById('txtconsulta');
  if (jsontext.value.length > 0 && isValidJSON(jsontext.value)  ) {
     valid = true;
  }
 return valid;
}
function validateForm(){
  let valid = true;
    if($('#checkpassword').is(":checked")){
      let regex =  /^(?=.*\d)(?=.*[\u0021-\u002b\u003c-\u0040])(?=.*[A-Z])(?=.*[a-z])\S{8,16}$/;
      let password = document.getElementById('password');
      let repeatPasword = document.getElementById('repeatPasword');
      if(password.value != repeatPasword.value ){
        //la contrasnia no coinciden
        $('#newUsuario').removeClass('alert-success');
        $('#newUsuario').addClass('alert-warning');
        $('#newUsuario').show();
        $('#newUsuario').html('Las contraseñas no coinciden');
        valid = false;
        //console.log('no coinciden');
      }
      if (!regex.test(password.value)) {
        //console.log('error de formato');
        $('#newUsuario').removeClass('alert-success');
        $('#newUsuario').addClass('alert-warning');
        $('#newUsuario').show();
        $('#newUsuario').html('La contraseña debe tener al menos 8 dígitos una mayúscula, una minúscula, un número y un carácter especial.');
        valid = false;
      }
    }
    console.log(valid);
 return valid;
}
function isValidJSON(string) {
  try {
    JSON.parse(string);
  } catch (e) {
    return false;
  }

  return true;
}
