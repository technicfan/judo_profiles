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

// disable submitting for unwanted buttons
document.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", (event) => {
        event.preventDefault();
    });
});

// only post if form is valid
document.querySelector("#profile_form").addEventListener("submit", (event) => {
    event.preventDefault();
    if (document.activeElement.dataset.type) {
        post_data(document.activeElement.dataset.type);
    } else {
        post_data();
    }
});

// Positions
let delete_mode = false,
    move = null;
document.querySelectorAll(".position.option").forEach((element) => {
    element.addEventListener("mousedown", mouseDownOpt);
});

function mouseDownOpt(e) {
    if (move != null) {
        mouseDownDoc(e);
    }
    let target = e.target;
    move = document.getElementById(getMatchingId(target.id));
    target.classList.add("active");
    image.addEventListener("mousedown", mouseDownImg);
    document.addEventListener("mousedown", mouseDownDoc);
}

function mouseDownDoc(e) {
    if (move != null) {
        if (
            e.target.id != "image" &&
            e.target.id != getMatchingId(move.id) &&
            !move.classList.contains("active")
        ) {
            document
                .getElementById(getMatchingId(move.id))
                .classList.remove("active");
            image.removeEventListener("mousedown", mouseDownImg);
        }
        if (e.target.id != getMatchingId(move.id)) {
            document.removeEventListener("mousedown", mouseDownDoc);
        }
    }
}

function mouseDownImg(e) {
    if (delete_mode) {
        delClick();
    } else {
        if (move != null && e.target != move) {
            move.classList.add("active");
            let image_rect = image.getBoundingClientRect();
            placeRelative(
                move,
                e.offsetY / image_rect.height,
                e.offsetX / image_rect.width,
            );
            if (move.classList.contains("l")) {
                var side = "left";
            } else {
                var side = "right";
            }
            document.querySelectorAll("." + side).forEach((select) => {
                if (
                    $("#" + select.id)
                        .find("[value='" + move.dataset.number + "']")
                        .text() == ""
                ) {
                    $("#" + select.id).append(
                        '<option value="' +
                        move.dataset.number +
                        '">' +
                        move.dataset.number +
                        "</option>",
                    );
                }
            });
            move.addEventListener("mousedown", mouseDownPos);
        }
    }
}

function mouseDownPos(e) {
    move = document.getElementById(e.target.id);
    if (delete_mode) {
        move.classList.remove("active");
        document
            .getElementById(getMatchingId(move.id))
            .classList.remove("active");
        if (move.classList.contains("l")) {
            var side = "left";
        } else {
            var side = "right";
        }
        $("." + side + ' [value="' + move.dataset.number + '"]').remove();
        move = null;
    } else {
        move.style.cursor = "grabbing";
        document.addEventListener("mousemove", mouseMovePos);
        document.addEventListener("mouseup", mouseUpPos);
    }
}

function mouseMovePos(e) {
    if (move != null) {
        image_rect = image.getBoundingClientRect();
        placeRelative(
            move,
            (e.clientY - image_rect.top) / image_rect.height,
            (e.clientX - image_rect.left) / image_rect.width,
        );
    }
}

function mouseUpPos() {
    if (move != null) {
        move.style.removeProperty("cursor");
        document.removeEventListener("mousemove", mouseMovePos);
    }
}

function getRelative(object) {
    let image_rect = image.getBoundingClientRect();
    let object_rect = object.getBoundingClientRect();
    y =
        parseFloat(object.style.top) / 100 +
        object_rect.height / 2 / image_rect.height;
    x =
        parseFloat(object.style.left) / 100 +
        object_rect.width / 2 / image_rect.width;

    return [y, x];
}

function delClick() {
    if (delete_mode) {
        document.querySelectorAll(".move").forEach((position) => {
            position.classList.remove("delete");
        });
        document.getElementById("delete").classList.remove("active");
        delete_mode = false;
    } else {
        var count = 0;
        document.querySelectorAll(".move").forEach((position) => {
            if (position.classList.contains("active")) {
                position.classList.add("delete");
                count += 1;
            }
        });
        if (count != 0) {
            delete_mode = true;
        } else {
            document.getElementById("delete").classList.remove("active");
        }
    }
}
