const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");

let response_waiting = false; // 서버로부터 응답을 받고 있는지 확인하는 변수. true면 채팅을 입력할 수 없음

function addChat(text, is_user = true) {
    // jquery로 채팅 박스 추가
    query = `<div class='chat${is_user ? " user" : ""}'></div>`;
    const chatBox = $(query);
    chatBox.text(text);
    $(".chat-container").append(chatBox);
    // 채팅 박스 추가 후 스크롤 맨 아래로 내리기
    window.scrollTo(0, document.body.scrollHeight);
}

form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (input.value && !response_waiting) {
        response_waiting = true;
        addChat(input.value, true);

        // csrf 토큰 가져오기
        let csrftoken = document.getElementsByName("csrfmiddlewaretoken")[0]
            .value;

        // formdata 생성
        let formData = new FormData();
        formData.append("message", input.value);

        input.value = "";

        // ajax로 서버에 데이터 전송
        $.ajax({
            type: "POST",
            url: "/chat/",
            headers: { "X-CSRFToken": csrftoken },
            cache: false,
            data: formData,
            processData: false,
            contentType: false,
        }).done(function (data) {
            // console.log(data["message"]);
            addChat(data["message"], false);
            response_waiting = false;
        });
    }
});
