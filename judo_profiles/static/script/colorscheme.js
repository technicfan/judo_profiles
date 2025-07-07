// Copyright (C) 2025 technicfan
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

const dark_mode = window.matchMedia("(prefers-color-scheme: dark)");
const icon = document.getElementById("theme-selector").children[0];

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
            icon.className = "bi bi-circle-half";
            auto_color_scheme(dark_mode);
            dark_mode.addEventListener("change", auto_color_scheme);
            break;
        case "light":
            localStorage.setItem("theme", "light");
            dark_mode.removeEventListener("change", auto_color_scheme);
            icon.className = "bi bi-sun-fill";
            set_color_scheme(theme);
            break;
        case "dark":
            localStorage.setItem("theme", "dark");
            dark_mode.removeEventListener("change", auto_color_scheme);
            icon.className = "bi bi-moon-fill";
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
