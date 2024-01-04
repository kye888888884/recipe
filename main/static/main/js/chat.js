const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");

let response_waiting = false; // 서버로부터 응답을 받고 있는지 확인하는 변수. true면 채팅을 입력할 수 없음
let chat_word_delay = 20; // 채팅 단어가 한 글자씩 출력되는 딜레이, 단위: ms
let current_intent = ""; // 현재 사용자의 의도. Dialogflow에서 인식한 intent를 저장하는 변수
let recipes = null; // 추천받은 레시피 목록 (top개)
let recipe = null; // 선택한 레시피
let recipe_id = null; // 선택한 레시피의 id

function setResponseWaiting(value) {
    response_waiting = value;
    const image_active = document.getElementById("send-active");
    const image_inactive = document.getElementById("send-inactive");

    if (value) {
        image_active.hidden = true;
        image_inactive.hidden = false;
    } else {
        image_active.hidden = false;
        image_inactive.hidden = true;
    }
}

function scrollBottom() {
    window.scrollTo(0, document.body.scrollHeight);
}

function addChat(text, is_user = true, is_server = true) {
    // jquery로 채팅 박스 추가
    query = `<div class='chat${is_user ? " user" : ""}'></div>`;
    const chat_box = $(query);
    if (is_user) chat_box.text(text);

    $(".chat-container").append(chat_box);
    // 채팅 박스 추가 후 스크롤 맨 아래로 내리기
    scrollBottom();
    // 채팅 단어가 한 글자씩 출력되는 효과
    if (!is_user) typingEffect(chat_box, text, 0, is_server);
}

// 채팅 단어가 한 글자씩 출력되는 효과
function typingEffect(chat_box, text, i = 0, is_server = true) {
    if (i < text.length) {
        // 문자가 @면 줄바꿈
        if (text.charAt(i) == "@") {
            chat_box.html(chat_box.html() + "<br />");
        } else chat_box.html(chat_box.html() + text.charAt(i));
        i++;
        setTimeout(function () {
            typingEffect(chat_box, text, i, is_server);
        }, chat_word_delay);
    } else {
        if (is_server) setResponseWaiting(false);
    }
    scrollBottom();
}

form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (input.value && !response_waiting) {
        setResponseWaiting(true);
        addChat(input.value, true);

        // csrf 토큰 가져오기
        let csrftoken = document.getElementsByName("csrfmiddlewaretoken")[0]
            .value;

        // formdata 생성
        let formData = new FormData();
        formData.append("message", input.value);
        formData.append("intent", current_intent);
        if (recipes) {
            formData.append("recipes", recipes);
        }
        if (recipe) {
            formData.append("recipe", recipe);
        }
        if (recipe_id) {
            formData.append("recipe_id", recipe_id);
        }
        formData.append("csrf", csrftoken);

        input.value = "";

        if (current_intent == "recipe") {
            recipes = null;
            recipe = null;
            recipe_id = null;
        }

        // ajax로 서버에 데이터 전송

        if (current_intent == "recommend") {
            let xmlhttp = new XMLHttpRequest();
            url = "/chat/";

            query = `<div class='chat'></div>`;
            const chat_box = $(query);
            $(".chat-container").append(chat_box);

            xmlhttp.addEventListener(
                "progress",
                updateProgressCreator(chat_box),
                false
            );
            xmlhttp.addEventListener("loadend", function () {
                setResponseWaiting(false);
                scrollBottom();
            });
            xmlhttp.open("POST", url, true);
            xmlhttp.setRequestHeader("X-CSRFToken", csrftoken);
            xmlhttp.send(formData);
        } else {
            $.ajax({
                type: "POST",
                url: "/chat/",
                headers: { "X-CSRFToken": csrftoken },
                cache: false,
                data: formData,
                processData: false,
                contentType: false,
            }).done(function (data) {
                console.log(data);
                msg = data["message"];
                if (data["recipes"]) {
                    recipes = data["recipes"];
                }
                if (data["recipe"]) {
                    recipe = data["recipe"];
                }
                if (data["recipe_id"]) {
                    recipe_id = data["recipe_id"];
                }
                addChat(msg, false);
                current_intent = data["intent"];
                // console.log(current_intent);
            });
        }
    }
});

function updateProgressCreator(chatBox) {
    return function updateProgress(oEvent) {
        // log("inside progress");
        // log(oEvent);
        // log(oEvent.currentTarget.responseText.length);
        // log(oEvent.target.responseText);
        let text = oEvent.target.responseText;
        // @을 <br />로 바꾸기
        text = text.replaceAll("@", "<br />");
        chatBox.html(text);
        scrollBottom();
    };
}
