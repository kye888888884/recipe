const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");

let response_waiting = false; // 서버로부터 응답을 받고 있는지 확인하는 변수. true면 채팅을 입력할 수 없음
let chat_word_delay = 20; // 채팅 단어가 한 글자씩 출력되는 딜레이, 단위: ms를 저장하는 변수
let data = {
    prev_intent: "", // 이전 intent
    intent: "", // 현재 intent
    recommended_recipes: null, // 추천받은 레시피 목록 (top개)
    recipe: null, // 선택한 레시피 이름
    recipe_id: null, // 선택한 레시피 id
    inbun: null, // 인분
    ingredients: null, // 사용자가 입력한 재료 목록
    main_ingredients: null, // 사용자가 입력한 주재료 목록
};
// csrf 토큰 가져오기
let csrftoken = document.getElementsByName("csrfmiddlewaretoken")[0].value;

window.onload = function () {
    addChat(
        "안녕하세요! 가지고 있는 재료를 적어주시면 관련된 레시피를 알려드릴게요.@또는 우측 하단 촬영 버튼을 눌러서 재료 사진을 찍어주세요!",
        false
    );
};

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

function addChat(text, is_user = true, is_server = true, custom = false) {
    // jquery로 채팅 박스 추가
    query = `<div class='chat${is_user ? " user" : ""}'></div>`;
    const chat_box = $(query);
    if (is_user) chat_box.text(text);

    $(".chat-container").append(chat_box);
    // 채팅 박스 추가 후 스크롤 맨 아래로 내리기
    // 채팅 단어가 한 글자씩 출력되는 효과
    if (!is_user) typingEffect(chat_box, text, 0, is_server, custom);
    else {
        if (custom) {
            chat_box.append(custom);
        }
    }
    scrollBottom();
}

// 채팅 단어가 한 글자씩 출력되는 효과
function typingEffect(chat_box, text, i = 0, is_server = true, custom = false) {
    if (i < text.length) {
        // 문자가 @면 줄바꿈
        if (text.charAt(i) == "@") {
            chat_box.html(chat_box.html() + "<br />");
        } else chat_box.html(chat_box.html() + text.charAt(i));
        i++;
        setTimeout(function () {
            typingEffect(chat_box, text, i, is_server, custom);
        }, chat_word_delay);
    } else {
        if (is_server) setResponseWaiting(false);
        if (custom) {
            chat_box.append(custom);
        }
    }
    scrollBottom();
}

form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (input.value && !response_waiting) {
        setResponseWaiting(true);
        addChat(input.value, true);

        // formdata 생성
        let formData = new FormData();
        formData.append("message", input.value);
        formData.append("csrf", csrftoken);
        for (let key in data) {
            formData.append(key, data[key]);
        }

        input.value = "";

        // data 초기화
        // if (data["intent"] == "inbun") {
        //     data["prev_intent"] = "";
        //     data["intent"] = "";
        //     data["recommended_recipes"] = null;
        //     data["recipe"] = null;
        //     data["recipe_id"] = null;
        //     data["ingredients"] = null;
        //     data["main_ingredients"] = null;
        // }

        // ajax로 서버에 데이터 전송

        if (data["intent"] == "recommend_positive") {
            data["intent"] = "after_recommend";

            addChat(
                `잠시만요! 곧 ${data["recipe"]} 레시피를 알려드릴게요.`,
                false,
                false
            );

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
            }).done(function (res) {
                // console.log(res);
                msg = res["message"];
                data["prev_intent"] = res["prev_intent"];
                data["intent"] = res["intent"];
                if (res["recommended_recipes"]) {
                    data["recommended_recipes"] = res["recommended_recipes"];
                }
                if (res["recipe"]) {
                    data["recipe"] = res["recipe"];
                }
                if (res["recipe_id"]) {
                    data["recipe_id"] = res["recipe_id"];
                }
                if (res["inbun"]) {
                    data["inbun"] = res["inbun"];
                }
                if (res["ingredients"]) {
                    data["ingredients"] = res["ingredients"];
                }
                if (res["main_ingredients"]) {
                    data["main_ingredients"] = res["main_ingredients"];
                }
                console.log(data);
                addChat(msg, false);
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
