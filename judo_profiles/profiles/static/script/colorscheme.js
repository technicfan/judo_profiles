const dark_mode = window.matchMedia('(prefers-color-scheme: dark)')
const button = document.getElementById("theme-selector")

function auto_color_scheme(value){
    if (value.matches){
        document.documentElement.setAttribute("data-bs-theme", "dark")
    } else {
        document.documentElement.setAttribute("data-bs-theme", "light")
    }
}

function set_color_scheme(theme){
    switch(theme){
        case "auto":
            localStorage.setItem("theme", "auto")
            button.innerHTML = "Auto"
            auto_color_scheme(dark_mode)
            dark_mode.addEventListener("change", auto_color_scheme)
            break
        case "light":
            localStorage.setItem("theme", "light")
            dark_mode.removeEventListener("change", auto_color_scheme)
            button.innerHTML = "Light"
            document.documentElement.setAttribute("data-bs-theme", "light")
            break
        case "dark":
            localStorage.setItem("theme", "dark")
            dark_mode.removeEventListener("change", auto_color_scheme)
            button.innerHTML = "Dark"
            document.documentElement.setAttribute("data-bs-theme", "dark")
            break
    }
}

function change_color_theme(){
    if (localStorage.getItem("theme")){
        var theme = localStorage.getItem("theme")
    } else {
        var theme = "auto"
    }
    switch(theme){
        case "auto":
            set_color_scheme("dark")
            break
        case "light":
            set_color_scheme("auto")
            break
        case "dark":
            set_color_scheme("light")
            break
    }
}

document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("theme")){
        set_color_scheme(localStorage.getItem("theme"))
    } else {
        set_color_scheme("auto")
    }
})
