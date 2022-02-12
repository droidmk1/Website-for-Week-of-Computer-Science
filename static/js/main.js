const loggedOutLinks = document.querySelectorAll('.logged-out')
const loggedInLinks = document.querySelectorAll('.logged-in')
var NombreUsuario = ''
var MandarForm = "0"

//login check
const loginCheck = user => {
    if(user) {
        loggedInLinks.forEach(link => link.style.display = 'block');
        loggedOutLinks.forEach(link => link.style.display = 'none');
        console.log('hola estoy aqui')
        console.log(NombreUsuario);
        if(MandarForm == "1"){
            // window.location.href = '/'
            $("#login-email").val(NombreUsuario)
            $("#login-form").submit()
            MandarForm = "0"
            console.log('en if valor variable')
            console.log(MandarForm)
        }
        else {
            console.log('en else valor variable')
            console.log(MandarForm)
        }
    } else {
        loggedInLinks.forEach(link => link.style.display = 'none');
        loggedOutLinks.forEach(link => link.style.display = 'block');
    }
}

const signupForm = document.querySelector('#signup-form');

signupForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const email = document.querySelector('#signup-email').value;
    const password = document.querySelector('#signup-password').value;
    //console.log(email, password)

    auth
        .createUserWithEmailAndPassword(email, password)
        .then(UserCredential => {
            //clear the form
            signupForm.reset();
            // signupForm.querySelector('.error').innerHTML = '';

            //close the modal
            $('#signupModal').modal('hide');
            MandarForm = "1"

            //console.log('sign up')
        })
        .catch(err => {
            signupForm.querySelector('.errorForm').innerHTML = err.message;
        });
});

// signin
const signinform = document.querySelector('#login-form');

signinform.addEventListener('submit', e => {
    e.preventDefault();
    const email = document.querySelector('#login-email').value;
    const password = document.querySelector('#login-password').value;
    //console.log(email, password)

    auth
        .signInWithEmailAndPassword(email, password)
        .then(UserCredential => {
            //clear the form
            signinform.reset();
            // signupForm.querySelector('.error').innerHTML = '';

            //close the modal
            $('#signinModal').modal('hide');
            MandarForm = "1"

            //console.log('sign in')
        })
        .catch(err => {
            signinform.querySelector('.errorForm').innerHTML = err.message;
        });
})

// Google Login
const googleButton = document.querySelector("#googleLogin")
googleButton.addEventListener('click', e => {
    //console.log('click google')
    const provider = new firebase.auth.GoogleAuthProvider();
    auth.signInWithPopup(provider)
        .then(result => {
            // console.log('google sign in')
            MandarForm = "1"
            // console.log('valor google mandarform')
            // console.log(MandarForm)
            $("#login-email").val(NombreUsuario)
            $("#login-form").submit()
        })
        .catch(err => {
            console.log(err)
        })

    //close the modal
    $('#signinModal').modal('hide');
})

// LogOut
const logout = document.querySelector("#logout");

logout.addEventListener('click', e => {
    e.preventDefault();
    auth.signOut().then(() => {
        console.log('log out')
        console.log('borrando nombre usuario')
        NombreUsuario=''
        MandarForm="0"
        console.log('valor final nombreusuario')
        console.log(NombreUsuario);
        console.log('valor final mandarform')
        console.log(MandarForm)
        location.href = '/logout';
    })
})


//Events user
auth.onAuthStateChanged(user =>{
    if(user) {
        console.log('estado usuario: sign in')
        NombreUsuario = user.email;
        loginCheck(user);
    } else {
        console.log('estado usuario: log out')
        loginCheck(user);
    }
})


// SCROLL ANIMATION
function mostrarScroll(){
    var html = document.getElementsByTagName("html")[0];
    var animado = document.getElementsByClassName("animado");
    // console.log(`Elemento animado: ${animado}`);
    // console.log(animado);
    document.addEventListener("scroll", function(){
        var topVentana = html.scrollTop; //Para saber cuanto se ha bajado el scroll
        // console.log(`En que parte de la ventana estamos ${topVentana}`);
        
        for( i=0 ; i< animado.length; i++){

            let posicion = animado[i].getBoundingClientRect(); //PARA CONOCER LA POSICON DEL ELEMENTO
            var topelemenAparece = posicion.top;//Para calcular la distancia del top de la ventana hasta el elemento
            // console.log(`Distancia del top al elemento: ${topelemenAparece}`); 
                if(topelemenAparece +200 < topVentana){
                    animado[i].style.opacity = 1;
                    animado[i].classList.add("mostrarArriba");
                }//endif
            }//endfor
        }//endfunction
    )//endEventListener
}
mostrarScroll();

//SCROOLL ANIMATION: solo para el contenedor del titulo de CC , pues el momento de aparecer es distinto 
//misma funcionalidad, diferente algoritmo
window.onscroll = function(){miFuncion()};
var titulo_cc = document.getElementById("contenedor1-0");
var distancia_titulo;
function miFuncion(){
    position = titulo_cc.getBoundingClientRect();
    distancia_titulo = window.innerHeight - position.top;
    console.log(distancia_titulo);
    if(distancia_titulo >= 50){
        titulo_cc.style.opacity  = 1;
    }
}


//FUNCION PARA FIJAR EL NAVBAR
function fijar(){
    var html = document.getElementsByTagName("html")[0];
    var nav = document.getElementsByClassName("navbar");

    document.addEventListener("scroll", function(){
        var topVentana = html.scrollTop; //Para saber cuanto se ha bajado el scroll
        
        for( i=0 ; i< nav.length; i++){

            let posicion = nav[i].getBoundingClientRect(); //PARA CONOCER LA POSICON DEL ELEMENTO
            var topelemenAparece = posicion.top;//Para calcular la distancia del top de la ventana hasta el elemento
                if(1 < topVentana){
                    nav[i].classList.add("fijar");
                    nav[i].style.background = "rgba(0, 0, 0, 0.514)";
                }//endif
                else{
                    nav[i].classList.remove("fijar");
                    nav[i].style.backgroundColor = "#0057A3";
                }
            }//endfor
        }//endfunction
    )//endEventListener
}
fijar();






//TYPING
var typed = new Typed(".typing", {
    strings: ["DATA SCIENCE", "BLOCKCHAIN", "NETWORKING", "MACHINE LEARNING", "BIG DATA"],
    typeSpeed: 120,
    backSpeed: 50,
    loop: true
});

