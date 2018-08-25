(function(){
			console.log('hfiehfieh');
			var video = document.getElementById('video');
			var canvas = document.getElementById('canvas');
			// var photo = document.getElementById('photo');
			var holder = document.getElementById('cam-holder');
			context = canvas.getContext('2d');

			if (navigator.mediaDevices.getUserMedia) {

				navigator.mediaDevices.getUserMedia({video:{width:400,height:300}, audio:false})
				.then(function(stream) {
					video.srcObject = stream;
					video.play();

				})
				.catch(function(error) {
					console.log(error.message);
				});
			}

			var count = 0;

			document.getElementById('capture').addEventListener('click',function(){
				count++;

				// photo.style.display = 'block';
				context.drawImage(video, 0,0,400,300);

				var image = document.createElement('img');
				image.setAttribute('src',canvas.toDataURL('image/png'));
				image.classList.add("cam-img");
				holder.appendChild(image);
				console.log('key pressed');

				// photo.setAttribute('src', canvas.toDataURL('image/png'));
			})

		})();