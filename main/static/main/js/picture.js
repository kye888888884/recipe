const input_photo = document.querySelector("#input-photo");
const shoot_container = document.querySelector(".shoot-container");
const cam_container = document.querySelector(".cam-container");
const pic = document.querySelector("#pic");
var video = document.querySelector("#video");

shoot_container.addEventListener("click", function () {
    // 숨기기
    shoot_container.style.display = "none";
});

input_photo.addEventListener("change", function (e) {
    // $("#pic").attr("src", URL.createObjectURL(e.target.files[0]));
    img = document.createElement("img");
    img.src = URL.createObjectURL(e.target.files[0]);
    img.alt = "사진";
    // 이미지 로드가 완료되면
    img.onload = function () {
        // base64로 인코딩
        base = getBase64Image(img);
        sendImage(base);
        addChat("", true, false, img);
    };
});

function getBase64Image(img) {
    var canvas = document.createElement("canvas");
    canvas.width = img.width;
    canvas.height = img.height;

    var ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);

    var dataURL = canvas.toDataURL("image/jph");
    return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
}

function shoot() {
    if (!("url" in window) && "webkitURL" in window) {
        window.URL = window.webkitURL;
    }
}

function showShooting() {
    shoot_container.style.display = "flex";
}

function showCam() {
    cam_container.style.display = "flex";
    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices
            .getUserMedia({ video: true })
            .then(function (stream) {
                video.srcObject = stream;
            })
            .catch(function (err0r) {
                console.log("Something went wrong!");
            });
    }
}

function closeCam() {
    cam_container.style.display = "none";
    video.pause();
    video.srcObject = null;
    // navigator.mediaDevices.getUserMedia({ video: false });
}

function takePic() {
    var canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas
        .getContext("2d")
        .drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
    var img = document.createElement("img");
    img.src = canvas.toDataURL();
    img.alt = "사진";
    // 이미지 로드가 완료되면
    img.onload = function () {
        // base64로 인코딩
        base = getBase64Image(img);
        sendImage(base);
        addChat("", true, false, img);
    };
    closeCam();
}

function sendImage(img) {
    // 이미지를 서버로 전송
    $.ajax({
        type: "POST",
        url: "/upload/",
        data: {
            csrfmiddlewaretoken: csrftoken,
            image: img,
        },
        success: function (response) {
            // 서버에서 받은 응답 출력
            console.log(response["names"]);
            if (response["names"].length == 0) {
                addChat("재료를 인식하지 못했어요.", false);
                return;
            }
            names = response["names"];
            // 재료 버튼 추가
            //     인식한 재료를 확인해주세요! 잘못 인식된 재료가 있으면 눌러서 삭제해주세요.<br />
            //   <div class="ingredient-container">
            //     <button class="ingredient">양파</button>
            //     <button class="ingredient">당근</button>
            //     <button class="ingredient">감자</button>
            //     <button class="ingredient">양배추</button>
            //     <button class="ingredient">고추</button>
            //     <button class="ingredient">파</button>
            //   </div>
            //   <button class="ingredient-ok">완료</button>
            let custom = document.createElement("div");

            let container = document.createElement("div");
            container.classList.add("ingredient-container");
            let btns = [];
            for (i = 0; i < names.length; i++) {
                let btn = document.createElement("button");
                btn.classList.add("ingredient");
                btn.innerText = names[i];
                container.appendChild(btn);
                btn.addEventListener("click", function () {
                    this.classList.toggle("selected");
                });
                btns.push(btn);
            }
            custom.appendChild(container);

            let btn = document.createElement("button");
            btn.classList.add("ingredient-ok");
            btn.innerText = "완료";
            btn.addEventListener("click", function () {
                names = [];
                for (i = 0; i < btns.length; i++) {
                    if (!btns[i].classList.contains("selected")) {
                        names.push(btns[i].innerText);
                    }
                }
                input.value = names.join(", ");
                console.log(names);
            });
            custom.appendChild(btn);
            console.log(btns);

            addChat(
                "인식한 재료를 확인해주세요!@잘못 인식된 재료가 있으면 눌러서 삭제해주세요.",
                false,
                false,
                custom
            );
        },
    });
}
