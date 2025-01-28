// disable submitting for unwanted buttons
document.querySelectorAll("button").forEach(button => { button.addEventListener("click", event => { event.preventDefault() }) })

// Positions
let delete_mode = false, move = null;
document.querySelectorAll(".option").forEach(element => { element.addEventListener("mousedown", mouseDownOpt) })

function mouseDownOpt(e){
    if (move != null){
        mouseDownDoc(e)
    }
    let target = e.target
    move = document.getElementById(getMatchingID(target.id))
    colorSelected(target.className[0] + " " + target.className.slice(-1), "black")
    image.addEventListener("mousedown", mouseDownImg)
    document.addEventListener("mousedown", mouseDownDoc)
}

function mouseDownDoc(e){
    if (move != null){
        if (e.target.id != "image" && e.target.id != getMatchingID(move.id) && move.style.display != "flex"){
            colorSelected(move.className[0] + " " + move.className.slice(-1), "grey")
            image.removeEventListener("mousedown", mouseDownImg)
        }
        if (e.target.id != getMatchingID(move.id)){
            document.removeEventListener("mousedown", mouseDownDoc)
        }
    }
}

function mouseDownImg(e){
    if (e.target != move){
        move.style.display = "flex"
        let image_rect = image.getBoundingClientRect()
        placeRelative(move, e.offsetY / image_rect.height, e.offsetX / image_rect.width)
        if (move.className[0] == "l"){
            var side = "left"
        } else {
            var side = "right"
        }
        document.querySelectorAll("." + side).forEach(select => {
            if ($("#" + select.id).find("[value='" + move.className.slice(-1) + "']").text() == ""){
                $("#" + select.id).append('<option value="' + move.className.slice(-1) + '">' + move.className.slice(-1) + '</option>')
            }
        })
        move.addEventListener("mousedown", mouseDownPos)
    }
}

function mouseDownPos(e){
    move = document.getElementById(e.target.id)
    if (delete_mode){
        move.style.display = "none"
        document.getElementById(getMatchingID(move.id)).style.borderColor = "grey"
        document.querySelectorAll(".move").forEach(position => {
            if (position.style.display == "flex"){
                position.style.borderColor = "black"
            }
            position.style.cursor = "grab"
        })
        if (move.className[0] == "l"){
            var side = "left"
        } else {
            var side = "right"
        }
        $('.' + side + ' [value="' + move.className.slice(-1) + '"]').remove()
        $('.' + side).val('').trigger('chosen:updated')
        delete_mode = false
        move = null
    } else {
        move.style.cursor = "grabbing"
        document.addEventListener("mousemove", mouseMovePos)
        document.addEventListener("mouseup", mouseUpPos)
    }
}

function mouseMovePos(e){
    if (move != null){
        image_rect = image.getBoundingClientRect()
        placeRelative(move, (e.clientY - image_rect.top) / image_rect.height,
                        (e.clientX - image_rect.left) / image_rect.width)
    }
}

function mouseUpPos(e){
    if (move != null){
        move.style.cursor = "grab"
        document.removeEventListener("mousemove", mouseMovePos)
    }
}

function getRelative(object){
    let image_rect = image.getBoundingClientRect()
    let object_rect = object.getBoundingClientRect()
    y = parseFloat(object.style.top) / 100 + object_rect.height / 2 / image_rect.height
    x = parseFloat(object.style.left) / 100 + object_rect.width / 2 / image_rect.width
    
    return [y, x]
}

function getMatchingID(id){
    if (id[0] == "p"){
        return "o" + id.slice(1)
    } else if (id[0] == "o"){
        return "p" + id.slice(1)
    }
}

function delClick(){
    document.querySelectorAll(".move").forEach(position => {
        if (position.style.display == "flex"){
            position.style.borderColor = "red"
            position.style.cursor = "not-allowed"
            delete_mode = true
        }
    })
}
