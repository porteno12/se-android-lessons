"""
התרשימים והציורים של המדריך, כ-SVG. stages.py מרחיב את הסימונים:
  {{DIAGRAM:name|כיתוב}}   תרשים מהרשימה DIAGRAMS
  {{PHONE:name|כיתוב}}     ציור של הטלפון: איך המשחק אמור להיראות בסוף שלב
צבעי המסגרות והטקסט מגיעים מה-CSS של המדריך (class); צבעי המשחק עצמו קבועים כאן, כמו ב-colors.xml.
"""
import html
import re

GREEN, YELLOW, GRAY = '#6AAA64', '#C9B458', '#787C7E'
PRIMARY, INK, KEY_BG, SCREEN_BG = '#538D4E', '#1A1A2E', '#D3D6DA', '#F7F7F7'
STATE = {'c': GREEN, 'p': YELLOW, 'a': GRAY}


class D:
    def __init__(self, name, w, h):
        self.name, self.w, self.h, self.p = name, w, h, []

    def rect(self, x, y, w, h, cls='box', rx=10, fill=None, stroke=None, dash=False):
        st = ''
        if fill:
            st += 'fill:%s;' % fill
        if stroke:
            st += 'stroke:%s;' % stroke
        if dash:
            st += 'stroke-dasharray:6 4;'
        self.p.append('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" class="%s"%s/>'
                      % (x, y, w, h, rx, cls, ' style="%s"' % st if st else ''))

    def t(self, x, y, s, cls='', anchor='middle', size=None, weight=None, fill=None):
        """טקסט. מחרוזת שמתחילה ב-` היא קוד: גופן קוד, משמאל לימין."""
        code = s.startswith('`')
        if code:
            s = s[1:]
            cls = (cls + ' code').strip()
        st = ''
        if size:
            st += 'font-size:%spx;' % size
        if weight:
            st += 'font-weight:%s;' % weight
        if fill:
            st += 'fill:%s;' % fill
        self.p.append('<text x="%s" y="%s" text-anchor="%s" direction="%s"%s%s>%s</text>'
                      % (x, y, anchor, 'ltr' if code else 'rtl',
                         ' class="%s"' % cls if cls else '', ' style="%s"' % st if st else '',
                         html.escape(s)))

    def box(self, x, y, w, h, lines, cls='box', size=None, fill=None, dash=False):
        self.rect(x, y, w, h, cls, fill=fill, dash=dash)
        lh = (size or 15) + 8
        top = y + h / 2 - (len(lines) - 1) * lh / 2 + 5
        for i, s in enumerate(lines):
            self.t(x + w / 2, top + i * lh, s, size=size)

    def arrow(self, pts, label=None, lx=None, ly=None, cls='arr', lcls='dim', anchor='middle'):
        d = 'M%s,%s ' % pts[0] + ' '.join('L%s,%s' % p for p in pts[1:])
        self.p.append('<path d="%s" class="%s" marker-end="url(#ah-%s)"/>' % (d, cls, self.name))
        if label:
            if lx is None:
                (x1, y1), (x2, y2) = pts[0], pts[-1]
                lx, ly = (x1 + x2) / 2, (y1 + y2) / 2 - 8
            self.t(lx, ly, label, cls=lcls, anchor=anchor)

    def svg(self, label):
        return ('<svg class="dg" viewBox="0 0 %s %s" role="img" aria-label="%s">'
                '<defs><marker id="ah-%s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="ahead"/></marker></defs>%s</svg>'
                % (self.w, self.h, html.escape(label), self.name, ''.join(self.p)))


def tile(d, x, y, s, letter='', state=None):
    fill = STATE.get(state, '#FFFFFF')
    d.p.append('<rect x="%s" y="%s" width="%s" height="%s" rx="3" style="fill:%s;stroke:%s;stroke-width:1.5"/>'
               % (x, y, s, s, fill, fill if state else '#9AA0A6'))
    if letter:
        d.t(x + s / 2, y + s / 2 + s * 0.2, letter, size=round(s * 0.55), weight=700,
            fill='#FFFFFF' if state else INK)


def window(d, x, y, w, h, title):
    """חלון של אנדרואיד סטודיו: מסגרת עם פס כותרת."""
    d.rect(x, y, w, h, 'win', rx=8)
    d.rect(x, y, w, 26, 'winbar', rx=8)
    for i, c in enumerate(('#FF5F57', '#FEBC2E', '#28C840')):
        d.p.append('<circle cx="%s" cy="%s" r="5" style="fill:%s"/>' % (x + 14 + i * 16, y + 13, c))
    d.t(x + w / 2, y + 18, '`' + title, size=12, cls='dim')


# ============================================================ step 1

def newproject():
    d = D('newproject', 720, 300)
    window(d, 20, 10, 680, 280, 'New Project')
    d.t(60, 62, '`Phone and Tablet', anchor='start', size=13, cls='dim')
    names = ['No Activity', 'Empty Activity', 'Empty Views Activity', 'Basic Views Activity']
    for i, n in enumerate(names):
        x = 50 + i * 160
        sel = n == 'Empty Views Activity'
        d.rect(x, 80, 145, 130, 'box green' if sel else 'box', rx=8,
               fill='rgba(125,224,125,.16)' if sel else None)
        d.rect(x + 45, 98, 55, 80, 'mini', rx=6)
        d.t(x + 72, 200, '`' + n, size=11)
    d.arrow([(310, 250), (270, 214)])
    d.t(320, 255, 'בוחרים את זה', anchor='end', weight=700)
    d.t(560, 255, '"Empty Activity" היא Compose – לא בשבילנו', cls='dim')
    return d


def projectform():
    d = D('projectform', 720, 260)
    window(d, 20, 10, 680, 240, 'New Project – Empty Views Activity')
    fields = [('Name', 'HebrewWordle'), ('Package name', 'com.example.hebrewwordle'),
              ('Language', 'Java'), ('Minimum SDK', 'API 24 ("Nougat"; Android 7.0)')]
    for i, (k, v) in enumerate(fields):
        y = 52 + i * 46
        d.t(60, y + 20, '`' + k, anchor='start', size=13, cls='dim')
        d.rect(220, y, 440, 30, 'field', rx=5)
        d.t(232, y + 20, '`' + v, anchor='start', size=13)
    d.rect(560, 222, 100, 22, 'box green', rx=5)
    d.t(610, 238, '`Finish', size=12)
    return d


def projecttree():
    d = D('projecttree', 720, 300)
    window(d, 20, 10, 330, 280, 'Project  ▾ Android')
    rows = [(0, '▾ app', False), (1, '▾ manifests', False), (1, '▾ java', False),
            (2, '▾ com.example.hebrewwordle', False), (3, 'MainActivity', True), (1, '▾ res', False),
            (2, '▸ drawable', False), (2, '▾ layout', False), (3, 'activity_main.xml', True), (2, '▸ values', False)]
    for i, (lvl, s, hi) in enumerate(rows):
        y = 52 + i * 23
        if hi:
            d.rect(36, y - 15, 300, 21, 'box green', rx=4, fill='rgba(125,224,125,.18)')
        d.t(44 + lvl * 18, y, '`' + s, anchor='start', size=13)
    d.box(420, 70, 280, 60, ['`MainActivity.java', 'קוד Java: מה המסך עושה'], 'box blue', size=14)
    d.box(420, 180, 280, 60, ['`activity_main.xml', 'XML: איך המסך נראה'], 'box yellow', size=14)
    d.arrow([(418, 100), (240, 145)])
    d.arrow([(418, 210), (290, 237)])
    return d


def files():
    d = D('files', 720, 240)
    d.box(500, 40, 200, 84, ['`MainActivity.java', 'מה המסך עושה'], 'box blue')
    d.box(20, 40, 200, 84, ['`activity_main.xml', 'איך המסך נראה'], 'box yellow')
    d.arrow([(500, 82), (222, 82)])
    d.t(360, 70, '`setContentView(R.layout.activity_main)', size=13)
    d.t(360, 104, 'ה-Java טוען את ה-XML', cls='dim')
    d.box(250, 165, 220, 56, ['המסך שהמשתמש רואה'], 'box green')
    d.arrow([(600, 124), (430, 163)])
    d.arrow([(120, 124), (290, 163)])
    return d


# ============================================================ step 2

def lifecycle():
    d = D('lifecycle', 720, 330)
    ys = [20, 105, 190, 275]
    names = [['הפעילות לא קיימת'], ['נוצרה: המסך נבנה'], ['מוצגת על המסך'], ['פעילה: אפשר ללחוץ']]
    for i, (y, n) in enumerate(zip(ys, names)):
        d.box(250, y, 220, 44, n, 'box green' if i == 3 else 'box', dash=(i == 0))
    downs = ['`onCreate()', '`onStart()', '`onResume()']
    ups = ['`onDestroy()', '`onStop()', '`onPause()']
    for i in range(3):
        y, yn = ys[i], ys[i + 1]
        d.arrow([(470, y + 15), (510, y + 15), (510, yn + 15), (473, yn + 15)])
        d.t(522, (y + yn) / 2 + 22, downs[i], anchor='start')
        d.arrow([(250, yn + 30), (210, yn + 30), (210, y + 30), (247, y + 30)])
        d.t(198, (y + yn) / 2 + 36, ups[i], anchor='end')
    d.t(640, 14, 'נכנסים ↓', cls='dim')
    d.t(80, 14, '↑ יוצאים', cls='dim')
    return d


def override():
    d = D('override', 720, 230)
    d.box(200, 10, 320, 80, ['`AppCompatActivity', 'הקוד של אנדרואיד', '`onStart() { ... }'], 'box', size=14)
    d.box(200, 140, 320, 80, ['`MainActivity', 'הקוד שלנו', '`@Override onStart()'], 'box blue', size=14)
    d.arrow([(360, 140), (360, 92)], 'extends – יורשת', 450, 120, anchor='start')
    d.t(610, 175, '`super.onStart();', anchor='middle')
    d.t(610, 198, 'קודם החלק של אנדרואיד', cls='dim')
    d.t(110, 175, '`Log.d(...);', anchor='middle')
    d.t(110, 198, 'ואחריו החלק שלנו', cls='dim')
    return d


def println():
    d = D('println', 720, 190)
    d.box(390, 20, 310, 66, ['יחידה 1: תוכנית Java', '`System.out.println("...")'], 'box', size=14)
    d.box(20, 20, 310, 66, ['אפליקציית אנדרואיד', '`Log.d(TAG, "...")'], 'box blue', size=14)
    d.arrow([(545, 86), (545, 130)])
    d.arrow([(175, 86), (175, 130)])
    d.box(390, 132, 310, 44, ['חלון ה-Console'], 'box', size=14)
    d.box(20, 132, 310, 44, ['חלון ה-Logcat'], 'box green', size=14)
    d.t(360, 60, '≈', size=30, weight=700)
    return d


def logcat():
    d = D('logcat', 720, 270)
    d.box(30, 12, 660, 44, ['`Log.d(TAG, "onStart - המסך מוצג");'], 'box blue')
    d.arrow([(360, 56), (360, 92)], 'מופיע בחלון Logcat', 470, 80)
    window(d, 30, 95, 660, 160, 'Logcat')
    d.rect(44, 128, 300, 24, 'field', rx=4)
    d.t(56, 145, '`tag:LIFECYCLE', anchor='start', size=13)
    d.t(352, 145, '← כאן כותבים את הסינון', anchor='start', cls='dim')
    lines = ['D  LIFECYCLE  onCreate - הפעילות נוצרת', 'D  LIFECYCLE  onStart - המסך מוצג',
             'D  LIFECYCLE  onResume - אפשר ללחוץ על המסך']
    for i, s in enumerate(lines):
        d.t(52, 180 + i * 24, '`' + s, anchor='start', size=14, cls='hl' if i == 1 else '')
    return d


def rotate():
    d = D('rotate', 720, 280)

    def row(y, title, chips):
        d.t(700, y - 14, title, anchor='start', weight=700)
        x = 700
        for i, (s, kind) in enumerate(chips):
            w = 98
            cls = {'n': 'box', 'g': 'box green', 'o': 'box orange', 'd': 'box'}[kind]
            d.box(x - w, y, w, 40, [s], cls, size=13, dash=(kind == 'd'))
            if i < len(chips) - 1:
                d.arrow([(x - w, y + 20), (x - w - 14, y + 20)])
            x -= w + 16

    row(40, 'לוחצים על כפתור הבית, ואחר כך חוזרים למשחק',
        [('`onPause', 'n'), ('`onStop', 'n'), ('המשחק ברקע', 'd'), ('`onStart', 'n'), ('`onResume', 'n')])
    row(165, 'מסובבים את הטלפון',
        [('`onPause', 'n'), ('`onStop', 'n'), ('`onDestroy', 'o'), ('`onCreate', 'g'),
         ('`onStart', 'n'), ('`onResume', 'n')])
    d.t(408, 236, 'נהרסת', cls='dim')
    d.t(294, 236, 'נוצרת מחדש', cls='dim')
    d.t(360, 266, 'בסיבוב, הפעילות הישנה נהרסת ונבנית פעילות חדשה – מאפס', weight=700)
    return d


# ============================================================ step 3

def xml_view():
    d = D('xml_view', 720, 240)
    d.rect(20, 15, 230, 210, 'box', fill=SCREEN_BG)
    d.t(135, 70, 'ווֹרדל בעברית', size=22, weight=700, fill=PRIMARY)
    d.t(135, 100, 'נחשו מילה בת 5 אותיות...', size=12, fill=INK)
    d.rect(300, 15, 400, 210, 'term', rx=8)
    code = ['<TextView', '    android:id="@+id/txtTitle"', '    android:text="@string/title"',
            '    android:textColor="@color/primary"', '    android:textSize="28sp" />']
    for i, s in enumerate(code):
        d.t(318, 50 + i * 30, '`' + s, anchor='start', size=14, cls='hl' if i == 0 else '')
    d.arrow([(300, 45), (240, 64)])
    d.t(500, 212, 'תגית = רכיב על המסך · מאפיין = איך הוא נראה', cls='dim')
    return d


def linear():
    d = D('linear', 720, 300)
    d.rect(230, 32, 260, 255, 'box green', dash=True)
    d.t(360, 22, '`LinearLayout  orientation="vertical"')
    items = [('1', 'כותרת', ''), ('2', 'הודעה', ''), ('3', 'לוח', 'בשלב 4'), ('4', 'מקלדת', 'בשלב 5')]
    for i, (n, s, later) in enumerate(items):
        y = 50 + i * 58
        d.box(255, y, 210, 44, [s], 'box', dash=bool(later))
        d.t(480, y + 28, n, cls='dim', anchor='start')
        if later:
            d.t(240, y + 28, 'נוסיף ' + later, cls='dim', anchor='start')
    d.arrow([(560, 60), (560, 260)])
    d.t(580, 160, 'הסדר בקובץ', anchor='start')
    d.t(580, 182, '= הסדר על המסך', anchor='start')
    return d


def sizes():
    d = D('sizes', 720, 215)
    d.rect(40, 32, 640, 168, 'box', dash=True)
    d.t(360, 22, 'ההורה: ה-LinearLayout (כל רוחב המסך)', cls='dim')
    d.box(55, 50, 610, 46, ['כל הרוחב של ההורה'], 'box blue')
    d.t(70, 79, '`match_parent', anchor='start')
    d.box(465, 128, 200, 46, ['כמה שהתוכן צריך'], 'box yellow')
    d.t(450, 157, '`wrap_content', anchor='end')
    return d


def resources():
    d = D('resources', 720, 260)
    for x, s in [(595, 'בתבנית כותבים שם'), (355, 'הערך יושב בקובץ'), (125, 'מה שמופיע בפועל')]:
        d.t(x, 22, s, cls='dim')
    rows = [('`@string/title', '`strings.xml', None, 'ווֹרדל בעברית'),
            ('`@color/primary', '`colors.xml', PRIMARY, ''),
            ('`@dimen/screen_padding', '`dimens.xml', None, '12dp')]
    for i, (ref, f, sw, val) in enumerate(rows):
        y = 40 + i * 72
        d.box(490, y, 210, 48, [ref], 'box yellow', size=14)
        d.box(280, y, 150, 48, [f], 'box', size=14)
        d.arrow([(490, y + 24), (432, y + 24)])
        d.arrow([(280, y + 24), (232, y + 24)])
        if sw:
            d.rect(30, y, 190, 48, 'box', fill=sw)
            d.t(125, y + 30, '`#538D4E', fill='#FFFFFF')
        else:
            d.box(30, y, 190, 48, [val], 'box green')
    return d


def units():
    d = D('units', 720, 190)
    for i, (cnt, lab) in enumerate([(4, 'טלפון רגיל'), (8, 'טלפון חד (יותר פיקסלים)')]):
        x = 460 if i == 0 else 100
        d.rect(x, 20, 160, 120, 'box')
        step = 80 / cnt
        for k in range(cnt + 1):
            d.p.append('<line x1="%s" y1="60" x2="%s" y2="140" class="grid"/>' % (x + 40 + k * step, x + 40 + k * step))
            d.p.append('<line x1="%s" y1="%s" x2="%s" y2="%s" class="grid"/>' % (x + 40, 60 + k * step, x + 120, 60 + k * step))
        d.rect(x + 40, 60, 80, 80, 'box green', rx=2, fill='rgba(125,224,125,.25)')
        d.t(x + 80, 45, '`52dp', size=14)
        d.t(x + 80, 165, lab, cls='dim')
    d.t(360, 80, '=', size=34, weight=700)
    d.t(360, 185, 'אותו גודל על המסך, גם כשמספר הפיקסלים שונה', weight=700)
    return d


# ============================================================ step 4

def weight():
    d = D('weight', 720, 290)
    d.rect(250, 15, 220, 262, 'box', fill=SCREEN_BG)
    d.t(360, 48, 'ווֹרדל בעברית', size=17, weight=700, fill=PRIMARY)
    d.t(360, 70, 'נחשו מילה בת 5 אותיות...', size=10, fill=INK)
    d.rect(262, 82, 196, 183, 'box green', dash=True, fill='rgba(125,224,125,.12)')
    d.t(360, 170, 'הלוח', size=16, weight=700, fill=INK)
    d.t(360, 192, 'כל הגובה שנשאר', size=12, fill=INK)
    for y, lab in [(45, '`wrap_content'), (68, '`wrap_content')]:
        d.arrow([(495, y), (472, y)])
        d.t(505, y + 5, lab, anchor='start')
    d.arrow([(495, 175), (472, 175)])
    d.t(505, 172, '`height="0dp"', anchor='start')
    d.t(505, 194, '`weight="1"', anchor='start')
    return d


def rtl():
    d = D('rtl', 720, 170)
    for i, (lab, order, word) in enumerate([('`ltr', [0, 1, 2, 3, 4], 'ש ו ל ח ן'), ('`rtl', [4, 3, 2, 1, 0], '')]):
        y = 30 + i * 70
        d.t(700, y + 28, lab, anchor='end')
        for k, c in enumerate(order):
            x = 330 + k * 56
            tile(d, x, y, 46, 'שולחן'[c], None)
            d.t(x + 23, y + 62, str(c), cls='dim', size=12)
    d.t(160, 58, 'טלפון באנגלית בלי rtl:', cls='dim')
    d.t(160, 80, 'המילה נקראת הפוך ✗', cls='dim')
    d.t(160, 128, 'עם rtl: עמודה 0 מימין ✓', weight=700)
    return d


def board():
    d = D('board', 720, 330)
    d.rect(190, 35, 340, 270, 'box green', dash=True)
    d.t(430, 24, '`boardContainer', anchor='end')
    d.t(440, 24, 'LinearLayout אנכי', anchor='end', cls='dim')
    for r in range(6):
        y = 50 + r * 42
        d.rect(205, y, 310, 36, 'box blue', rx=6)
        for c in range(5):
            tile(d, 278 + (4 - c) * 34, y + 4, 28, 'א' if (r, c) == (2, 0) else '')
    d.t(175, 70, 'כל שורה היא', anchor='start', cls='dim')
    d.t(175, 92, '`LinearLayout', anchor='end', cls='dim')
    d.t(175, 114, 'אופקי, עם 5 אריחים', anchor='start', cls='dim')
    d.arrow([(600, 155), (420, 155)])
    d.t(610, 160, '`tiles[2][0]', anchor='start')
    d.t(610, 182, 'שורה 2, עמודה 0', anchor='start', cls='dim')
    d.t(360, 325, 'עמודה 4   ←   ←   ←   עמודה 0', cls='dim')
    return d


def shape():
    d = D('shape', 720, 190)
    d.rect(400, 15, 300, 160, 'term', rx=8)
    for i, s in enumerate(['<shape android:shape="rectangle">', '  <solid  color=לבן />',
                           '  <stroke width=2dp color=אפור />', '  <corners radius=4dp />', '</shape>']):
        d.t(414, 45 + i * 28, '`' + s, anchor='start', size=13)
    d.arrow([(398, 95), (300, 95)])
    tile(d, 150, 35, 120, '')
    d.t(80, 60, 'מלבן', cls='dim')
    d.t(80, 95, 'מסגרת אפורה', cls='dim')
    d.t(80, 130, 'פינות מעוגלות', cls='dim')
    return d


def newview():
    d = D('newview', 720, 210)
    steps = [('`new TextView(this)', 'יוצרים אריח'), ('`setLayoutParams(...)', 'גודל ושוליים'),
             ('`setBackground(...)', 'הצורה מ-drawable'), ('`rowLayout.addView(tile)', 'מכניסים לשורה')]
    for i, (code, lab) in enumerate(steps):
        x = 540 - i * 175
        d.box(x - 12, 20, 172, 70, [code, lab], 'box blue' if i == 0 else 'box', size=11)
        if i < 3:
            d.arrow([(x - 12, 55), (x - 13, 55)])
    d.t(620, 125, '`this', anchor='middle')
    d.t(620, 148, 'הפעילות: האריח צריך לדעת', cls='dim')
    d.t(620, 170, 'לאיזה מסך הוא שייך', cls='dim')
    d.t(180, 135, 'בלי addView האריח קיים בזיכרון', cls='dim')
    d.t(180, 157, 'אבל לא מופיע על המסך', cls='dim')
    return d


# ============================================================ step 5

def event():
    d = D('event', 720, 175)
    d.box(500, 30, 200, 70, ['אצבע לוחצת', 'על המקש "ש"'], 'box yellow')
    d.box(260, 30, 200, 70, ['אנדרואיד מחפש', 'מי מאזין לכפתור'], 'box')
    d.box(20, 30, 200, 70, ['`onLetterKey(view)', 'המתודה שלנו רצה'], 'box green')
    d.arrow([(500, 65), (462, 65)])
    d.arrow([(260, 65), (222, 65)])
    d.t(120, 135, '`view')
    d.t(120, 160, 'הכפתור שנלחץ', cls='dim')
    return d


def ways():
    d = D('ways', 720, 225)
    cols = [('מקשי האותיות', '`android:onClick', 'ב-XML', '1', 'שלב 5'),
            ('מחק', 'הפעילות', 'מממשת', '2', 'שלב 6'),
            ('בדיקה', 'מחלקה', 'פנימית', '3', 'שלב 8'),
            ('משחק חדש', 'מאזין', 'אנונימי', '4', 'שלב 9')]
    for i, (btn, a, b, n, st) in enumerate(cols):
        x = 545 - i * 175
        d.rect(x, 15, 155, 44, 'box', fill=KEY_BG if i < 2 else (PRIMARY if i == 2 else SCREEN_BG))
        d.t(x + 77, 43, btn, fill='#FFFFFF' if i == 2 else INK, weight=700)
        d.arrow([(x + 77, 59), (x + 77, 88)])
        d.box(x, 90, 155, 70, [a, b], 'box green')
        d.t(x + 77, 188, 'דרך ' + n, weight=700)
        d.t(x + 77, 210, st, cls='dim')
    return d


def onclick_xml():
    d = D('onclick_xml', 720, 180)
    d.box(390, 30, 310, 70, ['`themes.xml  (KeyButton)', '`android:onClick="onLetterKey"'], 'box yellow', size=14)
    d.box(20, 30, 310, 70, ['`MainActivity.java', '`public void onLetterKey(View view)'], 'box blue', size=14)
    d.arrow([(390, 65), (332, 65)])
    d.t(360, 132, 'הקשר הוא השם בלבד. המהדר לא בודק אותו –', cls='dim')
    d.t(360, 156, 'טעות בשם תתגלה רק כשלוחצים', cls='dim')
    return d


def style():
    d = D('style', 720, 210)
    d.box(220, 10, 280, 92, ['`KeyButton', 'רוחב שווה · רקע אפור', '`onClick = onLetterKey'], 'box yellow', size=14)
    for i, k in enumerate(['ק', 'ר', 'א', 'ט', 'ו', '…']):
        x = 115 + i * 85
        d.rect(x, 150, 70, 44, 'box', fill=KEY_BG)
        d.t(x + 35, 178, k, fill=INK, weight=700)
        d.arrow([(360, 102), (x + 35, 148)])
    return d


def include():
    d = D('include', 720, 220)
    d.rect(420, 15, 280, 190, 'box', fill=SCREEN_BG)
    d.t(560, 40, '`activity_main.xml', fill=INK, size=13)
    for i, s in enumerate(['כותרת', 'הודעה', 'לוח']):
        d.rect(440, 52 + i * 34, 240, 28, 'box', rx=5)
        d.t(560, 71 + i * 34, s, size=13)
    d.rect(432, 156, 256, 36, 'box yellow', rx=5, dash=True)
    d.t(560, 179, '`<include layout="@layout/keyboard"/>', size=10)
    d.rect(20, 120, 280, 85, 'box yellow')
    d.t(160, 145, '`keyboard.xml', size=13)
    for r in range(3):
        for k in range(8):
            d.rect(40 + k * 30, 155 + r * 15, 26, 11, 'key', rx=2, fill=KEY_BG)
    d.arrow([(302, 165), (438, 174)])
    d.t(160, 100, 'המקלדת בקובץ משלה', cls='dim')
    return d


def cast():
    d = D('cast', 720, 160)
    d.box(470, 20, 230, 60, ['`View view', 'רכיב כלשהו על המסך'], 'box', size=14)
    d.box(20, 20, 260, 60, ['`((Button) view).getText()', '"ש"'], 'box green', size=14)
    d.arrow([(470, 50), (282, 50)], '`(Button)', 376, 38)
    d.t(376, 75, 'אנחנו יודעים שזה כפתור', cls='dim')
    d.t(360, 130, 'כמו ביחידה 1: המרה (casting) ממחלקת-אב למחלקת-בן', cls='dim')
    return d


def builder():
    d = D('builder', 720, 160)
    states = [('""', ''), ('"ש"', 'append(\'ש\')'), ('"של"', 'append(\'ל\')'), ('"ש"', 'deleteCharAt(1)')]
    for i, (v, op) in enumerate(states):
        x = 560 - i * 180
        d.box(x, 40, 140, 56, ['`' + v], 'box yellow' if i else 'box', size=16)
        if i:
            d.arrow([(x + 178, 68), (x + 142, 68)])
            d.t(x + 160, 120, '`' + op, size=12, cls='dim')
    d.t(380, 22, '`StringBuilder current', anchor='start', size=13)
    d.t(372, 22, 'מחרוזת שאפשר להוסיף לה ולמחוק ממנה', anchor='start', cls='dim')
    return d


# ============================================================ step 6

def listener_this():
    d = D('listener_this', 720, 200)
    d.rect(560, 60, 140, 50, 'box', fill=KEY_BG)
    d.t(630, 91, 'מחק', fill=INK, weight=700)
    d.box(20, 25, 330, 120, ['`MainActivity', '`implements View.OnClickListener', '`onClick(View view) { ... }'],
          'box blue', size=14)
    d.arrow([(560, 85), (352, 85)], '`setOnClickListener(this)', 455, 72)
    d.t(455, 112, 'this = הפעילות עצמה', cls='dim')
    d.t(360, 185, 'לחיצה על "מחק" ← אנדרואיד קורא ל-onClick של הפעילות', cls='dim')
    return d


def getid():
    d = D('getid', 720, 200)
    d.box(470, 60, 230, 70, ['`onClick(View view)', 'מי נלחץ?'], 'box blue', size=14)
    d.p.append('<path d="M470,95 L400,95" class="arr" marker-end="url(#ah-getid)"/>')
    d.box(230, 20, 160, 50, ['`R.id.btnDelete'], 'box yellow', size=13)
    d.box(230, 120, 160, 50, ['`R.id.btnCheck'], 'box', size=13, dash=True)
    d.arrow([(400, 95), (392, 45)])
    d.arrow([(400, 95), (392, 145)])
    d.box(20, 20, 170, 50, ['מוחקים אות'], 'box green', size=14)
    d.arrow([(230, 45), (192, 45)])
    d.t(105, 150, 'כפתור נוסף? עוד if', cls='dim')
    d.t(470, 175, '`view.getId()', size=13)
    return d


# ============================================================ step 7

def model():
    d = D('model', 720, 270)
    d.rect(20, 20, 300, 175, 'box green', dash=True)
    d.t(110, 42, '`model', anchor='middle')
    d.t(210, 42, 'Java רגיל', cls='dim')
    d.box(40, 55, 260, 40, ['`WordleGame'], 'box', size=14)
    d.box(40, 100, 125, 40, ['`Guess'], 'box', size=14)
    d.box(175, 100, 125, 40, ['`LetterState'], 'box', size=14)
    d.t(170, 175, 'חוקי המשחק – בלי אנדרואיד', cls='dim')
    d.box(480, 45, 220, 90, ['`MainActivity', 'הלוח, המקלדת, ההודעות'], 'box blue')
    d.arrow([(480, 75), (302, 75)])
    d.t(391, 64, 'מה הצבע של כל אות?', size=13)
    d.box(40, 215, 260, 42, ['בדיקות JUnit – על המחשב'], 'box yellow', size=14)
    d.arrow([(170, 215), (170, 197)])
    d.t(590, 175, 'החץ הולך רק לכיוון אחד:', cls='dim')
    d.t(590, 197, 'המודל לא מכיר את המסך', cls='dim')
    return d


def states():
    d = D('states', 720, 150)
    items = [('EMPTY', None, 'עוד לא נבדק'), ('ABSENT', 'a', 'לא במילה'),
             ('PRESENT', 'p', 'במילה, במקום אחר'), ('CORRECT', 'c', 'במקום הנכון')]
    for i, (n, st, lab) in enumerate(items):
        x = 590 - i * 175
        tile(d, x + 20, 15, 56, 'ש', st)
        d.t(x + 48, 100, '`' + n, size=13)
        d.t(x + 48, 125, lab, cls='dim')
    return d


def guessobj():
    d = D('guessobj', 720, 170)
    d.rect(180, 15, 360, 140, 'box blue')
    d.t(360, 38, '`Guess')
    d.t(520, 70, '`word = "מורים"', anchor='end', size=14)
    for c, (ch, st) in enumerate(zip('מורים', 'paaca')):
        tile(d, 470 - c * 56, 85, 46, ch, st)
    d.t(620, 112, '`states[]', anchor='middle', size=13)
    d.t(110, 112, 'מילה + מצב לכל אות', cls='dim')
    return d


def twopass():
    d = D('twopass', 720, 265)
    rows = [('המילה הסודית', 'תלמיד', [None] * 5), ('הניחוש', 'תתתתת', [None] * 5),
            ('מעבר 1: ירוקים', 'תתתתת', ['c', None, None, None, None]),
            ('מעבר 2: כל השאר', 'תתתתת', ['c', 'a', 'a', 'a', 'a'])]
    for i, (lab, word, st) in enumerate(rows):
        y = 15 + i * 62
        d.t(700, y + 32, lab, anchor='start', weight=700 if i > 1 else None)
        for c in range(5):
            tile(d, 450 - c * 54, y, 46, word[c], st[c])
    d.t(120, 168, 'ה-ת\' הראשונה במקום הנכון:', cls='dim')
    d.t(120, 190, 'ירוקה, ומנצלת את ה-ת\' היחידה', cls='dim')
    d.t(120, 230, 'לשאר כבר לא נשארה ת\':', cls='dim')
    d.t(120, 252, 'אפורות', cls='dim')
    return d


def junit():
    d = D('junit', 720, 190)
    d.box(160, 10, 400, 50, ['`assertEquals(CORRECT, result[0]);'], 'box blue', size=14)
    d.t(360, 82, 'מה שציפינו  ·  מה שהקוד החזיר', cls='dim')
    d.box(390, 110, 300, 60, ['✓ שווים', 'הבדיקה עוברת (ירוק)'], 'box green', size=14)
    d.box(30, 110, 300, 60, ['✗ שונים', 'הבדיקה נכשלת ומראה מה התקבל'], 'box orange', size=14)
    d.arrow([(420, 60), (520, 108)])
    d.arrow([(300, 60), (200, 108)])
    return d


def testrun():
    d = D('testrun', 720, 240)
    window(d, 20, 10, 680, 220, 'Run: WordleGameTest')
    d.t(60, 60, '`✓ WordleGameTest   9 tests passed', anchor='start', size=14, cls='hl')
    tests = ['allCorrectWhenGuessEqualsSecret', 'letterInWrongPlaceIsPresent', 'duplicateLetterIsCountedOnce',
             'greenWinsOverYellowForDuplicates', 'finalLettersMatchRegularLetters', '…']
    for i, s in enumerate(tests):
        d.t(80, 90 + i * 24, '`✓ ' + s, anchor='start', size=13)
    return d


# ============================================================ step 8

def stringarray():
    d = D('stringarray', 720, 170)
    d.box(520, 20, 180, 120, ['`words.xml', 'שולחן', 'מקלדת', '…'], 'box yellow', size=14)
    d.box(250, 45, 190, 70, ['`String[] words', 'מערך של 105 מילים'], 'box blue', size=14)
    d.arrow([(520, 80), (442, 80)])
    d.t(481, 105, '`getStringArray', size=11)
    d.box(20, 45, 150, 70, ['"תלמיד"', 'מילה אקראית'], 'box green', size=14)
    d.arrow([(250, 80), (172, 80)])
    d.t(211, 105, '`Random', size=12)
    return d


def checkflow():
    d = D('checkflow', 720, 330)
    d.box(250, 10, 220, 40, ['לחיצה על "בדיקה"'], 'box yellow', size=14)
    d.arrow([(360, 50), (360, 70)])
    d.box(250, 72, 220, 40, ['המשחק כבר נגמר?'], 'box', size=14, dash=True)
    d.arrow([(250, 92), (180, 92)], 'כן', 215, 84)
    d.box(30, 72, 150, 40, ['לא עושים כלום'], 'box', size=13)
    d.arrow([(360, 112), (360, 132)])
    d.t(372, 126, 'לא', cls='dim', anchor='start')
    d.box(250, 134, 220, 40, ['יש 5 אותיות?'], 'box', size=14, dash=True)
    d.arrow([(250, 154), (180, 154)], 'לא', 215, 146)
    d.box(30, 134, 150, 40, ['"צריך 5 אותיות"'], 'box', size=13)
    d.arrow([(360, 174), (360, 194)])
    d.t(372, 188, 'כן', cls='dim', anchor='start')
    d.box(220, 196, 280, 40, ['`game.submit(...)'], 'box green', size=13)
    d.t(600, 222, 'המודל משלב 7 בודק', cls='dim')
    d.arrow([(360, 236), (360, 256)])
    d.box(220, 258, 280, 40, ['`showGuess  ·  updateMessage'], 'box blue', size=13)
    d.t(600, 280, 'צובעים את השורה', cls='dim')
    d.t(600, 302, 'ומעדכנים הודעה', cls='dim')
    return d


def inner():
    d = D('inner', 720, 230)
    d.rect(20, 25, 680, 190, 'box blue')
    d.t(360, 50, '`class MainActivity')
    d.box(45, 75, 270, 115, ['`class CheckListener', '`onClick(View view)', 'בודק · צובע · מעדכן'], 'box yellow', size=14)
    d.box(430, 75, 245, 115, ['השדות של הפעילות', '`game  ·  current', '`tiles  ·  txtMessage'], 'box', size=14)
    d.arrow([(315, 132), (428, 132)], 'רואה אותם ישירות', 372, 120)
    return d


def fmt():
    d = D('fmt', 720, 160)
    d.box(440, 15, 260, 54, ['נשארו %1$d ניסיונות'], 'box yellow', size=15)
    d.t(570, 92, '+', size=24, weight=700)
    d.box(440, 100, 260, 46, ['המספר 5'], 'box', size=14)
    d.arrow([(440, 80), (282, 80)], '`getString', 361, 68)
    d.box(20, 53, 260, 54, ['נשארו 5 ניסיונות'], 'box green')
    return d


def currentrow():
    d = D('currentrow', 720, 230)
    for r in range(4):
        y = 15 + r * 50
        word, st = [('מורים', 'paaca'), ('תל', ''), ('', ''), ('', '')][r]
        for c in range(5):
            tile(d, 420 - c * 48, y, 42, word[c] if c < len(word) else '', st[c] if c < len(st) else None)
    d.arrow([(540, 86), (476, 86)])
    d.t(550, 82, '`game.getGuessCount()', anchor='start', size=13)
    d.t(550, 104, '= 1 → שורה 1', anchor='start', cls='dim')
    d.t(140, 40, 'ניחוש אחד כבר נבדק', cls='dim')
    d.t(140, 90, 'כאן מקלידים עכשיו', weight=700)
    return d


# ============================================================ step 9

def anonymous():
    d = D('anonymous', 720, 200)
    d.rect(20, 15, 680, 170, 'term', rx=8)
    code = ['findViewById(R.id.btnNewGame).setOnClickListener(',
            '        new View.OnClickListener() {',
            '            public void onClick(View v) {',
            '                startNewGame();',
            '            }',
            '        });']
    for i, s in enumerate(code):
        d.t(40, 45 + i * 25, '`' + s, anchor='start', size=14, cls='hl' if i in (1, 3) else '')
    d.t(560, 70, '← מחלקה בלי שם, נוצרת כאן', anchor='start', cls='dim')
    d.t(560, 120, '← כל מה שהיא עושה', anchor='start', cls='dim')
    return d


def keymap():
    d = D('keymap', 720, 200)
    d.box(470, 60, 230, 70, ['`paintKey(\'ש\', PRESENT)'], 'box blue', size=14)
    d.rect(250, 22, 170, 160, 'box', dash=True)
    d.t(335, 16, '`keyByLetter', cls='dim')
    for i, k in enumerate(['ק', 'ש', 'ר']):
        y = 35 + i * 48
        d.t(295, y + 26, '`\'%s\'' % k)
        d.arrow([(318, y + 20), (358, y + 20)])
        d.rect(362, y + 4, 40, 32, 'box', fill=YELLOW if k == 'ש' else KEY_BG, rx=5)
        d.t(382, y + 26, k, fill='#FFFFFF' if k == 'ש' else INK, weight=700)
    d.arrow([(470, 95), (422, 95)])
    d.box(20, 60, 180, 70, ['המקש "ש"', 'נצבע בצהוב'], 'box green', size=14)
    d.arrow([(250, 95), (202, 95)])
    return d


def upgrade():
    d = D('upgrade', 720, 175)
    for i, (col, name) in enumerate([(GRAY, 'אפור'), (YELLOW, 'צהוב'), (GREEN, 'ירוק')]):
        x = 520 - i * 220
        d.rect(x, 30, 160, 56, 'box', fill=col)
        d.t(x + 80, 64, name, fill='#FFFFFF', weight=700)
        if i < 2:
            d.arrow([(x, 58), (x - 58, 58)], 'עולה', x - 30, 48)
    d.arrow([(140, 90), (140, 128), (380, 128), (380, 92)], cls='arr bad')
    d.t(260, 160, '✗ לא יורדים: מקש ירוק נשאר ירוק', cls='dim')
    return d


def gravity():
    d = D('gravity', 720, 200)
    d.rect(380, 35, 320, 80, 'box blue')
    d.t(540, 82, 'הטקסט במרכז הרכיב')
    d.t(540, 22, '`gravity="center"')
    d.t(540, 145, 'מזיז את התוכן בתוך הרכיב', cls='dim')
    d.rect(20, 35, 320, 80, 'box', dash=True)
    d.rect(110, 55, 140, 40, 'box yellow', rx=20)
    d.t(180, 81, 'משחק חדש', size=14)
    d.t(180, 22, '`layout_gravity="center_horizontal"')
    d.t(180, 145, 'מזיז את הרכיב עצמו בתוך ההורה', cls='dim')
    return d


# ============================================================ step 10

def lost():
    d = D('lost', 720, 200)
    for i, (lab, rows) in enumerate([('לפני הסיבוב', [('מורים', 'paaca'), ('תל', '')]), ('אחרי הסיבוב', [])]):
        x = 460 if i == 0 else 60
        d.t(x + 100, 22, lab, weight=700)
        for r in range(3):
            word, st = rows[r] if r < len(rows) else ('', '')
            for c in range(5):
                tile(d, x + 160 - c * 40, 38 + r * 40, 34, word[c] if c < len(word) else '',
                     st[c] if c < len(st) else None)
    d.arrow([(450, 95), (272, 95)], '`onDestroy → onCreate', 361, 83)
    d.t(160, 180, 'לוח ריק ומילה סודית חדשה ✗', cls='dim')
    return d


def bundle():
    d = D('bundle', 720, 240)
    d.box(500, 50, 200, 90, ['הפעילות הישנה', 'לפני הסיבוב'], 'box orange')
    d.rect(250, 30, 220, 140, 'box yellow')
    d.t(360, 55, '`Bundle', weight=700)
    for i, s in enumerate(['`secret: "תלמיד"', '`guesses: ["מורים"]', '`current: "תל"']):
        d.t(360, 88 + i * 26, s, size=14)
    d.box(20, 50, 200, 90, ['הפעילות החדשה', '`restoreGame()'], 'box green')
    d.arrow([(500, 95), (472, 95)])
    d.t(600, 168, '`onSaveInstanceState', size=13)
    d.arrow([(250, 95), (222, 95)])
    d.t(120, 168, '`onCreate(savedInstanceState)', size=13)
    d.t(360, 215, 'שומרים רק את מה שאי אפשר לחשב. את הצבעים מחשבים מחדש', cls='dim')
    return d


def nullcheck():
    d = D('nullcheck', 720, 180)
    d.box(250, 15, 220, 50, ['`savedInstanceState'], 'box blue', size=14)
    d.arrow([(320, 65), (180, 110)], '`null', 230, 80)
    d.arrow([(400, 65), (540, 110)], 'יש בו משהו', 500, 80)
    d.box(40, 112, 280, 54, ['הפעלה רגילה', '`startNewGame()'], 'box', size=14)
    d.box(400, 112, 280, 54, ['חזרה מסיבוב', '`restoreGame(...)'], 'box green', size=14)
    return d


DIAGRAMS = {f.__name__: f for f in (
    newproject, projectform, projecttree, files, lifecycle, override, println, logcat, rotate,
    xml_view, linear, sizes, resources, units, weight, rtl, board, shape, newview,
    event, ways, onclick_xml, style, include, cast, builder, listener_this, getid,
    model, states, guessobj, twopass, junit, testrun, stringarray, checkflow, inner, fmt, currentrow,
    anonymous, keymap, upgrade, gravity, lost, bundle, nullcheck)}


# ============================================================ the phone

KEY_ROWS = ['קראטוןםפ', 'שדגכעיחלךף', 'זסבהנמצתץ']


def phone(name, hello=False, title=False, msg='', board=False, rows=None, keys=False, actions=False,
          newgame=False, keycolors=None):
    d = D('phone_' + name, 240, 470)
    d.rect(4, 4, 232, 462, 'phone', rx=30)
    d.rect(14, 26, 212, 424, 'screen', rx=10, fill=SCREEN_BG if title else '#FFFFFF')
    if hello:
        d.t(120, 240, '`Hello World!', fill=INK, size=13)
    if title:
        d.t(120, 64, 'ווֹרדל בעברית', size=18, weight=700, fill=PRIMARY)
        d.t(120, 83, msg or 'נחשו מילה בת 5 אותיות. יש לכם 6 ניסיונות.', size=8, fill=INK)
    if board:
        rows = rows or {}
        for r in range(6):
            word, st = rows.get(r, ('', ''))
            for c in range(5):
                tile(d, 47 + (4 - c) * 30, 94 + r * 30, 26, word[c] if c < len(word) else '',
                     st[c] if c < len(st) else None)
    if newgame:
        d.p.append('<rect x="78" y="290" width="84" height="22" rx="11" style="fill:none;stroke:%s;stroke-width:1.5"/>'
                   % PRIMARY)
        d.t(120, 305, 'משחק חדש', size=9, fill=PRIMARY)
    if keys:
        kc = keycolors or {}
        for r, letters in enumerate(KEY_ROWS):
            n = len(letters)
            kw = (200 - (n - 1) * 2) / n
            for i, ch in enumerate(letters):
                x = 20 + i * (kw + 2)
                st = kc.get(ch)
                d.rect(round(x, 1), 322 + r * 28, round(kw, 1), 24, 'key', rx=3, fill=STATE[st] if st else KEY_BG)
                d.t(round(x + kw / 2, 1), 338 + r * 28, ch, size=10, fill='#FFFFFF' if st else INK)
    if actions:
        d.rect(20, 406, 99, 24, 'key', rx=3, fill=KEY_BG)
        d.t(69.5, 422, 'מחק', size=10, fill=INK)
        d.rect(121, 406, 99, 24, 'key', rx=3, fill=PRIMARY)
        d.t(170.5, 422, 'בדיקה', size=10, fill='#FFFFFF')
    return d


GUESS = {0: ('מורים', 'paaca')}
GUESS_KEYS = {'מ': 'p', 'ו': 'a', 'ר': 'a', 'י': 'c', 'ם': 'a'}
PHONES = {
    's1': dict(hello=True),
    's3': dict(title=True),
    's4': dict(title=True, board=True),
    's5': dict(title=True, board=True, rows={0: ('שלו', '')}, keys=True),
    's6': dict(title=True, board=True, rows={0: ('של', '')}, keys=True, actions=True),
    's8': dict(title=True, msg='נשארו 5 ניסיונות', board=True, rows={**GUESS, 1: ('תל', '')}, keys=True, actions=True),
    's9': dict(title=True, msg='נשארו 5 ניסיונות', board=True, rows={**GUESS, 1: ('תל', '')}, keys=True,
               actions=True, newgame=True, keycolors=GUESS_KEYS),
}


def expand(text):
    def dia(m):
        name, cap = m.group(1), m.group(2)
        if name not in DIAGRAMS:
            raise SystemExit('unknown diagram ' + name)
        return '<figure class="diagram">%s<figcaption>%s</figcaption></figure>' % (DIAGRAMS[name]().svg(cap), cap)

    def ph(m):
        name, cap = m.group(1), m.group(2)
        if name not in PHONES:
            raise SystemExit('unknown phone ' + name)
        return ('<figure class="diagram phonefig">%s<figcaption>%s</figcaption></figure>'
                % (phone(name, **PHONES[name]).svg(cap), cap))

    text = re.sub(r'\{\{DIAGRAM:(\w+)\|([^}]*)\}\}', dia, text)
    return re.sub(r'\{\{PHONE:(\w+)\|([^}]*)\}\}', ph, text)


# ============================================================ animations
# כל אנימציה היא SVG עם CSS keyframes משלה, באורך מחזור T שניות, שחוזר על עצמו.
# כל רכיב מונפש מקבל "מסלול": רשימת (זמן, css). בלי תנועה (prefers-reduced-motion) רואים את כל הרכיבים במצבם הרגיל.

class A(D):
    def __init__(self, name, w, h, T):
        super().__init__(name, w, h)
        self.T, self.css, self.n = T, [], 0

    def track(self, frames, base=''):
        self.n += 1
        c = '%s-%d' % (self.name, self.n)
        fr = sorted(frames, key=lambda f: f[0])
        if fr[0][0] > 0:
            fr = [(0, fr[0][1])] + fr
        if fr[-1][0] < self.T:
            fr = fr + [(self.T, fr[-1][1])]
        ks = ''.join('%.3f%%{%s}' % (min(t, self.T) / self.T * 100, css) for t, css in fr)
        self.css.append('@keyframes k-%s{%s}.%s{animation:k-%s %ss linear infinite;%s}' % (c, ks, c, c, self.T, base))
        return c

    def vis(self, on, off=None):
        off = self.T - 0.5 if off is None else off
        return self.track([(0, 'opacity:0'), (on, 'opacity:0'), (on + 0.25, 'opacity:1'),
                           (off, 'opacity:1'), (off + 0.25, 'opacity:0')])

    def g(self, cls):
        self.p.append('<g class="%s">' % cls)

    def end(self):
        self.p.append('</g>')

    def svg(self, label):
        return super().svg(label).replace('<svg class="dg"', '<svg class="dg anim"', 1).replace(
            '<defs>', '<style>%s</style><defs>' % ''.join(self.css), 1)


def anim_lifecycle():
    d = A('anim_lifecycle', 720, 410, 24)
    ys = [55, 135, 215, 295]
    names = ['הפעילות לא קיימת', 'נוצרה: המסך נבנה', 'מוצגת על המסך', 'פעילה: אפשר ללחוץ']
    for i, (y, n) in enumerate(zip(ys, names)):
        d.box(440, y, 250, 46, [n], 'box green' if i == 3 else 'box', dash=(i == 0))
    for s, on, off in [('▶ מפעילים את המשחק', 0, 4.6), ('🏠 לוחצים על כפתור הבית', 5, 8.6),
                       ('↩ חוזרים למשחק', 9, 12.6), ('🔄 מסובבים את הטלפון', 13, 22.8)]:
        d.g(d.vis(on, off))
        d.t(565, 32, s, weight=700, size=17)
        d.end()
    seq = [(0, 0), (1, 1), (2, 2), (3, 3), (6, 2), (7, 1), (10, 2), (11, 3),
           (14, 2), (15, 1), (16, 0), (17, 1), (18, 2), (19, 3)]
    tr = lambda lv: 'transform:translate(0px,%spx)' % (ys[lv] - ys[0])
    frames, prev = [(0, tr(0))], 0
    for t, lv in seq[1:]:
        frames += [(t - 0.35, tr(prev)), (t, tr(lv))]
        prev = lv
    frames += [(d.T - 0.4, tr(prev)), (d.T, tr(0))]
    d.g(d.track(frames))
    d.rect(434, ys[0] - 5, 262, 56, 'hlbox', rx=12)
    d.end()
    window(d, 20, 45, 380, 350, 'Logcat')
    logs = [(1, 'onCreate', ''), (2, 'onStart', ''), (3, 'onResume', ''), (6, 'onPause', ''), (7, 'onStop', ''),
            (10, 'onStart', ''), (11, 'onResume', ''), (14, 'onPause', ''), (15, 'onStop', ''),
            (16, 'onDestroy', '#FFA94D'), (17, 'onCreate', '#7DE07D'), (18, 'onStart', ''), (19, 'onResume', '')]
    for i, (t, m, col) in enumerate(logs):
        d.g(d.vis(t))
        d.t(38, 96 + i * 22.5, '`D  LIFECYCLE  ' + m, anchor='start', size=13, fill=col or None)
        d.end()
    d.t(565, 375, 'המסגרת הצהובה: איפה המשחק נמצא עכשיו', cls='dim')
    return d


def anim_board():
    d = A('anim_board', 720, 330, 11)
    d.rect(20, 20, 320, 165, 'term', rx=8)
    for i, s in enumerate(['for (row = 0; row < ROWS; row++)', '  for (col = 0; col < COLS; col++)',
                           '    tile = new TextView(this)', '    tiles[row][col] = tile',
                           '    rowLayout.addView(tile)']):
        d.t(36, 50 + i * 28, '`' + s, anchor='start', size=13)
    step, t0 = 0.27, 0.5
    for r in range(6):
        y = 25 + r * 48
        d.g(d.vis(t0 + r * 5 * step - 0.1))
        d.rect(400, y - 3, 300, 46, 'box blue', rx=6)
        d.end()
        d.g(d.vis(t0 + r * 5 * step, t0 + (r + 1) * 5 * step if r < 5 else None))
        d.t(180, 240, '`row = %d' % r, size=20)
        d.end()
        for c in range(5):
            t = t0 + (r * 5 + c) * step
            d.g(d.vis(t))
            tile(d, 438 + (4 - c) * 46, y, 40)
            d.end()
            d.g(d.vis(t, t + step if (r, c) != (5, 4) else None))
            d.t(180, 280, '`col = %d' % c, size=20)
            d.end()
    return d


def anim_tap():
    d = A('anim_tap', 720, 300, 12)
    for c in range(5):
        tile(d, 470 + (4 - c) * 50, 20, 44)
    rows = ['קראטוןםפ', 'שדגכעיחלךף']
    pos = {}
    for r, letters in enumerate(rows):
        n = len(letters)
        kw = (400 - (n - 1) * 4) / n
        for i, ch in enumerate(letters):
            x = 300 + i * (kw + 4)
            d.rect(round(x, 1), 120 + r * 50, round(kw, 1), 42, 'key', rx=5, fill=KEY_BG)
            d.t(round(x + kw / 2, 1), 147 + r * 50, ch, fill=INK, weight=700)
            pos[ch] = (x + kw / 2, 141 + r * 50)
    d.box(20, 110, 240, 56, ['`onLetterKey(view)'], 'box', size=15)
    states = ['""', '"ש"', '"של"', '"שלו"']
    taps = [(1, 'ש', 0), (4, 'ל', 1), (7, 'ו', 2)]
    for t, ch, col in taps:
        x, y = pos[ch]
        d.g(d.vis(t - 0.4, t + 0.6))
        d.p.append('<circle cx="%s" cy="%s" r="16" class="finger"/>' % (round(x, 1), y))
        d.end()
        d.g(d.vis(t + 0.3, t + 1.3))
        d.rect(16, 106, 248, 64, 'hlbox', rx=12)
        d.end()
        d.g(d.vis(t + 1.0))
        tile(d, 470 + (4 - col) * 50, 20, 44, ch)
        d.end()
    bounds = [0, 1.6, 4.6, 7.6, None]
    for i, s in enumerate(states):
        d.g(d.vis(bounds[i], bounds[i + 1]))
        d.t(140, 228, '`current = ' + s, size=17)
        d.end()
    d.arrow([(296, 150), (266, 140)])
    return d


def anim_twopass():
    d = A('anim_twopass', 720, 300, 13)
    xs = [450 - c * 62 for c in range(5)]
    for lab, y in [('המילה הסודית', 30), ('הניחוש', 110), ('התוצאה', 200)]:
        d.t(700, y + 32, lab, anchor='start', weight=700)
    for c in range(5):
        tile(d, xs[c], 30, 50, 'תלמיד'[c])
        tile(d, xs[c], 110, 50, 'ת')
        tile(d, xs[c], 200, 50)
    d.g(d.vis(0.5, 5.8))
    d.t(110, 60, 'מעבר 1:', weight=700, size=17)
    d.t(110, 84, 'מחפשים ירוקים', cls='dim')
    d.end()
    d.g(d.vis(6, 12.4))
    d.t(110, 60, 'מעבר 2:', weight=700, size=17)
    d.t(110, 84, 'כל השאר', cls='dim')
    d.end()
    # הסמן על הניחוש
    pts = [(1 + c * 0.8, c) for c in range(5)] + [(6.6 + (c - 1) * 1.3, c) for c in range(1, 5)]
    tr = lambda c: 'transform:translate(%spx,0px)' % (xs[c] - xs[0])
    frames, prev = [(0, tr(0) + ';opacity:0'), (0.8, tr(0) + ';opacity:0'), (1, tr(0) + ';opacity:1')], 0
    for t, c in pts[1:]:
        frames += [(t - 0.3, tr(prev) + ';opacity:1'), (t, tr(c) + ';opacity:1')]
        prev = c
    frames += [(d.T - 0.6, tr(prev) + ';opacity:1'), (d.T - 0.3, tr(prev) + ';opacity:0')]
    d.g(d.track(frames))
    d.rect(xs[0] - 5, 105, 60, 60, 'hlbox', rx=8)
    d.end()
    d.g(d.vis(1.3))
    tile(d, xs[0], 200, 50, 'ת', 'c')
    d.end()
    d.g(d.vis(1.6))
    d.rect(xs[0], 30, 50, 50, 'used', rx=3)
    d.t(xs[0] + 25, 96, 'נוצלה', cls='dim', size=12)
    d.end()
    for c in range(1, 5):
        t = 6.6 + (c - 1) * 1.3
        d.g(d.vis(t + 0.4))
        tile(d, xs[c], 200, 50, 'ת', 'a')
        d.end()
    d.g(d.vis(7, 12.4))
    d.t(110, 225, 'אין עוד ת\' פנויה', cls='dim')
    d.t(110, 247, 'במילה הסודית ← אפור', cls='dim')
    d.end()
    return d


def anim_check():
    d = A('anim_check', 720, 320, 11)
    xs = [640 - c * 54 for c in range(5)]
    for c in range(5):
        tile(d, xs[c], 30, 46, 'מורים'[c])
        tile(d, xs[c], 84, 46)
    for c, st in enumerate('paaca'):
        d.g(d.vis(1.8 + c * 0.45))
        tile(d, xs[c], 30, 46, 'מורים'[c], st)
        d.end()
    d.g(d.vis(0, 4.0))
    d.rect(xs[4] - 6, 24, 278, 58, 'hlbox', rx=8)
    d.end()
    d.g(d.vis(4.4))
    d.rect(xs[4] - 6, 78, 278, 58, 'hlbox', rx=8)
    d.end()
    d.g(d.vis(0, 4.2))
    d.t(530, 172, 'נחשו מילה בת 5 אותיות. יש לכם 6 ניסיונות.', size=14)
    d.end()
    d.g(d.vis(4.4))
    d.t(530, 172, 'נשארו 5 ניסיונות', size=16, weight=700)
    d.end()
    d.rect(470, 200, 120, 40, 'key', rx=6, fill=PRIMARY)
    d.t(530, 226, 'בדיקה', fill='#FFFFFF', weight=700)
    d.g(d.vis(0.6, 1.5))
    d.p.append('<circle cx="530" cy="220" r="18" class="finger"/>')
    d.end()
    calls = [('`game.submit("מורים")', 1.2, 1.9), ('`showGuess(0, guess)', 1.8, 4.0), ('`updateMessage()', 4.1, 4.9)]
    for i, (s, on, off) in enumerate(calls):
        y = 40 + i * 75
        d.box(20, y, 290, 54, [s], 'box', size=14)
        d.g(d.vis(on, off))
        d.rect(16, y - 4, 298, 62, 'hlbox', rx=12)
        d.end()
    d.t(165, 280, 'השורה הבאה מחכה להקלדה', cls='dim')
    return d


def anim_keys():
    d = A('anim_keys', 720, 260, 11)
    keys = ['מ', 'ו', 'ר', 'י', 'ל', 'ד', 'ת']
    xs = {k: 590 - i * 82 for i, k in enumerate(keys)}
    for k in keys:
        d.rect(xs[k], 110, 66, 56, 'key', rx=6, fill=KEY_BG)
        d.t(xs[k] + 33, 145, k, fill=INK, weight=700, size=20)

    def paint(k, st, on):
        d.g(d.vis(on))
        d.rect(xs[k], 110, 66, 56, 'key', rx=6, fill=STATE[st])
        d.t(xs[k] + 33, 145, k, fill='#FFFFFF', weight=700, size=20)
        d.end()

    d.g(d.vis(0.5, 4.2))
    d.t(360, 40, 'ניחוש 1: מורים', weight=700, size=18)
    d.end()
    for k, st in [('מ', 'p'), ('ו', 'a'), ('ר', 'a'), ('י', 'c')]:
        paint(k, st, 1.5)
    d.g(d.vis(4.5))
    d.t(360, 40, 'ניחוש 2: יולדת', weight=700, size=18)
    d.end()
    for k in 'לדת':
        paint(k, 'p', 5.2)
    d.g(d.vis(5.4, 7.0))
    d.rect(xs['י'] + 8, 70, 50, 34, 'key', rx=5, fill=YELLOW)
    d.t(xs['י'] + 33, 93, 'י', fill='#FFFFFF', weight=700)
    d.end()
    d.g(d.vis(6.2, 7.0))
    d.t(xs['י'] + 33, 98, '✗', size=34, weight=700, fill='#ff6b6b')
    d.end()
    d.g(d.vis(7.0))
    d.t(xs['י'] + 33, 200, 'י נשארת ירוקה', weight=700)
    d.t(xs['י'] + 33, 222, 'רק עולים בדרגה', cls='dim')
    d.end()
    return d


def anim_rotate():
    d = A('anim_rotate', 720, 350, 18)
    rot = 'transform-box:fill-box;transform-origin:center;'

    def portrait(on, off, rotate_at):
        frames = [(0, 'opacity:0;transform:rotate(0deg)'), (on, 'opacity:0;transform:rotate(0deg)'),
                  (on + 0.25, 'opacity:1;transform:rotate(0deg)'), (rotate_at, 'opacity:1;transform:rotate(0deg)'),
                  (rotate_at + 0.8, 'opacity:0;transform:rotate(-90deg)'), (off, 'opacity:0;transform:rotate(-90deg)')]
        d.g(d.track(frames, rot))
        d.rect(115, 50, 120, 230, 'phone', rx=16)
        d.rect(122, 62, 106, 206, 'screen', rx=6, fill=SCREEN_BG)
        for r, (word, st) in enumerate([('מורים', 'paaca'), ('תל', '')]):
            for c in range(5):
                tile(d, 128 + (4 - c) * 19.5, 100 + r * 20, 17, word[c] if c < len(word) else '',
                     st[c] if c < len(st) else None)
        d.end()

    def landscape(on, off, filled_at=None):
        d.g(d.vis(on, off))
        d.rect(60, 105, 230, 120, 'phone', rx=16)
        d.rect(72, 112, 206, 106, 'screen', rx=6, fill=SCREEN_BG)
        for r in range(2):
            for c in range(5):
                tile(d, 128 + (4 - c) * 19.5, 130 + r * 20, 17)
        d.end()
        if filled_at:
            d.g(d.vis(filled_at, off))
            for r, (word, st) in enumerate([('מורים', 'paaca'), ('תל', '')]):
                for c in range(5):
                    if c < len(word):
                        tile(d, 128 + (4 - c) * 19.5, 130 + r * 20, 17, word[c], st[c] if c < len(st) else None)
            d.end()

    # סצנה 1: בלי שמירה
    d.g(d.vis(0, 8))
    d.t(175, 30, 'בלי שמירה', weight=700, size=18)
    d.end()
    portrait(0, 8, 2)
    landscape(2.7, 8)
    d.g(d.vis(3.5, 8))
    d.t(175, 260, '✗ הלוח ריק, מילה סודית חדשה', weight=700, fill='#ff6b6b')
    d.end()
    # סצנה 2: עם Bundle
    d.g(d.vis(8.6))
    d.t(175, 30, 'עם onSaveInstanceState', weight=700, size=18)
    d.end()
    portrait(8.6, d.T, 12)
    landscape(12.7, d.T - 0.5, 14.6)
    d.g(d.vis(8.6))
    d.rect(430, 80, 270, 170, 'box yellow')
    d.t(565, 106, '`Bundle', weight=700)
    d.end()
    chips = ['`secret: "תלמיד"', '`guesses: ["מורים"]', '`current: "תל"']
    for i, s in enumerate(chips):
        t0 = 10 + i * 0.35
        frames = [(0, 'opacity:0;transform:translate(-390px,0px)'), (t0, 'opacity:0;transform:translate(-390px,0px)'),
                  (t0 + 0.1, 'opacity:1;transform:translate(-390px,0px)'), (t0 + 0.9, 'opacity:1;transform:translate(0px,0px)'),
                  (13.6 + i * 0.2, 'opacity:1;transform:translate(0px,0px)'),
                  (14.4 + i * 0.2, 'opacity:1;transform:translate(-390px,0px)'),
                  (14.6 + i * 0.2, 'opacity:0;transform:translate(-390px,0px)')]
        d.g(d.track(frames))
        d.rect(450, 122 + i * 40, 230, 32, 'box', rx=6)
        d.t(565, 143 + i * 40, s, size=13)
        d.end()
    d.g(d.vis(10, 11.5))
    d.t(565, 290, '`onSaveInstanceState', size=14)
    d.end()
    d.g(d.vis(13.5, 14.8))
    d.t(565, 290, '`onCreate → restoreGame', size=14)
    d.end()
    d.g(d.vis(15))
    d.t(175, 260, '✓ אותו משחק בדיוק', weight=700, fill='#7DE07D')
    d.end()
    return d


ANIMS = {f.__name__: f for f in (anim_lifecycle, anim_board, anim_tap, anim_twopass, anim_check, anim_keys,
                                 anim_rotate)}
_expand_static = expand


def expand(text):
    def an(m):
        name, cap = m.group(1), m.group(2)
        if name not in ANIMS:
            raise SystemExit('unknown animation ' + name)
        return ('<figure class="diagram animfig">%s<figcaption>🎬 %s</figcaption></figure>'
                % (ANIMS[name]().svg(cap), cap))

    return _expand_static(re.sub(r'\{\{ANIM:(\w+)\|([^}]*)\}\}', an, text))
