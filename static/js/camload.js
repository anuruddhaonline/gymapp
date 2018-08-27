function b64toBlob(b64Data, contentType, sliceSize) {
    contentType = contentType || '';
    sliceSize = sliceSize || 512;

    var byteCharacters = atob(b64Data);
    var byteArrays = [];

    for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        var slice = byteCharacters.slice(offset, offset + sliceSize);

        var byteNumbers = new Array(slice.length);
        for (var i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }

        var byteArray = new Uint8Array(byteNumbers);

        byteArrays.push(byteArray);
    }

    var blob = new Blob(byteArrays, {type: contentType});
    return blob;
}


var blobArray = [];


(function () {
    console.log('hfiehfieh');
    var video = document.getElementById('video');
    var canvas = document.getElementById('canvas');
    // var photo = document.getElementById('photo');
    var holder = document.getElementById('cam-holder');
    context = canvas.getContext('2d');

    if (navigator.mediaDevices.getUserMedia) {

        navigator.mediaDevices.getUserMedia({video: {width: 400, height: 300}, audio: false})
            .then(function (stream) {
                video.srcObject = stream;
                video.play();

            })
            .catch(function (error) {
                console.log(error.message);
            });
    }


    var count = 0;

    $('#capture').on('click', function () {
        count++;

        // photo.style.display = 'block';
        context.drawImage(video, 0, 0, 400, 300);

        if (count <= 12) {

            var image = document.createElement('img');
            image.setAttribute('src', canvas.toDataURL('image/png'));
            image.classList.add("cam-img");
            holder.appendChild(image);

            var ImageURL = canvas.toDataURL('image/png');

            // Split the base64 string in data and contentType
            var block = ImageURL.split(";");
            // Get the content type
            var contentType = block[0].split(":")[1];// In this case "image/gif"
            //get type
            var fileType = contentType.split("/")[1];
            // get the real base64 content of the file
            var realData = block[1].split(",")[1];
            // Convert to blob
            var blobs = b64toBlob(realData, contentType);

            blobArray.push({blobs:blobs, filename:'img'+count+'.'+fileType});

        }

        console.log('key pressed');

    })


})();


$("#regform").submit(function (e) {
    e.preventDefault();
    var form = document.getElementById("regform");

    // Create a FormData and append the file
    var fd = new FormData(form);

    for (var i = 0; i < 12; i++) {
        fd.append("img", blobArray[i].blobs, blobArray[i].filename);
    }


    $.ajax({
        url: "http://localhost:5000/dash/",
        data: fd,// the formData function is available in almost all new browsers.
        type: "POST",
        contentType: false,
        processData: false,
        cache: false,
        error: function (err) {
            console.error(err);
        },
        success: function (data) {
            alert(data);
        },
        complete: function () {
            console.log("Request finished.");
            location.reload();
        }
    });


});