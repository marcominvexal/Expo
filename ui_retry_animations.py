"""HTML/CSS for Gemini retry wait screen and sync success character — girly pink theme."""


def gemini_retry_wait_html(remaining_seconds, total_timeout_left):
    return f"""
    <div class="hd-wait-container">
        <div class="hd-status">
            <span class="pulse-dot">💗</span>
            <strong>ちょっと待ってね〜! Gemini-chan needs a tiny breather (๑˃ᴗ˂)ﻭ</strong>
            Retrying in <span>{remaining_seconds}s</span>
            ({total_timeout_left}s sparkle-time left ✨)
        </div>
        <div class="hd-stage">
            <div class="hd-walker">
                <div class="hd-bow">🎀</div>
                <div class="hd-antenna">
                    <div class="hd-bulb"></div>
                    <div class="hd-stem"></div>
                </div>
                <div class="hd-head">
                    <div class="hd-glass-visor">
                        <div class="hd-blush hd-blush-l"></div>
                        <div class="hd-eye-glow"></div>
                        <div class="hd-eye-glow"></div>
                        <div class="hd-blush hd-blush-r"></div>
                    </div>
                </div>
                <div class="hd-body"><div class="hd-dial">♡</div></div>
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
            50% {{ transform: translateY(-14px) scale(1.02); }}
            100% {{ transform: translateY(0px) scale(1); }}
        }}
        @keyframes hd-walk-L {{
            0% {{ transform: rotate(-32deg); }}
            100% {{ transform: rotate(32deg); }}
        }}
        @keyframes hd-walk-R {{
            0% {{ transform: rotate(32deg); }}
            100% {{ transform: rotate(-32deg); }}
        }}
        @keyframes eye-shimmer {{
            0%, 100% {{ opacity: 0.75; box-shadow: 0 0 10px #f472b6; }}
            50% {{ opacity: 1; box-shadow: 0 0 18px #e879f9; }}
        }}
        @keyframes bow-wiggle {{
            0%, 100% {{ transform: rotate(-8deg); }}
            50% {{ transform: rotate(8deg); }}
        }}
        .hd-wait-container {{
            background: linear-gradient(135deg, #fff0f6 0%, #fce7f3 50%, #fae8ff 100%);
            border: 2px solid #f9a8d4;
            border-radius: 24px;
            padding: 24px;
            box-shadow: 0 12px 40px rgba(236, 72, 153, 0.25);
            font-family: 'Quicksand', system-ui, sans-serif;
            color: #9d174d;
        }}
        .hd-status {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            font-size: 14px;
            letter-spacing: 0.3px;
            text-align: center;
            flex-wrap: wrap;
            font-weight: 600;
        }}
        .hd-status span {{ color: #db2777; font-weight: 800; }}
        .pulse-dot {{
            font-size: 16px;
            animation: eye-shimmer 1s infinite alternate;
            flex-shrink: 0;
        }}
        .hd-stage {{
            height: 150px;
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
            animation: hd-bounce 0.55s ease-in-out infinite;
        }}
        .hd-bow {{
            font-size: 22px;
            margin-bottom: -4px;
            animation: bow-wiggle 1.2s ease-in-out infinite;
        }}
        .hd-antenna {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .hd-bulb {{
            width: 10px;
            height: 10px;
            background: linear-gradient(135deg, #f9a8d4, #ec4899);
            border-radius: 50%;
            box-shadow: 0 0 14px #f472b6;
        }}
        .hd-stem {{ width: 3px; height: 10px; background: #f9a8d4; }}
        .hd-head {{
            width: 58px;
            height: 44px;
            background: linear-gradient(135deg, #fbcfe8 0%, #f9a8d4 100%);
            border-radius: 16px;
            padding: 3px;
            box-shadow: inset 0 2px 4px rgba(255,255,255,0.7), 0 4px 12px rgba(236,72,153,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .hd-glass-visor {{
            width: 100%;
            height: 100%;
            background: rgba(255, 240, 246, 0.95);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}
        .hd-eye-glow {{
            width: 10px;
            height: 10px;
            background: #ec4899;
            border-radius: 50%;
            animation: eye-shimmer 0.5s infinite alternate;
        }}
        @keyframes blush-glow {{
            0%, 100% {{ opacity: 0.55; transform: scale(1); }}
            50% {{ opacity: 0.95; transform: scale(1.18); }}
        }}
        .hd-blush {{
            width: 7px;
            height: 5px;
            background: radial-gradient(circle, #fb7185 0%, rgba(251,113,133,0) 70%);
            border-radius: 50%;
            animation: blush-glow 1.4s ease-in-out infinite;
        }}
        .hd-body {{
            width: 66px;
            height: 50px;
            background: linear-gradient(135deg, #e879f9 0%, #c084fc 100%);
            border-radius: 10px;
            margin-top: -1px;
            box-shadow: inset 0 2px 3px rgba(255,255,255,0.5), 0 4px 12px rgba(192,132,252,0.35);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .hd-dial {{
            font-size: 14px;
            color: #fff;
            font-weight: 700;
        }}
        .hd-legs {{ display: flex; gap: 16px; margin-top: -2px; }}
        .hd-leg {{
            width: 10px;
            height: 22px;
            background: #f472b6;
            border-radius: 5px;
            transform-origin: top center;
        }}
        .hd-left {{ animation: hd-walk-L 0.5s ease-in-out infinite alternate; }}
        .hd-right {{ animation: hd-walk-R 0.5s ease-in-out infinite alternate; }}
        .hd-shadow {{
            width: 50px;
            height: 6px;
            background: rgba(219, 39, 119, 0.25);
            border-radius: 50%;
            margin-top: 4px;
            filter: blur(1px);
        }}
    </style>
    """


SYNC_SUCCESS_CHARACTER_HTML = """
<div class="hd-box">
    <div class="hd-bubble">やったー！ Sync done — your funnel is all pretty and updated! ♡(◍•ᴗ•◍)♡ 💖✨</div>
    <div class="hd-avatar">
        <div class="hd-bow-top">🎀</div>
        <div class="hd-antenna-main">
            <div class="hd-orb"></div>
            <div class="hd-wire"></div>
        </div>
        <div class="hd-robot-face">
            <div class="hd-screen-inner">
                <div class="hd-eyes-container">
                    <div class="hd-cheek hd-cheek-l"></div>
                    <div class="hd-neon-eye"></div>
                    <div class="hd-neon-eye"></div>
                    <div class="hd-cheek hd-cheek-r"></div>
                </div>
                <div class="hd-speaking-mouth"></div>
            </div>
        </div>
        <div class="hd-torso"><div class="hd-core-light">♡</div></div>
        <div class="hd-floor-shadow"></div>
    </div>
</div>
<style>
    @keyframes float-hd {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(2deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    @keyframes eye-blink-hd {
        0%, 92%, 100% { transform: scaleY(1); }
        96% { transform: scaleY(0.1); }
    }
    @keyframes hd-baby-talk {
        0%, 100% { height: 4px; border-radius: 2px; width: 18px; background: #ec4899; }
        50% { height: 12px; border-radius: 50%; width: 14px; background: #f472b6; }
    }
    @keyframes bow-spin {
        0%, 100% { transform: rotate(-10deg) scale(1); }
        50% { transform: rotate(10deg) scale(1.1); }
    }
    .hd-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 22px;
        background: linear-gradient(135deg, #fff0f6 0%, #fce7f3 50%, #fae8ff 100%);
        border-radius: 28px;
        border: 2px solid #f9a8d4;
        box-shadow: 0 20px 50px rgba(236, 72, 153, 0.3);
        animation: float-hd 3s ease-in-out infinite;
        font-family: 'Quicksand', system-ui, sans-serif;
    }
    .hd-bubble {
        position: relative;
        background: linear-gradient(135deg, #fbcfe8 0%, #f9a8d4 100%);
        border-radius: 22px;
        padding: 16px 24px;
        font-weight: 800;
        color: #831843;
        max-width: 320px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(244, 114, 182, 0.35);
        margin-bottom: 22px;
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
        border-color: #f9a8d4 transparent;
    }
    .hd-bow-top {
        font-size: 28px;
        margin-bottom: 2px;
        animation: bow-spin 2s ease-in-out infinite;
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
        background: linear-gradient(135deg, #f472b6, #e879f9);
        border-radius: 50%;
        box-shadow: 0 0 15px #f472b6;
    }
    .hd-wire { width: 4px; height: 12px; background: #f9a8d4; }
    .hd-robot-face {
        width: 92px;
        height: 70px;
        background: linear-gradient(135deg, #fbcfe8 0%, #f9a8d4 100%);
        border-radius: 24px;
        padding: 5px;
        box-shadow: inset 0 2px 4px rgba(255,255,255,0.6), 0 10px 25px rgba(236,72,153,0.25);
    }
    .hd-screen-inner {
        width: 100%;
        height: 100%;
        background: #fff0f6;
        border-radius: 18px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 8px;
        position: relative;
        overflow: hidden;
    }
    .hd-screen-inner::before {
        content: '✨';
        position: absolute;
        top: 4px;
        right: 8px;
        font-size: 12px;
        opacity: 0.7;
    }
    .hd-eyes-container { display: flex; gap: 14px; align-items: center; }
    @keyframes cheek-glow {
        0%, 100% { opacity: 0.6; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.2); }
    }
    .hd-cheek {
        width: 10px;
        height: 7px;
        background: radial-gradient(circle, #fb7185 0%, rgba(251,113,133,0) 72%);
        border-radius: 50%;
        animation: cheek-glow 1.5s ease-in-out infinite;
    }
    .hd-neon-eye {
        width: 14px;
        height: 14px;
        background: linear-gradient(135deg, #ec4899 0%, #d946ef 100%);
        border-radius: 50%;
        box-shadow: 0 0 12px #f472b6;
        animation: eye-blink-hd 4s infinite;
    }
    .hd-speaking-mouth {
        width: 18px;
        height: 4px;
        background: #ec4899;
        border-radius: 2px;
        box-shadow: 0 0 6px #f472b6;
        animation: hd-baby-talk 0.22s ease-in-out infinite alternate;
    }
    .hd-torso {
        width: 62px;
        height: 32px;
        background: linear-gradient(135deg, #e879f9 0%, #c084fc 100%);
        border-radius: 0 0 18px 18px;
        margin: -1px auto 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 16px rgba(192, 132, 252, 0.35);
    }
    .hd-core-light {
        font-size: 14px;
        color: #fff;
        font-weight: 700;
    }
    .hd-floor-shadow {
        width: 70px;
        height: 6px;
        background: rgba(219, 39, 119, 0.25);
        border-radius: 50%;
        margin-top: 12px;
        filter: blur(2px);
    }
</style>
<script>
    (function() {
        // ✨ cute sparkle chime (Web Audio) — a little kawaii arpeggio
        function playChime() {
            try {
                var AC = window.AudioContext || window.webkitAudioContext;
                if (!AC) return;
                var ctx = new AC();
                if (ctx.state === 'suspended') { ctx.resume(); }
                // bright major-pentatonic sparkle: C6 E6 G6 C7 E7
                var notes = [1046.5, 1318.5, 1568.0, 2093.0, 2637.0];
                notes.forEach(function(freq, i) {
                    var t = ctx.currentTime + i * 0.085;
                    var osc = ctx.createOscillator();
                    var gain = ctx.createGain();
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(freq, t);
                    gain.gain.setValueAtTime(0.0001, t);
                    gain.gain.exponentialRampToValueAtTime(0.18, t + 0.02);
                    gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.45);
                    osc.connect(gain).connect(ctx.destination);
                    osc.start(t);
                    osc.stop(t + 0.5);
                });
            } catch (e) {}
        }

        // 🎀 cute Japanese female voice
        function pickJapaneseVoice(voices) {
            var female = voices.filter(function(v) {
                return /ja(-|_)JP/i.test(v.lang) || /japanese|日本語|kyoko|haruka|o-?ren|nanami|sayaka|ayumi/i.test(v.name);
            });
            // Prefer known female JP voices, else first JP voice, else any.
            var preferred = female.find(function(v) {
                return /kyoko|haruka|nanami|sayaka|ayumi|o-?ren|google 日本語/i.test(v.name);
            });
            return preferred || female[0] || null;
        }

        function speak() {
            if (!window.speechSynthesis) return;
            window.speechSynthesis.cancel();
            var phrase = new SpeechSynthesisUtterance(
                'やったー！同期完了だよっ！ファネルが全部きれいに更新されました！'
            );
            phrase.lang = 'ja-JP';
            var voice = pickJapaneseVoice(window.speechSynthesis.getVoices());
            if (voice) { phrase.voice = voice; phrase.lang = voice.lang; }
            phrase.volume = 1.0;
            phrase.pitch = 1.9;   // very cute / high
            phrase.rate = 1.08;
            phrase.onend = function() {
                var mouth = document.querySelector('.hd-speaking-mouth');
                if (mouth) {
                    mouth.style.animation = 'none';
                    mouth.style.height = '4px';
                    mouth.style.width = '18px';
                }
            };
            window.speechSynthesis.speak(phrase);
        }

        setTimeout(function() {
            playChime();
            // Voices can load asynchronously; wait for them if needed.
            if (window.speechSynthesis && window.speechSynthesis.getVoices().length === 0) {
                window.speechSynthesis.onvoiceschanged = function() {
                    window.speechSynthesis.onvoiceschanged = null;
                    speak();
                };
                setTimeout(speak, 600);
            } else {
                speak();
            }
        }, 350);
    })();
</script>
"""
