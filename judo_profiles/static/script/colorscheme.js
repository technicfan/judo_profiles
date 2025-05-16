const dark_mode = window.matchMedia("(prefers-color-scheme: dark)");
const button = document.getElementById("theme-selector");

function set_color_scheme(theme) {
    var other = theme == "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-bs-theme", theme);
    document.querySelectorAll(`.btn-${other}`).forEach((btn) => {
        btn.classList.remove(`btn-${other}`);
        btn.classList.add(`btn-${theme}`);
    });
}

function auto_color_scheme(value) {
    set_color_scheme(value.matches ? "dark" : "light");
}

function change_color_scheme(theme) {
    switch (theme) {
        case "auto":
            localStorage.setItem("theme", "auto");
            button.innerHTML = "Auto";
            auto_color_scheme(dark_mode);
            dark_mode.addEventListener("change", auto_color_scheme);
            break;
        case "light":
            localStorage.setItem("theme", "light");
            dark_mode.removeEventListener("change", auto_color_scheme);
            button.innerHTML = "Light";
            set_color_scheme(theme);
            break;
        case "dark":
            localStorage.setItem("theme", "dark");
            dark_mode.removeEventListener("change", auto_color_scheme);
            button.innerHTML = "Dark";
            set_color_scheme(theme);
            break;
    }
}

function theme_selector_callback() {
    if (localStorage.getItem("theme")) {
        var theme = localStorage.getItem("theme");
    } else {
        var theme = "auto";
    }
    switch (theme) {
        case "auto":
            change_color_scheme("dark");
            break;
        case "light":
            change_color_scheme("auto");
            break;
        case "dark":
            change_color_scheme("light");
            break;
    }
}

if (localStorage.getItem("theme")) {
    change_color_scheme(localStorage.getItem("theme"));
} else {
    change_color_scheme("auto");
}
