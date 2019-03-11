//kliknuti proiz
var proizvod;

// UBACI PROIZVOD U KORPU
$(document).on('click', '#addToCart button', function() {
       var product_name = $(this).attr("id");
       $.ajax({
            url:'/addToCart',
            method:'POST',
            data:{ product_name:product_name },

            success:function(data) {
               alert(product_name + " je/su dodat/a/e u korpu!");
            }
       });

});

// Obrisi PROIZVOD
$(document).on('click', '#removeArticle button', function() {
       var name = ($(this).attr("id")).substring(3);

       $.ajax({
            url:'/getArticleFromDb',
            method:'POST',
            data:{ name : name },

            success:function(data) {
               $(document).on('click', '#izbrisiProizvod #btnRmv', function() {
                    $.ajax({
                        url:'/removeArticle',
                        method:'POST',
                        data:{ name : data.name },

                        success:function(data) {
                             alert(name + " je/su obrisan/a/e iz baze proizvoda!");
                        }
                    });
               });
            }
       });


});

// izmeni PROIZVOD
$(document).on('click', '#changeArticle button', function() {
      name = ($(this).attr("id")).substring(3);

      $.ajax({
            url:'/getArticleFromDb',
            method:'POST',
            dataType: 'json',
            data:{ name : name },

            success:function(data) {
                $("#izmNaziv").val(data.name);
                $("#izmCena").val(data.price);
                $("#izmOpis").val(data.desc);
                $("#izmSliku").val(data.image);
                $("#izmDostupan").val(data.is_available);
                var id = data.id;

                // Dodaj izmenjeni proizvod u bazu
                $(document).on('click', '#izmeniProizvod #btnUpd', function() {
                       var newName = $("#izmNaziv").val();
                       var price = $("#izmCena").val();
                       var desc = $("#izmOpis").val();
                       var image = $("#izmSliku").val();
                       var is_available = $("#izmDostupan").val();

                       $.ajax({
                            url:'/saveChangesOnArticle',
                            method:'POST',
                            data:{ id : id, name : newName, price : price, desc : desc, image : image, is_available : is_available },

                            success:function(data) {
                                $("#izmProizvod").modal('toggle');
                                alert("Uspesno ste izmenili proizvod!");
                                window.location = "/";
                            }
                      });
                });
            }
      });

});


//POSAO ZA STUDENTE
function prijavaZaPosao(){
    var nameCand = $("#name").val();
    var surnameCand = $("#surname").val();
    var emailCand = $("#email").val();
    var messageCand = $("#message").val();
    var zanimanjeCand = document.getElementById("zanimanje").value;
    var godista = document.getElementsByName("godiste");
    var faxi = document.getElementsByName("faculty");
    var fax="ok";
    var godiste=0;

    for (var i=0;i<faxi.length;i++){
        if (faxi[i].selected){
            fax=faxi[i].value;
        }
    }
     for (var i=0;i<godista.length;i++){
        if (godista[i].selected){
            godiste=godista[i].value;
        }
    }

    var inputs = ['name', 'surname', 'email', 'message'];

    $.ajax({
        url:'/apply_for_student_job',
        method:'POST',
        data: {first_name : nameCand, last_name : surnameCand, email : emailCand, message : messageCand, profession : zanimanjeCand, birth_year : godiste, faculty : fax},

        success:function(data) {
            $("#studentBut").modal('toggle');
            alert("Uspesno ste se prijavili za posao, neko od nasih operatera ce vas kontaktirati u najkracem mogucem roku!");
            for (var i = 0; i < inputs.length; i++) {
                $("#" + inputs[i]).val('');
            }
        }
    });
}

//POSAO OPERATERA
function prijavaZaPosaoOp(){
    var nameCand = $("#nameOp").val();
    var surnameCand = $("#surnameOp").val();
    var emailCand = $("#emailOp").val();
    var messageCand = $("#messageOp").val();
    var godista= document.getElementsByName("godisteOp");
    var godiste=0;

     for (var i=0;i<godista.length;i++){
        if (godista[i].selected){
            godiste=godista[i].value;
        }
     }

     var inputs = ['nameOp', 'surnameOp', 'emailOp', 'messageOp'];

     $.ajax({
        url:'/apply_for_operator_job',
        method:'POST',
        data: {first_name : nameCand, last_name : surnameCand, email : emailCand, message : messageCand, birth_year : godiste},

        success:function(data) {
            $("#operaterBut").modal('toggle');
            alert("Uspesno ste se prijavili za posao operatera, neko od nasih kolega/nica ce vas kontaktirati u najkracem mogucem roku!");
            // ocisti polja nakon ubacivanja prijave u bazu
            for (var i = 0; i < inputs.length; i++) {
                $("#" + inputs[i]).val('');
            }
        }
    });

}

function posaoProfi(){
    alert("Popunjena mesta za trazeni posao. Pokusajte neki drugi put.");
}

// Zavrsi kupovinu
function kupovina(){

        var racun = $("#racun span").text();
        var d = new Date();
        var vreme = d.getDate() + ". " + (d.getMonth()+1) + ". " + d.getFullYear() + ". godine u " + d.getHours() + ":" + d.getMinutes();

        console.log(racun + " i " + vreme);

        $.ajax({
             url:'/complete_buy',
             method:'POST',
             data:{ price: racun, time: vreme },

             success:function(data) {
                alert(data.notice);
                window.location = "/";
             }
        });
}

// Zavrsi kupovinu
function odustanak(){

        console.log("Odustajem!");

        $.ajax({
             url:'/refuse_buy',
             method:'POST',

             success:function(data) {
                alert(data.notice);
                window.location = "/";
             }
        });
}




// UZMI PODATKE IZ UPITNIKA ZA OSTAVLJANJE UTISAKA
function ajaxZahtev(){

        var cene = document.getElementsByName("cena");
        var kvaliteti = document.getElementsByName("kvalitet");
        var brzine = document.getElementsByName("brzina");
        var komentar = $("#message").val();

        var cena = NaN;
        for (var i=0; i<5;i++){
            if (cene[i].checked){
                cena=cene[i].value
            }
        }
        var kvalitet = NaN;
        for (var i=0; i<5;i++){
            if (kvaliteti[i].checked){
                kvalitet=kvaliteti[i].value
            }
        }
        var brzina = NaN;
        for (var i=0; i<5;i++){
            if (brzine[i].checked){
                brzina=brzine[i].value
            }
        }

        $.ajax({
             url:'/post_impression',
             method:'POST',
             data:{ price: cena, quality: kvalitet, speed: brzina, comment: komentar },

             success:function(data) {
                alert(data.notice);
             }
        });
}
// IZBOR KATEGORIJE
$(document).on('click', '.list-group button', function() {

    articles = document.getElementsByClassName("article");
    services = document.getElementsByClassName("service");

    if (this.id == "articles") {
        $('#' + this.id).hide();
        $("#services").show();

        for(var i = 0; i < articles.length; i++) {
            $(articles[i]).show();
        }
        for (var i = 0; i < services.length; i++) {
            $(services[i]).hide();
        }
    }
    else {
        $('#' + this.id).hide();
        $("#articles").show();

        for(var i = 0; i < services.length; i++) {
            $(services[i]).show();
        }
        for (var i = 0; i < articles.length; i++) {
            $(articles[i]).hide();
        }
    }
    $('.pagination').hide();
});

$(document).ready(function() {
    first = document.getElementsByClassName("1");
    second = document.getElementsByClassName("2");

    for(var i = 0; i < first.length; i++) {
        $('.1').show();
    }
    for (var i = 0; i < second.length; i++) {
        $('.2').hide();
    }

    $('.pagination').show();
});
$(document).on('click', '.pagination li a', function() {
    first = document.getElementsByClassName("1");
    second = document.getElementsByClassName("2");

    if (this.id == "1") {
        for(var i = 0; i < first.length; i++) {
            $('.1').show();
        }

        for (var i = 0; i < second.length; i++) {
            $('.2').hide();
        }
        $('.pagination').show();
    }
    else {
        for(var i = 0; i < second.length; i++) {
            $('.2').show();
        }
        for (var i = 0; i < first.length; i++) {
            $('.1').hide();
        }
        $('.pagination').show();
    }
});

//VALIDACIJA REGISTRACIJE
$(document).on('click', '#register',function () {
    var username = $("#usernameRg").val();

    var email = $("#emailRg").val();

    var password = $("#passwordRg").val();
    var passConf = $("#passwordConf").val();

    var address = $("#addressRg").val();

    var ph_num = $("#phoneRg").val();

    var first_name = $("#first_nameRg").val();
    var last_name = $("#last_nameRg").val();

    $.ajax({
        url:'/check_register',
        method:'POST',
        data: {username : username, email : email, password : password, passConf : passConf, address : address, ph_num : ph_num, first_name : first_name, last_name : last_name},

        success:function(data) {
               if (data.info == 'Korisnik vec postoji!') {
                   $("#invalidInput").html(data.info);
                   $("#invalidInput").css("display", "block");
               }
               else if (data.info == 'Lozinke se ne poklapaju!') {
                   $("#invalidInput").html(data.info);
                   $("#invalidInput").css("display", "block");
               }
               else {
                    $.ajax({
                        url:'/register',
                        method:'POST',
                        data: {id : data.info},
                        dataType: "html",
                        success:function(data) {
                            alert("Uspesno ste se registrovali! Dobrodosli kod Potrcka!")
                            window.location = "/";
                        }
                    });
               }
        }
    });
});

function validateFormPass(){
    var sifra = $("#newPassAgn").val();
    var sifraComf = $("#newPass").val();

    if (sifra != sifraComf){
        alert("Sifre se ne poklapaju!");
        return false;
    }
}
// VALIDACIJA PRIJAVE
$(document).on('click', '#logIn', function() {
       var user = $("#usernameLg").val();
       var pass = $("#passwordLg").val();

       if (user != null && pass != null) {
           $.ajax({
            url:'/check_login',
            method:'POST',
            data:{ username : user, password : pass },

            success:function(data) {
               if (data.info == 'Korisnik ne postoji!') {
                   $("#invalidUsername").html(data.info);
                   $("#invalidUsername").css("display", "block");
               }
               else if (data.info == 'Uneli ste pogresnu lozinku!') {
                   $("#invalidPassword").html(data.info);
                   $("#invalidPassword").css("display", "block");
               }
               else {
                    $.ajax({
                        url:'/login',
                        method:'POST',
                        data: {id : data.info},
                        dataType: "html",
                        success:function(data) {
                            alert("Uspesno ste se prijavili!")
                            window.location = "/";
                        }
                    });
               }
            }
         });
       }
});


