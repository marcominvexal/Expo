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



def sync_success_sticker_html(image_data_uri):
    """Sync success: sticker pops up, giggles, says "Yay!" with party poppers, then goes back."""
    colors = ["#FFDE4D", "#FF5E8A", "#4DD8FF", "#7CFF6B", "#B27CFF", "#FF9F43"]
    confetti = []
    for i in range(36):
        side = "left" if i % 2 == 0 else "right"
        # Fan the pieces upward and inward from each popper.
        dx = (30 + (i * 37) % 170) * (1 if side == "left" else -1)
        dy = -(90 + (i * 53) % 140)
        spin = (i * 97) % 720 - 360
        delay = 0.55 + (i % 6) * 0.03
        confetti.append(
            f'<span class="cf cf-{side}" style="--dx:{dx}px;--dy:{dy}px;--spin:{spin}deg;'
            f'background:{colors[i % len(colors)]};animation-delay:{delay:.2f}s;'
            f'{"border-radius:50%;" if i % 3 == 0 else ""}"></span>'
        )
    confetti_html = "".join(confetti)
    return f"""
<div class="ss-box">
    <div class="ss-stage">
        <span class="ss-popper ss-popper-left">&#127881;</span>
        <span class="ss-popper ss-popper-right">&#127881;</span>
        {confetti_html}
        <div class="ss-bubble"><span class="ss-spark ss-spark-1">&#10024;</span><span class="ss-yay">Yaaayyy!</span> &#127881;<span class="ss-spark ss-spark-2">&#10024;</span></div>
        <img class="ss-sticker" src="{image_data_uri}" alt="Yay, sync complete">
    </div>
    <div class="ss-caption">Sync completed &mdash; your live funnel is updated.</div>
</div>
<style>
    body {{ margin: 0; }}
    .ss-box {{
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 12px 16px 16px;
        background: linear-gradient(135deg, #14142B 0%, #080811 100%);
        border-radius: 24px;
        border: 1px solid #222244;
        font-family: 'Segoe UI', system-ui, sans-serif;
        overflow: hidden;
    }}
    .ss-stage {{
        position: relative;
        width: 100%;
        height: 230px;
        display: flex;
        align-items: flex-end;
        justify-content: center;
    }}
    .ss-sticker {{
        width: 180px;
        height: 180px;
        object-fit: contain;
        transform-origin: 50% 90%;
        transform: scale(0);
        filter: drop-shadow(0 10px 18px rgba(0, 0, 0, 0.45));
        /* pop up -> giggle -> hold -> go back down */
        animation: ss-pop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) 0.1s forwards,
                   ss-giggle 1.1s ease-in-out 0.6s,
                   ss-back 0.5s cubic-bezier(0.55, 0, 0.75, -0.4) 3.2s forwards;
    }}
    @keyframes ss-pop {{
        0% {{ transform: scale(0) translateY(60px); }}
        100% {{ transform: scale(1) translateY(0); }}
    }}
    @keyframes ss-giggle {{
        0%, 100% {{ transform: scale(1) rotate(0deg); }}
        10% {{ transform: scale(1.04, 0.96) rotate(-7deg); }}
        20% {{ transform: scale(0.97, 1.03) rotate(6deg); }}
        30% {{ transform: scale(1.04, 0.96) rotate(-6deg); }}
        40% {{ transform: scale(0.97, 1.03) rotate(5deg); }}
        50% {{ transform: scale(1.03, 0.97) rotate(-4deg); }}
        60% {{ transform: scale(0.98, 1.02) rotate(3deg); }}
        75% {{ transform: scale(1.01) rotate(-1.5deg); }}
    }}
    @keyframes ss-back {{
        0% {{ transform: scale(1) translateY(0); }}
        100% {{ transform: scale(0) translateY(60px); }}
    }}
    .ss-bubble {{
        position: absolute;
        top: 6px;
        left: 50%;
        transform: translateX(-50%) scale(0);
        background: linear-gradient(135deg, #FFDE4D 0%, #F1C40F 100%);
        border-radius: 18px;
        padding: 8px 20px;
        font-size: 26px;
        font-weight: 900;
        color: #0C0C1E;
        white-space: nowrap;
        z-index: 2;
        animation: ss-bubble-in 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) 0.55s forwards,
                   ss-bubble-out 0.3s ease-in 3.1s forwards;
    }}
    .ss-bubble::after {{
        content: '';
        position: absolute;
        bottom: -9px;
        left: 50%;
        transform: translateX(-50%);
        border-width: 10px 9px 0;
        border-style: solid;
        border-color: #F1C40F transparent;
    }}
    .ss-yay {{
        display: inline-block;
        background: linear-gradient(90deg, #FF3B6B, #FF9F1C, #FFE14D, #3BE38B, #3BB8FF, #A35BFF, #FF3B6B);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        -webkit-text-stroke: 0.6px rgba(12, 12, 30, 0.35);
        animation: ss-rainbow 1.2s linear infinite, ss-sing 0.45s ease-in-out 0.9s 4 alternate;
    }}
    @keyframes ss-rainbow {{
        to {{ background-position: 300% 0; }}
    }}
    @keyframes ss-sing {{
        from {{ transform: scale(1) rotate(-3deg); }}
        to {{ transform: scale(1.15) rotate(3deg); }}
    }}
    .ss-spark {{
        position: absolute;
        font-size: 18px;
        animation: ss-twinkle 0.6s ease-in-out infinite alternate;
    }}
    .ss-spark-1 {{ top: -12px; left: -10px; }}
    .ss-spark-2 {{ bottom: -8px; right: -12px; animation-delay: 0.3s; }}
    @keyframes ss-twinkle {{
        from {{ transform: scale(0.6) rotate(0deg); opacity: 0.6; }}
        to {{ transform: scale(1.2) rotate(25deg); opacity: 1; }}
    }}
    @keyframes ss-bubble-in {{
        to {{ transform: translateX(-50%) scale(1); }}
    }}
    @keyframes ss-bubble-out {{
        from {{ transform: translateX(-50%) scale(1); opacity: 1; }}
        to {{ transform: translateX(-50%) scale(0.6); opacity: 0; }}
    }}
    .ss-popper {{
        position: absolute;
        bottom: 18px;
        font-size: 40px;
        opacity: 0;
        animation: ss-popper 3.4s ease-out 0.45s forwards;
    }}
    .ss-popper-left {{ left: 12%; }}
    .ss-popper-right {{ right: 12%; transform: scaleX(-1); }}
    @keyframes ss-popper {{
        0% {{ opacity: 0; translate: 0 20px; }}
        8% {{ opacity: 1; translate: 0 -6px; }}
        14% {{ translate: 0 0; }}
        85% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    .cf {{
        position: absolute;
        bottom: 40px;
        width: 8px;
        height: 12px;
        opacity: 0;
        animation: ss-confetti 1.6s cubic-bezier(0.15, 0.6, 0.35, 1) forwards;
    }}
    .cf-left {{ left: calc(12% + 20px); }}
    .cf-right {{ right: calc(12% + 20px); }}
    @keyframes ss-confetti {{
        0% {{ opacity: 1; transform: translate(0, 0) rotate(0deg); }}
        60% {{ opacity: 1; }}
        100% {{ opacity: 0; transform: translate(var(--dx), calc(var(--dy) + 120px)) rotate(var(--spin)); }}
    }}
    .ss-caption {{
        margin-top: 6px;
        color: #C9C9E8;
        font-size: 14px;
        font-weight: 600;
    }}
</style>
<script>
    setTimeout(function() {{
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        // Sing-song "Yaaayyy!": a stretched high note that swoops up.
        var yay = new SpeechSynthesisUtterance('Yaaaaaay!');
        yay.volume = 1.0;
        yay.pitch = 2.0;
        yay.rate = 0.7;
        var yay2 = new SpeechSynthesisUtterance('Yaaaay!');
        yay2.volume = 1.0;
        yay2.pitch = 2.0;
        yay2.rate = 0.85;
        window.speechSynthesis.speak(yay);
        window.speechSynthesis.speak(yay2);
    }}, 600);
</script>
"""
