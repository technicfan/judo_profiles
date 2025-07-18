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

function get_positions() {
    var pos = [];
    document.querySelectorAll(".move").forEach((position) => {
        if (position.getAttribute("data-id")) {
            var action = "update";
            var id = parseInt(position.getAttribute("data-id"));
        } else {
            var action = "add";
            var id = null;
        }
        if (position.classList.contains("active")) {
            let x = getRelative(position);
            pos.push({
                number: parseInt(position.dataset.number),
                side: position.classList.contains("l"),
                x: x[1],
                y: x[0],
                action: action,
                id: id,
            });
        } else if (id != null) {
            pos.push({
                action: "delete",
                id: id,
            });
        }
    });
    return pos;
}

function get_own_techniques() {
    var own_techniques = [];
    document.querySelectorAll(".own_technique").forEach((div) => {
        let side = div.querySelector(".direction").value == "l";
        let technique = div.querySelector(".technique").value;
        let left = div.querySelector(".select_position.left").value;
        let right = div.querySelector(".select_position.right").value;
        let state = div.querySelector(".state").value;
        let direction = div.id[3];
        if (technique && left && right && state && direction) {
            if (div.getAttribute("data-id")) {
                var action = "update";
                var id = parseInt(div.getAttribute("data-id"));
            } else {
                var action = "add";
                var id = null;
            }
            own_techniques.push({
                side: side,
                technique: parseInt(technique),
                left: parseInt(left),
                right: parseInt(right),
                state: parseInt(state),
                direction: parseInt(direction),
                action: action,
                id: id,
            });
        }
    });
    deleted_own_techniques.forEach((id) => {
        own_techniques.push({
            action: "delete",
            id: id,
        });
    });
    return own_techniques;
}

function get_rank_items() {
    var rank_items = [];
    document.querySelectorAll(".rank_item").forEach((div) => {
        let type = div.classList[0];
        if (div.getAttribute("data-id")) {
            var action = "update";
            var id = parseInt(div.getAttribute("data-id"));
        } else {
            var action = "add";
            var id = null;
        }
        if (type == "combination") {
            let technique1 = div.querySelector(".technique1").value;
            let technique2 = div.querySelector(".technique2").value;
            if (technique1 && technique2) {
                rank_items.push({
                    number: parseInt(div.id.slice(-1)),
                    technique1: parseInt(technique1),
                    technique2: parseInt(technique2),
                    action: action,
                    type: type,
                    id: id,
                });
            }
        } else {
            let technique = div.querySelector(".technique").value;
            if (technique) {
                rank_items.push({
                    number: parseInt(div.id.slice(-1)),
                    technique: parseInt(technique),
                    action: action,
                    type: type,
                    id: id,
                });
            }
        }
    });
    deleted_rank_items.forEach((item) => {
        rank_items.push({
            action: "delete",
            type: item["type"],
            id: item["id"],
        });
    });
    return rank_items;
}

function get_data() {
    let name = document.getElementById("name").value;
    let last_name = document.getElementById("last_name").value;
    let year = document.getElementById("year").value;
    let weight = document.getElementById("weight").value;
    let user = document.getElementById("user")
        ? document.getElementById("user").value
        : null;
    let left = document.getElementById("side_left").checked;
    let right = document.getElementById("side_right").checked;
    var side = null;
    if (left && right) {
        var side = 3;
    } else if (left) {
        var side = 1;
    } else if (right) {
        var side = 2;
    }
    return {
        name: name,
        last_name: last_name,
        year: year,
        weight: weight,
        user: user ? parseInt(user) : null,
        side: side,
        positions: get_positions(),
        own_techniques: get_own_techniques(),
        rank_items: get_rank_items(),
    };
}

function post_data(action = "redirect") {
    var data = get_data();
    data["changed"] = JSON.stringify(data) != JSON.stringify(original_data);
    data["action"] = action;
    const request = new Request(window.location.href, {
        method: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN,
            "Content-Type": "application/json; charset=utf-8",
        },
        mode: "same-origin",
        body: JSON.stringify(data),
    });
    fetch(request).then((response) => {
        location.href = response.url;
    });
}

const original_data = get_data();
