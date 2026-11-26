#!/usr/bin/env python3
"""
Build KEYSA's news stories into the static site.

The site is a compiled Next.js export (see README.md): its pages cannot be
edited at the source. So new stories are written as plain HTML pages that
reuse the export's own stylesheet, header and footer — they look identical,
but carry no Next.js runtime. A few lines of vanilla JS stand in for what the
runtime did on these pages: the mobile menu, the light/dark switch and the
fade-in on scroll.

    python3 _stories/build.py                 rebuild pages from STORIES below
    python3 _stories/build.py --photos DIR    also (re)import photos from DIR
                                              (the Facebook export's KEYSA_posts/)

What it writes:
    news/index.html               the News page: new stories first, then the
                                  original ones, then a "From the field" grid
    news/<slug>/index.html        one page per story
    news/stories/*.jpg            photos, max 1600px
    sitemap.xml                   story URLs added

It reads only the two pristine templates saved beside it, so running it twice
gives the same result. To add a story: add an entry to STORIES (or FIELD for a
captioned photo), put its photos in news/stories/, run this, commit.
"""
import html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "_stories")
SITE = "https://www.keysa.org"
CSS = os.path.join(ROOT, "_next/static/chunks/1i05tt5ae0r1h.css")

# ---------------------------------------------------------------- content --
# Text from KEYSA's Facebook page (export of 25 Nov 2026), lightly edited for
# spelling and flow. "src" = folder number and photo number in that export.
STORIES = [
    {
        "slug": "nairobi-river-restoration",
        "tag": "Climate action",
        "kicker": "Climate action · Nairobi",
        "title": "Reclaiming the Nairobi River: KEYSA Joins the Push for Climate Action",
        "summary": "KEYSA joined like-minded organisations in Nairobi to deliberate on restoring the Nairobi River — and on stopping the encroachment of its riparian land.",
        "body": [
            "KEYSA, alongside like-minded organisations in Nairobi, participated in an engagement focused on the reclamation and restoration of the Nairobi River as a critical component of climate change mitigation and environmental conservation.",
            "The engagement gave stakeholders an opportunity to deliberate on practical measures for restoring the river ecosystem, promoting environmental sustainability and strengthening community participation in climate action.",
            "Discussions also addressed the growing encroachment on riparian land by private-sector entities and institutions, highlighting the need for stronger enforcement of environmental regulations and protection of riparian areas.",
            "Through this engagement, KEYSA reaffirmed its commitment to championing climate action, environmental conservation and sustainable urban development in Nairobi.",
        ],
        "photos": [
            ("01", 1, "Participants at the Nairobi River restoration engagement follow a presentation",
             "Stakeholders deliberate on practical measures to restore the Nairobi River."),
        ],
    },
    {
        "slug": "irmt-monitoring-rarieda",
        "tag": "Monitoring & evaluation",
        "kicker": "Monitoring & evaluation · Rarieda",
        "title": "Monitoring and Evaluation of the IRMT Pilot Program at Rarieda",
        "summary": "KEYSA assessed the Integrated Rural Maintenance and Training pilot at Rarieda Training and Resource Centre — and whether multi-trade NITA courses make trainees more versatile.",
        "body": [
            "KEYSA conducted a monitoring and evaluation exercise for the Integrated Rural Maintenance and Training (IRMT) pilot program at Rarieda Training and Resource Centre (RTRC).",
            "The exercise sought to assess the effectiveness and relevance of integrating NITA core courses, enabling trainees to acquire broader, multi-trade skills and become more versatile and competent professionals.",
        ],
        "photos": [
            ("03", 2, "The KEYSA monitoring and evaluation team outside Rarieda Training and Resource Centre",
             "The evaluation team at Rarieda Training and Resource Centre."),
            ("03", 5, "A session with trainees and staff during the IRMT evaluation", ""),
            ("03", 1, "The resource centre library at Rarieda", ""),
            ("03", 4, "Team members during the evaluation exercise", ""),
        ],
    },
    {
        "slug": "kisumu-ending-youth-trafficking",
        "tag": "Anti-trafficking",
        "kicker": "Anti-trafficking · Kisumu",
        "title": "Over 400 Voices in Kisumu for Ending Human Trafficking Among the Youth",
        "summary": "A stakeholder convening in Kisumu brought together more than 400 participants under the theme Ending Human Trafficking Among the Youth.",
        "body": [
            "KEYSA took part in a stakeholder convening in Kisumu that brought together more than 400 participants under the theme Ending Human Trafficking Among the Youth.",
            "KEYSA remains at the forefront of advocating for human rights and dignity, especially among vulnerable groups.",
        ],
        "photos": [
            ("06", 1, "Participants seated under a tent at the Kisumu stakeholder convening on ending human trafficking",
             "More than 400 participants gathered in Kisumu."),
        ],
    },
    {
        "slug": "interpol-seah-capacity-building",
        "tag": "Safeguarding",
        "kicker": "Safeguarding · Capacity building",
        "title": "Strengthening Safeguarding: KEYSA in an Interpol Capacity-Building Program",
        "summary": "A high-level program with Interpol on preventing sexual exploitation, abuse and harassment (SEAH) in the aid and humanitarian sector.",
        "body": [
            "KEYSA participated in a high-level capacity-building program in collaboration with Interpol, focused on Preventing Sexual Exploitation, Abuse and Harassment (SEAH) in the Aid and Humanitarian Sector. It brought together law enforcement and humanitarian actors to strengthen coordinated responses to safeguarding risks.",
            "The workshop enhanced our practical understanding of survivor-centred approaches, inter-agency collaboration and accountability mechanisms, while equipping us with tools to identify, prevent and respond to SEAH within vulnerable communities.",
            "It also deepened our ability to bridge gaps between enforcement systems and humanitarian practice, reinforcing our commitment to promoting ethical standards, protection frameworks and safer programming environments in anti-trafficking and community-based interventions.",
        ],
        "photos": [
            ("09", 1, "Participants of the Interpol capacity-building program on preventing sexual exploitation, abuse and harassment",
             "Law enforcement and humanitarian actors at the SEAH capacity-building program."),
        ],
    },
    {
        "slug": "giving-to-homes-and-rescue-centres",
        "tag": "Community",
        "kicker": "Community · Partnerships",
        "title": "Partnership and Giving: Supporting Homes and Rescue Centres",
        "summary": "Through collaborative efforts, KEYSA donates clothes and other essential materials to homes and rescue centres.",
        "body": [
            "Caring for humanity — and especially for the disadvantaged — is a calling we are all mandated to uphold.",
            "And as the saying goes, it takes two to tango. KEYSA plays a key role in supporting the less fortunate in society through collaborative efforts, donating clothes and other essential materials to homes and rescue centres.",
        ],
        "photos": [
            ("11", 1, "KEYSA team members with bags of donated clothes and supplies for homes and rescue centres",
             "Donations ready for delivery to homes and rescue centres."),
        ],
    },
]

# Short posts: a captioned photo in the "From the field" grid on the News page.
FIELD = [
    ("10", 1, "From the field", "A young man with the supplies for his new tea-hawking business",
     "Providing an unemployed young man with the essential support and supplies to start a tea-hawking business — an income of his own and a better livelihood."),
    ("12", 1, "Green jobs", "Stacks of interlocking blocks made by young people",
     "Interlocking block-making project: green jobs that build youth employability and combat climate change, contributing to poverty alleviation and community development."),
    ("13", 1, "Sports & talents", "KEYSA handing a basketball to the Wanga Kingdom Warriors team",
     "Basketball donation to the Wanga Kingdom Warriors."),
    ("02", 1, "Economic empowerment", "Young women in a hands-on skills training session",
     "An economic empowerment initiative for young people."),
    ("07", 1, "Mentorship", "A KEYSA facilitator speaking with a group of young people",
     "A candid talk with young people, encouraging them to believe in themselves and stay focused on their life goals."),
    ("08", 1, "Partnerships", "KEYSA partners in discussion with program beneficiaries",
     "A group of our partners engaging some of our program beneficiaries. Knowledge is power."),
]

# ------------------------------------------------------------------ helpers --
e = lambda s: html.escape(s, quote=True)


def photo_name(folder, n):
    return f"/news/stories/{folder}-{n}.jpg"


def import_photos(src_dir):
    out = os.path.join(ROOT, "news/stories")
    os.makedirs(out, exist_ok=True)
    wanted = {(f, n) for s in STORIES for (f, n, *_rest) in s["photos"]}
    wanted |= {(f, n) for (f, n, *_rest) in FIELD}
    for folder, n in sorted(wanted):
        match = [d for d in os.listdir(src_dir) if d.startswith(folder + " ")]
        if not match:
            sys.exit(f"no folder {folder} in {src_dir}")
        src = os.path.join(src_dir, match[0], f"photo_{n}.jpg")
        dst = os.path.join(ROOT, photo_name(folder, n).lstrip("/"))
        # Fit within 1600px, drop metadata (camera, location), web quality.
        subprocess.run(["convert", src, "-auto-orient", "-resize", "1600x1600>",
                        "-strip", "-quality", "82", dst], check=True)
        print("photo", dst.replace(ROOT + "/", ""))


def image_size(path):
    out = subprocess.run(["identify", "-format", "%w %h", path],
                         capture_output=True, text=True, check=True).stdout.split()
    return int(out[0]), int(out[1])


def img(folder, n, alt, cls, lazy=True):
    w, h = image_size(os.path.join(ROOT, photo_name(folder, n).lstrip("/")))
    loading = ' loading="lazy"' if lazy else ""
    return (f'<img alt="{e(alt)}"{loading} width="{w}" height="{h}" decoding="async" '
            f'class="{cls}" src="{photo_name(folder, n)}"/>')


# Stands in for the Next.js runtime on these static pages.
RUNTIME_JS = """<script>
(function(){
  var header=document.querySelector('header');
  var btn=document.querySelector('button[aria-controls="mobile-nav"]');
  var NAV=%s;
  var OPEN='<path d="M4 7h16M4 12h16M4 17h16"></path>', CLOSE='<path d="m6 6 12 12M18 6 6 18"></path>';
  if(btn&&header){btn.addEventListener('click',function(){
    var nav=document.getElementById('mobile-nav');
    if(nav){nav.remove();btn.setAttribute('aria-expanded','false');btn.setAttribute('aria-label','Open menu');btn.querySelector('svg').innerHTML=OPEN;}
    else{header.insertAdjacentHTML('beforeend',NAV);btn.setAttribute('aria-expanded','true');btn.setAttribute('aria-label','Close menu');btn.querySelector('svg').innerHTML=CLOSE;}
  });}
  var t=document.querySelector('button[aria-label*="theme"]');
  function label(){var d=document.documentElement.getAttribute('data-theme')==='dark';if(t)t.setAttribute('aria-label',d?'Switch to light theme':'Switch to dark theme');}
  if(t){label();t.addEventListener('click',function(){
    var d=document.documentElement.getAttribute('data-theme')==='dark';
    if(d){document.documentElement.removeAttribute('data-theme');}else{document.documentElement.setAttribute('data-theme','dark');}
    try{localStorage.setItem('keysa-theme',d?'light':'dark');}catch(e){}
    label();
  });}
  var els=document.querySelectorAll('.reveal');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('reveal-in');io.unobserve(x.target);}});},{rootMargin:'0px 0px -40px 0px'});
    els.forEach(function(el){io.observe(el);});
  } else { els.forEach(function(el){el.classList.add('reveal-in');}); }
})();
</script>"""

MOBILE_NAV = (
    '<nav id="mobile-nav" aria-label="Mobile" class="border-t border-ink-600 bg-ink-900 lg:hidden"><div class="container-page flex flex-col gap-1 py-4">'
    + "".join(
        ('<a aria-current="page" ' if label == "News" else "<a ")
        + 'class="rounded-xl px-4 py-3 text-base font-medium '
        + ("bg-green-400/10 text-green-300" if label == "News" else "text-mist-300 hover:bg-ink-850")
        + f'" href="{href}">{label}</a>'
        for label, href in [("About", "/about/"), ("Programs", "/programs/"), ("Projects", "/projects/"),
                            ("Get Involved", "/get-involved/"), ("News", "/news/"), ("Contact", "/contact/")])
    + '<a class="mt-2 inline-flex items-center justify-center gap-2 rounded-full bg-accent-400 px-5 py-3 text-sm font-semibold text-on-red" href="/donate/">Donate</a></div></nav>'
)


def make_static(page):
    """Strip the Next.js runtime, keep the theme pre-paint script and JSON-LD."""
    def keep(m):
        tag, body = m.group(1), m.group(2)
        if "__next" in body:  # the Next.js data stream (it quotes the theme script too)
            return ""
        if body.lstrip().startswith("(function(){try{var t=localStorage") or "application/ld+json" in tag:
            return m.group(0)
        return ""
    page = re.sub(r"<script([^>]*)>(.*?)</script>", keep, page, flags=re.S)
    page = re.sub(r'<link rel="preload" as="script"[^>]*/>', "", page)
    page = page.replace("</body>", RUNTIME_JS % json.dumps(MOBILE_NAV) + "</body>")
    return page


def set_meta(page, title, description, url, image):
    full = f"{title} | KEYSA"
    page = re.sub(r"<title>.*?</title>", f"<title>{e(full)}</title>", page, count=1)
    reps = {
        r'<meta name="description" content="[^"]*"': f'<meta name="description" content="{e(description)}"',
        r'<meta property="og:title" content="[^"]*"': f'<meta property="og:title" content="{e(full)}"',
        r'<meta property="og:description" content="[^"]*"': f'<meta property="og:description" content="{e(description)}"',
        r'<meta property="og:url" content="[^"]*"': f'<meta property="og:url" content="{url}"',
        r'<link rel="canonical" href="[^"]*"': f'<link rel="canonical" href="{url}"',
        r'<meta name="twitter:title" content="[^"]*"': f'<meta name="twitter:title" content="{e(full)}"',
        r'<meta name="twitter:description" content="[^"]*"': f'<meta name="twitter:description" content="{e(description)}"',
    }
    for pat, rep in reps.items():
        page = re.sub(pat, lambda _m, r=rep: r, page, count=1)
    if image:
        # Facebook / WhatsApp previews show the story's own photo.
        page = re.sub(r'<meta property="og:image" content="[^"]*"', f'<meta property="og:image" content="{SITE}{image}"', page, count=1)
        page = re.sub(r'<meta name="twitter:image" content="[^"]*"', f'<meta name="twitter:image" content="{SITE}{image}"', page, count=1)
        for k in ("og:image:width", "og:image:height", "og:image:type", "og:image:alt"):
            page = re.sub(rf'<meta property="{k}" content="[^"]*"/>', "", page, flags=re.S)
        for k in ("twitter:image:width", "twitter:image:height", "twitter:image:type", "twitter:image:alt"):
            page = re.sub(rf'<meta name="{k}" content="[^"]*"/>', "", page, flags=re.S)
    return page


ARROW = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="h-4 w-4 transition-transform group-hover:translate-x-1"><path d="M4 12h16m0 0-6-6m6 6-6 6"></path></svg>'


def badge(text):
    return f'<span class="inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium border-green-400/30 bg-green-400/10 text-green-300">{e(text)}</span>'


# ------------------------------------------------------------- story pages --
def story_page(tpl, s):
    url = f"{SITE}/news/{s['slug']}/"
    first = s["photos"][0]
    page = make_static(tpl)
    page = set_meta(page, s["title"], s["summary"], url, photo_name(first[0], first[1]))
    page = re.sub(r'<link rel="preload" as="image" href="/news/[^"]*"/>',
                  f'<link rel="preload" as="image" href="{photo_name(first[0], first[1])}"/>', page)
    # JSON-LD article
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": s["title"],
          "author": {"@type": "Organization", "name": "KEYSA Communications"},
          "publisher": {"@type": "NGO", "name": "Kenya Youth Support Association", "url": SITE},
          "description": s["summary"], "image": SITE + photo_name(first[0], first[1]), "url": url}
    page = re.sub(r'(<script type="application/ld\+json">)\{"@context":"https://schema.org","@type":"Article".*?(</script>)',
                  lambda m: m.group(1) + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + m.group(2), page, flags=re.S)
    # hero
    page = re.sub(r'(<span class="inline-block h-px w-8 bg-green-400" aria-hidden="true"></span>)[^<]*(</p><h1)',
                  lambda m: m.group(1) + e(s["kicker"]) + m.group(2), page, count=1)
    page = re.sub(r'(<h1 class="[^"]*">)[^<]*(</h1>)', lambda m: m.group(1) + e(s["title"]) + m.group(2), page, count=1)
    page = re.sub(r'<p class="mt-5 text-sm font-medium text-mist-500">By .*?</p>',
                  '<p class="mt-5 text-sm font-medium text-mist-500">By <span class="text-mist-200">KEYSA Communications</span> · News &amp; Events</p>',
                  page, count=1, flags=re.S)
    # article
    fig = (f'<figure class="mx-auto mb-12 max-w-3xl">'
           + img(first[0], first[1], first[2], "w-full rounded-2xl border border-ink-600 object-cover shadow-[0_24px_50px_-32px_rgba(15,40,20,0.45)]", lazy=False)
           + (f'<figcaption class="mt-3 text-center text-xs leading-relaxed text-mist-500">{e(first[3])}</figcaption>' if first[3] else "")
           + "</figure>")
    prose = "".join(f"<p>{e(p)}</p>" for p in s["body"])
    gallery = ""
    if len(s["photos"]) > 1:
        gallery = ('<div class="mx-auto mt-12 grid max-w-3xl gap-4 sm:grid-cols-2">'
                   + "".join(img(f, n, alt, "aspect-video w-full rounded-2xl border border-ink-600 object-cover")
                             for (f, n, alt, _c) in s["photos"][1:])
                   + "</div>")
    article = (f'<article class="py-16 sm:py-20"><div class="container-page">{fig}'
               f'<div class="prose-ngo mx-auto max-w-2xl text-base text-mist-300">{prose}'
               f'<p class="!mb-0 border-t border-ink-600 pt-6 text-sm font-semibold text-mist-500">— KEYSA Communications, News &amp; Events, KEYSA</p></div>'
               f"{gallery}</div></article>")
    page = re.sub(r"<article.*?</article>", lambda _m: article, page, count=1, flags=re.S)
    return page


# --------------------------------------------------------------- news page --
def card(s, delay):
    f, n, alt, _c = s["photos"][0]
    return (f'<div class="reveal reveal-up  " style="transition-delay:{delay}ms"><a class="group flex h-full flex-col overflow-hidden rounded-2xl border border-ink-600 bg-ink-800 transition-all duration-300 hover:-translate-y-1 hover:border-green-400/50" href="/news/{s["slug"]}/">'
            + img(f, n, alt, "aspect-video w-full border-b border-ink-600 object-cover")
            + f'<div class="flex flex-1 flex-col p-7"><div class="flex items-center gap-2">{badge(s["tag"])}</div>'
            f'<h2 class="mt-4 font-display text-xl font-bold text-mist-100 group-hover:text-green-300">{e(s["title"])}</h2>'
            f'<p class="mt-2 text-sm font-medium text-mist-500">By KEYSA Communications · News &amp; Events</p>'
            f'<p class="mt-3 flex-1 text-sm leading-relaxed text-mist-400">{e(s["summary"])}</p>'
            f'<span class="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-green-400">Read more{ARROW}</span></div></a></div>')


def field_section():
    items = "".join(
        f'<div class="reveal reveal-up  " style="transition-delay:{(i % 3) * 80}ms"><figure class="flex h-full flex-col overflow-hidden rounded-2xl border border-ink-600 bg-ink-800">'
        + img(f, n, alt, "aspect-video w-full border-b border-ink-600 object-cover")
        + f'<figcaption class="flex flex-1 flex-col gap-3 p-6"><div>{badge(tag)}</div><p class="text-sm leading-relaxed text-mist-300">{e(cap)}</p></figcaption></figure></div>'
        for i, (f, n, tag, alt, cap) in enumerate(FIELD))
    return ('<section class="border-t border-ink-600 bg-ink-850 py-16 sm:py-20"><div class="container-page">'
            '<div class="max-w-3xl"><p class="kicker mb-3 flex items-center gap-2.5 "><span class="inline-block h-px w-8 bg-green-400" aria-hidden="true"></span>From the field</p>'
            '<h2 class="font-display text-3xl font-bold tracking-tight text-mist-100 text-balance">Moments from our programs</h2>'
            '<p class="mt-4 text-base leading-relaxed text-mist-400">Snapshots of the everyday work: livelihoods, green jobs, sport and mentorship across our communities.</p></div>'
            f'<div class="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{items}</div>'
            '<p class="mt-10 text-sm text-mist-500">Follow more of our work on <a class="font-semibold text-green-400 hover:text-green-300" href="https://www.facebook.com/profile.php?id=61583833030180">Facebook</a>.</p>'
            "</div></section>")


def news_page(tpl):
    page = make_static(tpl)
    cards = "".join(card(s, (i % 2) * 80) for i, s in enumerate(STORIES))
    marker = '<div class="grid gap-5 md:grid-cols-2">'
    assert page.count(marker) == 1, "news grid not found"
    page = page.replace(marker, marker + cards, 1)
    # Re-number the original cards' stagger so the pairs stay in step.
    end = page.find("</section>", page.find(marker))
    page = page[:end + len("</section>")] + field_section() + page[end + len("</section>"):]
    return page


# ----------------------------------------------------------------- checks --
def check_classes(pages):
    """Every class used must exist in the compiled CSS, or it silently does nothing."""
    css = open(CSS).read()
    used = set()
    for p in pages:
        for cls in re.findall(r'class="([^"]*)"', p):
            used.update(cls.split())
    missing = []
    for c in sorted(used):
        esc = re.sub(r"([:/\[\]().,!%#])", r"\\\1", c)
        if "." + esc not in css and c not in ("group", "reveal-up", "kicker", "hero-stagger", "container-page", "prose-ngo", "tricolor", "bg-grid", "glow-bg", "reveal"):
            missing.append(c)
    if missing:
        print("WARNING: classes not in the stylesheet:", " ".join(missing))


def sitemap():
    path = os.path.join(ROOT, "sitemap.xml")
    sm = open(path).read()
    for s in STORIES:
        loc = f"{SITE}/news/{s['slug']}/"
        if loc not in sm:
            sm = sm.replace("</urlset>", f"<url><loc>{loc}</loc><changefreq>yearly</changefreq><priority>0.6</priority></url>\n</urlset>")
    open(path, "w").write(sm)


def main():
    if "--photos" in sys.argv:
        import_photos(sys.argv[sys.argv.index("--photos") + 1])
    art_tpl = open(os.path.join(HERE, "article-template.html")).read()
    news_tpl = open(os.path.join(HERE, "news-template.html")).read()
    pages = []
    for s in STORIES:
        out = os.path.join(ROOT, "news", s["slug"])
        os.makedirs(out, exist_ok=True)
        p = story_page(art_tpl, s)
        open(os.path.join(out, "index.html"), "w").write(p)
        pages.append(p)
        print("page ", f"news/{s['slug']}/")
    p = news_page(news_tpl)
    open(os.path.join(ROOT, "news/index.html"), "w").write(p)
    pages.append(p)
    print("page  news/")
    # The News page is now static: drop its Next.js payloads, so a click on
    # "News" from any other page does a normal page load of this HTML instead
    # of rendering the old, pre-built list.
    for f in os.listdir(os.path.join(ROOT, "news")):
        if f.endswith(".txt"):
            os.remove(os.path.join(ROOT, "news", f))
    sitemap()
    check_classes(pages)


if __name__ == "__main__":
    main()
