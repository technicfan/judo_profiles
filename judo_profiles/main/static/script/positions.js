const image = document.getElementById("image_container")

function placeRelative(object, relativeY, relativeX){
    var image_rect = image.getBoundingClientRect()
    var object_rect = object.getBoundingClientRect()
    var maxY = 1 - object_rect.height / 2 / image_rect.height
    var maxX = 1 - object_rect.width / 2 / image_rect.width
    var minY = object_rect.height / 2 / image_rect.height
    var minX = object_rect.width / 2 / image_rect.width

    if (relativeY >= maxY){
        var relativeY = maxY
    } else if (relativeY <= minY){
        var relativeY = minY
    }
    if (relativeX >= maxX){
        var relativeX = maxX
    } else if (relativeX <= minX){
        var relativeX = minX
    }

    object.style.top = relativeY * 100 - object_rect.height / 2 / image_rect.height * 100 + "%"
    object.style.left = relativeX * 100 - object_rect.width / 2 / image_rect.width * 100 + "%"
}

function colorSelected(classes, color){
    var selected = document.getElementsByClassName(classes)
    for (let i = 0; i < selected.length; i++) {
        selected.item(i).style.borderColor = color
    }
}
