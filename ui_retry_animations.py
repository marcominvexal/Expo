"""HTML/CSS for Gemini retry wait screen and sync success character."""


def gemini_retry_wait_html(remaining_seconds, total_timeout_left):
    return f"""
    <div class="hd-wait-container">
        <div class="hd-status">
            <span class="pulse-dot"></span>
            <strong>Gemini is experiencing heavy load.</strong>
            Retrying in <span>{remaining_seconds}s</span>
            ({total_timeout_left}s total backup time left)
        </div>
        <div class="hd-stage">
            <div class="hd-walker">
                <div class="hd-antenna">
                    <div class="hd-bulb"></div>
                    <div class="hd-stem"></div>
                </div>
                <div class="hd-head">
                    <div class="hd-glass-visor">
                        <div class="hd-eye-glow"></div>
                        <div class="hd-eye-glow"></div>
                    </div>
                </div>
                <div class="hd-body"><div class="hd-dial"></div></div>
                <div class="hd-legs">
                    <div class="hd-leg hd-left"></div>
                    <div class="hd-leg hd-right"></div>
                </div>
                <div class="hd-shadow"></div>
            </div>
        </div>
    </div>
    <style>
        @keyframes hd-bounce {{
            0% {{ transform: translateY(0px) scale(1); }}
            50% {{ transform: translateY(-12px) scale(0.98); }}
            100% {{ transform: translateY(0px) scale(1); }}
        }}
        @keyframes hd-walk-L {{
            0% {{ transform: rotate(-30deg); }}
            100% {{ transform: rotate(30deg); }}
        }}
        @keyframes hd-walk-R {{
            0% {{ transform: rotate(30deg); }}
            100% {{ transform: rotate(-30deg); }}
        }}
        @keyframes eye-shimmer {{
            0%, 100% {{ opacity: 0.7; box-shadow: 0 0 8px #FF4B4B; }}
            50% {{ opacity: 1; box-shadow: 0 0 16px #FF4B4B; }}
        }}
        .hd-wait-container {{
            background: linear-gradient(135deg, #1E1E2F 0%, #11111D 100%);
            border: 2px solid #2A2A40;
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 12px 40px rgba(0,0,0,0.3);
            font-family: system-ui, -apple-system, sans-serif;
            color: #E2E8F0;
        }}
        .hd-status {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            font-size: 14px;
            letter-spacing: 0.5px;
            text-align: center;
            flex-wrap: wrap;
        }}
        .hd-status span {{ color: #4DEEEA; font-weight: 700; }}
        .pulse-dot {{
            width: 8px;
            height: 8px;
            background: #FF4B4B;
            border-radius: 50%;
            box-shadow: 0 0 10px #FF4B4B;
            animation: eye-shimmer 1s infinite alternate;
            flex-shrink: 0;
        }}
        .hd-stage {{
            height: 140px;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            position: relative;
            margin-top: 15px;
        }}
        .hd-walker {{
            display: flex;
            flex-direction: column;
            align-items: center;
            animation: hd-bounce 0.5s ease-in-out infinite;
        }}
        .hd-antenna {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .hd-bulb {{
            width: 10px;
            height: 10px;
            background: linear-gradient(135deg, #FF4B4B, #B30000);
            border-radius: 50%;
            box-shadow: 0 0 12px #FF4B4B;
        }}
        .hd-stem {{ width: 3px; height: 10px; background: #515170; }}
        .hd-head {{
            width: 56px;
            height: 42px;
            background: linear-gradient(135deg, #4DEEEA 0%, #20A4A1 100%);
            border-radius: 14px;
            padding: 3px;
            box-shadow: inset 0 2px 4px rgba(255,255,255,0.4), 0 4px 10px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .hd-glass-visor {{
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.8);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}
        .hd-eye-glow {{
            width: 10px;
            height: 10px;
            background: #FF4B4B;
            border-radius: 50%;
            animation: eye-shimmer 0.5s infinite alternate;
        }}
        .hd-body {{
            width: 64px;
            height: 48px;
            background: linear-gradient(135deg, #FFDE4D 0%, #D4AF37 100%);
            border-radius: 8px;
            margin-top: -1px;
            box-shadow: inset 0 2px 3px rgba(255,255,255,0.5), 0 4px 10px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .hd-dial {{
            width: 24px;
            height: 8px;
            background: #1E1E2F;
            border-radius: 4px;
        }}
        .hd-legs {{ display: flex; gap: 16px; margin-top: -2px; }}
        .hd-leg {{
            width: 10px;
            height: 22px;
            background: #33334D;
            border-radius: 5px;
            transform-origin: top center;
        }}
        .hd-left {{ animation: hd-walk-L 0.5s ease-in-out infinite alternate; }}
        .hd-right {{ animation: hd-walk-R 0.5s ease-in-out infinite alternate; }}
        .hd-shadow {{
            width: 50px;
            height: 6px;
            background: rgba(0,0,0,0.4);
            border-radius: 50%;
            margin-top: 4px;
            filter: blur(1px);
        }}
    </style>
    """


SYNC_SUCCESS_CHARACTER_HTML = """
<div class="hd-box">
    <div class="hd-bubble">Sync completed successfully! Your live funnel is updated. ✨</div>
    <div class="hd-avatar">
        <div class="hd-antenna-main">
            <div class="hd-orb"></div>
            <div class="hd-wire"></div>
        </div>
        <div class="hd-robot-face">
            <div class="hd-screen-inner">
                <div class="hd-eyes-container">
                    <div class="hd-neon-eye"></div>
                    <div class="hd-neon-eye"></div>
                </div>
                <div class="hd-speaking-mouth"></div>
            </div>
        </div>
        <div class="hd-torso"><div class="hd-core-light"></div></div>
        <div class="hd-floor-shadow"></div>
    </div>
</div>
<style>
    @keyframes float-hd {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    @keyframes eye-blink-hd {
        0%, 92%, 100% { transform: scaleY(1); }
        96% { transform: scaleY(0.1); }
    }
    @keyframes hd-baby-talk {
        0%, 100% { height: 4px; border-radius: 2px; width: 20px; }
        50% { height: 12px; border-radius: 50%; width: 16px; background: #FF4B4B; }
    }
    .hd-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
        background: linear-gradient(135deg, #14142B 0%, #080811 100%);
        border-radius: 24px;
        border: 1px solid #222244;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        animation: float-hd 3s ease-in-out infinite;
    }
    .hd-bubble {
        position: relative;
        background: linear-gradient(135deg, #FFDE4D 0%, #F1C40F 100%);
        border-radius: 20px;
        padding: 16px 24px;
        font-weight: 800;
        color: #0C0C1E;
        max-width: 300px;
        text-align: center;
        font-family: system-ui, -apple-system, sans-serif;
        box-shadow: 0 8px 24px rgba(241,196,15,0.3);
        margin-bottom: 25px;
        font-size: 15px;
    }
    .hd-bubble::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        border-width: 10px 10px 0;
        border-style: solid;
        border-color: #F1C40F transparent;
    }
    .hd-avatar {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .hd-antenna-main {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .hd-orb {
        width: 12px;
        height: 12px;
        background: linear-gradient(135deg, #4DEEEA, #20A4A1);
        border-radius: 50%;
        box-shadow: 0 0 15px #4DEEEA;
    }
    .hd-wire { width: 4px; height: 12px; background: #3A3A55; }
    .hd-robot-face {
        width: 90px;
        height: 68px;
        background: linear-gradient(135deg, #2A2A40 0%, #1A1A2E 100%);
        border-radius: 22px;
        padding: 5px;
        box-shadow: inset 0 2px 4px rgba(255,255,255,0.2), 0 10px 25px rgba(0,0,0,0.4);
    }
    .hd-screen-inner {
        width: 100%;
        height: 100%;
        background: #09090F;
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 8px;
        position: relative;
        overflow: hidden;
    }
    .hd-screen-inner::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 50%;
        background: linear-gradient(to bottom, rgba(255,255,255,0.08), transparent);
        pointer-events: none;
    }
    .hd-eyes-container { display: flex; gap: 20px; }
    .hd-neon-eye {
        width: 14px;
        height: 14px;
        background: linear-gradient(135deg, #4DEEEA 0%, #00B4B4 100%);
        border-radius: 50%;
        box-shadow: 0 0 12px #4DEEEA;
        animation: eye-blink-hd 4s infinite;
    }
    .hd-speaking-mouth {
        width: 20px;
        height: 4px;
        background: #4DEEEA;
        border-radius: 2px;
        box-shadow: 0 0 6px #4DEEEA;
        animation: hd-baby-talk 0.22s ease-in-out infinite alternate;
    }
    .hd-torso {
        width: 60px;
        height: 30px;
        background: linear-gradient(135deg, #FF4B4B 0%, #990000 100%);
        border-radius: 0 0 16px 16px;
        margin: -1px auto 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    }
    .hd-core-light {
        width: 12px;
        height: 12px;
        background: #FFF;
        border-radius: 50%;
        box-shadow: 0 0 10px #FFF;
    }
    .hd-floor-shadow {
        width: 70px;
        height: 6px;
        background: rgba(0,0,0,0.6);
        border-radius: 50%;
        margin-top: 12px;
        filter: blur(2px);
    }
</style>
<script>
    setTimeout(function() {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        var phrase = new SpeechSynthesisUtterance(
            'Sync completed successfully! Your live funnel is updated.'
        );
        phrase.volume = 1.0;
        phrase.pitch = 0.52;
        phrase.rate = 0.92;
        window.speechSynthesis.speak(phrase);
        phrase.onend = function() {
            var mouth = document.querySelector('.hd-speaking-mouth');
            if (mouth) {
                mouth.style.animation = 'none';
                mouth.style.height = '4px';
                mouth.style.width = '20px';
            }
        };
    }, 400);
</script>
"""
