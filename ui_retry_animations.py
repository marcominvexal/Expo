"""HTML/CSS for Gemini retry wait screen and sync success character."""


def gemini_retry_wait_html(remaining_seconds, total_timeout_left):
    return f"""
    <div class="wait-frame">
        <div class="status-msg">
            ⏳ <strong>Gemini is busy (503 Error).</strong><br>
            Retrying in <span class="highlight">{remaining_seconds}s</span>...
            (Total timeout limit: {total_timeout_left}s remaining)
        </div>
        <div class="animation-stage">
            <div class="cartoon-walker">
                <div class="antenna-dot"></div>
                <div class="antenna-line"></div>
                <div class="robot-head"><div class="visor"></div></div>
                <div class="robot-body"><div class="heartbeat"></div></div>
                <div class="robot-legs">
                    <div class="leg left-leg"></div>
                    <div class="leg right-leg"></div>
                </div>
            </div>
        </div>
    </div>
    <style>
        @keyframes bobbing {{
            0% {{ transform: translateY(0px); }}
            100% {{ transform: translateY(-8px); }}
        }}
        @keyframes swingingLeft {{
            0% {{ transform: rotate(-28deg); }}
            100% {{ transform: rotate(28deg); }}
        }}
        @keyframes swingingRight {{
            0% {{ transform: rotate(28deg); }}
            100% {{ transform: rotate(-28deg); }}
        }}
        @keyframes pulse {{
            0%, 100% {{ background: #FF4C4C; }}
            50% {{ background: #FFFF00; }}
        }}
        .wait-frame {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #F9F9FB;
            border: 3px dashed #4DEEEA;
            border-radius: 16px;
            padding: 22px;
            margin: 15px 0;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
        }}
        .status-msg {{
            font-family: 'Comic Sans MS', sans-serif;
            font-size: 15px;
            color: #2C3E50;
            text-align: center;
            line-height: 1.6;
            margin-bottom: 20px;
        }}
        .highlight {{
            color: #FF4C4C;
            font-weight: bold;
            font-size: 18px;
        }}
        .animation-stage {{
            height: 110px;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            width: 100%;
        }}
        .cartoon-walker {{
            display: flex;
            flex-direction: column;
            align-items: center;
            animation: bobbing 0.45s ease-in-out infinite alternate;
        }}
        .antenna-dot {{
            width: 8px;
            height: 8px;
            background: #FF4C4C;
            border: 2px solid #000;
            border-radius: 50%;
            animation: pulse 0.3s infinite;
        }}
        .antenna-line {{
            width: 3px;
            height: 8px;
            background: #000;
        }}
        .robot-head {{
            width: 44px;
            height: 32px;
            background: #4DEEEA;
            border: 3px solid #000;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .visor {{
            width: 30px;
            height: 8px;
            background: #000;
            border-radius: 4px;
            position: relative;
        }}
        .visor::after {{
            content: '';
            position: absolute;
            left: 4px;
            top: 2px;
            width: 4px;
            height: 4px;
            background: #FFF;
            border-radius: 50%;
        }}
        .robot-body {{
            width: 50px;
            height: 40px;
            background: #FFDE4D;
            border: 3px solid #000;
            border-radius: 6px;
            margin-top: -2px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .heartbeat {{
            width: 14px;
            height: 14px;
            background: #000;
            clip-path: polygon(50% 0%, 100% 35%, 80% 100%, 50% 75%, 20% 100%, 0% 35%);
        }}
        .robot-legs {{
            display: flex;
            gap: 12px;
            margin-top: -2px;
        }}
        .leg {{
            width: 7px;
            height: 18px;
            background: #000;
            border-radius: 4px;
            transform-origin: top center;
        }}
        .left-leg {{
            animation: swingingLeft 0.45s ease-in-out infinite alternate;
        }}
        .right-leg {{
            animation: swingingRight 0.45s ease-in-out infinite alternate;
        }}
    </style>
    """


SYNC_SUCCESS_CHARACTER_HTML = """
<div class="character-box">
    <div class="bubble">Sync completed successfully! Your live funnel is updated. ✨</div>
    <div class="bot-avatar">
        <div class="antenna"></div>
        <div class="head">
            <div class="eyes">
                <div class="eye left"></div>
                <div class="eye right"></div>
            </div>
            <div class="mouth"></div>
        </div>
        <div class="body-frame"><div class="screen">⚡</div></div>
    </div>
</div>
<style>
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }
    @keyframes blink {
        0%, 90%, 100% { transform: scaleY(1); }
        95% { transform: scaleY(0.1); }
    }
    @keyframes talk {
        0%, 100% { width: 16px; height: 4px; border-radius: 2px; }
        50% { width: 14px; height: 10px; border-radius: 50%; }
    }
    .character-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif;
        padding: 10px;
        animation: float 2.5s ease-in-out infinite;
    }
    .bubble {
        position: relative;
        background: #FFDE4D;
        border: 3px solid #000;
        border-radius: 16px;
        padding: 12px 18px;
        font-weight: bold;
        color: #000;
        max-width: 280px;
        text-align: center;
        box-shadow: 4px 4px 0px #000;
        margin-bottom: 15px;
        font-size: 14px;
    }
    .bubble::after {
        content: '';
        position: absolute;
        bottom: -12px;
        left: 50%;
        transform: translateX(-50%);
        border-width: 12px 12px 0;
        border-style: solid;
        border-color: #FFDE4D transparent;
        width: 0;
    }
    .bubble::before {
        content: '';
        position: absolute;
        bottom: -17px;
        left: 50%;
        transform: translateX(-50%);
        border-width: 14px 14px 0;
        border-style: solid;
        border-color: #000 transparent;
        width: 0;
        z-index: -1;
    }
    .bot-avatar {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .antenna {
        width: 5px;
        height: 12px;
        background: #000;
        position: relative;
    }
    .antenna::before {
        content: '';
        position: absolute;
        top: -6px;
        left: -4px;
        width: 13px;
        height: 13px;
        background: #FF4C4C;
        border: 3px solid #000;
        border-radius: 50%;
    }
    .head {
        width: 75px;
        height: 55px;
        background: #4DEEEA;
        border: 4px solid #000;
        border-radius: 18px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 6px;
        box-shadow: 4px 4px 0px #000;
    }
    .eyes { display: flex; gap: 14px; }
    .eye {
        width: 12px;
        height: 12px;
        background: #000;
        border-radius: 50%;
        animation: blink 3.5s infinite;
    }
    .mouth {
        width: 16px;
        height: 4px;
        background: #000;
        border-radius: 2px;
        animation: talk 0.25s ease-in-out infinite alternate;
    }
    .body-frame {
        width: 50px;
        height: 35px;
        background: #EAEAEA;
        border: 4px solid #000;
        border-top: none;
        border-radius: 0 0 12px 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 4px 4px 0px #000;
    }
    .screen { font-size: 14px; }
</style>
<script>
    setTimeout(function() {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        var phrase = new SpeechSynthesisUtterance(
            'Sync completed successfully! Your live funnel is updated.'
        );
        phrase.volume = 1.0;
        phrase.rate = 1.05;
        phrase.pitch = 1.35;
        window.speechSynthesis.speak(phrase);
        setTimeout(function() {
            var mouth = document.querySelector('.mouth');
            if (mouth) mouth.style.animation = 'none';
        }, 3200);
    }, 300);
</script>
"""
