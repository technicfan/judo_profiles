let special = 0,
    ground = 0,
    combination = 0,
    deleted_rank_items = [];

function get_type(type) {
    if (type === "0") {
        return "ground";
    } else if (type == "1") {
        return "special";
    } else {
        return type;
    }
}

function add_rank_item(raw_type, context = null) {
    var type = get_type(raw_type);
    switch (type) {
        case "special":
            special += 1;
            var number = special;
            var html =
                `
            <div class="special rank_item" id="special_item` +
                number +
                `">
                <p class="d-inline"><b>` +
                number +
                `</b></p>
                <select id="special_t` +
                number +
                `" class="technique form-select d-inline" style="width: fit-content;" required>
                    <option value="" selected>${gettext("Technique")}</option>` +
                techniques +
                `</select>
                <button id="special_b` +
                number +
                `" class="btn btn-danger btn-sm" onclick="remove_rank('special', this)">${gettext("Delete")}</button>
            </div>
            `;
            break;
        case "ground":
            ground += 1;
            var number = ground;
            var html =
                `
            <div class="ground rank_item" id="ground_item` +
                number +
                `">
                <p class="d-inline"><b>` +
                number +
                `</b></p>
                <select id="ground_t` +
                number +
                `" class="technique form-select d-inline" style="width: fit-content;" required>
                    <option value="" selected>${gettext("Technique")}</option>` +
                gtechniques +
                `</select>
                <button id="ground_b` +
                number +
                `" class="btn btn-danger btn-sm" onclick="remove_rank('ground', this)">${gettext("Delete")}</button>
            </div>
            `;
            break;
        case "combination":
            combination += 1;
            var number = combination;
            var html =
                `
            <div class="combination rank_item" id="combination_item` +
                number +
                `">
                <p class="d-inline"><b>` +
                number +
                `</b></p>
                <select id="combination_t1` +
                number +
                `" class="technique1 form-select d-inline" style="width: fit-content;" required>
                    <option value="" selected>1. ${gettext("Technique")}</option>` +
                techniques +
                `</select>
                <select id="combination_t2` +
                number +
                `" class="technique2 form-select d-inline" style="width: fit-content;" required>
                    <option value="" selected>2. ${gettext("Technique")}</option>` +
                techniques +
                `</select>
                <button id="combination_b` +
                number +
                `" class="btn btn-danger btn-sm" onclick="remove_rank('combination', this)">${gettext("Delete")}</button>
            </div>
            `;
            break;
    }
    if (number <= 4) {
        $("#" + type + number).append(html);
        document.getElementById(type + number).classList.remove("d-none");
        var div = document.getElementById(type + "_item" + number);
        div.querySelector("button").addEventListener("click", (event) => {
            event.preventDefault();
        });

        if (context != null) {
            div.setAttribute("data-id", context["id"]);
            if (type == "combination") {
                div.querySelector(".technique1").value = context["technique1"];
                div.querySelector(".technique2").value = context["technique2"];
            } else {
                div.querySelector(".technique").value = context["technique"];
            }
        }
    } else {
        switch (type) {
            case "special":
                special -= 1;
                break;
            case "ground":
                ground -= 1;
                break;
            case "combination":
                combination -= 1;
                break;
        }
    }
}

function remove_rank(type, element) {
    var number = element.id.slice(-1);
    if (
        document.getElementById(type + "_item" + number).getAttribute("data-id")
    ) {
        deleted_rank_items.push({
            type: type,
            id: parseInt(
                document
                    .getElementById(type + "_item" + number)
                    .getAttribute("data-id"),
            ),
        });
    }
    $("#" + type + "_item" + number).remove();
    if (number < 4) {
        document.querySelectorAll("." + type + ".rank_item").forEach((div) => {
            var curr_number = parseInt(div.id.slice(-1));
            div.querySelectorAll("select, button").forEach((select) => {
                if (curr_number > number) {
                    select.id = select.id.slice(0, -1) + (curr_number - 1);
                }
            });
            if (curr_number > number) {
                let id = div.id;
                $("#" + type + (curr_number - 1)).append(div);
                var div = document.getElementById(id);
                div.querySelector("p").innerHTML = "<b>" + (curr_number - 1) + "</b>";
                div.id = div.id.slice(0, -1) + (curr_number - 1);
            }
        });
    }

    switch (type) {
        case "special":
            document.getElementById(type + special).classList.add("d-none");
            special -= 1;
            break;
        case "ground":
            document.getElementById(type + ground).classList.add("d-none");
            ground -= 1;
            break;
        case "combination":
            document.getElementById(type + combination).classList.add("d-none");
            combination -= 1;
            break;
    }
}
