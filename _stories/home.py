"""
The home page, rebuilt around real photos from KEYSA's work.

Called by build.py. Reads the pristine export (_stories/home-template.html)
and keeps its header, footer and three sections word for word (Projects,
Values, the closing call to action). It replaces the rest:

  hero        the original words, with a photo collage instead of a text card
  ribbon      a slowly scrolling strip of photos from the field
  numbers     the same four figures, counting up on a green band
  programs    the same five programs, each with a photo
  mission     the mission statement over a full-width photo
  stories     the three latest news stories

Everything new uses the export's own utility classes plus a small <style>
block (kh-*) built on the site's colour variables, so dark mode keeps working.
"""
import re

from build import ARROW, STORIES, card, e, make_static

SITE = "https://www.keysa.org"

STYLE = """<style>
.kh-collage{position:relative;height:540px}
.kh-ph{position:absolute;overflow:hidden;border-radius:28px;border:6px solid var(--color-ink-800);box-shadow:0 30px 60px -30px rgba(10,30,15,.55);background:var(--color-ink-700)}
.kh-ph img{width:100%;height:100%;object-fit:cover;display:block}
.kh-ph-a{left:6%;top:4%;width:72%;height:62%;transform:rotate(-2deg);animation:khFloat 9s ease-in-out infinite}
.kh-ph-b{right:0;top:30%;width:46%;height:40%;transform:rotate(4deg);animation:khFloat 11s ease-in-out infinite reverse}
.kh-ph-c{left:0;bottom:0;width:52%;height:36%;transform:rotate(-5deg);animation:khFloat 10s ease-in-out infinite}
.kh-chip{position:absolute;z-index:2;display:flex;align-items:center;gap:10px;padding:10px 14px;border-radius:16px;background:var(--color-ink-800);border:1px solid var(--color-ink-600);box-shadow:0 18px 40px -22px rgba(10,30,15,.6);font-size:.8rem;line-height:1.25;color:var(--color-mist-200);max-width:230px}
.kh-chip b{display:block;font-size:1.05rem;color:var(--color-green-400)}
.kh-chip-dot{flex:none;width:34px;height:34px;border-radius:12px;display:grid;place-items:center;background:color-mix(in srgb,var(--color-green-400) 14%,transparent);color:var(--color-green-400);font-size:1.1rem}
.kh-chip-1{right:2%;top:2%;animation:khFloat 7s ease-in-out infinite}
.kh-chip-2{left:46%;bottom:6%;animation:khFloat 8s ease-in-out infinite reverse}
@keyframes khFloat{0%,100%{translate:0 0}50%{translate:0 -10px}}
@media (max-width:1023px){
  .kh-collage{height:auto;display:grid;grid-template-columns:1.4fr 1fr;grid-template-rows:170px 170px;gap:12px}
  .kh-ph{position:relative;inset:auto;width:auto;height:auto;transform:none;animation:none;border-width:4px;border-radius:20px}
  .kh-ph-a{grid-row:1/3}
  .kh-chip{display:none}
}
.kh-ribbon{overflow:hidden;-webkit-mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent);mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent)}
.kh-track{display:flex;gap:16px;width:max-content;animation:khScroll 70s linear infinite}
.kh-ribbon:hover .kh-track,.kh-ribbon:focus-within .kh-track{animation-play-state:paused}
@keyframes khScroll{to{transform:translateX(calc(-50% - 8px))}}
.kh-tile{position:relative;flex:none;width:300px;height:200px;border-radius:20px;overflow:hidden;border:1px solid var(--color-ink-600);background:var(--color-ink-700)}
.kh-tile img{width:100%;height:100%;object-fit:cover;transition:transform .7s cubic-bezier(.16,1,.3,1)}
.kh-tile:hover img{transform:scale(1.07)}
.kh-tile span{position:absolute;inset:auto 0 0 0;padding:28px 14px 12px;font-size:.8rem;font-weight:600;color:#fff;background:linear-gradient(transparent,rgba(5,10,5,.82))}
@media (prefers-reduced-motion:reduce){.kh-track{animation:none}.kh-ribbon{overflow-x:auto}.kh-ph,.kh-chip{animation:none}}
.kh-band{position:relative;overflow:hidden;background:linear-gradient(120deg,#0b5a2f 0%,#12804a 55%,#0a4d29 100%);color:#fff}
.kh-band::before{content:"";position:absolute;inset:0;background:radial-gradient(600px 220px at 85% -10%,rgba(255,255,255,.16),transparent 70%),radial-gradient(500px 200px at 0% 120%,rgba(220,47,60,.25),transparent 70%)}
.kh-band .kh-num{font-size:clamp(2.4rem,5vw,3.4rem);font-weight:700;line-height:1;color:#fff}
.kh-band .kh-lbl{margin-top:8px;font-size:.88rem;color:rgba(255,255,255,.78)}
.kh-zoom{overflow:hidden}
.kh-zoom img{transition:transform .7s cubic-bezier(.16,1,.3,1)}
.kh-zoom:hover img{transform:scale(1.06)}
.kh-pill{position:absolute;left:16px;top:16px;display:inline-flex;align-items:center;gap:8px;padding:6px 12px 6px 6px;border-radius:999px;background:rgba(255,255,255,.92);color:#0e3b22;font-size:.75rem;font-weight:700}
.kh-pill i{display:grid;place-items:center;width:26px;height:26px;border-radius:999px;background:#157f47;color:#fff;font-style:normal}
.kh-pill svg{width:15px;height:15px}
.kh-mission{position:relative;overflow:hidden;color:#fff}
.kh-mission>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.kh-mission::after{content:"";position:absolute;inset:0;background:linear-gradient(100deg,rgba(4,16,8,.92) 0%,rgba(4,16,8,.78) 45%,rgba(4,16,8,.35) 100%)}
.kh-mission>div{position:relative;z-index:1}
.kh-quote{font-size:clamp(1.5rem,3.2vw,2.35rem);line-height:1.3;font-weight:600;color:#fff}
.kh-tick{display:flex;align-items:flex-start;gap:10px;color:rgba(255,255,255,.85);font-size:.95rem}
.kh-tick svg{flex:none;width:20px;height:20px;margin-top:1px;color:#3ddc7d}
.kh-ghost{display:inline-flex;align-items:center;gap:8px;border:1px solid rgba(255,255,255,.45);color:#fff;border-radius:999px;padding:12px 22px;font-size:.875rem;font-weight:600;transition:background .2s}
.kh-ghost:hover{background:rgba(255,255,255,.12);color:#fff;text-decoration:none}
</style>"""

COUNT_JS = """<script>
(function(){
  var els=document.querySelectorAll('[data-count]');
  function run(el){var to=+el.getAttribute('data-count'),suf=el.getAttribute('data-suffix')||'',t0=null;
    function f(t){if(!t0)t0=t;var p=Math.min(1,(t-t0)/1400);el.textContent=Math.round(to*(1-Math.pow(1-p,3)))+suf;if(p<1)requestAnimationFrame(f);}
    requestAnimationFrame(f);}
  if(!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion: reduce)').matches){els.forEach(function(el){el.textContent=el.getAttribute('data-count')+(el.getAttribute('data-suffix')||'');});return;}
  var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){run(x.target);io.unobserve(x.target);}});},{threshold:.4});
  els.forEach(function(el){io.observe(el);});
})();
</script>"""

TICK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"></path></svg>'

RIBBON = [
    ("/news/stories/13-1.jpg", "Basketball for the Wanga Kingdom Warriors", "/news/#from-the-field"),
    ("/news/stories/10-1.jpg", "A tea-hawking business, up and running", "/news/#from-the-field"),
    ("/news/httc-2026-group.jpg", "4th International Conference on Human Trafficking", "/news/human-trafficking-conference-2026/"),
    ("/news/stories/12-1.jpg", "Green jobs: interlocking block-making", "/news/#from-the-field"),
    ("/news/stories/06-1.jpg", "400+ in Kisumu against youth trafficking", "/news/kisumu-ending-youth-trafficking/"),
    ("/news/stories/02-1.jpg", "Skills for economic empowerment", "/news/#from-the-field"),
    ("/news/stories/01-1.jpg", "Restoring the Nairobi River", "/news/nairobi-river-restoration/"),
    ("/news/nairobi-forum.jpg", "Youth empowerment forum, Nairobi", "/news/nairobi-youth-empowerment-forum/"),
    ("/news/stories/07-1.jpg", "Mentorship: believe in yourself", "/news/#from-the-field"),
    ("/news/stories/11-1.jpg", "Giving to homes and rescue centres", "/news/giving-to-homes-and-rescue-centres/"),
    ("/news/stories/09-1.jpg", "Safeguarding training with Interpol", "/news/interpol-seah-capacity-building/"),
    ("/news/stories/03-2.jpg", "Evaluating skills training at Rarieda", "/news/irmt-monitoring-rarieda/"),
]

# Program page -> photo shown on its card.
PROGRAM_PHOTO = {
    "/programs/education/": ("Education", "/news/stories/02-1.jpg", "Young women in a hands-on skills training session"),
    "/programs/sports-and-talents/": ("Sports & talents", "/news/stories/13-1.jpg", "Young basketball players receiving a ball from KEYSA"),
    "/programs/technology/": ("Technology", "/news/stories/08-1.jpg", "Young people in a learning session with KEYSA partners"),
    "/programs/financial-literacy/": ("Financial literacy", "/news/stories/10-1.jpg", "A young man with the supplies for his new business"),
    "/programs/community-development/": ("Climate & community", "/news/stories/12-1.jpg", "Interlocking blocks made by young people"),
}


def sections(main):
    out, depth, start = [], 0, 0
    for t in re.finditer(r"<(/?)section\b", main):
        if not t.group(1):
            if depth == 0:
                start = t.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                out.append((start, main.find(">", t.start()) + 1))
    return out


def hero(original):
    # Keep the original left column (badge, headline, text, buttons) as is.
    left = original[original.find('<div class="hero-stagger">'):original.find('<div class="reveal reveal-scale')]
    bg = original[original.find(">") + 1:original.find('<div class="container-page')]
    collage = (
        '<div class="reveal reveal-scale" style="transition-delay:120ms"><div class="kh-collage">'
        '<div class="kh-ph kh-ph-a"><img alt="Young basketball players celebrating a ball donation from KEYSA" width="1600" height="1200" fetchpriority="high" src="/news/stories/13-1.jpg"/></div>'
        '<div class="kh-ph kh-ph-b"><img alt="Delegates at the 4th International Conference on Human Trafficking" width="1600" height="1066" src="/news/httc-2026-group.jpg"/></div>'
        '<div class="kh-ph kh-ph-c"><img alt="A young entrepreneur with the supplies for his tea business" width="1600" height="1066" src="/news/stories/10-1.jpg"/></div>'
        '<div class="kh-chip kh-chip-1"><span class="kh-chip-dot">🤝</span><span><b>400+</b>voices in Kisumu against youth trafficking</span></div>'
        '<div class="kh-chip kh-chip-2"><span class="kh-chip-dot">🌱</span><span><b>Green jobs</b>for young people in our communities</span></div>'
        "</div></div>"
    )
    return (f'<section class="relative overflow-hidden border-b border-ink-600">{bg}'
            f'<div class="container-page relative grid items-center gap-12 py-16 sm:py-24 lg:grid-cols-[1.15fr_0.85fr]">{left}{collage}</div></section>')


def ribbon():
    def tiles(hidden):
        attrs = ' aria-hidden="true" tabindex="-1"' if hidden else ""
        return "".join(
            f'<a class="kh-tile" href="{href}"{attrs}><img alt="{"" if hidden else e(cap)}" loading="lazy" width="300" height="200" src="{src}"/><span>{e(cap)}</span></a>'
            for src, cap, href in RIBBON)
    return ('<section class="py-14" aria-label="Photos from our programs">'
            '<div class="container-page mb-4 flex flex-wrap items-end justify-between gap-3">'
            '<p class="kicker flex items-center gap-2.5 "><span class="inline-block h-px w-8 bg-green-400" aria-hidden="true"></span>Life at KEYSA</p>'
            f'<a class="inline-flex items-center gap-1.5 text-sm font-semibold text-green-400" href="/news/">See all our stories{ARROW}</a></div>'
            f'<div class="kh-ribbon"><div class="kh-track">{tiles(False)}{tiles(True)}</div></div></section>')


def numbers():
    stats = [(5, "", "Thematic program areas"), (600, "+", "Youth targeted across active projects"),
             (100, "k", "Trees in our reforestation goal"), (8, "", "Teams in our first community tournament")]
    items = "".join(
        f'<div class="reveal reveal-up  " style="transition-delay:{i * 80}ms"><div class="text-center">'
        f'<p class="font-display kh-num" data-count="{n}" data-suffix="{suf}">{n}{suf}</p><p class="kh-lbl">{e(lbl)}</p></div></div>'
        for i, (n, suf, lbl) in enumerate(stats))
    return f'<section class="kh-band"><div class="container-page relative grid grid-cols-2 gap-8 py-14 lg:grid-cols-4">{items}</div></section>'


def programs(original):
    """Same section, but every program card leads with a photo."""
    sec = original
    def photo_card(m):
        a = m.group(0)
        href = re.search(r'href="([^"]+)"', a).group(1)
        if href not in PROGRAM_PHOTO:
            return a
        label, src, alt = PROGRAM_PHOTO[href]
        icon = re.search(r'(<span class="inline-flex h-12 w-12[^"]*">)(<svg.*?</svg>)</span>', a, flags=re.S)
        a = a.replace('class="group flex h-full flex-col rounded-2xl border border-ink-600 bg-ink-800 p-7 ',
                      'class="group kh-zoom flex h-full flex-col overflow-hidden rounded-2xl border border-ink-600 bg-ink-800 ', 1)
        a = a.replace(icon.group(0), "", 1)
        head = (f'<div class="relative kh-zoom"><img alt="{e(alt)}" loading="lazy" width="800" height="450" class="aspect-video w-full object-cover" src="{src}"/>'
                f'<span class="kh-pill"><i>{icon.group(2)}</i>{e(label)}</span></div><div class="flex flex-1 flex-col p-7">')
        a = re.sub(r'(<a [^>]*>)', lambda mm: mm.group(1) + head, a, count=1)
        a = a.replace('<h3 class="mt-5 ', '<h3 class="', 1)
        return a[:-4] + "</div></a>"
    return re.sub(r'<a class="group flex h-full flex-col rounded-2xl[^"]*" href="/programs/[^"]+/">.*?</a>', photo_card, sec, flags=re.S)


def mission():
    return ('<section class="kh-mission"><img alt="" loading="lazy" width="1040" height="520" src="/news/stories/06-1.jpg"/>'
            '<div class="container-page py-20 sm:py-28"><div class="max-w-2xl">'
            '<span class="inline-flex items-center gap-1.5 rounded-full bg-green-400 px-3 py-1 text-xs font-bold text-on-accent">Our mission</span>'
            '<blockquote class="font-display kh-quote mt-6">“To empower youth by providing them with opportunities and resources in education, sports, technology and financial literacy.”</blockquote>'
            '<div class="mt-8 space-y-3">'
            f'<p class="kh-tick">{TICK}Youth are the primary drivers of any nation&#x27;s development</p>'
            f'<p class="kh-tick">{TICK}Inclusive by design — every background, equal opportunity</p>'
            f'<p class="kh-tick">{TICK}Serving Bungoma, Kakamega, Busia and Nairobi counties</p></div>'
            '<div class="mt-8 flex flex-wrap gap-3"><a class="inline-flex items-center justify-center gap-2 rounded-full px-6 py-3 text-sm font-semibold transition-colors duration-200 bg-accent-400 text-on-red hover:bg-accent-500" href="/get-involved/">Get involved</a>'
            '<a class="kh-ghost" href="/about/">Our story</a></div></div></div></section>')


def latest():
    cards = "".join(card(s, i * 80) for i, s in enumerate(STORIES[:3]))
    return ('<section class="py-20 sm:py-24"><div class="container-page">'
            '<div class="flex flex-wrap items-end justify-between gap-4"><div class="max-w-2xl">'
            '<p class="kicker mb-3 flex items-center gap-2.5 "><span class="inline-block h-px w-8 bg-green-400" aria-hidden="true"></span>Latest news</p>'
            '<h2 class="font-display text-3xl font-bold tracking-tight text-mist-100 sm:text-4xl text-balance">Fresh from the field</h2>'
            '<p class="mt-4 text-base leading-relaxed text-mist-400">What our team and our young people have been up to lately.</p></div>'
            f'<a class="inline-flex items-center gap-1.5 rounded-full border border-ink-500 px-5 py-2.5 text-sm font-semibold text-mist-200 hover:border-green-400 hover:text-mist-100" href="/news/">All news &amp; stories{ARROW}</a></div>'
            f'<div class="mt-10 grid gap-5 lg:grid-cols-3">{cards}</div></div></section>')


def build_home(tpl):
    page = make_static(tpl)
    i, j = page.find("<main"), page.find("</main>")
    main = page[i:j]
    secs = sections(main)
    assert len(secs) == 6, f"expected 6 home sections, found {len(secs)}"
    S = [main[a:b] for a, b in secs]
    # 0 hero, 1 numbers, 2 programs, 3 projects, 4 values, 5 call to action
    body = (hero(S[0]) + ribbon() + numbers() + programs(S[2]) + mission() + latest()
            + S[3] + S[4] + S[5])
    head_end = main.find(">") + 1
    new_main = main[:head_end] + body + main[secs[-1][1]:]
    page = page[:i] + new_main + page[j:]
    page = page.replace("</head>", STYLE + "</head>", 1)
    page = page.replace("</body>", COUNT_JS + "</body>", 1)
    return page
