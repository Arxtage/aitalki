MAIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSocket Audio Test</title>
</head>
<body>
    <h1>WebSocket Audio Test</h1>
    <button id="startRecording">Start Recording</button>
    <button id="stopRecording" disabled>Stop Recording</button>
    <audio id="audioPlayback" controls></audio>

    <script>
        let socket = new WebSocket("ws://localhost:8000/ws");
        let mediaRecorder;
        let audioChunks = [];

        socket.onmessage = function(event) {
            const audioPlayback = document.getElementById("audioPlayback");
            const blob = new Blob([event.data], { type: 'audio/wav' });
            audioPlayback.src = URL.createObjectURL(blob);
            audioPlayback.play();
        };

        document.getElementById("startRecording").onclick = async function() {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            mediaRecorder.ondataavailable = function(event) {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = function() {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                socket.send(audioBlob);
                audioChunks = [];  // Reset the chunks for the next recording
            };

            document.getElementById("stopRecording").disabled = false;
        };

        document.getElementById("stopRecording").onclick = function() {
            mediaRecorder.stop();
            document.getElementById("stopRecording").disabled = true;
        };
    </script>
</body>
</html>
"""
