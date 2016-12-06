from enum import Enum

class HiraType(Enum):
    Ignore = 0
    Kata = 1
    Special = 2

class RomanToKana(object):
    vowels = ('a', 'i', 'u', 'e', 'o')

    consonants = (
        ('', ('あ', 'い', 'う', 'え', 'お'), ('ア', 'イ', 'ウ', 'エ', 'オ')),
        ('wh', ('うぁ', 'うぃ', 'う', 'うぇ', 'うぉ'), ('ウァ', 'ウィ', 'ウ', 'ウェ', 'ウォ')),
        ('l', ('ぁ', 'ぃ', 'ぅ', 'ぇ', 'ぉ'), ('ァ', 'ィ', 'ゥ', 'ェ', 'ォ')),
        ('x', ('ぁ', 'ぃ', 'ぅ', 'ぇ', 'ぉ'), ('ァ', 'ィ', 'ゥ', 'ェ', 'ォ')),
        ('k', ('か', 'き', 'く', 'け', 'こ'), ('カ', 'キ', 'ク', 'ケ', 'コ')),
        ('ky', ('きゃ', 'きぃ', 'きゅ', 'きぇ', 'きょ'), ('キャ', 'キィ', 'キュ', 'キェ', 'キョ')),
        ('kw', ('くぁ', None, None, None, None), ('クァ', None, None, None, None)),
        ('c', ('か', 'し', 'く', 'せ', 'こ'), ('カ', 'シ', 'ク', 'セ', 'コ')),
        ('q', ('くぁ', 'くぃ', 'く', 'くぇ', 'くぉ'), ('クァ', 'クィ', 'ク', 'クェ', 'クォ')),
        ('qy', ('くゃ', 'くぃ', 'くゅ', 'くぇ', 'くょ'), ('クャ', 'クィ', 'クュ', 'クェ', 'クョ')),
        ('qw', ('くぁ', 'くぃ', 'くぅ', 'くぇ', 'くぉ'), ('クァ', 'クィ', 'クゥ', 'クェ', 'クォ')),
        ('g', ('が', 'ぎ', 'ぐ', 'げ', 'こ'), ('ガ', 'ギ', 'グ', 'ゲ', 'ゴ')),
        ('gy', ('ぎゃ', 'ぎぃ', 'ぎゅ', 'ぎぇ', 'ぎょ'), ('ギャ', 'ギィ', 'ギュ', 'ギェ', 'ギョ')),
        ('gw', ('ぐぁ', 'ぐぃ', 'ぐぅ', 'ぐぇ', 'ぐぉ'), ('グァ', 'グィ', 'グゥ', 'グェ', 'グォ')),
        ('s', ('さ', 'し', 'す', 'せ', 'そ'), ('サ', 'シ', 'ス', 'セ', 'ソ')),
        ('sy', ('しゃ', 'しぃ', 'しゅ', 'しぇ', 'しょ'), ('シャ', 'シィ', 'シュ', 'シェ', 'ショ')),
        ('sh', ('しゃ', 'し', 'しゅ', 'しぇ', 'しょ'), ('シャ', 'シ', 'シュ', 'シェ', 'ショ')),
        ('sw', ('すぁ', 'すぃ', 'すぅ', 'すぇ', 'すぉ'), ('スァ', 'スィ', 'スゥ', 'スェ', 'スォ')),
        ('z', ('ざ', 'じ', 'ず', 'ぜ', 'ぞ'), ('ザ', 'ジ', 'ズ', 'ゼ', 'ゾ')),
        ('zy', ('じゃ', 'じぃ', 'じゅ', 'じぇ', 'じょ'), ('ジャ', 'ジィ', 'ジュ', 'ジェ', 'ジョ')),
        ('j', ('じゃ', 'じ', 'じゅ', 'じぇ', 'じょ'), ('ジャ', 'ジ', 'ジュ', 'ジェ', 'ジョ')),
        ('jy', ('じゃ', 'じぃ', 'じゅ', 'じぇ', 'じょ'), ('ジャ', 'ジィ', 'ジュ', 'ジェ', 'ジョ')),
        ('t', ('た', 'ち', 'つ', 'て', 'と'), ('タ', 'チ', 'ツ', 'テ', 'ト')),
        ('ty', ('ちゃ', 'ちぃ', 'ちゅ', 'ちぇ', 'ちょ'), ('チャ', 'チィ', 'チュ', 'チェ', 'チョ')),
        ('ch', ('ちゃ', 'ち', 'ちゅ', 'ちぇ', 'ちょ'), ('チャ', 'チ', 'チュ', 'チェ', 'チョ')),
        ('cy', ('ちゃ', 'ちぃ', 'ちゅ', 'ちぇ', 'ちょ'), ('チャ', 'チィ', 'チュ', 'チェ', 'チョ')),
        ('ts', ('つぁ', 'つぃ', 'つ', 'つぇ', 'つぉ'), ('ツァ', 'ツィ', 'ツ', 'ツェ', 'ツォ')),
        ('th', ('てゃ', 'てぃ', 'てゅ', 'てぇ', 'てょ'), ('テャ', 'ティ', 'テュ', 'テェ', 'テョ')),
        ('tw', ('とぁ', 'とぃ', 'とぅ', 'とぇ', 'とぉ'), ('トァ', 'トィ', 'トゥ', 'トェ', 'トォ')),
        ('d', ('だ', 'ぢ', 'づ', 'で', 'ど'), ('ダ', 'ヂ', 'ヅ', 'デ', 'ド')),
        ('dy', ('ぢゃ', 'ぢぃ', 'ぢゅ', 'ぢぇ', 'ぢょ'), ('ヂャ', 'ヂィ', 'ヂュ', 'ヂェ', 'ヂョ')),
        ('dh', ('でゃ', 'でぃ', 'でゅ', 'でぇ', 'でょ'), ('デャ', 'ディ', 'デュ', 'デェ', 'デョ')),
        ('dw', ('どぁ', 'どぃ', 'どぅ', 'どぇ', 'どぉ'), ('ドァ', 'ドィ', 'ドゥ', 'ドェ', 'ドォ')),
        ('lt', (None, None, 'っ', None, None), (None, None, 'ッ', None, None)),
        ('xt', (None, None, 'っ', None, None), (None, None, 'ッ', None, None)),
        ('lts', (None, None, 'っ', None, None), (None, None, 'ッ', None, None)),
        ('n', ('な', 'に', 'ぬ', 'ね', 'の'), ('ナ', 'ニ', 'ヌ', 'ネ', 'ノ')),
        ('ny', ('にゃ', 'にぃ', 'にゅ', 'にぇ', 'にょ'), ('ニャ', 'ニィ', 'ニュ', 'ニェ', 'ニョ')),
        ('h', ('は', 'ひ', 'ふ', 'へ', 'ほ'), ('ハ', 'ヒ', 'フ', 'ヘ', 'ホ')),
        ('hy', ('ひゃ', 'ひぃ', 'ひゅ', 'ひぇ', 'ひょ'), ('ヒャ', 'ヒィ', 'ヒュ', 'ヒェ', 'ヒョ')),
        ('f', ('ふぁ', 'ふぃ', 'ふ', 'ふぇ', 'ふぉ'), ('ファ', 'フィ', 'フ', 'フェ', 'フォ')),
        ('fw', ('ふぁ', 'ふぃ', 'ふぅ', 'ふぇ', 'ふぉ'), ('ファ', 'フィ', 'フゥ', 'フェ', 'フォ')),
        ('fy', ('ふゃ', 'ふぃ', 'ふゅ', 'ふぇ', 'ふょ'), ('フャ', 'フィ', 'フュ', 'フェ', 'フョ')),
        ('b', ('ば', 'び', 'ぶ', 'べ', 'ぼ'), ('バ', 'ビ', 'ブ', 'ベ', 'ボ')),
        ('by', ('びゃ', 'びぃ', 'びゅ', 'びぇ', 'びょ'), ('ビャ', 'ビィ', 'ビュ', 'ビェ', 'ビョ')),
        ('p', ('ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ'), ('パ', 'ピ', 'プ', 'ペ', 'ポ')),
        ('py', ('ぴゃ', 'ぴぃ', 'ぴゅ', 'ぴぇ', 'ぴょ'), ('ピャ', 'ピィ', 'ピュ', 'ピェ', 'ピョ')),
        ('m', ('ま', 'み', 'む', 'め', 'も'), ('マ', 'ミ', 'ム', 'メ', 'モ')),
        ('my', ('みゃ', 'みぃ', 'みゅ', 'みぇ', 'みょ'), ('ミャ', 'ミィ', 'ミュ', 'ミェ', 'ミョ')),
        ('y', ('や', 'い', 'ゆ', 'いぇ', 'よ'), ('ヤ', 'イ', 'ユ', 'イェ', 'ヨ')),
        ('ly', ('ゃ', 'ぃ', 'ゅ', 'ぇ', 'ょ'), ('ャ', 'ィ', 'ュ', 'ェ', 'ョ')),
        ('xy', ('ゃ', 'ぃ', 'ゅ', 'ぇ', 'ょ'), ('ャ', 'ィ', 'ュ', 'ェ', 'ョ')),
        ('r', ('ら', 'り', 'る', 'れ', 'ろ'), ('ラ', 'リ', 'ル', 'レ', 'ロ')),
        ('ry', ('りゃ', 'りぃ', 'りゅ', 'りぇ', 'りょ'), ('リャ', 'リィ', 'リュ', 'リェ', 'リョ')),
        ('wy', (None, 'ゐ', None, 'ゑ', None), (None, 'ヰ', None, 'ヱ', None)),
        ('lw', ('ゎ', None, None, None, None), ('ヮ', None, None, None, None)),
    )

    consonants_w = (
        ('w', ('わ', 'うぃ', 'う', 'うぇ', 'を'), ('ワ', 'ウィ', 'ウ', 'ウェ', 'ヲ')),
        ('w', ('わ', 'ゐ', 'う', 'ゑ', 'を'), ('ワ', 'ヰ', 'ウ', 'ヱ', 'ヲ')),
    )

    consonants_v = (
        ('v', (None, None, None, None, None), ('ヴァ', 'ヴィ', 'ヴ', 'ヴェ', 'ヴォ')),
        ('v', ('ヴぁ', 'ヴぃ', 'ヴ', 'ヴぇ', 'ヴぉ'), ('ヴァ', 'ヴィ', 'ヴ', 'ヴェ', 'ヴォ')),
        ('v', ('ゔぁ', 'ゔぃ', 'ゔ', 'ゔぇ', 'ゔぉ'), ('ヴァ', 'ヴィ', 'ヴ', 'ヴェ', 'ヴォ')),
    )

    consonants_vy = (
        ('vy', (None, None, None, None, None), ('ヴャ', 'ヴィ', 'ヴュ', 'ヴェ', 'ヴョ')),
        ('vy', ('ヴゃ', 'ヴぃ', 'ヴゅ', 'ヴぇ', 'ヴょ'), ('ヴャ', 'ヴィ', 'ヴュ', 'ヴェ', 'ヴョ')),
        ('vy', ('ゔゃ', 'ゔぃ', 'ゔゅ', 'ゔぇ', 'ゔょ'), ('ヴャ', 'ヴィ', 'ヴュ', 'ヴェ', 'ヴョ')),
    )

    consonants_lk = (
        ('lk', (None, None, None, None, None), ('ヵ', None, None, 'ヶ', None)),
        ('lk', ('ヵ', None, None, 'ヶ', None), ('ヵ', None, None, 'ヶ', None)),
        ('lk', ('ゕ', None, None, 'ゖ', None), ('ヵ', None, None, 'ヶ', None)),
    )

    consonants_xk = (
        ('xk', (None, None, None, None, None), ('ヵ', None, None, 'ヶ', None)),
        ('xk', ('ヵ', None, None, 'ヶ', None), ('ヵ', None, None, 'ヶ', None)),
        ('xk', ('ゕ', None, None, 'ゖ', None), ('ヵ', None, None, 'ヶ', None)),
    )

    kana_n = ('ん', 'ン')

    @staticmethod
    def makeConvTable(vowels, consonants):
        return [
            tuple(zip(map((lambda v: consonant + v), vowels), hiras, katas))
            for (consonant, hiras, katas) in consonants
        ]

    def __init__(self, old_w = False,
            hiratype_v = HiraType.Kata, hiratype_lk = HiraType.Kata):
        self._old_w = old_w
        self._hiratype_v = hiratype_v
        self._hiratype_lk = hiratype_lk
        self._commonConvTable = self.makeConvTable(
            self.vowels, self.consonants
        )
        self._updateConvTable()

    def _updateConvTable(self):
        consonants = (
            self.consonants_w[self.old_w],
            self.consonants_v[self.hiratype_v.value],
            self.consonants_vy[self.hiratype_v.value],
            self.consonants_lk[self.hiratype_lk.value],
            self.consonants_xk[self.hiratype_lk.value],
        )
        addConvTable = self.makeConvTable(self.vowels, consonants)
        self._convTable = self._commonConvTable + addConvTable

    @property
    def old_w(self):
        return self._old_w

    @old_w.setter
    def old_w(self, old_w):
        self._old_w = old_w
        self._updateConvTable()

    @property
    def hiratype_v(self):
        return self._hiratype_v

    @hiratype_v.setter
    def hiratype_v(self, hiratype_v):
        self._hiratype_v = hiratype_v
        self._updateConvTable()

    @property
    def hiratype_lk(self):
        return self._hiratype_lk

    @hiratype_lk.setter
    def hiratype_lk(self, hiratype_lk):
        self._hiratype_lk = hiratype_lk
        self._updateConvTable()

    def romanToHira(self):
        pass

    def romanToKata(self):
        pass

