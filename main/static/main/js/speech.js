const searchConsole = document.getElementById("chat-input");
let textLength = 0;
let isRecording = false;

// ----- 현재 브라우저에서 API 사용이 유효한가를 검증
function availabilityFunc() {
    //현재 SpeechRecognition을 지원하는 크롬 버전과 webkit 형태로 제공되는 버전이 있으므로 둘 중 해당하는 생성자를 호출한다.
    recognition = new webkitSpeechRecognition() || new SpeechRecognition();
    recognition.lang = "ko"; // 음성인식에 사용되고 반환될 언어를 설정한다.
    recognition.maxAlternatives = 5; //음성 인식결과를 5개 까지 보여준다.
    recognition.interimResults = true; // 음성인식 결과를 반환할 때 중간 결과도 반환한다.

    if (!recognition) {
        alert("현재 브라우저는 사용이 불가능합니다.");
    }
}

function setRecordIcon(isRecording) {
    const recordIcon = document.getElementById("record-icon");
    const recordBtn = document.getElementById("btn-record");
    if (isRecording) {
        recordIcon.innerText = "pending";
        // btn-pulse 클래스를 추가하여 애니메이션을 실행한다.
        recordBtn.classList.add("btn-pulse");
    } else {
        recordIcon.innerText = "mic";
        // btn-pulse 클래스를 제거하여 애니메이션을 중지한다.
        recordBtn.classList.remove("btn-pulse");
    }
}

// --- 음성녹음을 실행하는 함수
function startRecord() {
    if (isRecording) {
        endRecord();
        isRecording = false;
        return;
    }
    isRecording = true;
    console.log("시작");
    setRecordIcon(true);
    textLength = 0;

    // ⏺️클릭 시 음성인식을 시작한다.
    recognition.addEventListener("speechstart", () => {
        console.log("인식");
    });

    //음성인식이 끝까지 이루어지면 중단된다.
    recognition.addEventListener("speechend", () => {
        console.log("인식2");
        setRecordIcon(false);
    });

    //음성인식 결과를 반환
    // SpeechRecognitionResult 에 담겨서 반환된다.
    recognition.addEventListener("result", (e) => {
        text = e.results[0][0].transcript;
        if (text.length > textLength) {
            textLength = text.length;
            searchConsole.value = text;
            console.log(text.length);
            console.log(text);
        }
    });

    recognition.start();
}
//  🛑 클릭 시 종료(안 눌러도 음성인식은 알아서 종료됨)
function endRecord() {
    console.log("종료");
    setRecordIcon(false);
    recognition.stop(); // 음성인식을 중단하고 중단까지의 결과를 반환
}

window.addEventListener("load", availabilityFunc);
