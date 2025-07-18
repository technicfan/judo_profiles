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

let own0 = 0,
    own1 = 0,
    own2 = 0,
    own3 = 0,
    own4 = 0,
    own5 = 0,
    deleted_own_techniques = [];

function add_own(field, context = null) {
    switch (field) {
        case 0:
            own0 += 1;
            var number = own0;
            break;
        case 1:
            own1 += 1;
            var number = own1;
            break;
        case 2:
            own2 += 1;
            var number = own2;
            break;
        case 3:
            own3 += 1;
            var number = own3;
            break;
        case 4:
            own4 += 1;
            var number = own4;
            break;
        case 5:
            own5 += 1;
            var number = own5;
            break;
    }
    if (number <= 3) {
        let own_technique_html =
            `
        <div class="own_technique text-center" id="own` +
            field +
            "_" +
            number +
            `">
            <table style="table-layout: fixed;">
                <tr>
                    <td>
                        <select id="own` +
            field +
            "_d" +
            number +
            `" class="direction form-select form-select-sm d-inline m-1" style="width: fit-content;" required>
                            <option value="" selected>${gettext("Stance")}</option>
                            <option value="l">${gettext("Left")}</option>
                            <option value="r">${gettext("Right")}</option>
                        </select>
                        <select id="own` +
            field +
            "_t" +
            number +
            `" class="technique form-select form-select-sm d-inline m-1" style="width: fit-content;">
                            <option value="" selected>${gettext("Technique")}</option>` +
            stechniques +
            `</select>
                    </td>
                </tr>
                <tr>
                    <td>
                        <select id="own` +
            field +
            "_pl" +
            number +
            `" class="select_position left form-select form-select-sm d-inline m-1" style="width: fit-content;" required>
                            <option value="" selected>${gettext("left")}</option>
                        </select>
                        <select id="own` +
            field +
            "_pr" +
            number +
            `" class="select_position right form-select form-select-sm d-inline m-1" style="width: fit-content;" required>
                            <option value="" selected>${gettext("right")}</option>
                        </select>
                        <select id="own` +
            field +
            "_s" +
            number +
            `" class="state form-select form-select-sm d-inline m-1" style="width: fit-content;" required>
                            <option value="" selected>${gettext("State")}</option>
                            <option value="0">${gettext("Stable_short")}</option>
                            <option value="1">${gettext("Trainig_short")}</option>
                            <option value="2">${gettext("Learn_short")}</option>
                        </select>
                        <button id="own` +
            field +
            "_b" +
            number +
            `" class="btn btn-danger btn-sm" onclick="remove_own(` +
            field +
            `, this)">${gettext("Delete")}</button>
                    </td>
                </tr>
            </table>
            <hr class="my-1">
        </div>
        `;

        $("#own" + field).append(own_technique_html);
        var div = document.getElementById("own" + field + "_" + number);
        document
            .getElementById("own" + field + "_" + number)
            .querySelectorAll("button")
            .forEach((button) => {
                button.addEventListener("click", (event) => {
                    event.preventDefault();
                });
            });
        document.querySelectorAll(".move").forEach((position) => {
            if (position.classList.contains("active")) {
                $(
                    "#" +
                    "own" +
                    field +
                    "_" +
                    "p" +
                    position.className[0] +
                    number,
                ).append(
                    '<option value="' +
                    position.dataset.number +
                    '">' +
                    position.dataset.number +
                    "</option>",
                );
            }
        });
        if (context != null) {
            div.setAttribute("data-id", context["id"]);
            div.querySelector(".direction").value = context["side"];
            div.querySelector(".technique").value = context["technique"];
            div.querySelector(".left").value = context["left"];
            div.querySelector(".right").value = context["right"];
            div.querySelector(".state").value = context["state"];
        }
    } else {
        switch (field) {
            case 0:
                own0 -= 1;
                break;
            case 1:
                own1 -= 1;
                break;
            case 2:
                own2 -= 1;
                break;
            case 3:
                own3 -= 1;
                break;
            case 4:
                own4 -= 1;
                break;
            case 5:
                own5 -= 1;
                break;
        }
    }
}

function remove_own(field, element) {
    var number = element.id.slice(-1);
    if (
        document
            .getElementById("own" + field + "_" + number)
            .getAttribute("data-id")
    ) {
        deleted_own_techniques.push(
            parseInt(
                document
                    .getElementById("own" + field + "_" + number)
                    .getAttribute("data-id"),
            ),
        );
    }
    $("#own" + field + "_" + number).remove();
    if (number < 3) {
        document
            .getElementById("own" + field)
            .querySelectorAll("div")
            .forEach((div) => {
                var curr_number = parseInt(div.id.slice(-1));
                div.querySelectorAll("select, button").forEach((select) => {
                    if (curr_number > number) {
                        select.id = select.id.slice(0, -1) + (curr_number - 1);
                    }
                });
                if (curr_number > number) {
                    div.id = div.id.slice(0, -1) + (curr_number - 1);
                }
            });
    }

    switch (field) {
        case 0:
            own0 -= 1;
            break;
        case 1:
            own1 -= 1;
            break;
        case 2:
            own2 -= 1;
            break;
        case 3:
            own3 -= 1;
            break;
        case 4:
            own4 -= 1;
            break;
        case 5:
            own5 -= 1;
            break;
    }
}
