// Añade el siguiente código en tu página o archivo JavaScript

// Esta función se ejecutará cuando se cargue la página
window.onload = function () {
    // Verifica si el usuario intenta navegar hacia atrás
    window.onpageshow = function (event) {
        if (event.persisted) {
            // Si se detecta un intento de navegación hacia atrás, redirige a otra página
            window.location.href = "{{url_for('login')}}";
        }
    };

    // Esta función se ejecutará cuando el usuario intente navegar hacia atrás
    window.onbeforeunload = function () {
        // Establece un flag para indicar que el usuario está intentando navegar hacia atrás
        sessionStorage.setItem("intentando_retroceder", "true");
    };
};

// Esta función se ejecutará cuando la página sea recargada
window.onunload = function () {
    // Si se detecta que el usuario está intentando retroceder, redirige a otra página
    if (sessionStorage.getItem("intentando_retroceder")) {
        window.location.href = "{{url_for('login')}}";
    }
};
