// disable submitting for unwanted buttons
document.querySelectorAll("button").forEach(button => { button.addEventListener("click", event => { event.preventDefault() }) })

// Positions
let newX = 0, newY = 0, startX = 0, startY = 0, delete_mode = false, move = null;
document.querySelectorAll(".option").forEach(element => { element.addEventListener("mousedown", mouseDownOpt) })

function mouseDownOpt(e){
    if (move != null){
        mouseDownDoc(e)
    }
    target = e.target
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
    if (move != null){
        move.style.display = "flex"
        placeRelative(move, (e.clientY - move.clientHeight / 2 - image.getBoundingClientRect().top) / image.clientHeight, 
                        (e.clientX - move.clientWidth / 2 - image.getBoundingClientRect().left) / image.clientWidth)
        if (move.className[0] == "l"){
            side = "left"
        } else {
            side = "right"
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
                position.style.cursor = "grab"
            }
        })
        if (move.className[0] == "l"){
            side = "left"
        } else {
            side = "right"
        }
        $('.' + side + ' [value="' + move.className.slice(-1) + '"]').remove()
        $('.' + side).val('').trigger('chosen:updated')
        delete_mode = false
        move = null
    } else {
        startX = e.clientX
        startY = e.clientY
        move.style.cursor = "grabbing"
        document.addEventListener("mousemove", mouseMovePos)
        document.addEventListener("mouseup", mouseUpPos)
    }
}

function mouseMovePos(e){
    if (move != null){
        if (e.clientX <= image.getBoundingClientRect().left + image.offsetWidth && e.clientX >= image.getBoundingClientRect().left){
            newX = startX - e.clientX
            startX = e.clientX
        }
        if (e.clientY <= image.getBoundingClientRect().top + image.clientHeight && e.clientY >= image.getBoundingClientRect().top){
            newY = startY - e.clientY
            startY = e.clientY
        }
        placeRelative(move, (move.getBoundingClientRect().top - newY - image.getBoundingClientRect().top) / image.clientHeight,
                        (move.getBoundingClientRect().left - newX - image.getBoundingClientRect().left) / image.clientWidth)
    }
}

function mouseUpPos(e){
    if (move != null){
        move.style.cursor = "grab"
        document.removeEventListener("mousemove", mouseMovePos)
    }
}

function getRelative(object){
    y = (parseInt(object.style.top) - image.getBoundingClientRect().top - window.scrollY) / image.clientHeight
    x = (parseInt(object.style.left) - image.getBoundingClientRect().left - window.scrollX) / image.clientWidth
    
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
